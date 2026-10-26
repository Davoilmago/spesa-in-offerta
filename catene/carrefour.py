"""
Carrefour: ogni punto vendita ha una pagina con i suoi volantini.
Es. Nettuno: https://www.carrefour.it/volantino/supermercato-carrefour-market-nettuno-via-trieste-78/5208

VERSIONE DI ESPLORAZIONE: scrive nel log cosa trova (link, pulsanti, risposte di rete)
per capire come scaricare il PDF. Per ogni negozio serve "id" (es. 5208) e "url" (la pagina del negozio).
"""

import contextlib
import io
import re
from pathlib import Path

import comune

LOG = Path("volantini/_debug/carrefour.txt")
NOME = "carrefour"
GIORNI = [0, 1, 2, 3, 4, 5, 6]
CONDIVISO = False


def log(testo):
    print(testo)
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(testo + "\n")


def elementi(pagina, titolo):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        comune.stampa_elementi_visibili(pagina, titolo)
    log(buf.getvalue().rstrip())


def scarica(contesto, negozio, etichetta):
    pagina = contesto.new_page()
    risposte = []
    pagina.on("response", lambda r: risposte.append((r.status, r.request.resource_type, r.url))
              if re.search(r"pdf|flyer|volantin|leaflet|publitas|issuu|shopfully|page", r.url, re.I) else None)
    try:
        url = negozio["url"]
        log(f"=== apro {url}")
        pagina.goto(url, wait_until="domcontentloaded", timeout=60000)
        pagina.wait_for_timeout(8000)
        comune.prova_chiudi_cookie(pagina)
        pagina.wait_for_timeout(1500)
        log(f"titolo: {pagina.title()!r}")
        hrefs = pagina.eval_on_selector_all(
            "a[href]", "els => els.map(e => (e.innerText||'').trim().replace(/\\s+/g,' ').slice(0,60) + ' -> ' + e.href)")
        vol = [h for h in hrefs if re.search(r"/volantino/.*/\d+$|pdf", h, re.I)]
        for h in vol[:30]:
            log(f"link volantino: {h}")
        links = []
        for h in vol:
            u = h.split(" -> ")[-1]
            if re.search(r"/\d{5}$", u) and u not in links and "/5208/" in u:
                links.append(u)
        log(f"volantini: {len(links)}")
        for u in links[:2]:
            log(f"--- apro volantino {u[-60:]}")
            pagina.goto(u, wait_until="domcontentloaded", timeout=60000)
            pagina.wait_for_timeout(9000)
            comune.prova_chiudi_cookie(pagina)
            log(f"titolo: {pagina.title()!r}  url: {pagina.url}")
            try:
                log("testo: " + re.sub(r"\n+", " | ", pagina.locator("body").inner_text(timeout=5000))[:1200])
            except Exception:
                pass
            hs = pagina.eval_on_selector_all(
                "a[href], iframe[src]", "els => els.map(e => (e.innerText||e.tagName).trim().replace(/\\s+/g,' ').slice(0,50) + ' -> ' + (e.href||e.src))")
            for h in hs:
                if re.search(r"pdf|volantin|flyer|sfoglia|download|scarica|iframe|http", h, re.I) and "carrefour.it/it" not in h:
                    log(f"  {h[:230]}")
            for fr in pagina.frames:
                log(f"  frame: {fr.url[:200]}")
            elementi(pagina, "pulsanti visibili")
            for st, tp, ru in risposte[-20:]:
                log(f"  risposta {st} {tp}: {ru[:220]}")
            comune.salva_debug(pagina, "carrefour")
    except Exception as e:
        log(f"errore: {str(e).splitlines()[0][:200]}")
    finally:
        pagina.close()
    return [(None, None)]
