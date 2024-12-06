import requests
from bs4 import BeautifulSoup
import re
from tqdm import tqdm
import  json
import argparse
import datetime
from multiprocessing import Pool
from deleteDr import deleteDr

def processPriest(link, deacon, retired):
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
            imgSrc = "https://www.migorkat.hu" + soup.select_one("article.person img").get("src")
        except:
            pass

        birth = None
        ordination = None
        
        for field in soup.select(".field"):
            if "Születési helye" in field.text:
                reszek = [int(d.split(".")[0].strip()) for d in field.select_one(".datetime").text.split(" ")]
                birth = datetime.date(reszek[0], reszek[1], reszek[2])
            if "Pappá szentelés" in field.text:
                reszek = [int(d.split(".")[0].strip()) for d in field.select_one(".datetime").text.split(" ")]
                ordination = datetime.date(reszek[0], reszek[1], reszek[2])

        return {
            "name": soup.select_one("h1.page-title").text, # A pap neve
            "img": imgSrc, # A kép linkje,
            "src": link,
            "birth": birth,
            "ordination": ordination,
            "deacon": deacon,
            "retired": retired,
            "bishop": "Orosz Atanáz dr." in soup.select_one("h1.page-title").text
        }

@deleteDr
def MEM(filename=None, year=None):
    # Replace this with the URL of the website you want to scrape

    urls = [
        {
            "url": 'https://www.migorkat.hu/szolgalattevok?diocese=miskolc&pde=priest&status=active',
            "deacon": False,
            "retired": False
        },
        {
            "url": 'https://www.migorkat.hu/szolgalattevok?diocese=miskolc&pde=priest&status=pensioner',
            "deacon": False,
            "retired": True
        },
        {
            "url": 'https://www.migorkat.hu/szolgalattevok?diocese=miskolc&pde=deacon&status=pensioner',
            "deacon": True,
            "retired": True
        },
        {
            "url": 'https://www.migorkat.hu/szolgalattevok?diocese=miskolc&pde=priest&status=pensioner',
            "deacon": False,
            "retired": True
        }
    ]
    papok = []
    for url in urls:
        response = requests.get(url["url"], verify=False)
        # Check if the request was successful
        if response.status_code == 200:
            html_content = response.content
        else:
            print(f"{url['url']} - Failed to fetch the website.")

        # Parse the HTML content with BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        for pap in soup.findAll("article"):
            papok.append((f"https://www.migorkat.hu{pap.get('about')}", url["deacon"], url["retired"]))

    with Pool() as p:
        paplista = p.starmap(processPriest, papok)
    
    paplista = [p for p in paplista if p != None]

    if filename == None: return paplista
    else:
        with open(filename, "w") as outfile:
            outfile.write(json.dumps(paplista, default=str))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                        description='Miskolci egyházmegye papjainak adatai')
    parser.add_argument('--filename', required=False, action="store", default=None, help="JSON to save. If not set, the result will be displayed on screen")

    args = parser.parse_args()

    if args.filename==None: print(MEM(args.filename))
    else: MEM(args.filename)