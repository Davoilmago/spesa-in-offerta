"""
Spesa in Offerta - prepara il sito (le pagine dei volantini come immagini + l'indice per l'app).

Cosa fa:
  1. legge volantini/elenco.json (scritto da scarica_volantini.py)
  2. trasforma ogni PDF in una immagine per pagina:  sito/flyers/<codice>/01.jpg, 02.jpg ...
     (un PDF uguale usato in piu' citta' viene trasformato una volta sola)
  3. cerca le date di validita' (nell'elenco, nel testo del PDF o con la regola della catena)
  4. scrive l'indice  sito/dati/volantini.json  che l'app legge da sola

Si lancia con:  python prepara_sito.py
Servono i programmi pdftoppm / pdftotext (pacchetto poppler-utils).
"""

import json
import re
import shutil
import subprocess
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

CARTELLA_PDF = Path("volantini")
CARTELLA_SITO = Path("sito")
LARGHEZZA = 1000          # larghezza delle pagine in pixel
QUALITA_JPEG = 70

MESI = {
    "gennaio": 1, "febbraio": 2, "marzo": 3, "aprile": 4, "maggio": 5, "giugno": 6,
    "luglio": 7, "agosto": 8, "settembre": 9, "ottobre": 10, "novembre": 11, "dicembre": 12,
}
NOMI_MESI = "|".join(MESI)
GIORNO = r"(?:lun|mar|mer|gio|ven|sab|dom)[a-zì]*"

# "da venerdì 30 ottobre a giovedì 12 novembre 2026"
RE_DA_A = re.compile(
    rf"\bda\s+{GIORNO}\s+(\d{{1,2}})[°º]?\s+({NOMI_MESI})(?:\s+(\d{{4}}))?\s+a\s+{GIORNO}\s+(\d{{1,2}})[°º]?\s+({NOMI_MESI})(?:\s+(\d{{4}}))?",
    re.I,
)
# "dal 15 al 28 ottobre" / "dal 28 ottobre al 3 novembre 2026"
RE_DAL_AL = re.compile(
    rf"\bdal\s+(\d{{1,2}})[°º]?(?:\s+({NOMI_MESI}))?(?:\s+(\d{{4}}))?\s+al\s+(\d{{1,2}})[°º]?\s+({NOMI_MESI})(?:\s+(\d{{4}}))?",
    re.I,
)
# "dal 15/10 al 28/10"
RE_NUM = re.compile(r"\bdal\s+(\d{1,2})[/.](\d{1,2})(?:[/.](\d{2,4}))?\s+al\s+(\d{1,2})[/.](\d{1,2})(?:[/.](\d{2,4}))?", re.I)


def esegui(comando):
    return subprocess.run(comando, capture_output=True, text=True, check=False)


def slug(testo):
    return re.sub(r"[^a-z0-9]+", "-", testo.lower()).strip("-")


def numero_pagine(pdf):
    risultato = esegui(["pdfinfo", str(pdf)])
    trovato = re.search(r"^Pages:\s+(\d+)", risultato.stdout, re.M)
    return int(trovato.group(1)) if trovato else 0


def testo_pagine(pdf, prima, ultima):
    risultato = esegui(["pdftotext", "-f", str(prima), "-l", str(ultima), "-layout", str(pdf), "-"])
    return re.sub(r"\s+", " ", risultato.stdout or "")


def crea_data(anno, mese, giorno):
    try:
        return date(anno, mese, giorno)
    except ValueError:
        return None


def trova_date(testo, anno_riferimento, al_atteso=None, giorno_riferimento=None):
    """Cerca nel testo un periodo di validita' (il primo che compare).
    Se si conosce gia' la data di fine ('al_atteso'), sceglie il periodo che finisce quel giorno.
    Restituisce (dal, al) come date oppure None."""
    candidati = []   # (posizione nel testo, ...)
    for m in RE_DA_A.finditer(testo):
        g1, m1, a1, g2, m2, a2 = m.groups()
        candidati.append((m.start(), int(g1), MESI[m1.lower()], a1, int(g2), MESI[m2.lower()], a2))
    for m in RE_DAL_AL.finditer(testo):
        g1, m1, a1, g2, m2, a2 = m.groups()
        mese2 = MESI[m2.lower()]
        mese1 = MESI[m1.lower()] if m1 else mese2
        candidati.append((m.start(), int(g1), mese1, a1, int(g2), mese2, a2))
    for m in RE_NUM.finditer(testo):
        g1, m1, a1, g2, m2, a2 = m.groups()
        candidati.append((m.start(), int(g1), int(m1), a1, int(g2), int(m2), a2))
    candidati.sort(key=lambda c: c[0])

    validi = []
    for _, g1, m1, a1, g2, m2, a2 in candidati:
        def anno(a, default):
            if not a:
                return default
            a = int(a)
            return a + 2000 if a < 100 else a

        if not a1 and not a2:
            # senza anno: scelgo l'anno che mette il periodo piu' vicino al giorno del download
            migliore = None
            for anno1 in (anno_riferimento - 1, anno_riferimento, anno_riferimento + 1):
                anno2 = anno1 if (m1, g1) <= (m2, g2) else anno1 + 1
                d1, d2 = crea_data(anno1, m1, g1), crea_data(anno2, m2, g2)
                if not (d1 and d2):
                    continue
                riferimento = date(anno_riferimento, 6, 30) if giorno_riferimento is None else giorno_riferimento
                distanza = 0 if d1 <= riferimento <= d2 else min(abs((riferimento - d1).days), abs((riferimento - d2).days))
                if migliore is None or distanza < migliore[0]:
                    migliore = (distanza, d1, d2)
            dal, al = (migliore[1], migliore[2]) if migliore else (None, None)
        else:
            anno2 = anno(a2, anno_riferimento)
            anno1 = anno(a1, anno2 if (m1, g1) <= (m2, g2) else anno2 - 1)
            dal, al = crea_data(anno1, m1, g1), crea_data(anno2, m2, g2)
        if dal and al and dal <= al and (al - dal).days <= 45:
            validi.append((dal, al))
    if al_atteso:
        for dal, al in validi:
            if al == al_atteso:
                return dal, al
        return None
    return validi[0] if validi else None


def periodo_per_catena(voce, riferimento):
    """Regole di riserva quando il periodo non si trova da nessun'altra parte."""
    if voce["catena"] == "eurospin":   # volantino settimanale lunedi-domenica
        lunedi = riferimento - timedelta(days=riferimento.weekday())
        return lunedi, lunedi + timedelta(days=6)
    return None


def converti(pdf, destinazione):
    """PDF -> 01.jpg, 02.jpg ... Restituisce il numero di pagine create."""
    if destinazione.exists():
        shutil.rmtree(destinazione)
    destinazione.mkdir(parents=True)
    risultato = esegui([
        "pdftoppm", "-jpeg", "-jpegopt", f"quality={QUALITA_JPEG}",
        "-scale-to-x", str(LARGHEZZA), "-scale-to-y", "-1", str(pdf), str(destinazione / "p"),
    ])
    pagine = sorted(destinazione.glob("p-*.jpg"))
    if risultato.returncode != 0 or not pagine:
        print(f"[ERRORE] conversione non riuscita per {pdf}: {risultato.stderr.strip()[:200]}")
        shutil.rmtree(destinazione, ignore_errors=True)
        return 0
    for i, pagina in enumerate(pagine, start=1):   # nomi uguali per tutti: 01.jpg, 02.jpg ...
        pagina.rename(destinazione / f"{i:02d}.jpg")
    return len(pagine)


def leggi_elenco():
    try:
        voci = json.loads((CARTELLA_PDF / "elenco.json").read_text(encoding="utf-8"))
    except Exception as errore:
        print(f"[ERRORE] non riesco a leggere volantini/elenco.json: {errore}")
        return []
    return [v for v in voci if isinstance(v, dict) and v.get("file")]


def main():
    voci = leggi_elenco()
    if not voci:
        print("Nessun volantino da preparare.")
        sys.exit(1)

    cartella_pagine = CARTELLA_SITO / "flyers"
    cartella_dati = CARTELLA_SITO / "dati"
    cartella_dati.mkdir(parents=True, exist_ok=True)
    if cartella_pagine.exists():
        shutil.rmtree(cartella_pagine)
    cartella_pagine.mkdir(parents=True)

    errori = 0
    convertiti = {}   # sha256 -> {codice, n, testo}
    zone = {}

    for voce in sorted(voci, key=lambda v: v["file"]):
        pdf = CARTELLA_PDF / voce["file"]
        if not pdf.exists():
            print(f"[ERRORE] manca il file {pdf}")
            errori += 1
            continue

        firma = voce.get("sha256") or pdf.name
        if firma not in convertiti:
            codice = firma[:12]
            n = converti(pdf, cartella_pagine / codice)
            if n == 0:
                errori += 1
                continue
            convertiti[firma] = {"codice": codice, "n": n, "copertina": testo_pagine(pdf, 1, 1), "testo": testo_pagine(pdf, 1, 3)}
            print(f"[pagine] {voce['file']}: {n} pagine -> flyers/{codice}")
        c = convertiti[firma]

        try:
            riferimento = datetime.fromisoformat(voce["scaricato_il"]).date()
        except Exception:
            riferimento = date.today()

        dal = al = None
        fonte = None
        try:
            if voce.get("valido_dal") and voce.get("valido_al"):
                dal, al, fonte = date.fromisoformat(voce["valido_dal"]), date.fromisoformat(voce["valido_al"]), "elenco"
        except ValueError:
            dal = al = None
        if dal is None:
            al_atteso = None
            try:
                al_atteso = date.fromisoformat(voce["valido_al"]) if voce.get("valido_al") else None
            except ValueError:
                pass
            # prima la copertina, poi le prime pagine
            periodo = trova_date(c["copertina"], riferimento.year, al_atteso, riferimento) or trova_date(c["testo"], riferimento.year, al_atteso, riferimento)
            if periodo:
                dal, al = periodo
                fonte = "testo del PDF"
        if dal is None and voce.get("valido_al"):
            try:
                al, fonte = date.fromisoformat(voce["valido_al"]), "scadenza indicata sul sito"
            except ValueError:
                al = None
        if dal is None and al is None:
            periodo = periodo_per_catena(voce, riferimento)
            if periodo:
                dal, al = periodo
                fonte = "regola della catena"

        voce_sito = {
            "dir": f"flyers/{c['codice']}",
            "pagine": c["n"],
            "titolo": voce.get("titolo") or "",
            "dal": dal.isoformat() if dal else "",
            "al": al.isoformat() if al else "",
            "fonte_date": fonte or "",
            "negozio": voce.get("negozio", ""),
            "scaricato_il": voce.get("scaricato_il", ""),
        }
        zone.setdefault(voce["citta"], {}).setdefault(voce["catena"], []).append(voce_sito)
        print(f"    {voce['citta']} / {voce['catena']}: validita' {voce_sito['dal'] or '?'} - {voce_sito['al'] or '?'} ({fonte or 'sconosciuta'})")

    indice = {"generato_il": datetime.now().isoformat(timespec="seconds"), "zone": zone}
    (cartella_dati / "volantini.json").write_text(json.dumps(indice, indent=1, ensure_ascii=False), encoding="utf-8")

    print(f"\nFatto: {len(convertiti)} volantini convertiti, {errori} errori.")
    sys.exit(1 if errori else 0)


if __name__ == "__main__":
    main()
