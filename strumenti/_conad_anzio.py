"""Conad Anzio (Spazio Conad, Viale Antium 4) - volantino 10-19 novembre 2026. Zona 'A'.
Uso: python3 strumenti/_conad_anzio.py [percorso offerte.js]   (default sito/offerte.js). Idempotente."""
import os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from strumenti import offerte_lib as L
from PIL import Image

PERC = sys.argv[1] if len(sys.argv) > 1 else "sito/offerte.js"
PDF = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "volantini/lazio/anzio/conad.pdf")
WD = "/tmp/w3/c"
if not os.path.exists(WD + "/p-32.jpg"):
    os.makedirs(WD, exist_ok=True)
    subprocess.run(["pdftoppm", "-jpeg", "-scale-to-x", "2000", "-scale-to-y", "-1", PDF, WD + "/p"], check=True, stderr=subprocess.DEVNULL)

D1, AL, FISSI = "2026-11-10", "2026-11-19", "2026-12-31"
d = L.carica(PERC)
oggi = "2026-11-06"
# rimuove offerte proprie precedenti e le conad zona A scadute
d["offerte"] = [o for o in d["offerte"] if not (o["s"] == "conad" and (
    (o["z"] == "A" and o["dal"] == D1) or (o["z"] == "A" and o["al"] < oggi)))]

def G(n):
    p = L.trova_prodotto(d, n)
    assert p, n
    return p["id"]

BF = " (Bassi e Fissi fino al 31 dicembre 2026)"
# (pag, prodotto, prezzo, q, descrizione, riquadro su griglia 1000px, carta, al)
R = [
# p1
(1,"Latte UHT",4.59,6,"Parmalat Bontà e Linea parz. scremato con vitamina D 1 l x 6",(40,400,325,590),0,AL),
(1,"Biscotti",1.39,0.7,"Balocco vari tipi 700 g (max 6 pezzi)",(540,315,700,575),1,AL),
(1,"Detersivo lavatrice",7.95,4.2,"Omino Bianco muschio bianco o igienizzante 35 lavaggi x 3, 1,4 l x 3 (max 3 pezzi)",(85,610,470,900),1,AL),
# p2 carta
(2,"Yogurt",1.89,0.92,"Danone Vellutato con frutta frullata 115 g x 8",(455,130,880,320),1,AL),
(2,"Mozzarella",2.38,0.4,"Natura Sincera 100 g x 4",(365,390,580,570),1,AL),
(2,"Patatine surgelate",1.49,0.5,"Pizzoli Patasnella ultraveloci 500 g",(675,375,890,560),1,AL),
(2,"Cialde caffè",12.99,80,"Kimbo Espresso Napoli 80 capsule compatibili Nespresso (max 3 pezzi)",(100,410,320,730),1,AL),
(2,"Caffè macinato",11.90,1,"Kimbo Gusto di Napoli 250 g x 4",(400,630,545,730),1,AL),
(2,"Fette biscottate",1.39,0.6,"Delverde Granfetta 80 fette 600 g",(120,830,440,1050),1,AL),
(2,"Croissant e brioche",1.49,0.225,"Bauli croissant vari tipi a partire da 225 g (max 9 pezzi)",(690,650,890,960),1,AL),
# p3 carta
(3,"Pasta di semola",0.69,0.5,"Voiello vari formati 500 g (max 24 pezzi)",(25,130,230,330),1,AL),
(3,"Passata di pomodoro",0.75,0.69,"Valgrì passata densa di pomodoro 690 g (max 12 pezzi)",(395,120,490,330),1,AL),
(3,"Acqua",2.52,9,"Uliveto effervescente naturale 1,5 l x 6",(665,110,840,330),1,AL),
(3,"Tonno in scatola",5.94,0.504,"Asdomar al naturale o all'olio di oliva 56 g x 9 (max 3 pezzi)",(25,350,220,570),1,AL),
(3,"Bibite gassate",1.25,2,"Pepsi classica o zero zuccheri 2 l (max 12 pezzi)",(365,345,510,575),1,AL),
(3,"Detersivo lavastoviglie",9.90,1,"Finish pastiglie o gel Quantum o Ultimate, maxi convenienza 120 lavaggi, a partire da 801 g (max 3 pezzi)",(640,400,940,705),1,AL),
(3,"Carta igienica",4.45,8,"Regina Cartacamomilla Maxi 8 maxi rotoli (max 3 pezzi)",(25,630,225,830),1,AL),
(3,"Bagnoschiuma",1.49,1,"Mil Mil vari tipi 1 l (max 6 pezzi)",(50,820,240,1040),1,AL),
(3,"Birra",1.99,0.99,"Heineken original o 0.0 33 cl x 3 (max 8 pezzi)",(360,660,620,950),1,AL),
(3,"Shampoo e balsamo",1.99,0.2,"Garnier Ultra Dolce shampoo o balsamo vari tipi, a partire da 200 ml (max 6 pezzi)",(660,820,860,1050),1,AL),
# p4 Natale
(4,"Panettone e pandoro",8.90,0.7,"Bauli panettone moro con gocce di cioccolato o crema gianduia, a partire da 700 g",(85,140,450,480),0,AL),
(4,"Panettone e pandoro",8.90,0.75,"Bauli Panmoro con gocce e crema al cioccolato o di Verona, a partire da 750 g",(540,150,800,480),0,AL),
(4,"Panettone e pandoro",5.99,0.8,"Balocco panettone Gocciolotto con maxi gocce di cioccolato 800 g",(55,605,180,790),0,AL),
(4,"Panettone e pandoro",7.49,0.75,"Bauli pandoro Ciocco Top 3 cioccolati o pistacchio 750 g",(55,815,200,975),0,AL),
(4,"Panettone e pandoro",7.49,0.75,"Bauli panettone Ciocco Top 3 cioccolati o pistacchio 750 g",(320,610,500,900),0,AL),
(4,"Panettone e pandoro",11.90,0.85,"Vergani pandoro pistacchio o caramello salato 850 g",(570,600,800,940),0,AL),
# p5
(5,"Cioccolatini e praline",10.90,0.375,"Ferrero Rocher 30 praline 375 g",(50,190,460,480),0,AL),
(5,"Cioccolatini e praline",5.99,0.2,"Lindt Lindor praline vari tipi 200 g",(500,125,830,330),0,AL),
(5,"Torrone",4.99,0.255,"Pernigotti torrone vari tipi 255 g",(495,370,870,550),0,AL),
(5,"Torrone",3.99,0.25,"Sperlari Zanzibar Il Nocciolato vari tipi 250 g",(30,600,380,785),0,AL),
(5,"Torrone",3.99,0.2,"Sperlari Zanzibar Le Specialità vari tipi 200 g",(30,830,375,1010),0,AL),
# p6
(6,"Banane",1.59,1,"Dole origine Centro America cat. I, al kg",(60,290,330,570),0,AL),
(6,"Clementine e mandarini",2.99,1.5,"Clementine Conad Percorso Qualità 1,5 kg",(740,120,890,340),0,AL),
(6,"Mele",1.59,0.75,"Golden DOP Melinda 750 g",(545,350,730,510),0,AL),
(6,"Kiwi",3.39,0.45,"Kiwi Green Zespri 450 g",(760,365,980,505),0,AL),
(6,"Noci",3.99,1,"Noci origine Francia cat. I, al kg",(525,610,740,730),0,AL),
(6,"Limoni",1.89,0.7,"Limoni 700 g, 100% italiani",(760,580,870,750),0,AL),
(6,"Broccoli e verdure a foglia",1.69,0.5,"Spinaci Conad 500 g, 100% italiani",(525,830,640,1000),0,AL),
(6,"Insalata",1.19,0.3,"Iceberg Conad 300 g",(760,835,930,1000),0,AL),
# p7
(7,"Patate",1.99,1.5,"Patata dell'Alto Viterbese IGP 1,5 kg, 100% Lazio",(20,320,330,790),0,AL),
(7,"Verdure fresche varie",1.49,0.6,"Cavolo nero toscano 600 g, 100% Lazio",(640,100,880,250),0,AL),
(7,"Verdure fresche varie",1.79,1,"Cavolfiore romanesco origine Lazio cat. I, al kg",(490,250,840,420),0,AL),
(7,"Verdure fresche varie",1.69,1,"Cicoria a mazzi origine Lazio cat. I, al kg",(590,410,940,560),0,AL),
(7,"Verdure fresche varie",1.89,1,"Finocchi origine Lazio cat. I, al kg",(500,590,890,790),0,AL),
(7,"Zucchine",1.79,1,"Zucchine verdi origine Lazio cat. I, al kg",(500,820,630,975),0,AL),
(7,"Funghi champignon",1.99,0.5,"Funghi champignon Conad 500 g, 100% Lazio",(725,820,880,1000),0,AL),
# p8
(8,"Legumi secchi",2.39,0.4,"Colfiorito lenticchie 400 g",(400,125,590,290),0,AL),
(8,"Legumi secchi",1.39,0.35,"Piacersi Conad legumi decorticati (ceci, fave, lenticchie rosse o piselli) a partire da 350 g",(30,290,230,740),0,AL),
(8,"Zuppe pronte e noodles",1.69,0.35,"Conad minestrone o zuppa alla toscana 350 g",(700,140,900,290),0,AL),
(8,"Frutta fresca varia",3.99,0.2,"Conad mix di bosco (mirtilli, lamponi e more) 200 g",(700,380,890,520),0,AL),
(8,"Succo di frutta",2.89,0.75,"Leni's spremuta di mela con mirtillo 750 ml",(410,590,560,790),0,AL),
# p9
(9,"Altro pesce",18.90,1,"Polpo arricciato, al kg",(20,120,240,290),0,AL),
(9,"Calamari e totani",6.90,1,"Anelli di totano decongelato, al kg",(255,120,480,290),0,AL),
(9,"Filetti di merluzzo",18.90,1,"Cuore di merluzzo pollack d'Alaska, al kg",(25,360,245,500),0,AL),
(9,"Salmone fresco",12.90,1,"Salmone a tranci, al kg",(255,370,480,520),0,AL),
(9,"Gamberi e mazzancolle",12.90,1,"Scampi, al kg",(255,590,480,760),0,AL),
(9,"Spigola e orata",9.90,1,"Spigola da 300 a 500 g, al kg",(495,820,780,970),0,AL),
(9,"Vino bianco",3.79,0.75,"Zibibbo Terre Siciliane IGT Cardilla 75 cl",(760,750,850,1010),0,AL),
# p10
(10,"Suino (altri tagli)",5.45,1,"Coppa con osso di suino Conad Percorso Qualità, al kg",(55,330,500,560),0,AL),
(10,"Suino (altri tagli)",5.95,1,"Pancetta di suino con costine, al kg",(530,120,880,330),0,AL),
(10,"Fesa di tacchino a fette",11.90,1,"Fesa di tacchino a fette formato convenienza, al kg",(525,360,750,505),0,AL),
(10,"Pollo e tacchino (altri tagli)",4.90,1,"Coscia di tacchino, al kg",(760,360,980,510),0,AL),
(10,"Pollo e tacchino (altri tagli)",3.99,0.4,"Conad bocconcini di pollo o di tacchino 400 g",(60,600,260,735),0,AL),
(10,"Hamburger",3.50,0.18,"Conad Smash Burger gusto formaggio o BBQ 90 g x 2",(295,595,440,735),0,AL),
(10,"Hamburger",4.30,0.18,"Sapori&Dintorni hamburger razze tipiche italiane vari tipi 180 g",(530,660,840,1020),0,AL),
(10,"Bovino (tagli vari)",16.90,1,"Bistecca di bovino adulto con osso, al kg",(55,820,500,990),0,AL),
# p11 vini 75 cl
(11,"Vino bianco",6.50,0.75,"Isonzo del Friuli DOC Cormòns 75 cl",(30,125,115,390),0,AL),
(11,"Vino bianco",3.99,0.75,"Verdicchio dei Castelli di Jesi DOC Classico Baró 75 cl",(265,125,350,390),0,AL),
(11,"Vino bianco",4.99,0.75,"Vermentino Toscana IGT Cantine Leonardo da Vinci 75 cl",(505,125,585,390),0,AL),
(11,"Vino bianco",8.49,0.75,"Greco di Tufo DOCG Feudi di San Gregorio 75 cl",(735,125,820,390),0,AL),
(11,"Vino rosso",3.99,0.75,"Nero d'Avola Syrah Sicilia DOC Settesoli 75 cl",(30,430,115,700),0,AL),
(11,"Vino rosso",4.50,0.75,"Lagrein Trentino DOC Grigolli Concilio 75 cl",(265,430,345,700),0,AL),
(11,"Vino rosso",4.50,0.75,"Chianti Riserva DOCG Geografico 75 cl",(495,430,585,700),0,AL),
(11,"Vino rosso",7.90,0.75,"Valpolicella Ripasso DOC Superiore Valdimezzo Sartori di Verona 75 cl",(725,495,810,960),0,AL),
(11,"Vino rosso",4.79,0.75,"Vitiano Rosso IGP Falesco 75 cl",(30,740,115,1000),0,AL),
(11,"Vino rosso",4.90,0.75,"Cannonau di Sardegna DOC Piero Mancini 75 cl",(265,740,345,1000),0,AL),
(11,"Vino rosso",5.99,0.75,"Rosso di Torgiano DOC Rubesco Lungarotti 75 cl",(495,740,585,1000),0,AL),
# p12 (all'etto)
(12,"Grana e formaggi duri",1.25,1,"Grana Padano scelto DOP stagionatura min. 16 mesi, a spicchi da 800 g (all'etto)",(60,130,500,470),0,AL),
(12,"Grana e formaggi duri",1.49,1,"Piave DOP Mezzano Lattebusche (all'etto)",(600,815,880,1010),0,AL),
(12,"Ricotta",0.75,1,"Santa Lucia Galbani (all'etto)",(530,130,870,330),0,AL),
(12,"Mozzarella",9.90,1,"Fiordilatte o ovolo Pettinicchio, al kg (0,99 all'etto)",(540,355,640,500),0,AL),
(12,"Gorgonzola",1.29,1,"Sapori&Idee gorgonzola e mascarpone (all'etto)",(765,360,900,490),0,AL),
(12,"Caciotta e formaggi semiduri",2.29,1,"Formaggio di capra La Prima, Testadura o Fior di Capra Amalattea (all'etto)",(60,590,420,780),0,AL),
(12,"Caciotta e formaggi semiduri",1.29,1,"Caciotta Roccapontina Casale Torrealta Cademartori (all'etto)",(525,585,750,745),0,AL),
(12,"Caciotta e formaggi semiduri",1.39,1,"Formaggio Il Vergaro Petrucci (all'etto)",(760,590,880,740),0,AL),
(12,"Formaggi freschi e latticini vari",10.90,1,"Brie Président, al kg (1,09 all'etto)",(60,820,280,960),0,AL),
(12,"Caciotta e formaggi semiduri",1.19,1,"Raclette (all'etto)",(305,825,490,960),0,AL),
# p13 (all'etto)
(13,"Prosciutto cotto",1.49,1,"Gran Tenerone Gran Terre, di alta qualità (all'etto)",(25,125,150,320),0,AL),
(13,"Prosciutto cotto",1.39,1,"Casa Modena arrosto Rustico, di alta qualità (all'etto)",(255,120,380,275),0,AL),
(13,"Salame",1.89,1,"Casa Modena Gran Magro, Milano o Ungherese (all'etto)",(20,355,200,500),0,AL),
(13,"Salumi affettati assortiti",2.89,1,"Conad roast beef all'inglese sottofesa (all'etto)",(260,380,390,520),0,AL),
(13,"Guanciale e pancetta",1.69,1,"Sapori&Dintorni guanciale (all'etto)",(560,270,880,500),0,AL),
(13,"Bresaola",3.49,1,"Sapori&Dintorni Bresaola della Valtellina IGP punta d'anca (all'etto)",(25,640,240,940),0,AL),
(13,"Prosciutto cotto",1.99,1,"Sapori&Dintorni cotto di alta qualità nazionale (all'etto)",(250,640,460,940),0,AL),
(13,"Mortadella",0.99,1,"Bologna IGP Due Torri Alcisa classica o con pistacchi (all'etto)",(730,590,940,740),0,AL),
(13,"Speck",1.99,1,"Speck cotto Senfter (all'etto)",(495,820,640,960),0,AL),
(13,"Speck",2.59,1,"Speck Alto Adige IGP Senfter (all'etto)",(725,820,900,960),0,AL),
# p14
(14,"Latte UHT",1.59,1,"Sapori&Dintorni latte intero di montagna microfiltrato pastorizzato 1 l",(60,125,170,290),0,AL),
(14,"Latte UHT",0.98,1,"Arborea Ad scremato o alta digeribilità 1 l",(295,125,430,290),0,AL),
(14,"Kefir",1.49,0.5,"I Love Kefir Sveltesse Nestlé vari tipi 500 g",(60,320,170,450),0,AL),
(14,"Kefir",0.69,0.33,"Müller Kefir da bere vari tipi 330 g",(545,330,720,560),0,AL),
(14,"Kefir",0.79,0.15,"Piacersi Conad kefir vari tipi 150 g",(60,880,200,1010),0,AL),
(14,"Yogurt",0.94,0.5,"Yogurt intero Vipiteno vari tipi 500 g",(290,310,400,450),0,AL),
(14,"Yogurt",2.69,1,"Conad yogurt bianco magro 0,1% di grassi o intero 1 kg"+BF,(770,290,900,470),0,FISSI),
(14,"Yogurt",0.85,0.25,"Conad soia 100% vegetale vari tipi 125 g x 2",(60,500,185,600),0,AL),
(14,"Yogurt",0.99,0.16,"Danone Hipro 15 g proteine vari tipi 160 g",(765,545,900,650),0,AL),
(14,"Yogurt",0.99,0.2,"Danone Hipro 20 g proteine al caramello 200 g",(770,710,880,790),0,AL),
(14,"Yogurt",0.99,0.12,"Conad cocco stracciatella o cocco con mango 100% vegetale 120 g",(295,690,415,780),0,AL),
(14,"Yogurt",1.91,0.4,"Nestlé Fruttolo Maxi Duo vari tipi 100 g x 4",(760,860,900,940),0,AL),
(14,"Yogurt",1.89,0.32,"Yomo Yomino 100% naturale fragola o banana 80 g x 4",(295,860,420,990),0,AL),
(14,"Yogurt",2.39,0.6,"Piacersi Conad latte fermentato con Lactobacillus Casei vari tipi 100 g x 6",(60,690,180,800),0,AL),
# p15
(15,"Grana e formaggi duri",28.90,10,"Sapori&Dintorni Parmigiano Reggiano DOP oltre 30 mesi, al kg",(25,285,120,375),0,AL),
(15,"Panna",1.39,0.2,"Parmalat Chef La Panna 200 ml",(270,150,390,290),0,AL),
(15,"Mozzarella",1.99,0.18,"Conad nodini di mozzarella 180 g",(260,330,380,440),0,AL),
(15,"Mozzarella",2.99,0.375,"Santa Lucia Galbani La Leggera Tris 125 g x 3",(510,130,700,350),0,AL),
(15,"Stracchino, crescenza e robiola",1.99,0.2,"Conad stracchino cremoso 200 g"+BF,(740,225,890,320),0,FISSI),
(15,"Stracchino, crescenza e robiola",2.44,0.18,"Vallelata stracchino cremoso 180 g",(270,510,390,590),0,AL),
(15,"Ricotta",1.43,0.2,"Vallelata ricottine fresche 100 g x 2",(510,510,640,570),0,AL),
(15,"Burro",1.74,0.2,"Gran Soresina Latteria Soresina burro 200 g",(745,500,860,570),0,AL),
(15,"Formaggio spalmabile",1.74,0.16,"Philadelphia Original 80 g x 2",(330,700,580,830),0,AL),
(15,"Pasta fresca",2.59,0.25,"Sapori&Dintorni pasta fresca all'uovo ripiena vari tipi 250 g",(30,390,230,600),0,AL),
(15,"Gnocchi",1.45,0.35,"Sapori&Dintorni gnocchetti alla tirolese 350 g",(30,680,160,830),0,AL),
(15,"Gorgonzola",2.59,2,"Conad gorgonzola dolce DOP 200 g (all'etto 1,30)",(30,870,150,1020),0,AL),
(15,"Grana e formaggi duri",4.99,2.5,"Conad Emmentaler svizzero 250 g",(280,870,350,1000),0,AL),
(15,"Grana e formaggi duri",1.19,1,"Gran Biraghi formaggio grattugiato fresco 100 g",(500,860,620,990),0,AL),
# p16
(16,"Guanciale e pancetta",1.44,1.2,"Beretta Il Guanciale Stick 60 g x 2 (sconto 50%)",(300,130,420,215),0,AL),
(16,"Guanciale e pancetta",1.89,1.6,"Negroni pancetta dolce o affumicata in cubetti 80 g x 2 (sconto 50%)",(570,125,740,215),0,AL),
(16,"Wurstel",1.35,0.25,"Wüber Wüberone pollo gusto delicato 250 g",(765,120,900,200),0,AL),
(16,"Pasta fresca",2.39,0.25,"Giovanni Rana Gioiaverde ravioli vari tipi 250 g (sconto 40%)",(60,310,270,640),0,AL),
(16,"Lasagne e cannelloni pronti",2.74,0.3,"Giovanni Rana parmigiana di melanzane o lasagne, a partire da 300 g (sconto 50%)",(310,310,640,430),0,AL),
(16,"Salmone affumicato",7.90,0.2,"Conad salmone affumicato norvegese 200 g",(290,520,430,640),0,AL),
(16,"Molluschi e frutti di mare",1.79,0.18,"Coraya bastoncini di mare 180 g (sconto 50%)",(760,510,880,640),0,AL),
(16,"Salame",15.90,10,"Galbani Galbanetto Il Tradizionale 220 g circa, al kg",(760,705,890,790),0,AL),
(16,"Uova",3.49,10,"Aia 10 uova fresche medie a pasta gialla da allevamento a terra (sconto 30%)",(760,860,900,960),0,AL),
(16,"Pasta sfoglia e basi",1.99,0.23,"Buitoni pasta brisée, frolla, sfoglia o pan dolce vari tipi 230 g",(190,750,720,830),0,AL),
# p17 surgelati
(17,"Zuppe surgelate",2.08,0.75,"Orogel Il Benessere minestrone Leggerezza 750 g (sconto 30%)",(20,125,235,270),0,AL),
(17,"Zuppe surgelate",2.44,0.6,"Findus minestrone Tradizione 5 minuti 600 g (sconto 30%)",(285,870,430,980),0,AL),
(17,"Molluschi e frutti di mare",6.19,0.5,"Conad seppie indopacifiche 500 g",(255,330,380,470),0,AL),
(17,"Pizza surgelata",2.21,0.375,"Cameo Pizza Regina alta margherita o diabolica, a partire da 375 g (sconto 40%)",(495,130,700,470),0,AL),
(17,"Verdure surgelate",1.79,0.6,"Orogel spinaci in soffici foglie 600 g",(735,520,900,650),0,AL),
(17,"Verdure surgelate",1.72,0.45,"Orogel Il Benessere contorno Leggerezza 450 g (sconto 50%)",(495,520,615,640),0,AL),
(17,"Gelati e sorbetti",3.19,0.5,"Conad vaschetta gelato I Cremosi vari tipi 500 g",(25,710,180,830),0,AL),
(17,"Filetti di merluzzo",6.49,0.3,"Findus 4 fiori di merluzzo 300 g",(610,810,730,890),0,AL),
(17,"Bastoncini e croccanti di pesce",5.99,0.75,"Findus bastoncini di merluzzo 24 pezzi + 6 gratis, 750 g",(560,910,700,980),0,AL),
(17,"Verdure surgelate",3.99,0.7,"Findus piselli primavera 700 g",(840,830,940,930),0,AL),
# p18
(18,"Caffè in grani",15.90,1,"Lavazza crema e gusto o espresso classico 1 kg",(60,125,155,290),0,AL),
(18,"Cialde caffè",13.99,100,"Conad Espresso Bar 100 cialde per macchine espresso 700 g",(295,130,420,230),0,AL),
(18,"Tè e tisane",1.99,1,"Lipton infuso vari tipi 20 filtri 34 g",(60,305,180,395),0,AL),
(18,"Cereali e muesli",1.99,0.4,"Nestlé Lion cereali integrali cioccolato e caramello 400 g (sconto 32%)",(535,330,650,480),0,AL),
(18,"Merendine",1.65,0.252,"Conad muffin 6 pezzi con pepite di cioccolato 252 g"+BF,(800,355,880,425),0,FISSI),
(18,"Biscotti",2.49,1,"Colussi Zuppalatte 250 g x 4",(60,495,190,562),0,AL),
(18,"Biscotti",1.99,0.26,"Mulino Bianco Baiocchi o Schiaccianoci, a partire da 260 g (sconto 33%)",(300,510,430,650),0,AL),
(18,"Biscotti",2.29,0.25,"Conad frollini al cacao extra croccanti 250 g",(530,510,640,640),0,AL),
(18,"Biscotti",2.09,0.263,"Doria Bucaneve senza lattosio o senza zuccheri aggiunti, a partire da 263 g",(770,500,985,575),0,AL),
(18,"Biscotti",1.75,0.24,"Mulino Bianco Nastrine 6 pezzi 240 g (sconto 35%)",(300,710,430,830),0,AL),
(18,"Biscotti",1.89,0.168,"Mulino Bianco Baiocchi nocciolato o pistacchio 168 g (sconto 32%)",(530,700,650,830),0,AL),
(18,"Merendine",2.99,0.36,"Ferrero Fiesta L'Originale 10 merendine 360 g",(770,700,920,780),0,AL),
(18,"Crema alla nocciola",2.99,0.58,"Barilla Pan di Stelle crema 580 g (sconto 50%)",(60,890,160,1030),0,AL),
(18,"Miele",4.49,0.5,"Conad miele millefiori 500 g",(300,890,430,1030),0,AL),
(18,"Confettura",3.49,0.33,"Rigoni di Asiago Fior di Frutta bio vari tipi, a partire da 330 g",(535,890,650,1030),0,AL),
# p19
(19,"Tavolette di cioccolato",3.25,0.13,"Novi nocciolato vari tipi 130 g",(30,130,160,225),0,AL),
(19,"Tavolette di cioccolato",2.19,0.2,"Conad tavoletta di cioccolato latte o fondente 200 g",(265,130,400,225),0,AL),
(19,"Pane e panini",1.99,0.5,"Pema pane di segale integrale o integrale agli 8 cereali 500 g",(25,310,160,400),0,AL),
(19,"Crackers",1.79,0.19,"Wasa fette croccanti vari tipi, a partire da 190 g",(500,315,625,410),0,AL),
(19,"Crackers",2.35,0.7,"Doriano Doria cracker vari tipi 700 g",(30,495,160,585),0,AL),
(19,"Pasta di semola",1.15,0.5,"Barilla Piccolini vari formati 500 g",(530,495,640,610),0,AL),
(19,"Patatine",1.88,0.175,"Pringles vari tipi 175 g (sconto 30%)",(30,880,160,1030),0,AL),
(19,"Frutta secca mista",2.99,0.25,"Ventura mix tostato in forno 250 g",(265,870,372,1030),0,AL),
(19,"Passata di pomodoro",0.79,0.4,"Petti pomodori pelati I Succosi 400 g",(500,880,610,1030),0,AL),
(19,"Sugo pronto",1.59,0.27,"Rodolfi I Sughi di Casa vari tipi 135 g x 2 (sconto 40%)",(735,870,880,1000),0,AL),
# p20
(20,"Passata di pomodoro",0.89,0.69,"La Molisana La Nostra Passata fine e vellutata 690 g (sconto 34%)",(90,125,190,290),0,AL),
(20,"Passata di pomodoro",1.25,0.35,"Petti polpa fine o passata di datterini toscano bio 350 g (sconto 33%)",(295,130,400,290),0,AL),
(20,"Passata di pomodoro",1.09,0.42,"Mutti polpa di pomodoro 210 g x 2 (sconto 31%)",(525,125,700,210),0,AL),
(20,"Sugo pronto",0.99,0.35,"Bottega di Sicilia salsa pronta vari tipi 350 g (sconto 50%)",(770,130,880,290),0,AL),
(20,"Olio di semi",2.99,1,"Maya olio di semi di mais 1 l",(90,310,188,470),0,AL),
(20,"Olio extravergine di oliva",4.99,1,"Conad olio extra vergine di oliva classico 1 l",(320,310,420,470),0,AL),
(20,"Olio extravergine di oliva",7.99,1,"Monini Il Decanto olio extra vergine di oliva 1 l",(560,310,640,470),0,AL),
(20,"Olio extravergine di oliva",7.99,1,"Farchioni olio extra vergine di oliva italiano filiera tracciata 1 l (sconto 35%)",(790,320,860,470),0,AL),
(20,"Tonno in scatola",3.99,0.122,"Callipo filetti di tonno vari tipi, a partire da 122 g sgocciolato (sconto 50%)",(290,505,400,640),0,AL),
(20,"Tonno in scatola",10.90,0.72,"Rio Mare all'olio di oliva Gran Risparmio 120 g x 6",(525,495,720,600),0,AL),
(20,"Tonno in scatola",3.59,0.195,"Rio Mare all'olio di oliva 65 g x 3",(760,520,900,590),0,AL),
(20,"Conserve di verdura e frutta",0.85,0.25,"Bonduelle Legumeria vari tipi, a partire da 250 g sgocciolato",(60,870,160,1020),0,AL),
(20,"Conserve di verdura e frutta",3.09,0.56,"Bonduelle mais 140 g x 3 + 1 gratis",(300,880,450,955),0,AL),
# p21
(21,"Acqua",0.25,2,"Fabia acqua minerale naturale 2 l",(295,120,370,290),0,AL),
(21,"Succo di frutta",1.99,1.6,"Valfrutta succo e polpa vari tipi 200 ml x 8 (sconto 50%)",(770,125,940,215),0,AL),
(21,"Succo di frutta",1.59,1,"Conad succo 100% vari tipi 1 l",(35,310,160,390),0,AL),
(21,"Tè freddo",0.89,1.25,"Vitasnella tè zero pesca o limone 1,25 l (sconto 35%)",(280,320,400,480),0,AL),
(21,"Succo di frutta",2.29,2,"Rauch Bravo bevanda vari tipi 2 l",(525,310,640,450),0,AL),
(21,"Bibite gassate",1.29,1.5,"Fanta o Sprite vari tipi 1,5 l",(760,310,880,470),0,AL),
(21,"Bibite gassate",0.89,1,"Lemonsoda o Oransoda vari tipi 1 l (sconto 25%)",(20,500,150,650),0,AL),
(21,"Birra",1.39,0.66,"Angelo Poretti 4 Luppoli 66 cl",(530,490,600,650),0,AL),
(21,"Birra",0.79,0.5,"11 Paralleli birra bionda classica 50 cl",(760,490,830,650),0,AL),
(21,"Birra",1.99,0.5,"La Bière du Démon 12° 50 cl",(50,680,120,830),0,AL),
(21,"Birra",4.39,0.75,"L'Angelus birra Triple Hop 75 cl",(290,680,350,830),0,AL),
(21,"Birra",2.10,0.44,"Mastri Birrai Umbri birra artigianale IPA o Pils 44 cl",(530,690,630,830),0,AL),
(21,"Vino rosso",2.99,1.5,"Conad Lambrusco dell'Emilia IGT secco o amabile 1,5 l",(730,680,850,830),0,AL),
(21,"Vino (varie etichette)",2.59,1,"Bella Tavola vino bianco o rosso 1 l",(30,870,200,1020),0,AL),
(21,"Vino (varie etichette)",7.49,5,"Rusticanello Terre Siciliane IGT Cantine Ivam bianco o rosso 5 l",(265,870,380,1020),0,AL),
(21,"Vino (varie etichette)",2.70,0.75,"Masseria Settearchi Falanghina o Negroamaro Salento IGT 75 cl (sconto 50%)",(495,880,640,1030),0,AL),
(21,"Vino (varie etichette)",4.90,0.75,"Roccafiore Grechetto o Sangiovese Umbria IGT 75 cl",(755,860,840,1030),0,AL),
# p22
(22,"Vino rosso",3.79,0.75,"Cardilla Frappato Terre Siciliane IGT 75 cl",(100,130,190,290),0,AL),
(22,"Prosecco",3.25,0.75,"Villa Annone spumante Prosecco DOC extra dry 75 cl (sconto 50%)",(300,130,380,290),0,AL),
(22,"Prosecco",2.49,0.75,"Villa Annone spumante Ribolla Gialla extra dry 75 cl (sconto 50%)",(535,130,620,290),0,AL),
(22,"Aperitivi e spritz",4.99,0.7,"Conad bitter 70 cl",(800,130,880,290),0,AL),
(22,"Aperitivi e spritz",2.95,0.7,"Conad aperitivo ideale per spritz 70 cl (sconto 31%)",(50,310,160,470),0,AL),
(22,"Amari e liquori",9.90,0.7,"Jannamico liquore amaro L'Originale Abruzzese 70 cl",(300,310,390,470),0,AL),
(22,"Amari e liquori",6.79,0.5,"Zedda Piras mirto 50 cl",(560,310,630,470),0,AL),
(22,"Superalcolici",9.90,0.7,"J&B blended scotch whisky 70 cl",(80,500,190,660),0,AL),
(22,"Superalcolici",22.90,0.7,"Johnnie Walker Black blended scotch whisky 70 cl",(305,500,390,660),0,AL),
(22,"Superalcolici",7.45,0.7,"Wyborowa vodka 70 cl",(560,500,630,660),0,AL),
(22,"Superalcolici",24.90,0.7,"Citadelle gin de France 70 cl",(800,500,880,660),0,AL),
# p23 casa
(23,"Detersivo lavatrice (al lavaggio)",15.90,1,"Dixan Pulito Profondo detersivo lavatrice 82 lavaggi 4,805 kg",(260,150,360,290),0,AL),
(23,"Ammorbidente",2.97,1.9,"Fabuloso ammorbidente concentrato vari tipi 86 lavaggi 1,9 l (sconto 50%)",(490,125,640,290),0,AL),
(23,"Detergente pavimenti",1.89,0.9,"Citrosil detergente pavimenti igienizzante 900 ml, a partire da",(30,500,150,650),0,AL),
(23,"Detergente spray",1.50,0.5,"Winni's detergente multiuso spray 500 ml, a partire da",(265,500,380,650),0,AL),
(23,"Detergente spray",1.99,0.65,"Vetril detergente vetri e multiuso spray 650 ml",(500,500,610,650),0,AL),
(23,"Detergente pavimenti",1.99,0.75,"Emulsio detergente pavimenti o panni Ravviva vari tipi 750 ml (sconto 33%)",(740,500,990,760),0,AL),
(23,"Anticalcare",1.49,0.75,"Conad anticalcare spray 750 ml"+BF,(95,722,160,800),0,FISSI),
(23,"Gel WC",1.69,0.7,"WC Net vari tipi 700 ml",(260,680,400,830),0,AL),
# p24 animali
(24,"Umido per gatto",0.59,0.085,"Sheba cibo umido per gatto vari tipi 85 g",(60,130,190,290),0,AL),
(24,"Umido per gatto",1.49,0.34,"Petfriends Plus filettini in salsa gatti adulti 85 g x 4",(290,130,420,290),0,AL),
(24,"Crocchette per gatto",2.85,0.8,"Petfriends Plus alimento gatto adult vari tipi 800 g",(520,125,660,290),0,AL),
(24,"Crocchette per cane",3.45,0.8,"Cesar cibo secco cani manzo, pollame e verdure, salmone e verdure 800 g",(65,300,190,470),0,AL),
(24,"Umido per cane",1.18,0.085,"Cesar Fresh Bowls alimento umido cane pollo e riso o anatra e riso 85 g (sconto 30%)",(400,315,620,430),0,AL),
(24,"Carta igienica",1.69,4,"Conad carta igienica ultra morbida 4 rotoli"+BF,(305,895,430,1000),0,FISSI),
# p25 igiene
(25,"Bagnoschiuma",1.79,0.225,"Nivea o Dove doccia crema o doccia schiuma vari tipi 225 ml, a partire da",(35,125,230,290),0,AL),
(25,"Shampoo e balsamo",2.69,0.2,"Pantene shampoo, balsamo, olio o maschera, a partire da 200 ml",(255,125,380,290),0,AL),
(25,"Shampoo e balsamo",2.49,0.225,"Clear Men shampoo vari tipi 225 ml",(525,125,640,290),0,AL),
(25,"Sapone",0.89,0.3,"Vidal sapone liquido muschio bianco 300 ml (sconto 50%)",(45,330,170,480),0,AL),
(25,"Sapone",1.49,0.4,"Neutro Roberts ricarica sapone liquido 400 ml",(255,310,380,480),0,AL),
(25,"Detergente intimo",1.49,0.6,"Conad Essentiae ricarica detergente intimo 600 ml",(525,310,640,470),0,AL),
(25,"Crema mani e corpo",1.49,0.15,"Leocrema crema corpo o multiuso, a partire da 150 ml",(520,500,630,650),0,AL),
(25,"Crema mani e corpo",1.50,0.1,"Conad Essentiae crema mani protettiva 100 ml",(800,500,885,590),0,AL),
(25,"Dentifricio",2.49,0.075,"Parodontax dentifricio vari tipi, a partire da 75 ml",(60,865,410,975),0,AL),
# p26 / p28
(26,"Asciugatutto",3.99,1,"Paperd bobina asciugatutto 700 strappi, 2 veli",(770,610,900,770),1,AL),
(28,"Stendini e assi da stiro",29.94,1,"Colombo stendibiancheria Brooklyn in acciaio, 25 m di stesa (sconto 40%, prima 49,90 €)",(525,135,740,330),0,AL),
]

ids = {n: G(n) for n in {r[1] for r in R}}
# anti-duplicati: stesso prodotto/prezzo/q gia' presente per conad con zona A e dal >= 2026-11-05
esist = {(o["p"], o["prezzo"], o["q"]): o["l"].lower() for o in d["offerte"] if o["s"] == "conad" and "A" in o["z"] and o["dal"] >= "2026-11-05"}
cache = {}
n = salt = 0
for pag, nome, prezzo, q, desc, box, carta, al in R:
    assert prezzo > 0 and q > 0 and D1 <= al
    if (ids[nome], prezzo, q) in esist and desc.split()[0].lower() in esist[(ids[nome], prezzo, q)]:
        salt += 1; print("saltata:", nome, prezzo, q)
        continue
    im = cache.setdefault(pag, Image.open(f"{WD}/p-{pag:02d}.jpg").convert("RGB"))
    foto = L.ritaglia(im, tuple(2 * v for v in box))
    L.aggiungi_offerta(d, ids[nome], "conad", prezzo, q, desc, "A", D1, al, carta, foto)
    n += 1
L.salva(d, PERC)
print(n, "offerte conad zona A inserite;", salt, "saltate (duplicati)")
