import requests
from bs4 import BeautifulSoup
import  json
import argparse
from tqdm.contrib.concurrent import process_map
import urllib3
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
        phones = ""
        websites = []
        postalCode = ""
        settlement = ""
        address = ""

        raw = soup.select_one("main").text.strip().splitlines()
        raw = [r.strip() for r in raw if r.strip() != ""]
        for i in range(1,len(raw)):
            if raw[i].startswith("Parókia címe:"):
                fullAddress = raw[i+1].strip()
                if fullAddress:
                    postalCode = fullAddress.split(" ")[0].strip()
                    settlement = fullAddress.split(" ")[1].split(',')[0].strip().title()
                    address = " ".join(fullAddress.split(" ")[2:]).strip()
            if raw[i].startswith("Telefonszám:"):
                phones = [f'0036{raw[i+1].strip().replace(" ","").replace("+36", "").replace("-", "").replace("/", "")}']
            if raw[i].startswith("Honlap:"):
                websites = [raw[i+1].strip()]

        return {
            "name": raw[0], # A plébánia neve
            "parishioner": {}, # A plébános
            "src": link,
            "phones": phones,
            "websites": websites, # Honlap
            "postalCode": postalCode, # Irányítószám
            "settlement": settlement, # Település
            "address": address, # Cím
            "emails": []
        }

def MEM(filename=None, year=None):
    # Replace this with the URL of the website you want to scrape
    url="https://migorkat.hu/parokiak/"
    parokiak = []
    response = requests.get(url, verify=False)
    if response.status_code == 200:
        html_content = response.content
    else:
        print(f"{url['url']} - Failed to fetch the website.")

    # Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(html_content, 'html5lib')
    for parokia in soup.select("main h2 a"):
        parokiak.append(parokia.get('href'))

    parokialista = process_map(processParish, parokiak)
    
    parokialista = [p for p in parokialista if p != None]
    parokialista = list({v['src']:v for v in parokialista}.values())

    if filename == None: return parokialista
    else:
        with open(filename, "w") as outfile:
            outfile.write(json.dumps(parokialista, default=str))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                        description='Miskolci egyházmegye parókiáinak adatai')
    parser.add_argument('--filename', required=False, action="store", default=None, help="JSON to save. If not set, the result will be displayed on screen")

    args = parser.parse_args()

    if args.filename==None: print(MEM(args.filename))
    else: MEM(args.filename)