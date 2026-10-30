"""
Crai: ogni negozio ha una sua pagina https://crai.it/negozi-e-volantini/<id>-<nome> con il volantino
del punto vendita (se pubblicato). Questo modulo e' ESPLORATIVO: apre la pagina del negozio,
scrive nel log (volantini/_log_crai.txt) testo, link, frame e file PDF visti dalla rete,
e scarica il primo PDF trovato. Dopo aver letto il log si rifinisce il modulo.

Nel file della citta':  "crai": [{"nota": "Crai Via Vecchiarelli 2", "pagina": "https://crai.it/negozi-e-volantini/2049-crai-anzio"}]
Senza "pagina" cerca nell'elenco dei negozi il nome della citta' e del negozio ("cerca").
"""

import re

import comune

NOME = "crai"
GIORNI = [0, 3, 4]
CONDIVISO = False

ELENCO = "https://crai.it/negozi-e-volantini"

_LOG = []
_print = print


def print(*a, **k):
    _print(*a, **k)
    _LOG.append(" ".join(str(x) for x in a))
    try:
        (comune.CARTELLA_PDF / "_log_crai.txt").write_text("\n".join(_LOG), encoding="utf-8")
    except Exception:
        pass


def esplora(pagina, titolo):
    print(f"  == {titolo}: {pagina.url}")
    try:
        testo = re.sub(r"\s+", " ", pagina.inner_text("body"))
        print(f"    testo: {testo[:1800]!r}")
    except Exception as e:
        print(f"    testo non leggibile: {e}")
    for frame in comune.tutti_i_frame(pagina):
        try:
            print(f"    frame: {frame.url}")
            links = frame.eval_on_selector_all(
                "a[href]", "els => els.map(e => [e.href, (e.innerText||'').trim().slice(0,50)])")
            utili = [l for l in links if re.search(r"pdf|volantin|anzio|nettuno|download|scarica|sfoglia", l[0] + l[1], re.I)]
            print(f"    link utili ({len(utili)}/{len(links)}): {utili[:40]}")
        except Exception as e:
            print(f"    frame non esplorabile: {str(e)[:100]}")


def scarica(contesto, negozio, etichetta):
    pagina = contesto.new_page()
    visti = []
    pagina.on("response", lambda r: visti.append(r.url) if re.search(r"\.pdf(\?|$)", r.url, re.I) else None)
    json_visti = []

    def _json(r):
        try:
            if "json" in (r.headers.get("content-type") or "") and re.search(r"crai", r.url):
                json_visti.append(r)
        except Exception:
            pass
    pagina.on("response", _json)
    try:
        url = negozio.get("pagina") or ELENCO
        pagina.goto(url, wait_until="domcontentloaded", timeout=60000)
        pagina.wait_for_timeout(7000)
        comune.prova_chiudi_cookie(pagina)
        esplora(pagina, "pagina iniziale")
        if not negozio.get("pagina"):
            cerca = negozio.get("cerca", "")
            for frame in comune.tutti_i_frame(pagina):
                campi = frame.locator("input[type=text], input[type=search], input:not([type])")
                if campi.count() > 0:
                    try:
                        campi.first.fill(cerca)
                        campi.first.press("Enter")
                        pagina.wait_for_timeout(5000)
                    except Exception as e:
                        print(f"    ricerca non usabile: {str(e)[:100]}")
                    break
            esplora(pagina, "dopo la ricerca")
        # prova a premere un pulsante/link del volantino
        for testo in ("Sfoglia il volantino", "Volantino", "Vedi il volantino", "Scarica"):
            try:
                el = pagina.get_by_text(re.compile(testo, re.I)).first
                if el.is_visible(timeout=1500):
                    el.click(timeout=4000)
                    pagina.wait_for_timeout(5000)
                    print(f"    cliccato '{testo}' -> {pagina.url}")
                    esplora(pagina, f"dopo clic '{testo}'")
                    break
            except Exception:
                pass
        for r in json_visti[:40]:
            try:
                t = r.text()
                print(f"    JSON {r.url[:150]} ({len(t)} car.)")
                for m in list(re.finditer(r"(Anzio|Nettuno|Vecchiarelli|San Giacomo)", t, re.I))[:6]:
                    print(f"      ...{t[max(0, m.start() - 250):m.end() + 250]!r}")
            except Exception:
                pass
        href = ""
        for frame in comune.tutti_i_frame(pagina):
            h = frame.eval_on_selector_all(
                "a[href*='.pdf']",
                "els => (els.map(e => e.href).filter(h => !/company_profile|prontuario|codice_etico|informativa|regolamento/i.test(h))[0] || '')")
            if h:
                href = h
                break
        visti = [v for v in visti if not re.search(r"company_profile|prontuario|codice_etico|informativa|regolamento", v, re.I)]
        if not href and visti:
            href = visti[0]
        print(f"    PDF visti dalla rete: {visti[:10]}")
        comune.salva_debug(pagina, "crai-" + comune.slug(etichetta))
        if not href:
            print(f"[ERRORE] {etichetta}: link PDF non trovato (forse nessun volantino attivo)")
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
        return [(file, {"titolo": "Volantino Crai", "indirizzo": href})]
    except Exception as errore:
        print(f"[ERRORE] {etichetta}: {str(errore).splitlines()[0][:200]}")
        return [(None, None)]
    finally:
        pagina.close()
