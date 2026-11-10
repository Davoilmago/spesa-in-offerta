"""
Strumenti per il file delle offerte del comparatore: sito/offerte.js

Il file contiene TUTTO: i prodotti, le offerte (prezzo, negozio, date) e le foto (incorporate).
Formato:   window.OFFERTE = { "aggiornato": "...", "prodotti": [...], "offerte": [...] };

  prodotti: {id, e (emoji), n (nome), cat, sub, u (unita' di confronto: kg, l, pezzo...)}
  offerte:  {p (id prodotto), s (negozio), prezzo, q (quantita' nella confezione, nell'unita' del prodotto),
             l (descrizione), z (zone: A=Anzio, N=Nettuno, AN=entrambe), c (0 / 1 serve la carta / 2 serve l'app),
             dal, al (date ISO), img (foto: percorso del file, es. "img/ab12cd34ef56.jpg", in sito/img/)}

Le foto NON stanno piu' dentro offerte.js: sono file separati in sito/img/ (nome = impronta del contenuto,
cosi' le foto uguali si riusano). salva() cancella da sito/img le foto che nessuna offerta usa piu'.

Uso da Python:
    from strumenti.offerte_lib import carica, salva, ritaglia, aggiungi_offerta, togli_scadute
"""

import base64
import hashlib
import io
import json
from datetime import date
from pathlib import Path

PREFISSO = "window.OFFERTE="


def carica(percorso="sito/offerte.js"):
    testo = Path(percorso).read_text(encoding="utf-8").strip()
    assert testo.startswith(PREFISSO), "file offerte.js non riconosciuto"
    return json.loads(testo[len(PREFISSO):].rstrip(";"))


def salva(dati, percorso="sito/offerte.js"):
    try:  # accorpa i prodotti per famiglia (vedi famiglie.py)
        try:
            from .famiglie import normalizza
        except ImportError:
            from famiglie import normalizza
        normalizza(dati)
    except ImportError:
        pass
    dati["aggiornato"] = date.today().isoformat()
    converti_foto_incorporate(dati)
    pulisci_foto(dati)
    Path(percorso).write_text(PREFISSO + json.dumps(dati, ensure_ascii=False, separators=(",", ":")) + ";", encoding="utf-8")


CARTELLA_IMG = Path("sito/img")


def ritaglia(immagine_pagina, riquadro, larghezza_max=300, qualita=72):
    """Ritaglia riquadro=(x0, y0, x1, y1) da una pagina (percorso o immagine PIL).
    Salva la foto come file in sito/img/ e restituisce il suo percorso relativo (es. "img/ab12cd34ef56.jpg")."""
    from PIL import Image

    im = Image.open(immagine_pagina) if not hasattr(immagine_pagina, "crop") else immagine_pagina
    foto = im.convert("RGB").crop(riquadro)
    if foto.width > larghezza_max:
        foto = foto.resize((larghezza_max, round(foto.height * larghezza_max / foto.width)))
    buffer = io.BytesIO()
    foto.save(buffer, "JPEG", quality=qualita, optimize=True)
    dati_foto = buffer.getvalue()
    nome = hashlib.sha1(dati_foto).hexdigest()[:12] + ".jpg"
    CARTELLA_IMG.mkdir(parents=True, exist_ok=True)
    (CARTELLA_IMG / nome).write_bytes(dati_foto)
    return "img/" + nome


def converti_foto_incorporate(dati):
    """Trasforma le vecchie foto incorporate (data URI) in file di sito/img/. Restituisce quante ne ha convertite."""
    n = 0
    CARTELLA_IMG.mkdir(parents=True, exist_ok=True)
    for o in dati["offerte"]:
        img = o.get("img")
        if img and img.startswith("data:image"):
            raw = base64.b64decode(img.split(",", 1)[1])
            nome = hashlib.sha1(raw).hexdigest()[:12] + ".jpg"
            (CARTELLA_IMG / nome).write_bytes(raw)
            o["img"] = "img/" + nome
            n += 1
    return n


def pulisci_foto(dati):
    """Cancella da sito/img le foto che nessuna offerta usa piu'. Restituisce quante ne ha tolte."""
    if not CARTELLA_IMG.exists():
        return 0
    usate = {Path(o["img"]).name for o in dati["offerte"] if o.get("img") and not o["img"].startswith("data:")}
    tolte = 0
    for f in CARTELLA_IMG.glob("*.jpg"):
        if f.name not in usate:
            f.unlink()
            tolte += 1
    return tolte


def trova_prodotto(dati, nome):
    for p in dati["prodotti"]:
        if p["n"].lower() == nome.lower():
            return p
    return None


def nuovo_prodotto(dati, nome, emoji, categoria, unita, sub=None):
    p = trova_prodotto(dati, nome)
    if p:
        return p
    p = {"id": max([x["id"] for x in dati["prodotti"]] + [0]) + 1, "e": emoji, "n": nome, "cat": categoria, "sub": sub, "u": unita}
    dati["prodotti"].append(p)
    return p


def aggiungi_offerta(dati, prodotto, negozio, prezzo, q, descrizione, zone, dal, al, carta=0, img=None):
    """Aggiunge un'offerta. 'prodotto' e' il nome o l'id."""
    pid = prodotto if isinstance(prodotto, int) else trova_prodotto(dati, prodotto)["id"]
    dati["offerte"].append({"p": pid, "s": negozio, "prezzo": prezzo, "q": q, "l": descrizione, "z": zone,
                            "c": carta, "dal": dal, "al": al, "img": img})


def togli_scadute(dati, oggi=None, giorni_tolleranza=0):
    """Toglie le offerte finite da piu' di 'giorni_tolleranza' giorni e i prodotti rimasti senza offerte."""
    oggi = oggi or date.today()
    tenute = [o for o in dati["offerte"] if (date.fromisoformat(o["al"]) - oggi).days >= -giorni_tolleranza]
    tolte = len(dati["offerte"]) - len(tenute)
    dati["offerte"] = tenute
    usati = {o["p"] for o in tenute}
    dati["prodotti"] = [p for p in dati["prodotti"] if p["id"] in usati]
    return tolte
