import sys; sys.path.insert(0,'/home/claude/spesa-in-offerta')
from strumenti import offerte_lib as L
A="/tmp/claude-0/-home-claude/7a1e70a4-cacf-559b-b441-ef58517f91bd/scratchpad/eu/alta/p-%02d.jpg"
d=L.carica('sito/offerte.js')
d['offerte']=[o for o in d['offerte'] if o['s']!='eurospin']
DAL,AL="2026-10-22","2026-11-01"
def P(nome,e,cat,u): return L.nuovo_prodotto(d,nome,e,cat,u)["id"]
LAT="Latte, Uova & Latticini";SAL="Salumi & Formaggi";DIS="Pasta, Olio & Conserve";FV="Frutta & Verdura";CAR="Carne";BEV="Bevande";COL="Colazione & Dolci";SUR="Surgelati"
def nuovo_casa(n,e,u): 
    p=L.nuovo_prodotto(d,n,e,"Altro",u); p["sub"]="Casa & pulizia"; return p["id"]
n={}
n['cachi']=P("Cachi","🍊",FV,"kg"); n['gala']=P("Mele Gala","🍎",FV,"kg"); n['patate']=P("Patate","🥔",FV,"kg")
n['mandorle']=P("Mandorle sgusciate","🥜",FV,"kg"); n['noci']=P("Noci","🥜",FV,"kg")
n['bresaola']=P("Bresaola","🥩",SAL,"etto"); n['salame']=P("Salame piccante","🥓",SAL,"etto"); n['asiago']=P("Asiago","🧀",SAL,"etto")
n['spalm']=P("Formaggio spalmabile","🧀",LAT,"kg"); n['ricotta']=P("Ricotta","🧀",LAT,"kg"); n['yogurt']=P("Yogurt","🥛",LAT,"kg")
n['pfresca']=P("Pasta fresca","🍝",DIS,"kg"); n['farina']=P("Farina 00","🌾",DIS,"kg"); n['sugo']=P("Sugo pronto","🍅",DIS,"kg")
n['olioo']=P("Olio di oliva","🫒",DIS,"l"); n['oliosem']=P("Olio di semi","🫒",DIS,"l"); n['tonno']=P("Tonno in scatola","🐟",DIS,"kg")
n['pane']=P("Pane in cassetta","🍞",COL,"kg"); n['nocciola']=P("Crema alla nocciola","🍫",COL,"kg"); n['ciocc']=P("Cioccolato fondente","🍫",COL,"kg")
n['succo']=P("Succo di frutta","🧃",BEV,"l")
n['muscolo']=P("Muscolo di bovino","🥩",CAR,"kg"); n['fettine']=P("Fettine di bovino","🥩",CAR,"kg"); n['costine']=P("Costine di suino","🥩",CAR,"kg")
n['macsuino']=P("Macinato di suino","🥩",CAR,"kg"); n['salsiccia']=P("Salsiccia di suino","🌭",CAR,"kg"); n['pollo']=P("Petto di pollo a fette","🍗",CAR,"kg")
n['manzo']=P("Fesa di manzo cotta","🥩",CAR,"kg"); n['hamb']=P("Hamburger di bovino","🍔",SUR,"kg"); n['wurstel']=P("Wurstel","🌭",CAR,"kg")
ids=dict(latte=1,mozz=2,pasta=3,evo=4,passata=5,golden=7,uva=9,brocc=10,funghi=14,fesa=18,braciole=19,burro=24,cotto=27,crudo=26,grana=29,gorg=30,riso=31,biscotti=32,caffe=33,cialde=34,pizza=35,bastoncini=36,birra=37,bibite=38,spigole=20,cartaig=40,asciug=41,detlav=42,ammorb=43,tovagl=46,bagno=47,crocc=51)
# (pagina, prodotto, prezzo, q, descrizione, box griglia, dal)
R=[
(1,ids['latte'],4.69,6,"Parz. scremato 6 x 1 l (quantità limitata)",(50,440,390,790),DAL),
(1,ids['pasta'],0.69,0.5,"Grano IGP assortita 500 g",(350,390,700,740),DAL),
(1,n['cachi'],1.99,1,"Al kg",(590,675,880,860),DAL),
(1,ids['golden'],0.99,1,"Al kg (sacchetto 3 kg)",(220,780,590,1030),DAL),
(2,ids['cotto'],2.49,1.2,"Alta qualità 120 g",(170,130,500,330),DAL),
(2,n['bresaola'],3.99,1,"Punta d'anca riserva 100 g",(510,205,730,340),DAL),
(2,n['salame'],1.09,1,"Ventricina piccante 100 g",(860,160,990,330),DAL),
(2,ids['cotto'],1.15,1.5,"Spalla cotta 150 g",(170,410,260,560),DAL),
(2,n['asiago'],7.59,10,"Asiago fresco DOP al kg (-15% alla cassa)",(600,440,740,570),DAL),
(2,ids['grana'],3.49,3,"Grana Padano DOP 300 g",(850,380,950,590),DAL),
(2,ids['mozz'],2.79,0.3,"Bocconcini di bufala DOP 300 g",(60,690,260,800),DAL),
(2,n['spalm'],0.79,0.2,"Fresco spalmabile 200 g",(400,620,700,800),DAL),
(2,n['ricotta'],0.59,0.25,"Ricotta fresca 250 g",(60,930,200,1060),DAL),
(2,n['pfresca'],0.79,0.5,"Trofie/orecchiette fresche 500 g",(530,910,730,1060),DAL),
(3,n['yogurt'],0.75,0.15,"Greco magro pesca/mirtillo 150 g",(330,200,480,330),DAL),
(3,n['yogurt'],0.59,0.15,"Bianco con cereali 150 g",(520,220,730,330),DAL),
(3,n['farina'],0.39,1,"Farina 00 di grano tenero 1 kg",(50,470,260,780),DAL),
(3,ids['riso'],3.39,2,"Basmati 2 kg",(380,400,500,580),DAL),
(3,ids['passata'],0.65,0.7,"Passata di pomodoro 700 g",(560,450,720,820),DAL),
(3,n['sugo'],0.89,0.4,"Basilico/all'arrabbiata 400 g",(390,590,500,830),DAL),
(3,n['olioo'],3.79,1,"Olio di oliva 1 l",(780,690,950,1070),DAL),
(3,n['oliosem'],6.59,5,"Olio di semi di girasole 5 l",(375,885,500,1070),DAL),
(4,n['tonno'],0.89,0.16,"Al naturale 160 g",(660,130,900,350),DAL),
(4,n['tonno'],2.19,0.3,"Trancetti all'olio d'oliva 300 g",(390,230,480,340),DAL),
(4,n['pane'],1.19,0.75,"American sandwich 750 g",(385,350,490,590),DAL),
(4,ids['caffe'],2.49,0.25,"Cuor d'aroma 250 g",(860,430,960,590),DAL),
(4,ids['cialde'],2.69,16,"Compatibili Dolce Gusto 16 pz",(170,600,490,820),DAL),
(4,ids['biscotti'],1.79,0.65,"Frollini integrali 650 g",(850,600,970,830),DAL),
(4,ids['evo'],7.69,1,"Estratto a freddo 1 l",(390,840,450,1060),DAL),
(4,n['nocciola'],1.99,0.2,"Crema alla nocciola 200 g",(800,900,960,1050),DAL),
(5,n['nocciola'],2.69,0.75,"Crema alla nocciola 750 g",(320,200,440,350),DAL),
(5,n['ciocc'],1.19,0.1,"Fondente 72% 100 g",(390,400,480,540),DAL),
(5,ids['bibite'],0.59,1.5,"Aranciata 1,5 l",(160,600,230,830),DAL),
(5,ids['birra'],0.49,0.5,"Birra 500 ml",(400,660,470,810),DAL),
(5,n['succo'],0.89,1,"Succo e polpa albicocca/pera 1 l",(680,640,930,1060),DAL),
(9,n['succo'],1.99,1,"Succo di mela Alpenspitz 1 l",(150,850,250,1120),DAL),
(9,ids['latte'],0.89,1,"Latte fieno UHT parz. scremato 1 l",(400,320,500,530),DAL),
(6,ids['asciug'],1.79,3,"Forte 3 rotoli",(430,110,690,310),DAL),
(6,ids['cartaig'],1.99,4,"La Lunghissima 4 rotoli, 2 veli",(740,250,980,550),DAL),
(6,ids['detlav'],1.79,1.5,"Capi colorati 25 lavaggi 1,5 l",(140,550,260,760),DAL),
(6,ids['detlav'],2.99,1.875,"Essenza di argan 25 lavaggi 1,875 l",(630,410,720,550),DAL),
(6,ids['ammorb'],1.29,1.5,"Concentrato 60 lavaggi 1,5 l",(310,650,470,770),DAL),
(6,ids['crocc'],2.39,1.5,"Premium pollo e tacchino 1,5 kg",(640,860,735,990),DAL),
(7,ids['bastoncini'],2.79,0.45,"15 pz 450 g",(730,440,960,590),DAL),
(7,ids['pizza'],1.99,0.365,"Ai funghi 365 g",(90,950,280,1060),DAL),
(7,ids['spigole'],6.39,0.38,"Filetti di branzino/spigola surgelati 380 g",(300,440,420,580),DAL),
(7,n['hamb'],4.99,0.75,"Bovino 10 pz 750 g",(290,690,490,800),DAL),
(8,ids['cotto'],2.99,1.2,"Alla meranese Alpenspitz 120 g",(560,495,740,630),DAL),
(8,ids['burro'],1.99,0.25,"Burro da latte fieno 250 g",(770,750,900,860),DAL),
(8,ids['grana'],1.99,1.25,"Trentingrana grattugiato 125 g",(640,700,740,860),DAL),
(12,n['mandorle'],6.99,0.8,"Sgusciate 800 g",(170,110,390,310),DAL),
(12,n['patate'],0.99,1,"Patate gialle al kg (sacco 2 kg)",(810,100,930,310),DAL),
(12,ids['uva'],2.99,0.8,"Vaschetta 800 g",(170,430,390,580),"2026-10-26"),
(12,n['gala'],1.49,1,"Al kg",(470,430,640,580),"2026-10-26"),
(12,ids['brocc'],1.49,0.5,"Broccoletti 500 g",(750,440,920,580),"2026-10-26"),
(13,n['muscolo'],10.99,1,"Muscolo di bovino adulto al kg",(70,150,340,320),DAL),
(13,n['fettine'],13.99,1,"Per pizzaiola e scaloppe al kg",(360,180,650,310),DAL),
(13,n['costine'],4.99,1,"Costine di suino al kg",(700,170,930,310),DAL),
(13,n['macsuino'],5.99,1,"Macinato di suino al kg",(30,430,340,550),DAL),
(13,n['salsiccia'],6.99,1,"Salsiccia di suino al kg",(380,410,640,540),DAL),
(13,n['pollo'],8.49,1,"Petto di pollo a fette al kg",(690,420,950,550),DAL),
(13,n['manzo'],16.99,1,"Fesa di manzo cotta al kg (gastronomia)",(30,700,300,860),DAL),
(13,ids['cotto'],11.49,10,"Prosciutto cotto scelto al kg (gastronomia)",(320,700,650,890),DAL),
(13,ids['fesa'],10.99,1,"Arrosto di fesa di tacchino al kg (gastronomia)",(700,710,950,880),DAL),
(13,ids['grana'],15.99,10,"Pecorino romano DOP al kg (gastronomia)",(190,890,390,1120),DAL),
(13,ids['gorg'],10.99,10,"Gorgonzola e mascarpone al kg (gastronomia)",(700,990,960,1120),DAL),
(14,n['sugo'],0.85,0.36,"Salsa di pomodoro datterino 360 g",(95,460,240,790),DAL),
(14,n['wurstel'],1.15,0.25,"Puro suino 3 pz 250 g",(290,460,470,570),DAL),
(14,ids['tovagl'],1.29,0.5,"Colorati 50 pz",(60,960,260,1110),DAL),
(14,ids['bagno'],1.19,0.5,"Assortito 500 ml",(320,940,480,1110),DAL),
(15,ids['funghi'],1.49,0.6,"Champignon a fette surgelati 600 g",(190,110,390,340),DAL),
(15,ids['evo'],6.49,0.75,"Bio 750 ml",(150,385,270,830),DAL),
(15,n['pfresca'],2.19,0.5,"Fettuccine/tagliatelle all'uovo 500 g",(740,440,960,590),DAL),
(15,ids['biscotti'],1.39,0.2,"Sbarazzini 200 g",(280,700,500,790),DAL),
(22,n['noci'],3.99,1,"Noci di Perigord DOP al kg (solo 30/10-1/11)",(270,240,500,370),"2026-10-30"),
(22,ids['braciole'],5.99,1,"Braciole di coppa al kg (solo 30/10-1/11)",(660,230,920,390),"2026-10-30"),
(22,ids['crudo'],2.49,2,"Prosciutto crudo 2 x 100 g, -30% (solo 30/10-1/11)",(140,420,300,600),"2026-10-30"),
(22,ids['cartaig'],2.29,12,"La Morbida 12 rotoli, -33% (solo 30/10-1/11)",(640,470,970,670),"2026-10-30"),
]
from PIL import Image
cache={}
import io
sheet=[]
for pag,pid,prezzo,q,desc,box,dal in R:
    im=cache.setdefault(pag,Image.open(A%pag).convert("RGB"))
    b=tuple(2*v for v in box)
    foto=L.ritaglia(im,b)
    L.aggiungi_offerta(d,pid,"eurospin",prezzo,q,desc,"AN",dal,AL,0,foto)
    sheet.append(im.crop(b).resize((200,200)))
usati={o["p"] for o in d["offerte"]}
d["prodotti"]=[p for p in d["prodotti"] if p["id"] in usati]
L.salva(d,'sito/offerte.js')
W=Image.new("RGB",(200*10,200*((len(sheet)+9)//10)),"white")
for k,im in enumerate(sheet): W.paste(im,((k%10)*200,(k//10)*200))
W.save("/tmp/claude-0/-home-claude/7a1e70a4-cacf-559b-b441-ef58517f91bd/scratchpad/eu/ritagli.jpg",quality=70)
print(len(R),"offerte eurospin;",len(d['prodotti']),"prodotti;",len(d['offerte']),"offerte")
