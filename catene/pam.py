"""
Pam Panorama: ogni punto vendita ha una pagina con i suoi volantini.
Es. Nettuno: https://www.pampanorama.it/punti-vendita/roma-nettuno

La pagina del negozio contiene i link ai volantini (ce ne puo' essere piu' di uno:
quello normale e le "Occasioni Extra"). Ogni volantino si apre sul sito volantinopiu.com,
dove c'e' il link "Scarica PDF" che punta direttamente al file.

Nel file della citta' serve "id": la parte finale dell'indirizzo (es. roma-nettuno).
"""

import re
from datetime import date
from urllib.parse import unquote

import comune

NOME = "pam"
GIORNI = [3, 4, 5]   # il volantino cambia di solito il giovedi
CONDIVISO = False

MESI = {"gennaio": 1, "febbraio": 2, "marzo": 3, "aprile": 4, "maggio": 5, "giugno": 6, "luglio": 7,
        "agosto": 8, "settembre": 9, "ottobre": 10, "novembre": 11, "dicembre": 12}
RE_VALIDITA = re.compile(r"dal\s+(\d{1,2})\s+([a-zà]+)\s+al\s+(\d{1,2})\s+([a-zà]+)(?:\s+(\d{4}))?", re.I)


def url_negozio(id_negozio):
    return f"https://www.pampanorama.it/punti-vendita/{id_negozio}"


def leggi_validita(titolo):
    """'Offerte valide dal 22 Ottobre al 4 Novembre' -> ('2026-10-22', '2026-11-04')."""
    m = RE_VALIDITA.search(titolo or "")
    if not m:
        return None, None
    g1, m1, g2, m2, anno = m.groups()
    m1, m2 = MESI.get(m1.lower()), MESI.get(m2.lower())
    if not m1 or not m2:
        return None, None
    anno = int(anno) if anno else date.today().year
    try:
        dal = date(anno, m1, int(g1))
        al = date(anno + (1 if m2 < m1 else 0), m2, int(g2))
    except ValueError:
        return None, None
    return dal.isoformat(), al.isoformat()


def link_volantini(pagina):
    trovati = []
    hrefs = pagina.eval_on_selector_all("a[href]", "els => els.map(e => e.href)")
    for h in hrefs:
        m = re.search(r"link=([^&]+)", h)
        if m and "volantinopiu" in h:
            u = unquote(m.group(1))
            if u not in trovati:
                trovati.append(u)
    return trovati


def scarica_uno(contesto, pagina, url, etichetta):
    pagina.goto(url, wait_until="domcontentloaded", timeout=60000)
    pagina.wait_for_timeout(6000)
    comune.prova_chiudi_cookie(pagina)
    titolo = re.sub(r"^\s*PAM Panorama\s*-\s*", "", pagina.title() or "").strip()
    href = pagina.eval_on_selector_all(
        'a[aria-label*="scarica pdf" i], a[href*=".pdf"]',
        "els => (els.map(e => e.href).find(h => /\\.pdf/i.test(h)) || '')",
    )
    if not href:
        print(f"[ERRORE] {etichetta}: link 'Scarica PDF' non trovato in {url}")
        comune.salva_debug(pagina, comune.slug(etichetta))
        return None, None
    risposta = contesto.request.get(href, timeout=120000)
    corpo = risposta.body()
    if not (risposta.ok and corpo[:5] == b"%PDF-"):
        print(f"[ERRORE] {etichetta}: {href[:120]} non e' un PDF (stato {risposta.status})")
        return None, None
    comune.CARTELLA_TMP.mkdir(exist_ok=True)
    file = comune.CARTELLA_TMP / f"{comune.slug(etichetta)}.pdf"
    file.write_bytes(corpo)
    dal, al = leggi_validita(titolo)
    info = {"titolo": titolo}
    if dal and al:
        info.update({"valido_dal": dal, "valido_al": al})
    print(f"[ok] {etichetta}: PDF scaricato ({len(corpo) // 1024} KB) - {titolo!r}")
    return file, info


def scarica(contesto, negozio, etichetta):
    """Restituisce una lista di (file temporaneo, info), uno per ogni volantino del negozio."""
    pagina = contesto.new_page()
    risultati = []
    try:
        pagina.goto(url_negozio(negozio["id"]), wait_until="domcontentloaded", timeout=60000)
        pagina.wait_for_timeout(8000)
        comune.prova_chiudi_cookie(pagina)
        link = link_volantini(pagina)
        print(f"    volantini trovati per {negozio['id']}: {len(link)}")
        if not link:
            print(f"[ERRORE] {etichetta}: nessun link ai volantini nella pagina del negozio")
            comune.salva_debug(pagina, comune.slug(etichetta))
            return [(None, None)]
        for i, u in enumerate(link[:4], 1):
            try:
                risultati.append(scarica_uno(contesto, pagina, u, f"{etichetta}_{i}"))
            except Exception as errore:
                print(f"[ERRORE] {etichetta}_{i}: {str(errore).splitlines()[0][:200]}")
                risultati.append((None, None))
    except Exception as errore:
        print(f"[ERRORE] {etichetta}: {str(errore).splitlines()[0][:200]}")
        return [(None, None)]
    finally:
        pagina.close()
    return risultati
