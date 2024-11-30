import requests
from bs4 import BeautifulSoup
import re
from tqdm import tqdm
import json
import argparse
import time
from multiprocessing import Pool

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
                print("Failed to fetch the website.")
        except:
            try:
                response = requests.get(link)
                if response.status_code == 200:
                    html_content = response.content
                else:
                    print("Failed to fetch the website.")
            except:
                print("Big error")
                return

        soup = BeautifulSoup(html_content, 'html.parser').get_text().splitlines()
        papok = []
        for row in soup:
            for title in titles:
                if title[0]+":" in row:
                    for ember in row.split(" és "):
                        try:
                            name = ember.split(":")[-1].strip().split(",")[0].strip()
                            name = " ".join([nt for nt in name.split(" ") if nt[0].isupper()])
                            name = name.split("P.")[-1].strip()
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
                                            "retired": None
                                        })
                        except:
                            print(f"{link} - {row}")
            if "P." in row:
                name = row.strip().split(" és")[0].split(":")[-1].strip()
                if name not in [p["name"] for p in papok]:
                    name = row.split("P.")[1].strip()
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
                                    "retired": None
                                })
        return papok


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
