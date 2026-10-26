"""
Spesa in Offerta - scarico automatico dei volantini (Eurospin e Lidl, Anzio e Nettuno).

Cosa fa:
  1. apre il lettore del volantino con un browser automatico
  2. preme il pulsante di download (Eurospin: freccia a sinistra; Lidl: Menu -> Scarica il PDF)
  3. se compare una finestra di conferma, la conferma; se il PDF si apre in una
     nuova scheda, lo prende da li'
  4. salva il PDF nella cartella "volantini" con il tuo schema di nomi
     (supermercato_CAP_Citta.pdf, es. eurospin_00042_Anzio.pdf)
  5. se due negozi della stessa citta hanno lo stesso volantino, ne tiene uno solo
  6. se piu' citta condividono lo stesso volantino (Lidl nazionale), lo scarica una volta
     sola e ne salva una copia per ogni citta'

Per aggiungere altre catene o altri negozi basta aggiungere voci in NEGOZI.
"""

import base64
import hashlib
import json
import re
import shutil
import sys
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import quote
from zoneinfo import ZoneInfo

from playwright.sync_api import TimeoutError as PlaywrightTimeout
from playwright.sync_api import sync_playwright

CARTELLA_PDF = Path("volantini")
CARTELLA_DEBUG = Path("debug")

SUFFISSO = "?SHOPPING_LIST_VISIBLE=false&CLOSE_BUTTON_VISIBLE=false&PRE_OPEN_PANEL_STORE_SELECTOR=false"


def url_lettore(nome_negozio):
    """Indirizzo della pagina Eurospin che mostra il lettore del volantino."""
    interno = f"https://www.eurospin.it/smt-digitalflyer/punti-vendita/{nome_negozio}{SUFFISSO}"
    return "https://www.eurospin.com/it-it/volantino-store-eurospin/?url=" + quote(interno, safe="")


# Elenco dei negozi da controllare.
# Eurospin: "negozio" e' la parte finale dell'indirizzo del lettore (es. .../punti-vendita/anzio-2)
# Lidl: il volantino e' nazionale, quindi "fonte" uguale = scaricato una volta sola e copiato per ogni citta'
NEGOZI = [
    {"catena": "eurospin", "cap": "00042", "citta": "Anzio", "negozio": "anzio", "nota": "Via Nerone 15"},
    {"catena": "eurospin", "cap": "00042", "citta": "Anzio", "negozio": "anzio-2", "nota": "Via del Cinema 26"},
    {"catena": "eurospin", "cap": "00048", "citta": "Nettuno", "negozio": "nettuno", "nota": "Via Scipione Borghese 35"},
    {"catena": "lidl", "cap": "00042", "citta": "Anzio", "negozio": "naz", "fonte": "lidl-naz", "nota": "volantino nazionale"},
    {"catena": "lidl", "cap": "00048", "citta": "Nettuno", "negozio": "naz", "fonte": "lidl-naz", "nota": "volantino nazionale"},
]

# Come riconoscere il pulsante di download di Eurospin, dal piu' preciso al meno preciso.
SELETTORI_DOWNLOAD = [
    '[aria-label*="scarica" i]',
    '[title*="scarica" i]',
    '[aria-label*="download" i]',
    '[title*="download" i]',
    'button:has-text("Scarica")',
    'a:has-text("Scarica")',
]

# Possibili finestre di conferma che si aprono dopo il clic.
CONTENITORI_FINESTRA = '[role="dialog"], [aria-modal="true"], [class*="modal" i], [class*="popup" i], [class*="overlay" i]'
TESTI_CONFERMA = re.compile(r"^\s*(scarica.*|download.*|conferma|continua|ok|salva|procedi)\s*$", re.I)


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


def trova_pulsante_download(pagina):
    """Eurospin: cerca il pulsante in pagina e dentro i frame. Restituisce (locator, descrizione) oppure (None, None)."""
    for frame in tutti_i_frame(pagina):
        for selettore in SELETTORI_DOWNLOAD:
            try:
                loc = frame.locator(selettore).first
                if loc.count() > 0 and loc.is_visible():
                    return loc, f"selettore {selettore}"
            except Exception:
                continue

    # Ultima risorsa: la barra laterale a sinistra ha 5 icone (casa, lente, download, mappa, condividi).
    # Il download e' la terza dall'alto.
    for frame in tutti_i_frame(pagina):
        try:
            candidati = frame.locator('button, a, [role="button"]')
            trovati = []
            for i in range(candidati.count()):
                el = candidati.nth(i)
                if not el.is_visible():
                    continue
                box = el.bounding_box()
                if box and box["x"] < 100 and box["y"] > 150:
                    trovati.append((box["y"], el))
            trovati.sort(key=lambda t: t[0])
            if len(trovati) >= 3:
                return trovati[2][1], "terza icona della barra a sinistra"
        except Exception:
            continue
    return None, None


# ---------------------------------------------------------------- Lidl

def finestre_lidl():
    """Date dei volantini Lidl: escono il giovedi' e valgono fino al mercoledi' successivo.
    Restituisce prima la settimana in corso, poi la successiva e la precedente."""
    oggi = datetime.now(ZoneInfo("Europe/Rome")).date()
    inizio = oggi - timedelta(days=(oggi.weekday() - 3) % 7)
    risultato = []
    for spostamento in (0, 7, -7):
        dal = inizio + timedelta(days=spostamento)
        al = dal + timedelta(days=6)
        risultato.append((dal, al))
    return risultato


def url_lidl(dal, al):
    return (
        "https://www.lidl.it/l/it/volantini/"
        f"offerte-valide-dal-{dal:%d-%m}-al-{al:%d-%m}-volantino-settimanale-NAZ/view/flyer/page/1"
    )


def apri_menu_lidl(pagina):
    """Preme 'Menu' in alto a destra. Restituisce True se l'ha trovato."""
    for frame in tutti_i_frame(pagina):
        candidati = [
            frame.get_by_role("button", name=re.compile(r"^\s*men[uù]\s*$", re.I)),
            frame.get_by_text(re.compile(r"^\s*men[uù]\s*$", re.I)),
        ]
        for loc in candidati:
            try:
                el = loc.first
                if el.count() > 0 and el.is_visible():
                    el.click(timeout=5000)
                    return True
            except Exception:
                continue
    return False


def trova_scarica_pdf_lidl(pagina):
    for frame in tutti_i_frame(pagina):
        try:
            el = frame.get_by_text(re.compile(r"scarica il pdf", re.I)).first
            if el.count() > 0 and el.is_visible():
                return el
        except Exception:
            continue
    return None


def apri_lidl(pagina):
    """Apre il volantino Lidl in corso e il menu. Restituisce (pulsante, come, info) oppure (None, None, None)."""
    for dal, al in finestre_lidl():
        indirizzo = url_lidl(dal, al)
        print(f"    provo il volantino Lidl dal {dal:%d/%m} al {al:%d/%m}")
        try:
            risposta = pagina.goto(indirizzo, wait_until="domcontentloaded", timeout=60000)
        except PlaywrightTimeout:
            print("    pagina non caricata in tempo")
            continue
        if risposta is not None and risposta.status >= 400:
            print(f"    pagina non trovata (stato {risposta.status})")
            continue
        pagina.wait_for_timeout(6000)  # il lettore si carica dopo, con JavaScript
        prova_chiudi_cookie(pagina)

        menu_aperto = False
        for _ in range(8):
            if apri_menu_lidl(pagina):
                menu_aperto = True
                break
            pagina.wait_for_timeout(1500)
        if not menu_aperto:
            print("    pulsante Menu non trovato")
            continue

        for _ in range(5):
            pulsante = trova_scarica_pdf_lidl(pagina)
            if pulsante is not None:
                info = {"valido_dal": dal.isoformat(), "valido_al": al.isoformat(), "indirizzo": indirizzo}
                return pulsante, "testo 'Scarica il PDF'", info
            pagina.wait_for_timeout(1000)
        print("    'Scarica il PDF' non trovato nel menu")
    return None, None, None


def prova_pdf_diretto(contesto, pulsante, destinazione):
    """Se il pulsante e' un link a un file PDF, lo scarica direttamente."""
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


# ---------------------------------------------------------------- strumenti comuni

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


def scarica_un_negozio(contesto, negozio):
    """Scarica il volantino. Restituisce (percorso del file temporaneo, info) oppure (None, None)."""
    etichetta = f"{negozio['catena']}_{negozio['negozio']}"
    pagina = contesto.new_page()
    scaricati = []
    nuove_schede = []
    info = {}

    def nuova_scheda_aperta(p):
        nuove_schede.append(p)
        p.on("download", lambda d: scaricati.append(d))

    pagina.on("download", lambda d: scaricati.append(d))
    contesto.on("page", nuova_scheda_aperta)
    try:
        if negozio["catena"] == "lidl":
            pulsante, come, info = apri_lidl(pagina)
        else:
            pagina.goto(url_lettore(negozio["negozio"]), wait_until="domcontentloaded", timeout=60000)
            pagina.wait_for_timeout(6000)  # il lettore si carica dopo, con JavaScript
            prova_chiudi_cookie(pagina)
            pulsante, come = trova_pulsante_download(pagina)

        if pulsante is None:
            print(f"[ERRORE] {etichetta}: pulsante di download non trovato")
            stampa_elementi_visibili(pagina, "elementi visibili")
            salva_debug(pagina, etichetta)
            return None, None
        print(f"[ok] {etichetta}: pulsante trovato ({come})")
        print(f"    elemento: {descrivi(pulsante)}")

        CARTELLA_PDF.mkdir(exist_ok=True)
        temporaneo = CARTELLA_PDF / f"_tmp_{etichetta}.pdf"

        # Se il pulsante e' un link a un PDF, la via piu' semplice e' scaricarlo direttamente.
        if negozio["catena"] == "lidl" and prova_pdf_diretto(contesto, pulsante, temporaneo):
            return temporaneo, info

        # 1) il download parte subito?
        if not premi_e_aspetta(pagina, pulsante, scaricati):
            print(f"    nessun download dopo i tentativi: guardo cosa e' successo")
            stampa_elementi_visibili(pagina, "elementi visibili dopo il clic")
            salva_debug(pagina, etichetta)

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
            salva_debug(pagina, etichetta)
            return None, None

        scaricati[0].save_as(str(temporaneo))

        with open(temporaneo, "rb") as f:
            if f.read(5) != b"%PDF-":
                print(f"[ERRORE] {etichetta}: il file scaricato non sembra un PDF")
                salva_debug(pagina, etichetta)
                temporaneo.unlink(missing_ok=True)
                return None, None
        return temporaneo, info
    except PlaywrightTimeout as errore:
        print(f"[ERRORE] {etichetta}: tempo scaduto ({str(errore)[:600]!r})")
        salva_debug(pagina, etichetta)
        return None, None
    except Exception as errore:
        print(f"[ERRORE] {etichetta}: {errore}")
        try:
            salva_debug(pagina, etichetta)
        except Exception:
            pass
        return None, None
    finally:
        for nuova in nuove_schede:
            try:
                nuova.close()
            except Exception:
                pass
        pagina.close()


def impronta(percorso):
    h = hashlib.sha256()
    with open(percorso, "rb") as f:
        for blocco in iter(lambda: f.read(1024 * 1024), b""):
            h.update(blocco)
    return h.hexdigest()


def main():
    risultati = []     # un elemento per ogni file tenuto
    visti = {}         # (catena, cap) -> impronte gia' salvate
    cache_fonti = {}   # fonte condivisa -> (file temporaneo, info), per scaricare una volta sola
    errori = 0

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        contesto = browser.new_context(
            locale="it-IT",
            timezone_id="Europe/Rome",
            accept_downloads=True,
            viewport={"width": 1400, "height": 900},
        )

        for negozio in NEGOZI:
            fonte = negozio.get("fonte")
            if fonte and fonte in cache_fonti:
                temporaneo, info = cache_fonti[fonte]
                print(f"[condiviso] {negozio['catena']} {negozio['citta']}: uso il volantino gia' scaricato ({fonte})")
            else:
                temporaneo, info = scarica_un_negozio(contesto, negozio)
                if fonte:
                    cache_fonti[fonte] = (temporaneo, info)

            if temporaneo is None:
                errori += 1
                continue

            chiave = (negozio["catena"], negozio["cap"])
            gia_salvati = visti.setdefault(chiave, {})
            firma = impronta(temporaneo)

            if firma in gia_salvati:
                print(f"[uguale] {negozio['nota']}: stesso volantino di {gia_salvati[firma]}, non lo duplico")
                continue

            base = f"{negozio['catena']}_{negozio['cap']}_{negozio['citta']}"
            nome = f"{base}.pdf" if not gia_salvati else f"{base}_{len(gia_salvati) + 1}.pdf"
            destinazione = CARTELLA_PDF / nome
            shutil.copyfile(temporaneo, destinazione)
            gia_salvati[firma] = nome

            voce = {
                "file": nome,
                "catena": negozio["catena"],
                "citta": negozio["citta"],
                "cap": negozio["cap"],
                "negozio": negozio["nota"],
                "sha256": firma,
                "byte": destinazione.stat().st_size,
                "scaricato_il": datetime.now().isoformat(timespec="seconds"),
            }
            voce.update(info or {})
            risultati.append(voce)
            print(f"[salvato] {nome} ({negozio['nota']})")

        browser.close()

    CARTELLA_PDF.mkdir(exist_ok=True)
    # pulizia dei file temporanei
    for temporaneo in CARTELLA_PDF.glob("_tmp_*.pdf"):
        temporaneo.unlink(missing_ok=True)

    (CARTELLA_PDF / "elenco.json").write_text(
        json.dumps(risultati, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    print(f"\nFatto: {len(risultati)} file salvati, {errori} errori.")
    # Se qualcosa e' andato storto il lavoro risulta "fallito" e GitHub ti manda una email.
    sys.exit(1 if errori else 0)


if __name__ == "__main__":
    main()
