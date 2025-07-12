import requests
from bs4 import BeautifulSoup
import re
from tqdm import tqdm
import  json
import argparse
import datetime
import re
from tqdm.contrib.concurrent import process_map
import urllib3
from getPriest import get_priest

urllib3.disable_warnings(category=urllib3.exceptions.InsecureRequestWarning)


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
        postalCode = ""
        settlement = ""
        address = ""
        parishioner = {}
        phones = []
        websites = []
        emails = []

        for r in soup.select("tr"):
            try:
                if "A parókia címe:" in r.text:
                    fullAddress = r.text.split("A parókia címe:")[-1].strip()
                    if fullAddress:
                        postalCode = fullAddress.split(" ")[0].strip()
                        settlement = fullAddress.split(" ")[1].split(',')[0].strip().title()
                        address = " ".join(fullAddress.split(" ")[2:]).strip()
                if "Telefonszám:" in r.text:
                    phone = r.text.split("Telefonszám:")[-1].strip().replace(" ", "").replace("-", "").replace("/", "").replace("(", "").replace(")", "")
                    if phone != "":
                        phones.append(f"0036{phone}")
                
                if "Saját honlap:" in r.text:
                    website = r.text.split("Saját honlap:")[-1].strip()
                    if website != "":
                        websites.append(website)


            except:
                print(link + " - " + soup.select_one("#parokianev").text)
            
        for s in soup.select("tr.szolgalat td table tr"): 
            if (s.select("td")[0].text.strip().endswith("-") or s.select("td")[0].text.strip() == f"{datetime.date.today().year}") and ("parókus" in s.text.lower() or "szervezőlelkész" in s.text.lower()):
                a = s.select_one('a[href*="?q=pap&"]')
                parishioner = get_priest(a["href"], a.text.strip())

        return {
            "name": soup.select_one("#parokianev").text, # A plébánia neve
            "parishioner": parishioner, # A plébános
            "src": link,
            "phones": phones,
            "websites": websites, # Honlap
            "postalCode": postalCode, # Irányítószám
            "settlement": settlement, # Település
            "address": address, # Cím
            "emails": emails
        }

def NYEM(filename=None, year=None):
    # Replace this with the URL of the website you want to scrape
    url = 'https://www.nyirgorkat.hu/?q=parokiak&egyhazmegye=3&l=hu'
    response = requests.get(url, verify=False)
    # Check if the request was successful
    if response.status_code == 200:
        html_content = response.content
    else:
        print(f"{url} - Failed to fetch the website.")

    # Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(html_content, 'html5lib')
    parokiak = []
    for parokia in soup.select('a[href*="?q=parokia&"]'):
        parokiak.append("https://www.nyirgorkat.hu/"+parokia["href"])
    
    parokialista = process_map(processParish, parokiak)

    parokialista = [pap for pap in parokialista if pap != None]
    parokialista = list({v['src']:v for v in parokialista}.values())
    if filename == None: return parokialista
    else:
        with open(filename, "w") as outfile:
            outfile.write(json.dumps(parokialista, default=str))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                        description='Nyíregyházi egyházmegye parókiáinak adatai')
    parser.add_argument('--filename', required=False, action="store", default=None, help="JSON to save. If not set, the result will be displayed on screen")

    args = parser.parse_args()

    if args.filename==None: print(NYEM(args.filename))
    else: NYEM(args.filename)