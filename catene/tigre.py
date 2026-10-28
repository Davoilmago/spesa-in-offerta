"""
Tigre Amico (Oasi Tigre, gruppo Gabrielli): https://www.oasitigre.it
Ogni negozio ha una pagina "il-mio-negozio.<ID>.html" (Anzio, Via Matteotti 18 = 6507) con i pulsanti
"Sfoglia volantino": ognuno apre un libro Calameo (https://www.calameo.com/read/<bkcode>).
Il volantino delle offerte ha un nome tipo "A23_2026"; "Buoni e Fissi" e' il catalogo fedelta' (non lo scarico).
Le pagine Calameo sono SVG (p1.svgz, p2.svgz...) con un token di accesso: le scarico, le disegno col browser
e le unisco in un PDF.

Nel file della citta':  "tigre": [{"nota": "Tigre Amico Via Matteotti 18", "id": "6507"}]
"""
import base64
import gzip
import json
import re

import comune

NOME = "tigre"
GIORNI = [0, 3, 4]
CONDIVISO = False
PAGINA = "https://www.oasitigre.it/it/il-mio-negozio.{id}.html"

_LOG = []
_print = print


def print(*a, **k):
    _print(*a, **k)
    _LOG.append(" ".join(str(x) for x in a))
    try:
        (comune.CARTELLA_PDF / "_log_tigre.txt").write_text("\n".join(_LOG), encoding="utf-8")
    except Exception:
        pass


def libro(contesto, bk, etichetta):
    """Scarica le pagine SVG del libro Calameo e le unisce in un PDF. Restituisce il file o None."""
    pag = contesto.new_page()
    pag.set_default_timeout(25000)
    visti, dati = [], {}

    def risposta(r):
        if "ps.calameoassets.com" in r.url and ".svgz" in r.url:
            visti.append(r.url)
        if "book/get" in r.url and bk in r.url:
            try:
                dati["book"] = json.loads(r.text())
            except Exception:
                pass
    pag.on("response", risposta)
    try:
        pag.goto(f"https://v.calameo.com/?bkcode={bk}&mode=mini&view=scroll&clickto=view&clicktarget=_blank",
                 wait_until="domcontentloaded", timeout=40000)
        pag.wait_for_timeout(9000)
        n = (dati.get("book", {}).get("content", {}).get("document", {}) or {}).get("pages")
        key = (dati.get("book", {}).get("content", {}) or {}).get("key")
        print(f"    libro {bk}: pagine={n} key={key} svgz visti={len(visti)}")
        if not (n and key and visti):
            return None
        m = re.match(r"https://ps\.calameoassets\.com/([^/]+)/p\d+\.svgz\?(.*)$", visti[0])
        if not m:
            return None
        coda = m.group(2)
        print(f"    token: {coda[:200]}")
        svgs = []
        for i in range(1, int(n) + 1):
            r = contesto.request.get(f"https://ps.calameoassets.com/{key}/p{i}.svgz?{coda}",
                                     headers={"Referer": "https://v.calameo.com/"}, timeout=60000)
            corpo = r.body()
            if corpo[:2] == b"\x1f\x8b":
                corpo = gzip.decompress(corpo)
            if not r.ok or b"<svg" not in corpo[:2000]:
                print(f"    pagina {i}: stato {r.status}, {len(corpo)} byte, non SVG: {corpo[:80]!r}")
                break
            svgs.append(corpo)
        print(f"    pagine SVG scaricate: {len(svgs)} ({sum(len(x) for x in svgs) // 1024} KB)")
        if not svgs:
            return None
        print(f"    inizio svg 1: {svgs[0][:500]!r}")
        print(f"    href esterni svg 1: {len(re.findall(rb'href=\"http', svgs[0]))}; immagini incorporate: {len(re.findall(rb'data:image', svgs[0]))}")
        mw = re.search(rb'viewBox="[\d.\-]+ [\d.\-]+ ([\d.]+) ([\d.]+)"', svgs[0]) or re.search(rb'width="([\d.]+)[a-z]*" height="([\d.]+)', svgs[0])
        w, h = (float(mw.group(1)), float(mw.group(2))) if mw else (807.0, 765.0)
        scala = 1400 / h if h else 1.5
        W, H = int(w * scala), int(h * scala)
        rend = contesto.new_page()
        rend.set_viewport_size({"width": W, "height": H})
        jpgs = []
        for s in svgs:
            rend.set_content('<html><body style="margin:0;background:#fff"><img style="width:%dpx;height:%dpx;display:block" src="data:image/svg+xml;base64,%s"></body></html>'
                             % (W, H, base64.b64encode(s).decode()), wait_until="load")
            rend.wait_for_timeout(300)
            jpgs.append("data:image/jpeg;base64," + base64.b64encode(rend.screenshot(type="jpeg", quality=82)).decode())
        rend.close()
        html = ("<html><head><style>@page{size:%dpx %dpx;margin:0}html,body{margin:0;padding:0}"
                "img{display:block;width:%dpx;height:%dpx;page-break-after:always}</style></head><body>" % (W, H, W, H)
                + "".join(f'<img src="{j}">' for j in jpgs) + "</body></html>")
        stampa = contesto.new_page()
        stampa.set_content(html, wait_until="load", timeout=120000)
        comune.CARTELLA_TMP.mkdir(exist_ok=True)
        file = comune.CARTELLA_TMP / f"{comune.slug(etichetta)}_{bk[-6:]}.pdf"
        stampa.pdf(path=str(file), width=f"{W}px", height=f"{H}px", print_background=True)
        stampa.close()
        print(f"    PDF {file.name}: {len(svgs)} pagine, {file.stat().st_size // 1024} KB")
        return file
    finally:
        try:
            pag.close()
        except Exception:
            pass


def scarica(contesto, negozio, etichetta):
    pagina = contesto.new_page()
    pagina.set_default_timeout(25000)
    try:
        url = PAGINA.format(id=negozio.get("id", "6507"))
        pagina.goto(url, wait_until="domcontentloaded", timeout=40000)
        pagina.wait_for_timeout(6000)
        comune.prova_chiudi_cookie(pagina)
        bott = pagina.eval_on_selector_all(
            "a.gotoVolantino", "els => els.map(e => [e.dataset.id || '', e.dataset.url || '', (e.closest('div,li,section') ? e.closest('div,li,section').innerText : '').replace(/\\s+/g,' ').slice(0,200)])")
        print(f"    volantini nella pagina: {bott}")
        risultati = []
        for did, href, testo in bott:
            if re.search(r"buoni|fissi", did, re.I):
                continue
            bk = re.search(r"/read/([0-9a-z]+)", href)
            if not bk:
                continue
            f = libro(contesto, bk.group(1), etichetta)
            if f:
                risultati.append((f, {"titolo": f"Volantino Tigre Amico {did}", "indirizzo": href}))
        if not risultati:
            print(f"[ERRORE] {etichetta}: nessun volantino scaricato")
            return [(None, None)]
        print(f"[ok] {etichetta}: {len(risultati)} volantino/i")
        return risultati
    except Exception as errore:
        print(f"[ERRORE] {etichetta}: {str(errore).splitlines()[0][:200]}")
        return [(None, None)]
    finally:
        for p in list(contesto.pages):
            try:
                p.close()
            except Exception:
                pass
