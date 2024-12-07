import requests
from bs4 import BeautifulSoup
import re
from tqdm import tqdm
import json
import argparse
import datetime
from tqdm.contrib.concurrent import process_map
from deleteDr import deleteDr
import urllib3
urllib3.disable_warnings(category=urllib3.exceptions.InsecureRequestWarning)

def str2date(datum):
    reszek = [d.strip() for d in datum.split("-")]
    return datetime.date(int(reszek[0]), int(reszek[1]), int(reszek[2]))

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

        soup = BeautifulSoup(html_content, 'html.parser')
    
        if not "szalézi szerzetes pap" in soup.text:
            return

        imgSrc = ""
        try:
            imgSrc = soup.select_one("#szaleziak a img").get("src")
        except:
            pass
        birth = None
        ordination = None
        for sor in soup.select_one("#szaleziak_detail").findAll("tr"): # Papi táblázat
            if "Születési dátum" in sor.text: 
                birth = str2date(sor.text.split(":")[1].strip())
            if "Szentelés" in sor.text:
                ordination = str2date(sor.text.split(":")[1].strip())

        return {
            "name": soup.select_one("#highSpan h4").text, # A pap neve
            "birth": birth,
            "ordination": ordination,
            "img": imgSrc,
            "src": link,
            "orderAbbreviation": "SDB"
        }


@deleteDr
def SDB(filename=None, year=None):
    # Replace this with the URL of the website you want to scrape
    url = 'https://www.szaleziak.hu/_static/magyar_tartomany_szaleziak.php'
    response = requests.get(url, verify=False)
    # Check if the request was successful
    if response.status_code == 200:
        html_content = response.content
    else:
        print(f"{url} - Failed to fetch the website.")

    # Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    papok = []
    for pap in soup.select("#szaleziak_wrapp"): 
        papok.append(f"https://www.szaleziak.hu/_static/{pap['href']}") # Papi oldalak linkjei

    paplista = process_map(processPriest, papok)
    paplista = [p for p in paplista if p != None]

    if filename == None: return paplista
    else:
        with open(filename, "w") as outfile:
            outfile.write(json.dumps(paplista, default=str))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                        description='Szent Istvánról elnevezett Magyar Szalézi Tartomány papjainak adatai')
    parser.add_argument('--filename', required=False, action="store", default=None, help="JSON to save. If not set, the result will be displayed on screen")

    args = parser.parse_args()

    if args.filename==None: print(SDB(args.filename))
    else: SDB(args.filename)