import requests
from bs4 import BeautifulSoup
import re
from tqdm import tqdm
import json
import argparse
import time
from multiprocessing import Pool

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

        soup = BeautifulSoup(html_content, 'html.parser').select_one(".entry-content").get_text().splitlines()
        papok = []
        for row in soup:
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
                                    "retired": None
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
                                    "retired": None
                                })
                except:
                    print(f"{link} - {row}")
        return papok


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
