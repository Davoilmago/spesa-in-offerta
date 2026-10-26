"""
Carrefour: ogni punto vendita ha una pagina con i suoi volantini.
Es. Nettuno: https://www.carrefour.it/volantino/supermercato-carrefour-market-nettuno-via-trieste-78/5208

La pagina elenca i volantini del negozio ("dal 23/10 al 5/11  Prezzi Freschi", "Speciale Aia", ...).
Ogni volantino ha un numero (es. 57038) e il PDF si scarica da:
https://gdodig-car.youroperator.it/api/v1/geteditions/dwnpdfedition.php?id_edizione=<numero>

Teniamo solo i volantini alimentari (si escludono cataloghi di giocattoli, vini, casa, idee regalo, punti Payback).
Nel file della citta' serve per ogni negozio: "id" (es. 5208) e "url" (la pagina del negozio).
"""

import re
from datetime import date

import comune

NOME = "carrefour"
GIORNI = [3, 4, 5]   # i volantini cambiano di solito il giovedi
CONDIVISO = False

URL_PDF = "https://gdodig-car.youroperator.it/api/v1/geteditions/dwnpdfedition.php?id_edizione={}"
ESCLUDI = re.compile(r"giocattol|vini|casa|regalo|payback|bazar|tessile|elettronic|natale", re.I)
RE_VOCE = re.compile(r"dal\s+(\d{1,2})/(\d{1,2})\s+al\s+(\d{1,2})/(\d{1,2})\s+(.+)", re.I)


def date_voce(g1, m1, g2, m2):
    oggi = date.today()
    try:
        dal = date(oggi.year, int(m1), int(g1))
        al = date(oggi.year, int(m2), int(g2))
        if al < dal:
            # volantino a cavallo d'anno: se siamo a inizio anno e' iniziato l'anno scorso
            if oggi.month <= 6:
                dal = date(oggi.year - 1, int(m1), int(g1))
            else:
                al = date(oggi.year + 1, int(m2), int(g2))
    except ValueError:
        return None, None
    return dal.isoformat(), al.isoformat()


def trova_volantini(pagina):
    """Restituisce [(numero, titolo, dal, al)] dei volantini alimentari del negozio."""
    voci = pagina.eval_on_selector_all(
        "a[href]",
        "els => els.map(e => [(e.innerText||'').trim().replace(/\\s+/g,' '), e.href])",
    )
    trovati = {}
    for testo, href in voci:
        m = RE_VOCE.match(testo)
        n = re.search(r"/(\d{5})(?:\?|$)", href)
        if not m or not n:
            continue
        titolo = m.group(5).strip()
        if ESCLUDI.search(titolo):
            continue
        dal, al = date_voce(*m.group(1, 2, 3, 4))
        trovati.setdefault(n.group(1), (titolo, dal, al))
    return [(num, *v) for num, v in trovati.items()]


def scarica(contesto, negozio, etichetta):
    """Restituisce una lista di (file temporaneo, info), uno per ogni volantino alimentare."""
    pagina = contesto.new_page()
    risultati = []
    try:
        pagina.goto(negozio["url"], wait_until="domcontentloaded", timeout=60000)
        pagina.wait_for_timeout(8000)
        comune.prova_chiudi_cookie(pagina)
        volantini = trova_volantini(pagina)
        print(f"    volantini alimentari trovati per {negozio['id']}: {[(n, t) for n, t, *_ in volantini]}")
        if not volantini:
            print(f"[ERRORE] {etichetta}: nessun volantino trovato nella pagina del negozio")
            comune.salva_debug(pagina, comune.slug(etichetta))
            return [(None, None)]
        comune.CARTELLA_TMP.mkdir(exist_ok=True)
        for numero, titolo, dal, al in volantini:
            nome = f"{etichetta}_{numero}"
            try:
                risposta = contesto.request.get(URL_PDF.format(numero), timeout=120000)
                corpo = risposta.body()
                if not (risposta.ok and corpo[:5] == b"%PDF-"):
                    print(f"[ERRORE] {nome}: la risposta non e' un PDF (stato {risposta.status})")
                    risultati.append((None, None))
                    continue
                file = comune.CARTELLA_TMP / f"{comune.slug(nome)}.pdf"
                file.write_bytes(corpo)
                info = {"titolo": titolo}
                if dal and al:
                    info.update({"valido_dal": dal, "valido_al": al})
                print(f"[ok] {nome}: PDF scaricato ({len(corpo) // 1024} KB) - {titolo!r} {dal}..{al}")
                risultati.append((file, info))
            except Exception as errore:
                print(f"[ERRORE] {nome}: {str(errore).splitlines()[0][:200]}")
                risultati.append((None, None))
    except Exception as errore:
        print(f"[ERRORE] {etichetta}: {str(errore).splitlines()[0][:200]}")
        return [(None, None)]
    finally:
        pagina.close()
    return risultati
