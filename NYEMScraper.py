import requests
from bs4 import BeautifulSoup
import re
from tqdm import tqdm
import  json
import argparse
import datetime
import re
from tqdm.contrib.concurrent import process_map
import urllib3
from deleteDr import deleteDr

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
        if "Elhunyt:" in soup.text: return
        if not "Pappá szentelés" in soup.text and not "Diakónussá szentelés" in soup.text: return
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
                print(link + " - " + soup.select_one("#parokianev").text)
            
        retired = True
        for s in soup.select(".szolgalat td td"):
            if re.search("-<td>", str(s)): retired = False

        if retired == False and "nyugállományban" in soup.select_one("#pap table.table").text.lower(): retired = True

        return {
            "name": soup.select_one("#parokianev").text, # A pap neve
            "img": imgSrc, # A kép linkje,
            "src": link,
            "birth": birth,
            "ordination": ordination,
            "deacon": not "Pappá szentelés" in soup.text,
            "bishop": "Szocska A. Ábel" in soup.select_one("#parokianev").text,
            "retired": retired
        }

@deleteDr
def NYEM(filename=None, year=None):
    # Replace this with the URL of the website you want to scrape
    url = 'https://www.nyirgorkat.hu/?q=papok&egyhazmegye=3&l=hu'
    response = requests.get(url, verify=False)
    # Check if the request was successful
    if response.status_code == 200:
        html_content = response.content
    else:
        print(f"{url} - Failed to fetch the website.")

    # Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
    papok = []
    for pap in soup.select('a[href*="?q=pap&"]'):
        papok.append("https://www.nyirgorkat.hu/"+pap["href"])
    
    paplista = process_map(processPriest, papok)

    paplista = [pap for pap in paplista if pap != None]
    paplista = list({v['src']:v for v in paplista}.values())
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