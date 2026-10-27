"""
iN's Mercato: la pagina https://www.insmercato.it/volantino/ ha tre menu (Provincia, Citta', Filiale).
Dopo aver scelto la filiale, il pulsante "SCARICA IL PDF" diventa un link diretto al file, ad esempio
https://insmercato-cdn.it/insmercato/volantino/22/lfxsip/pdf/volantino-A.pdf

Nel file della citta' servono per ogni negozio: "provincia", "citta'" e "filiale" cosi' come compaiono nei menu
(es. Roma / Nettuno / Via Ugo La Malfa, 9). Le date si leggono dal PDF stesso.
"""

import re
import shutil
import subprocess
from datetime import date

import comune

_LOG = []
_print = print


def print(*a, **k):
    _print(*a, **k)
    _LOG.append(" ".join(str(x) for x in a))
    try:
        (comune.CARTELLA_PDF / "_log_ins.txt").write_text("\n".join(_LOG), encoding="utf-8")
    except Exception:
        pass


NOME = "ins"
GIORNI = [0, 1, 3, 4]   # lunedi, martedi, giovedi, venerdi (i volantini cambiano a meta' settimana)
CONDIVISO = False


def scegli(pagina, indice, cerca):
    menu = pagina.locator("select").nth(indice)
    opzioni = menu.evaluate("e => [...e.options].map(o => [o.value, o.text])")
    scelto = next((v for v, t in opzioni if cerca.lower() in t.lower()), None)
    if scelto is None:
        print(f"    nel menu {indice} non trovo {cerca!r}: {[t for _, t in opzioni][:15]}")
        return False
    menu.select_option(scelto)
    pagina.wait_for_timeout(2500)
    return True


MESI = {"gennaio": 1, "febbraio": 2, "marzo": 3, "aprile": 4, "maggio": 5, "giugno": 6, "luglio": 7,
        "agosto": 8, "settembre": 9, "ottobre": 10, "novembre": 11, "dicembre": 12}
RE_DATE = re.compile(r"dal\s+(\d{1,2})\s*(?:([a-z]+)\s+)?al\s+(\d{1,2})\s+([a-z]+)\s*(\d{4})?", re.I)


def date_dalla_copertina(pdf):
    """La copertina e' un'immagine con scritto 'DAL 21 OTTOBRE AL 1 NOVEMBRE 2026': la leggo con l'OCR.
    Restituisce (dal, al) come testo ISO, oppure (None, None) se non riesce."""
    if not (shutil.which("pdftoppm") and shutil.which("tesseract")):
        print("    OCR non disponibile: date non lette")
        return None, None
    try:
        base = comune.CARTELLA_TMP / "ins_cop"
        testo = ""
        for ritaglio in (["-x", "0", "-y", "1000", "-W", "900", "-H", "300"], []):
            for f in comune.CARTELLA_TMP.glob("ins_cop*.png"):
                f.unlink(missing_ok=True)
            subprocess.run(["pdftoppm", "-png", "-r", "110", "-f", "1", "-l", "1", *ritaglio, str(pdf), str(base)], check=True, timeout=60)
            immagine = next(comune.CARTELLA_TMP.glob("ins_cop*.png"))
            testo = subprocess.run(["tesseract", str(immagine), "stdout", "--psm", "6"], capture_output=True, text=True, timeout=90).stdout
            m = RE_DATE.search(testo.replace("\n", " "))
            if m:
                g1, m1, g2, m2, anno = m.groups()
                m2 = MESI.get((m2 or "").lower())
                m1 = MESI.get((m1 or "").lower(), m2)
                if m1 and m2:
                    a = int(anno) if anno else date.today().year
                    dal = date(a - (1 if m1 > m2 else 0), m1, int(g1))
                    al = date(a, m2, int(g2))
                    print(f"    date lette dalla copertina: {dal} - {al}")
                    return dal.isoformat(), al.isoformat()
        print(f"    date non trovate nella copertina: {testo[:120]!r}")
    except Exception as errore:
        print(f"    lettura delle date non riuscita: {str(errore)[:120]}")
    finally:
        for f in comune.CARTELLA_TMP.glob("ins_cop*.png"):
            f.unlink(missing_ok=True)
    return None, None


def scarica(contesto, negozio, etichetta):
    pagina = contesto.new_page()
    try:
        pagina.goto("https://www.insmercato.it/volantino/", wait_until="domcontentloaded", timeout=60000)
        pagina.wait_for_timeout(6000)
        comune.prova_chiudi_cookie(pagina)
        scelte = [negozio.get("provincia", "Roma"), negozio.get("citta", "Nettuno"), negozio.get("filiale", "")]
        for i, cerca in enumerate(scelte):
            if not scegli(pagina, i, cerca):
                comune.salva_debug(pagina, comune.slug(etichetta))
                return [(None, None)]
        href = pagina.eval_on_selector_all(
            "a[href]", "els => (els.find(e => /scarica il pdf/i.test(e.innerText||'')) || {}).href || ''")
        if not re.search(r"\.pdf", href or "", re.I):
            print(f"[ERRORE] {etichetta}: link 'Scarica il pdf' non trovato ({href!r})")
            comune.salva_debug(pagina, comune.slug(etichetta))
            return [(None, None)]
        print(f"    PDF: {href}")
        risposta = contesto.request.get(href, timeout=120000)
        corpo = risposta.body()
        if not (risposta.ok and corpo[:5] == b"%PDF-"):
            print(f"[ERRORE] {etichetta}: la risposta non e' un PDF (stato {risposta.status})")
            return [(None, None)]
        comune.CARTELLA_TMP.mkdir(exist_ok=True)
        file = comune.CARTELLA_TMP / f"{comune.slug(etichetta)}.pdf"
        file.write_bytes(corpo)
        m = re.search(r"/volantino/(\d+)/", href)
        info = {"titolo": f"Volantino {m.group(1)}" if m else ""}
        dal, al = date_dalla_copertina(file)
        if dal and al:
            info.update({"valido_dal": dal, "valido_al": al})
        print(f"[ok] {etichetta}: PDF scaricato ({len(corpo) // 1024} KB)")
        return [(file, info)]
    except Exception as errore:
        print(f"[ERRORE] {etichetta}: {str(errore).splitlines()[0][:200]}")
        return [(None, None)]
    finally:
        pagina.close()
