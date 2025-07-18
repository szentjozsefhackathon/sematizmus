import requests
from bs4 import BeautifulSoup
import re
from tqdm.contrib.concurrent import process_map
import json
import argparse
from multiprocessing import Pool
from getPriest import get_priest

def processParish(link):
        try:
            response = requests.get(link)
            if response.status_code == 200:
                html_content = response.content
            else:
                print(f"{link} - Failed to fetch the website.")
        except:
                response = requests.get(link)
                if response.status_code == 200:
                    html_content = response.content
                else:
                    print(f"{link} - Failed to fetch the website.")

        soup = BeautifulSoup(html_content, 'html5lib')
        parishioner = {}
        phones = []
        _phones = soup.select_one(".views-field-field-templom-tel .field-content").get_text().replace("/","").replace(" ","").replace(".","").replace("-","").replace(";",",").split("(")[0].strip() if soup.select_one(".views-field-field-templom-tel .field-content") else ""
        for p in _phones.split(","):
            _phone = ""
            for d in p:
                if d.isdigit():
                    _phone += d
            if p.strip() != "":
                phones.append(f"0040{_phone.strip()}")

        emails = [soup.select_one(".views-field-field-templom-email .field-content").get_text().strip()] if soup.select_one(".views-field-field-templom-email .field-content") else []
        name = soup.select_one("h3").get_text() if soup.select_one("h3") else ""
        fullAddress = soup.select_one(".views-field-field-templom-postacim .field-content").get_text() if soup.select_one(".views-field-field-templom-postacim .field-content") else ""
        postalCode = ""
        address = ""
        settlement = ""
        try:
            if fullAddress:
                postalCode = fullAddress.split("–")[0].strip()
                settlement = fullAddress.split("–")[1].split(",")[0].strip().title()
                address = ",".join(fullAddress.split("–")[1].split(",")[1:]).strip()
        except:
            print(f"{link} - {name} - Címfeldolgozás: {fullAddress}")
        for view in soup.select(".view"):
            if "Szolgálatot teljesít:" in (view.select_one(".view-header").get_text()) if view.select_one(".view-header") else "":
                try:
                    for r in view.select(".views-row"):
                        if "plébános" in r.text:
                            a = r.select_one("a")
                            if a == None:
                                continue
                            pName = a.get_text().strip()
                            while pName.count("  ") > 0:
                                pName = pName.replace("  ", " ")
                            parishioner = get_priest(f'https://ersekseg.ro{a["href"]}', pName, True)
                except:
                    print(f"{link} - {name} - Plébános feldolgozási hiba")
                    return None
        if parishioner != {}:
            return {
                        "name": name, # A plébánia neve
                        "parishioner": parishioner, # A plébános
                        "src": link,
                        "emails": list(emails), # E-mail
                        "phones": phones, # Telefonszám
                        "websites": [], # Honlap
                        "postalCode": postalCode, # Irányítószám
                        "settlement": settlement, # Település
                        "address": address # Cím
                    }
        else:
            return None

def processPage(link):
        try:
            response = requests.get(link)
            if response.status_code == 200:
                html_content = response.content
            else:
                print(f"{link} - Failed to fetch the website.")
        except:
                response = requests.get(link)
                if response.status_code == 200:
                    html_content = response.content
                else:
                    print(f"{link} - Failed to fetch the website.")

        soup = BeautifulSoup(html_content, 'html5lib')
        plebaniak = []
        for plebania in  soup.select("#main #content .views-row"):

            if "ellátó plébánia" in plebania.get_text().lower():
                continue
            if "filia" in plebania.get_text().lower():
                continue
            if plebania.select_one("h3 a") is None:
                continue
            plebaniak.append(plebania.select_one("h3 a")["href"])

        return plebaniak

def RO_GYFEM(filename=None, year=None):
    
    plebanialinkek = process_map(processPage, [f"https://ersekseg.ro/hu/templomok-abc-sorrendben?page={i}" for i in range(68)])
    plebanialinkek = sum([x for x in plebanialinkek if x is not None], [])
    plebanialinkek = [f"https://ersekseg.ro{link}" for link in plebanialinkek if link is not None]
    print(plebanialinkek)
    plebanialista = process_map(processParish, plebanialinkek)
    plebanialista = [plebania for plebania in plebanialista if plebania != None]


    if filename == None:
        return plebanialista
    else:
        with open(filename, "w") as outfile:
            outfile.write(json.dumps(plebanialista, default=str))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Gyulafehérvári főegyházmegye plébániáinak adatai')
    parser.add_argument('--filename', required=False, action="store", default=None,
                        help="JSON to save. If not set, the result will be displayed on screen")

    args = parser.parse_args()

    if args.filename == None:
        print(RO_GYFEM(args.filename))
    else:
        RO_GYFEM(args.filename)
