"""
Eurospin: il lettore del volantino ha un pulsante con la freccia di download
(barra a sinistra). Il volantino cambia ogni settimana (da lunedi a domenica).

Per ogni negozio nel file della citta' serve "id": la parte finale dell'indirizzo
del lettore, es. https://www.eurospin.it/smt-digitalflyer/punti-vendita/anzio-2
"""

from urllib.parse import quote

import comune

NOME = "eurospin"
GIORNI = [0, 1]     # quando scaricarlo in automatico: lunedi e martedi (0 = lunedi ... 6 = domenica)
CONDIVISO = False   # ogni negozio ha il suo volantino (poi i doppioni vengono tolti)

SUFFISSO = "?SHOPPING_LIST_VISIBLE=false&CLOSE_BUTTON_VISIBLE=false&PRE_OPEN_PANEL_STORE_SELECTOR=false"

# Come riconoscere il pulsante di download, dal piu' preciso al meno preciso.
SELETTORI_DOWNLOAD = [
    '[aria-label*="scarica" i]',
    '[title*="scarica" i]',
    '[aria-label*="download" i]',
    '[title*="download" i]',
    'button:has-text("Scarica")',
    'a:has-text("Scarica")',
]


def url_lettore(id_negozio):
    """Indirizzo della pagina Eurospin che mostra il lettore del volantino."""
    interno = f"https://www.eurospin.it/smt-digitalflyer/punti-vendita/{id_negozio}{SUFFISSO}"
    return "https://www.eurospin.com/it-it/volantino-store-eurospin/?url=" + quote(interno, safe="")


def trova_pulsante(pagina):
    """Cerca il pulsante in pagina e dentro i frame. Restituisce (locator, descrizione) oppure (None, None)."""
    for frame in comune.tutti_i_frame(pagina):
        for selettore in SELETTORI_DOWNLOAD:
            try:
                loc = frame.locator(selettore).first
                if loc.count() > 0 and loc.is_visible():
                    return loc, f"selettore {selettore}"
            except Exception:
                continue

    # Ultima risorsa: la barra laterale a sinistra ha 5 icone (casa, lente, download, mappa, condividi).
    # Il download e' la terza dall'alto.
    for frame in comune.tutti_i_frame(pagina):
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


def apri(pagina, negozio):
    """Apre il lettore del volantino e trova il pulsante. Restituisce (pulsante, come, info)."""
    pagina.goto(url_lettore(negozio["id"]), wait_until="domcontentloaded", timeout=60000)
    pagina.wait_for_timeout(6000)  # il lettore si carica dopo, con JavaScript
    comune.prova_chiudi_cookie(pagina)
    pulsante, come = trova_pulsante(pagina)
    return pulsante, come, {}


def scarica(contesto, negozio, etichetta):
    """Scarica il volantino di un negozio. Restituisce (file temporaneo, info) oppure (None, None)."""
    return comune.scarica_da_pulsante(contesto, etichetta, lambda pagina: apri(pagina, negozio))
