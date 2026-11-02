"""
Modulo di ESPLORAZIONE (non scarica volantini): per Latina cerca nei localizzatori di negozi di Conad,
Carrefour ed Eurospin gli indirizzi/codici dei negozi, e scrive il risultato in volantini/_log_esploralatina.txt.
Dopo aver letto il log si tolgono questi test e si scrivono i veri file della citta'.
"""

import json
import re

import comune

NOME = "esploralatina"
GIORNI = []
CONDIVISO = False

_LOG = []
_print = print


def print(*a, **k):
    _print(*a, **k)
    _LOG.append(" ".join(str(x) for x in a))
    try:
        (comune.CARTELLA_PDF / "_log_esploralatina.txt").write_text("\n".join(_LOG), encoding="utf-8")
    except Exception:
        pass


OBIETTIVI = [
    ("eurospin2", "https://www.eurospin.com/it-it/punti-vendita/", r"punti-vendita|latina|volantino"),
]


def esplora(contesto, nome, url, filtro):
    pagina = contesto.new_page()
    risposte = []

    def _r(r):
        try:
            if "json" in (r.headers.get("content-type") or ""):
                risposte.append(r)
        except Exception:
            pass
    pagina.on("response", _r)
    try:
        print(f"== {nome}: {url}")
        pagina.goto(url, wait_until="domcontentloaded", timeout=60000)
        pagina.wait_for_timeout(6000)
        comune.prova_chiudi_cookie(pagina)
        print(f"   titolo: {pagina.title()!r}  url: {pagina.url}")
        for frame in comune.tutti_i_frame(pagina):
            campi = frame.locator("input[type=text], input[type=search], input:not([type])")
            n = campi.count()
            print(f"   frame {frame.url[:80]}: {n} campi")
            for i in range(min(n, 3)):
                try:
                    c = campi.nth(i)
                    if not c.is_visible():
                        continue
                    c.fill("Latina")
                    pagina.wait_for_timeout(1500)
                    c.press("Enter")
                    pagina.wait_for_timeout(6000)
                    print(f"   cercato 'Latina' nel campo {i}")
                    try:
                        c.press("ArrowDown")
                        pagina.wait_for_timeout(500)
                        c.press("Enter")
                        pagina.wait_for_timeout(8000)
                        print("   scelto il suggerimento 'Latina, LT, Italia'")
                    except Exception as e2:
                        print(f"   suggerimento non cliccabile: {str(e2)[:80]}")
                    break
                except Exception as e:
                    print(f"   campo {i} non usabile: {str(e)[:80]}")
        print(f"   url dopo la ricerca: {pagina.url}")
        testo = re.sub(r"\s+", " ", pagina.inner_text("body"))
        print(f"   testo: {testo[:1200]!r}")
        for frame in comune.tutti_i_frame(pagina):
            try:
                links = frame.eval_on_selector_all("a[href]", "els => els.map(e => [e.href, (e.innerText||'').trim().slice(0,60)])")
                utili = [l for l in links if re.search(filtro, l[0], re.I) and re.search(r"latina|lt\b|pontina", l[0] + l[1], re.I)]
                print(f"   link utili ({len(utili)}/{len(links)}): {utili[:40]}")
            except Exception:
                pass
        for r in risposte[:60]:
            try:
                t = r.text()
                print(f"   JSON-visto {r.url[:150]} ({len(t)} car.)")
                if re.search(r"latina|corbusier", t, re.I):
                    print(f"   JSON {r.url[:160]} ({len(t)} car.)")
                    for m in list(re.finditer(r"corbusier|Latina \(", t, re.I))[:8]:
                        print(f"      ...{t[max(0, m.start() - 220):m.end() + 220]!r}")
            except Exception:
                pass
        comune.salva_debug(pagina, f"latina-{nome}")
    except Exception as e:
        print(f"   [ERRORE] {str(e).splitlines()[0][:200]}")
    finally:
        pagina.close()


def scarica(contesto, negozio, etichetta):
    for nome, url, filtro in OBIETTIVI:
        esplora(contesto, nome, url, filtro)
    return [(None, None)]
