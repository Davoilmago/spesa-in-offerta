"""
iN's Mercato: la pagina https://www.insmercato.it/volantino/ ha tre menu (Provincia, Citta', Filiale)
e i pulsanti "Scarica il pdf" e "Sfoglia il volantino".

VERSIONE DI ESPLORAZIONE: scrive nel log i menu, le scelte e cosa succede ai pulsanti.
"""

import contextlib
import io
import re
from pathlib import Path

import comune

LOG = Path("volantini/_debug/ins.txt")
NOME = "ins"
GIORNI = [0, 1, 2, 3, 4, 5, 6]
CONDIVISO = False


def log(t):
    print(t)
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(t + "\n")


def elementi(pagina, titolo):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        comune.stampa_elementi_visibili(pagina, titolo)
    log(buf.getvalue().rstrip())


def scarica(contesto, negozio, etichetta):
    pagina = contesto.new_page()
    risposte = []
    pagina.on("response", lambda r: risposte.append((r.status, r.url)) if re.search(r"pdf|volantin|flyer|sfoglia|download", r.url, re.I) else None)
    scaricati = []
    pagina.on("download", lambda d: scaricati.append(d))
    try:
        pagina.goto("https://www.insmercato.it/volantino/", wait_until="domcontentloaded", timeout=60000)
        pagina.wait_for_timeout(7000)
        comune.prova_chiudi_cookie(pagina)
        log(f"titolo: {pagina.title()!r}")
        selects = pagina.locator("select")
        n = selects.count()
        log(f"menu a tendina: {n}")
        for i in range(n):
            s = selects.nth(i)
            opts = s.evaluate("e => [...e.options].map(o => o.value + '=' + o.text)")
            log(f"  select {i} id={s.get_attribute('id')!r} name={s.get_attribute('name')!r}: {opts[:12]} (tot {len(opts)})")
        elementi(pagina, "pulsanti")
        for i, cerca in enumerate(["Roma", "Nettuno", "Via Ugo La Malfa"]):
            s = pagina.locator("select").nth(i)
            opts = s.evaluate("e => [...e.options].map(o => [o.value, o.text])")
            scelto = next((v for v, t in opts if cerca.lower() in t.lower()), None)
            log(f"  menu {i}: cerco {cerca!r} -> {scelto!r}")
            if scelto is None:
                log(f"  opzioni menu {i}: {opts[:40]}")
                break
            s.select_option(scelto)
            pagina.wait_for_timeout(3000)
        hs = pagina.eval_on_selector_all("a[href]", "els => els.map(e => (e.innerText||'').trim().slice(0,40) + ' -> ' + e.href)")
        for h in hs:
            if re.search(r"pdf|sfoglia|volantin|scarica", h, re.I):
                log(f"  link: {h[:250]}")
        for testo in ["Scarica il pdf", "Sfoglia il volantino"]:
            try:
                b = pagina.get_by_text(testo, exact=False).first
                log(f"  pulsante {testo!r}: href={b.evaluate('e => e.href || (e.closest(\"a\")||{}).href')!r} target={b.get_attribute('target')!r}")
            except Exception as e:
                log(f"  pulsante {testo!r}: {str(e)[:100]}")
        try:
            pagina.get_by_text("Scarica il pdf", exact=False).first.click(timeout=8000)
            pagina.wait_for_timeout(8000)
            log(f"  dopo il clic: url={pagina.url} download={len(scaricati)}")
        except Exception as e:
            log(f"  clic non riuscito: {str(e)[:150]}")
        for st, u in risposte[-20:]:
            log(f"  risposta {st}: {u[:220]}")
        for sch in contesto.pages:
            log(f"  scheda: {sch.url[:200]}")
        elementi(pagina, "pulsanti dopo")
        comune.salva_debug(pagina, "ins")
    except Exception as e:
        log(f"errore: {str(e).splitlines()[0][:200]}")
    finally:
        pagina.close()
    return [(None, None)]
