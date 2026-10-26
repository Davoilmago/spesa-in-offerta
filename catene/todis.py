"""
Todis: il volantino e' REGIONALE (uguale per tutte le citta' della regione), quindi viene
scaricato una volta per regione e copiato per ogni citta'. Dura circa due settimane
(es. "dal 15 al 28 ottobre").

Pagina: https://www.todis.it/volantini/lazio/
Sotto il lettore c'e' il link "Scarica il volantino in PDF" (e, accanto, quello "accessibile",
che NON ci serve). Il link punta direttamente al file PDF.

Nei file delle citta' basta scrivere:  "todis": [{"zona": "lazio", "nota": "volantino Lazio"}]
"""

import re

from playwright.sync_api import TimeoutError as PlaywrightTimeout

import comune

NOME = "todis"
GIORNI = [3, 4]     # giovedi e venerdi (il volantino cambia di solito il giovedi)
CONDIVISO = True    # un solo volantino per tutte le citta' della stessa zona


def zona(negozio):
    return (negozio.get("zona") or "lazio").lower()


def chiave_condivisione(negozio):
    """I negozi con la stessa chiave usano lo stesso volantino."""
    return zona(negozio)


def url_todis(zona_todis):
    return f"https://www.todis.it/volantini/{zona_todis}/"


def trova_pulsante(pagina, anche_qualsiasi_pdf=False):
    """Trova il link 'Scarica il volantino in PDF' (non quello 'accessibile').
    Solo come ultima possibilita' ripiega su un qualsiasi link a un PDF."""
    for frame in comune.tutti_i_frame(pagina):
        candidati = [
            ("testo 'Scarica il volantino in PDF'", frame.get_by_role("link", name=re.compile(r"scarica il volantino in pdf", re.I))),
            ("testo 'Scarica il volantino in PDF'", frame.get_by_text(re.compile(r"scarica il volantino in pdf", re.I))),
        ]
        if anche_qualsiasi_pdf:
            candidati.append(("link a un file .pdf", frame.locator('a[href*=".pdf"]:not([href*="access" i])')))
        for come, loc in candidati:
            try:
                el = loc.first
                if el.count() > 0 and el.is_visible():
                    return el, come
            except Exception:
                continue
    return None, None


def apri(pagina, negozio):
    """Apre la pagina del volantino. Restituisce (pulsante, come, info) oppure (None, None, None)."""
    indirizzo = url_todis(zona(negozio))
    print(f"    apro {indirizzo}")
    try:
        risposta = pagina.goto(indirizzo, wait_until="domcontentloaded", timeout=60000)
    except PlaywrightTimeout:
        print("    pagina non caricata in tempo")
        return None, None, None
    if risposta is not None and risposta.status >= 400:
        print(f"    pagina non trovata (stato {risposta.status})")
        return None, None, None
    pagina.wait_for_timeout(4000)
    comune.prova_chiudi_cookie(pagina)

    for giro in range(10):
        pulsante, come = trova_pulsante(pagina, anche_qualsiasi_pdf=(giro >= 7))
        if pulsante is not None:
            return pulsante, come, {"indirizzo": indirizzo}
        if giro == 3:
            comune.prova_chiudi_cookie(pagina)
        pagina.wait_for_timeout(1500)
    return None, None, None


def scarica(contesto, negozio, etichetta):
    """Scarica il volantino della zona. Restituisce (file temporaneo, info) oppure (None, None)."""
    return comune.scarica_da_pulsante(
        contesto, etichetta, lambda pagina: apri(pagina, negozio), prova_diretto=True
    )
