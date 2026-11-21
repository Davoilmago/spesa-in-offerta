"""Carrefour Market Latina - Black Friday (17-26 novembre 2026), zona L. Idempotente.
Uso: python3 strumenti/_carrefour_latina_bf.py  (richiede le parti in /tmp/claude-0/w/parte*.py e le pagine a 2000 px in /tmp/claude-0/w/hi/)"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from strumenti import offerte_lib as L
from PIL import Image
W = "/tmp/claude-0/w/"
R = []
for n in (1, 2, 3):
    ns = {}
    exec(open(W + f"parte{n}.py").read(), ns)
    R += ns["R"]
D1, AL = "2026-11-17", "2026-11-26"
d = L.carica()
d["offerte"] = [o for o in d["offerte"] if not (o["s"] == "carrefour" and o["z"] == "L" and o["dal"] == D1 and o["al"] == AL)]
cache = {}; saltate = []
for pag, box, prod, prezzo, q, desc, carta in R:
    if prod.startswith("NEW:"):
        nome, em, cat, sub, u = prod[4:].split("|")
        prod = L.nuovo_prodotto(d, nome, em, cat, u, sub or None)["n"]
    p = L.trova_prodotto(d, prod)
    if not p or prezzo <= 0 or q <= 0:
        saltate.append((pag, prod, prezzo, q)); continue
    f = W + "hi/p-%02d.jpg" % pag
    im = cache.setdefault(f, Image.open(f).convert("RGB"))
    foto = L.ritaglia(im, tuple(2 * v for v in box))
    L.aggiungi_offerta(d, p["id"], "carrefour", prezzo, q, desc, "L", D1, AL, carta, foto)
L.salva(d)
print(len(R), "righe;", "saltate:", saltate, "; offerte totali", len(d["offerte"]))
