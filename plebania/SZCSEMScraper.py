import requests
from bs4 import BeautifulSoup
import re
from tqdm import tqdm
import json
import argparse
import datetime
from multiprocessing import Pool

from getPriest import get_priest
#TODO: Algyő, Újszeged honlap
def phone_format(phone):
    phones = []
    if phone == None:
        return []
    phone = phone.replace("és", ";").replace("/", "").replace(" ", "").replace("-","").replace("+36","")
    for p in phone.split(";"):
        phones.append(f"0036{p.strip()}")
    return phones

def processDeanDistrict(link):
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
        plebaniak = []
        for p in soup.select("p"):
            if "templomigazgató" in p.text.lower():
                continue
            rows = p.get_text().splitlines()
            
            if rows[0].startswith("F.") or rows[0].startswith("P."):
                continue
            parishioner = None
            phones = None
            website = None
            postalCode = None
            settlement = None
            address = None
            email = None
            name = None
            if "*" in rows[0]:
                continue
            try:
                name = rows[0].split(".")[1].strip().title()
                if name == "Apátfalva":
                    continue
            except:
                if rows[0] == "Szent Mihály Plébánia":
                    name = "Apátfalva"
                else:
                    print(f"{link} - {rows[0]} - Név")
                    continue
            if ":" in name:
                continue
            if name.startswith("P.") or name.startswith("F."):
                continue
            if "Esperesség" in name:
                continue
            if name == "":
                continue
            if name == "Hu/":
                continue
            firstRow = True
            for row in rows:
                if firstRow:
                    firstRow = False
                    continue
                addressStarts = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]
                parishionerStarts = ["Plébános", "Plébániai kormányzó"]
                for start in addressStarts:
                    try: 
                        if address != None:
                            break
                        if row.startswith(start):
                            fullAddress = row.strip()
                            postalCode = fullAddress.split(" ")[0]
                            settlement = fullAddress.split(" ")[1].split(",")[0].strip()
                            address = ' '.join(fullAddress.split(" ")[2:]).strip()
                            break
                    except:
                        print(f"{link} - {row} - cím")
                        break
                for start in parishionerStarts:
                    if row.startswith(start):
                        parishioner = get_priest(link, row.split(":")[1].strip(), dontFind=True)
                        break
                if row.startswith("Világhálós oldal:"):
                    website = ":".join(row.split(":")[1:]).strip()
                if row.startswith("E-mail:") or row.startswith("Email:"):
                    email = row.split(":")[1].strip()
                if row.startswith("Tel.:") or row.startswith("Mobil:"):
                    phones = row.split(":")[1].strip()
            try: 
                plebaniak.append({
                    "name": name, # A plébánia neve
                    "parishioner": parishioner, # A plébános
                    "src": link,
                    "emails": [email], # E-mail
                    "phones": phone_format(phones), # Telefonszám
                    "websites": [website], # Honlap
                    "postalCode": postalCode, # Irányítószám
                    "settlement": settlement, # Település
                    "address": address # Cím
                })
            except:
                print(f"{link} - {row}")
        return plebaniak


def SZCSEM(filename=None, year=None):
    deanDistricts = [
        "http://szeged-csanad.hu/szarvasi-esperesseg/", 
        "http://szeged-csanad.hu/gyulai-esperesseg/",
        "http://szeged-csanad.hu/oroshazi-esperesseg/",
        "http://szeged-csanad.hu/szentesi-esperesseg/",
        "http://szeged-csanad.hu/kisteleki-esperesseg/",
        "http://szeged-csanad.hu/makoi-esperesseg/",
        "http://szeged-csanad.hu/szegedi-esperesseg/"]
    
    plebanialista = []

    with Pool() as p:
        plebanialista = p.map(processDeanDistrict, [(d) for d in deanDistricts])

    plebanialista = sum([x for x in plebanialista if x is not None], [])



    if filename == None:
        return plebanialista
    else:
        with open(filename, "w") as outfile:
            outfile.write(json.dumps(plebanialista, default=str))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Szeged-Csanádi egyházmegye plébániáinak adatai')
    parser.add_argument('--filename', required=False, action="store", default=None,
                        help="JSON to save. If not set, the result will be displayed on screen")

    args = parser.parse_args()

    if args.filename == None:
        print(SZCSEM(args.filename))
    else:
        SZCSEM(args.filename)
