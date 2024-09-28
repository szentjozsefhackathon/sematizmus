import requests
from bs4 import BeautifulSoup
import re
from tqdm import tqdm
import  json
import argparse

def NYEM(filename=None, year=None):
    # Replace this with the URL of the website you want to scrape
    url = 'https://www.nyirgorkat.hu/?q=papok&egyhazmegye=3&l=hu'
    response = requests.get(url, verify=False)
    # Check if the request was successful
    if response.status_code == 200:
        html_content = response.content
    else:
        print("Failed to fetch the website.")

    # Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
    papok = []
    for pap in soup.select('a[href*="?q=pap&"]'):
        papok.append(pap["href"])


    paplista = []
    
    for pap in tqdm(papok): # Nézze meg az összes pap linkjét
        try: # Kétszeri próbálkozásra szokott menni
            response = requests.get(f"https://www.nyirgorkat.hu/{pap}", verify=False)
            if response.status_code == 200:
                html_content = response.content
            else:
                print("Failed to fetch the website.")
        except:
            try:
                response = requests.get(f"https://www.nyirgorkat.hu/{pap}", verify=False)
                if response.status_code == 200:
                    html_content = response.content
                else:
                    print("Failed to fetch the website.")
            except:
                print("Big error")
                continue


        soup = BeautifulSoup(html_content, 'html.parser')
        if "Elhunyt:" in soup.text: continue
        
        imgSrc = ""
        try:
            imgSrc = "https://nyirgorkat.hu" + soup.select_one("img.indexpap").get("src")
        except:
            pass

        paplista.append({
            "name": soup.select_one("#parokianev").text, # A pap neve
            "img": imgSrc, # A kép linkje,
            "src": f"https://nyirgorkat.hu/{pap}"
        })
    if filename == None: return paplista
    else:
        with open(filename, "w") as outfile:
            outfile.write(json.dumps(paplista))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                        description='Nyíregyházi egyházmegye papjainak adatai')
    parser.add_argument('--filename', required=False, action="store", default=None, help="JSON to save. If not set, the result will be displayed on screen")

    args = parser.parse_args()

    if args.filename==None: print(NYEM(args.filename))
    else: NYEM(args.filename)