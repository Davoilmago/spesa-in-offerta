"""
Pam Panorama: ogni punto vendita ha una pagina con il suo volantino.
Es. Nettuno: https://www.pampanorama.it/punti-vendita/roma-nettuno

La pagina funziona solo con JavaScript. Questa prima versione e' di ESPLORAZIONE:
apre la pagina, scrive nel log cosa trova (link, pulsanti, testo) e prova a
seguire il link del volantino e a scaricarlo. Dal log si capisce poi come rifinirla.
Per ogni negozio nel file della citta' serve "id": la parte finale dell'indirizzo
(es. roma-nettuno).
"""

import re

import comune

NOME = "pam"
GIORNI = [0, 1, 2, 3, 4, 5, 6]   # all'inizio proviamo ogni giorno (i doppioni vengono tolti)
CONDIVISO = False


def url_negozio(id_negozio):
    return f"https://www.pampanorama.it/punti-vendita/{id_negozio}"


def stampa_pagina(pagina, titolo):
    print(f"    === {titolo}")
    try:
        print(f"    url: {pagina.url}  titolo: {pagina.title()!r}")
    except Exception:
        pass
    for frame in comune.tutti_i_frame(pagina):
        try:
            testo = frame.locator("body").inner_text(timeout=5000)
            print(f"    testo ({frame.url[:80]}): {re.sub(chr(10)+'+', ' | ', testo)[:1500]!r}")
        except Exception:
            pass
        try:
            hrefs = frame.eval_on_selector_all(
                "a[href]", "els => els.map(e => (e.innerText||'').trim().slice(0,40) + ' -> ' + e.href)"
            )
            utili = [h for h in hrefs if re.search(r"volantin|flyer|pdf|offert|catalog", h, re.I)]
            for h in utili[:30]:
                print(f"    link: {h}")
            print(f"    (link totali: {len(hrefs)})")
        except Exception:
            pass
    comune.stampa_elementi_visibili(pagina, titolo)


def trova_scarica(pagina):
    for frame in comune.tutti_i_frame(pagina):
        for sel in ['a[href$=".pdf" i]', '[aria-label*="scarica" i]', '[title*="scarica" i]',
                    '[aria-label*="download" i]', 'button:has-text("Scarica")', 'a:has-text("Scarica")',
                    'a:has-text("PDF")', 'button:has-text("PDF")']:
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

    pulsante, come = trova_scarica(pagina)
    if pulsante is not None:
        return pulsante, come, {}

    # Seguo il link/pulsante del volantino, se c'e'
    for frame in comune.tutti_i_frame(pagina):
        for loc in [frame.get_by_role("link", name=re.compile(r"volantin", re.I)),
                    frame.get_by_role("button", name=re.compile(r"volantin", re.I)),
                    frame.get_by_text(re.compile(r"sfoglia|vedi il volantino|volantino", re.I))]:
            try:
                el = loc.first
                if el.count() == 0 or not el.is_visible():
                    continue
                print(f"    clic su: {comune.descrivi(el)}")
                el.click(timeout=5000)
                pagina.wait_for_timeout(8000)
                stampa_pagina(pagina, "dopo il clic sul volantino")
                pulsante, come = trova_scarica(pagina)
                if pulsante is not None:
                    return pulsante, come, {}
                break
            except Exception as e:
                print(f"    clic non riuscito: {str(e).splitlines()[0][:120]}")
    comune.salva_debug(pagina, "pam-esplorazione")
    return None, None, None


def scarica(contesto, negozio, etichetta):
    return comune.scarica_da_pulsante(contesto, etichetta, lambda pagina: apri(pagina, negozio), prova_diretto=True)
