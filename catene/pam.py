"""
Pam Panorama: ogni punto vendita ha una pagina con il suo volantino.
Es. Nettuno: https://www.pampanorama.it/punti-vendita/roma-nettuno

La pagina funziona solo con JavaScript. Questa prima versione e' di ESPLORAZIONE:
apre la pagina, scrive nel log cosa trova (link, pulsanti, testo) e prova a
seguire il link del volantino e a scaricarlo. Dal log si capisce poi come rifinirla.
Per ogni negozio nel file della citta' serve "id": la parte finale dell'indirizzo
(es. roma-nettuno).
"""

import contextlib
import io
import re
from pathlib import Path

import comune

LOG = Path("volantini/_debug/pam.txt")   # il registro viene salvato nel progetto, cosi' lo posso leggere


def log(testo):
    print(testo)
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(testo + "\n")


NOME = "pam"
GIORNI = [0, 1, 2, 3, 4, 5, 6]   # all'inizio proviamo ogni giorno (i doppioni vengono tolti)
CONDIVISO = False


def url_negozio(id_negozio):
    return f"https://www.pampanorama.it/punti-vendita/{id_negozio}"


def stampa_pagina(pagina, titolo):
    log(f"    === {titolo}")
    try:
        log(f"    url: {pagina.url}  titolo: {pagina.title()!r}")
    except Exception:
        pass
    for frame in comune.tutti_i_frame(pagina):
        try:
            testo = frame.locator("body").inner_text(timeout=5000)
            log(f"    testo ({frame.url[:80]}): {re.sub(chr(10)+'+', ' | ', testo)[:1500]!r}")
        except Exception:
            pass
        try:
            hrefs = frame.eval_on_selector_all(
                "a[href]", "els => els.map(e => (e.innerText||'').trim().slice(0,40) + ' -> ' + e.href)"
            )
            utili = [h for h in hrefs if re.search(r"volantin|flyer|pdf|offert|catalog|sfoglia", h, re.I)]
            for h in utili[:30]:
                log(f"    link: {h}")
            log(f"    (link totali: {len(hrefs)})")
        except Exception:
            pass
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        comune.stampa_elementi_visibili(pagina, titolo)
    log(buf.getvalue().rstrip())


def trova_scarica(pagina):
    for frame in comune.tutti_i_frame(pagina):
        for sel in ['[aria-label*="scarica" i]', '[title*="scarica" i]', '[aria-label*="download" i]',
                    'button:has-text("Scarica il volantino")', 'a:has-text("Scarica il volantino")']:
            try:
                loc = frame.locator(sel).first
                if loc.count() > 0 and loc.is_visible():
                    return loc, f"selettore {sel}"
            except Exception:
                continue
    return None, None


def apri(pagina, negozio):
    pagina.goto(url_negozio(negozio["id"]), wait_until="domcontentloaded", timeout=60000)
    pagina.wait_for_timeout(8000)
    comune.prova_chiudi_cookie(pagina)
    pagina.wait_for_timeout(1500)
    stampa_pagina(pagina, "pagina del negozio Pam")

    # Seguo il link/pulsante del volantino, se c'e'
    for frame in comune.tutti_i_frame(pagina):
        for loc in [frame.get_by_role("link", name=re.compile(r"volantin", re.I)),
                    frame.get_by_role("button", name=re.compile(r"volantin", re.I)),
                    frame.get_by_text(re.compile(r"sfoglia|vedi il volantino|volantino", re.I))]:
            try:
                el = loc.first
                if el.count() == 0 or not el.is_visible():
                    continue
                log(f"    clic su: {comune.descrivi(el)}")
                el.click(timeout=5000)
                pagina.wait_for_timeout(8000)
                stampa_pagina(pagina, "dopo il clic sul volantino")
                break
            except Exception as e:
                log(f"    clic non riuscito: {str(e).splitlines()[0][:120]}")
    log("    [esplorazione] nessun download tentato")
    comune.salva_debug(pagina, "pam-esplorazione")
    return None, None, None


def scarica(contesto, negozio, etichetta):
    return comune.scarica_da_pulsante(contesto, etichetta, lambda pagina: apri(pagina, negozio), prova_diretto=True)
