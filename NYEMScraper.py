import requests
from bs4 import BeautifulSoup
import re
from tqdm import tqdm
import  json
import argparse
import datetime
import re
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
    reszek = [d.split(".")[0].strip() for d in datum.strip().split(" ")]
    return datetime.date(int(reszek[0]), honapok[reszek[1]], int(reszek[2]))

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
        if not "Pappá szentelés" in soup.text and not "Diakónussá szentelés" in soup.text: continue
        imgSrc = ""
        try:
            imgSrc = "https://nyirgorkat.hu" + soup.select_one("img.indexpap").get("src")
        except:
            pass
        birth = None
        ordination = None

        for r in soup.select("tr"):
            try:
                if "Születés helye" in r.text:
                    birth = str2date(r.text.split(",")[-1])
                if "Pappá szentelés" in r.text:
                    ordination = str2date(r.text.split(",")[-1])
                if "Diakónussá szentelés" in r.text and not "Pappá szentelés" in soup.text:
                    ordination = str2date(r.text.split(",")[-1])
            except:
                print(soup.select_one("#parokianev").text)
            
        retired = True
        for s in soup.select(".szolgalat td td"):
            if re.search("-<td>", str(s)): retired = False

        if retired == False and "nyugállományban" in soup.text.lower(): retired = True

        paplista.append({
            "name": soup.select_one("#parokianev").text, # A pap neve
            "img": imgSrc, # A kép linkje,
            "src": f"https://nyirgorkat.hu/{pap}",
            "birth": birth,
            "ordination": ordination,
            "deacon": not "Pappá szentelés" in soup.text,
            "bishop": "Szocska A. Ábel" in soup.select_one("#parokianev").text,
            "retired": retired
        })
    if filename == None: return paplista
    else:
        with open(filename, "w") as outfile:
            outfile.write(json.dumps(paplista, default=str))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                        description='Nyíregyházi egyházmegye papjainak adatai')
    parser.add_argument('--filename', required=False, action="store", default=None, help="JSON to save. If not set, the result will be displayed on screen")

    args = parser.parse_args()

    if args.filename==None: print(NYEM(args.filename))
    else: NYEM(args.filename)