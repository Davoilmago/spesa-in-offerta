"""
Conad: ogni negozio e' indipendente e puo' avere PIU' volantini nello stesso periodo
(es. "1+1" e "Super Formati Super Prezzi"), anche con date che si sovrappongono.

Ogni volantino ha un indirizzo di questo tipo:
  https://www.conad.it/volantini/Spazio-Conad-Fascia2?anacanId=008625
dove 'Spazio-Conad-Fascia2' e' il nome del volantino e 008625 e' il codice del negozio.
Nella pagina c'e' il pulsante "Download PDF" in alto a destra.

Nel file della citta' ogni volantino e' una riga:
  {"id": "008625", "volantino": "Spazio-Conad-Fascia2", "nota": "Spazio Conad, Viale Antium 4"}

Oppure, se non conosci i nomi dei volantini, basta l'indirizzo della scheda del negozio: il programma
apre la scheda, legge da solo i volantini disponibili e li scarica tutti:
  {"id": "010443", "scheda": "https://www.conad.it/ricerca-negozi/conad-via-carlo-cattaneo-22-00048-nettuno--010443",
   "nota": "Conad Via Carlo Cattaneo 22"}

Se i due volantini hanno contenuto diverso vengono salvati come conad.pdf e conad_2.pdf
(se sono uguali ne viene tenuto uno solo). Nell'elenco (elenco.json) restano titolo e scadenza.
"""

import re
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from playwright.sync_api import TimeoutError as PlaywrightTimeout

import comune

NOME = "conad"
GIORNI = [1, 2, 4, 5]   # martedi, mercoledi, venerdi, sabato (i volantini cambiano di solito il martedi o il venerdi)
CONDIVISO = False


def url_conad(negozio):
    return f"https://www.conad.it/volantini/{negozio['volantino']}?anacanId={negozio['id']}"


def trova_pulsante(pagina):
    """Trova il pulsante 'Download PDF'."""
    nome = re.compile(r"download\s*pdf|scarica\s*(il\s*)?pdf", re.I)
    for frame in comune.tutti_i_frame(pagina):
        candidati = [
            ("pulsante 'Download PDF'", frame.get_by_role("button", name=nome)),
            ("link 'Download PDF'", frame.get_by_role("link", name=nome)),
            ("testo 'Download PDF'", frame.get_by_text(nome)),
            ("link a un file .pdf", frame.locator('a[href*=".pdf"]')),
        ]
        for come, loc in candidati:
            try:
                el = loc.first
                if el.count() > 0 and el.is_visible():
                    return el, come
            except Exception:
                continue
    return None, None


def leggi_titolo_e_scadenza(pagina):
    """Dalla barra sopra il volantino: 'Super Formati Super Prezzi' / 'Scade lunedi 02/11'."""
    info = {}
    try:
        righe = [r.strip() for r in pagina.inner_text("body").splitlines() if r.strip()]
    except Exception:
        return info
    for i, riga in enumerate(righe):
        trovato = re.match(r"scade\s+\S+\s+(\d{1,2})/(\d{1,2})", riga, re.I)
        if trovato:
            giorno, mese = int(trovato.group(1)), int(trovato.group(2))
            oggi = datetime.now(ZoneInfo("Europe/Rome")).date()
            try:
                scadenza = date(oggi.year, mese, giorno)
                if scadenza < oggi - timedelta(days=60):
                    scadenza = date(oggi.year + 1, mese, giorno)
                info["valido_al"] = scadenza.isoformat()
            except ValueError:
                pass
            info["scadenza_testo"] = riga
            if i > 0:
                info["titolo"] = righe[i - 1]
            break
    return info


def stampa_altri_volantini(pagina):
    """Scrive nel log gli altri volantini del negozio che compaiono nella pagina (servira' per trovarli da soli)."""
    try:
        link = pagina.evaluate(
            "() => Array.from(new Set(Array.from(document.querySelectorAll('a[href*=\"/volantini/\"]')).map(a => a.href)))"
        )
    except Exception:
        return
    if link:
        print(f"    altri indirizzi 'volantini' nella pagina ({len(link)}):")
        for indirizzo in link[:15]:
            print(f"      {indirizzo}")


def apri(pagina, negozio):
    return apri_url(pagina, url_conad(negozio))


def apri_url(pagina, indirizzo):
    """Apre il volantino. Restituisce (pulsante, come, info) oppure (None, None, None)."""
    print(f"    apro {indirizzo}")
    try:
        risposta = pagina.goto(indirizzo, wait_until="domcontentloaded", timeout=60000)
    except PlaywrightTimeout:
        print("    pagina non caricata in tempo")
        return None, None, None
    if risposta is not None and risposta.status >= 400:
        print(f"    pagina non trovata (stato {risposta.status})")
        return None, None, None
    pagina.wait_for_timeout(5000)
    comune.prova_chiudi_cookie(pagina)

    for giro in range(10):
        pulsante, come = trova_pulsante(pagina)
        if pulsante is not None:
            info = {"indirizzo": indirizzo}
            info.update(leggi_titolo_e_scadenza(pagina))
            if info.get("titolo") or info.get("scadenza_testo"):
                print(f"    volantino: {info.get('titolo')!r}, {info.get('scadenza_testo')!r}")
            stampa_altri_volantini(pagina)
            return pulsante, come, info
        if giro == 3:
            comune.prova_chiudi_cookie(pagina)
        pagina.wait_for_timeout(1500)
    return None, None, None


def scopri_volantini(contesto, negozio):
    """Apre la scheda del negozio e legge i volantini disponibili.
    Restituisce (lista di indirizzi, scheda_caricata_bene)."""
    scheda = negozio["scheda"]
    pagina = contesto.new_page()
    try:
        print(f"    apro la scheda del negozio {scheda}")
        try:
            risposta = pagina.goto(scheda, wait_until="domcontentloaded", timeout=60000)
        except PlaywrightTimeout:
            print("    scheda non caricata in tempo")
            return [], False
        if risposta is not None and risposta.status >= 400:
            print(f"    scheda non trovata (stato {risposta.status})")
            return [], False
        pagina.wait_for_timeout(5000)
        comune.prova_chiudi_cookie(pagina)

        link, vista_sezione = [], False
        for giro in range(10):
            try:
                link = pagina.evaluate(
                    "() => Array.from(new Set(Array.from(document.querySelectorAll('a[href*=\"/volantini/\"]')).map(a => a.href)))"
                )
                vista_sezione = bool(re.search(r"volantini\s+disponibili", pagina.inner_text("body"), re.I))
            except Exception:
                pass
            if any("anacanid" in l.lower() for l in link):
                break
            if giro == 3:
                comune.prova_chiudi_cookie(pagina)
            pagina.wait_for_timeout(1500)

        for l in link:
            print(f"      indirizzo trovato: {l}")
        scelti = [l for l in link if "anacanid" in l.lower()]
        if not scelti and not vista_sezione:
            comune.salva_debug(pagina, f"conad-scheda-{negozio.get('id', 'x')}")
        return scelti[:6], bool(scelti) or vista_sezione
    finally:
        pagina.close()


def scarica(contesto, negozio, etichetta):
    """Scarica un volantino (se il negozio ha 'volantino') oppure tutti quelli della scheda del negozio.
    Restituisce (file temporaneo, info) oppure, per la scheda, una lista di coppie (file, info)."""
    if negozio.get("volantino"):
        etichetta = f"{etichetta}_{negozio['volantino']}"
        return comune.scarica_da_pulsante(
            contesto, etichetta, lambda pagina: apri(pagina, negozio), prova_diretto=True
        )

    indirizzi, scheda_ok = scopri_volantini(contesto, negozio)
    if not scheda_ok:
        print(f"[ERRORE] {etichetta}: non riesco a leggere i volantini dalla scheda del negozio")
        return [(None, None)]
    if not indirizzi:
        print(f"    {etichetta}: la scheda del negozio non elenca volantini")
        return []

    risultati = []
    for indirizzo in indirizzi:
        nome = re.sub(r"[^A-Za-z0-9]+", "-", indirizzo.split("?")[0].rstrip("/").split("/")[-1])
        risultati.append(
            comune.scarica_da_pulsante(
                contesto, f"{etichetta}_{nome}", lambda pagina, i=indirizzo: apri_url(pagina, i), prova_diretto=True
            )
        )
    return risultati
