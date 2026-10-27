"""
iN's Mercato: la pagina https://www.insmercato.it/volantino/ ha tre menu (Provincia, Citta', Filiale).
Dopo aver scelto la filiale, il pulsante "SCARICA IL PDF" diventa un link diretto al file, ad esempio
https://insmercato-cdn.it/insmercato/volantino/22/lfxsip/pdf/volantino-A.pdf

Nel file della citta' servono per ogni negozio: "provincia", "citta'" e "filiale" cosi' come compaiono nei menu
(es. Roma / Nettuno / Via Ugo La Malfa, 9). Le date si leggono dal PDF stesso.
"""

import re

import comune

NOME = "ins"
GIORNI = [0, 1, 3, 4]   # lunedi, martedi, giovedi, venerdi (i volantini cambiano a meta' settimana)
CONDIVISO = False


def scegli(pagina, indice, cerca):
    menu = pagina.locator("select").nth(indice)
    opzioni = menu.evaluate("e => [...e.options].map(o => [o.value, o.text])")
    scelto = next((v for v, t in opzioni if cerca.lower() in t.lower()), None)
    if scelto is None:
        print(f"    nel menu {indice} non trovo {cerca!r}: {[t for _, t in opzioni][:15]}")
        return False
    menu.select_option(scelto)
    pagina.wait_for_timeout(2500)
    return True


def scarica(contesto, negozio, etichetta):
    pagina = contesto.new_page()
    try:
        pagina.goto("https://www.insmercato.it/volantino/", wait_until="domcontentloaded", timeout=60000)
        pagina.wait_for_timeout(6000)
        comune.prova_chiudi_cookie(pagina)
        scelte = [negozio.get("provincia", "Roma"), negozio.get("citta", "Nettuno"), negozio.get("filiale", "")]
        for i, cerca in enumerate(scelte):
            if not scegli(pagina, i, cerca):
                comune.salva_debug(pagina, comune.slug(etichetta))
                return [(None, None)]
        href = pagina.eval_on_selector_all(
            "a[href]", "els => (els.find(e => /scarica il pdf/i.test(e.innerText||'')) || {}).href || ''")
        if not re.search(r"\.pdf", href or "", re.I):
            print(f"[ERRORE] {etichetta}: link 'Scarica il pdf' non trovato ({href!r})")
            comune.salva_debug(pagina, comune.slug(etichetta))
            return [(None, None)]
        print(f"    PDF: {href}")
        risposta = contesto.request.get(href, timeout=120000)
        corpo = risposta.body()
        if not (risposta.ok and corpo[:5] == b"%PDF-"):
            print(f"[ERRORE] {etichetta}: la risposta non e' un PDF (stato {risposta.status})")
            return [(None, None)]
        comune.CARTELLA_TMP.mkdir(exist_ok=True)
        file = comune.CARTELLA_TMP / f"{comune.slug(etichetta)}.pdf"
        file.write_bytes(corpo)
        m = re.search(r"/volantino/(\d+)/", href)
        info = {"titolo": f"Volantino {m.group(1)}" if m else ""}
        print(f"[ok] {etichetta}: PDF scaricato ({len(corpo) // 1024} KB)")
        return [(file, info)]
    except Exception as errore:
        print(f"[ERRORE] {etichetta}: {str(errore).splitlines()[0][:200]}")
        return [(None, None)]
    finally:
        pagina.close()
