"""
Spesa in Offerta - scarico automatico dei volantini Eurospin (Anzio e Nettuno).

Cosa fa:
  1. apre il lettore del volantino di ogni negozio con un browser automatico
  2. preme il pulsante di download (quello con la freccia verso il basso)
  3. se compare una finestra di conferma, la conferma; se il PDF si apre in una
     nuova scheda, lo prende da li'
  4. salva il PDF nella cartella "volantini" con il tuo schema di nomi
     (supermercato_CAP_Citta.pdf, es. eurospin_00042_Anzio.pdf)
  5. se due negozi della stessa citta hanno lo stesso volantino, ne tiene uno solo

Per aggiungere altre catene o altri negozi basta aggiungere voci in NEGOZI.
"""

import base64
import hashlib
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

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
# "negozio" e' la parte finale dell'indirizzo del lettore (es. .../punti-vendita/anzio-2)
NEGOZI = [
    {"catena": "eurospin", "cap": "00042", "citta": "Anzio", "negozio": "anzio", "nota": "Via Nerone 15"},
    {"catena": "eurospin", "cap": "00042", "citta": "Anzio", "negozio": "anzio-2", "nota": "Via del Cinema 26"},
    {"catena": "eurospin", "cap": "00048", "citta": "Nettuno", "negozio": "nettuno", "nota": "Via Scipione Borghese 35"},
]

# Come riconoscere il pulsante di download, dal piu' preciso al meno preciso.
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
    for testo in ["Rifiuta", "Rifiuta tutti", "Solo necessari", "Solo essenziali", "Accetta solo i necessari"]:
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
    """Cerca il pulsante in pagina e dentro i frame. Restituisce (locator, descrizione) oppure (None, None)."""
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


def scarica_un_negozio(contesto, negozio):
    """Scarica il volantino di un negozio. Restituisce il percorso del file temporaneo oppure None."""
    etichetta = f"{negozio['catena']}_{negozio['negozio']}"
    pagina = contesto.new_page()
    scaricati = []
    nuove_schede = []
    pagina.on("download", lambda d: scaricati.append(d))
    contesto.on("page", lambda p: nuove_schede.append(p))
    try:
        pagina.goto(url_lettore(negozio["negozio"]), wait_until="domcontentloaded", timeout=60000)
        pagina.wait_for_timeout(6000)  # il lettore si carica dopo, con JavaScript
        prova_chiudi_cookie(pagina)

        pulsante, come = trova_pulsante_download(pagina)
        if pulsante is None:
            print(f"[ERRORE] {etichetta}: pulsante di download non trovato")
            stampa_elementi_visibili(pagina, "elementi visibili")
            salva_debug(pagina, etichetta)
            return None
        print(f"[ok] {etichetta}: pulsante trovato ({come})")
        print(f"    elemento: {descrivi(pulsante)}")

        CARTELLA_PDF.mkdir(exist_ok=True)
        temporaneo = CARTELLA_PDF / f"_tmp_{etichetta}.pdf"

        pulsante.click(timeout=15000)

        # 1) il download parte subito?
        if not aspetta(pagina, scaricati, 10):
            print(f"    nessun download dopo 10 secondi: guardo cosa e' successo")
            stampa_elementi_visibili(pagina, "elementi visibili dopo il clic")
            salva_debug(pagina, etichetta)

            # 2) magari e' comparsa una finestra di conferma
            if prova_conferma(pagina):
                aspetta(pagina, scaricati, 90)

            # 3) oppure il PDF si e' aperto in una nuova scheda
            if not scaricati and nuove_schede:
                for nuova in nuove_schede:
                    if pdf_da_nuova_scheda(nuova, temporaneo):
                        return temporaneo

            # 4) ultima possibilita': aspetto ancora
            if not scaricati:
                aspetta(pagina, scaricati, 60)

        if not scaricati:
            print(f"[ERRORE] {etichetta}: nessun file scaricato")
            salva_debug(pagina, etichetta)
            return None

        scaricati[0].save_as(str(temporaneo))

        with open(temporaneo, "rb") as f:
            if f.read(5) != b"%PDF-":
                print(f"[ERRORE] {etichetta}: il file scaricato non sembra un PDF")
                salva_debug(pagina, etichetta)
                temporaneo.unlink(missing_ok=True)
                return None
        return temporaneo
    except PlaywrightTimeout:
        print(f"[ERRORE] {etichetta}: tempo scaduto")
        salva_debug(pagina, etichetta)
        return None
    except Exception as errore:
        print(f"[ERRORE] {etichetta}: {errore}")
        try:
            salva_debug(pagina, etichetta)
        except Exception:
            pass
        return None
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
    risultati = []  # un elemento per ogni file tenuto
    visti = {}      # (catena, cap) -> impronte gia' salvate e quanti file ci sono
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
            temporaneo = scarica_un_negozio(contesto, negozio)
            if temporaneo is None:
                errori += 1
                continue

            chiave = (negozio["catena"], negozio["cap"])
            gia_salvati = visti.setdefault(chiave, {})
            firma = impronta(temporaneo)

            if firma in gia_salvati:
                print(f"[uguale] {negozio['nota']}: stesso volantino di {gia_salvati[firma]}, non lo duplico")
                temporaneo.unlink()
                continue

            base = f"{negozio['catena']}_{negozio['cap']}_{negozio['citta']}"
            nome = f"{base}.pdf" if not gia_salvati else f"{base}_{len(gia_salvati) + 1}.pdf"
            destinazione = CARTELLA_PDF / nome
            temporaneo.replace(destinazione)
            gia_salvati[firma] = nome

            risultati.append(
                {
                    "file": nome,
                    "negozio": negozio["nota"],
                    "sha256": firma,
                    "byte": destinazione.stat().st_size,
                    "scaricato_il": datetime.now().isoformat(timespec="seconds"),
                }
            )
            print(f"[salvato] {nome} ({negozio['nota']})")

        browser.close()

    CARTELLA_PDF.mkdir(exist_ok=True)
    (CARTELLA_PDF / "elenco.json").write_text(
        json.dumps(risultati, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    print(f"\nFatto: {len(risultati)} file salvati, {errori} errori.")
    # Se qualcosa e' andato storto il lavoro risulta "fallito" e GitHub ti manda una email.
    sys.exit(1 if errori else 0)


if __name__ == "__main__":
    main()
