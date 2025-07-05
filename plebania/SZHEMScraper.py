import requests
from bs4 import BeautifulSoup
import re
from tqdm import tqdm
import json
import argparse
from tqdm.contrib.concurrent import process_map
import urllib3
from getPriest import get_priest
import time
urllib3.disable_warnings(category=urllib3.exceptions.InsecureRequestWarning)


def processParish(link):
        try: # Kétszeri próbálkozásra szokott menni
            time.sleep(5)
            response = requests.get(link, verify=False)
            if response.status_code == 200:
                html_content = response.content
            else:
                print(f"{link} - Failed to fetch the website.")
        except:
            try:
                time.sleep(5)
                response = requests.get(link, verify=False)
                if response.status_code == 200:
                    html_content = response.content
                else:
                    print(f"{link} - Failed to fetch the website.")
            except:
                print(f"{link} - Big error")
                return


        soup = BeautifulSoup(html_content, 'html5lib')
        if "lelkészség" in soup.select_one("#plebaniaNeve").text.lower():
            return None
        parishioner = {}
        phones = []
        websites = []
        postalCode = ""
        settlement = ""
        address = ""
        emails = []

        fullAddress = soup.select_one("#plebaniaCim").text.strip()
        if fullAddress:
            postalCode = fullAddress.split(" ")[0].strip()
            settlement = fullAddress.split(" ")[1].split(',')[0].strip().title()
            address = " ".join(fullAddress.split(" ")[2:]).strip()
        
        _phone = ""
        alkalmasKarakterek = "0123456789;"
        if soup.select_one("#plebaniaTelefon") != None:
            for karakter in soup.select_one("#plebaniaTelefon").text.strip().replace(",", ";"):
                if karakter in alkalmasKarakterek:
                    _phone += karakter
        
            phones = [f"0036{phone.strip()}" for phone in _phone.split(";") if phone.strip() != ""]
        for pap in soup.select("a.ellatoSzemelyek"):
            if "plébános" in pap.text.lower() or "plébániai kormányzó" in pap.text.lower():
                parishioner = get_priest(pap["href"], pap.text.strip())
                break
        
        for emailweb in soup.select("#plebaniaEmail"):
            email_regex = r'[a-zA-Z0-9._%+-]+@[A-Za-z0-9.-]+\.[a-zA-Z]{2,}'
            email_matches = re.findall(email_regex, emailweb.text)
            if email_matches:
                for email in email_matches:
                    emails.append(email.strip())
            else:
                for web in emailweb.text.replace(";", ",").replace(" ", "").split(","):
                    websites.append(web.strip())


        return {
            "name": soup.select_one("#plebaniaNeve").text, # A plébánia neve
            "parishioner": parishioner, # A plébános
            "src": link,
            "phones": phones,
            "websites": websites, # Honlap
            "postalCode": postalCode, # Irányítószám
            "settlement": settlement, # Település
            "address": address, # Cím
            "emails": emails
        }



def SZHEM(filename=None, year=None):
    # Replace this with the URL of the website you want to scrape
    url = 'https://martinus.hu/hu/nev-es-cimtar/plebaniak-filiak'
    response = requests.get(url, verify=False)
    # Check if the request was successful
    if response.status_code == 200:
        html_content = response.content
    else:
        print(f"{url} - Failed to fetch the website.")

    # Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(html_content, 'html5lib')

    plebaniak = [plebania["href"] for plebania in soup.select("#plebaniakHasabok a")]

    plebanialista = process_map(processParish, plebaniak)
    plebanialista = [p for p in plebanialista if p != None]

    if filename == None: return plebanialista
    else:
        with open(filename, "w") as outfile:
            outfile.write(json.dumps(plebanialista, default=str))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                        description='Szombathelyi egyházmegye plébániáinak adatai')
    parser.add_argument('--filename', required=False, action="store", default=None, help="JSON to save. If not set, the result will be displayed on screen")

    args = parser.parse_args()

    if args.filename==None: print(SZHEM(args.filename))
    else: SZHEM(args.filename)