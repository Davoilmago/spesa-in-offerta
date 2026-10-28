"""
Tigre Amico (Oasi Tigre): sito https://www.oasitigre.it  (volantino del punto vendita di Anzio, Via Matteotti 18).
Primo giro ESPLORATIVO: il modulo apre le pagine candidate, scrive nel log (volantini/_log_tigre.txt) testo, link
e frame che vede, e scarica il primo PDF trovato. Dopo aver letto il log si rifinisce.

Nel file della citta':  "tigre": [{"nota": "Tigre Amico Via Matteotti 18", "citta": "Anzio"}]
"""
import re

import comune

NOME = "tigre"
GIORNI = [0, 3, 4]
CONDIVISO = False

CANDIDATE = [
    "https://www.oasitigre.it/",
    "https://www.oasitigre.it/volantini",
    "https://www.oasitigre.it/volantino",
    "https://www.oasitigre.it/punti-vendita",
    "https://www.tigre.it/",
]

_LOG = []
_print = print


def print(*a, **k):
    _print(*a, **k)
    _LOG.append(" ".join(str(x) for x in a))
    try:
        (comune.CARTELLA_PDF / "_log_tigre.txt").write_text("\n".join(_LOG), encoding="utf-8")
    except Exception:
        pass


def esplora(pagina, titolo):
    print(f"  == {titolo}: {pagina.url}")
    try:
        testo = re.sub(r"\s+", " ", pagina.inner_text("body"))
        print(f"    testo: {testo[:1200]!r}")
    except Exception as e:
        print(f"    testo non leggibile: {str(e)[:100]}")
    for frame in comune.tutti_i_frame(pagina):
        try:
            print(f"    frame: {frame.url}")
            links = frame.eval_on_selector_all(
                "a[href], iframe[src]", "els => els.map(e => [e.href || e.src, (e.innerText||'').trim().slice(0,40)])")
            utili = [l for l in links if re.search(r"pdf|volantin|flyer|anzio|calameo|issuu|offert|punti|negozi|store", l[0] + l[1], re.I)]
            print(f"    link utili ({len(utili)}/{len(links)}): {utili[:40]}")
        except Exception as e:
            print(f"    frame non esplorabile: {str(e)[:100]}")


def scarica(contesto, negozio, etichetta):
    pagina = contesto.new_page()
    pagina.set_default_timeout(25000)
    pdfs = []
    pagina.on("response", lambda r: pdfs.append(r.url) if ("pdf" in (r.headers.get("content-type", "") or "").lower() or r.url.lower().split("?")[0].endswith(".pdf")) else None)
    try:
        for url in CANDIDATE:
            try:
                r = pagina.goto(url, wait_until="domcontentloaded", timeout=40000)
                pagina.wait_for_timeout(5000)
                comune.prova_chiudi_cookie(pagina)
                print(f"[pagina] {url} -> stato {r.status if r else '?'}")
                esplora(pagina, url)
            except Exception as e:
                print(f"[pagina] {url} non apribile: {str(e).splitlines()[0][:120]}")
        href = ""
        for frame in comune.tutti_i_frame(pagina):
            h = frame.eval_on_selector_all("a[href*='.pdf']", "els => (els.map(e => e.href)[0] || '')")
            if h:
                href = h
                break
        href = href or (pdfs[0] if pdfs else "")
        print(f"    pdf visti in rete: {pdfs[:5]}")
        if not href:
            print(f"[ERRORE] {etichetta}: link PDF non trovato")
            comune.salva_debug(pagina, comune.slug(etichetta))
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
        return [(file, {"titolo": "Volantino Tigre Amico", "indirizzo": href})]
    except Exception as errore:
        print(f"[ERRORE] {etichetta}: {str(errore).splitlines()[0][:200]}")
        return [(None, None)]
    finally:
        pagina.close()
