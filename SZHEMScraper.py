import requests
from bs4 import BeautifulSoup
import re
from tqdm import tqdm
import  json
import argparse
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

def SZHEM(filename=None, year=None):
    url = "https://www.martinus.hu/nev-es-cimtar/lelkipasztorok?oldal="
    papok = []
    def papkereso(link):
        response = requests.get(link, verify=False)
        if response.status_code == 200:
            html_content = response.content
        else:
            print("Failed to fetch the website.")
        soup = BeautifulSoup(html_content, 'html.parser')
        _papok = []
        for pap in soup.select_one(".content ul").select("li"):
            _papok.append(pap.select_one("a")["href"])
        
        return _papok
    
    for i in tqdm(range(6,-1,-1)):
        papok += papkereso(f"{url}{i}")




    paplista = []
    for pap in tqdm(papok): # Nézze meg az összes pap linkjét
        try: # Kétszeri próbálkozásra szokott menni
            response = requests.get(f"https://www.martinus.hu{pap}", verify=False)
            if response.status_code == 200:
                html_content = response.content
            else:
                print("Failed to fetch the website.")
        except:
            try:
                response = requests.get(f"https://www.martinus.hu{pap}", verify=False)
                if response.status_code == 200:
                    html_content = response.content
                else:
                    print("Failed to fetch the website.")
            except:
                print("Big error")
                pass


        soup = BeautifulSoup(html_content, 'html.parser')
        nev = soup.select_one("#main .content h1").text
        if "+" in nev:
            continue

        print(nev)
        imgSrc = ""
        try:
            imgSrc = "https://www.martinus.hu" + soup.select_one(".content img").get("src")
        except:
            pass
        birth = None
        ordination = None

        for sor in soup.select("#main .content p"):
            if "Születési hely, idő:" in sor.text:
                try:
                    birth = str2date(sor.text.split(", ")[-1].strip())
                    
                except: pass
            if "Felszentelés" in sor.text:
                ordination = str2date(sor.text.split(": ")[-1].split(", ")[-1].strip())
        paplista.append({
            "name": nev,
            "birth": birth,
            "img": imgSrc,
            "src": f"https://www.martinus.hu{pap}",
            "retired": "nyugállomány" in soup.text,
            "bishop": "megyéspüspök" in soup.text,
            "ordination": ordination
        })
    if filename == None: return paplista
    else:
        with open(filename, "w") as outfile:
            outfile.write(json.dumps(paplista, default=str))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                        description='Szombathelyi egyházmegye papjainak adatai')
    parser.add_argument('--filename', required=False, action="store", default=None, help="JSON to save. If not set, the result will be displayed on screen")

    args = parser.parse_args()

    if args.filename==None: print(SZHEM(args.filename))
    else: SZHEM(args.filename)