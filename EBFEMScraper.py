import requests
from bs4 import BeautifulSoup
import re
from tqdm import tqdm
import json
import argparse
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
import time
import datetime

honapok = {
    "január": 1,
    "február": 2,
    "március": 3,
    "április": 4,
    "május": 5,
    "június": 6,
    "július": 7,
    "augusztus": 8,
    "szeptember": 9,
    "október": 10,
    "november": 11,
    "december": 12
}

def str2date(datum):
    reszek = [d.split(".")[0].strip() for d in datum.strip().split(" ")]
    return datetime.date(int(reszek[0]), honapok[reszek[1]], int(reszek[2]))


def EBFEM(filename=None, year=None, appendHibas=True, headless = True):

    url = 'https://www.esztergomi-ersekseg.hu/papsag'
    options = webdriver.FirefoxOptions()
    if headless:
        options.add_argument("--headless")
    driver = webdriver.Firefox(options=options)

    driver.get(url)


    driver.implicitly_wait(2)
    select = Select(driver.find_element(By.CSS_SELECTOR, "select[name='kat']"))
    select.select_by_visible_text('mind')

    driver.implicitly_wait(2)

    driver.execute_script("(async function() {szuro()})()")

    driver.implicitly_wait(2)

    driver.execute_script("(async function() {while (isDataAvailable) {listmore(); await new Promise(r => setTimeout(r, 3000))}})()")

    for i in tqdm(range(40)):
        time.sleep(1)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()
    papok = []

    for pap in soup.select_one("#listazas").select(".hirbox"):
        papok.append(pap.select_one('a')['href'])  # Papi oldalak linkjei
    
    firstLine = 0
    paplista = []
    hibasak = []

    for pap in tqdm(papok):  # Nézze meg az összes pap linkjét
        try:  # Kétszeri próbálkozásra szokott menni
            response = requests.get(f"{url}/{pap.split('/')[1]}")
            if response.status_code == 200:
                html_content = response.content
            else:
                print("Failed to fetch the website.")
        except:
            try:
                response = requests.get(f"{url}/{pap.split('/')[1]}")
                if response.status_code == 200:
                    html_content = response.content
                else:
                    print("Failed to fetch the website.")
            except:
                print("Big error")
                continue

        soup = BeautifulSoup(html_content, 'html.parser')
        nev = soup.select_one("h1").text.strip()
        if "†" in nev:
            continue

        bishop = False
        if soup.select_one(".titulus"):
            if "érsek" in soup.select_one(".titulus").text or "segédpüspök" in soup.select_one(".titulus").text and not "érseki" in soup.select_one(".titulus").text.lower():
                bishop = True
        
        deacon = False
        retired = False
        szent = 0
        for fieldset in soup.select("fieldset"):
            if "Szentelés" in fieldset.text:
                try:
                    szent = str2date(fieldset.text.split(", ")[1])
                except:
                    pass
            if "Jelenlegi beosztások" in fieldset.text and "Diakónus" in fieldset.text:
                deacon = True
            if not "Életrajz" in fieldset.text:
                continue
            if "Nyugállományban" in fieldset.text:
                retired = True
            szul = 0
            try:
                szul = str2date(fieldset.text.split(", ")[1])
            except:
                try:
                    szul =  str2date(" ".join(fieldset.text.split(", ")[0].split(" ")[1:]))
                except:
                    try:
                        szul = str2date(" ".join(fieldset.text.split(", ")[0].split("-")[0].split(" ")[2:]))

                    except:
                        try:
                            szul = int(fieldset.text.split("-")[0].split(" ")[1])
                        except:
                            try:
                                szul = str2date(fieldset.text.split("-")[0].split(",")[1])
                            except:
                                try:
                                    szul = str2date(" ".join(fieldset.text.split("-")[0].split(" ")[1:]))
                                except:
                                    try:
                                        szul = int(fieldset.text.split(".")[0].split(" ")[-1])
                                    except:
                                        pass
                                
            
            if nev == "Fábry Kornél dr.": #https://hu.wikipedia.org/wiki/F%C3%A1bry_Korn%C3%A9l
                szul = 1972
            
            if nev == "Riesz Domonkos": #http://esztergomiszeminarium.eu/riesz-domonkos/
                szul = 1994
            
            if nev == "Faragó András": #http://esztergomiszeminarium.eu/i-evfolyam/farago-andras/
                szul = 1993

            if nev == "Fehér Zoltán": #https://albertfalviplebania.hu/index.php/cikkek/interju-feher-zoltan-atyaval
                szul = 1995
            
            if nev == "Forgács Balázs": # http://esztergomiszeminarium.eu/forgacs-balazs/
                szul = 1988
            
            if nev == "Gyurász Krisztián": #https://bosihirado.net/index.php/papjaink
                szul = 1989
            
            if nev == "Kiss Géza Imre":
                szul = 1988
            
            if nev == "Lendvai Z. Zalán OFM": #https://orszagutiferencesek.hu/plebania/kepviselotestulet/
                szul = 1964
            
            if nev == "Lőw Gergely": #https://pmi.katolikus.hu/?page_id=1904
                szul = 1993
            
            if nev == "Máté János Kristóf": #http://esztergomiszeminarium.eu/mate-janos-kristof/
                szul = 1993

            if nev == "Varga Kamill OFM": #http://jaszhelytortenet.hu/e-6-15-varga-jozsef-fr-kamill-ofm.html
                szul = 1974

            if szul == 0:
                hibasak.append({"név": nev, "hiba": "Születés nem található"})
                if appendHibas: paplista.append({
                    "name": nev,
                    "birth": None,
                    "img": "https://www.esztergomi-ersekseg.hu" + soup.select_one(".adatlap img").get("src"),
                    "src": f"{url}/{pap.split('/')[1]}",
                    "ordination": szent if szent != 0 else None,
                    "bishop": bishop,
                    "deacon": deacon,
                    "retired": retired
                })
                break
            
            szulev = szul.year if isinstance(szul, datetime.date) else szul
            szentev = szent.year if isinstance(szent, datetime.date) else szent

            if szent == 0:
                szent = None
            if szulev<szentev:
                paplista.append({
                                "name": nev,
                                "birth": szul,
                                "img": "https://www.esztergomi-ersekseg.hu" + soup.select_one(".adatlap img").get("src"),
                                "src": f"{url}/{pap.split('/')[1]}",
                                "ordination": szent,
                                "bishop": bishop,
                                "deacon": deacon,
                                "retired": retired
                            })
            else:
                if appendHibas:
                    paplista.append({
                                "name": nev,
                                "birth": None,
                                "img": "https://www.esztergomi-ersekseg.hu" + soup.select_one(".adatlap img").get("src"),
                                "src": f"{url}/{pap.split('/')[1]}",
                                "ordination": szent,
                                "bishop": bishop,
                                "deacon": deacon,
                                "retired": retired
                            })
                hibasak.append({"név": nev, "hiba": "Szentelése előbbi, mint születése"})
            break

    print(hibasak)
    print("Hibás:", len(hibasak))
    print("Talán jó:", len(paplista))

    if filename == None:
        return paplista
    else:
        with open(filename, "w") as outfile:
            outfile.write(json.dumps(paplista, default=str))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Esztergom-Budapesti főegyházmegye papjainak adatai')
    parser.add_argument('--filename', required=False, action="store", default=None,
                        help="JSON to save. If not set, the result will be displayed on screen")

    args = parser.parse_args()

    if args.filename == None:
        print(EBFEM(args.filename, headless = False))
    else:
        EBFEM(args.filename, headless = False)
