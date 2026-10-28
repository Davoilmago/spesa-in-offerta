"""
Raggruppamento per FAMIGLIA dei prodotti del comparatore.

Regola d'oro: nel comparatore si accorpano i prodotti uguali o molto simili in UNA scheda
(es. tutti i vini rossi sotto "Vino rosso", tutti i deodoranti sotto "Deodorante"), cosi' si
confrontano i prezzi dei vari supermercati. Il dettaglio (marca, gusto, formato) resta nella
descrizione dell'offerta. Un prodotto resta da solo SOLO se e' davvero unico.

Come funziona: `normalizza(dati)` ricalcola le famiglie di tutti i prodotti in base alle regole
qui sotto (la prima che corrisponde vince) e sposta le offerte, convertendo la quantita'
(es. etto -> kg). E' idempotente e viene chiamata da `offerte_lib.salva()`: quindi basta
inserire il prodotto col suo nome specifico, poi la scheda viene accorpata da sola.
Per un nuovo gruppo basta aggiungere una riga a REGOLE.

Una regola: R(espressione, "Nome famiglia", "Categoria", "unita'", emoji, sotto-categoria, filtro-categoria, volume)
  - espressione: regex sul nome del prodotto (minuscolo)
  - filtro-categoria: la regola vale solo se la categoria attuale inizia cosi'
  - volume=True: ammette l <-> kg (latticini, yogurt...)
"""
import re

CAT_FIX = {
    "Latte Uova & Latticini": "Latte, Uova & Latticini",
    "Pasta Olio & Conserve": "Pasta, Olio & Conserve",
    "Filetti di acciughe": "Pesce",
}
CONT = {"pezzo", "pz", "uovo", "rotolo", "cialda", "100 pz"}
FRUTTA, CARNE, PESCE, LATTE, SALUMI, PASTA, COLAZ, SURG, BEV, ALTRO = (
    "Frutta & Verdura", "Carne", "Pesce", "Latte, Uova & Latticini", "Salumi & Formaggi",
    "Pasta, Olio & Conserve", "Colazione & Dolci", "Surgelati", "Bevande", "Altro")
ALIM = "Alimentari vari"   # sezione a parte (prima era una sottocategoria di "Altro")
EMO = {ALIM: "🍽️", FRUTTA: "🍎", CARNE: "🥩", PESCE: "🐟", LATTE: "🥛", SALUMI: "🥓", PASTA: "🍝", COLAZ: "🥐", SURG: "🧊", BEV: "🧃", ALTRO: "🛒"}

REGOLE = []


def R(rx, nome, cat, unita, emoji=None, sub=None, g=None, vol=False):
    REGOLE.append((re.compile(rx), nome, cat, unita, emoji or EMO[cat], sub, g, vol))


# ---------------- BEVANDE ----------------
R(r"rosato|rosé", "Vino rosato", BEV, "l", "🍷", g="Bev")
R(r"traminer|sauvignon|chardonnay|soave|lugana|verdicchio|pecorino offida|orvieto|solopaca|marino doc|trebbiano|trevenezie|duchessa lia|vino bianco|\bbianco\b|pinot grigio|vermentino|falanghina|greco di tufo|est est est|passerina|zibibbo|frizzante|vini d.abruzzo|vini igt", "Vino bianco", BEV, "l", "🥂", g="Bev")
R(r"vino rosso|\brosso\b|chianti|montepulciano|nero d.avola|primitivo|valpolicella|syrah|merlot|frappato|romae roma|lambrusco|vini crifo|terre siciliane|calenzana|nero di troia|barbera|cabernet|sangiovese|morellino|brunello|montefalco", "Vino rosso", BEV, "l", "🍷", g="Bev")
R(r"prosecco|spumante|valdobbiadene|cartizze|franciacorta|champagne", "Prosecco", BEV, "l", "🥂", g="Bev")
R(r"spritz|aperol|campari|aperitiv|bitter", "Aperitivi e spritz", BEV, "l", "🍹", g="Bev")
R(r"\bbirr|bjorne|ma\.ma|faxe", "Birra", BEV, "l", "🍺", g="Bev")
R(r"vodka|whisk|jack daniel|\brum\b|\bgin\b|grappa|distillat|cognac|brandy|tequila|bourbon", "Superalcolici", BEV, "l", "🥃", g="Bev")
R(r"amaro|sambuca|genziana|liquore|cointreau|limoncello|disaronno|baileys|amaretto|vecchio", "Amari e liquori", BEV, "l", "🥃", g="Bev")
R(r"^acqua(?! tonica)|levissima", "Acqua", BEV, "l", "💧", g="Bev")
R(r"energy|energetic|red bull|energade", "Bevande energetiche", BEV, "l", "⚡", g="Bev")
R(r"bevanda (vegetale|di soia|a base|coco|cocco|di mandorla|di riso|di avena)|orasì|bjorg|valsoia|sogno veg.*bevanda|bevanda.*sogno veg", "Bevanda vegetale", BEV, "l", "🥛")
R(r"^(thè|tè)\b|\bthè\b", "Tè freddo", BEV, "l", "🍵", g="Bev")
R(r"bibit|gassat|\bcola\b|fanta|sprite|pepsi|tonic|gasco|guizza|aranciata|chinotto|lemonsoda|schweppes|tonica|^bevande? (zero|i classici|conad)|bevanda zero", "Bibite gassate", BEV, "l", "🥤", g="Bev")
R(r"succ[oh]|bevanda (al|alla|lime)|frullato di frutta|skipper|valfrutta|nettare|spremuta|nettari|bravo rauch|polposa", "Succo di frutta", BEV, "l", "🧃", g="Bev")

# ---------------- LATTE, UOVA, LATTICINI ----------------
R(r"latte.*(senza lattosio|zymil|accadì|alta digeribilità)|accadì", "Latte senza lattosio", LATTE, "l", "🥛", vol=True)
R(r"^latte (uht|parzialmente|intero|microfiltrato|fresco|di)|latte uht|^latte$|^latte per|^latte scremato", "Latte UHT", LATTE, "l", "🥛", vol=True)
R(r"^(frozen )?yogurt|yomo|sojasun|^yogurt|yakult|actimel|probiotic|yogurt da bere", "Yogurt", LATTE, "kg", "🥛", g="Latte", vol=True)
R(r"kefir", "Kefir", LATTE, "kg", "🥛", vol=True)
R(r"^(?!.*(carrozza|pizza|pomodoro|cotolett))(mozzarell|mozar|cuor di latte|ciliegine)", "Mozzarella", LATTE, "kg", "🧀")
R(r"stracchino|crescenza|robiola|squacquerone", "Stracchino, crescenza e robiola", LATTE, "kg", "🧀")
R(r"philadelphia|formaggio fresco|formaggio spalmabile|exquisa|fresco cremoso", "Formaggio spalmabile", LATTE, "kg", "🧀")
R(r"^ricotta|ricottin", "Ricotta", LATTE, "kg", "🧀")
R(r"^burro(?! di arachidi)", "Burro", LATTE, "kg", "🧈")
R(r"^panna|crema vegetale da montare|panna spray|panna per caffè", "Panna", LATTE, "l", "🥛", vol=True)
R(r"^albume", "Albume", LATTE, "kg", "🥚", vol=True)
R(r"uova", "Uova", LATTE, "uovo", "🥚")

# ---------------- FORMAGGI E SALUMI ----------------
R(r"grana|parmigiano|parmareggio|parmissimo|reggiano|grattugiato", "Grana e formaggi duri", SALUMI, "etto", "🧀", g="Salumi")
R(r"^pecorino|pecorino (sardo|stagionato|gran)|cacio ercole", "Pecorino", SALUMI, "etto", "🧀", g="Salumi")
R(r"gorgonzola", "Gorgonzola", SALUMI, "etto", "🧀")
R(r"provol|scamorz|pasta filata", "Provola, scamorza e provolone", SALUMI, "etto", "🧀", g="Salumi")
R(r"leerdammer|emmental|gouda|edam|sottilette|formaggio fuso|latteria nazionale", "Formaggio a fette", SALUMI, "etto", "🧀")
R(r"caciotta|casciotta|primosale|tomino|biraghini|formaggio (dolce|corno)|boncaccio|primo sale|asiago|\btoma\b|grottone|settecolli|maasdam|fontal|di capra|caciottone|piave|scoparolo|feta|bergader|cremosissimo|galbanino|formaggio misto|formaggio stagionato|^formaggio (?!fresco|a fette|spalmabile|grattugiato)|brie|ciambella|brigante|rugantino", "Caciotta e formaggi semiduri", SALUMI, "etto", "🧀", g="Salumi")
R(r"prosciutto (crudo|di san daniele|di carpegna|san daniele|di parma)|sofficiotto|culatta|prosciutto di modena", "Prosciutto crudo", SALUMI, "etto", "🥓")
R(r"prosciutto cotto|cotto di tacchino|julienne|il cotto|sofficette|prosciutto in vaschetta|tuttoprosciutto", "Prosciutto cotto", SALUMI, "etto", "🍖")
R(r"mortadella", "Mortadella", SALUMI, "etto", "🥓")
R(r"piccante|nduja|^salame piccante", "Salame piccante", SALUMI, "etto", "🌶️", g="Salumi")
R(r"salam|finocchiona|ciauscolo|cacciatore|galbanetto|monetine", "Salame", SALUMI, "etto", "🥓", g="Salumi")
R(r"guanciale|pancetta|bacon|lardo", "Guanciale e pancetta", SALUMI, "etto", "🥓", g="Salumi")
R(r"^coppa|capocollo", "Coppa e capocollo", SALUMI, "etto", "🥓", g="Salumi")
R(r"lonz|lombetta", "Lonza e lonzino", SALUMI, "etto", "🥓", g="Salumi")
R(r"w[uü]rstel|wudy|kaminwurzerl|servelade|wüberini|wuberini", "Wurstel", CARNE, "kg", "🌭")
R(r"salumi affettati|antipasto calabro|affettati|cubetti di tacchino", "Salumi affettati assortiti", SALUMI, "etto", "🥓")

# ---------------- CARNE ----------------
R(r"macinato di suino|macinato suino", "Macinato di suino", CARNE, "kg", g="Carne")
R(r"braciol|fettine di collo", "Braciole di suino", CARNE, "kg", g="Carne")
R(r"salsicc", "Salsiccia di suino", CARNE, "kg", g="Carne")
R(r"hamburger di (pollo|tacchino)", "Hamburger di pollo e tacchino", CARNE, "kg")
R(r"^(?!.*vegetal)(cotolett|cordon bleu|spinacine|nuggets di pollo|bon roll|bastoncini di pollo|chicken nuggets)", "Cotolette e panati di pollo", CARNE, "kg")
R(r"petto di pollo", "Petto di pollo a fette", CARNE, "kg")
R(r"fusi di pollo|cosciotto di pollo|quarto posteriore|pollo in parti|cosce di pollo", "Cosce e fusi di pollo", CARNE, "kg")
R(r"fettine.*vitell", "Fettine di vitello", CARNE, "kg")
R(r"fesa di tacchino|girello di tacchino|arrosto di tacchino", "Fesa di tacchino a fette", CARNE, "kg")
R(r"^arista di suino|lombo di suino|fettine di lombo|sottilissime di lombo", "Arista e lombo di suino", CARNE, "kg", g="Carne")
R(r"filetto di suino|filetto suino", "Filetto di suino", CARNE, "kg", g="Carne")

# ---------------- PESCE ----------------
R(r"salmone.*(affumicat|marinat)|affumicato.*salmone|carpaccio di salmone", "Salmone affumicato", PESCE, "kg")
R(r"^(?!.*sugo)(gambero|gambere|gamberi|gamberett|mazzancoll|gamberoni)", "Gamberi e mazzancolle", PESCE, "kg")
R(r"calamar|totan|seppiolin|seppi", "Calamari e totani", PESCE, "kg")
R(r"filetti di merluzzo", "Filetti di merluzzo", PESCE, "kg")
R(r"bastoncini di merluzzo|croccole|croccanti di merluzzo", "Bastoncini e croccanti di pesce", SURG, "kg", "🐟")
R(r"sgombro", "Filetti di sgombro", PESCE, "kg")
R(r"alici|acciughe", "Alici e acciughe", PESCE, "kg")
R(r"tonno (extragusto|in olio|all.olio)|filetti di tonno|tonno in scatola|tonno mareblu|tonno (rizzoli|as do|al naturale|filo|in pezzi)|tranci di tonno|insalata di tonno", "Tonno in scatola", PASTA, "kg", "🐟")
R(r"tartare di tonno", "Tartare di tonno", PESCE, "kg")

# ---------------- FRUTTA E VERDURA ----------------
R(r"^mel[ae] ", "Mele", FRUTTA, "kg", "🍎", g="Frutta")
R(r"^uva", "Uva", FRUTTA, "kg", "🍇", g="Frutta")
R(r"^zucca(?! halloween)|fiori di zucca", "Zucca", FRUTTA, "kg", "🎃")
R(r"^patate", "Patate", FRUTTA, "kg", "🥔")
R(r"^carot", "Carote", FRUTTA, "kg", "🥕")
R(r"^insalata|cicorino|misticanza|lattughino|songino", "Insalata", FRUTTA, "kg", "🥬", g="Frutta")
R(r"^limoni", "Limoni", FRUTTA, "kg", "🍋")
R(r"^banane", "Banane", FRUTTA, "kg", "🍌")
R(r"^clementine|mandarin", "Clementine e mandarini", FRUTTA, "kg", "🍊")
R(r"^funghi (champignon|misti)", "Funghi champignon", FRUTTA, "kg", "🍄")
R(r"^noci\b", "Noci", FRUTTA, "kg", "🥜")
R(r"anacard", "Anacardi", FRUTTA, "kg", "🥜", g="Col|Frutta|Pasta")
R(r"arachidi", "Arachidi", FRUTTA, "kg", "🥜", g="Col")
R(r"^nocciole", "Nocciole", FRUTTA, "kg", "🌰", g="Col|Frutta|Pasta")
R(r"pistacch", "Pistacchi", FRUTTA, "kg", "🥜", g="Col|Frutta|Pasta")
R(r"frutta secca|mix trio|crio mix|mix di frutta secca|semi di chia", "Frutta secca mista", FRUTTA, "kg", "🥜")
R(r"datter", "Datteri", FRUTTA, "kg", "🌴", g="Col")
R(r"avocado", "Avocado", FRUTTA, "kg", "🥑")
R(r"^(?!.*(spinaciotto|spinacine))spinaci", "Spinaci", FRUTTA, "kg", "🥬", g="Sur")
R(r"minestrone|contorno|tris mediterraneo|verdurì|rosette|piselli|^fave|prezzemolo|cicoria|verdure surgelate", "Verdure surgelate", SURG, "kg", "🥦", g="Sur")
R(r"zuppe|virtù di zuppa|zuppa pronta", "Zuppe surgelate", SURG, "kg", "🍲", g="Sur")
R(r"^patatine", "Patatine surgelate", SURG, "kg", "🍟", g="Sur")
R(r"gelato|coni gelato|sorbett|biscotti gelato|mochi|gelati|coni miniature|magnum", "Gelati e sorbetti", SURG, "kg", "🍦", g="Sur")
R(r"^pizz(a |ette)", "Pizza surgelata", SURG, "kg", "🍕")

# ---------------- PASTA, OLIO, CONSERVE ----------------
R(r"pasta di semola|pasta integrale|^pasta di|pasta senza glutine|pasta kamut|pasta di legumi|pasta legumi|pasta high protein|pasta biologica", "Pasta di semola", PASTA, "kg", "🍝")
R(r"pasta all.uovo|fettuccine|tagliatelle all|lasagne all.uovo|emiliane", "Pasta all'uovo", PASTA, "kg", "🍝")
R(r"cappelletti|pasta fresca|ripiena|ravioli|tortellini|pappardelle|trofiette|orecchiettine|passatelli", "Pasta fresca", PASTA, "kg", "🍝")
R(r"gnocch|chicche", "Gnocchi", PASTA, "kg", "🥔")
R(r"lasagn|cannelloni", "Lasagne e cannelloni pronti", PASTA, "kg", "🍝")
R(r"^riso(?!tto| soffiato)", "Riso", PASTA, "kg", "🍚", g="Pasta")
R(r"passata|polpa di pomodoro|polpa datterini|pelati|pomodorini|san marzano|datterini|concentrato", "Passata di pomodoro", PASTA, "kg", "🍅")
R(r"^(sugo|sughi|gran sugo)|il mio gran rag", "Sugo pronto", PASTA, "kg", "🍅")
R(r"^pesto", "Pesto", PASTA, "kg", "🌿")
R(r"extra ?vergine", "Olio extravergine di oliva", PASTA, "l", "🫒")
R(r"^olio di oliva", "Olio di oliva", PASTA, "l", "🫒")
R(r"fagioli in scatola|ceci e fagioli|legumi in vaso|lenticchie a vapore|legumi lessati|fagioli alla|ceci|(?<!pasta e )fagioli|cannellini|legumi cotti|legumi bio|legumi al naturale", "Legumi in scatola e vaso", PASTA, "kg", "🫘")
R(r"lenticchie di|^ceci italia|fagioli borlotti", "Legumi secchi", PASTA, "kg", "🫘")
R(r"^olive", "Olive", PASTA, "kg", "🫒")
R(r"carciof", "Carciofini sott'olio", PASTA, "kg", "🥫", g="Pasta")
R(r"capper", "Capperi", PASTA, "kg", "🥫")
R(r"maionese|ketchup|senape|besciamella|salsa (rosa|bbq)|salsa develey|^salsa|salsa tartufata|glassa|cetrioli", "Maionese, ketchup e salse", PASTA, "l", "🥫", vol=True)
R(r"brodo", "Brodo", PASTA, "l", "🥫", vol=True)
R(r"aceto|acetaia|condimento.*balsamico", "Aceto balsamico", PASTA, "l", "🥫")
R(r"crauti|cavolo rosso", "Crauti e cavolo rosso", PASTA, "kg", "🥫")
R(r"^farina", "Farina", PASTA, "kg", "🌾")

# ---------------- COLAZIONE E DOLCI ----------------
R(r"halloween|scary box|ghost is|zucca trolli|monster|horror|occhi mallow|ciocozucca|teschio|candy box|zucca porta", "Dolciumi Halloween", COLAZ, "kg", "🎃", g="Col")
R(r"fette biscottate|fette tostate", "Fette biscottate", COLAZ, "kg", "🍞")
R(r"chocowafer|choco wafer|kinder|kit ?kat|twix|\bmars\b|novipiù|happy snack|snack al cioccolato|snack cioccolato|loacker|m&m|mikado", "Snack al cioccolato", COLAZ, "kg", "🍫", g="Col")
R(r"merendin|buondì|girella|yo-yo|nastrine|^la merenda|plum cake|kinder delice|tortino|^tortine|torte in festa|pan di stelle|^merende|merendina|plumcake|merenda con|mini fette|fiesta|crostatine|brioss", "Merendine", COLAZ, "kg", "🥐", g="Col")
R(r"^torta|ciambellone|sbrisolona|rollé|brownies|pasticciotto|crostat", "Torte e dolci da forno", COLAZ, "kg", "🍰", g="Col")
R(r"biscott|frollini|cantuccini|pavesini|oro ciok|oswego|alveari|tortini al farro|cookies|pastafrolla|saiwa|bucaneve|krumiri|baiocchi|novellini", "Biscotti", COLAZ, "kg", "🍪", g="Col")
R(r"wafer", "Wafer", COLAZ, "kg", "🍫", g="Col")
R(r"pane in cassetta|gran carré|pan brioche a fette|pan carré|pan bauletto|pane bauletto|pane caserecio|focaccine|panini per hamburger", "Pane in cassetta", COLAZ, "kg", "🍞", g="Col|Altro")
R(r"croissant|cornetto|pain chocolat|donut|cornetti|brioche|pains au", "Croissant e brioche", COLAZ, "kg", "🥐", g="Col")
R(r"pinsa", "Pinsa", COLAZ, "kg", "🍕", g="Col|Altro")
R(r"piadin|piadelle", "Piadina", COLAZ, "kg", "🫓")
R(r"cereali|muesli|granola|fiocchi di avena|farro soffiato|corn flakes|coco pops|fiocchi di riso", "Cereali e muesli", COLAZ, "kg", "🥣", g="Col")
R(r"barrett", "Barrette di cereali e proteiche", COLAZ, "kg", "🍫", g="Col")
R(r"gallette", "Gallette", COLAZ, "kg", "🍘", g="Col|Altro")
R(r"^crackers|cracker", "Crackers", COLAZ, "kg", "🍘", g="Col|Altro")
R(r"grissini|sfoglie di pane", "Grissini", COLAZ, "kg", "🥖", g="Col|Altro")
R(r"tarall", "Taralli", COLAZ, "kg", "🥨", g="Col|Altro")
R(r"^patatine", "Patatine", COLAZ, "kg", "🍟", g="Col|Altro")
R(r"snack (di )?mais|snack triangolini|corn cone|pop corn|chips di verdure|fonzies|mix di salatini|snack&vai|coni gusto nacho|leggerine|petali snack|bake rolls|ghiottina|sfogline|fonzies|nacho|sticks|salatini|ortaggi croccanti|chips|snack conad|snack mais|snack di patate|snick snack|sfogliatine", "Snack salati", COLAZ, "kg", "🍿", g="Col|Altro")
R(r"fondente|excellence", "Cioccolato fondente", COLAZ, "kg", "🍫", g="Col")
R(r"cioccolato al latte|tavoletta di cioccolato bianco|milkinis", "Cioccolato al latte", COLAZ, "kg", "🍫", g="Col")
R(r"cioccolatini|praline|baci|bijou|raffaello|lindor|rondò|pralinate|monete di cioccolato|cremini|rovelli|boeri|raffaello|novi gran selezione", "Cioccolatini e praline", COLAZ, "kg", "🍫", g="Col")
R(r"panettone|pandoro|panettoncino|pandorino|pane dei morti|pan speziato", "Panettone e pandoro", COLAZ, "kg", "🎄", g="Col")
R(r"torron", "Torrone", COLAZ, "kg", "🍬", g="Col")
R(r"caramelle|haribo|fruit-tella|gelées|big frut|chupa|big babol|skittles|marshmallows|mallows|candy pocket|trolli|vampiri|toffee|pop eye|lecca", "Caramelle e gommose", COLAZ, "kg", "🍬", g="Col")
R(r"^crema (alla nocciola|spalmabile)|nocciolata", "Crema alla nocciola", COLAZ, "kg", "🍫", g="Col")
R(r"confettura|composta", "Confettura", COLAZ, "kg", "🍓", g="Col")
R(r"^miele", "Miele", COLAZ, "kg", "🍯")
R(r"caffè in grani", "Caffè in grani", COLAZ, "kg", "☕")
R(r"caffè solubile|orzo|cappuccino|preparato solubile|ginseng|camomilla solubile", "Caffè solubile", COLAZ, "kg", "☕")
R(r"cialde|capsule|caffè in capsule|caffè in cialde", "Cialde caffè", COLAZ, "cialda", "☕")
R(r"caffè macinato|caffè arabica|macinato cremoso|aroma italiano|caffè intermezzo|caffè espresso|espresso bar|qualità espresso|caffè qualità|borbone|miscela", "Caffè macinato", COLAZ, "kg", "☕")
R(r"^(tè|thè)\b|tisana|infusi|^tisane", "Tè e tisane", COLAZ, "pezzo", "🍵", g="Col")

# ---------------- CASA E PULIZIA ----------------
R(r"carta igienica", "Carta igienica", ALTRO, "rotolo", "🧻", "Casa & pulizia")
R(r"asciugatutto|bobina|carta casa|blitz|carta da cucina", "Asciugatutto", ALTRO, "rotolo", "🧻", "Casa & pulizia")
R(r"detersivo (lavatrice|liquido|per capi)|dash|dual power|cicli brevi", "Detersivo lavatrice", ALTRO, "l", "🧺", "Casa & pulizia")
R(r"detersivo (lavatrice|liquido|per capi)|dash|dual power|cicli brevi", "Detersivo lavatrice (al lavaggio)", ALTRO, "pezzo", "🧺", "Casa & pulizia")
R(r"ammorbidente|vernel|felce azzurra", "Ammorbidente", ALTRO, "l", "🧺", "Casa & pulizia")
R(r"ammorbidente|vernel|felce azzurra", "Ammorbidente (al lavaggio)", ALTRO, "pezzo", "🧺", "Casa & pulizia")
R(r"detersivo piatti|piatti con spugnetta", "Detersivo piatti", ALTRO, "l", "🍽️", "Casa & pulizia")
R(r"lavastoviglie|finish|\bkop\b|\btabs\b|pastiglie|baleno", "Detersivo lavastoviglie", ALTRO, "pezzo", "🍽️", "Casa & pulizia")
R(r"lavastoviglie|finish|\bkop\b|\btabs\b|pastiglie|baleno", "Gel lavastoviglie", ALTRO, "l", "🍽️", "Casa & pulizia")
R(r"gel wc|detergente wc|wc gel", "Gel WC", ALTRO, "l", "🚽", "Casa & pulizia")
R(r"^tovaglioli(?! halloween)", "Tovaglioli", ALTRO, "pezzo", "🧻", "Casa & pulizia")
R(r"candeggina", "Candeggina", ALTRO, "l", "🧴", "Casa & pulizia")
R(r"detergente spray|sgrassatore|spray (vetri|bagno|pulizia)|\bcif\b|chanteclair|valido|quasar|amuchina|pronto 5|mr\. muscle|mr muscle|citrosil|viakal|infinite|detergente emulsio", "Detergente spray", ALTRO, "l", "🧴", "Casa & pulizia")
R(r"detergente (per )?pavimenti|\brio\b|detersivo igienizzante pavimenti|detersivo pavimenti|lavaincera|ravviva|mangiapolvere", "Detergente pavimenti", ALTRO, "l", "🧴", "Casa & pulizia")
R(r"anticalcare|calgon", "Anticalcare", ALTRO, "l", "🧴", "Casa & pulizia")
R(r"^sacch|sacco immondizia|pattumiera|condominiali", "Sacchi immondizia", ALTRO, "pezzo", "🗑️", "Casa & pulizia")
R(r"cattura ?polvere|catturapolvere|duster", "Panni cattura polvere", ALTRO, "pezzo", "🧹", "Casa & pulizia")
R(r"acchiappacolore|assorbicolori", "Foglietti catturacolore", ALTRO, "pezzo", "🧺", "Casa & pulizia")
R(r"^panni|^panno|spugna|tonkita panni|brilla", "Panni e spugne", ALTRO, "pezzo", "🧽", "Casa & pulizia")
R(r"^fazzoletti|veline", "Fazzoletti", ALTRO, "pezzo", "🤧", "Casa & pulizia")
R(r"profumatore|deodorante per ambienti|ambipur|diffusore|elixir", "Profumatore ambiente e bucato", ALTRO, "pezzo", "🌸", "Casa & pulizia")
R(r"^guanti (universali|in lattice)|smilex", "Guanti per pulizie", ALTRO, "pezzo", "🧤", "Casa & pulizia")
R(r"pellicola|alluminio|carta forno", "Pellicola, alluminio e carta forno", ALTRO, "pezzo", "🧻", "Casa & pulizia")

# ---------------- IGIENE ----------------
R(r"shampoo|balsamo|elvive|linea capelli|pantene", "Shampoo e balsamo", ALTRO, "l", "🧴", "Igiene & persona", g="Altro")
R(r"maschera (capelli|elvive)|^maschera$", "Maschera capelli", ALTRO, "l", "🧴", "Igiene & persona")
R(r"bagno ?schiuma|bagnodoccia|docciaschiuma|\bdoccia\b", "Bagnoschiuma", ALTRO, "l", "🧴", "Igiene & persona")
R(r"dentifricio", "Dentifricio", ALTRO, "l", "🪥", "Igiene & persona")
R(r"collutorio", "Collutorio", ALTRO, "l", "🪥", "Igiene & persona")
R(r"^(?!.*(elettric|testine|ricariche))(spazzolin)", "Spazzolino da denti", ALTRO, "pezzo", "🪥", "Igiene & persona")
R(r"^deodorante(?! per ambienti)", "Deodorante", ALTRO, "l", "🧴", "Igiene & persona")
R(r"sapone|saponetta", "Sapone", ALTRO, "l", "🧼", "Igiene & persona")
R(r"salviett(e|ine) (intime|igiene intima)", "Salviettine intime", ALTRO, "pezzo", "🧴", "Igiene & persona")
R(r"detergente intimo", "Detergente intimo", ALTRO, "l", "🧴", "Igiene & persona")
R(r"crema viso|revitalift|q10|svr|hyalu", "Crema viso", ALTRO, "l", "🧴", "Igiene & persona")
R(r"crema mani|cream corpo|equilibra|scrub corpo|crema corpo|glysolid", "Crema mani e corpo", ALTRO, "l", "🧴", "Igiene & persona")
R(r"colorazione", "Colorazione capelli", ALTRO, "pezzo", "💇", "Igiene & persona")
R(r"assorbenti|proteggi slip|salvaslip|mutandina mestruale", "Assorbenti", ALTRO, "pezzo", "🧴", "Igiene & persona")
R(r"pannolini", "Pannolini", ALTRO, "pezzo", "👶", "Igiene & persona")

# ---------------- ANIMALI ----------------
R(r"crocchette per cani|crocchette cane|crocchette.*cani|crocchette per cane", "Crocchette per cane", ALTRO, "kg", "🐕", "Animali")
R(r"crocchette.*gatt|croccantini.*gatt|lechat|alimento per gatti", "Crocchette per gatto", ALTRO, "kg", "🐈", "Animali")
R(r"bocconcini per cani|umido per cane|patè per cani|patè per cane|petfriends conad|bocconcini in (salsa|lattina) per cani", "Umido per cane", ALTRO, "kg", "🐕", "Animali")
R(r"umido per gatt|cibo umido per gatt|mousse (gatto|revelations)|mousse.*gourmet|sheba|gourmet|vitakraft|poésie|bocconcini gatto|filets|bocconcini in (salsa|lattina) per gatti", "Umido per gatto", ALTRO, "kg", "🐈", "Animali")
R(r"snack (per )?cani|snack cane|biscotti per cani|dentalife", "Snack per cani", ALTRO, "kg", "🐕", "Animali")
R(r"catsticks|snack per gatti", "Snack per gatti", ALTRO, "kg", "🐈", "Animali")
R(r"lettiera", "Lettiera per gatti", ALTRO, "l", "🐈", "Animali")

# ---------------- ABBIGLIAMENTO, PIANTE, CASA, FAI DA TE ----------------
R(r"pantofol|ciabatt", "Pantofole e ciabatte", ALTRO, "pezzo", "🥿", "Abbigliamento & tessile", g="Altro")
R(r"calze neve|calze da neve", "Calze da neve per auto", ALTRO, "pezzo", "❄️", "Fai da te & utensili")
R(r"calze|calzini|gambaletto|collant", "Calze", ALTRO, "pezzo", "🧦", "Abbigliamento & tessile", g="Altro")
R(r"pigiama", "Pigiama", ALTRO, "pezzo", "👕", "Abbigliamento & tessile")
R(r"scarpa.*antinfortunistica", "Scarpe antinfortunistiche", ALTRO, "pezzo", "👞", "Fai da te & utensili")
R(r"(giubbino|giacca).*uomo|uomo.*(giubbino|giacca)", "Giubbino e giacca da uomo", ALTRO, "pezzo", "🧥", "Abbigliamento & tessile")
R(r"(giubbino|giacca).*donna|donna.*(giubbino|giacca)", "Giubbino e giacca da donna", ALTRO, "pezzo", "🧥", "Abbigliamento & tessile")
R(r"crisantemi", "Crisantemi", ALTRO, "pezzo", "🌼", "Giardino & piante")
R(r"piante verdi|dracaena|bromelia|succulent|echeveria|aromi misti", "Piante verdi in vaso", ALTRO, "pezzo", "🪴", "Giardino & piante")
R(r"termoventilatore", "Termoventilatore", ALTRO, "pezzo", "🔥", "Elettronica")
R(r"friggitrice", "Friggitrice ad aria", ALTRO, "pezzo", "🍟", "Elettronica")
R(r"^trapano", "Trapano", ALTRO, "pezzo", "🔧", "Fai da te & utensili")
R(r"set .*cacciaviti", "Set cacciaviti", ALTRO, "pezzo", "🔧", "Fai da te & utensili")
R(r"scaffale", "Scaffale", ALTRO, "pezzo", "🗄️", "Casalinghi & bazar")
R(r"scala 3 gradini|sgabello", "Scala a 3 gradini", ALTRO, "pezzo", "🪜", "Fai da te & utensili")
R(r"stendibiancheria", "Stendibiancheria", ALTRO, "pezzo", "🧺", "Casalinghi & bazar")
R(r"candela profumata", "Candela profumata", ALTRO, "pezzo", "🕯️", "Casalinghi & bazar")
R(r"catena lumin|tenda luminosa|catena luci", "Catena luminosa LED", ALTRO, "pezzo", "💡", "Casalinghi & bazar")
R(r"calendario dell.avvento", "Calendario dell'Avvento", ALTRO, "pezzo", "🎄", "Casalinghi & bazar")
R(r"^padella", "Padella", ALTRO, "pezzo", "🍳", "Casalinghi & bazar")
R(r"plaid", "Plaid", ALTRO, "pezzo", "🛋️", "Casalinghi & bazar")
R(r"contenitori in plastica", "Contenitori in plastica", ALTRO, "pezzo", "📦", "Casalinghi & bazar")
R(r"ombrello", "Ombrello mini automatico", ALTRO, "pezzo", "☂️", "Casalinghi & bazar")

# ---------------- ALTRE FAMIGLIE (carne, pesce, frutta, pronti) ----------------
R(r"funghi porcini|porcini", "Funghi porcini", SURG, "kg", "🍄")
R(r"cozze|vongole|ostriche|polpo|frutti di mare|misto mare|insalata di mare|antipasto di mare|lupini", "Molluschi e frutti di mare", PESCE, "kg", "🦪", g="Pesce")
R(r"poké|poke|sushi", "Poké e sushi", PESCE, "kg", "🍣")
R(r"trota|pesce spada|merluzzo|baccalà|platessa|medaglioni di salmone|salmone in pasta|surimi|cuori di merluzzo|filetto di|tonno fresco", "Altro pesce", PESCE, "kg", "🐟", g="Pesce")
R(r"ali di pollo|bombette|straccetti di pollo|tagliata di pollo|birbe|rollè di pollo|pollo alla diavola|coscia di tacchino|pulled pork|nuggets|pulled chicken|bistecchine di pollo|filetti di pollo|cuoripieni|buona domenica|bocconcini di pollo|alette|polpette|bocconcini panati|panati", "Pollo e tacchino (altri tagli)", CARNE, "kg", "🍗", g="Carne")
R(r"suino|maiale|stincotto|stinco", "Suino (altri tagli)", CARNE, "kg", "🥩", g="Carne")
R(r"bovino|scottona|vitella|vitellone|manzo|trippa|fracosta|ossobuco|spezzatino|vitello", "Bovino (tagli vari)", CARNE, "kg", "🥩", g="Carne")
R(r"mango|ananas|melagrana|patate dolci|polpa di avocado|frutta in pezzi|frutti di bosco", "Frutta fresca varia", FRUTTA, "kg", "🍍", g="Frutta")
R(r"cavolfiore|cetrioli|cipolle|aglio|finocch|radicchio|iceberg|cipolla|ortaggi|spinaci", "Verdure fresche varie", FRUTTA, "kg", "🥬", g="Frutta")
R(r"fichi secchi|prugne secche|semi di zucca|goji|disidratata|crioessiccata|squeeze di frutta|frutta ricoperta|prugne denocciolate|semi di chia", "Frutta secca e disidratata", COLAZ, "kg", "🥜", g="Col|Frutta|Pasta")
R(r"gocce di cioccolato|decorazioni|glassa|preparato (ideale|per)|vaniglia|canditi|sciroppo d.acero|lievito|condensato|aroma naturale|zucchero|cannella|noce di cocco", "Ingredienti per dolci", COLAZ, "kg", "🧁", g="Col")
R(r"pan di segale|pane fresco|panini al latte|panini hamburger|puccia|pagnottelle|panfiocco|cuor di lino|pane kamut|pane per hamburger|stagnati", "Pane e panini", COLAZ, "kg", "🍞", g="Col|Altro")
R(r"pancakes", "Pancake", COLAZ, "kg", "🥞")
R(r"ovetti|palmine|nesquik|mellows|tartellette|frullato di frutta", "Dolci e snack vari", COLAZ, "kg", "🍬", g="Col")
R(r"burrata|burratina|mascarpone|fiocchi di latte|tzatziki|mousse proteica|boscatella|stracciatella|fiocchi cremosi|jocca", "Formaggi freschi e latticini vari", LATTE, "kg", "🧀")
R(r"speck", "Speck", SALUMI, "etto", "🥓")
R(r"arista arrosto|vitel tonn|snack la merenda|salsiccia dolce in cubetti|fesa di manzo cotta|teneroni|abc della merenda", "Salumi e arrosti affettati vari", SALUMI, "kg", "🥓", g="Salumi|Carne")
R(r"risotto|cous cous|piatto fatto|pizzoccheri|spatzle|pasta e fagioli|crespelle|melanzane alla parmigiana|torta ricotta|torta salata|cicora|mais in scatola|carne in gelatina|pastina|crockburger|farro|pallotte|patè ai funghi|cuor di brodo|cotti al vapore|air-fry|mix 5 cereali|legumi e cereali|purè|chicche", "Piatti pronti e cereali", PASTA, "kg", "🍲", g="Pasta|Surg")
R(r"panzerotti|medaglioni al formaggio|panciottini|rösti|strudel|suppli|pizzarollo|falafel|coccole bonduelle|spaghetti alle vongole|polpo e patate|spinaciotto|muffin|mirtilli|frozen yogurt|dessert a forma|misto di funghi|code di mazzancolle|cordon bleu|crocchette|versilfood", "Piatti pronti e dolci surgelati", SURG, "kg", "🧊", g="Surg")

# ---------------- NUOVE FAMIGLIE (rilettura Conad) ----------------
R(r"caffè latte|latte e cacao|nesquik|latte macchiato|coffe to go|latte al cioccolato|latte con cioccolato", "Latte aromatizzato e caffè latte", LATTE, "l", "🥛", vol=True)
R(r"mousse|dessert|danette|fruttolo|budino", "Dessert e mousse al latte", LATTE, "kg", "🍮")
R(r"formaggini|formaggino", "Formaggini", SALUMI, "kg", "🧀")
R(r"bresaola", "Bresaola", SALUMI, "etto", "🥓")
R(r"stinco", "Suino (altri tagli)", CARNE, "kg", "🥩")
R(r"macinato", "Macinato misto", CARNE, "kg", "🥩", g="Carne")
R(r"hamburger", "Hamburger", CARNE, "kg", "🍔", g="Carne")
R(r"spigol|orata|branzino|ombrina|ricciola", "Spigola e orata", PESCE, "kg", "🐟", g="Pesce")
R(r"salmone", "Salmone fresco", PESCE, "kg", "🐟", g="Pesce")
R(r"^pere", "Pere", FRUTTA, "kg", "🍐", g="Frutta")
R(r"kiwi", "Kiwi", FRUTTA, "kg", "🥝", g="Frutta")
R(r"^aranc", "Arance", FRUTTA, "kg", "🍊", g="Frutta")
R(r"cachi", "Cachi", FRUTTA, "kg", "🍑", g="Frutta")
R(r"castagne|marroni", "Castagne e marroni", FRUTTA, "kg", "🌰", g="Frutta")
R(r"mandorle", "Mandorle", FRUTTA, "kg", "🥜", g="Col|Frutta|Pasta")
R(r"pouch|frullati|le fruttine|snack verso natura|frullato|fruttini|plasmon", "Snack e pouch di frutta", FRUTTA, "kg", "🍓", g="Frutta")
R(r"zucchin", "Zucchine", FRUTTA, "kg", "🥒", g="Frutta")
R(r"broccol|cime di rapa|friarielli|cicoria|bietol|erbette", "Broccoli e verdure a foglia", FRUTTA, "kg", "🥦", g="Frutta")
R(r"pomodor", "Pomodori freschi", FRUTTA, "kg", "🍅", g="Frutta")
R(r"broccoli|friarielli|campagnole|cime di rapa|fagiolini|asparagi|biete|erbette|zucca a cubetti|vellutata|primavera", "Verdure surgelate", SURG, "kg", "🥦", g="Sur")
R(r"hamburger|burger vegetale|crocchette vegetali", "Hamburger e burger surgelati", SURG, "kg", "🍔", g="Sur")
R(r"filett|branzino|orata|cuori di filetto", "Filetti di pesce surgelati", SURG, "kg", "🐟", g="Sur")
R(r"findus|gratinati|chicken pops|4 fiori|sofficini|preparati di pollo|panati di merluzzo|piatti pronti di pesce|spaghettata|aperisfizi|focaccine|impasto per pizza|pizza la saporita", "Piatti pronti surgelati", SURG, "kg", "🧊", g="Sur")
R(r"tiramis|profiteroles|saint honor", "Dolci surgelati", SURG, "kg", "🍰", g="Sur")
R(r"olio di semi|olio per fritt|frì max|friol|viviamo", "Olio di semi", PASTA, "l", "🫒")
R(r"pesche|sciroppo|cetrioli|lupini|funghi trifolati|zucca alla brace|piselli|ortaggi|tahina", "Conserve di verdura e frutta", PASTA, "kg", "🥫", g="Pasta")
R(r"sfoglia|base fresca|brisée|impasto", "Pasta sfoglia e basi", PASTA, "kg", "🥧")
R(r"zuppa|zuppe e creme|zuppe|vellutata|saikebon|noodles", "Zuppe pronte e noodles", PASTA, "pezzo", "🍜", g="Pasta|Altro")
R(r"dado|aromat|insaporitore|zafferano", "Dadi e insaporitori", PASTA, "kg", "🧂", g="Pasta|Altro")
R(r"cacao|ciobar|cioccolata in polvere", "Cacao e cioccolata in polvere", COLAZ, "kg", "🍫", g="Col")
R(r"tavolett|lastrine|cioccolato", "Tavolette di cioccolato", COLAZ, "kg", "🍫", g="Col")
R(r"burger|tofu|tempeh|seitan|affettato vegetale|sogno veg|kioene|piatti vegetali|cotolette vegetali|tortini", "Burger e alternative vegetali", ALIM, "kg", "🌱")
R(r"omogeneizz", "Omogeneizzati", ALIM, "kg", "👶")
R(r"salviett.*(disinfett|igieniz|milleusi)|milleusi", "Salviette igienizzanti per casa", ALTRO, "pezzo", "🧻", "Casa & pulizia")
R(r"additivo|smacchiator|difendi colore|napisan|vanish|cura lavatrice|anticalcare lavatrice|pastiglie anticalcare|palline magnetiche|calgon", "Additivi e smacchiatori lavatrice", ALTRO, "pezzo", "🧺", "Casa & pulizia")
R(r"secchio|mocio|\bmop\b|scopa|set pulizia pavimenti", "Secchio, mocio e scope", ALTRO, "pezzo", "🧹", "Casa & pulizia")
R(r"(spazzolin|testine|ricariche).*(elettric|oral-b|dentalvis)|elettrico", "Spazzolino elettrico e testine", ALTRO, "pezzo", "🪥", "Igiene & persona")
R(r"dentalvis|blanx|dentiere|forcelle", "Accessori igiene orale", ALTRO, "pezzo", "🪥", "Igiene & persona")
R(r"rasoio|radi\s*&\s*getta|radi e getta|ricariche gillette|ricariche per rasoio|rasoi|lamette", "Rasoi", ALTRO, "pezzo", "🪒", "Igiene & persona")
R(r"salviett|struccanti|umidificate|bastoncini cotonati", "Salviettine e bastoncini", ALTRO, "pezzo", "🧴", "Igiene & persona")
R(r"barba|nivea men|noxzema", "Prodotti per la barba", ALTRO, "pezzo", "🧴", "Igiene & persona")
R(r"borotalco|bagno ", "Bagnoschiuma", ALTRO, "l", "🧴", "Igiene & persona")
R(r"cuccia|cuscino (rettangolare|ovale) per animali|divano per animali|lettino per gatti|set cuccia", "Cucce e cuscini per animali", ALTRO, "pezzo", "🛏️", "Animali")
R(r"ciotol|giocattolo per animali|salviette per animali|riso soffiato per animali", "Ciotole e accessori per animali", ALTRO, "pezzo", "🦴", "Animali")
R(r"tappetini igienici", "Tappetini igienici", ALTRO, "pezzo", "🐕", "Animali")
R(r"massagg|shiatsu|pistola|tens\b|inalatore|pressione|pesapersone|venoso|kinesiologico|cuscino girevole|sedile per massaggio", "Apparecchi per massaggio e benessere", ALTRO, "pezzo", "💆", "Salute & benessere")
R(r"voltaren|moment|bronchenolo|vitamine e minerali|vitamine|multivitamin|integrator", "Farmaci e integratori", ALTRO, "pezzo", "💊", "Salute & benessere")
R(r"pile alcalin|pile stilo|stilo o ministilo|pile ministilo|pila transistor|pile e batterie", "Pile e batterie", ALTRO, "pezzo", "🔋", "Elettronica")
R(r"giubbino|\bpile\b|softshell|soft shell|gilet|micropile", "Giubbini e pile", ALTRO, "pezzo", "🧥", "Abbigliamento & tessile")
R(r"maglia|maglione|felpa|cardigan|dolcevita|lupetto|camicia", "Maglie e felpe", ALTRO, "pezzo", "👕", "Abbigliamento & tessile")
R(r"pantalon|jeans|jeggings|joggers|leggings|^tuta", "Pantaloni e tute", ALTRO, "pezzo", "👖", "Abbigliamento & tessile")
R(r"boxer|slip |intimo", "Intimo", ALTRO, "pezzo", "🩲", "Abbigliamento & tessile")
R(r"berretto|cappell|scaldacollo|sciarpa", "Cappelli e sciarpe", ALTRO, "pezzo", "🧢", "Abbigliamento & tessile")
R(r"scarpa|scarpe|anfibio|stivaletto", "Scarpe", ALTRO, "pezzo", "👟", "Abbigliamento & tessile")
R(r"completo letto|parure|copripiumino|trapunta|coperta|guanciale|topper|federe|linea letto|accappatoio", "Biancheria letto e bagno", ALTRO, "pezzo", "🛏️", "Abbigliamento & tessile")
R(r"costumi halloween", "Costumi Halloween", ALTRO, "pezzo", "🎃", "Giocattoli")
R(r"tovaglia|canovaccio", "Tovaglie e canovacci", ALTRO, "pezzo", "🍽️", "Casalinghi & bazar")
R(r"natalizi|albero di natale|schiaccianoci|gnomo|palline|decorazione led|lampada decorativa|tazza di natale", "Decorazioni natalizie", ALTRO, "pezzo", "🎄", "Casalinghi & bazar")
R(r"halloween|zucca di plastica|ready fluo|porta scherzetti|portadolcetti|zucca porta", "Articoli Halloween", ALTRO, "pezzo", "🎃", "Casalinghi & bazar")
R(r"\bcero|\bceri|lumino", "Ceri e lumini votivi", ALTRO, "pezzo", "🕯️", "Casalinghi & bazar")
R(r"contenitor|organizer|scatola|scatole|custodi|box sottoletto|pouf|portabiancheria|cesta|sottovuoto|divisori|appendiabiti|grucce|stender|cassettiera", "Contenitori e organizer", ALTRO, "pezzo", "📦", "Casalinghi & bazar")
R(r"armadio|scarpiera|mobile|tavolo pieghevole", "Armadi e mobili", ALTRO, "pezzo", "🗄️", "Casalinghi & bazar")
R(r"stendino|asse da stiro|teli da stiro", "Stendini e assi da stiro", ALTRO, "pezzo", "🧺", "Casalinghi & bazar")
R(r"casseruola|rostiera|coperchio|stampo|stampi|set padelle|tagliapizza|pinza|coltello|tagliacastagne|caffettiera|spray staccante", "Pentole e utensili da cucina", ALTRO, "pezzo", "🍳", "Casalinghi & bazar")
R(r"piatti.*(bio|biodegr)|bicchieri bio|biotable|bibo", "Piatti e bicchieri biodegradabili", ALTRO, "pezzo", "🍽️", "Casalinghi & bazar")
R(r"mollette", "Mollette", ALTRO, "pezzo", "🧺", "Casalinghi & bazar")
R(r"accendigas|accendini", "Accendini", ALTRO, "pezzo", "🔥", "Casalinghi & bazar")
R(r"bottiglia termica|tazza mickey", "Bottiglie e tazze", ALTRO, "pezzo", "🥤", "Casalinghi & bazar")
R(r"ferro (da stiro|a vapore|a caldaia)|stiratore", "Ferro da stiro", ALTRO, "pezzo", "👔", "Elettronica")
R(r"^lavatrice", "Lavatrice", ALTRO, "pezzo", "🧺", "Elettronica")
R(r"^asciugatrice", "Asciugatrice", ALTRO, "pezzo", "🧺", "Elettronica")
R(r"\btv\b", "Smart TV", ALTRO, "pezzo", "📺", "Elettronica")
R(r"^pile |pile alcaline", "Pile", ALTRO, "pezzo", "🔋", "Elettronica")
R(r"lampadin", "Lampadine LED", ALTRO, "pezzo", "💡", "Elettronica")
R(r"stufa", "Stufa", ALTRO, "pezzo", "🔥", "Elettronica")
R(r"aspirapolvere|scopa elettrica|aspiracenere|lavapavimenti|lavatappeti|levapelucchi|battimaterasso", "Aspirapolvere e pulitori elettrici", ALTRO, "pezzo", "🧹", "Elettronica")
R(r"sbattitore|impastatrice|frullatore|bollitore|macinasale", "Piccoli elettrodomestici da cucina", ALTRO, "pezzo", "🍳", "Elettronica")
R(r"giochi? .*legno|in legno|legno per", "Giochi in legno", ALTRO, "pezzo", "🧸", "Giocattoli")
R(r"orchide|phal[ae]", "Orchidee", ALTRO, "pezzo", "🌸", "Giardino & piante")
R(r"ciclamin", "Ciclamini", ALTRO, "pezzo", "🌸", "Giardino & piante")
R(r"piantine|amaryllis|calluna|kalanchoe|giacinti|fiori e composizioni|mix fiorito|crisantem", "Piante fiorite", ALTRO, "pezzo", "🌼", "Giardino & piante")
R(r"martell|chiavi|cacciaviti|flessometro|set 33|porta inserti|cassetta porta attrezzi|trolley kit|box hobby", "Utensili manuali", ALTRO, "pezzo", "🔧", "Fai da te & utensili")
R(r"colla ", "Colle", ALTRO, "pezzo", "🧴", "Fai da te & utensili")
R(r"spray 200|deghiacciante|sblocca|lubrificante|antimuffa", "Spray e prodotti per manutenzione", ALTRO, "pezzo", "🔧", "Fai da te & utensili")
R(r"carrello", "Carrelli", ALTRO, "pezzo", "🛒", "Fai da te & utensili")

# ---------------- NUOVE FAMIGLIE (Elite) ----------------
R(r"formaggio a fette|fettine di formaggio|sottilette|fette extra fondenti", "Formaggio a fette", SALUMI, "kg", "🧀")
R(r"lettiera", "Lettiera per gatti", ALTRO, "pezzo", "🐈", "Animali")
R(r"colorazione", "Colorazione capelli", ALTRO, "pezzo", "💇", "Igiene & persona")
R(r"suppl[iì]|mozzarella in carrozza", "Supplì e mozzarella in carrozza", SURG, "kg", "🧆")
R(r"misto scoglio|frutti di mare|vongole|polpette di merluzzo|cozze", "Frutti di mare e preparati di pesce", SURG, "kg", "🦐", g="Sur")
R(r"^prugne|^susine", "Prugne", FRUTTA, "kg", "🍑", g="Frutta")
R(r"^melanzane", "Melanzane", FRUTTA, "kg", "🍆", g="Frutta")
R(r"^funghi (prataioli|pioppini|cardoncelli|freschi)", "Funghi freschi", FRUTTA, "kg", "🍄", g="Frutta")
R(r"passato di verdure|minestrone|contornissimi|purè fresco", "Passati, minestroni e contorni pronti", FRUTTA, "kg", "🥣", g="Frutta|Pasta")
R(r"^vini? ", "Vino (varie etichette)", BEV, "l", "🍷", g="Bev")

# rinomine di famiglie gia' esistenti (nome vecchio -> nuovo)
RINOMINE = {
    "panna fresca": "Panna",
    "merendine al latte": "Merendine",
    "fagioli in scatola": "Legumi in scatola e vaso",
    "pannolini pampers baby dry": "Pannolini",
    "mele golden": "Mele",
    "whiskey": "Superalcolici",
    "distillato": "Superalcolici",
}


def _classe(u):
    u = (u or "").lower()
    if u in ("kg", "etto"):
        return "m"
    if u == "l":
        return "v"
    if u in CONT:
        return "c"
    return u


def _fattore(da, a, vol):
    """moltiplicatore della quantita' passando dall'unita' 'da' a 'a' (None = impossibile)."""
    if da == a:
        return 1.0
    cd, ca = _classe(da), _classe(a)
    if cd == "c" and ca == "c":
        return 1.0
    if cd == "m" and ca == "m":
        return 0.1 if (da, a) == ("etto", "kg") else 10.0
    if {cd, ca} == {"m", "v"} and vol:
        return {"etto": 0.1}.get(da, 1.0) / ({"etto": 0.1}.get(a, 1.0))
    return None


_QTA = re.compile(r"(?:(\d+)\s*[x×]\s*)?(\d+(?:[.,]\d+)?)\s*(ml|cl|l|lt|litri|g|gr|kg|etto|hg)\b", re.I)
_ALMENO = {"ml": ("v", 0.001), "cl": ("v", 0.01), "l": ("v", 1.0), "lt": ("v", 1.0), "litri": ("v", 1.0),
           "g": ("m", 0.001), "gr": ("m", 0.001), "kg": ("m", 1.0), "etto": ("m", 0.1), "hg": ("m", 0.1)}


def _q_da_descrizione(desc, classe_target, unita_target):
    """Cerca nella descrizione un formato (es. '2 x 75 ml') e lo converte nell'unita' della famiglia."""
    m = _QTA.search(desc or "")
    if not m:
        return None
    mult = int(m.group(1)) if m.group(1) else 1
    cl, fat = _ALMENO[m.group(3).lower()]
    if cl != classe_target:
        return None
    base = mult * float(m.group(2).replace(",", ".")) * fat  # in l o kg
    return base * (10 if unita_target == "etto" else 1)


def normalizza(dati, verbose=False):
    """Accorpa i prodotti per famiglia. Restituisce (prodotti_spostati, prodotti_saltati)."""
    P = dati["prodotti"]
    for p in P:
        p["cat"] = CAT_FIX.get(p["cat"], p["cat"])
        if p["cat"] == "Altro" and p.get("sub") == ALIM:   # Alimentari vari non e' piu' dentro "Altro"
            p["cat"], p["sub"] = ALIM, None
        if p.get("u") == "pz":
            p["u"] = "pezzo"
    for p in P:
        nuovo = RINOMINE.get(p["n"].lower())
        if nuovo and not any(x["n"].lower() == nuovo.lower() for x in P):
            p["n"] = nuovo
    per_nome = {p["n"].lower(): p for p in P}
    prox = max(p["id"] for p in P) + 1
    mappa, fatt, spostati = {}, {}, 0
    for p in sorted(P, key=lambda x: x["id"]):
        nome = p["n"].lower()
        for rx, fam, cat, unita, emo, sub, g, vol in REGOLE:
            if not rx.search(nome):
                continue
            if g and not any(p["cat"].startswith(x) for x in g.split("|")):
                continue
            t = per_nome.get(fam.lower())
            tu = t["u"] if t else unita
            f = _fattore(p["u"], tu, vol)
            if f is None and _classe(tu) == "c" and _classe(p["u"]) in ("m", "v"):
                for o in dati["offerte"]:
                    if o["p"] == p["id"]:
                        o["q"] = 1.0
                f = 1.0
            if f is None:
                ct = _classe(tu)
                offs = [o for o in dati["offerte"] if o["p"] == p["id"]]
                qs = [_q_da_descrizione(o.get("l"), ct, tu) for o in offs] if ct in ("v", "m") else []
                if not qs or any(q is None or q <= 0 for q in qs):
                    continue
                for o, q in zip(offs, qs):
                    o["q"] = round(q, 6)
                f = 1.0
            if not t:
                t = {"id": prox, "e": emo, "n": fam, "cat": cat, "sub": sub, "u": unita}
                prox += 1
                P.append(t)
                per_nome[fam.lower()] = t
            if t["id"] != p["id"]:
                mappa[p["id"]] = t["id"]
                fatt[p["id"]] = f
                spostati += 1
            break
    if mappa:
        for o in dati["offerte"]:
            if o["p"] in mappa:
                f = fatt[o["p"]]
                o["p"] = mappa[o["p"]]
                if f != 1.0:
                    o["q"] = round(o["q"] * f, 6)
    usati = {o["p"] for o in dati["offerte"]}
    dati["prodotti"] = [p for p in P if p["id"] in usati]
    return spostati
