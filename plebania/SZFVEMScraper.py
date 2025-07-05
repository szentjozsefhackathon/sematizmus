import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import  json
import argparse
from getPriest import get_priest
import urllib3
urllib3.disable_warnings(category=urllib3.exceptions.InsecureRequestWarning)


def SZFVEM(filename=None, year=None):

    response = requests.get("https://www.szfvar.katolikus.hu/adattar/plebaniak", verify=False)
    if response.status_code == 200:
        html_content = response.content
    else:
        print(f"Székesfehérvár Failed to fetch the website.")
    soup = BeautifulSoup(html_content, 'html5lib')
    plebanialista = []
    for plebania in tqdm(soup.select_one(".adattar").select(".listadoboz")):
        if "látja el" in plebania.text.lower():
            continue
        if "templomigazgató" in plebania.text.lower():
            continue
        name = plebania.select_one("h3").text.split("Plébánia")[0].strip()
        src = "https://www.szfvar.katolikus.hu" + plebania.select_one("h3 a")["href"]
        postalCode = ""
        settlement = ""
        address = ""
        phones = []
        parishioner = {}
        websites = []
        emails = []
        for br in plebania.find_all("br"):
            br.replace_with("\n")
        rows = plebania.get_text().splitlines()
        parishioner_name = ""
        print(rows)
        for row in rows:
            if "cím" in row.lower():
                try: 
                    fullAddress = row.split(":")[-1].strip()
                    postalCode = fullAddress.split(" ")[0]
                    settlement = fullAddress.split(",")[0].split(" ")[1]
                    address = fullAddress.split(",")[1].strip()
                except:
                    print(f"{src} - {row} - Cím feldolgozási hiba")
                    continue
            if "telefon" in row.lower():
                phones.append(row.split(":")[-1].strip())
            if "mobil" in row.lower():
                phones.append(row.split(":")[-1].strip())
            if "weboldal" in row.lower():
                websites = row.split(":")[-1].strip().replace(" ","").split(",")
            if "e-mail" in row.lower():
                emails = row.split(":")[-1].strip().replace(" ","").split(",")
            if "plébános" in row.lower() or "plébániai kormányzó" in row.lower():
                parishioner_name = row.split(":")[-1].strip()
        for a in plebania.select("a"):
            if a.text==parishioner_name:
                parishioner = get_priest("https://www.szfvar.katolikus.hu" + a["href"], parishioner_name)
                break
        if parishioner == {}:
            parishioner = get_priest("https://www.szfvar.katolikus.hu/plebanosok", parishioner_name)

        phones = [f"0036{p.replace('*','').replace(' ', '').replace('(','').replace(')','').replace('-','').replace('/','').strip()}" for p in phones if p.strip() != ""]
        emails = [email.strip() for email in emails if email.strip() != ""]
        plebanialista.append({
            "name": name, # A plébánia neve
            "parishioner": parishioner, # A plébános
            "src": src,
            "phones": phones, # Telefonszám
            "websites": websites, # Honlap
            "postalCode": postalCode, # Irányítószám
            "settlement": settlement, # Település
            "address": address, # Cím
            "emails": emails
        })




        
    
    if filename == None: return plebanialista
    else:
        with open(filename, "w") as outfile:
            outfile.write(json.dumps(plebanialista, default=str))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                        description='Székesfehérvári egyházmegye plébániáinak adatai')
    parser.add_argument('--filename', required=False, action="store", default=None, help="JSON to save. If not set, the result will be displayed on screen")

    args = parser.parse_args()

    if args.filename==None: print(SZFVEM(args.filename))
    else: SZFVEM(args.filename)