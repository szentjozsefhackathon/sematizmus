import requests
from bs4 import BeautifulSoup
import re
from tqdm import tqdm
import json
import argparse
import datetime
from multiprocessing import Pool
from orderAbbreviation import orderAbbreviation
from deleteDr import deleteDr

def processDeanDistrict(link):
        titles = [
            ("Adminisztrátor", False), 
            ("Állandó diakónus", True),
            ("Plébános", False),
            ("Pléb. korm.", False),
            ("Plébániai kormányzó", False),
            ("Káplán", False),
            ("Templomigazgató", False),
            ("Administrator is spiritualibus", False),
            ("Mb. adminisztrátor", False),
            ("Kisegítő lelkész", False),
            ("Plébánia vezető", False),
            ("Kisegítő lelkészek", False)
            ]
        try:
            response = requests.get(link)
            if response.status_code == 200:
                html_content = response.content
            else:
                print(f"{link} - Failed to fetch the website.")
        except:
            try:
                response = requests.get(link)
                if response.status_code == 200:
                    html_content = response.content
                else:
                    print(f"{link} - Failed to fetch the website.")
            except:
                print(f"{link} - Big error")
                return

        soup = BeautifulSoup(html_content, 'html5lib').select_one("article div div")
        papok = []
        dutyStation = None
        for div in soup.select("div"):
            if len(div.text.split(":")) == 1:
                for strong in div.select("strong"):
                    dutyStation = strong.text.split(".")[-1].strip().replace(" - ", "-").title()
            rows = div.text.splitlines()
            for row in rows:
                for title in titles:
                    if title[0]+":" in row:
                        for ember in row.split(" és "):
                            try:
                                name = ember.split(":")[-1].strip().split(",")[0].strip()
                                name = name.replace("Sch.P", "SchP")
                                name = " ".join([nt for nt in name.split(" ") if nt[0].isupper()])
                                name = name.split("P.")[-1].strip()
                                name = name.split("Mons.")[-1].strip()
                                if name == "":
                                    continue
                                papok.append({
                                                "name": name,
                                                "birth": None,
                                                "img": None,
                                                "src": link,
                                                "ordination": None,
                                                "bishop": False,
                                                "deacon": title[1],
                                                "retired": None,
                                                "dutyStation": dutyStation
                                            })
                            except:
                                print(f"{link} - {row} - {dutyStation}")
                if "P." in row:
                    name = row.strip().split(" és")[0].split(":")[-1].strip()
                    name = name.replace("Sch.P.", "SchP")
                    name = name.split("P.")[1].strip()
                    name = name.split("Mons.")[-1].strip()
                    if not name in [p["name"] for p in papok]:
                        name = " ".join([nt for nt in name.split(" ") if nt[0].isupper()])
                        if name == "":
                            continue
                        papok.append({
                                        "name": name,
                                        "birth": None,
                                        "img": None,
                                        "src": link,
                                        "ordination": None,
                                        "bishop": False,
                                        "deacon": False,
                                        "retired": None,
                                        "dutyStation": dutyStation
                                    })
        return papok
@deleteDr
@orderAbbreviation
def KKFEM(filename=None, year=None):
    deanDistricts = [
        "https://asztrik.hu/index.php/teruleti-beosztas/kalocsai-esperesi-kerulet",
        "https://asztrik.hu/index.php/teruleti-beosztas/keceli-esperesi-kerulet",
        "https://asztrik.hu/index.php/teruleti-beosztas/bacsalmasi-esperesi-kerulet",
        "https://asztrik.hu/index.php/teruleti-beosztas/janoshalmi-esperesi-kerulet",
        "https://asztrik.hu/index.php/teruleti-beosztas/bajai-esperesi-kerulet",
        "https://asztrik.hu/index.php/teruleti-beosztas/hajosi-esperesi-kerulet",
        "https://asztrik.hu/index.php/teruleti-beosztas/kecskemeti-esperesi-kerulet",
        "https://asztrik.hu/index.php/teruleti-beosztas/felegyhazi-esperesi-kerulet",
        "https://asztrik.hu/index.php/teruleti-beosztas/majsai-esperesi-kerulet",
        "https://asztrik.hu/index.php/teruleti-beosztas/solti-esperesi-kerulet"
    ]
    
    paplista = []
    hibasak = []

    paplista = []
    with Pool() as p:
        paplista = p.map(processDeanDistrict, [(d) for d in deanDistricts])

    paplista = sum([x for x in paplista if x is not None], [])

    paplista.append({
        "name": "Dr. Bábel Balázs",
        "birth": datetime.date(1950,10,18),
        "ordination": datetime.date(1976,6,19),
        "bishop": True,
        "src": "https://asztrik.hu/index.php/fopasztor",
        "img": "https://asztrik.hu/sites/default/files/content/Babel_Balazs_ersek_2020_web.jpg"
    })
    if filename == None:
        return paplista
    else:
        with open(filename, "w") as outfile:
            outfile.write(json.dumps(paplista, default=str))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Kalocsa-Kecskeméti főegyházmegye papjainak adatai')
    parser.add_argument('--filename', required=False, action="store", default=None,
                        help="JSON to save. If not set, the result will be displayed on screen")

    args = parser.parse_args()

    if args.filename == None:
        print(KKFEM(args.filename))
    else:
        KKFEM(args.filename)
