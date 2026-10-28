"""
Decò (Gruppo Arena): modulo ESPLORATIVO. Prova alcuni indirizzi del sito ufficiale, scrive in volantini/_log_deco.txt
cosa trova (testo, menu, link a PDF / volantini / Anzio) e scarica il primo PDF che riesce a trovare.
Nel file della citta':  "deco": [{"nota": "Decò Via di Valle Schioia 67", "citta": "Anzio"}]
"""
import re

import comune

NOME = "deco"
GIORNI = [0, 3, 4]
CONDIVISO = False

CANDIDATI = [
    "https://www.supermercatideco.it/",
    "https://www.supermercatideco.it/news/",
    "https://www.supermercatideco.it/deco-italia/",
    "https://www.supermercatideco.it/punti-vendita/",
    "https://www.supermercatideco.it/sitemap/",
]

_LOG = []
_print = print


def print(*a, **k):
    _print(*a, **k)
    _LOG.append(" ".join(str(x) for x in a))
    try:
        (comune.CARTELLA_PDF / "_log_deco.txt").write_text("\n".join(_LOG), encoding="utf-8")
    except Exception:
        pass


def esplora(pagina, titolo):
    print(f"  == {titolo}: {pagina.url} | titolo={pagina.title()!r}")
    try:
        print(f"    testo: {re.sub(chr(10), ' ', pagina.inner_text('body'))[:900]!r}")
    except Exception as e:
        print(f"    testo non leggibile: {e}")
    trovati = []
    try:
        tutti = pagina.eval_on_selector_all("a[href]", "els => els.map(e => [e.href, (e.innerText||'').trim().slice(0,30)])")
        print(f"    TUTTI i link ({len(tutti)}): {tutti[:90]}")
    except Exception as e:
        print(f"    link non leggibili: {e}")
    for frame in comune.tutti_i_frame(pagina):
        try:
            for i in range(min(frame.locator("select").count(), 6)):
                opz = frame.locator("select").nth(i).evaluate("e => [...e.options].map(o => o.text)")
                print(f"    select {i}: {opz[:20]}")
            links = frame.eval_on_selector_all("a[href]", "els => els.map(e => [e.href, (e.innerText||'').trim().slice(0,40)])")
            utili = [l for l in links if re.search(r"pdf|volantin|anzio|punti-vendita|negozi|scarica", l[0] + l[1], re.I)]
            print(f"    link utili ({len(utili)}/{len(links)}): {utili[:25]}")
            trovati += utili
        except Exception as e:
            print(f"    frame non esplorabile: {str(e)[:100]}")
    return trovati


def scarica(contesto, negozio, etichetta):
    pagina = contesto.new_page()
    pagina.set_default_timeout(20000)
    try:
        href = ""
        for url in CANDIDATI:
            try:
                r = pagina.goto(url, wait_until="domcontentloaded", timeout=25000)
                pagina.wait_for_timeout(4000)
                print(f"[{url}] stato {r.status if r else '?'}")
                if not r or r.status >= 400:
                    continue
                comune.prova_chiudi_cookie(pagina)
                utili = esplora(pagina, url)
                pdf = [l[0] for l in utili if re.search(r"\.pdf", l[0], re.I)]
                if pdf:
                    href = pdf[0]
                    break
                # segui un link che parla di Anzio o di volantino
                nxt = [l[0] for l in utili if re.search(r"anzio", l[0] + l[1], re.I)] or \
                      [l[0] for l in utili if re.search(r"volantin", l[0] + l[1], re.I) and l[0].rstrip("/") != url.rstrip("/")]
                if nxt:
                    pagina.goto(nxt[0], wait_until="domcontentloaded", timeout=25000)
                    pagina.wait_for_timeout(4000)
                    utili = esplora(pagina, "seguito " + nxt[0])
                    pdf = [l[0] for l in utili if re.search(r"\.pdf", l[0], re.I)]
                    if pdf:
                        href = pdf[0]
                        break
            except Exception as e:
                print(f"[{url}] errore: {str(e).splitlines()[0][:150]}")
        if not href:
            print(f"[ERRORE] {etichetta}: nessun PDF trovato")
            return [(None, None)]
        r = contesto.request.get(href, timeout=120000)
        corpo = r.body()
        if not (r.ok and corpo[:5] == b"%PDF-"):
            print(f"[ERRORE] {etichetta}: {href[:100]} non e' un PDF (stato {r.status})")
            return [(None, None)]
        comune.CARTELLA_TMP.mkdir(exist_ok=True)
        file = comune.CARTELLA_TMP / f"{comune.slug(etichetta)}.pdf"
        file.write_bytes(corpo)
        print(f"[ok] {etichetta}: {href} ({len(corpo) // 1024} KB)")
        return [(file, {"titolo": "Volantino Decò", "indirizzo": href})]
    except Exception as errore:
        print(f"[ERRORE] {etichetta}: {str(errore).splitlines()[0][:200]}")
        return [(None, None)]
    finally:
        pagina.close()
