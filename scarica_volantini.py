"""
Spesa in Offerta - avvio dello scarico dei volantini.

Come si usa:
  python scarica_volantini.py                 -> tutte le catene di tutte le citta'
  python scarica_volantini.py lidl            -> solo Lidl
  python scarica_volantini.py eurospin lidl   -> solo queste catene
  python scarica_volantini.py --solo-oggi     -> solo le catene previste per il giorno di oggi
                                                 (e' quello che usa l'avvio automatico)

Come e' organizzato il progetto:
  dati/<regione>/<citta>.json                 i negozi di ogni citta' (qui si aggiungono citta' e negozi)
  catene/<catena>.py                          come si scarica il volantino di ogni supermercato
  comune.py                                   gli strumenti usati da tutte le catene
  volantini/<regione>/<citta>/<catena>.pdf    i PDF scaricati
  volantini/elenco.json                       l'elenco di tutto quello che e' stato scaricato
"""

import argparse
import importlib
import json
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from playwright.sync_api import sync_playwright

import comune

CARTELLA_DATI = Path("dati")


def carica_catena(nome):
    return importlib.import_module(f"catene.{nome}")


def leggi_zone():
    """Legge i file dati/<regione>/<citta>.json. Restituisce (zone, numero di errori)."""
    zone = []
    errori = 0
    for percorso in sorted(CARTELLA_DATI.glob("*/*.json")):
        try:
            dati = json.loads(percorso.read_text(encoding="utf-8"))
            if not dati.get("regione") or not dati.get("citta"):
                raise ValueError("mancano 'regione' o 'citta'")
            zone.append(dati)
        except Exception as errore:
            print(f"[ERRORE] il file {percorso} non e' valido: {errore}")
            errori += 1
    return zone, errori


def elenco_lavori(zone, catene):
    """Un lavoro per ogni negozio di ogni citta' delle catene scelte."""
    lavori = []
    for zona in zone:
        for catena, negozi in zona.get("negozi", {}).items():
            if catena not in catene:
                continue
            for negozio in negozi:
                lavori.append(
                    {
                        "catena": catena,
                        "regione": zona["regione"],
                        "citta": zona["citta"],
                        "cap": zona.get("cap", ""),
                        "negozio": negozio,
                    }
                )
    return lavori


def leggi_elenco():
    """Legge l'elenco gia' salvato (ignora le voci del vecchio formato)."""
    percorso = comune.CARTELLA_PDF / "elenco.json"
    try:
        voci = json.loads(percorso.read_text(encoding="utf-8"))
    except Exception:
        return []
    return [v for v in voci if isinstance(v, dict) and "regione" in v]


def cartella_zona(regione, citta):
    return comune.CARTELLA_PDF / comune.slug(regione) / comune.slug(citta)


def leggi_argomenti(argv=None):
    parser = argparse.ArgumentParser(description="Scarica i volantini dei supermercati.")
    parser.add_argument("catene", nargs="*", help="catene da scaricare (se vuoto: tutte)")
    parser.add_argument("--solo-oggi", action="store_true", help="solo le catene previste per oggi")
    return parser.parse_args(argv)


def main(argv=None):
    args = leggi_argomenti(argv)
    comune.CARTELLA_PDF.mkdir(exist_ok=True)

    zone, errori = leggi_zone()
    nomi_presenti = sorted({c for z in zone for c in z.get("negozi", {})})
    richieste = [c.lower() for c in args.catene] or nomi_presenti

    moduli = {}
    for nome in richieste:
        try:
            moduli[nome] = carica_catena(nome)
        except ModuleNotFoundError as errore:
            print(f"[ERRORE] catena '{nome}' non utilizzabile: manca catene/{nome}.py ({errore})")
            errori += 1

    if args.solo_oggi:
        giorno = datetime.now(ZoneInfo("Europe/Rome")).weekday()
        moduli = {n: m for n, m in moduli.items() if giorno in getattr(m, "GIORNI", range(7))}
        print(f"Catene previste per oggi: {', '.join(sorted(moduli)) or 'nessuna'}")

    lavori = elenco_lavori(zone, set(moduli))
    if not lavori:
        print("Niente da scaricare.")
        sys.exit(1 if errori else 0)

    nuove_voci = []
    tenuti = {}               # (regione, citta, catena) -> {impronta: nome del file}
    gruppi_con_errori = set()
    cache = {}                # volantini condivisi tra citta' (es. Lidl nazionale): (catena, chiave) -> (file, info)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        contesto = browser.new_context(
            locale="it-IT",
            timezone_id="Europe/Rome",
            accept_downloads=True,
            viewport={"width": 1400, "height": 900},
        )

        for lavoro in lavori:
            catena = lavoro["catena"]
            modulo = moduli[catena]
            negozio = lavoro["negozio"]
            gruppo = (lavoro["regione"], lavoro["citta"], catena)
            nota = negozio.get("nota", "")

            chiave = None
            if getattr(modulo, "CONDIVISO", False):
                chiave = modulo.chiave_condivisione(negozio)

            if chiave is not None and (catena, chiave) in cache:
                temporaneo, info = cache[(catena, chiave)]
                print(f"[condiviso] {catena} {lavoro['citta']}: uso il volantino gia' scaricato ({chiave})")
            else:
                etichetta = f"{catena}_{chiave or negozio.get('id') or 'unico'}"
                temporaneo, info = modulo.scarica(contesto, negozio, etichetta)
                if chiave is not None:
                    cache[(catena, chiave)] = (temporaneo, info)

            if temporaneo is None:
                errori += 1
                gruppi_con_errori.add(gruppo)
                continue

            gia_salvati = tenuti.setdefault(gruppo, {})
            firma = comune.impronta(temporaneo)
            if firma in gia_salvati:
                print(f"[uguale] {lavoro['citta']} {catena} ({nota}): stesso volantino di {gia_salvati[firma]}, non lo duplico")
                continue

            cartella = cartella_zona(lavoro["regione"], lavoro["citta"])
            cartella.mkdir(parents=True, exist_ok=True)
            nome_file = f"{catena}.pdf" if not gia_salvati else f"{catena}_{len(gia_salvati) + 1}.pdf"
            destinazione = cartella / nome_file
            shutil.copyfile(temporaneo, destinazione)
            gia_salvati[firma] = nome_file

            voce = {
                "file": destinazione.relative_to(comune.CARTELLA_PDF).as_posix(),
                "regione": lavoro["regione"],
                "citta": lavoro["citta"],
                "cap": lavoro["cap"],
                "catena": catena,
                "negozio": nota,
                "sha256": firma,
                "byte": destinazione.stat().st_size,
                "scaricato_il": datetime.now().isoformat(timespec="seconds"),
            }
            voce.update(info or {})
            nuove_voci.append(voce)
            print(f"[salvato] {voce['file']} ({nota})")

        browser.close()

    # Se per una citta'/catena e' andato tutto bene, tolgo i file di settimane precedenti che non servono piu'.
    gruppi_a_posto = {g for g in tenuti if g not in gruppi_con_errori}
    for regione, citta, catena in gruppi_a_posto:
        cartella = cartella_zona(regione, citta)
        validi = set(tenuti[(regione, citta, catena)].values())
        for vecchio in cartella.glob(f"{catena}*.pdf"):
            if re.fullmatch(rf"{re.escape(catena)}(_\d+)?\.pdf", vecchio.name) and vecchio.name not in validi:
                vecchio.unlink()
                print(f"[rimosso] {vecchio.relative_to(comune.CARTELLA_PDF).as_posix()} (non piu' presente)")

    # I PDF del vecchio formato (direttamente in volantini/, senza cartelle) non servono piu':
    # li tolgo solo se questa volta e' andato tutto bene, cosi' non perdo mai l'ultima copia.
    if errori == 0:
        for vecchio in comune.CARTELLA_PDF.glob("*.pdf"):
            vecchio.unlink()
            print(f"[rimosso] {vecchio.name} (vecchio formato)")

    # L'elenco si aggiorna: le catene non scaricate oggi restano come erano.
    file_nuovi = {v["file"] for v in nuove_voci}
    elenco = [
        v
        for v in leggi_elenco()
        if (v["regione"], v["citta"], v["catena"]) not in gruppi_a_posto and v["file"] not in file_nuovi
    ]
    elenco.extend(nuove_voci)
    elenco.sort(key=lambda v: v["file"])
    (comune.CARTELLA_PDF / "elenco.json").write_text(
        json.dumps(elenco, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    shutil.rmtree(comune.CARTELLA_TMP, ignore_errors=True)

    print(f"\nFatto: {len(nuove_voci)} file salvati, {errori} errori.")
    # Se qualcosa e' andato storto il lavoro risulta "fallito" e GitHub ti manda una email.
    sys.exit(1 if errori else 0)


if __name__ == "__main__":
    main()
