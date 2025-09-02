import requests
from bs4 import BeautifulSoup as bs
import csv
import sys
import time

if len(sys.argv) != 3:
    print("Chyba: Zadejte přesně 2 argumenty.\n"
          "Správný způsob zadání: python main.py <odkaz> <nazev_souboru.csv>")
    sys.exit()

url_celek = sys.argv[1]
nazev_souboru = sys.argv[2]

if "volby.cz" not in url_celek:
    print("Chyba: První argument musí být odkaz na stránku volby.cz")
    sys.exit()

if not nazev_souboru.endswith(".csv"):
    print("Chyba: Druhý argument musí končit .csv")
    sys.exit()

def get_obce(url_celek):
    print("Stahuji data z vybraného url:",url_celek)

    base_url = "https://www.volby.cz/pls/ps2017nss/"
    obsah = requests.get(url_celek)
    parsed = bs(obsah.text,features="html.parser")
    vsechny_tabulky = parsed.find_all("table", {"class": "table"})
    obce = list()
    kody = []
    obce_nazvy = []
    vysledky_vsechny_obce = []
    for tabulka in vsechny_tabulky:  # procházím tabulky
        radky_tabulky = list(tabulka.find_all("tr"))  # dávám do seznamu řádky
        for radek in radky_tabulky[2:]:  # procházím řádky kromě prvních dvou (kde
            # nejsou data, ale záhlaví, takže tam chybí dále hledané td
            bunky_tabulky = list(radek.find_all("td"))  # hledám buňky na řádku,
            # kde jsou data
            for bunka in bunky_tabulky[0:1]: #vezme jen první sloupec/buňku
                odkaz = bunka.find("a") #najde odkaz v buňce
                if odkaz:
                    href = base_url + odkaz.get("href") #vytáhnu URL
                    vysledky_obce = get_vysledky(href) #ukládám do proměnné
                    vysledky_vsechny_obce.append(vysledky_obce) #ukládám do
                    # seznamu
                    kody.append(bunky_tabulky[0].text)
                    obce_nazvy.append(bunky_tabulky[1].text)
                    time.sleep(5)

    return vysledky_vsechny_obce, kody, obce_nazvy

def get_vysledky(href):
    obsah = requests.get(href)
    parsed = bs(obsah.text,features="html.parser")
    #údaje z první tabulky (voliči, obálky, platné hlasy)
    statistiky = parsed.find("table", {"class": "table"}) #najde první tabulku
    vsechny_radky = list(statistiky.find_all("tr")) #najde všechny řádky v tabulce
    bunky = list(vsechny_radky[2].find_all("td")) #najde třetí řádek
    volici = bunky[3].text #najde čtvrtou buňku v řádku
    obalky = bunky[4].text
    hlasy = bunky[7].text
    #print(volici,obalky,hlasy)

    #vyberu všechny tabulky na stránce
    vsechny_tabulky = parsed.find_all("table", {"class": "table"})
    vysledky = list()
    for tabulka in vsechny_tabulky[1:]: #procházím tabulky kromě první
        radky_tabulky = list(tabulka.find_all("tr")) #dávám do seznamu řádky
        for radek in radky_tabulky[2:]: #procházím řádky kromě prvních dvou (kde
            # nejsou data, ale záhlaví, takže tam chybí dále hledané td
            bunky_tabulky = list(radek.find_all("td")) #hledám buňky na řádku,
            # kde jsou data
            bunka = [bunky_tabulky[1].text, bunky_tabulky[2].text] #beru jen
            # druhou a třetí buňku, kde mám hledaná data a dávám je k sobě jako pár
            vysledky.append(bunka) #přidávám pár do listu
    #print(vysledky)

    strany = []
    hlasy_stran =[]
    for a in vysledky:
        strany.append(a[0])
        hlasy_stran.append(a[1])
    #print(strany)
    #print(hlasy_stran)

    return volici, obalky, hlasy, vysledky, strany, hlasy_stran

final_vysledky = (get_obce(url_celek))

print("Ukládám do souboru:",nazev_souboru)

with (open(nazev_souboru, "w", newline="", encoding="utf-8") as
csvfile):
    writer = csv.writer(csvfile)
    vysledky_obci = final_vysledky[0]
    kody_obci = final_vysledky[1]
    nazvy_obci = final_vysledky[2]
    strany_hlavicky = vysledky_obci[0][4]
    fix_hlavicky = ["Kód obce", "Název obce", "Voliči v seznamu","Vydané "
                    "obálky","Platné hlasy"]
    hlavicky = fix_hlavicky + strany_hlavicky
    writer.writerow(hlavicky)
    for i, vysledky_obce in enumerate(vysledky_obci):
        kod = kody_obci[i]
        obec = nazvy_obci[i]
        volici = vysledky_obce[0]
        obalky = vysledky_obce[1]
        hlasy = vysledky_obce[2]
        hlasy_stran = vysledky_obce[5]

        fix_data = [kod,obec,volici,obalky,hlasy]
        data = fix_data + hlasy_stran
        writer.writerow(data)

print("Hotovo, ukončuji election-scraper.")