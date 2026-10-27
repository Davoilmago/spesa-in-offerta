"""
MD (discount): i volantini sono pubblicati su https://www.1leadermarketing.it/volantino/
NOTA: la pagina https://www.1leadermarketing.it/volantino/ mostra gia' il volantino del punto vendita di Anzio
(Via Goldoni 62) con il link diretto https://www.1leadermarketing.it/volantino/volantino.pdf (28 pagine, validita'
scritta in copertina). Il modulo scrive nel log cosa vede, cosi' si controlla se il sito cambia. Apre la pagina, prova a scegliere Anzio dai menu o dai campi di ricerca,
scrive nel log (volantini/_log_md.txt) cosa vede (testo, menu, link) e scarica il primo PDF trovato.
Dopo aver letto il log si rifinisce il modulo.

Nel file della citta' basta scrivere:  "md": [{"nota": "MD Via Goldoni 62", "citta": "Anzio"}]
"""

import re

import comune

NOME = "md"
GIORNI = [0, 3, 4]
CONDIVISO = False

URL = "https://www.1leadermarketing.it/volantino/"

_LOG = []
_print = print


def print(*a, **k):
    _print(*a, **k)
    _LOG.append(" ".join(str(x) for x in a))
    try:
        (comune.CARTELLA_PDF / "_log_md.txt").write_text("\n".join(_LOG), encoding="utf-8")
    except Exception:
        pass


def esplora(pagina, titolo):
    print(f"  == {titolo}: {pagina.url}")
    try:
        testo = re.sub(r"\s+", " ", pagina.inner_text("body"))
        print(f"    testo: {testo[:1500]!r}")
    except Exception as e:
        print(f"    testo non leggibile: {e}")
    for frame in comune.tutti_i_frame(pagina):
        try:
            print(f"    frame: {frame.url}")
            for i in range(min(frame.locator("select").count(), 8)):
                opz = frame.locator("select").nth(i).evaluate("e => [...e.options].map(o => o.text)")
                print(f"    select {i}: {opz[:25]}")
            for i in range(min(frame.locator("input").count(), 8)):
                el = frame.locator("input").nth(i)
                print(f"    input {i}: type={el.get_attribute('type')} name={el.get_attribute('name')} ph={el.get_attribute('placeholder')}")
            links = frame.eval_on_selector_all(
                "a[href]", "els => els.map(e => [e.href, (e.innerText||'').trim().slice(0,40)])")
            utili = [l for l in links if re.search(r"pdf|volantin|anzio|download|scarica", l[0] + l[1], re.I)]
            print(f"    link utili ({len(utili)}/{len(links)}): {utili[:30]}")
        except Exception as e:
            print(f"    frame non esplorabile: {str(e)[:100]}")


def scarica(contesto, negozio, etichetta):
    pagina = contesto.new_page()
    try:
        pagina.goto(URL, wait_until="domcontentloaded", timeout=60000)
        pagina.wait_for_timeout(6000)
        comune.prova_chiudi_cookie(pagina)
        esplora(pagina, "pagina iniziale")
        cerca = negozio.get("citta", "Anzio")
        # prova 1: menu a tendina con Anzio
        for frame in comune.tutti_i_frame(pagina):
            for i in range(frame.locator("select").count()):
                menu = frame.locator("select").nth(i)
                opz = menu.evaluate("e => [...e.options].map(o => [o.value, o.text])")
                v = next((v for v, t in opz if cerca.lower() in t.lower()), None)
                if v is not None:
                    menu.select_option(v)
                    pagina.wait_for_timeout(3000)
                    print(f"    scelto {cerca} nel menu {i}")
        # prova 2: campo di ricerca
        for frame in comune.tutti_i_frame(pagina):
            campi = frame.locator("input[type=text], input[type=search], input:not([type])")
            if campi.count() > 0:
                try:
                    campi.first.fill(cerca)
                    campi.first.press("Enter")
                    pagina.wait_for_timeout(4000)
                    print(f"    cercato {cerca} nel campo di ricerca")
                except Exception as e:
                    print(f"    campo di ricerca non usabile: {str(e)[:100]}")
                break
        esplora(pagina, "dopo la scelta")
        href = ""
        for frame in comune.tutti_i_frame(pagina):
            h = frame.eval_on_selector_all("a[href*='.pdf']", "els => (els.map(e => e.href)[0] || '')")
            if h:
                href = h
                break
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
        return [(file, {"titolo": "Volantino MD", "indirizzo": href})]
    except Exception as errore:
        print(f"[ERRORE] {etichetta}: {str(errore).splitlines()[0][:200]}")
        return [(None, None)]
    finally:
        pagina.close()
