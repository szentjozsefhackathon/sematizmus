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

def phone_format(phone):
    if phone == None:
        return []
    
    phones = ["0036"+phone.replace("+36", "").replace("/", "").replace(" ", "").replace("-", "")]

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
        if "ellátja" in soup.text.lower():
            return None

        parishioner = None
        phones = None
        websites = []
        postalCode = None
        settlement = None
        address = None
        emails = []
        for p in soup.select(".entry-content p"):
            for br in p.find_all("br"):
                br.replace_with("\n")
            for row in p.get_text().splitlines():
                if row.startswith("Plébános:") or row.startswith("Plébániai kormányzó:"):
                    try:
                        parishioner = get_priest(None, row.split(":")[1].strip(), True)
                    except:
                        print(f"{link} - {row} - Plébános feldolgozási hiba")
                if row.startswith("Telefonszám:"):
                    phones = row.split(":")[1].strip()
                if row.startswith("Honlap:"):
                    websites = ":".join(row.split(":")[1:]).strip().replace(" ","").split(",")
                if row.startswith("Cím:"):
                    try: 
                        fullAddress = row.split(":")[-1].strip()
                        postalCode = fullAddress.split(" ")[0]
                        settlement = fullAddress.split(" ")[1]
                        address = " ".join(fullAddress.split(" ")[2:]).strip()
                    except:
                        print(f"{link} - {row} - Cím feldolgozási hiba")
                if row.startswith("Email:"):
                    emails = ":".join(row.split(":")[1:]).strip().replace(" ","").split(",")

        
        return {
            "name": soup.select_one(".entry-title").text, # A plébánia neve
            "parishioner": parishioner, # A plébános
            "src": link,
            "phones": phone_format(phones), # Telefonszám
            "websites": websites, # Honlap
            "postalCode": postalCode, # Irányítószám
            "settlement": settlement, # Település
            "address": address, # Cím
            "emails": emails
        }



def DNYEM(filename=None, year=None):
    # Replace this with the URL of the website you want to scrape
    url = 'https://dnyem.hu/plebaniak_/'
    response = requests.get(url, verify=False)
    # Check if the request was successful
    if response.status_code == 200:
        html_content = response.content
    else:
        print(f"{url} - Failed to fetch the website.")

    # Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(html_content, 'html5lib')

    plebaniak = []
    for plebania in soup.select("article h4 a"):
        plebaniak.append(plebania['href'])

    plebanialista = process_map(processParish, plebaniak)
    plebanialista = [p for p in plebanialista if p != None]

    if filename == None: return plebanialista
    else:
        with open(filename, "w") as outfile:
            outfile.write(json.dumps(plebanialista, default=str))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                        description='Debrecen-Nyíregyházi egyházmegye plébániáinak adatai')
    parser.add_argument('--filename', required=False, action="store", default=None, help="JSON to save. If not set, the result will be displayed on screen")

    args = parser.parse_args()

    if args.filename==None: print(DNYEM(args.filename))
    else: DNYEM(args.filename)