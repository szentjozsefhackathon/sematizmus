import requests
from bs4 import BeautifulSoup
import re
from tqdm import tqdm
import json
import argparse
from tqdm.contrib.concurrent import process_map
from deleteDr import deleteDr
import urllib3
urllib3.disable_warnings(category=urllib3.exceptions.InsecureRequestWarning)



def processHouse(link):
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

        if "Kolozsvári Piarista Misszió" in soup.text:
            return
        
        papok = []
        for pap in soup.select("table tbody tr td:first-child"): # Papi táblázat
            papok.append({
                "name": pap.text.strip(),
                "src": link,
                "orderAbbreviation": "SP"
            })

        return papok


@deleteDr
def SP(filename=None, year=None):
    # Replace this with the URL of the website you want to scrape
    url = 'https://piarista.hu/szerzeteskozossegek/'
    response = requests.get(url, verify=False)
    # Check if the request was successful
    if response.status_code == 200:
        html_content = response.content
    else:
        print(f"{url} - Failed to fetch the website.")

    # Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    hazak = []
    for haz in soup.select(".gdlr-core-blog-thumbnail a"): 
        hazak.append(haz["href"])

    paplista = process_map(processHouse, hazak)
    paplista = [p for p in paplista if p != None]
    paplista = sum(paplista, [])
    if filename == None: return paplista
    else:
        with open(filename, "w") as outfile:
            outfile.write(json.dumps(paplista, default=str))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                        description='Piarista Rend Magyar Tartománya papjainak adatai')
    parser.add_argument('--filename', required=False, action="store", default=None, help="JSON to save. If not set, the result will be displayed on screen")

    args = parser.parse_args()

    if args.filename==None: print(SP(args.filename))
    else: SP(args.filename)