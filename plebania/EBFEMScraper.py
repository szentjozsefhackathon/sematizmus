import requests
from bs4 import BeautifulSoup
import re
from tqdm import tqdm
import json
import argparse
import datetime
from tqdm.contrib.concurrent import process_map
import urllib3
from getPriest import get_priest
urllib3.disable_warnings(category=urllib3.exceptions.InsecureRequestWarning)

def phone_format(phone, mobile):
    if phone == None and mobile == None: return []
    phones = []
    if phone != None:
        phone = phone.replace(" ", "").replace("-", "").replace("/", "")
        for p in phone.split(","):
            _phone = f"0036{p}"
            _phone = _phone.split("(")[0].strip()
            phones.append(_phone)
    if mobile != None:
        mobile = mobile.replace(" ", "").replace("-", "").replace("/", "")
        for m in mobile.split(","):
            _mobile = f"0036{m}"
            _mobile = _mobile.split("(")[0].strip()
            phones.append(_mobile)
    
    phones = [p for p in phones if re.match(r'^0036\d+$', p)]

    return phones

def processParish(link):
        try: # Kétszeri próbálkozásra szokott menni
            response = requests.get(link, verify=False)
            if response.status_code == 200:
                html_content = response.content
            else:
                print(f"{link} - Failed to fetch the website.")
        except:
            try:
                response = requests.get(link, verify=False)
                if response.status_code == 200:
                    html_content = response.content
                else:
                    print(f"{link} - Failed to fetch the website.")
            except:
                print(f"{link} - Big error")
                return


        soup = BeautifulSoup(html_content, 'html5lib')
        if "templomigazgató" in soup.text.lower():
            return None
        if "kápolnaigazgatóság" in soup.text.lower():
            return None
        parishioner = None
        phones = None
        websites = []
        postalCode = None
        settlement = None
        address = None
        emails = []
        mobiles = None
        for fs in soup.select("fieldset"):
            if "Lelkipásztorok" in fs.find("legend").text:
                if "ellátja" in fs.text.lower():
                    return None
                for p in fs.select("p"):
                    for br in p.find_all("br"):
                        br.replace_with("\n")
                    if "plébános" in p.text.lower() or "plébániai kormányzó" in p.text.lower():
                        parishioner = get_priest(p.find("a")["href"], p.text.splitlines()[0].split(":")[1].strip())
            if "Plébánia" in fs.find("legend").text:
                for p in fs.select("p"):
                    for br in p.find_all("br"):
                        br.replace_with("\n")
                    for row in p.get_text().splitlines():
                        if row.startswith("Cím:"):
                            try: 
                                fullAddress = row.split(":")[-1].strip()
                                postalCode = fullAddress.split(" ")[0]
                                settlement = fullAddress.split(",")[0].split(" ")[1]
                                address = fullAddress.split(",")[1].strip()
                            except:
                                print(f"{link} - {row} - Cím feldolgozási hiba")
                                continue
                        if row.startswith("Telefon:"):
                            phones = row.split(":")[1].strip()
                        if row.startswith("Weboldal:"):
                            websites = ":".join(row.split(":")[1:]).strip().replace(" ","").split(",")
                        if row.startswith("E-mail:"):
                            emails = ":".join(row.split(":")[1:]).strip().replace(" ","").split(",")
                        if row.startswith("Mobil:"):
                            mobiles = row.split(":")[1].strip()
        
        return {
            "name": soup.select_one(".adatlap h1").text, # A plébánia neve
            "parishioner": parishioner, # A plébános
            "src": link,
            "phones": phone_format(phones, mobiles), # Telefonszám
            "websites": websites, # Honlap
            "postalCode": postalCode, # Irányítószám
            "settlement": settlement, # Település
            "address": address, # Cím
            "emails": emails
        }



def EBFEM(filename=None, year=None):
    # Replace this with the URL of the website you want to scrape
    url = 'https://www.esztergomi-ersekseg.hu/plebaniak'
    response = requests.get(url, verify=False)
    # Check if the request was successful
    if response.status_code == 200:
        html_content = response.content
    else:
        print(f"{url} - Failed to fetch the website.")

    # Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(html_content, 'html5lib')

    plebaniak = []
    for plebania in soup.select(".hirbox h3 a"):
        plebaniak.append(f"https://www.esztergomi-ersekseg.hu/{plebania['href']}")

    plebanialista = process_map(processParish, plebaniak)
    plebanialista = [p for p in plebanialista if p != None]

    if filename == None: return plebanialista
    else:
        with open(filename, "w") as outfile:
            outfile.write(json.dumps(plebanialista, default=str))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                        description='Esztergom-Budapesti főegyházmegye plébániáinak adatai')
    parser.add_argument('--filename', required=False, action="store", default=None, help="JSON to save. If not set, the result will be displayed on screen")

    args = parser.parse_args()

    if args.filename==None: print(EBFEM(args.filename))
    else: EBFEM(args.filename)