"""
Strumenti per il file delle offerte del comparatore: sito/offerte.js

Il file contiene TUTTO: i prodotti, le offerte (prezzo, negozio, date) e le foto (incorporate).
Formato:   window.OFFERTE = { "aggiornato": "...", "prodotti": [...], "offerte": [...] };

  prodotti: {id, e (emoji), n (nome), cat, sub, u (unita' di confronto: kg, l, pezzo...)}
  offerte:  {p (id prodotto), s (negozio), prezzo, q (quantita' nella confezione, nell'unita' del prodotto),
             l (descrizione), z (zone: A=Anzio, N=Nettuno, AN=entrambe), c (0 / 1 serve la carta / 2 serve l'app),
             dal, al (date ISO), img (foto, data URI)}

Uso da Python:
    from strumenti.offerte_lib import carica, salva, ritaglia, aggiungi_offerta, togli_scadute
"""

import base64
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
        from famiglie import normalizza
        normalizza(dati)
    except ImportError:
        pass
    dati["aggiornato"] = date.today().isoformat()
    Path(percorso).write_text(PREFISSO + json.dumps(dati, ensure_ascii=False, separators=(",", ":")) + ";", encoding="utf-8")


def ritaglia(immagine_pagina, riquadro, larghezza_max=300, qualita=72):
    """Ritaglia riquadro=(x0, y0, x1, y1) da una pagina (percorso o immagine PIL). Restituisce la foto come data URI."""
    from PIL import Image

    im = Image.open(immagine_pagina) if not hasattr(immagine_pagina, "crop") else immagine_pagina
    foto = im.convert("RGB").crop(riquadro)
    if foto.width > larghezza_max:
        foto = foto.resize((larghezza_max, round(foto.height * larghezza_max / foto.width)))
    buffer = io.BytesIO()
    foto.save(buffer, "JPEG", quality=qualita, optimize=True)
    return "data:image/jpeg;base64," + base64.b64encode(buffer.getvalue()).decode()


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
