import requests
from bs4 import BeautifulSoup
import re
from tqdm import tqdm
import json
import argparse
import datetime
from tqdm.contrib.concurrent import process_map
from orderAbbreviation import orderAbbreviation
from deleteDr import deleteDr
import urllib3
urllib3.disable_warnings(category=urllib3.exceptions.InsecureRequestWarning)
honapok = {
        "január": 1,
        "február": 2,
        "március": 3,
        "április": 4,
        "május": 5,
        "június": 6,
        "július": 7,
        "augusztus": 8,
        "szeptember": 9,
        "október": 10,
        "november": 11,
        "december": 12
}
def str2date(datum):
    reszek = [d.split(".")[0].strip() for d in datum.split(" ")]
    return datetime.date(int(reszek[0]), honapok[reszek[1]], int(reszek[2]))

def processPriest(link):
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
        imgSrc = ""
        try:
            imgSrc = "https://pecsiegyhazmegye.hu" + soup.select_one(".item-page img").get("src")
        except:
            pass

        if imgSrc == "https://pecsiegyhazmegye.hu/images/szemelyek/80417_lm.png":
            imgSrc = None
        birth = None
        ordination = None
        dutyStation = set()
        for sor in soup.select_one(".kpriest-content-right table").findAll("tr"): # Papi táblázat
            if(sor.select_one("th").text == "Született"): 
                birth = str2date(sor.select_one("td").text.strip().split(", ")[1])
            
            if(sor.select_one("th").text == "Szentelés"):
                try:
                    ordination = str2date(sor.select_one("td").text.strip().split(", ")[1])
                except:
                    ordination = str2date(sor.select_one("td").text.strip())
            if(sor.select_one("th").text == "Szolgálati hely"):
                for ds in sor.select_one("td").select("p"):
                    dutyStation.add(ds.text.strip())
        
        dutyStation = "; ".join(list(dutyStation))
        if len(dutyStation) == 0:
            dutyStation = None
        return {
            "name": soup.select_one(".page-header h2").text, # A pap neve
            "birth": birth,
            "ordination": ordination,
            "img": imgSrc, # A kép linkje,
            "src": link,
            "retired": "nyugállományban" in soup.select_one("#content").text or "ny. megyéspüspök" in soup.select_one("#content").text,
            "bishop": "megyéspüspök" in soup.select_one("#content").text,
            "deacon": "diakónus" in soup.select_one("#content").text,
            "dutyStation": dutyStation
        }


@deleteDr
@orderAbbreviation
def PEM(filename=None, year=None):
    # Replace this with the URL of the website you want to scrape
    url = 'https://pecsiegyhazmegye.hu/egyhazmegye/papsag/papjaink'
    response = requests.get(url, verify=False)
    # Check if the request was successful
    if response.status_code == 200:
        html_content = response.content
    else:
        print(f"{url} - Failed to fetch the website.")

    # Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    papok = []
    firstLine = True # Az első sor csak fejléc
    for sor in soup.select_one(".item-page table").tbody.findAll("tr"): # Táblázat sorainak keresése
        if firstLine:
            firstLine = False
            continue

        papok.append(sor.findAll('td')[0].select_one('a')['href']) # Papi oldalak linkjei

    paplista = process_map(processPriest, papok)
    paplista = [p for p in paplista if p != None]

    if filename == None: return paplista
    else:
        with open(filename, "w") as outfile:
            outfile.write(json.dumps(paplista, default=str))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                        description='Pécsi egyházmegye papjainak adatai')
    parser.add_argument('--filename', required=False, action="store", default=None, help="JSON to save. If not set, the result will be displayed on screen")

    args = parser.parse_args()

    if args.filename==None: print(PEM(args.filename))
    else: PEM(args.filename)