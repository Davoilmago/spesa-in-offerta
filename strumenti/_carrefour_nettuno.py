"""Carrefour Market Nettuno (6-15 novembre 2026): Sottocosto (zona N), Speciale detersivi e Speciale Aia (zona NL).
Uso: python3 strumenti/_carrefour_nettuno.py [percorso_offerte.js]   (idempotente)"""
import os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from strumenti import offerte_lib as L
from PIL import Image

PERC = sys.argv[1] if len(sys.argv) > 1 else "sito/offerte.js"
VOL = "/home/claude/spesa-in-offerta/volantini/lazio/nettuno/"
W = "/tmp/w2/"
PDF = {"n": "carrefour.pdf", "c2": "carrefour_2.pdf", "c3": "carrefour_3.pdf"}
D1, AL = "2026-11-06", "2026-11-15"


def pagina(src, pag):
    cart = W + src
    os.makedirs(cart, exist_ok=True)
    f = cart + ("/p-%02d.jpg" if src == "n" else "/p-%d.jpg") % pag
    if not os.path.exists(f):
        subprocess.run(["pdftoppm", "-jpeg", "-scale-to-x", "2000", "-scale-to-y", "-1", VOL + PDF[src], cart + "/p"], check=True)
    return f


# (src, pagina, riquadro su griglia 1000 px, prodotto, prezzo, q, descrizione[, dal, al])
R = [
# --- pagina 1
("n",1,(170,300,350,520),"Acqua",1.55,9,"Sant'Anna 6 x 1,5 l (sottocosto -50%)"),
("n",1,(460,320,670,520),"Caffè macinato",6.99,0.5,"Lavazza Qualità Rossa 2 x 250 g (sottocosto -43%)"),
("n",1,(690,320,900,600),"Detersivo lavatrice",6.49,2.295,"Dash liquido 3 pezzi, 2,295 l (sottocosto -67%)"),
("n",1,(90,580,330,670),"Spigola e orata",7.90,1,"Spigola, al kg (-43%)"),
("n",1,(510,590,700,720),"Pollo e tacchino (altri tagli)",2.99,1,"Pollo in parti senza petto, 100% italiano, al kg"),
("n",1,(100,770,260,880),"Salame",1.19,1,"Salsiccia secca Norcia Lanzi, all'etto (-40%)"),
("n",1,(330,760,480,900),"Pecorino",1.79,1,"Pecorino Romano DOP del Lazio La Quercia, all'etto (-20%)"),
("n",1,(555,780,690,880),"Piatti pronti e cereali",4.39,0.2,"Saltimbocca alla romana Nonna Lina 200 g (-20%)"),
# --- pagina 2
("n",2,(50,170,310,430),"Pizza surgelata",3.49,0.9,"Margherita Bella Napoli Buitoni 3 pz, 900 g (sottocosto -50%)"),
("n",2,(370,210,640,470),"Verdure surgelate",1.59,0.75,"Minestrone Leggerezza Orogel 750 g (sottocosto -47%)"),
("n",2,(700,250,940,440),"Ricotta",0.99,0.25,"Ricotta Vallelata 250 g (sottocosto -44%)"),
("n",2,(140,590,320,880),"Gorgonzola",1.59,2,"Gorgonzola DOP Biraghi 200 g (sottocosto -50%)"),
("n",2,(450,570,640,880),"Grana e formaggi duri",5.90,7,"GranFerrari 700 g (sottocosto -54%)"),
("n",2,(680,570,920,790),"Mozzarella",1.99,0.3,"Granarolo 100% latte italiano 3 x 100 g (sottocosto -58%)"),
# --- pagina 3
("n",3,(120,200,310,480),"Latte UHT",0.79,1,"Granarolo parzialmente scremato 1 l (sottocosto -53%)"),
("n",3,(330,250,600,440),"Yogurt",0.69,0.25,"Yomo al caffè 2 x 125 g (sottocosto -50%)"),
("n",3,(640,270,940,450),"Lasagne e cannelloni pronti",3.99,1,"Lasagna al ragù Roscio 1 kg (sottocosto -55%)"),
("n",3,(60,580,300,790),"Prosciutto cotto",2.69,2,"Bipack Firmati Rovagnati 200 g (sottocosto -60%)"),
("n",3,(340,580,610,780),"Mortadella",2.59,2.2,"Mortadella IGP Bi-Pack Beretta 220 g (sottocosto -57%)"),
("n",3,(740,600,940,830),"Pasta fresca",1.69,0.25,"Tortellini Antica Bottega Fini 250 g (sottocosto -51%)"),
# --- pagina 4
("n",4,(110,170,320,520),"Biscotti",1.59,0.5,"Gocciole Classiche Pavesi 500 g (sottocosto -45%)"),
("n",4,(350,215,610,530),"Merendine",1.69,0.3,"Muffin Mr. Day 300 g (sottocosto -45%)"),
("n",4,(730,215,940,530),"Cereali e muesli",2.39,0.4,"Coco Pops Kellogg's 400 g (sottocosto -40%)"),
("n",4,(240,640,410,880),"Confettura",3.09,0.33,"Confetture Bio Rigoni 330 g (sottocosto -36%)"),
("n",4,(620,610,880,890),"Cialde caffè",13.49,60,"Capsule compatibili Nespresso Lavazza 60 pz, 342 g (sottocosto -34%)"),
# --- pagina 5
("n",5,(70,170,360,410),"Tonno in scatola",6.59,0.56,"Rio Mare all'olio di oliva 7 x 80 g (sottocosto -45%)"),
("n",5,(500,210,610,550),"Olio extravergine di oliva",3.79,1,"Ulisse Clemente 1 l (sottocosto -40%)"),
("n",5,(780,220,900,520),"Passata di pomodoro",0.89,0.8,"Mutti 800 g (sottocosto -60%)"),
("n",5,(70,560,240,800),"Pasta di semola",0.77,0.5,"La Molisana integrale 500 g (sottocosto -51%)"),
("n",5,(350,570,470,880),"Pasta di semola",0.65,0.5,"La Molisana 500 g (sottocosto -53%)"),
("n",5,(590,590,700,880),"Pane in cassetta",0.59,0.4,"Pan Bauletto Bianco Mulino Bianco 400 g (sottocosto -54%)"),
("n",5,(760,570,910,810),"Patatine",1.65,0.3,"Patatine Rustiche San Carlo 300 g (sottocosto -49%)"),
# --- pagina 6
("n",6,(180,170,310,540),"Bibite gassate",1.59,1.5,"Coca Cola 1,5 l (sottocosto -32%)"),
("n",6,(470,210,580,600),"Birra",1.19,0.355,"Tennent's Super 355 ml (sottocosto -39%)"),
("n",6,(740,210,900,550),"Birra",0.79,0.5,"Heineken Original 500 ml (sottocosto -47%)"),
("n",6,(190,590,370,900),"Riso",2.09,1,"Riso Arborio Scotti 1 kg (sottocosto -53%)"),
# --- pagina 7
("n",7,(160,170,290,540),"Prosecco",2.49,0.75,"Prosecco DOC Extra Dry Velodoro 750 ml (sottocosto -36%)"),
("n",7,(450,190,560,540),"Vino rosso",2.59,0.75,"Chianti Riserva DOCG Piccini 750 ml (sottocosto -57%)"),
("n",7,(690,210,900,490),"Birra",2.89,1.98,"Peroni 6 x 330 ml (sottocosto -48%)"),
("n",7,(140,580,250,900),"Bibite gassate",0.85,1.2,"San Pellegrino aranciata 1,2 l (sottocosto -45%)"),
("n",7,(300,590,580,780),"Detersivo lavatrice (al lavaggio)",4.89,21,"Dixan Discs 21 lavaggi, 347 g (sottocosto -48%)"),
("n",7,(730,580,880,910),"Ammorbidente",3.75,1.827,"Lenor concentrato 87 lavaggi, 1,827 l (sottocosto -53%)"),
# --- pagina 8
("n",8,(80,190,370,460),"Asciugatutto",1.79,2,"Scottex Tuttofare 2 rotoli (sottocosto -37%)"),
("n",8,(630,230,930,400),"Dentifricio",1.69,0.075,"Colgate Sensation White 75 ml (sottocosto -48%)"),
("n",8,(180,590,310,900),"Bagnoschiuma",1.69,0.6,"Bagnodoccia Neutromed 600 ml (sottocosto -56%)"),
("n",8,(460,610,580,900),"Shampoo e balsamo",2.15,0.25,"Shampoo Pantene 250 ml (sottocosto -49%)"),
("n",8,(650,520,910,790),"Carta igienica",2.89,12,"Regina Rotoloni 4 rotoli = 12 rotoli standard (sottocosto -28%)"),
# --- pagina 9
("n",9,(110,590,290,870),"Lettiera per gatti",3.74,10,"Sanicat Classic profumo di lavanda 10 l (sottocosto -42%)"),
# --- pagina 10 carne
("n",10,(60,100,275,180),"Bovino (tagli vari)",12.95,1,"Fracosta con osso di vitella, al kg"),
("n",10,(285,100,500,180),"Hamburger",12.95,1,"Hamburger di vitella, al kg"),
("n",10,(540,90,730,185),"Salsiccia di suino",5.99,1,"Salsiccia di suino al finocchio, al kg (-25%)"),
("n",10,(750,100,965,185),"Pollo e tacchino (altri tagli)",2.99,1,"Ali di pollo 100% italiano, al kg (-40%)"),
("n",10,(50,270,270,340),"Petto di pollo a fette",8.95,1,"Petto di pollo a fette, confezione risparmio, al kg"),
("n",10,(290,270,500,350),"Cosce e fusi di pollo",3.99,1,"Cosciotto di pollo 100% italiano, al kg"),
("n",10,(515,280,735,355),"Suino (altri tagli)",4.95,1,"Spuntature di suino, al kg (-44%)"),
("n",10,(750,290,965,370),"Hamburger",5.35,0.6,"Hamburger misti di suino 6 pz, 600 g (-33%)"),
("n",10,(55,445,275,500),"Hamburger",19.95,1,"Miniburger di Chianina Terre d'Italia, al kg"),
("n",10,(285,465,500,520),"Cotolette e panati di pollo",3.59,0.3,"Linea Panati Aia (es. La Viennese) 300 g (-40%)"),
("n",10,(590,430,920,500),"Petto di pollo a fette",9.95,1,"Filettini di pollo 100% italiano, al kg (-40%)"),
("n",10,(110,610,270,690),"Braciole di suino",4.95,1,"Braciole di collo di suino 100% italiano, al kg (-50%)"),
("n",10,(290,615,500,690),"Bovino (tagli vari)",15.85,1,"Bocconcini di scottona, al kg"),
("n",10,(530,600,730,690),"Bovino (tagli vari)",16.95,1,"Arrosto di scottona, al kg"),
("n",10,(750,620,950,690),"Bovino (tagli vari)",16.95,1,"Fettine sceltissime di scottona, al kg (-22%)"),
("n",10,(65,780,280,860),"Arista e lombo di suino",7.95,1,"Sottilissime di lombo, al kg (-43%)"),
("n",10,(290,790,500,860),"Suino (altri tagli)",9.99,0.6,"Ribs di suino Aia lenta cottura BBQ o rosmarino 600 g (-35%)"),
("n",10,(530,780,730,850),"Bovino (tagli vari)",17.95,1,"Tagliata di scottona, al kg (-21%)"),
("n",10,(750,810,965,870),"Bovino (tagli vari)",3.89,0.12,"Arrosticini di Black Angus o Chianina 120 g (-35%)"),
# --- pagina 11 gastronomia
("n",11,(130,70,290,200),"Provola, scamorza e provolone",1.59,1,"Provolone piccante Auricchio, all'etto (-22%)"),
("n",11,(335,70,470,175),"Caciotta e formaggi semiduri",1.19,1,"Asiago DOP Terre d'Italia, all'etto (-20%)"),
("n",11,(575,80,705,185),"Grana e formaggi duri",1.19,1,"Grana Padano DOP Stagionatura oltre 16 mesi, all'etto (-35%)"),
("n",11,(765,80,960,160),"Formaggi freschi e latticini vari",1.29,0.1,"Brie President, all'etto (-26%)"),
("n",11,(80,250,260,390),"Gorgonzola",0.89,1,"Gorgonzola DOP, all'etto"),
("n",11,(310,300,470,365),"Mozzarella",3.37,0.25,"Mozzarella e bocconcini di Bufala Campana DOP Terre d'Italia 250 g (-25%)"),
("n",11,(530,250,700,370),"Caciotta e formaggi semiduri",0.79,1,"Maasdam, al kg 7,90 (all'etto 0,79)"),
("n",11,(805,250,960,330),"Pane e panini",2.50,0.28,"Panini al latte 8 pezzi, 280 g (-26%)"),
("n",11,(140,455,255,560),"Caciotta e formaggi semiduri",1.17,1,"Caciotta Giulietta Sini Formaggi, all'etto (-30%)"),
("n",11,(330,450,470,540),"Pecorino",1.79,1,"Pecorino d'Abruzzo De Remigis, all'etto (-20%)"),
("n",11,(580,455,710,540),"Caciotta e formaggi semiduri",1.91,1,"Formaggio Artigiano Sini, all'etto (-20%)"),
("n",11,(810,455,940,545),"Caciotta e formaggi semiduri",1.39,1,"Caciotta di Norcia Grifo Latte, all'etto (-30%)"),
("n",11,(125,590,255,710),"Caciotta e formaggi semiduri",1.34,1,"Casciotta della Duchessa Val D'Apsa, all'etto (-25%)"),
("n",11,(355,590,485,700),"Caciotta e formaggi semiduri",1.27,1,"Caciotta Dolce Cassia Sini, all'etto (-20%)"),
("n",11,(590,590,710,700),"Caciotta e formaggi semiduri",1.27,1,"Formaggio Il Casaro I Buona Tavola Sini, all'etto (-20%)"),
("n",11,(790,595,945,680),"Ricotta",3.19,0.35,"Ricotta Gentile senza lattosio Boccea 350 g (-20%)"),
("n",11,(75,785,235,850),"Grana e formaggi duri",2.69,1,"Cacio e Pepe grattugiato Sini 100 g"),
("n",11,(600,760,720,900),"Pinsa",3.75,0.46,"Pinsa romana Nuvola Di Marco 460 g (-24%)"),
("n",11,(780,770,945,850),"Torte e dolci da forno",4.11,0.5,"Crostate Gargani 500 g (-25%)"),
# --- pagina 12 salumi
("n",12,(90,80,265,170),"Salame piccante",1.75,1,"Spianata Romana Fiorucci, all'etto (-20%)"),
("n",12,(345,95,505,200),"Prosciutto cotto",1.49,1,"Prosciutto cotto alta qualità Parmacotto, all'etto (-25%)"),
("n",12,(90,235,265,340),"Salame",1.59,1,"Salamini Picnic, all'etto (-20%)"),
("n",12,(340,255,500,340),"Salame",1.49,1,"Salame Ungherese Fiorucci, all'etto (-21%)"),
("n",12,(50,415,270,530),"Speck",1.59,1,"Speck Alto Adige, al kg 15,90 (-20%)"),
("n",12,(320,415,500,525),"Mortadella",1.49,1,"Mortadella Favola Palmieri, all'etto (-25%)"),
("n",12,(95,590,270,690),"Salumi affettati assortiti",1.49,1,"Porchetta al forno, all'etto (-21%)"),
("n",12,(600,115,740,195),"Guanciale e pancetta",1.83,1,"Trancio di pancetta tesa affumicata Sorrentino, all'etto (-20%)"),
("n",12,(850,115,960,195),"Salumi affettati assortiti",3.49,1,"Culatta stagionata Sorrentino, all'etto (-20%)"),
("n",12,(600,255,720,345),"Salame",1.35,1,"Salamella romana Sorrentino, all'etto (-20%)"),
("n",12,(850,250,965,340),"Guanciale e pancetta",3.19,1,"Pancetta arrotolata affettata Ghiotto 100 g (-20%)"),
("n",12,(600,420,720,505),"Coppa e capocollo",2.07,1,"Coppa stagionata Sorrentino, all'etto (-20%)"),
("n",12,(850,440,965,525),"Prosciutto crudo",3.99,1,"Prosciutto crudo affettato stagionatura 20 mesi Ghiotto 100 g (-20%)"),
("n",12,(630,765,740,925),"Gnocchi",3.49,0.5,"Gnocchetti tricolore 500 g"),
# --- pagina 13 pesce e ortofrutta
("n",13,(285,95,420,175),"Gamberi e mazzancolle",16.90,1,"Gamberi argentini decongelati, al kg (-26%)"),
("n",13,(515,100,710,170),"Calamari e totani",19.90,1,"Calamaro fresco, al kg (-20%)"),
("n",13,(745,95,960,165),"Altro pesce",12.90,1,"Filetto di brosme, al kg (-23%)"),
("n",13,(45,290,265,355),"Altro pesce",19.90,1,"Trancio di pesce spada decongelato, al kg (-31%)"),
("n",13,(325,280,470,355),"Altro pesce",29.90,1,"Filetto di baccalà dissalato 700/1000 g, al kg (-21%)"),
("n",13,(595,250,690,350),"Alici e acciughe",1.95,0.08,"Alici Rustic Rizzoli 80 g (-24%)"),
("n",13,(840,250,910,400),"Salmone affumicato",6.90,0.23,"Salmone affumicato norvegese Riunione 230 g (-30%)"),
("n",13,(90,440,235,530),"Filetti di sgombro",5.50,0.15,"Filetto sgombro affumicato Excelsior 150 g"),
("n",13,(290,430,500,510),"Cachi",2.80,1,"Cachi Persimon sfusi, al kg (-25%)"),
("n",13,(515,430,700,520),"Mele",2.06,1,"Mele Annurche IGP, al kg (-20%)"),
("n",13,(740,455,930,520),"Mele",2.40,0.9,"Mele Envy 900 g (-20%)"),
("n",13,(105,595,265,680),"Arance",1.67,1.5,"Arance Navel 1,5 kg (-30%)"),
("n",13,(335,600,485,690),"Patate",1.70,1.5,"Patate di Bologna DOP Terre d'Italia 1,5 kg (-20%)"),
("n",13,(510,595,700,690),"Verdure fresche varie",1.50,1,"Cavolfiore sfuso, al kg (-20%)"),
("n",13,(755,620,945,760),"Castagne e marroni",3.00,1,"Castagne sfuse, al kg (-30%)"),
("n",13,(60,765,215,850),"Zucchine",2.00,1,"Zucchine sfuse, al kg (-20%)"),
("n",13,(320,775,480,860),"Broccoli e verdure a foglia",1.00,1,"Broccolo romanesco sfuso, al kg"),
("n",13,(580,770,710,860),"Olive",2.80,0.25,"Olive Novelle Madama Oliva 250 g (-20%)"),
# --- pagina 14
("n",14,(60,80,265,350),"Grana e formaggi duri",4.98,2.4,"Parmigiano Reggiano grattugiato Virgilio 24 mesi, 3 x 80 g (3x2)"),
("n",14,(375,115,480,235),"Mozzarella",1.79,0.15,"Ciliegine Nonno Nanni 150 g (-23%)"),
("n",14,(600,80,710,190),"Formaggi freschi e latticini vari",2.19,0.19,"Primosale Linea Osella 190 g (-31%)"),
("n",14,(795,85,950,180),"Formaggio spalmabile",0.99,0.175,"Formaggio fresco cremoso Exquisa 175 g (-44%)"),
("n",14,(375,250,500,360),"Prosciutto crudo",2.69,1,"Prosciutto crudo dolce Parmacotto 100 g (-27%)"),
("n",14,(610,250,720,400),"Speck",1.99,0.7,"Sticks di speck Handl 70 g (-20%)"),
("n",14,(790,280,950,340),"Salame",3.99,2.2,"Salame Negronetto Negroni 220 g (-30%)"),
("n",14,(290,475,500,500),"Pasta sfoglia e basi",1.45,0.23,"Pasta sfoglia rettangolare Buitoni 230 g (-38%)"),
("n",14,(630,420,720,545),"Burger e alternative vegetali",1.99,0.2,"Mini burger vegetale agli spinaci Kioene 200 g (-32%)"),
("n",14,(830,420,960,535),"Pesto",1.19,0.14,"Pesto fresco senza aglio Biffi 140 g (-55%)"),
("n",14,(160,600,275,710),"Pizza surgelata",1.99,0.32,"Pizza Cameo Ristorante 320 g (-50%)"),
("n",14,(385,590,500,750),"Piatti pronti e cereali",4.49,0.5,"Cotechino IGP Casa Modena 500 g (-35%)"),
("n",14,(590,590,720,690),"Cotolette e panati di pollo",1.99,0.24,"Nuggets di pollo o spinacine Aia 240 g (-50%)"),
("n",14,(850,590,965,700),"Verdure surgelate",2.79,0.4,"Tris grigliato Gusto Ricco Orogel 400 g (-34%)"),
("n",14,(195,795,275,910),"Guanciale e pancetta",1.27,1,"Trancio di guanciale pepe o peperoncino Lattanzi, all'etto (-20%)"),
("n",14,(350,805,500,862),"Uova",2.79,10,"Uova antibiotic free 10 pz, 500 g (-20%)"),
("n",14,(650,800,780,875),"Mozzarella",2.99,0.25,"Fior di latte Caseificio Di Pasquo 250 g (-20%)"),
("n",14,(865,805,965,870),"Burro",2.39,0.25,"Burro Fattoria Latte Sano 250 g (-30%)"),
# --- pagina 15
("n",15,(110,90,250,180),"Filetti di merluzzo",4.25,0.4,"Filetti di merluzzo sudafricano surgelati 400 g (-20%)"),
("n",15,(350,100,690,230),"Bastoncini e croccanti di pesce",3.59,0.9,"30 bastoncini di merluzzo Ocean Catch 900 g (-20%)"),
("n",15,(840,80,960,190),"Patatine surgelate",1.59,0.75,"We Love Croccanti o Extrafini Pizzoli 750 g (-38%)"),
("n",15,(40,290,260,500),"Piadina",4.79,1.2,"Piadina Romagnola IGP alla Riminese 1+1 Riccione 1,2 kg (-50%)"),
("n",15,(345,255,445,320),"Bastoncini e croccanti di pesce",3.49,0.36,"Filetto di merluzzo gratinato con patate Frosta 360 g (-34%)"),
("n",15,(580,265,700,400),"Verdure surgelate",1.79,0.6,"Spinaci in foglia 600 g (-21%)"),
("n",15,(810,255,950,370),"Formaggio spalmabile",1.69,0.175,"Fiocchi cremosi Jocca 175 g (-28%)"),
("n",15,(330,420,480,520),"Formaggio spalmabile",1.49,0.165,"Certosa Galbani 165 g (-34%)"),
("n",15,(545,425,700,530),"Formaggi freschi e latticini vari",1.69,0.25,"Mascarpone Polenghi 250 g"),
("n",15,(830,425,950,525),"Formaggio a fette",1.89,1.25,"Fette Special Toast Leerdammer 125 g (-29%)"),
("n",15,(150,625,260,690),"Mozzarella",2.99,0.3,"Fior di latte Centrale Latte Roma 300 g (-25%)"),
("n",15,(370,620,495,700),"Stracchino, crescenza e robiola",1.29,0.1,"Robiola Centrale Latte Roma 100 g (-25%)"),
("n",15,(620,620,720,720),"Mozzarella",6.90,0.5,"Mozzarella di Bufala vaso Cuomo 500 g (-20%)"),
("n",15,(850,625,910,710),"Lasagne e cannelloni pronti",3.49,0.5,"Cannelloni Buongusto 500 g (-40%)"),
("n",15,(140,765,240,880),"Gnocchi",1.49,1,"Gnocchi di patate Il Buon Gusto in Tavola Eurotortellino 1 kg (-40%)"),
("n",15,(375,770,500,880),"Pasta all'uovo",1.49,0.45,"Tagliolini, fettuccine o tonnarelli Valleoro 450 g"),
("n",15,(575,765,720,900),"Filetti di merluzzo",6.79,1,"Filetti di merluzzo Atlantico surgelati 1 kg (-20%)"),
("n",15,(810,780,950,900),"Altro pesce",7.99,0.5,"Pesce spada in tranci Pescanova surgelato 500 g (-20%)"),
# --- pagina 16
("n",16,(95,125,260,340),"Yogurt",1.29,0.5,"Crema di yogurt Müller 500 g (-31%)"),
("n",16,(360,80,495,180),"Yogurt",0.89,0.15,"Danone Skyr bianco 150 g (-35%)"),
("n",16,(620,80,720,190),"Kefir",1.99,0.5,"Milk Kefir Plus bianco cereali 4 x 125 g (-26%)"),
("n",16,(830,80,960,180),"Kefir",1.09,0.16,"Milk Kefir anelli di cioccolato 160 g (-25%)"),
("n",16,(580,260,720,340),"Burro",1.99,0.25,"Burro Latteria Soresina 250 g (-45%)"),
("n",16,(820,260,960,350),"Uova",1.79,6,"Uova fresche bianche da terra Le Naturelle 6 pz, 300 g (-20%)"),
("n",16,(145,440,280,580),"Lasagne e cannelloni pronti",2.75,0.35,"Lasagna alla Bolognese monoporzione 350 g (-20%)"),
("n",16,(370,440,500,580),"Funghi porcini",5.59,0.3,"Funghi porcini a fette Bosco Reale surgelati 300 g (-20%)"),
("n",16,(580,420,725,530),"Verdure surgelate",1.99,0.24,"Tortini di spinaci Frosta 240 g (-26%)"),
("n",16,(860,420,960,520),"Pasta fresca",2.39,0.28,"Cuor di Sugo Rana 280 g (-40%)"),
("n",16,(180,625,270,700),"Latte UHT",0.79,0.5,"Latte alta qualità UHT intero Centrale Latte Roma 500 ml (-33%)"),
("n",16,(385,630,500,700),"Yogurt",1.39,0.25,"Yogurt intero bio Centrale Latte Roma 250 g (-35%)"),
("n",16,(660,620,730,740),"Panna",3.99,0.5,"Panna fresca Centrale Latte Roma 500 g (-30%)"),
("n",16,(855,615,965,715),"Zuppe surgelate",1.99,0.6,"Vellutata Carrefour 600 g (-23%)"),
("n",16,(370,780,500,880),"Supplì e mozzarella in carrozza",2.69,0.5,"Garbo Happy Mix 500 g (-32%)"),
("n",16,(630,775,730,860),"Verdure surgelate",2.59,0.6,"Pisellini Finissimi Orogel Dolce Italia 600 g (-23%)"),
("n",16,(850,775,960,860),"Verdure surgelate",2.39,0.3,"Carciofi in spicchi Orogel 300 g (-37%)"),
# --- pagina 17
("n",17,(90,100,250,175),"Wafer",2.79,0.225,"Wafer Loacker 225 g (-25%)"),
("n",17,(375,100,480,230),"Biscotti",1.99,0.4,"Crostatine cacao o albicocca Mulino Bianco 400 g (-25%)"),
("n",17,(115,250,250,350),"Snack al cioccolato",1.59,0.12,"Barrette Coco Pops 120 g (-25%)"),
("n",17,(315,270,500,350),"Biscotti",1.49,0.3,"Savoiardi Vicenzovo 300 g (-25%)"),
("n",17,(630,250,710,380),"Bevanda vegetale",1.99,1,"Latte d'avena integrale o mandorla Intensa Bjorg 1 l (-33%)"),
("n",17,(795,255,945,345),"Biscotti",2.49,0.8,"Granturchese Colussi 800 g (-30%)"),
("n",17,(75,440,250,510),"Merendine",2.99,0.36,"Fiesta Ferrero 360 g (-20%)"),
("n",17,(320,430,500,520),"Biscotti",2.45,0.33,"Ringo Famiglia vaniglia o cacao 330 g (-25%)"),
("n",17,(590,420,715,525),"Yogurt",1.49,0.2,"Hipro Pudding caramello 200 g (-23%)"),
("n",17,(100,600,250,690),"Fette biscottate",1.49,0.32,"Fette biscottate Misura 320 g (-25%)"),
("n",17,(375,590,490,740),"Crema alla nocciola",6.49,0.95,"Nutella 950 g"),
("n",17,(620,590,715,745),"Panna",1.89,0.5,"HuLaLà panna da montare 500 ml (-20%)"),
("n",17,(780,600,950,690),"Yogurt",2.69,0.6,"Yogurt bianco Müller Mix anelli o fiocchi di cioccolato 4 pz, 600 g (-31%)"),
("n",17,(650,760,710,900),"Succo di frutta",1.35,1,"Succhi di frutta Santal 1 l (-30%)"),
("n",17,(840,760,950,920),"Caffè solubile",3.75,0.14,"Cappuccino Nescafé Gold 140 g"),
# --- pagina 18-19 cioccolato e Natale
("n",18,(220,590,470,755),"Tavolette di cioccolato",2.29,0.085,"Tavolette Nero Perugina 85 g (-20%)"),
("n",18,(640,590,900,755),"Tavolette di cioccolato",2.89,0.1,"Tavolette Lindt Lindor 100 g (-20%)"),
("n",18,(150,775,470,925),"Tavolette di cioccolato",1.99,0.075,"Tavolette Ritter Sport 75 g (-20%)"),
("n",18,(640,765,710,925),"Tavolette di cioccolato",3.09,0.1,"Tavolette Cioccolato di Modica IGP Terre d'Italia 100 g (-20%)"),
("n",18,(780,765,960,880),"Tavolette di cioccolato",1.99,0.1,"Tavolette Novi 100 g (-30%)"),
("n",19,(210,420,420,590),"Panettone e pandoro",8.49,0.75,"Pandoro Melegatti impasto pistacchio o cacao con frutti rossi 750 g (-20%)"),
("n",19,(660,420,900,590),"Panettone e pandoro",3.89,0.75,"Il Pandoro, il Panettone o il Panettone senza canditi Maina 750 g (-35%)"),
("n",19,(700,160,940,400),"Panettone e pandoro",0.99,0.08,"Mini Pandoro, Mini Panettone classico o gocce cioccolato GS 80 g (-35%)"),
("n",19,(210,70,430,235),"Panettone e pandoro",2.49,0.09,"Mini Panettoncino gocce cioccolato Paw Patrol o Mini Pandorino Winx Balocco 90 g (-20%)"),
("n",19,(620,590,900,690),"Torrone",0.99,0.075,"Torrone mandorla morbido o friabile Casa Regale 75 g (-20%)"),
("n",19,(170,595,420,745),"Cioccolatini e praline",5.49,0.2,"Ferrero Rocher 16 pezzi, 200 g (-20%)"),
("n",19,(225,765,410,925),"Tavolette di cioccolato",1.69,0.1,"Tavolette Special Nuts Ritter Sport 100 g (-30%)"),
# --- pagina 20 alimentari confezionati
("n",20,(100,100,245,330),"Passata di pomodoro",0.55,0.4,"Polpa di pomodoro Napolina 400 g (-60%)"),
("n",20,(395,80,480,240),"Olio di oliva",3.99,1,"Olio di oliva Bertolli 1 l (-60%)"),
("n",20,(620,80,700,240),"Olio extravergine di oliva",4.99,1,"Olio extravergine Pantaleo 100% italiano 1 l (-50%)"),
("n",20,(900,80,965,240),"Olio extravergine di oliva",10.00,1,"Olio extravergine Grezzo Doli 100% italiano 1 l (-20%)"),
("n",20,(365,250,500,345),"Passata di pomodoro",1.49,0.8,"Polpa Petti 2 x 400 g (-44%)"),
("n",20,(620,250,710,360),"Sugo pronto",1.79,0.3,"Ragù Barilla 300 g (-38%)"),
("n",20,(855,250,945,405),"Maionese, ketchup e salse",2.19,0.49,"Maionese in vaso Kraft 490 ml (-36%)"),
("n",20,(115,435,260,510),"Tonno in scatola",5.75,0.2,"Tonno Consorcio 2 x 100 g (-45%)"),
("n",20,(405,425,505,550),"Pesto",2.49,0.13,"Pesto al tonno Rio Mare 130 g (-21%)"),
("n",20,(550,455,730,520),"Filetti di sgombro",2.39,0.12,"Sgombri grigliati Rio Mare 120 g"),
("n",20,(805,435,965,515),"Conserve di verdura e frutta",1.95,0.375,"Fagioli rossi Bonduelle 3 x 125 g (-23%)"),
("n",20,(150,600,255,745),"Patatine",1.75,0.3,"Patatine classiche Amica Chips 300 g (-35%)"),
("n",20,(410,590,470,750),"Patatine",1.85,0.175,"Pringles 175 g"),
("n",20,(625,590,735,700),"Crackers",1.59,0.56,"Crackers Gran Pavesi salati o senza sale 560 g (-40%)"),
("n",20,(845,595,965,745),"Zuppe pronte e noodles",1.19,0.06,"Saikebon Manzo cup 60 g (-25%)"),
("n",20,(650,770,740,925),"Conserve di verdura e frutta",3.29,0.54,"Melanzane saporite ortoCori 540 g"),
("n",20,(860,765,950,860),"Sugo pronto",4.89,0.18,"Sughi pronti Doli 180 g (-20%)"),
# --- pagina 21 bevande
("n",21,(160,80,250,235),"Bevande energetiche",1.19,0.5,"Monster Energy Drink 500 ml (-32%)"),
("n",21,(370,100,480,200),"Acqua",1.59,3,"Levissima 6 x 500 ml, 3 l (-32%)"),
("n",21,(620,75,700,240),"Tè freddo",0.69,1.5,"SanThè Sant'Anna limone o pesca 1,5 l (-46%)"),
("n",21,(890,80,945,240),"Birra",1.49,0.33,"Leffe blonde, triple, rouge o ambrée 330 ml (-25%)"),
("n",21,(160,250,240,405),"Birra",1.09,0.33,"Corona Extra 330 ml (-26%)"),
("n",21,(380,250,490,370),"Birra",5.39,3.96,"Birra Moretti 6 x 66 cl (-40%)"),
("n",21,(660,250,700,410),"Vino rosso",2.99,0.75,"Montepulciano d'Abruzzo DOC Spinelli 750 ml (-30%)"),
("n",21,(890,245,945,410),"Prosecco",4.49,0.75,"Spumante Blanc de Blancs Oro Valdo 750 ml (-38%)"),
("n",21,(145,420,190,580),"Vino bianco",2.79,0.75,"Le Morre Sicilia 750 ml (-55%)"),
("n",21,(385,420,440,580),"Vino bianco",5.99,0.75,"Roero Arneis DOCG Duchessa Lia 750 ml (-25%)"),
("n",21,(670,455,710,580),"Vino bianco",2.59,0.75,"Donna Circe Lazio IGP Bianco Vivace Cantina Villa Gianna 750 ml (-30%)"),
("n",21,(870,455,900,580),"Vino rosso",2.29,0.75,"Gran Picco Castelli Romani DOC Rosso San Marco 750 ml"),
("n",21,(200,590,240,720),"Vino rosso",4.39,0.75,"Barbera d'Asti DOCG Duchessa Lia 750 ml (-20%)"),
("n",21,(420,590,460,750),"Vino bianco",4.49,0.75,"Vermentino Aragosta DOC Santa Maria La Palma 750 ml (-26%)"),
("n",21,(610,590,650,750),"Amari e liquori",6.99,0.5,"Limoncello Pallini 500 ml (-21%)"),
("n",21,(860,590,945,750),"Superalcolici",6.99,0.7,"Gin Star al pompelmo rosa 700 ml"),
("n",21,(200,760,260,895),"Prosecco",2.49,0.75,"Spumante Rocca dei Forti rosé, brut o dolce 750 ml (-35%)"),
("n",21,(400,760,445,925),"Amari e liquori",9.99,0.7,"Amaro Braulio 700 ml"),
("n",21,(600,765,710,880),"Acqua",1.19,3,"Acqua effervescente naturale Egeria 6 x 500 ml, 3 l (-30%)"),
("n",21,(850,765,900,900),"Vino rosato",5.49,0.75,"Merlot Rosè IGT Terre d'Abruzzo Citra 750 ml (-21%)"),
# --- pagina 22 casa e persona
("n",22,(630,80,730,210),"Detersivo piatti",1.79,1,"Vert 500 ml, 1+1 gratis (2 pezzi 1,79 €)"),
("n",22,(390,260,460,410),"Sapone",1.19,0.3,"Sapone liquido Felce Azzurra 300 ml (-43%)"),
("n",22,(160,250,240,400),"Deodorante",2.99,0.15,"Deodorante spray o roll on Borotalco 150 ml (-33%)"),
("n",22,(150,80,280,235),"Detergente intimo",3.49,0.3,"Detergente intimo Chilly 300 ml (-30%)"),
("n",22,(600,590,740,700),"Carta igienica",1.99,4,"Regina Sensation 4 rotoli (-42%)"),
("n",22,(900,590,965,750),"Detergente spray",1.69,0.65,"Spray Vetril 650 ml (-40%)"),
("n",22,(370,810,500,880),"Umido per gatto",2.49,0.34,"Gourmet Perle Purina 4 pz, 340 g"),
("n",22,(900,810,965,880),"Crocchette per cane",3.85,1.5,"Friskies Nutrisoft Purina 1,5 kg (-24%)"),
# --- pagina 25 prodotti per i piu' piccoli
("n",25,(130,100,330,215),"Omogeneizzati",1.05,0.2,"Omogeneizzato alla frutta Mellin 2 x 100 g (-27%)"),
("n",25,(430,100,640,215),"Omogeneizzati",1.49,0.16,"Omogeneizzato alla carne Nipiol 2 x 80 g (-28%)"),
# --- pagina 29 animali
("n",29,(305,90,445,205),"Umido per gatto",2.09,0.28,"Ultima Affinity 4 pz, 280 g"),
("n",29,(575,100,670,200),"Umido per gatto",1.00,0.085,"Adoc 85 g (-23%)"),
("n",29,(355,300,500,450),"Crocchette per gatto",1.99,0.44,"Ultima Affinity secco 440 g (-35%)"),
("n",29,(590,320,705,480),"Snack per gatti",1.09,0.06,"Catisfactions 60 g (-24%)"),
("n",29,(755,95,915,360),"Crocchette per gatto",3.96,2,"Crocchette per gatti Carrefour 2 kg (-11%)"),
("n",29,(125,440,270,650),"Crocchette per cane",8.15,3,"Special Dog Excellence Monoprotein manzo 3 kg (-23%)"),
("n",29,(445,500,610,690),"Snack per cani",1.16,0.115,"Dentalife Purina medium o small 115 g (-20%)"),
("n",29,(785,530,930,650),"Umido per cane",0.79,0.15,"Cesar 150 g (-33%)"),
("n",29,(135,725,255,900),"Snack per gatti",1.15,0.06,"Felix Party Mix 60 g (-25%)"),
("n",29,(395,730,520,900),"Umido per cane",0.70,0.4,"Special Dog Monge 400 g (-30%)"),
("n",29,(805,715,930,900),"Crocchette per cane",5.40,2.5,"Miglior Cane Morando 2,5 kg (-28%)"),
# --- pagina 30 promo flash (6-8 nov e 12-15 nov)
("n",30,(180,170,450,260),"Hamburger",11.95,1,"Hamburger di scottona, al kg (Promo Flash 6-8 novembre)","2026-11-06","2026-11-08"),
("n",30,(235,285,470,400),"Gamberi e mazzancolle",19.90,1,"Coda di mazzancolla tropicale sgusciata, al kg (Promo Flash 6-8 novembre)","2026-11-06","2026-11-08"),
("n",30,(570,170,720,270),"Pecorino",1.99,1,"Pecorino Nero stagionato Pinzani, all'etto (Promo Flash 12-15 novembre)","2026-11-12","2026-11-15"),
("n",30,(790,165,910,260),"Prosciutto crudo",7.99,1.6,"Prosciutto di Carpegna DOP bipack 160 g (Promo Flash 12-15 novembre)","2026-11-12","2026-11-15"),
# --- Speciale detersivi (carrefour_3, zona N+L)
("c3",2,(280,110,470,520),"Anticalcare",5.19,0.75,"Calgon Power Gel 4in1 anticalcare detergente per lavatrice 750 ml (-20%)"),
("c3",2,(690,110,860,520),"Anticalcare",5.19,0.75,"Calgon Power Gel 4in1 anticalcare disinfettante per lavatrice 750 ml (-20%)"),
("c3",2,(280,760,460,1060),"Additivi e smacchiatori lavatrice",2.99,1,"Sole Curalavatrice Regular Extra Care 250 ml"),
("c3",2,(690,580,880,1060),"Detersivo piatti",2.99,1.1,"Sole detersivo per stoviglie Limone 1100 ml"),
# --- Speciale Aia, periodo 23 ott - 15 nov (carrefour_2, zona N+L)
("c2",2,(70,215,300,335),"Wurstel",1.99,0.28,"Aia Wudy Crunchy Pops 20 mini würstel panati 280 g (-39%)"),
("c2",2,(400,225,580,330),"Salsiccia di suino",3.99,0.3,"Aia Negronetta salsiccia fresca luganega di suino 300 g (-27%)"),
("c2",2,(715,220,870,330),"Salsiccia di suino",3.99,0.4,"Aia Punta di Coltello salsiccia fresca di suino 400 g (-33%)"),
("c2",2,(170,430,330,640),"Hamburger di pollo e tacchino",3.99,0.4,"Aia Hamburger classico di tacchino con rosmarino o di pollo 400 g (-49%)"),
("c2",2,(480,440,610,640),"Cosce e fusi di pollo",6.39,1,"Aia pollo fusi, sovracosce, al kg (-30%)"),
("c2",2,(765,470,935,600),"Petto di pollo a fette",11.79,1,"Aia pollo filetto a fette, al kg (-25%)"),
("c2",2,(180,670,420,880),"Hamburger",6.49,0.68,"Aia BonRoll classico, ripieno con spinaci o con speck 680 g (-44%)"),
("c2",2,(540,720,690,830),"Pollo e tacchino (altri tagli)",4.89,0.3,"Aia Chicken Salad tagliata di petti di pollo 300 g (-30%)"),
("c2",2,(730,725,920,830),"Pollo e tacchino (altri tagli)",4.89,0.3,"Aia Kebab di pollo tagliato in sfoglie 300 g (-23%)"),
("c2",2,(230,975,380,1075),"Cotolette e panati di pollo",2.99,0.265,"Aia Cordon Bleu classico con cotto di tacchino e formaggio 265 g (-25%)"),
("c2",2,(560,975,680,1075),"Cotolette e panati di pollo",2.99,0.2,"Aia Valdostana cotoletta di filetti di pollo impanati con scamorza affumicata 200 g (-28%)"),
("c2",2,(775,975,885,1075),"Cotolette e panati di pollo",2.99,0.24,"Aia Chicken Crunchy Burger hamburger impanato di pollo 240 g (-33%)"),
]

d = L.carica(PERC)
# idempotenza: toglie le offerte di questo volantino gia' inserite (zone N/NL, dal 6/11 in poi) e le Carrefour N scadute
prima = len(d["offerte"])
d["offerte"] = [o for o in d["offerte"] if not (o["s"] == "carrefour" and (
    (o["z"] in ("N", "NL") and o["dal"] >= D1) or (o["z"] == "N" and o["al"] < D1)))]
print("tolte", prima - len(d["offerte"]), "offerte carrefour N/NL scadute o gia' inserite")

cache = {}
for riga in R:
    src, pag, box, prod, prezzo, q, desc = riga[:7]
    dal, al = (riga[7], riga[8]) if len(riga) > 7 else (D1, AL)
    p = L.trova_prodotto(d, prod)
    assert p, "prodotto mancante: " + prod
    f = pagina(src, pag)
    im = cache.setdefault(f, Image.open(f).convert("RGB"))
    foto = L.ritaglia(im, tuple(2 * v for v in box))
    L.aggiungi_offerta(d, p["id"], "carrefour", prezzo, q, desc, "N" if src == "n" else "NL", dal, al, 0, foto)

usati = {o["p"] for o in d["offerte"]}
d["prodotti"] = [p for p in d["prodotti"] if p["id"] in usati]
L.salva(d, PERC)
print(len(R), "offerte carrefour inserite;", len(d["prodotti"]), "prodotti;", len(d["offerte"]), "offerte totali")
