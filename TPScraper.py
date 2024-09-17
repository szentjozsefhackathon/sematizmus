


import requests
from bs4 import BeautifulSoup
import re
from tqdm import tqdm
import  json
import argparse

def TP(filename=None, year=None):
    # Replace this with the URL of the website you want to scrape
    url = 'https://ktp.hu/js/ajax/listazo.php?url=lelkeszek%2Ftabori-lelkeszi-kar&fm=110&am=173'
    response = requests.get(url)
    # Check if the request was successful
    if response.status_code == 200:
        html_content = response.content
    else:
        print("Failed to fetch the website.")

    # Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    papok = []
    for sor in soup.findAll("a"):
        papok.append(sor['href']) # Papi oldalak linkjei

    papok.append("/lelkeszek/takacs-tamas")
    paplista = []
    for pap in tqdm(papok): # Nézze meg az összes pap linkjét
        if pap == "/lelkeszek/tabori-lelkeszi-kar/mikus-tibor":
            paplista.append({
                "name": "Mikus Tibor",
                "img": "https://ktp.hu/uploads/content/1523/kepek/o_mikus-tibor-fhdgy..jpg",
                "src": f"https://ktp.hu{pap}"
            })
            continue
        try: # Kétszeri próbálkozásra szokott menni
            response = requests.get(f"https://ktp.hu{pap}")
            if response.status_code == 200:
                html_content = response.content
            else:
                print("Failed to fetch the website.")
        except:
            try:
                response = requests.get(f"https://ktp.hu{pap}")
                if response.status_code == 200:
                    html_content = response.content
                else:
                    print("Failed to fetch the website.")
            except:
                print("Big error")
                continue
        

        soup = BeautifulSoup(html_content, 'html.parser')
        imgSrc = ""
        try:
            imgSrc = "https://ktp.hu" + soup.select_one(".bordo img").get("src")
        except:
            pass

        paplista.append({
            "name": soup.select_one(".bordo:first-child").text, # A pap neve
            "img": imgSrc, # A kép linkje,
            "src": f"https://ktp.hu{pap}"
        })
    if filename == None: return paplista
    else:
        with open(filename, "w") as outfile:
            outfile.write(json.dumps(paplista))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                        description='Tábori püspökség papjainak adatai')
    parser.add_argument('--filename', required=False, action="store", default=None, help="JSON to save. If not set, the result will be displayed on screen")

    args = parser.parse_args()

    if args.filename==None: print(TP(args.filename))
    else: TP(args.filename)