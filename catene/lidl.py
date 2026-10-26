"""
Lidl: il volantino settimanale e' NAZIONALE (uguale per tutta Italia), quindi viene
scaricato una volta sola e copiato per ogni citta'. Esce il giovedi' e vale fino al
mercoledi' successivo. Nel lettore: Menu (in alto a destra) -> Scarica il PDF.

L'indirizzo contiene le date, es.:
https://www.lidl.it/l/it/volantini/offerte-valide-dal-22-10-al-28-10-volantino-settimanale-NAZ/view/flyer/page/1
quindi lo ricostruiamo ogni volta dalle date della settimana in corso.
"""

import re
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from playwright.sync_api import TimeoutError as PlaywrightTimeout

import comune

NOME = "lidl"
GIORNI = [3, 4]     # quando scaricarlo in automatico: giovedi e venerdi (0 = lunedi ... 6 = domenica)
CONDIVISO = True    # un solo volantino per tutte le citta'


def chiave_condivisione(negozio):
    """I negozi con la stessa chiave usano lo stesso volantino."""
    return "nazionale"


def finestre_lidl():
    """Date dei volantini: escono il giovedi' e valgono fino al mercoledi' successivo.
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


def apri_menu(pagina):
    """Preme 'Menu' in alto a destra. Restituisce True se l'ha trovato."""
    # "Menù", "Menu" o "Menù" con accento rovinato dalla codifica: 'men' + al massimo due caratteri
    nome_menu = re.compile(r"^\s*men\S{0,2}\s*$", re.I)
    for frame in comune.tutti_i_frame(pagina):
        candidati = [
            frame.get_by_role("button", name=nome_menu),
            frame.get_by_text(nome_menu),
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


def trova_scarica_pdf(pagina):
    for frame in comune.tutti_i_frame(pagina):
        try:
            el = frame.get_by_text(re.compile(r"scarica il pdf", re.I)).first
            if el.count() > 0 and el.is_visible():
                return el
        except Exception:
            continue
    return None


def apri(pagina, negozio):
    """Apre il volantino in corso e il menu. Restituisce (pulsante, come, info) oppure (None, None, None)."""
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
        comune.prova_chiudi_cookie(pagina)

        menu_aperto = False
        for _ in range(8):
            if apri_menu(pagina):
                menu_aperto = True
                break
            pagina.wait_for_timeout(1500)
        if not menu_aperto:
            print("    pulsante Menu non trovato")
            continue

        for _ in range(5):
            pulsante = trova_scarica_pdf(pagina)
            if pulsante is not None:
                info = {"valido_dal": dal.isoformat(), "valido_al": al.isoformat(), "indirizzo": indirizzo}
                return pulsante, "testo 'Scarica il PDF'", info
            pagina.wait_for_timeout(1000)
        print("    'Scarica il PDF' non trovato nel menu")
    return None, None, None


def scarica(contesto, negozio, etichetta):
    """Scarica il volantino nazionale. Restituisce (file temporaneo, info) oppure (None, None)."""
    return comune.scarica_da_pulsante(
        contesto, etichetta, lambda pagina: apri(pagina, negozio), prova_diretto=True
    )
