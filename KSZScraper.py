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
        imgSrc = ""
        try:
            imgSrc = soup.select_one(".entry-content .wp-block-image img").get("src")
        except:
            pass
        return {
            "name": soup.select_one("h1.entry-title").text, 
            "seminarist": True, # Papnövendék,
            "img": imgSrc,
            "src": link
        }


@deleteDr
@orderAbbreviation
def KSZ(filename=None, year=None):
    # Replace this with the URL of the website you want to scrape
    url = 'https://kozpontiszeminarium.org/rolunk/lakoink/'
    response = requests.get(url, verify=False)
    # Check if the request was successful
    if response.status_code == 200:
        html_content = response.content
    else:
        print(f"{url} - Failed to fetch the website.")

    # Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    papok = []
    for sor in soup.select("div.entry-content ul:nth-of-type(2) li a"): # Táblázat sorainak keresése
        papok.append(sor['href']) # Papi oldalak linkjei

    paplista = process_map(processPriest, papok)
    paplista = [p for p in paplista if p != None]

    if filename == None: return paplista
    else:
        with open(filename, "w") as outfile:
            outfile.write(json.dumps(paplista, default=str))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                        description='Központi Szeminárium papnövendékeinek adatai')
    parser.add_argument('--filename', required=False, action="store", default=None, help="JSON to save. If not set, the result will be displayed on screen")

    args = parser.parse_args()

    if args.filename==None: print(KSZ(args.filename))
    else: KSZ(args.filename)