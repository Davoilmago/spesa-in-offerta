"""
Decò: i volantini stanno sulla piattaforma https://puntivenditadeco.multicedi.it/it (ricerca negozi) -> pagina del
negozio -> volantino digitale (deco.volantinopiu.com / PDF su resources.volantinopiu.it).
MODULO ESPLORATIVO: cerca "Anzio", apre il negozio di Via Valle Schioia, scrive nel log (volantini/_log_deco.txt)
pagine, frame e richieste di rete con 'pdf' o 'flyer', e scarica il primo PDF di volantino che trova.
Nel file della citta':  "deco": [{"nota": "Decò Via di Valle Schioia 67", "citta": "Anzio"}]
"""
import re
import time

import comune

NOME = "deco"
GIORNI = [0, 3, 4]
CONDIVISO = False
URL = "https://puntivenditadeco.multicedi.it/it"

_LOG = []
_print = print


def print(*a, **k):
    _print(*a, **k)
    _LOG.append(" ".join(str(x) for x in a))
    try:
        (comune.CARTELLA_PDF / "_log_deco.txt").write_text("\n".join(_LOG), encoding="utf-8")
    except Exception:
        pass


def descrivi(pagina, titolo):
    print(f"  == {titolo}: {pagina.url} | {pagina.title()!r}")
    try:
        print(f"    testo: {re.sub(chr(10), ' ', pagina.inner_text('body'))[:700]!r}")
    except Exception as e:
        print(f"    testo non leggibile: {e}")
    for fr in comune.tutti_i_frame(pagina):
        try:
            ls = fr.eval_on_selector_all("a[href]", "els => els.map(e => [e.href, (e.innerText||'').trim().slice(0,30)])")
            ut = [l for l in ls if re.search(r"pdf|volantin|flyer|anzio|sfoglia|scarica|promoz", l[0] + l[1], re.I)]
            print(f"    frame {fr.url[:120]} link={len(ls)} utili={ut[:20]}")
        except Exception as e:
            print(f"    frame non esplorabile: {str(e)[:80]}")


def scarica(contesto, negozio, etichetta):
    pagina = contesto.new_page()
    pagina.set_default_timeout(20000)
    rete = []
    pagina.on("response", lambda r: rete.append((r.status, r.url)) if re.search(r"\.pdf|flyer|volantin|joomag", r.url, re.I) else None)
    fine = time.time() + 420
    try:
        pagina.goto(URL, wait_until="domcontentloaded", timeout=30000)
        pagina.wait_for_timeout(5000)
        comune.prova_chiudi_cookie(pagina)
        # ricerca "Anzio"
        campo = pagina.locator("input[type=text], input[type=search], input:not([type])")
        print(f"    campi di testo: {campo.count()}")
        for i in range(min(campo.count(), 4)):
            el = campo.nth(i)
            print(f"      campo {i}: ph={el.get_attribute('placeholder')!r} name={el.get_attribute('name')!r} visibile={el.is_visible()}")
        usato = False
        for i in range(campo.count()):
            el = campo.nth(i)
            if el.is_visible():
                el.fill("Anzio")
                el.press("Enter")
                pagina.wait_for_timeout(5000)
                usato = True
                break
        print(f"    ricerca inserita: {usato}")
        descrivi(pagina, "dopo la ricerca")
        # scelgo il suggerimento "Anzio, Roma, Lazio"
        sug = pagina.get_by_text(re.compile(r"^Anzio, Roma, Lazio", re.I))
        print(f"    suggerimenti Anzio: {sug.count()}")
        if sug.count() > 0:
            sug.first.click()
            pagina.wait_for_timeout(6000)
        tutti = pagina.eval_on_selector_all("a[href*='/it/italia/']", "els => [...new Set(els.map(e => e.href))]")
        ad = [u for u in tutti if re.search(r"anzio|nettuno|schioia|lavinio", u, re.I)]
        print(f"    link negozi totali {len(tutti)}; Anzio/Nettuno: {ad}; primi: {tutti[:6]}")
        url_neg = next((u for u in ad if re.search(r"schioia", u, re.I)), ad[0] if ad else "")
        if not url_neg:
            url_neg = "https://puntivenditadeco.multicedi.it/it/italia/anzio/anzio-via-valle-schioia"
        print(f"    apro il negozio: {url_neg}")
        pagina.goto(url_neg, wait_until="domcontentloaded", timeout=30000)
        pagina.wait_for_timeout(7000)
        descrivi(pagina, "pagina negozio")
        # link/pulsanti del volantino nella pagina del negozio
        for fr in comune.tutti_i_frame(pagina):
            try:
                els = fr.locator("a, button, iframe")
                for i in range(min(els.count(), 120)):
                    e = els.nth(i)
                    tx = (e.inner_text() or "").strip()[:40] if e.evaluate("e => e.tagName") != "IFRAME" else ""
                    hr = e.get_attribute("href") or e.get_attribute("src") or ""
                    if re.search(r"volantin|flyer|sfoglia|pdf|joomag|promoz", tx + hr, re.I):
                        print(f"      elemento {i}: {e.evaluate('e => e.tagName')} {tx!r} {hr[:150]}")
            except Exception as ex:
                print(f"      errore elementi: {str(ex)[:80]}")
        print(f"    richieste di rete utili: {rete[:30]}")
        href = ""
        for st, u in rete:
            if st == 200 and re.search(r"\.pdf", u, re.I) and not re.search(r"termini|privacy|cookie", u, re.I):
                href = u
                break
        if not href:
            for fr in comune.tutti_i_frame(pagina):
                try:
                    h = fr.eval_on_selector_all("a[href*='.pdf']", "els => (els.map(e => e.href).filter(h => !/termini|privacy|cookie/i.test(h))[0] || '')")
                    if h:
                        href = h
                        break
                except Exception:
                    pass
        if not href:
            print(f"[ERRORE] {etichetta}: nessun PDF trovato")
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
        return [(file, {"titolo": "Volantino Decò", "indirizzo": href})]
    except Exception as errore:
        print(f"[ERRORE] {etichetta}: {str(errore).splitlines()[0][:200]}")
        return [(None, None)]
    finally:
        try:
            pagina.context.pages[0]
        except Exception:
            pass
        for p in list(contesto.pages):
            try:
                p.close()
            except Exception:
                pass
