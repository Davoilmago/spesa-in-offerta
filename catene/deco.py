"""
Decò: il volantino NON e' sul sito ufficiale ma sulla piattaforma dei punti vendita:
  https://puntivenditadeco.multicedi.it/it/italia/roma/anzio   (pagina del negozio, pulsante "SFOGLIA IL VOLANTINO")
  -> https://deco.volantinopiu.com/ws/pv003499.php             (volantino digitale)
  -> pagine come immagini: https://resources.volantinopiu.it/flyer/2/9/2/0/3/pagine/1.webp, 2.webp, ...
Non c'e' un PDF da scaricare: scarico le pagine una a una e le unisco in un PDF (stampandole con il browser).

Nel file della citta' serve l'indirizzo della pagina del negozio:
  "deco": [{"nota": "Decò Via di Valle Schioia 67", "pagina": "https://puntivenditadeco.multicedi.it/it/italia/roma/anzio"}]
Le date di validita' si leggono dalla copertina (se il testo della pagina non le riporta).
"""
import base64
import re

import comune

NOME = "deco"
GIORNI = [0, 3, 4]
CONDIVISO = False
PAGINA_DEFAULT = "https://puntivenditadeco.multicedi.it/it/italia/roma/anzio"

_LOG = []
_print = print


def print(*a, **k):
    _print(*a, **k)
    _LOG.append(" ".join(str(x) for x in a))
    try:
        (comune.CARTELLA_PDF / "_log_deco.txt").write_text("\n".join(_LOG), encoding="utf-8")
    except Exception:
        pass


def scarica(contesto, negozio, etichetta):
    pagina = contesto.new_page()
    pagina.set_default_timeout(25000)
    viste = {}
    pagina.on("response", lambda r: viste.setdefault(r.url, r.status) if re.search(r"volantinopiu", r.url) else None)
    try:
        pagina.goto(negozio.get("pagina", PAGINA_DEFAULT), wait_until="domcontentloaded", timeout=40000)
        pagina.wait_for_timeout(6000)
        comune.prova_chiudi_cookie(pagina)
        href = pagina.eval_on_selector_all(
            "a[href*='volantinopiu']", "els => (els.map(e => e.href)[0] || '')")
        if not href:
            print(f"[ERRORE] {etichetta}: link 'SFOGLIA IL VOLANTINO' non trovato")
            comune.salva_debug(pagina, comune.slug(etichetta))
            return [(None, None)]
        print(f"    viewer: {href}")
        pagina.goto(href, wait_until="domcontentloaded", timeout=40000)
        pagina.wait_for_timeout(9000)
        try:
            print(f"    testo viewer: {re.sub(chr(10), ' ', pagina.inner_text('body'))[:500]!r}")
        except Exception:
            pass
        base = None
        for u in list(viste):
            m = re.search(r"(https://resources[a-z]*\.volantinopiu\.it/flyer/[\d/]+)/pagine/\d+\.webp", u)
            if m:
                base = m.group(1)
                break
        if not base:
            try:
                html = pagina.content()
                m = re.search(r"(https://resources[a-z]*\.volantinopiu\.it/flyer/[\d/]+)/pagine/", html)
                base = m.group(1) if m else None
            except Exception:
                pass
        print(f"    cartella pagine: {base}; richieste viste: {list(viste.items())[:8]}")
        if not base:
            print(f"[ERRORE] {etichetta}: pagine del volantino non trovate")
            comune.salva_debug(pagina, comune.slug(etichetta))
            return [(None, None)]
        immagini = []
        for n in range(1, 81):
            r = contesto.request.get(f"{base}/pagine/{n}.webp", timeout=60000)
            if not r.ok or len(r.body()) < 2000:
                break
            immagini.append(r.body())
        print(f"    pagine scaricate: {len(immagini)} ({sum(len(x) for x in immagini) // 1024} KB)")
        if len(immagini) < 2:
            print(f"[ERRORE] {etichetta}: troppo poche pagine")
            return [(None, None)]
        # unisco le immagini in un PDF stampandole con il browser
        w = pagina.evaluate("""async (b64) => { const i = new Image(); i.src = 'data:image/webp;base64,' + b64;
            await i.decode(); return [i.naturalWidth, i.naturalHeight]; }""", base64.b64encode(immagini[0]).decode())
        print(f"    dimensione pagina: {w}")
        html = ("<html><head><style>@page{size:%dpx %dpx;margin:0}html,body{margin:0;padding:0}"
                "img{display:block;width:%dpx;height:%dpx;page-break-after:always}</style></head><body>" % (w[0], w[1], w[0], w[1])
                + "".join(f'<img src="data:image/webp;base64,{base64.b64encode(x).decode()}">' for x in immagini)
                + "</body></html>")
        stampa = contesto.new_page()
        stampa.set_content(html, wait_until="load", timeout=120000)
        comune.CARTELLA_TMP.mkdir(exist_ok=True)
        file = comune.CARTELLA_TMP / f"{comune.slug(etichetta)}.pdf"
        stampa.pdf(path=str(file), width=f"{w[0]}px", height=f"{w[1]}px", print_background=True)
        stampa.close()
        print(f"[ok] {etichetta}: {len(immagini)} pagine unite in PDF ({file.stat().st_size // 1024} KB)")
        return [(file, {"titolo": "Volantino Decò", "indirizzo": href})]
    except Exception as errore:
        print(f"[ERRORE] {etichetta}: {str(errore).splitlines()[0][:200]}")
        return [(None, None)]
    finally:
        for p in list(contesto.pages):
            try:
                p.close()
            except Exception:
                pass
