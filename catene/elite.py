"""
Elite Supermercati: i volantini sono pubblicati su https://superelite.it/promozioni
Ogni promozione ha la sua pagina (es. /promozioni/sottocosto) con il link "Scarica in PDF"
(index.php?option=com_myegojwt&view=flyer&id=NNNNN&pdf=1). Quasi tutti i volantini valgono per
tutti i negozi (con qualche eccezione scritta nella pagina), quindi si scarica una volta sola.
Tengo solo quelli ancora validi oggi.

Nel file della citta' basta scrivere:  "elite": [{"nota": "Elite Via De Gasperi 14"}]
"""

import re
from datetime import date

import comune

NOME = "elite"
GIORNI = [0, 3, 4]   # lunedi, giovedi, venerdi
CONDIVISO = True

MESI = {"gennaio": 1, "febbraio": 2, "marzo": 3, "aprile": 4, "maggio": 5, "giugno": 6, "luglio": 7,
        "agosto": 8, "settembre": 9, "ottobre": 10, "novembre": 11, "dicembre": 12}
RE_DATE = re.compile(r"dal\s+(\d{1,2})(?:\s+([a-zà]+))?\s+al\s+(\d{1,2})\s+([a-zà]+)(?:\s+(\d{4}))?", re.I)
CITTA = "nettuno"


def chiave_condivisione(negozio):
    return "tutti"


def validita(testo):
    """Restituisce (dal, al) con la data di fine piu' lontana trovata nella pagina."""
    migliore = (None, None)
    for g1, m1, g2, m2, anno in RE_DATE.findall(testo or ""):
        m2n = MESI.get(m2.lower())
        m1n = MESI.get((m1 or "").lower(), m2n)
        if not m2n:
            continue
        a = int(anno) if anno else date.today().year
        try:
            dal = date(a - (1 if m1n and m1n > m2n else 0), m1n, int(g1))
            al = date(a, m2n, int(g2))
        except (ValueError, TypeError):
            continue
        if migliore[1] is None or al > migliore[1]:
            migliore = (dal, al)
    return migliore


def vale_per_nettuno(testo):
    """Esclude i volantini scritti 'solo per' altri negozi."""
    t = (testo or "").lower()
    if "nettuno" in t:
        return True
    return not re.search(r"valid\w*\s+(solo|esclusivamente)|solo\s+(nei|negli|per i)\s+(negozi|punti)", t)


def scarica(contesto, negozio, etichetta):
    pagina = contesto.new_page()
    risultati = []
    try:
        pagina.goto("https://superelite.it/promozioni", wait_until="domcontentloaded", timeout=60000)
        pagina.wait_for_timeout(5000)
        comune.prova_chiudi_cookie(pagina)
        hrefs = pagina.eval_on_selector_all("a[href*='/promozioni/']", "els => els.map(e => e.href)")
        pagine = []
        for h in hrefs:
            h = h.split("#")[0].split("?")[0]
            if re.search(r"/promozioni/[^/]+$", h) and h not in pagine:
                pagine.append(h)
        print(f"    promozioni trovate: {len(pagine)}")
        oggi = date.today()
        for i, url in enumerate(pagine[:12], 1):
            try:
                pagina.goto(url, wait_until="domcontentloaded", timeout=60000)
                pagina.wait_for_timeout(3500)
                testo = pagina.inner_text("body")
                dal, al = validita(testo)
                if al is None or al < oggi:
                    print(f"    salto {url}: scaduta o senza date ({al})")
                    continue
                if not vale_per_nettuno(testo):
                    print(f"    salto {url}: non vale per Nettuno")
                    continue
                href = pagina.eval_on_selector_all(
                    "a[href*='pdf=1'], a[href*='.pdf']", "els => (els.map(e => e.href)[0] || '')")
                if not href:
                    print(f"[ERRORE] {etichetta}_{i}: link PDF non trovato in {url}")
                    risultati.append((None, None))
                    continue
                r = contesto.request.get(href, timeout=120000)
                corpo = r.body()
                if not (r.ok and corpo[:5] == b"%PDF-"):
                    print(f"[ERRORE] {etichetta}_{i}: {href[:100]} non e' un PDF (stato {r.status})")
                    risultati.append((None, None))
                    continue
                comune.CARTELLA_TMP.mkdir(exist_ok=True)
                file = comune.CARTELLA_TMP / f"{comune.slug(etichetta)}_{i}.pdf"
                file.write_bytes(corpo)
                info = {"titolo": pagina.title(), "indirizzo": url}
                if dal:
                    info["valido_dal"] = dal.isoformat()
                info["valido_al"] = al.isoformat()
                print(f"[ok] {etichetta}_{i}: {url} fino al {al} ({len(corpo) // 1024} KB)")
                risultati.append((file, info))
            except Exception as errore:
                print(f"[ERRORE] {etichetta}_{i}: {str(errore).splitlines()[0][:200]}")
                risultati.append((None, None))
        if not risultati:
            print(f"[ERRORE] {etichetta}: nessun volantino valido trovato")
            return [(None, None)]
    except Exception as errore:
        print(f"[ERRORE] {etichetta}: {str(errore).splitlines()[0][:200]}")
        return [(None, None)]
    finally:
        pagina.close()
    return risultati
