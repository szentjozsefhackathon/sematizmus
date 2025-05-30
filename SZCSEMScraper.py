import requests
from bs4 import BeautifulSoup
import re
from tqdm import tqdm
import json
import argparse
import datetime
from multiprocessing import Pool
from deleteDr import deleteDr
from orderAbbreviation import orderAbbreviation

def processDeanDistrict(link):
        titles = ["Plébános", "Plébániai kormányzó", "Káplán", "Kisegítő lelkész", "Templomigazgató"]
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

        soup = BeautifulSoup(html_content, 'html.parser').select_one(".entry-content")
        papok = []
        dutyStation = None
        for p in soup.select("p"):
            rows = p.get_text().splitlines()
            try: 
                if rows[0].startswith("F.") or rows[0].startswith("P."):
                    pass
                else: dutyStation = rows[0].split(".")[1].strip().title()
            except: pass
            for row in rows:
                if any(title+":" in row for title in titles):
                    try: 
                        papok.append({
                                        "name": row.split(":")[1].split("P.")[-1].strip(),
                                        "birth": None,
                                        "img": None,
                                        "src": link,
                                        "ordination": None,
                                        "bishop": False,
                                        "deacon": False,
                                        "retired": None,
                                        "dutyStation": dutyStation
                                    })
                    except:
                        print(f"{link} - {row}")
                elif "P." in row:
                    try:
                        papok.append({
                                        "name": row.split("P.")[-1].strip(),
                                        "birth": None,
                                        "img": None,
                                        "src": link,
                                        "ordination": None,
                                        "bishop": False,
                                        "deacon": False,
                                        "retired": None,
                                        "dutyStation": dutyStation
                                    })
                    except:
                        print(f"{link} - {row}")
        return papok

@deleteDr
@orderAbbreviation
def SZCSEM(filename=None, year=None):
    deanDistricts = [
        "http://szeged-csanad.hu/szarvasi-esperesseg/", 
        "http://szeged-csanad.hu/gyulai-esperesseg/",
        "http://szeged-csanad.hu/oroshazi-esperesseg/",
        "http://szeged-csanad.hu/szentesi-esperesseg/",
        "http://szeged-csanad.hu/kisteleki-esperesseg/",
        "http://szeged-csanad.hu/makoi-esperesseg/",
        "http://szeged-csanad.hu/szegedi-esperesseg/"]
    
    paplista = []
    hibasak = []

    paplista = []
    with Pool() as p:
        paplista = p.map(processDeanDistrict, [(d) for d in deanDistricts])

    paplista = sum([x for x in paplista if x is not None], [])

    paplista.append({
        "name": "Dr. Kiss-Rigó László",
        "birth": datetime.date(1955,4,6),
        "ordination": datetime.date(1981,6,14),
        "bishop": True,
        "src": "https://hu.wikipedia.org/wiki/Kiss-Rig%C3%B3_L%C3%A1szl%C3%B3",
        "img": "https://upload.wikimedia.org/wikipedia/commons/5/57/KissRigoLaszloFotoThalerTamas.JPG"
    })

    paplista.append({
        "name": "Dr. Kovács József",
        "src": "http://szeged-csanad.hu/puspoki-iroda/"
    })

    if filename == None:
        return paplista
    else:
        with open(filename, "w") as outfile:
            outfile.write(json.dumps(paplista, default=str))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Szeged-Csanádi egyházmegye papjainak adatai')
    parser.add_argument('--filename', required=False, action="store", default=None,
                        help="JSON to save. If not set, the result will be displayed on screen")

    args = parser.parse_args()

    if args.filename == None:
        print(SZCSEM(args.filename))
    else:
        SZCSEM(args.filename)
