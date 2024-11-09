import requests
from bs4 import BeautifulSoup
import re
from tqdm import tqdm
import json
import argparse
import datetime
import urllib3
urllib3.disable_warnings(category=urllib3.exceptions.InsecureRequestWarning)

honapok = {
    "jan": 1,
    "feb": 2,
    "márc": 3,
    "ápr": 4,
    "máj": 5,
    "jún": 6,
    "júl": 7,
    "aug": 8,
    "szept": 9,
    "okt": 10,
    "nov": 11,
    "dec": 12,
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
    "december": 12,
    "01": 1,
    "02": 2,
    "03": 3,
    "04": 4,
    "05": 5,
    "06": 6,
    "07": 7,
    "08": 8,
    "09": 9,
    "10": 10,
    "11": 11,
    "12": 12,
    "júni": 6,
    "jan": 1,
    "febr": 2,
    "márc": 3,
    "ápr": 4,
    "máj": 5,
    "jún": 6,
    "júl": 7,
    "aug": 8,
    "szept": 9,
    "okt": 10,
    "nov": 11,
    "dec": 12
}

def str2date(datum):
    if datum == "1968.okt. 7.":
        return datetime.date(1968,10,7)
    if datum == "1980. nov .22.":
        return datetime.date(1980,11,22)
    if datum == "1997.03.14.":
        return datetime.date(1997,3,14)
    if datum == "1945.febr. 14.":
        return datetime.date(1945,2,14)
    if datum == "1958": # ft. Figeczki Balázs
        return datetime.date(1958,11,9)
    if datum == "1947.":
        return datetime.date(1947,11,24)
    if datum == "1941máj 24.":
        return datetime.date(1941,5,24)
    if datum == "1985.jún.15.":
        return datetime.date(1985,6,15)

    datum = datum.replace(".", ". ").replace("  ", " ")
    reszek = [d.split(".")[0].strip() for d in datum.split(" ")]
    return datetime.date(int(reszek[0]), honapok[reszek[1]], int(reszek[2]))

def DNYEM(filename=None, year=None):
    url = 'https://www.dnyem.hu/papjaink/'
    response = requests.get(url, verify=False)
    if response.status_code == 200:
        html_content = response.content
    else:
        print("Failed to fetch the website.")

    soup = BeautifulSoup(html_content, 'html.parser')

    papok = []

    selectors = [".ticss-3566876d", ".ticss-d89e1c07", ".ticss-fcfbf173", ".uagb-block-fb335e5e", ".ticss-24c5c512"]

    for selector in selectors:
        for pap in soup.select_one(selector).findAll("h6"):
            papok.append(pap.select_one('a')['href'])
    
    firstLine = 0
    paplista = []
    ordinationFailed = []
    for pap in tqdm(papok):  # Nézze meg az összes pap linkjét
        try:  # Kétszeri próbálkozásra szokott menni
            response = requests.get(pap, verify=False)
            if response.status_code == 200:
                html_content = response.content
            else:
                print("Failed to fetch the website.")
        except:
            try:
                response = requests.get(pap, verify=False)
                if response.status_code == 200:
                    html_content = response.content
                else:
                    print("Failed to fetch the website.")
            except:
                print("Big error")
                continue

        soup = BeautifulSoup(html_content, 'html.parser')
        firstLine = True
        imgSrc = soup.select_one("#main img").get("src")
        name = " ".join([n for n in soup.select_one("#main article h1").text.split(" ") if n[0].isupper()])
        if name == "P. Maczák Béla MI":
            paplista.append({
                "name": name,
                "birth": datetime.date(1980,5,16),
                "img": imgSrc,
                "src": pap
            })
            continue
        for sor in soup.select_one("#main table").findAll("tr"):
            if firstLine and name !="Mészáros Zsolt":
                firstLine = False
                continue

            if name == "Molnár József":
                paplista.append({
                    "name": name,
                    "birth": 1968,
                    "img": imgSrc,
                    "src": pap
                })
                break
            if name == "Sári András":
                paplista.append({
                    "name": name,
                    "birth": 1971,
                    "img": imgSrc,
                    "src": pap
                })
                break

            print(name)
            try:
                sor.select_one("br").replace_with("\n")
            except: pass
            if len(sor.text.split("\n")[0].split(", ")) < 2:
                break # Ft. Czele József atyára tekintettel
            ordination = None
            for alsor in sor.text.split("\n"):
                if "szentelték" in alsor.lower():
                    try:
                        ordination = str2date(alsor.split(", ")[1])
                    except:
                        pass
            
            if ordination == None:
                ordinationFailed.append(name)

            paplista.append({
                "name": name,
                "birth": str2date(sor.text.split("\n")[0].split(", ")[1]),
                "ordination": ordination,
                "img": imgSrc,
                "src": pap,
                "retired": "nyugállományban" in soup.text.lower() or "nyugdíjas" in soup.text.lower(),
                "bishop": "püspök" in soup.select_one("#main article h1").text,
                "deacon": None
            })
            break
    print(ordinationFailed)
    print(f"Szentelés hiba: {len(ordinationFailed)}")

    if filename == None:
        return paplista
    else:
        with open(filename, "w") as outfile:
            outfile.write(json.dumps(paplista, default=str))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Debrecen-Nyíregyházi egyházmegye papjainak adatai')
    parser.add_argument('--filename', required=False, action="store", default=None,
                        help="JSON to save. If not set, the result will be displayed on screen")

    args = parser.parse_args()

    if args.filename == None:
        print(DNYEM(args.filename))
    else:
        DNYEM(args.filename)
