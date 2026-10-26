"""
Spesa in Offerta - scarico automatico dei volantini Eurospin (Anzio e Nettuno).

Cosa fa:
  1. apre il lettore del volantino di ogni negozio con un browser automatico
  2. preme il pulsante di download (quello con la freccia verso il basso)
  3. salva il PDF nella cartella "volantini" con il tuo schema di nomi
     (supermercato_CAP_Citta.pdf, es. eurospin_00042_Anzio.pdf)
  4. se due negozi della stessa citta hanno lo stesso volantino, ne tiene uno solo

Per aggiungere altre catene o altri negozi basta aggiungere voci in NEGOZI.
"""

import hashlib
import json
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
                el = elementi.nth(i)
                try:
                    righe.append(
                        f"{i}: tag={el.evaluate('e => e.tagName')} "
                        f"aria-label={el.get_attribute('aria-label')!r} "
                        f"title={el.get_attribute('title')!r} "
                        f"testo={(el.inner_text() or '').strip()[:40]!r} "
                        f"box={el.bounding_box()}"
                    )
                except Exception:
                    pass
        except Exception:
            pass
    (CARTELLA_DEBUG / f"{nome}.txt").write_text("\n".join(righe), encoding="utf-8")


def scarica_un_negozio(contesto, negozio):
    """Scarica il volantino di un negozio. Restituisce il percorso del file temporaneo oppure None."""
    etichetta = f"{negozio['catena']}_{negozio['negozio']}"
    pagina = contesto.new_page()
    try:
        pagina.goto(url_lettore(negozio["negozio"]), wait_until="domcontentloaded", timeout=60000)
        pagina.wait_for_timeout(6000)  # il lettore si carica dopo, con JavaScript
        prova_chiudi_cookie(pagina)

        pulsante, come = trova_pulsante_download(pagina)
        if pulsante is None:
            print(f"[ERRORE] {etichetta}: pulsante di download non trovato")
            salva_debug(pagina, etichetta)
            return None
        print(f"[ok] {etichetta}: pulsante trovato ({come})")

        with pagina.expect_download(timeout=60000) as info:
            pulsante.click()
        download = info.value

        CARTELLA_PDF.mkdir(exist_ok=True)
        temporaneo = CARTELLA_PDF / f"_tmp_{etichetta}.pdf"
        download.save_as(str(temporaneo))

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
