"""
Strumenti comuni a tutte le catene: browser, clic, download, controllo del PDF.

Ogni catena (cartella catene/) usa queste funzioni e aggiunge solo la parte che
la riguarda: come aprire il volantino e dove si trova il pulsante di download.
"""

import base64
import hashlib
import re
import unicodedata
from pathlib import Path

from playwright.sync_api import TimeoutError as PlaywrightTimeout

CARTELLA_PDF = Path("volantini")   # i PDF finali (questa cartella viene salvata su GitHub)
CARTELLA_TMP = Path("_tmp")        # file temporanei, cancellati a fine lavoro
CARTELLA_DEBUG = Path("debug")     # screenshot e liste dei pulsanti se qualcosa va storto

# Possibili finestre di conferma che si aprono dopo il clic.
CONTENITORI_FINESTRA = '[role="dialog"], [aria-modal="true"], [class*="modal" i], [class*="popup" i], [class*="overlay" i]'
TESTI_CONFERMA = re.compile(r"^\s*(scarica.*|download.*|conferma|continua|ok|salva|procedi)\s*$", re.I)


def slug(testo):
    """'Città di Castello' -> 'citta-di-castello' (per i nomi delle cartelle)."""
    pulito = unicodedata.normalize("NFKD", str(testo)).encode("ascii", "ignore").decode("ascii")
    pulito = re.sub(r"[^a-zA-Z0-9]+", "-", pulito).strip("-").lower()
    return pulito or "senza-nome"


def impronta(percorso):
    h = hashlib.sha256()
    with open(percorso, "rb") as f:
        for blocco in iter(lambda: f.read(1024 * 1024), b""):
            h.update(blocco)
    return h.hexdigest()


def prova_chiudi_cookie(pagina):
    """Se compare il banner dei cookie, sceglie l'opzione che rifiuta quelli non essenziali."""
    for testo in [
        "Rifiuta",
        "Rifiuta tutti",
        "Solo necessari",
        "Solo essenziali",
        "Accetta solo i necessari",
        "Solo i cookie necessari",
        "Accetta solo i cookie necessari",
    ]:
        try:
            pulsante = pagina.get_by_role("button", name=testo).first
            if pulsante.is_visible(timeout=1500):
                pulsante.click()
                pagina.wait_for_timeout(500)
                return
        except Exception:
            pass


def tutti_i_frame(pagina):
    return [pagina.main_frame] + [f for f in pagina.frames if f != pagina.main_frame]


def descrivi(el):
    """Descrizione corta di un elemento, per il log."""
    try:
        return (
            f"tag={el.evaluate('e => e.tagName')} "
            f"title={el.get_attribute('title')!r} "
            f"aria-label={el.get_attribute('aria-label')!r} "
            f"testo={(el.inner_text() or '').strip()[:40]!r} "
            f"box={el.bounding_box()}"
        )
    except Exception as errore:
        return f"(non descrivibile: {errore})"


def stampa_elementi_visibili(pagina, titolo):
    """Scrive nel log i pulsanti visibili, cosi' vediamo cosa c'e' sulla pagina."""
    print(f"    --- {titolo}")
    for frame in tutti_i_frame(pagina):
        try:
            elementi = frame.locator('button, a, [role="button"]')
            mostrati = 0
            for i in range(elementi.count()):
                el = elementi.nth(i)
                try:
                    if not el.is_visible():
                        continue
                except Exception:
                    continue
                print(f"    {descrivi(el)}")
                mostrati += 1
                if mostrati >= 40:
                    break
        except Exception:
            pass


def salva_debug(pagina, nome):
    """Salva uno screenshot e l'elenco dei pulsanti, per capire cosa non ha funzionato."""
    CARTELLA_DEBUG.mkdir(exist_ok=True)
    try:
        pagina.screenshot(path=str(CARTELLA_DEBUG / f"{nome}.png"), full_page=False)
    except Exception:
        pass
    righe = []
    for frame in tutti_i_frame(pagina):
        righe.append(f"--- frame: {frame.url}")
        try:
            elementi = frame.locator('button, a, [role="button"]')
            for i in range(min(elementi.count(), 80)):
                righe.append(f"{i}: {descrivi(elementi.nth(i))}")
        except Exception:
            pass
    (CARTELLA_DEBUG / f"{nome}.txt").write_text("\n".join(righe), encoding="utf-8")


def aspetta(pagina, lista, secondi):
    """Aspetta fino a 'secondi' che nella lista compaia qualcosa."""
    for _ in range(int(secondi * 2)):
        if lista:
            return True
        pagina.wait_for_timeout(500)
    return bool(lista)


def prova_conferma(pagina):
    """Se dopo il clic e' comparsa una finestra, preme il pulsante di conferma. Restituisce True se ha cliccato."""
    for frame in tutti_i_frame(pagina):
        try:
            finestre = frame.locator(CONTENITORI_FINESTRA)
            for i in range(finestre.count()):
                finestra = finestre.nth(i)
                if not finestra.is_visible():
                    continue
                print(f"    finestra trovata: {descrivi(finestra)}")
                try:
                    print(f"    testo della finestra: {(finestra.inner_text() or '').strip()[:200]!r}")
                except Exception:
                    pass
                pulsanti = finestra.locator('button, a, [role="button"]')
                for j in range(pulsanti.count()):
                    p = pulsanti.nth(j)
                    try:
                        if not p.is_visible():
                            continue
                        testo = (p.inner_text() or p.get_attribute("title") or p.get_attribute("aria-label") or "").strip()
                        if TESTI_CONFERMA.match(testo):
                            print(f"    premo '{testo}' nella finestra")
                            p.click(timeout=10000)
                            return True
                    except Exception:
                        continue
        except Exception:
            continue
    return False


def pdf_da_nuova_scheda(nuova, destinazione):
    """Se il PDF si e' aperto in una nuova scheda, prova a leggerlo da li'."""
    try:
        nuova.wait_for_timeout(3000)
        print(f"    nuova scheda: {nuova.url}")
        dati_base64 = nuova.evaluate(
            """async () => {
                const r = await fetch(location.href);
                const a = new Uint8Array(await r.arrayBuffer());
                let s = '';
                for (let i = 0; i < a.length; i += 0x8000) {
                    s += String.fromCharCode.apply(null, a.subarray(i, i + 0x8000));
                }
                return btoa(s);
            }"""
        )
        contenuto = base64.b64decode(dati_base64)
        if contenuto[:5] == b"%PDF-":
            destinazione.write_bytes(contenuto)
            return True
    except Exception as errore:
        print(f"    lettura dalla nuova scheda non riuscita: {errore}")
    return False


def prova_pdf_diretto(contesto, pulsante, destinazione):
    """Se il pulsante e' un link a un file PDF, lo scarica direttamente dall'indirizzo."""
    try:
        href = pulsante.evaluate("e => { const a = e.closest('a'); return a ? a.href : ''; }")
        if href and href.startswith("http"):
            print(f"    indirizzo del pulsante: {href[:200]}")
            risposta = contesto.request.get(href, timeout=60000)
            corpo = risposta.body()
            if risposta.ok and corpo[:5] == b"%PDF-":
                destinazione.write_bytes(corpo)
                print("    PDF scaricato direttamente dall'indirizzo")
                return True
            print(f"    l'indirizzo non e' un PDF (stato {risposta.status})")
    except Exception as errore:
        print(f"    scarico diretto non riuscito: {errore}")
    return False


def premi_e_aspetta(pagina, pulsante, scaricati):
    """Prova a premere il pulsante in tre modi, finche' parte il download. Restituisce True se e' partito."""
    tentativi = [
        ("clic normale", lambda: pulsante.click(timeout=5000)),
        ("clic forzato", lambda: pulsante.click(timeout=5000, force=True)),
        ("clic con JavaScript", lambda: pulsante.evaluate("e => e.click()")),
    ]
    primo_fallimento = True
    for nome, azione in tentativi:
        try:
            azione()
            print(f"    {nome}: eseguito")
        except Exception as errore:
            print(f"    {nome}: non riuscito ({str(errore)[:600]!r})")
            if primo_fallimento:
                primo_fallimento = False
                stampa_elementi_visibili(pagina, "elementi visibili dopo il primo clic fallito")
            continue
        if aspetta(pagina, scaricati, 8):
            print(f"    download partito con: {nome}")
            return True
    return bool(scaricati)


def scarica_da_pulsante(contesto, etichetta, apri, prova_diretto=False):
    """Scarica un volantino.

    'apri' e' la parte specifica della catena: riceve la pagina, apre il volantino e
    restituisce (pulsante, come, info). Se non trova il pulsante restituisce pulsante=None.

    Restituisce (percorso del file temporaneo, info) oppure (None, None).
    """
    CARTELLA_TMP.mkdir(exist_ok=True)
    temporaneo = CARTELLA_TMP / f"{slug(etichetta)}.pdf"
    pagina = contesto.new_page()
    scaricati = []
    nuove_schede = []

    def nuova_scheda_aperta(p):
        nuove_schede.append(p)
        p.on("download", lambda d: scaricati.append(d))

    pagina.on("download", lambda d: scaricati.append(d))
    contesto.on("page", nuova_scheda_aperta)
    try:
        pulsante, come, info = apri(pagina)
        info = info or {}

        if pulsante is None:
            print(f"[ERRORE] {etichetta}: pulsante di download non trovato")
            stampa_elementi_visibili(pagina, "elementi visibili")
            salva_debug(pagina, slug(etichetta))
            return None, None
        print(f"[ok] {etichetta}: pulsante trovato ({come})")
        print(f"    elemento: {descrivi(pulsante)}")

        # Se il pulsante e' un link a un PDF, la via piu' semplice e' scaricarlo direttamente.
        if prova_diretto and prova_pdf_diretto(contesto, pulsante, temporaneo):
            return temporaneo, info

        # 1) il download parte subito?
        if not premi_e_aspetta(pagina, pulsante, scaricati):
            print("    nessun download dopo i tentativi: guardo cosa e' successo")
            stampa_elementi_visibili(pagina, "elementi visibili dopo il clic")
            salva_debug(pagina, slug(etichetta))

            # 2) magari e' comparsa una finestra di conferma
            if prova_conferma(pagina):
                aspetta(pagina, scaricati, 90)

            # 3) oppure il PDF si e' aperto in una nuova scheda
            if not scaricati and nuove_schede:
                for nuova in nuove_schede:
                    if pdf_da_nuova_scheda(nuova, temporaneo):
                        return temporaneo, info

            # 4) ultima possibilita': aspetto ancora
            if not scaricati:
                aspetta(pagina, scaricati, 60)

        if not scaricati:
            print(f"[ERRORE] {etichetta}: nessun file scaricato")
            salva_debug(pagina, slug(etichetta))
            return None, None

        scaricati[0].save_as(str(temporaneo))

        with open(temporaneo, "rb") as f:
            if f.read(5) != b"%PDF-":
                print(f"[ERRORE] {etichetta}: il file scaricato non sembra un PDF")
                salva_debug(pagina, slug(etichetta))
                temporaneo.unlink(missing_ok=True)
                return None, None
        return temporaneo, info
    except PlaywrightTimeout as errore:
        print(f"[ERRORE] {etichetta}: tempo scaduto ({str(errore)[:600]!r})")
        salva_debug(pagina, slug(etichetta))
        return None, None
    except Exception as errore:
        print(f"[ERRORE] {etichetta}: {errore}")
        try:
            salva_debug(pagina, slug(etichetta))
        except Exception:
            pass
        return None, None
    finally:
        contesto.remove_listener("page", nuova_scheda_aperta)
        for nuova in nuove_schede:
            try:
                nuova.close()
            except Exception:
                pass
        pagina.close()
