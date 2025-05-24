import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import json
import argparse
import datetime
from orderAbbreviation import orderAbbreviation
from deleteDr import deleteDr
import time
from SZHEM_ArchivScraper import SZHEM_A
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
    reszek = [d.strip().split(".")[0] for d in datum.split(" ")]
    return datetime.date(int(reszek[0]), honapok[reszek[1]], int(reszek[2]))

def processPriest(link, deacon):
    try:  # Kétszeri próbálkozásra szokott menni
        response = requests.get(link, verify=False)
        if response.status_code == 200:
            html_content = response.content
        else:
            print(f"{link} - Failed to fetch the website.")
    except:
        time.sleep(5)
        response = requests.get(link, verify=False)
        if response.status_code == 200:
            html_content = response.content
        else:
            print(f"{link} - Failed to fetch the website.")
            return

    soup = BeautifulSoup(html_content, 'html.parser')
    
    img = soup.select_one(".lelkipasztorKepNagy").get("src") if soup.select_one(".lelkipasztorKepNagy") else (soup.select_one(".KepNagy").get("src") if soup.select_one(".KepNagy") else None)
    if img == "https://martinus.hu//dokumentumtar/lelkipasztor/lelkipasztor.svg":
        img = None

    return {
        "name": soup.select_one(".lelkipasztorNagyNev").text.strip().title() if soup.select_one(".lelkipasztorNagyNev") else (soup.select_one(".mainContentText h2").text.strip().title() if soup.select_one(".mainContentText h2") else None),
        "ordination": str2date(soup.select_one(".datum_ertek").text.strip()) if soup.select_one(".datum_ertek") else None,
        "deacon": deacon,
        "src": link,
        "bishop": link == "https://martinus.hu/hu/nev-es-cimtar/lelkipasztorok/fekete-szabolcs-benedek" or link == "https://martinus.hu/hu/nev-es-cimtar/lelkipasztorok/szekely-janos-dr",
        "img": img,
        "dutyStation": soup.select_one("#lelkipasztorKepDiv .capitalize").text.strip() if soup.select_one("#lelkipasztorKepDiv .capitalize") else None,
        "retired": "nyugállományban" in soup.text.lower()
    }

@deleteDr
@orderAbbreviation
def SZHEM_current(year=None):
    sources = [
        {
            "url": "https://martinus.hu/hu/nev-es-cimtar/lelkipasztorok",
            "deacon": False
        },
        {
            "url": "https://martinus.hu/hu/nev-es-cimtar/allando-diakonusok",
            "deacon": True
        },
    ]
    paplista = []
    papok = []
    for source in sources:
        time.sleep(5)
        response = requests.get(source["url"], verify=False)
        if response.status_code == 200:
            html_content = response.content
        else:
            print(f"{source['url']} - Failed to fetch the website.")

        soup = BeautifulSoup(html_content, 'html.parser')

        for pap in soup.select("#lelkipasztorokHasabok a"):
            link = pap.get("href")
            if "https://martinus.hu/" not in link:
                link = "https://martinus.hu/" + link
            papok.append({
                "url": link,
                "deacon": source["deacon"]
            })
    
    for pap in tqdm(papok):
        time.sleep(5)
        paplista.append(processPriest(pap["url"], pap["deacon"]))

    paplista = list(filter(lambda x: x is not None, paplista))
    return paplista

def SZHEM(filename=None, year=None):
    paplista = SZHEM_current(year)
    archiv = SZHEM_A()
    for i in range(len(paplista)):
        for archivPap in archiv:
            if paplista[i]["name"] == archivPap["name"] and paplista[i]["ordination"] == archivPap["ordination"]:
                paplista[i]["birth"] = archivPap.get("birth")
                break
    
    if filename is None:
        return paplista
    else:
        with open(filename, "w") as outfile:
            json.dump(paplista, outfile, indent=4, default=str)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Szombathelyi egyházmegye papjainak adatai')
    parser.add_argument('--filename', required=False, action="store", default=None,
                        help="JSON to save. If not set, the result will be displayed on screen")

    args = parser.parse_args()

    if args.filename == None:
        print(SZHEM(args.filename))
    else:
        SZHEM(args.filename)
