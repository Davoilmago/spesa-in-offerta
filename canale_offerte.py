"""
Pubblica ogni mattina sul canale Telegram "il paniere del giorno":
per i prodotti di tutti i giorni (latte, pasta, olio, caffe'...) dice in quale supermercato
di Anzio e Nettuno costano meno OGGI, confrontando il prezzo al kg / al litro.

Configurazione (segreti del repository su GitHub: Settings > Secrets and variables > Actions):
  TELEGRAM_TOKEN   token del bot (da @BotFather)
  TELEGRAM_CANALE  nome del canale, es. @offerte_anzio_nettuno (il bot deve essere amministratore del canale)
  SITO_URL         (facoltativo) indirizzo del sito

Senza segreti lo script stampa soltanto il messaggio.
Uso:  python canale_offerte.py            -> stampa e, se configurato, pubblica
      python canale_offerte.py --prova    -> stampa soltanto
"""

import json
import os
import statistics
import sys
import urllib.parse
import urllib.request
from datetime import date

from strumenti.offerte_lib import carica

# Prodotti del paniere, nell'ordine in cui compaiono nel messaggio (nomi come nel comparatore)
PANIERE = [
    "Latte UHT", "Uova", "Burro", "Mozzarella", "Yogurt", "Stracchino, crescenza e robiola",
    "Pasta di semola", "Riso", "Farina", "Passata di pomodoro", "Olio extravergine di oliva", "Tonno in scatola",
    "Caffè macinato", "Biscotti", "Acqua", "Mele", "Banane", "Petto di pollo a fette", "Macinato misto",
    "Prosciutto crudo",
]
# Un prezzo molto sotto la media di solito e' un prodotto diverso o un errore di unita': lo scarto
SOGLIA_DIVERSO = 0.5
MIN_OFFERTE = 2

NOMI_CATENE = {
    "eurospin": "Eurospin", "lidl": "Lidl", "todis": "Todis", "conad": "Conad", "pam": "Pam",
    "carrefour": "Carrefour", "ins": "iN's", "md": "MD", "deco": "Decò", "elite": "Elite", "tigre": "Tigre",
}
ZONE = {"A": "Anzio", "N": "Nettuno", "AN": "Anzio e Nettuno"}
UNITA = {"kg": "al kg", "l": "al litro", "etto": "all'etto", "pezzo": "al pezzo", "uovo": "a uovo"}
GIORNI = ["lunedì", "martedì", "mercoledì", "giovedì", "venerdì", "sabato", "domenica"]
MESI = ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio", "agosto",
        "settembre", "ottobre", "novembre", "dicembre"]


def euro(x):
    return f"{x:.2f}".replace(".", ",") + " €"


def esc(t):
    return str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def paniere(dati, oggi):
    per_nome = {p["n"].lower(): p for p in dati["prodotti"]}
    valide = {}
    for o in dati["offerte"]:
        if o.get("dal", "0000") <= oggi <= o.get("al", "9999") and o.get("q") and o.get("prezzo"):
            valide.setdefault(o["p"], []).append(o)

    righe = []
    for nome in PANIERE:
        p = per_nome.get(nome.lower())
        if not p:
            continue
        offerte = valide.get(p["id"], [])
        if len(offerte) < MIN_OFFERTE:
            continue
        mediana = statistics.median(o["prezzo"] / o["q"] for o in offerte)
        buone = [o for o in offerte if o["prezzo"] / o["q"] >= SOGLIA_DIVERSO * mediana]
        if not buone:
            continue
        migliore = min(buone, key=lambda o: o["prezzo"] / o["q"])
        negozi = {o["s"] for o in buone}
        righe.append((p, migliore, migliore["prezzo"] / migliore["q"], len(negozi)))
    return righe


def componi_messaggio(righe, oggi_d, sito):
    testo = [f"🛒 <b>Il paniere di oggi: dove costa meno</b>\n"
             f"Anzio e Nettuno · {GIORNI[oggi_d.weekday()]} {oggi_d.day} {MESI[oggi_d.month - 1]}\n"]
    for p, o, u, n_negozi in righe:
        extra = " (con carta)" if o.get("c") == 1 else (" (con app)" if o.get("c") == 2 else "")
        testo.append(
            f"{p.get('e', '')} <b>{esc(p['n'])}</b>: {NOMI_CATENE.get(o['s'], o['s'])} "
            f"({ZONE.get(o.get('z'), o.get('z'))}) <b>{euro(o['prezzo'])}</b>{extra}\n"
            f"     {esc(o.get('l', ''))} · {euro(u)} {UNITA.get(p.get('u'), 'per ' + str(p.get('u')))}"
        )
    testo.append("\nPrezzi dai volantini in corso, confrontati tra tutti i supermercati della zona.")
    if sito:
        testo.append(f"👉 Tutte le offerte e il confronto completo: {sito}")
    return "\n".join(testo)


def pubblica(token, canale, testo):
    dati = urllib.parse.urlencode({
        "chat_id": canale, "text": testo, "parse_mode": "HTML", "disable_web_page_preview": "true",
    }).encode()
    with urllib.request.urlopen(f"https://api.telegram.org/bot{token}/sendMessage", dati, timeout=30) as r:
        risposta = json.load(r)
    if not risposta.get("ok"):
        raise SystemExit(f"Telegram ha risposto con un errore: {risposta}")


def main():
    oggi_d = date.today()
    righe = paniere(carica(), oggi_d.isoformat())
    if not righe:
        print("Nessuna offerta da pubblicare oggi.")
        return
    sito = os.environ.get("SITO_URL") or "https://davoilmago.github.io/spesa-in-offerta/"
    testo = componi_messaggio(righe, oggi_d, sito)
    print(testo)
    if "--prova" in sys.argv:
        return
    token, canale = os.environ.get("TELEGRAM_TOKEN"), os.environ.get("TELEGRAM_CANALE")
    if not token or not canale:
        print("\n(TELEGRAM_TOKEN o TELEGRAM_CANALE non impostati: messaggio non pubblicato)")
        return
    pubblica(token, canale, testo)
    print("\nPubblicato su", canale)


if __name__ == "__main__":
    main()
