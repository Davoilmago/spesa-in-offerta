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
    "https://www.oasitigre.it/it/il-mio-negozio.6507.html",
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
            utili = [l for l in links if re.search(r"pdf|volantin|flyer|calameo|issuu|sfoglia", l[0] + l[1], re.I)]
            print(f"    link utili ({len(utili)}/{len(links)}): {utili[:40]}")
        except Exception as e:
            print(f"    frame non esplorabile: {str(e)[:100]}")


def scarica(contesto, negozio, etichetta):
    pagina = contesto.new_page()
    pagina.set_default_timeout(25000)
    pdfs = []
    rete = []

    def _resp(r):
        try:
            ct = (r.headers.get("content-type", "") or "").lower()
            if "json" in ct or "retailtune" in r.url or "calameo" in r.url or "store" in r.url.lower():
                corpo = r.text() if "json" in ct else ""
                print(f"    [rete] {r.status} {r.url[:160]} len={len(corpo)} anzio={'Anzio' in corpo}")
                if "locator.php" in r.url and "Anzio" in corpo:
                    j = corpo.index("Via Giacomo Matteotti, 18")
                    ini = corpo.rfind('{"store"', 0, j)
                    fine = corpo.find('{"store"', j)
                    blocco = corpo[ini:fine if fine > 0 else ini + 12000]
                    print(f"    [store-anzio] len={len(blocco)} {blocco[:7000]!r}")
                    for m in re.finditer(r"https?:[^\"]*(?:calameo|volantin|flyer|\.pdf)[^\"]*", blocco, re.I):
                        print(f"    [store-link] {m.group(0)}")
                elif "Anzio" in corpo:
                    i = corpo.index("Anzio")
                    print(f"    [rete-anzio] {corpo[max(0, i - 300):i + 500]!r}")
        except Exception:
            pass
    pagina.on("response", _resp)
    pagina.on("response", lambda r: pdfs.append(r.url) if ("pdf" in (r.headers.get("content-type", "") or "").lower() or r.url.lower().split("?")[0].endswith(".pdf")) else None)
    try:
        for url in CANDIDATE:
            try:
                r = pagina.goto(url, wait_until="domcontentloaded", timeout=40000)
                pagina.wait_for_timeout(5000)
                comune.prova_chiudi_cookie(pagina)
                print(f"[pagina] {url} -> stato {r.status if r else '?'}")
                esplora(pagina, url)
                # cerca il negozio di Anzio nei campi di ricerca
                for frame in (comune.tutti_i_frame(pagina) if "negozi-volantini" in url else []):
                    campi = frame.locator("input[type=text], input[type=search], input:not([type])")
                    for i in range(min(campi.count(), 6)):
                        try:
                            c = campi.nth(i)
                            print(f"    input {i}: ph={c.get_attribute('placeholder')} name={c.get_attribute('name')} vis={c.is_visible()}")
                            if c.is_visible():
                                c.fill("Anzio")
                                c.press("Enter")
                                pagina.wait_for_timeout(5000)
                                print(f"    cercato Anzio nel campo {i}")
                                try:
                                    sugg = frame.eval_on_selector_all(".pac-item, [role=option], .autocomplete li, ul.ui-autocomplete li", "els => els.map(e => e.innerText.trim().slice(0,80))")
                                    print(f"    suggerimenti: {sugg[:10]}")
                                    cards = frame.eval_on_selector_all("[class*=store], [class*=negozio]", "els => els.slice(0,6).map(e => e.className + ' | ' + e.innerText.trim().slice(0,60))")
                                    print(f"    card negozi: {cards}")
                                    if sugg:
                                        frame.locator(".pac-item, [role=option], .autocomplete li, ul.ui-autocomplete li").first.click(timeout=5000)
                                        pagina.wait_for_timeout(6000)
                                        esplora(pagina, "dopo suggerimento")
                                except Exception as e:
                                    print(f"    suggerimenti: errore {str(e)[:80]}")
                                esplora(pagina, "dopo ricerca Anzio")
                                for t in ("Anzio", "Matteotti"):
                                    try:
                                        frame.get_by_text(t, exact=False).first.click(timeout=5000)
                                        pagina.wait_for_timeout(5000)
                                        print(f"    cliccato su {t}")
                                        esplora(pagina, "dopo click " + t)
                                        break
                                    except Exception as e:
                                        print(f"    click {t} fallito: {str(e)[:80]}")
                                break
                        except Exception as e:
                            print(f"    campo {i} non usabile: {str(e)[:80]}")
            except Exception as e:
                print(f"[pagina] {url} non apribile: {str(e).splitlines()[0][:120]}")
        href = ""
        try:
            cal = pagina.eval_on_selector_all("a[href*='calameo'], iframe[src*='calameo'], [data-calameo], [href*='volantin']", "els => els.map(e => [e.tagName, e.href || e.src || '', (e.innerText||'').trim().slice(0,50), e.outerHTML.slice(0,200)])")
            print(f"    calameo/volantino: {cal[:10]}")
            html = pagina.content()
            for m in re.finditer(r"calameo[^\"' <>]{0,120}", html):
                print(f"    html-calameo: {m.group(0)}")
        except Exception as e:
            print(f"    calameo err {str(e)[:80]}")
        for frame in comune.tutti_i_frame(pagina):
            h = frame.eval_on_selector_all("a[href*='.pdf']", "els => (els.map(e => e.href)[0] || '')")
            if h:
                href = h
                break
        href = href or (pdfs[0] if pdfs else "")
        if "accessibil" in href.lower():
            href = ""
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
