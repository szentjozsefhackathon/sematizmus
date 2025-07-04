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
    if phone == None: return []
    phones = []
    phone = phone.replace("vagy", ";").replace(" ", "").replace("-", "")
    for p in phone.split(";"):
        _phone = "0036"
        _phone += p.split(")")[0].replace("(","")
        _phone += p.split(")")[1]
        _phone = _phone.split("(")[0]
        phones.append(_phone)

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
        parishioner = None
        phones = None
        website = None
        postalCode = None
        settlement = None
        address = None
        for sor in soup.select_one(".kpriest-content-right table").findAll("tr"): # Papi táblázat
            if sor.select_one("th").text == "Plébánia vezető":
                plink = sor.select_one("td a")["href"]
                parishioner = get_priest(plink, sor.select_one("td a").text.strip())
            if sor.select_one("th").text == "Telefonszám":
                phones = sor.select_one("td").text.strip()
            if sor.select_one("th").text == "Honlap":
                website = sor.select_one("td a")["href"].strip()
            if sor.select_one("th").text == "Cím":
                fullAddress = sor.select_one("td").text.strip()
                postalCode = fullAddress.split(" ")[0] # Itt a postai irányítószám
                settlement = fullAddress.split(",")[0].split(" ")[1] # Település
                address = fullAddress.split(",")[1].strip() # Cím
        
        return {
            "name": soup.select_one(".page-header h2").text, # A plébánia neve
            "parishioner": parishioner, # A plébános
            "src": link,
            "phones": phone_format(phones), # Telefonszám
            "websites": [website], # Honlap
            "postalCode": postalCode, # Irányítószám
            "settlement": settlement, # Település
            "address": address # Cím
        }



def PEM(filename=None, year=None):
    # Replace this with the URL of the website you want to scrape
    url = 'https://pecsiegyhazmegye.hu/egyhazmegye/plebaniak'
    response = requests.get(url, verify=False)
    # Check if the request was successful
    if response.status_code == 200:
        html_content = response.content
    else:
        print(f"{url} - Failed to fetch the website.")

    # Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    plebaniak = []
    firstLine = True # Az első sor csak fejléc
    for sor in soup.select_one(".item-page table").tbody.findAll("tr"): # Táblázat sorainak keresése
        if firstLine:
            firstLine = False
            continue

        plebaniak.append(f"https://pecsiegyhazmegye.hu{sor.findAll('td')[0].select_one('a')['href']}") 

    plebanialista = process_map(processParish, plebaniak)
    plebanialista = [p for p in plebanialista if p != None]

    if filename == None: return plebanialista
    else:
        with open(filename, "w") as outfile:
            outfile.write(json.dumps(plebanialista, default=str))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                        description='Pécsi egyházmegye plébániáinak adatai')
    parser.add_argument('--filename', required=False, action="store", default=None, help="JSON to save. If not set, the result will be displayed on screen")

    args = parser.parse_args()

    if args.filename==None: print(PEM(args.filename))
    else: PEM(args.filename)