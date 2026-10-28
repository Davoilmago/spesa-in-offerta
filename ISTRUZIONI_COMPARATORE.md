# Come aggiornare il comparatore (sito/offerte.js)

Il comparatore legge TUTTO da `sito/offerte.js` (prodotti, offerte, date, foto incorporate).
Formato: `window.OFFERTE={aggiornato, prodotti:[{id,e,n,cat,sub,u}], offerte:[{p,s,prezzo,q,l,z,c,dal,al,img}]}`
- `s` = catena (eurospin, lidl, todis, conad, pam, carrefour); `z` = zone: A (Anzio), N (Nettuno), AN (entrambe)
- `prezzo` = prezzo della confezione; `q` = quantita' nell'unita' del prodotto (`u`: kg, l, etto, pezzo...)
  Il confronto e' prezzo/q. Per i volantini "1+1" o "2 pezzi" il prezzo e' quello dei 2 pezzi e q raddoppia.
- `c` = 0 normale, 1 serve la carta fedelta', 2 serve l'app. `dal`/`al` = date ISO di validita'.
- Per prodotti a prezzo all'etto: prezzo = prezzo al kg e q = 10 (o prezzo all'etto e q = 1), restando coerenti con l'unita' `u`.
- Usare i nomi prodotto gia' esistenti quando possibile (`trova_prodotto`), altrimenti `nuovo_prodotto`.

## Procedura
1. Clona il repo. Leggi `sito/offerte.js` con `strumenti.offerte_lib.carica`.
2. Per ogni PDF nuovo in `volantini/<regione>/<citta>/<catena>*.pdf` NON ancora coperto dalle offerte (controlla le date in
   `sito/offerte.js` e le date del volantino): converti le pagine in JPEG a 2000 px di larghezza
   (`pdftoppm -jpeg -scale-to-x 2000 -scale-to-y -1`), disegna una griglia di coordinate sopra copie ridotte a 1000 px e LEGGI le pagine
   guardando le immagini (molti PDF Todis/Conad sono solo immagine). Ignora cosmesi, bazar, elettronica, abbigliamento, viaggi; tieni gli alimentari
   e i prodotti di casa/igiene/animali gia' presenti nel comparatore.
3. Per ogni offerta ritaglia la foto con `ritaglia(pagina, (x0,y0,x1,y1))` (le coordinate della griglia vanno moltiplicate x2 sulle immagini a 2000 px;
   scegli riquadri stretti sul solo prodotto, senza il prezzo). Aggiungi con `aggiungi_offerta(...)`.
4. Togli le offerte di quella catena e zona scadute (`al` precedente a oggi) senza toccare quelle ancora valide di altri negozi.
   Gli esempi completi sono in `esempi/` (esempio_eurospin.py, esempio_conad.py).
5. Salva con `salva(dati)`, verifica che il file si carichi, fai commit e push su `main`
   (il push di `sito/offerte.js` fa ripubblicare il sito da solo).
6. Controlla in Actions che la pubblicazione finisca con successo.

## Note Pam (Nettuno)
- I PDF sono due: `pam.pdf` (volantino principale) e `pam_2.pdf` ("Occasioni Extra"), pagine alte con il testo estraibile (`pdftotext`) utile per controllare i prezzi.
- "con APP" / "Pam Perte Plus" = `c` 2 (serve l'app). Prezzi "all'etto": prezzo = prezzo all'etto, q = 1 se l'unita' del prodotto e' `etto` (o q = 0.1 se e' `kg`).
- Ignora gli "sconto X% alla cassa" senza prezzo finale, vini/liquori e cosmesi non presenti nel comparatore.

## Note Carrefour (Nettuno)
- Il volantino principale e' `carrefour.pdf` ("Prezzi Freschi", pagine quadrate, prezzi per kg/etto/confezione scritti chiari). Il sito carrefour.it elenca anche ogni prodotto in testo.
- Controlla le date scritte sul volantino: "Speciale Aia" riporta una validita' piu' breve di quella indicata sul sito (scaduta il 22/10), quindi non va inserito se scaduto. "Speciale Purina" contiene pochi prezzi.
- Ignora i bollini "Prendi e Spendi" e "Spesamica Payback" (non sono sconti sul prezzo); il prezzo grande e' quello valido.


## iN's Mercato (Nettuno)
- Volantino a doppie pagine (13), PDF in volantini/lazio/nettuno/ins.pdf; date dalla copertina (OCR). Zona 'N', catena 'ins'.
- Leggere solo il cibo e la cura persona (pagine iniziali); le pagine casa/abbigliamento/piante non hanno prodotti del comparatore.
- Catene: eurospin, lidl, todis, conad, pam, carrefour, ins.


## Lidl: lettura completa (27/10)
- Il volantino Lidl va trascritto INTERO (cibo, casa, bazar, abbigliamento, piante, elettronica): 280 offerte. Prodotti non alimentari in categoria 'Altro' con sottocategorie (SUBS in sito/index.html).
- Non basta leggere solo i prodotti alimentari 'confrontabili': ogni prodotto del volantino deve comparire.

## REGOLA D'ORO: accorpare per FAMIGLIA
Il comparatore serve a confrontare i prezzi: prodotti uguali o molto simili vanno nella STESSA scheda
(tutti i vini rossi sotto "Vino rosso", i superalcolici sotto "Superalcolici", tutti i deodoranti sotto "Deodorante"...).
Marca, gusto e formato restano nella descrizione dell'offerta, NON nel nome del prodotto.
- `strumenti/famiglie.py` contiene le regole (regex -> famiglia) e viene eseguito in automatico da `offerte_lib.salva()`.
- Per un nuovo gruppo di prodotti basta aggiungere una riga `R(...)` in `REGOLE`.
- Un prodotto resta da solo solo se e' davvero unico (elettrodomestici, abiti, giocattoli...).
- Categorie con la virgola: "Latte, Uova & Latticini", "Pasta, Olio & Conserve".

## Associazioni decise dall'utente (da rispettare sempre)
- "Insalata iceberg" (e simili vendute al pezzo) va DENTRO la famiglia "Insalata" (categoria Frutta & Verdura, unita' kg). Poiche' il volantino da' il prezzo al pezzo, usa q=0.5 (peso stimato di circa 500 g) e scrivilo nella descrizione.
- "Alimentari vari" NON e' piu' una sottocategoria di "Altro": e' una sezione a parte (categoria "Alimentari vari"). Se per errore un prodotto arriva come Altro/Alimentari vari, normalizza() lo sposta da solo nella nuova sezione.

- Stendibiancheria -> famiglia "Stendini e assi da stiro".
- Qualsiasi lettiera per gatti (Easy+Go Sanicat, Natural Code, ecc.) -> famiglia "Lettiera per gatti".
