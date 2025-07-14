import requests
from bs4 import BeautifulSoup
import  json
import argparse
from tqdm.contrib.concurrent import process_map
import urllib3
import re
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


        soup = BeautifulSoup(html_content, 'html.parser')
        phones = []
        websites = []
        postalCode = ""
        settlement = ""
        address = ""
        emails = set()
        parishioner = {}

        with open("RO_NEM_nyers.json", "w") as f:
            f.write(json.dumps(soup.select_one("main").get_text(strip=True, separator="\n").splitlines(), indent=4))

        raw = soup.select_one("main").text.strip().splitlines()
        raw = [r.strip() for r in raw if r.strip() != ""]
        for i in range(len(raw)):
            if "plébános" in raw[i].lower() and len(raw) > i+1:
                parishionerName = raw[i+1].strip()
                parishionerLink = None
                for a in soup.select("a"):
                    if parishionerName in a.text:
                        parishionerLink = a.get('href')
                        break
                parishioner = get_priest(parishionerLink, parishionerName, True)

            if "postacím" in raw[i].lower():
                fullAddress = ":".join(raw[i].split(":")[1:]).strip()
                if fullAddress:
                    fullAddress = fullAddress.replace("\u2013", "").replace("-", "")
                    while fullAddress.count("  ") > 0:
                        fullAddress = fullAddress.replace("  ", " ")
                    try:
                        postalCode = fullAddress.split(" ")[0].strip()
                        settlement = fullAddress.split(" ")[1]
                        address = " ".join(fullAddress.split(" ")[2:]).strip()
                    except:
                        print(f"{link} - {fullAddress} - feldolgozási hiba")
                        postalCode = ""
                        settlement = ""
                        address = ""
            
            if raw[i].lower().startswith("telefon:"):
                _phones = raw[i].split(":")[1].strip().replace(" ","").replace("+40", "").replace("-", "").replace("/", "").replace(";", ",").split(",")
                for p in _phones:
                    if p.strip() != "":
                        phones.append("0040" + p.strip())
            if raw[i].lower().startswith("weboldal:"):
                websites.append(":".join(raw[i].split(":")[1:]).strip())


            email_regex = r'[a-zA-Z0-9._%+-]+@[A-Za-z0-9.-]+\.[a-zA-Z]{2,}'
            email_matches = re.findall(email_regex, raw[i])
            if email_matches:
                for email in email_matches:
                    emails.add(email.strip())
            

        return {
            "name": soup.select_one("h2").get_text(), # A plébánia neve
            "parishioner": parishioner, # A plébános
            "src": link,
            "phones": phones,
            "websites": websites, # Honlap
            "postalCode": postalCode, # Irányítószám
            "settlement": settlement, # Település
            "address": address, # Cím
            "emails": list(emails)
        }

def RO_NEM(filename=None, year=None):
    # Replace this with the URL of the website you want to scrape
    url="https://varad.org/egyhazmegye/plebaniak/"
    plebaniak = []
    response = requests.get(url, verify=False)
    if response.status_code == 200:
        html_content = response.content
    else:
        print(f"{url['url']} - Failed to fetch the website.")

    # Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(html_content, 'html5lib')
    for plebania in soup.select(".jet-listing-dynamic-link a"):
        plebaniak.append(plebania.get('href'))

    plebanialista = process_map(processParish, plebaniak)
    
    plebanialista = [p for p in plebanialista if p != None]
    plebanialista = list({v['src']:v for v in plebanialista}.values())

    if filename == None: return plebanialista
    else:
        with open(filename, "w") as outfile:
            outfile.write(json.dumps(plebanialista, default=str))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                        description='Nagyváradi egyházmegye plébániáinak adatai')
    parser.add_argument('--filename', required=False, action="store", default=None, help="JSON to save. If not set, the result will be displayed on screen")

    args = parser.parse_args()

    if args.filename==None: print(RO_NEM(args.filename))
    else: RO_NEM(args.filename)