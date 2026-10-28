# Canale Telegram "paniere del giorno" (aggiunto il 28/10/2026)

Ogni mattina (08:00 UTC) il workflow `.github/workflows/canale-telegram.yml` esegue `canale_offerte.py`,
che pubblica sul canale Telegram "il paniere di oggi": per 20 prodotti di tutti i giorni (lista `PANIERE`
in `canale_offerte.py`) il supermercato di Anzio/Nettuno dove costano meno oggi, con prezzo al kg/litro e link al sito.

- Confronta il prezzo per unita' (prezzo/q) solo tra offerte valide oggi.
- Scarta i prezzi sotto il 50% della mediana del prodotto (di solito sono prodotti diversi della stessa famiglia).
- Scartata la versione "offerte con il risparmio piu' alto": confrontava prodotti diversi (es. orzo dentro "caffe'")
  e dava sconti finti del 90%.
- Senza segreti il workflow mostra solo il messaggio nel log, non pubblica. Prova locale: `python canale_offerte.py --prova`

## Da fare per attivarlo (10 minuti)
1. Telegram: matita -> Nuovo canale -> nome tipo "Offerte Anzio e Nettuno" -> pubblico (es. @offerte_anzio_nettuno)
2. @BotFather -> /newbot -> un bot nuovo (es. OfferteAnzioBot), copiare il token (non riusare quello dell'oro)
3. Impostazioni del canale -> Amministratori -> aggiungere il bot
4. GitHub -> Settings -> Secrets and variables -> Actions -> New repository secret:
   - `TELEGRAM_TOKEN` = token del bot
   - `TELEGRAM_CANALE` = nome del canale con la @
5. Actions -> "Canale Telegram (paniere del giorno)" -> Run workflow: il primo messaggio esce subito

## Post da mettere nei gruppi Facebook di Anzio e Nettuno
> Ciao a tutti! 👋 Ho creato un sito gratuito che confronta ogni giorno le offerte di tutti i supermercati di Anzio e Nettuno:
> Conad, Lidl, Eurospin, MD, Todis, Pam, Carrefour, Decò, Elite e iN's. Scrivi un prodotto e vedi subito dove costa meno.
> Ogni mattina sul canale Telegram esce anche il "paniere del giorno": latte, pasta, olio, carne, frutta… e dove conviene comprarli.
> 👉 Sito: [link]  👉 Canale: [link]
> È gratis e senza pubblicità. Se vi è utile, condividetelo! 🛒

## Piano per guadagnarci (deciso il 28/10)
1. Canale attivo + post nei gruppi Facebook locali + contatore visite sul sito
2. Con qualche centinaio di iscritti: paginetta per i negozi della zona (macellerie, panifici, ortofrutta...)
   con i numeri di utenti e spazi sponsorizzati a 20-50 euro al mese. Obiettivo: 8-10 negozi = 200-300 euro al mese.
3. Da verificare prima di incassare: termini d'uso per loghi/volantini delle catene, cookie e privacy se si mette
   pubblicita', come dichiarare gli incassi (all'inizio di solito prestazione occasionale: chiedere a un commercialista).
