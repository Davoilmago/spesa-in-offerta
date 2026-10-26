import sys; sys.path.insert(0,'/home/claude/spesa-in-offerta')
from strumenti import offerte_lib as L
from PIL import Image
A="/tmp/claude-0/-home-claude/7a1e70a4-cacf-559b-b441-ef58517f91bd/scratchpad/co/alta/p-%02d.jpg"
d=L.carica('sito/offerte.js')
# togli le vecchie offerte Conad della zona Anzio gia' scadute e quelle di questo volantino (rilancio sicuro)
d['offerte']=[o for o in d['offerte'] if not (o['s']=='conad' and o.get('dal')=='2026-10-30')]
FV="Frutta & Verdura";CAR="Carne";PES="Pesce";SAL="Salumi & Formaggi"
def P(n,e,c,u): return L.nuovo_prodotto(d,n,e,c,u)["id"]
def G(n):
    p=L.trova_prodotto(d,n); assert p,n; return p["id"]
n=dict(
 pere=P("Pere","🍐",FV,"kg"),kiwi=P("Kiwi","🥝",FV,"kg"),limoni=P("Limoni","🍋",FV,"kg"),
 granny=P("Mele Granny Smith","🍏",FV,"kg"),fuji=P("Mele Fuji","🍎",FV,"kg"),reddel=P("Mele Red Delicious","🍎",FV,"kg"),
 tonnof=P("Tonno fresco","🐟",PES,"kg"),calamari=P("Calamari","🦑",PES,"kg"),mazz=P("Mazzancolle","🦐",PES,"kg"),cozze=P("Cozze","🦪",PES,"kg"),
 macbov=P("Macinato di bovino","🥩",CAR,"kg"),arista=P("Arista di suino","🥩",CAR,"kg"),filsuino=P("Filetto di suino","🥩",CAR,"kg"),quarto=P("Quarto posteriore di pollo","🍗",CAR,"kg"),
 salame=P("Salame","🥓",SAL,"etto"))
ids={k:G(v) for k,v in dict(latte="Latte UHT",pasta="Pasta di semola",evo="Olio extravergine di oliva",passata="Passata di pomodoro",cialde="Cialde caffè",caffe="Caffè macinato",tonno="Tonno in scatola",acqua="Acqua",biscotti="Biscotti",birra="Birra",asciug="Asciugatutto",detlav="Detersivo lavatrice",bagno="Bagnoschiuma",ammorb="Ammorbidente",cartaig="Carta igienica",bibite="Bibite gassate",
 banane="Banane",cachi="Cachi",noci="Noci",patate="Patate",castagne="Castagne",golden="Mele Golden",gala="Mele Gala",spigole="Spigole",
 hamb="Hamburger di bovino",pollo="Petto di pollo a fette",crudo="Prosciutto crudo",cotto="Prosciutto cotto",mozz="Mozzarella",ricotta="Ricotta",asiago="Asiago",grana="Grana e formaggi duri",gorg="Gorgonzola",fesa="Fesa di tacchino a fette",mortadella="Mortadella",
 yogurt="Yogurt",pfresca="Pasta fresca",nocciola="Crema alla nocciola",ciocc="Cioccolato fondente",sugo="Sugo pronto",pane="Pane in cassetta",succo="Succo di frutta",fettine="Fettine di bovino",wurstel="Wurstel",riso="Riso",
 pizza="Pizza surgelata",gamberoni="Gamberoni argentina",bastoncini="Bastoncini di merluzzo",funghi="Funghi champignon",croccane="Crocchette per cane",croccagatto="Crocchette per gatto").items()}
D1,D2,AL="2026-10-30","2026-11-06","2026-11-12"
# (pag, prodotto, prezzo, q, desc, box, dal, carta)
R=[
(1,ids['latte'],2.08,2,"Parmalat parz. scremato 1 l, 2 pezzi",(40,190,250,580),D1,1),
(1,ids['pasta'],1.88,2,"Barilla 1 kg, 2 pezzi",(210,590,500,950),D1,1),
(1,ids['evo'],8.38,2,"De Cecco classico 1 l, 2 pezzi",(520,350,700,720),D1,1),
(2,ids['cialde'],10.90,80,"Kimbo napoletano 80 cialde",(375,375,540,570),D1,1),
(2,ids['caffe'],12.49,1,"Kimbo fresco 4 x 250 g",(710,415,935,560),D1,1),
(2,ids['passata'],0.79,0.7,"La Torrente tradizionale 700 g",(430,600,520,810),D1,1),
(2,ids['tonno'],5.49,0.48,"Mareblu 8 x 60 g",(375,850,580,1020),D1,1),
(2,ids['acqua'],0.62,3,"Levissima 1,5 l, 2 pezzi",(690,610,860,1020),D1,1),
(2,ids['biscotti'],2.68,0.8,"Crostatine Mulino Bianco 400 g, 2 pezzi",(60,660,350,960),D1,1),
(3,ids['birra'],4.99,3.72,"Nastro Azzurro 6 x 62 cl",(45,120,215,320),D1,1),
(3,ids['asciug'],5.95,6,"Scottex Quanto Basta 6 maxirotoli",(335,380,545,540),D1,1),
(3,ids['detlav'],7.99,2.565,"Dixan 3 x 855 ml",(650,170,860,520),D1,1),
(3,ids['bagno'],4.94,1.4,"Dove 700 ml, 2 pezzi",(60,410,300,740),D1,1),
(6,ids['banane'],1.29,1,"Al kg",(60,300,430,560),D1,0),
(6,ids['cachi'],2.79,0.85,"Cachi 850 g",(525,225,630,330),D1,0),
(6,n['pere'],2.49,0.85,"Pera abate fetel 850 g",(790,145,950,290),D1,0),
(6,n['kiwi'],3.39,1,"Kiwi Cile al kg",(520,395,740,490),D1,0),
(6,n['limoni'],1.89,0.5,"Limoni 500 g",(760,360,860,520),D1,0),
(6,ids['castagne'],4.49,1,"Marroni al kg",(525,590,730,740),D1,0),
(6,ids['noci'],3.29,0.35,"Noci di Sorrento 350 g",(765,690,900,790),D1,0),
(6,ids['patate'],2.19,1.25,"Patata novella Selenella 1,25 kg",(535,810,650,980),D1,0),
(7,n['granny'],1.79,1,"Al kg",(50,330,430,520),D1,0),
(7,n['fuji'],1.59,1,"Al kg",(490,300,860,470),D1,0),
(7,n['reddel'],1.69,1,"Al kg",(540,830,940,1000),D1,0),
(7,ids['golden'],2.10,1.5,"Golden o Red Delicious DOP Val di Non 1,5 kg",(170,780,540,1030),D1,0),
(9,ids['spigole'],12.90,1,"Spigola italiana al kg",(20,120,410,330),D1,0),
(9,n['tonnof'],15.90,1,"Filetto di tonno decongelato al kg",(20,360,240,560),D1,0),
(9,n['calamari'],16.90,1,"Calamari al kg",(20,600,240,780),D1,0),
(9,n['mazz'],8.90,1,"Mazzancolle tropicali decongelate al kg",(255,590,480,780),D1,0),
(9,n['cozze'],3.80,1,"Cozze Olbiesine al kg",(490,790,720,960),D1,0),
(10,ids['hamb'],3.49,0.18,"Scottona 180 g",(60,330,400,560),D1,0),
(10,n['macbov'],12.90,1,"Macinato di bovino adulto al kg",(55,590,420,790),D1,0),
(10,n['arista'],4.90,1,"Arista di suino a trancio al kg",(530,140,740,290),D1,0),
(10,n['filsuino'],7.90,1,"Filetto di suino al kg",(540,440,980,680),D1,0),
(10,ids['pollo'],8.90,1,"Petto di pollo a fette al kg",(330,820,610,1010),D1,0),
(10,n['quarto'],3.50,1,"Quarto posteriore di pollo al kg",(770,830,960,980),D1,0),
(11,ids['crudo'],2.49,1,"Prosciutto di Parma DOP (all'etto)",(490,150,720,500),D1,0),
(11,ids['cotto'],1.59,1,"Cotto alta qualità arrosto (all'etto)",(740,180,960,510),D1,0),
(11,ids['mozz'],12.40,1,"Fiordilatte Vallelata al kg",(40,590,230,730),D1,0),
(11,ids['ricotta'],9.90,1,"Ricotta di pecora Amatrice al kg",(290,580,470,730),D1,0),
(11,ids['asiago'],0.89,1,"Asiago fresco DOP (all'etto)",(730,810,940,1000),D1,0),
(11,ids['grana'],2.29,1,"Pecorino Campagnolo (all'etto)",(500,810,700,970),D1,0),
(11,ids['grana'],1.79,1,"Piave vecchio DOP (all'etto)",(30,330,480,520),D1,0),
(12,n['salame'],1.59,1,"Milano o Ungherese Galbani (all'etto)",(55,130,280,490),D1,0),
(12,ids['fesa'],21.90,1,"Cotto di tacchino Galbani al kg",(290,360,510,500),D1,0),
(12,ids['cotto'],1.29,1,"Fetta Golosa Galbani (all'etto)",(530,130,740,510),D1,0),
(12,ids['grana'],1.35,1,"Grana Padano DOP 20 mesi (all'etto)",(50,590,290,790),D1,0),
(12,ids['gorg'],1.39,1,"Gorgonzola DOP (all'etto)",(540,660,780,880),D1,0),
(12,ids['mortadella'],1.39,1,"Mortadella in cotenna (all'etto)",(360,790,570,1020),D1,0),
(13,ids['latte'],0.98,1.5,"Sterilgarda parz. scremato 1,5 l",(55,130,150,290),D1,0),
(13,ids['yogurt'],2.69,1,"Müller cremoso 8 x 125 g",(550,120,720,250),D1,0),
(13,ids['mozz'],14.90,1,"Santa Lucia senza lattosio 100 g",(250,540,380,640),D1,0),
(13,ids['mozz'],4.68,0.6,"Fresca Granarolo 3 x 100 g, 2 pezzi",(740,310,950,470),D1,0),
(13,ids['mozz'],3.99,0.3,"Bufala Campana DOP 3 x 100 g",(30,530,230,680),D1,0),
(13,ids['ricotta'],2.49,0.45,"Santa Lucia 450 g",(730,520,950,650),D1,0),
(14,ids['grana'],3.99,1.5,"Parmigiano Reggiano DOP grattugiato 150 g",(530,140,720,280),D1,0),
(14,ids['grana'],2.99,1.5,"Grana Padano DOP grattugiato 150 g",(760,140,940,280),D1,0),
(14,ids['grana'],5.69,3,"Bocconcini di Grana Padano DOP 300 g",(60,320,200,480),D1,0),
(14,ids['crudo'],3.49,1.6,"Sofficette Citterio 2 x 80 g",(525,310,680,470),D1,0),
(14,ids['pfresca'],2.58,1,"Trofiette Giovanni Rana 500 g, 2 pezzi",(300,500,420,650),D1,0),
(14,ids['pfresca'],2.98,0.9,"Tonnarelli all'uovo Rana 450 g, 2 pezzi",(530,490,740,760),D1,0),
(14,ids['pfresca'],1.39,0.5,"Orecchiette o trofie Conad 500 g",(70,700,260,830),D1,0),
(14,n['salame'],11.90,10,"Napoli Galbanetto al kg",(555,860,740,1030),D1,0),
(15,ids['pizza'],4.98,1.24,"Regina classica Cameo 2 x 620 g",(20,320,240,590),D1,0),
(15,ids['gamberoni'],7.39,0.238,"Gamberi argentini Findus 238 g",(265,505,480,600),D1,0),
(15,ids['bastoncini'],3.19,0.45,"Conad 18 bastoncini 450 g",(20,710,240,800),D1,0),
(15,ids['funghi'],1.29,0.45,"Conad a fette surgelati 450 g",(20,880,240,1010),D1,0),
(17,ids['pane'],0.75,0.285,"Pan carrè Barilla 285 g",(20,310,240,470),D1,0),
(17,ids['pasta'],1.38,1,"Barilla integrale 500 g, 2 pezzi",(20,860,240,1020),D1,0),
(17,ids['riso'],1.95,1,"Gallo Blond 1 kg",(740,880,940,1020),D1,0),
(16,ids['cialde'],9.50,30,"L'Or Barista compatibili Nespresso 30 caps",(60,125,270,290),D1,0),
(16,ids['biscotti'],1.99,0.4,"Gocciole Pavesi 400 g",(300,320,500,470),D1,0),
(16,ids['biscotti'],2.58,1.3,"Cabrioni 650 g, 2 pezzi",(525,310,660,470),D1,0),
(16,ids['nocciola'],2.99,0.7,"Crema alle nocciole Conad 700 g",(525,510,640,660),D1,0),
(16,ids['ciocc'],1.39,0.1,"Tavoletta Novi fondente 100 g",(755,885,950,990),D1,0),
(16,ids['biscotti'],1.45,0.5,"Biscotti per latte o petit 500 g",(800,340,960,450),D1,0),
(18,ids['evo'],7.99,1,"Farchioni Il Casolare 1 l",(60,490,185,660),D1,0),
(18,ids['tonno'],4.99,0.31,"Auriga all'olio di oliva 310 g",(525,500,710,600),D1,0),
(18,ids['tonno'],4.95,0.26,"Rio Mare filo d'olio 4 x 65 g",(765,505,975,600),D1,0),
(18,ids['sugo'],2.50,0.56,"Mutti 280 g, 2 pezzi",(300,320,500,470),D1,0),
(18,ids['succo'],1.79,1.2,"Succo e polpa Conad 6 x 200 ml",(680,790,770,880),D1,0),
(19,ids['acqua'],0.25,1,"Acqua minerale naturale Conad 1 l",(515,500,610,670),D1,0),
(19,ids['bibite'],0.89,1.5,"Cola Conad 1,5 l",(790,900,930,1030),D1,0),
(19,ids['tonno'],5.29,0.312,"Rizzoli all'olio di oliva 312 g",(255,120,470,235),D1,0),
(20,ids['birra'],1.99,0.99,"Tuborg 3 x 33 cl",(60,140,270,290),D1,0),
(20,ids['birra'],2.29,0.44,"Guinness Blonde IPA 44 cl",(760,140,830,290),D1,0),
(21,ids['bagno'],2.99,1.2,"Essentiae 2 x 600 ml",(20,120,240,420),D1,0),
(21,ids['cartaig'],6.49,12,"Conad Maxi Rotoli 12 rotoli",(540,860,810,1030),D1,0),
(22,ids['croccane'],9.90,10,"Miglior Cane Morando con manzo 10 kg",(630,705,800,1020),D1,0),
(22,ids['croccagatto'],3.75,2,"Petfriends gatti sterilizzati 2 kg",(540,140,640,340),D1,0),
(24,ids['detlav'],4.59,1.4,"Perlana 28 lavaggi 1,4 l",(300,130,500,330),D1,0),
(24,ids['ammorb'],4.79,1.827,"Coccolino 87 lavaggi 1,827 l",(530,130,660,330),D1,0),
(30,ids['gala'],1.59,1,"Royal Gala al kg (dal 6/11)",(60,150,510,560),D2,0),
(30,ids['fettine'],16.90,1,"Fettine per pizzaiola di bovino adulto (dal 6/11)",(60,620,270,780),D2,0),
(30,ids['hamb'],3.90,0.18,"Danese di bovino adulto 180 g (dal 6/11)",(760,600,970,750),D2,0),
(31,ids['yogurt'],0.89,0.17,"Piacersi greco 170 g (dal 6/11)",(20,120,240,330),D2,0),
(31,ids['pasta'],1.19,1,"Rummo 1 kg (dal 6/11)",(500,125,950,540),D2,1),
(31,ids['gorg'],1.99,1.5,"Dolcelatte Galbani 150 g (dal 6/11)",(300,350,420,500),D2,0),
(31,ids['wurstel'],1.99,0.2,"Wüber 200 g (dal 6/11)",(490,590,690,740),D2,0),
(31,ids['cotto'],1.49,1,"Cotto toast Beretta 100 g (dal 6/11)",(65,590,200,740),D2,0),
(32,ids['evo'],6.90,1,"Cirio Riserva Francesco Cirio 1 l (dal 6/11)",(110,160,260,540),D2,1),
(32,ids['passata'],2.29,0.9,"Polpa di datterini Mutti 3 x 300 g (dal 6/11)",(540,170,960,300),D2,1),
(32,ids['detlav'],3.29,1.71,"Spuma di Sciampagna 38 lavaggi (dal 6/11)",(60,630,270,950),D2,1),
]
cache={};sheet=[]
for pag,pid,prezzo,q,desc,box,dal,carta in R:
    im=cache.setdefault(pag,Image.open(A%pag).convert("RGB"))
    b=tuple(2*v for v in box)
    L.aggiungi_offerta(d,pid,"conad",prezzo,q,desc,"A",dal,AL,carta,L.ritaglia(im,b))
    sheet.append(im.crop(b).resize((200,200)))
usati={o["p"] for o in d["offerte"]}
d["prodotti"]=[p for p in d["prodotti"] if p["id"] in usati]
L.salva(d,'sito/offerte.js')
W=Image.new("RGB",(2000,200*((len(sheet)+9)//10)),"white")
for k,im in enumerate(sheet): W.paste(im,((k%10)*200,(k//10)*200))
W.save("/tmp/claude-0/-home-claude/7a1e70a4-cacf-559b-b441-ef58517f91bd/scratchpad/co/ritagli.jpg",quality=70)
print(len(R),"offerte conad;",len(d['prodotti']),"prodotti;",len(d['offerte']),"offerte")
