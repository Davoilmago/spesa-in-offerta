"""
Dpiù (discount): i volantini sono PDF pubblicati su https://www.d-piu.com (es. https://www.d-piu.com/flyer/flyer-1.pdf).
Ogni volantino elenca in fondo i punti vendita dove vale ("OFFERTE VALIDE NEI PUNTI VENDITA DI: ...").
Il modulo raccoglie i PDF dal sito (link visti nella pagina + flyer-1 ... flyer-8), li scarica e tiene
SOLO quelli che nel testo nominano il negozio (parole di "cerca", es. "Bortolotti").
Le date si leggono dalla copertina ("DAL 5 AL 14 NOVEMBRE 2026").

Nel file della citta':  "dpiu": [{"nota": "Dpiù Borgo Sabotino, Via G. Bortolotti 3", "cerca": ["Bortolotti"]}]
"""

import re
import subprocess
from datetime import date

import comune

NOME = "dpiu"
GIORNI = [0, 3, 4]
CONDIVISO = False

SITO = "https://www.d-piu.com"
MESI = {"gennaio": 1, "febbraio": 2, "marzo": 3, "aprile": 4, "maggio": 5, "giugno": 6, "luglio": 7,
        "agosto": 8, "settembre": 9, "ottobre": 10, "novembre": 11, "dicembre": 12}
RE_DATE = re.compile(r"dal\s+(\d{1,2})(?:\s+([a-zà]+))?\s+al\s+(\d{1,2})\s+([a-zà]+)(?:\s+(\d{4}))?", re.I)

_LOG = []
_print = print


def print(*a, **k):
    _print(*a, **k)
    _LOG.append(" ".join(str(x) for x in a))
    try:
        (comune.CARTELLA_PDF / "_log_dpiu.txt").write_text("\n".join(_LOG), encoding="utf-8")
    except Exception:
        pass


def testo_pdf(percorso):
    try:
        return subprocess.run(["pdftotext", "-layout", str(percorso), "-"], capture_output=True, text=True, timeout=120).stdout
    except Exception as e:
        print(f"    pdftotext non disponibile: {e}")
        return ""


def validita(testo):
    for g1, m1, g2, m2, anno in RE_DATE.findall(testo or ""):
        m2n = MESI.get(m2.lower())
        m1n = MESI.get((m1 or "").lower(), m2n)
        if not m2n or not m1n:
            continue
        a = int(anno) if anno else date.today().year
        try:
            return date(a - (1 if m1n > m2n else 0), m1n, int(g1)), date(a, m2n, int(g2))
        except ValueError:
            continue
    return None, None


def scarica(contesto, negozio, etichetta):
    parole = negozio.get("cerca") or []
    if isinstance(parole, str):
        parole = [parole]
    pagina = contesto.new_page()
    visti = []
    pagina.on("response", lambda r: visti.append(r.url) if re.search(r"\.pdf(\?|$)", r.url, re.I) else None)
    risultati = []
    try:
        candidati = []
        try:
            pagina.goto(SITO, wait_until="domcontentloaded", timeout=60000)
            pagina.wait_for_timeout(6000)
            comune.prova_chiudi_cookie(pagina)
            for frame in comune.tutti_i_frame(pagina):
                try:
                    candidati += frame.eval_on_selector_all("a[href]", "els => els.map(e => e.href)")
                except Exception:
                    pass
            testo = re.sub(r"\s+", " ", pagina.inner_text("body"))
            print(f"    pagina {pagina.url}: {testo[:600]!r}")
        except Exception as e:
            print(f"    sito non raggiunto: {str(e).splitlines()[0][:150]}")
        candidati = [h for h in candidati if re.search(r"\.pdf(\?|$)", h, re.I)] + visti
        candidati += [f"{SITO}/flyer/flyer-{i}.pdf" for i in range(1, 9)]
        candidati = list(dict.fromkeys(candidati))
        print(f"    PDF candidati: {candidati}")
        oggi = date.today()
        firme = set()
        for i, url in enumerate(candidati, 1):
            try:
                r = contesto.request.get(url, timeout=120000)
                corpo = r.body()
            except Exception as e:
                print(f"    {url}: non scaricato ({str(e).splitlines()[0][:100]})")
                continue
            if not (r.ok and corpo[:5] == b"%PDF-"):
                print(f"    {url}: non e' un PDF (stato {r.status})")
                continue
            comune.CARTELLA_TMP.mkdir(exist_ok=True)
            file = comune.CARTELLA_TMP / f"{comune.slug(etichetta)}_{i}.pdf"
            file.write_bytes(corpo)
            firma = comune.impronta(file)
            if firma in firme:
                continue
            firme.add(firma)
            t = testo_pdf(file)
            dal, al = validita(t[:3000]) if t else (None, None)
            if al and al < oggi:
                print(f"    salto {url}: scaduto il {al}")
                continue
            if parole and t and not any(p.lower() in t.lower() for p in parole):
                print(f"    salto {url}: non nomina {parole} (dal {dal} al {al})")
                continue
            info = {"titolo": "Volantino Dpiù", "indirizzo": url}
            if dal:
                info["valido_dal"] = dal.isoformat()
            if al:
                info["valido_al"] = al.isoformat()
            print(f"[ok] {etichetta}_{i}: {url} dal {dal} al {al} ({len(corpo) // 1024} KB)")
            risultati.append((file, info))
        if not risultati:
            print(f"[ERRORE] {etichetta}: nessun volantino valido per {parole}")
            return [(None, None)]
    except Exception as errore:
        print(f"[ERRORE] {etichetta}: {str(errore).splitlines()[0][:200]}")
        return [(None, None)]
    finally:
        pagina.close()
    return risultati
