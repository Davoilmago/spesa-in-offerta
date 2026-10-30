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
    """Preme 'Menu' in alto a destra e controlla che si apra davvero.
    Prova clic normale, forzato e con JavaScript. Restituisce True se ha premuto il Menu."""
    # "Menù", "Menu" o "Menù" con accento rovinato dalla codifica: 'men' + al massimo due caratteri
    nome_menu = re.compile(r"^\s*men\S{0,2}\s*$", re.I)
    premuto = False
    for frame in comune.tutti_i_frame(pagina):
        candidati = [
            frame.get_by_role("button", name=nome_menu),
            frame.get_by_text(nome_menu),
        ]
        for loc in candidati:
            try:
                el = loc.first
                if el.count() == 0 or not el.is_visible():
                    continue
            except Exception as e:
                print(f"    ricerca Menu: {str(e).splitlines()[0][:150]}")
                continue
            metodi = [
                ("clic normale", lambda: el.click(timeout=4000)),
                ("clic forzato", lambda: el.click(timeout=3000, force=True)),
                ("clic con JavaScript", lambda: el.evaluate("e => e.click()")),
            ]
            for nome, azione in metodi:
                try:
                    azione()
                    premuto = True
                except Exception as e:
                    print(f"    Menu, {nome}: non riuscito ({str(e).splitlines()[0][:100]})")
                    continue
                for _ in range(3):
                    if trova_scarica_pdf(pagina) is not None:
                        print(f"    Menu aperto con: {nome}")
                        return True
                    pagina.wait_for_timeout(500)
                print(f"    Menu, {nome}: eseguito ma il menu non si e' aperto")
    return premuto


def chiudi_banner_extra(pagina):
    """Seconda possibilita' per i cookie: prova anche i pulsanti che accettano."""
    for testo in ["Accetta tutti", "Accetta tutto", "Accetta", "OK", "Ho capito", "Chiudi"]:
        try:
            pulsante = pagina.get_by_role("button", name=re.compile(rf"^\s*{re.escape(testo)}\s*$", re.I)).first
            if pulsante.is_visible(timeout=800):
                print(f"    banner: premo '{testo}'")
                pulsante.click(timeout=3000)
                pagina.wait_for_timeout(500)
                return
        except Exception:
            pass


def trova_scarica_pdf(pagina):
    for frame in comune.tutti_i_frame(pagina):
        try:
            el = frame.get_by_text(re.compile(r"scarica il pdf", re.I)).first
            if el.count() > 0 and el.is_visible():
                return el
        except Exception:
            continue
    return None


def pagina_non_trovata(pagina):
    """True se il lettore mostra 'Purtroppo non riusciamo a trovare la pagina'."""
    for frame in comune.tutti_i_frame(pagina):
        try:
            if frame.get_by_text(re.compile(r"non riusciamo a trovare la pagina", re.I)).count() > 0:
                return True
        except Exception:
            continue
    return False


def scopri_da_panoramica(pagina):
    """Dalla pagina d'errore torna alla panoramica dei volantini e ne legge i collegamenti.
    Cosi' non dipendiamo dall'indirizzo 'indovinato' con le date. Restituisce [(dal, al, indirizzo)]
    dei volantini validi oggi, il piu' recente per primo."""
    oggi = datetime.now(ZoneInfo("Europe/Rome")).date()
    try:
        pagina.goto("https://www.lidl.it/c/i-nostri-volantini/s10018048", wait_until="domcontentloaded", timeout=60000)
        pagina.wait_for_timeout(8000)
        comune.prova_chiudi_cookie(pagina)
        pagina.wait_for_timeout(2000)
        try:
            comune.salva_debug(pagina, "lidl-panoramica")
        except Exception:
            pass
    except Exception as e:
        print(f"    panoramica non raggiunta: {e}")
        return []
    print(f"    panoramica: {pagina.url}")
    # il volantino settimanale (alimentare) a volte compare dopo: attendo e scorro
    try:
        pagina.mouse.wheel(0, 600)
        pagina.wait_for_timeout(5000)
    except Exception:
        pass
    tutti = []
    for frame in comune.tutti_i_frame(pagina):
        try:
            tutti += frame.eval_on_selector_all("a[href]", "els => els.map(e => e.href)")
        except Exception:
            pass
    trovati = []
    for h in dict.fromkeys(tutti):
        print(f"    collegamento: {h}")
        if "volantin" not in h.lower() and "offerte-valide" not in h.lower():
            continue
        m = re.search(r"dal-(\d{1,2})-(\d{1,2})-al-(\d{1,2})-(\d{1,2})", h)
        if not m:
            continue
        g1, m1, g2, m2 = (int(x) for x in m.groups())
        try:
            dal = datetime(oggi.year, m1, g1).date()
            al = datetime(oggi.year + (1 if m2 < m1 else 0), m2, g2).date()
        except ValueError:
            continue
        if dal <= oggi <= al and ("/view/" in h or "/ar/" in h):
            if "/ar/" in h:
                # la pagina 'ar' e' la scheda del volantino; il lettore sta in /view/flyer/page/1
                trovati.append((dal, al, h.split("/ar/")[0] + "/view/flyer/page/1"))
            trovati.append((dal, al, h))
    # se il settimanale (cibo) non e' tra i link, provo a cliccare la sua scheda e leggo l'indirizzo
    if not any("settimanal" in t[2].lower() or "naz" in t[2].lower() for t in trovati):
        for testo in ("Volantino settimanale", "Offerte valide dal"):
            try:
                el = pagina.get_by_text(testo).first
                el.click(timeout=8000)
                pagina.wait_for_timeout(6000)
                u = pagina.url
                print(f"    cliccata scheda '{testo}' -> {u}")
                m = re.search(r"dal-(\d{1,2})-(\d{1,2})-al-(\d{1,2})-(\d{1,2})", u)
                if m and "volantin" in u.lower():
                    g1, m1, g2, m2 = (int(x) for x in m.groups())
                    dal = datetime(oggi.year, m1, g1).date()
                    al = datetime(oggi.year + (1 if m2 < m1 else 0), m2, g2).date()
                    base = u.split("/ar/")[0].split("/view/")[0]
                    trovati.append((dal, al, base + "/view/flyer/page/1"))
                    break
            except Exception as e:
                print(f"    scheda '{testo}' non cliccabile: {e}")
    # il settimanale alimentare per primo
    trovati.sort(key=lambda t: (("settimanal" in t[2].lower() or "naz" in t[2].lower()), t[0]), reverse=True)
    return trovati


def apri(pagina, negozio):
    """Apre il volantino in corso e il menu. Restituisce (pulsante, come, info) oppure (None, None, None)."""
    tentativi = []
    for dal, al in finestre_lidl():
        tentativi.append((dal, al, url_lidl(dal, al)))
        # Lidl ora scrive le date senza zero iniziale (es. dal-29-10-al-4-11)
        senza = f"{dal.day}-{dal.month}", f"{al.day}-{al.month}"
        for suff in ("volantino-settimanale-NAZ", "volantino-settimanale"):
            tentativi.append((dal, al, f"https://www.lidl.it/l/it/volantini/offerte-valide-dal-{senza[0]}-al-{senza[1]}-{suff}/view/flyer/page/1"))
    scoperti = False
    i = 0
    while i < len(tentativi):
        dal, al, indirizzo = tentativi[i]
        i += 1
        print(f"    provo il volantino Lidl dal {dal:%d/%m} al {al:%d/%m}: {indirizzo}")
        try:
            risposta = pagina.goto(indirizzo, wait_until="domcontentloaded", timeout=60000)
        except PlaywrightTimeout:
            print("    pagina non caricata in tempo")
            continue
        if risposta is not None and risposta.status >= 400:
            print(f"    pagina non trovata (stato {risposta.status})")
            continue
        pagina.wait_for_timeout(6000)  # il lettore si carica dopo, con JavaScript
        try:
            print(f"    pagina aperta: {pagina.url}  titolo: {pagina.title()!r}")
        except Exception:
            pass
        comune.prova_chiudi_cookie(pagina)

        if pagina_non_trovata(pagina):
            print("    il lettore dice: pagina non trovata")
            if not scoperti:
                scoperti = True
                for d2, a2, u2 in scopri_da_panoramica(pagina):
                    # scarico solo il settimanale alimentare, non i volantini speciali (non food)
                    if not ("settimanal" in u2.lower() or "naz" in u2.lower()):
                        print(f"    salto volantino speciale: {u2}")
                        continue
                    if all(u2 != t[2] for t in tentativi):
                        tentativi.append((d2, a2, u2))
                        print(f"    volantino scoperto dalla panoramica: dal {d2:%d/%m} al {a2:%d/%m}")
            continue

        menu_aperto = False
        for giro in range(8):
            if apri_menu(pagina):
                menu_aperto = True
                break
            if giro == 2:
                chiudi_banner_extra(pagina)
            pagina.wait_for_timeout(1500)
        if not menu_aperto:
            print("    pulsante Menu non trovato")
            comune.stampa_elementi_visibili(pagina, f"elementi visibili (volantino {dal:%d/%m})")
            comune.salva_debug(pagina, f"lidl-{dal:%d-%m}")
            continue

        for _ in range(5):
            pulsante = trova_scarica_pdf(pagina)
            if pulsante is not None:
                info = {"valido_dal": dal.isoformat(), "valido_al": al.isoformat(), "indirizzo": indirizzo}
                return pulsante, "testo 'Scarica il PDF'", info
            pagina.wait_for_timeout(1000)
        print("    'Scarica il PDF' non trovato nel menu")
        comune.stampa_elementi_visibili(pagina, f"elementi visibili con il menu aperto (volantino {dal:%d/%m})")
        comune.salva_debug(pagina, f"lidl-menu-{dal:%d-%m}")
    return None, None, None


def scarica(contesto, negozio, etichetta):
    """Scarica il volantino nazionale. Restituisce (file temporaneo, info) oppure (None, None)."""
    return comune.scarica_da_pulsante(
        contesto, etichetta, lambda pagina: apri(pagina, negozio), prova_diretto=True
    )
