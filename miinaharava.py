import haravasto as ha
import pyglet
from haravasto import NAPIT
import json
import time
import random

#fontin lataaminen
pyglet.font.add_file("pressstart2p.ttf")


tila = {
    "aika": 0,
    "aloitus_aika": 0,
    "pysaytetty_aika": 0
}

kasittelijat = {
    "piirto": None,
    "hiiri": None,
    "nappain": None,
    "toistuvat": [],
}

kysely = {
    "nykyinen_kysymys": 0,
    "huomautukset": 0,
    "kayttajan_teksti": "",
    "kohdistin_nakyy": True,
}

kentan_tiedot = {
    "leveys": 0,
    "korkeus": 0,
    "miinat": 0
}

kysymykset = {
     0: "Anna kentän leveys ruutuina: ",
     1: "Anna kentän korkeus ruutuina: ",
     2: "Anna miinojen määrä: ",
     3: "Kentän tiedot",
}

tilastot = {
    "pvm": 0,
    "klo": 0,
    "kesto_min": 0,
    "kesto_vuoro": 0,
    "tulos": None,
    "kentän_koko": 0,
    "miinat": 0,
}

peli = {
    "kentta": [],
    "avaamattomat": [],
    "avatut": [],
    "miinojen_sijainnit": [],
    "liput": [],
    "vuorot": 0,
    "havio_miina": [],
    "keskeytys": False,
    "tallennus": 0
}

mitat = {
    "leveys": 0,
    "korkeus": 0,
    "x_reuna": 0,
    "y_reuna": 0,
    "ruutu": 0
}




def luo_kentta(leveys, korkeus):
    """
    Luo pelikentän (kaksiulotteinen lista). Palauttaa kentän ja listan pelikentän
    koordinaattipareista.
    """
    pelikentta = []
    for rivi in range(korkeus):
        pelikentta.append([])
        for sarake in range(leveys):
            pelikentta[-1].append("0")

    koordinaattilista = []
    for x in range(leveys):
        for y in range(korkeus):
            koordinaattilista.append((x, y))
    
    return pelikentta, koordinaattilista

def miinoita(kentta, koordinaattilista, miinojen_maara):
    """
    Asettaa kentälle N kpl miinoja satunnaisiin paikkoihin. Palauttaa listan
    miinojen koordinaateista.
    """
    miina_sijainti = random.sample(koordinaattilista, miinojen_maara)
    for x, y in miina_sijainti:
        kentta[y][x] = "x"
    return miina_sijainti

def laske_miinat(x, y, rakenne):
    """
    Laskee annetun ruudun ympärillä olevien miinojen lukumäärän.
    Ei laske itse ruutua mukaan.
    """
    miinat_maara = 0
    rivit = len(rakenne)
    sarakkeet = len(rakenne[0])

    for i in range(y - 1, y + 2):
        for j in range(x - 1, x + 2):
            if (0 <= i < rivit) and (0 <= j < sarakkeet) and (j, i) != (x, y):
                if rakenne[i][j] == "x":
                    miinat_maara += 1

    return miinat_maara

def avaa_ruutu(kentta, avaamaton, avattu, x, y, miinat, liput):
    """
    Avaa klikatun ruudun (x, y) ja kentällä olevat avaamattomat, turvalliset ruudut siten, että
    täyttö aloitetaan annetusta klikatusta pisteestä.
    """
    rivit = len(kentta)
    sarakkeet = len(kentta[0])
    koordinaatit = [(x, y)]

    while koordinaatit:
        (poimittu_x, poimittu_y) = koordinaatit.pop()

        if not (0 <= poimittu_x < sarakkeet and 0 <= poimittu_y < rivit):
            continue

        if (poimittu_x, poimittu_y) in avattu:
            continue

        elif (poimittu_x, poimittu_y) in miinat:
            peli["havio_miina"].append((poimittu_x, poimittu_y))
            peli_paattyi("havio")
            return
        
        elif (poimittu_x, poimittu_y) in avaamaton and (poimittu_x, poimittu_y) not in liput:
            avaamaton.remove((poimittu_x, poimittu_y))
            avattu.append((poimittu_x, poimittu_y))
        

        miinat_ymparilla = laske_miinat(poimittu_x, poimittu_y,kentta)
        
        if miinat_ymparilla == 0:
            for i in range(poimittu_y - 1, poimittu_y + 2):
                for j in range(poimittu_x - 1, poimittu_x + 2):
                    if (0 <= i < rivit) and (0 <= j < sarakkeet):
                        viereinen = (j, i)
                        if viereinen not in avattu and viereinen not in liput and (j, i) not in koordinaatit:
                            koordinaatit.append(viereinen)

def tulvataytto(x, y, rakenne):
    """
    Suorittaa tulvatäytön avatulle ruudulle, jos kaikki ympäröivät miinat on liputettu.
    """
    viereiset = []
    for i in range(y - 1, y + 2):
        for j in range(x - 1, x + 2):
            if (0 <= j < len(rakenne[0]) and 0 <= i < len(rakenne) and (j, i) != (x, y)):
                viereiset.append((j, i))

    liput_maara = 0
    for j, i  in viereiset:
        if (j, i) in peli["liput"]:
            liput_maara += 1

    miinat_ymparilla = laske_miinat(x, y, rakenne)

    if liput_maara == miinat_ymparilla:
        for xx, yy in viereiset:
            if (xx, yy) not in peli["liput"]:
                avaa_ruutu(rakenne, peli["avaamattomat"], peli["avatut"], xx, yy, peli["miinojen_sijainnit"], peli["liput"])





def piirra_teksti(teksti, x, y, koko=32, vari=(255,255,255,255), ankkurix='center', ankkuriy='center'):
    """
    Piirtää valkoista tekstiä "Press Start 2P" -fontilla. x = tekstin keskikohta ja 
    y = tekstin keskikohta.
    """

    ha.grafiikka["spritet"].append(pyglet.text.Label(str(teksti),
        font_name="Press Start 2P",
        font_size=koko,
        color=vari,
        x=x, y=y,
        anchor_x = ankkurix, anchor_y= ankkuriy,
        batch=ha.grafiikka["puskuri"],
        group=ha.grafiikka["tekstijoukko"],
        )) 

def piirra_painike (x, y, leveys, korkeus, teksti, tekstikoko, kehys=4):
    """
    Piirtää mustan painikkeen valkoisella kehyksellä ja valkoisella tekstillä. 
    x = painikkeen vasen reuna, y = painikkeena alareuna.

    """
    k_leveys = kehys
    ha.piirra_suorakaide(x, y, leveys, korkeus, vari=(255, 255, 255, 255))
    ha.piirra_suorakaide(x + k_leveys, y + k_leveys, leveys - 2 * k_leveys, korkeus - 2 * k_leveys, vari=(0, 0, 0, 255))
    piirra_teksti(teksti, (leveys // 2 + x), (korkeus // 2 + y), koko=tekstikoko)

def piirra_sivu():
    """
    Piirtokäsittelijäfunktio yksinkertaiselle sivuille, jossa on pelkkä tausta.
    """
    ha.tyhjaa_ikkuna()
    ha.piirra_tausta()
    ha.piirra_ruudut()

def piirra_valikko():
    """
    Piirtokäsittelijäfunktio pelin valikolle. Piirtää valikon painikkeet.
    """
    ha.tyhjaa_ikkuna()
    ha.piirra_tausta()
     
   
    piirra_painike(217, 85, 365, 115, "LOPETA", 32)
    piirra_painike(217, 240, 365, 115, "TILASTOT", 32)
    piirra_painike(217, 400, 365, 115, "ALOITA", 32)

    ha.piirra_ruudut()

def piirra_kysely():
    """
    Piirtokäsittelijäfunktio kenttätietojen kyselylle. 
    """
    ha.tyhjaa_ikkuna()
    ha.piirra_tausta()

    piirra_painike(65, 15, 200, 50, "VALIKKO", 17)
    piirra_painike(300, 15, 200, 50, "TYHJENNÄ", 17)
    piirra_painike(535, 15, 200, 50, "ALOITA", 17) 
    
    huomautukset = {
        1: "-miinat eivät mahdu kentälle-",
        2: "-syötteen tulee olla nollasta eroava kokonaisluku-",
        3: "-kentän suurin mahdollinen korkeus on 25 ruutua-",
        4: "-kentän suurin mahdollinen leveys on 70 ruutua-",
    }
    
    y_kysymys = [428, 313, 204]
    VALI = 49
    kentan_tiedot_avaimet = ["leveys", "korkeus", "miinat"]
    
    piirra_teksti("SYÖTÄ KENTÄN TIEDOT", 400, 530, koko=19, ankkuriy='top')

    for i in range(3):
        piirra_teksti(kysymykset[i], 400, y_kysymys[i], koko=13, ankkuriy='top')
        
        if i == kysely["nykyinen_kysymys"]:
            piirra_teksti(kysely["kayttajan_teksti"], 400, y_kysymys[i] - VALI, koko=13)
            piirra_kohdistin(y_kysymys[i] - VALI)
        else:
            if kentan_tiedot_avaimet[i] in kentan_tiedot:
             arvo = str(kentan_tiedot[kentan_tiedot_avaimet[i]]) 
            else:
                arvo = ""

            piirra_teksti(arvo, 400, y_kysymys[i] - VALI, koko=13)

    if kysely["huomautukset"]:
        piirra_teksti(huomautukset[kysely["huomautukset"]], 400, 115, koko=10)

    ha.piirra_ruudut()


def piirra_kohdistin(y):
    """
    Piirtää kohdistimen käyttäjän syötteen perään kyselysivulla.
    """
    if len(kysely["kayttajan_teksti"]) > 0:
        siirtyma = len(kysely["kayttajan_teksti"]) * 11
    else:
        siirtyma = 0

    if kysely["kohdistin_nakyy"]:
        piirra_teksti("|", 400 + siirtyma, y, koko=13)
        
def piirra_kentta():
    """
    Lisää pelikentän ruudut piirtopuskuriin kentän koon perusteella.
    """

    for y in range(kentan_tiedot["korkeus"]):
        for x in range(kentan_tiedot["leveys"]):

            koord_x = x * mitat["ruutu"] + mitat["x_reuna"]
            koord_y = y * mitat["ruutu"] + mitat["y_reuna"]

            #pienet ruudut
            if kentan_tiedot["leveys"] > 36 or kentan_tiedot["korkeus"] > 14:
                if (x, y) in peli["havio_miina"]:
                    ha.lisaa_piirrettava_ruutu("hx_", koord_x, koord_y)
                elif (x, y) in peli["liput"]:
                    ha.lisaa_piirrettava_ruutu("f_", koord_x, koord_y)
                elif (x, y) in peli["avaamattomat"]:
                    ha.lisaa_piirrettava_ruutu("_", koord_x, koord_y)
                elif (x, y) in peli["avatut"]:
                    miinat_ymparilla = laske_miinat(x, y, peli["kentta"])
                    ha.lisaa_piirrettava_ruutu(f"{miinat_ymparilla}_", koord_x, koord_y)
                elif (x, y) in peli["miinojen_sijainnit"]:
                    ha.lisaa_piirrettava_ruutu("x_", koord_x, koord_y)

            #isot ruudut
            else:
                if (x, y) in peli["havio_miina"]:
                    ha.lisaa_piirrettava_ruutu("hx", koord_x, koord_y)
                elif (x, y) in peli["liput"]:
                    ha.lisaa_piirrettava_ruutu("f", koord_x, koord_y)
                elif (x, y) in peli["avaamattomat"]:
                    ha.lisaa_piirrettava_ruutu(" ", koord_x, koord_y)
                elif (x, y) in peli["avatut"]:
                    miinat_ymparilla = laske_miinat(x, y, peli["kentta"])
                    ha.lisaa_piirrettava_ruutu(str(miinat_ymparilla), koord_x, koord_y)
                elif (x, y) in peli["miinojen_sijainnit"]:
                    ha.lisaa_piirrettava_ruutu("x", koord_x, koord_y)
        
def piirra_ylapalkki():
    """
    Piirtää pelitilan yläpalkin; miinalaskurin, hymiön ja ajastimen.
    """

    miinoja_jaljella = str(miinalaskuri(kentan_tiedot["miinat"], len(peli["liput"])))

    if tila["aloitus_aika"] == 0:
        aika = 0
    elif tilastot["tulos"]:
        aika = tila["pysaytetty_aika"]
    else:
        aika = tila["aika"]


    #MIINALASKURI JA AJASTIN
    ha.lisaa_piirrettava_ruutu("loota", mitat["leveys"] // 2 - 155, mitat["korkeus"] - 90)
    ha.lisaa_piirrettava_ruutu("loota", mitat["leveys"] //2  + 55, mitat["korkeus"] - 90)
    piirra_teksti(miinoja_jaljella, mitat["leveys"] // 2 - 104, mitat["korkeus"] - 67, vari=(255, 255, 255, 255), koko=17)
    piirra_teksti(str(aika), mitat["leveys"] // 2 + 107, mitat["korkeus"] - 67, vari=(255, 255, 255, 255), koko=17)

    #HYMIÖ
    if tilastot["tulos"] == "Voitto":
        ha.lisaa_piirrettava_ruutu("lasit", mitat["leveys"] // 2 -25, mitat["korkeus"] - 90)
        
    elif tilastot["tulos"] == "Häviö":
        ha.lisaa_piirrettava_ruutu("risti", mitat["leveys"] // 2 - 25, mitat["korkeus"] - 90)
    else:
        ha.lisaa_piirrettava_ruutu("hymy", mitat["leveys"] // 2 - 25, mitat["korkeus"] - 90)

def piirra_alapalkki():
    """
    Pirtää pelitilan alapalkin. Kun peli on käynnissä, piirretään "KESKEYTÄ" -painike, jota
    painettaessa ilmestyy varmistusviesti sekä "KYLLÄ" ja "EI" -painikkeet.
    Kun peli on päättynyt, piirretään "UUDELLEEN", "TALLENNA" ja "VALIKKO" -painikkeet. 
    Funktio piirtää myös ilmoituksen pelin tallennuksen tilasta.
    """

    if tilastot["tulos"]:

        piirra_painike(mitat["leveys"] // 2 - 170, 40, 100, 25,"UUDELLEEN", 7, 2)
        piirra_painike(mitat["leveys"] // 2 - 50, 40, 100, 25,"TALLENNA", 7, 2)
        piirra_painike(mitat["leveys"] // 2 + 70, 40, 100, 25,"VALIKKO", 7, 2)

        #tallennusilmoitus
        if peli["tallennus"] == 1:
            piirra_teksti("-tallennus onnistui-", mitat["leveys"] // 2, 22, 10)  
        if peli["tallennus"] == 2:
             piirra_teksti("-tallennus epäonnistui-", mitat["leveys"] // 2, 22, 10)


    elif peli["keskeytys"] is True:
        piirra_teksti("-keskeytetäänkö peli?-", mitat["leveys"] // 2 + 40, 53, 7, ankkurix='right')
        piirra_painike(mitat["leveys"] // 2 + 70, 60, 70, 20,"KYLLÄ", 7, 2)
        piirra_painike(mitat["leveys"] // 2 + 70, 25, 70, 20,"EI", 7, 2)


    elif tila["aloitus_aika"]:
        piirra_painike(mitat["leveys"] // 2 - 100, 30, 200, 50,"KESKEYTÄ", 17)
        
def piirra_peli():
    """
    Piirtokäsittelijäfunktio pelitilalle. Yhdistää pelitilaan liittyvät piirtofunktiot.
    """
    ha.tyhjaa_ikkuna()
    ha.piirra_tausta()
    piirra_kentta()
    piirra_ylapalkki()
    piirra_alapalkki()
    ha.piirra_ruudut()

def piirra_tilastot():
    """
    Piirtokäsittelijäfunktio tilastoikkunalle. Piirtää tilastot ja "takaisin valikkoon" -painikkeen.
    """
    
    tiedosto = "TILASTOT.txt"

    #Lataa tilastot
    try:
        with open(tiedosto, "r") as kohde:
            kaikki_tiedot = json.load(kohde)
    except (FileNotFoundError, json.JSONDecodeError):
        kaikki_tiedot = []

    ha.tyhjaa_ikkuna()
    ha.piirra_tausta()

    piirra_painike(10, 570, 80, 20, "TAKAISIN", 6, 2)

    piirra_teksti("TILASTOT", 400, 580, koko=15,)
    
    for i, rivi in enumerate(kaikki_tiedot):
        y_rivi = 550 - i * 16
        try:
            rivi_teksti = (
                f"{rivi['pvm']} | {rivi['klo']} | "
                f"Kesto: {rivi['kesto_min']} min | Vuorot: {rivi['kesto_vuoro']} | "
                f"Tulos: {rivi['tulos']} | Koko: {rivi['kentän_koko']} | Miinat: {rivi['miinat']}"
            )
            ha.piirra_tekstia(rivi, 10, y_rivi, vari=(255,255,255,255),fontti="Arial", koko=8)
        except KeyError:
            print(f"Tilastojen piirto epäonnistui")

    ha.piirra_ruudut()






def nappi_aloitus(symboli, muokkausnapit):
    """
    Näppäinkäsittelijäfunktio aloitussivulle.
    """
    if symboli == NAPIT.ENTER:
        valikko_ikkuna()


def kysely_nappaimet(symboli, muokkausnapit):
    """
    Näppäinkäsittelijäfunktio kyselysivulle.
    """
    kentan_tiedot_avaimet = ["leveys", "korkeus", "miinat"]
    if symboli in [NAPIT._0, NAPIT._1, NAPIT._2, NAPIT._3, NAPIT._4, 
                   NAPIT._5, NAPIT._6, NAPIT._7, NAPIT._8, NAPIT._9]:
        if len(kysely["kayttajan_teksti"]) < 4:
            kysely["kayttajan_teksti"] += chr(symboli)
            kysely["huomautukset"] = 0
    
    elif symboli == NAPIT.BACKSPACE:
        if kysely["kayttajan_teksti"]:
            kysely["kayttajan_teksti"] = kysely["kayttajan_teksti"][:-1]
    
    elif symboli == NAPIT.ENTER:
        syote = kysely["kayttajan_teksti"]
        kysymys = kysely["nykyinen_kysymys"]
        tarkistus, tulos = syotteen_tarkistus(syote, kysymys)
        
        if tarkistus:
            kentan_tiedot[kentan_tiedot_avaimet[kysymys]] = tulos
            if kysely["nykyinen_kysymys"] < 2:
                kysely["nykyinen_kysymys"] += 1
                if kentan_tiedot_avaimet[kysely["nykyinen_kysymys"]] in kentan_tiedot:
                    kysely["kayttajan_teksti"] = str(kentan_tiedot[kentan_tiedot_avaimet[kysely["nykyinen_kysymys"]]])
                else:
                    kysely["kayttajan_teksti"] = ""
            else:
                tarkista_ja_aloita()
        else:
            kysely["huomautukset"] = tulos


def tyhja_nappain(symboli, muokkausnapit):
    """
    Näppäinkäsittelijäfunktio sivuille, joissa ei tarvita näppäimiä. Selkeyttää käyttöliittymän
    toimintaa.
    """
    pass
    




def valikko_hiiri(x, y, nappi, modifiointi):
    """
    Käsittelijäfunktio valikkosivun hiirelle.
    """

    if nappi == ha.HIIRI_VASEN:
        if (217 <= x <= 582) and (400 <= y <= 515):
            kysely_ikkuna()

        elif (217 <= x <= 582) and (240<= y <= 355):
            tilastot_ikkuna()

        elif (217 <= x <= 582) and (85 <= y <= 200):
            ha.lopeta()

def kysely_hiiri(x, y, nappi, modifiointi):
    """
    Käsittelijäfunktio kyselysivun hiirelle.
    """
    kentan_tiedot_avaimet = ["leveys", "korkeus", "miinat"]
    y_kysymys = [428, 313, 204]
    VALI = 49
    
    if nappi == ha.HIIRI_VASEN:

        #Tallennetaan aiempi syöte ennen siirtymistä toiseen kenttään
        syote = kysely["kayttajan_teksti"]
        kysymys = kysely["nykyinen_kysymys"]
        if syote:
            tarkistus, tulos = syotteen_tarkistus(syote, kysymys)
            if tarkistus:
                kentan_tiedot[kentan_tiedot_avaimet[kysymys]] = tulos
            else:
                kysely["huomautukset"] = tulos
        
        if (90 <= x <= 260) and (13 <= y <= 65):
            valikko_ikkuna()
        
        if (315 <= x <= 485) and (13 <= y <= 65):
            alusta_kentan_tiedot()
            alusta_kysely()
        
        if (580 <= x <= 750) and (13 <= y <= 65):
            tarkista_ja_aloita()
        
        #Syötteen muuttaminen klikkaamalla kysymyksen syötealuetta
        for i in range(3):
            if (40 <= x <= 760) and (y_kysymys[i] - 115 <= y <= y_kysymys[i]):
                kysely["nykyinen_kysymys"] = i
                if kentan_tiedot_avaimet[i] in kentan_tiedot:
                    kysely["kayttajan_teksti"] = str(kentan_tiedot[kentan_tiedot_avaimet[i]])
                else:
                    kysely["kayttajan_teksti"] = ""
                break


def peli_hiiri(x, y, nappi, modifiointi):
    """
    Käsittelijäfunktio pelitilan hiirelle. Sisältää eri hiiritoiminnot pelitilasta riippuen.
    Pelitilat = ALOITUS, KÄYNNISSÄ, KESKEYTYS, PÄÄTTYNYT
    """

    global tilastot
    global peli
    global tila

    koord_x = (x - mitat["x_reuna"]) // mitat["ruutu"]
    koord_y = (y - mitat["y_reuna"]) // mitat["ruutu"]    
    leveys = mitat["leveys"]


    #PÄÄTTYNYT
    if tilastot["tulos"]:
            if nappi == ha.HIIRI_VASEN:
                #Aloita peli uudelleen samalla kentällä.
                if (leveys // 2 - 170 < x < leveys // 2 - 70) and (40 < y < 75):
                    pelaa_uudelleen()

                #Tallentaa pelin tilastot tiedostoon.
                if leveys // 2 - 50 < x < leveys // 2 + 50 and (40 < y < 75):
                    tarkista_tallennus = tallenna_peli(tilastot, "TILASTOT.txt")
                    if tarkista_tallennus:
                        peli["tallennus"] += 1
                    else:
                        peli["tallennus"] += 2

                #Valikko
                if leveys // 2 + 70 < x < leveys // 2 + 170 and (40 < y < 75):
                    valikko_ikkuna()

    #KESKEYTYS
    elif peli["keskeytys"] is True:
        if nappi == ha.HIIRI_VASEN:
            #KYLLÄ, peli päättyi häviöön
            if (leveys // 2 + 70) < x < (leveys // 2 + 140) and (60 < y < 80):
                peli_paattyi('havio')

            #EI, peli jatkuu normaalisti
            if leveys // 2 + 70 < x < (leveys // 2 + 140) and (25 < y < 45):
                peli["keskeytys"] = False


    else:
        if nappi == ha.HIIRI_VASEN:
            
            #ALOITUS
            if tila["aloitus_aika"] == 0:
                tila["aloitus_aika"] = time.time()
                alusta_tilastot()

            #KÄYNNISSÄ, peliruutujen avaaminen ja tulvatäyttö
            if (koord_x, koord_y) in peli["avatut"]:
                peli["vuorot"] +=1
                tulvataytto(koord_x, koord_y, peli["kentta"])
            elif (koord_x, koord_y) not in peli["liput"]:
                peli["vuorot"] +=1
                avaa_ruutu(peli["kentta"], peli["avaamattomat"], peli["avatut"], koord_x, koord_y, peli["miinojen_sijainnit"], peli["liput"])

            #KESKEYTÄ -nappi, siirtyy keskeytys-tilaan
            if tila["aika"] > 1 and leveys // 2 - 100 < x < leveys // 2 + 100 and 30 < y < 80:
                peli["keskeytys"] = True

        #KÄYNNISSÄ, ruutujen liputus
        elif nappi == ha.HIIRI_OIKEA:
            peli["vuorot"] +=1
            liputa(koord_x, koord_y, peli["liput"], peli["vuorot"], kentan_tiedot["miinat"], peli["avatut"])

        #KÄYNNISSÄ, tulvatäyttö
        elif nappi == ha.HIIRI_KESKI:
            if (koord_x, koord_y) in peli["avatut"]:
                peli["vuorot"] +=1
                tulvataytto(koord_x, koord_y, peli["kentta"])

        if tarkista_voitto(peli["avaamattomat"], peli["miinojen_sijainnit"]):
            peli_paattyi('voitto')

def tilastot_hiiri(x, y, nappi, modifiointi):
     if nappi == ha.HIIRI_VASEN:
        if (10 < x < 90) and (570 < y < 590):
            valikko_ikkuna()

def aloitus_hiiri(x, y, nappi, modifiointi):
     """
    Käsittelijäfunktio valikkosivun hiirelle.
    """
 
     if nappi == ha.HIIRI_VASEN:
        valikko_ikkuna()






def luo_mitat(leveys, korkeus):
    """
    Luo mitat peli-ikkunalle kyselyssä annettujen kenttätietojen perusteella.
    """
    
    
    #korkea kenttä
    if korkeus > 14 or leveys > 36:
       ruutu_koko = 20
    else:
        ruutu_koko = 40
    x_reuna = 40
    y_reuna = 110
    leveys_ikkuna = leveys * ruutu_koko + 80
    korkeus_ikkuna = korkeus * ruutu_koko + 240
   
    #kapea kenttä
    if leveys <= 15 and korkeus > 14 or leveys <= 7:
        leveys_ikkuna = 390
        x_reuna = (390 - leveys * ruutu_koko) // 2

    return {
        "leveys": leveys_ikkuna,
        "korkeus": korkeus_ikkuna,
        "x_reuna": x_reuna,
        "y_reuna": y_reuna,
        "ruutu": ruutu_koko
    }

def alusta_kysely():
    """
    Alustaa kyselyn.
    """
    kysely.update({
        "nykyinen_kysymys": 0,
        "huomautukset": 0,
        "kayttajan_teksti": "",
        "kohdistin_nakyy": True
    })

def tarkista_ja_aloita():
    """
    Tarkistaa syötteiden kelpoisuuden ja käynnistää pelin, jos ne ovat kunnossa.
    """
    kentan_tiedot_avaimet = ["leveys", "korkeus", "miinat"]

    kysely_valmis = True
    for i, avain in enumerate(kentan_tiedot_avaimet):
        if avain in kentan_tiedot:
            syote = str(kentan_tiedot[avain]) 
        else:
            syote = ""
        hyvaksytty, _ = syotteen_tarkistus(syote, i)
        if not hyvaksytty:
            kysely_valmis = False
            break
    
    if kysely_valmis:
        peli_ikkuna()
    else:
        kysely["huomautukset"] = 2


def alusta_kentan_tiedot():
    """
    Alustaa kentän tiedot.
    """
    kentan_tiedot.update({
    "leveys": "",
    "korkeus": "",
    "miinat": ""
    })
    
def alusta_tilastot():
    """
    Alustaa pelin tilastot.
    """
    tilastot.update({
    "pvm": time.strftime("%Y-%m-%d", time.localtime()),
    "klo": time.strftime("%H:%M:%S", time.localtime()),
    "kesto_min": None,
    "kesto_vuoro": None,
    "tulos": None,
    "kentän_koko": f"{str(kentan_tiedot['leveys'])} x {str(kentan_tiedot['korkeus'])}",
    "miinat": f"{str(kentan_tiedot['miinat'])}",
    })

def peli_paattyi(tulos):
    """
    Tallentaa loput tilastot sanakirjaan ja paljastaa miinojen sijainnin pelin päätyttyä.
    """

    poista_toistuvat_kasittelijat() #aika pysähtyy
    tila["pysaytetty_aika"] = round(time.time() - tila["aloitus_aika"])

    tilastot["kesto_vuoro"] = str(peli["vuorot"])
    tilastot["kesto_min"] = str(round(time.time() - tila["aloitus_aika"]) // 60)

    if tulos == 'voitto':
        tilastot["tulos"] = "Voitto"
        for koordinaatti in peli["miinojen_sijainnit"]:
             if koordinaatti in peli["avaamattomat"] and koordinaatti not in peli["liput"]:
                  peli["liput"].append(koordinaatti)

    elif tulos == 'havio':
        tilastot["tulos"] = "Häviö"
        for koordinaatti in peli["miinojen_sijainnit"]:
                if koordinaatti in peli["liput"]:
                    peli["liput"].remove(koordinaatti)
                if koordinaatti in peli["avaamattomat"]:
                    peli["avaamattomat"].remove(koordinaatti) 


def alusta_peli(leveys, korkeus, miinat):
    """
    Luo kentän ja miinoittaa sen kyselyssä annettujen tietojen perusteella. Alustaa pelin
    ja tilan sanakirjat.
    """

    kentta, avaamattomat = luo_kentta(leveys, korkeus)
    miina_sijainnit = miinoita(kentta, avaamattomat, miinat)

    peli.update({
        "kentta": kentta,
        "avaamattomat": avaamattomat,
        "avatut": [],
        "miinojen_sijainnit": miina_sijainnit,
        "liput": [],
        "vuorot": 0,
        "havio_miina": [],
        "keskeytys": False,
        "tallennus": 0
        })

    tila.update({
        "aika": 0,
        "aloitus_aika": 0,
        "pysaytetty_aika": 0,
    })

def tallenna_peli(tiedot, tiedosto):
    """
    Tallentaa halutut tiedot haluttuun tiedostoon. Palauttaa True, jos tallennus onnistuu.
    """
    try:
        #Lataa aiemmat tiedot
        try:
            with open(tiedosto, "r") as kohde:
                kaikki_tiedot = json.load(kohde)
        except (FileNotFoundError, json.JSONDecodeError):
            kaikki_tiedot = []

        #Lisää uudet tiedot perään
        kaikki_tiedot.append(tiedot)

        #Tallentaa kaikki takaisin tiedostoon
        with open(tiedosto, "w") as kohde:
            json.dump(kaikki_tiedot, kohde, indent=4)
        return True
    except IOError:
        print("Tallennus epäonnistui")
        return False
    
def lataa_kuvia(polku):
    """
    Lataa pelikentän grafiikkoja.
    """
    pyglet.resource.path = [polku]
    kuvat = {}

    #isot ruudut (40 x 40)
    kuvat["0"] = pyglet.resource.image("tyhja.png")
    for i in range(1, 9):
        kuvat[str(i)] = pyglet.resource.image(f"{i}.png")
    kuvat["x"] = pyglet.resource.image("miina.png")
    kuvat[" "] = pyglet.resource.image("selka.png")
    kuvat["f"] = pyglet.resource.image("lippu.png")
    kuvat["hx"] = pyglet.resource.image("osui.png")

    #pienet ruudut (20 x 20)
    kuvat["0_"] = pyglet.resource.image("pikku_tyhja.png")
    for i in range(1, 9):
        kuvat[f"{i}_"] = pyglet.resource.image(f"{i}_.png")
    kuvat["x_"] = pyglet.resource.image("pikku_miina.png")
    kuvat["_"] = pyglet.resource.image("pikku_selka.png")
    kuvat["f_"] = pyglet.resource.image("pikku_lippu.png")
    kuvat["hx_"] = pyglet.resource.image("pikku_osui.png")

    #hymiöt
    kuvat["hymy"] = pyglet.resource.image("neutraali.png")
    kuvat["risti"] = pyglet.resource.image("havio.png")
    kuvat["lasit"] = pyglet.resource.image("voitto.png")

    #muuta grafiikkaa
    kuvat["loota"] = pyglet.resource.image("loota.png")

    ha.grafiikka["kuvat"].update(kuvat)

def kohdistin(kulunut_aika):
    """
    Toistuvan käsittelijän funktio, joka päivittää kohdistimen näkyvyyden.
    """
    kysely["kohdistin_nakyy"] = not kysely["kohdistin_nakyy"]

def paivita_aika(kulunut_aika):
    """
    Toistuvan käsittelijän funktio, joka päivittää aikaa.
    """
    nykyinen_aika = time.time()

    if tila["aloitus_aika"] == 0:
        tila["aika"] = 0 #selkeyttää piirtoa
    else:
        tila["aika"] = int(nykyinen_aika - tila["aloitus_aika"])
  
def miinalaskuri(miinat_maara, liput):
    """
    Laskee liputtamattomien miinojen määrän kentällä.
    """
    miinat_jaljella = int(miinat_maara) - int(liput)
    return miinat_jaljella

def paivita_kasittelijat():
    """
    Päivittää aktiiviset käsittelijät sanakirjaan.
    """
    ha.aseta_piirto_kasittelija(kasittelijat["piirto"])
    ha.aseta_hiiri_kasittelija(kasittelijat["hiiri"])
    ha.aseta_nappain_kasittelija(kasittelijat["nappain"])
    for funktio, aikavali in kasittelijat["toistuvat"]:
        ha.aseta_toistuva_kasittelija(funktio, aikavali)

def poista_toistuvat_kasittelijat():
    """
    Poistaa toistuvat käsittelijät.
    """
    for kasittelija in kasittelijat["toistuvat"]:
        pyglet.clock.unschedule(kasittelija)

def syotteen_tarkistus(syote, kysymys):
    """
    Tarkistaa käyttäjän syötteen ja palauttaa tuloksen.
    """
    try:
        arvo = int(syote)
        if arvo <= 0:
            return False, 2

        if kysymys == 0: #Leveys
            if arvo > 70:
                return False, 4

        elif kysymys == 1:  #Korkeus
            if arvo > 25:
                return False, 3

        elif kysymys == 2:  #Miinojen määrä
            if arvo >= kentan_tiedot["leveys"] * kentan_tiedot["korkeus"]:
                return False, 1

        return True, arvo

    except ValueError:
        return False, 2

def tarkista_voitto(avaamattomat, miinat):
    """
    Tarkistaa, onko peli voitettu. Palauttaa True, jos avaamattomien ruutujen koordinaatit 
    vastaavat miinojen koordinaatteja.
    """
    if set(avaamattomat) == set(miinat):
        return True
    return False

def pelaa_uudelleen():
    """
    Alustaa pelin ja tilastot sekä päivittää pelitilan aktiiviset käsittelijät.
    """
    alusta_peli(kentan_tiedot["leveys"],kentan_tiedot["korkeus"], kentan_tiedot["miinat"])
    alusta_tilastot()
    poista_toistuvat_kasittelijat()
    kasittelijat["piirto"] = piirra_peli
    kasittelijat["hiiri"] = peli_hiiri
    kasittelijat["nappain"] = tyhja_nappain
    kasittelijat["toistuvat"] = [
        (paivita_aika, 1),
    ]
    paivita_kasittelijat()

def liputa(x, y, liput, vuorot, miinat, avatut):
    """
    Asettaa lipun avaamattoman ruutuun tai poistaa lipun ruudusta, jossa on jo lippu.
    Lisää siis x, y -koordinaatin liputettujen ruutujen listaan tai poistaa sen listalta.
    """
    if (x, y) in liput:
        vuorot +=1
        liput.remove((x, y))
    elif (x, y) not in avatut:
        if len(liput) < miinat:
            vuorot +=1
            liput.append((x, y))


#IKKUNAT

def tilastot_ikkuna():
    """
    Muuttaa ikkunan tilastoikkunaksi.
    """
    ha.muuta_ikkunan_koko(800, 600, taustavari=(0, 0, 0, 255), taustakuva=None)
    poista_toistuvat_kasittelijat()
    kasittelijat["piirto"] = piirra_tilastot
    kasittelijat["hiiri"] = tilastot_hiiri
    kasittelijat["nappain"] = tyhja_nappain
    paivita_kasittelijat()
        
def peli_ikkuna():
    """
    Muuttaa ikkunan peliikkunaksi.
    """
    global mitat
    global peli
    global tila

    mitat = luo_mitat(kentan_tiedot["leveys"], kentan_tiedot["korkeus"])
    lataa_kuvia("grafiikka")
    ha.muuta_ikkunan_koko(mitat["leveys"], mitat["korkeus"], taustavari=(0, 0, 0, 255), taustakuva=None)
    pelaa_uudelleen()


def kysely_ikkuna():
    """
    Muuttaa ikkunan kyselyikkunaksi.
    """
    alusta_kysely()
    alusta_kentan_tiedot()
    taustakuva3 = ha.lataa_taustakuva("grafiikka", "t_kysely.png")
    ha.muuta_ikkunan_koko(800, 600, taustavari=(0, 0, 0, 255), taustakuva=taustakuva3)
    poista_toistuvat_kasittelijat()
    kasittelijat["piirto"] = piirra_kysely
    kasittelijat["hiiri"] = kysely_hiiri
    kasittelijat["nappain"] = kysely_nappaimet
    kasittelijat["toistuvat"] = [
        (kohdistin, 0.5),
    ]
    paivita_kasittelijat()

def valikko_ikkuna():
    """
    Muuttaa ikkunan valikkoikkunaksi.
    """
    taustakuva2 = ha.lataa_taustakuva("grafiikka", "t_valikko.jpg")
    ha.muuta_ikkunan_koko(800, 600, taustavari=(0, 0, 0, 255), taustakuva=taustakuva2)
    poista_toistuvat_kasittelijat()
    kasittelijat["piirto"] = piirra_valikko
    kasittelijat["hiiri"] = valikko_hiiri
    kasittelijat["nappain"] = tyhja_nappain
    paivita_kasittelijat()

def aloitus_ikkuna():
    """
    Luo peli-ikkunan ja piirtää aloitussivun.
    """
    taustakuva1 = ha.lataa_taustakuva("grafiikka", "t_aloitus.png")
    ha.luo_ikkuna(800, 600, taustavari=(0, 0, 0, 255), taustakuva=taustakuva1)
    ha.aseta_piirto_kasittelija(piirra_sivu)
    ha.aseta_nappain_kasittelija(nappi_aloitus)
    ha.aseta_hiiri_kasittelija(aloitus_hiiri)

if __name__ == "__main__":
    aloitus_ikkuna()
    ha.aloita()

