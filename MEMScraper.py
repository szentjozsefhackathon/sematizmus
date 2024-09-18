import requests
from bs4 import BeautifulSoup
import re
from tqdm import tqdm
import  json
import argparse

def MEM(filename=None, year=None):
    # Replace this with the URL of the website you want to scrape
    url = 'https://www.migorkat.hu/szolgalattevok?diocese=miskolc&pde=priest&status=active'
    response = requests.get(url)
    # Check if the request was successful
    if response.status_code == 200:
        html_content = response.content
    else:
        print("Failed to fetch the website.")

    # Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
    papok = []
    for pap in soup.findAll("article"):
        papok.append(pap.get("about"))


    paplista = []
    for pap in tqdm(papok): # Nézze meg az összes pap linkjét
        try: # Kétszeri próbálkozásra szokott menni
            response = requests.get(f"https://www.migorkat.hu{pap}")
            if response.status_code == 200:
                html_content = response.content
            else:
                print("Failed to fetch the website.")
        except:
            try:
                response = requests.get(f"https://www.migorkat.hu{pap}")
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
            imgSrc = "https://www.migorkat.hu" + soup.select_one("article.person img").get("src")
        except:
            pass


        paplista.append({
            "name": soup.select_one("h1.page-title").text, # A pap neve
            "img": imgSrc, # A kép linkje,
            "src": f"https://www.migorkat.hu{pap}"
        })
    if filename == None: return paplista
    else:
        with open(filename, "w") as outfile:
            outfile.write(json.dumps(paplista))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                        description='Miskolci egyházmegye papjainak adatai')
    parser.add_argument('--filename', required=False, action="store", default=None, help="JSON to save. If not set, the result will be displayed on screen")

    args = parser.parse_args()

    if args.filename==None: print(MEM(args.filename))
    else: MEM(args.filename)