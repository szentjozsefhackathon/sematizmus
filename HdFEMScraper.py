import requests
from bs4 import BeautifulSoup
import re
from tqdm import tqdm
import  json
import argparse
import datetime
from tqdm.contrib.concurrent import process_map
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
    nonBreakSpace = u'\xa0'
    reszek = [d.split(".")[0].strip() for d in datum.split("\n")[0].strip().split(nonBreakSpace)]
    return datetime.date(int(reszek[0]), honapok[reszek[1]], int(reszek[2]))

def processPriest(link):
        try: # Kétszeri próbálkozásra szokott menni
            response = requests.get(link, verify=False)
            if response.status_code == 200:
                html_content = response.content
            else:
                print("Failed to fetch the website.")
        except:
            try:
                response = requests.get(link, verify=False)
                if response.status_code == 200:
                    html_content = response.content
                else:
                    print("Failed to fetch the website.")
            except:
                print("Big error")
                return


        soup = BeautifulSoup(html_content, 'html.parser')
        imgSrc = ""
        try:
            imgSrc = "https://hd.gorogkatolikus.hu/" + soup.select_one(".kep-terkep img").get("src")
        except:
            pass
        name = soup.select_one(".aloldal_cim").text
        birth = None
        ordination = None
        for sor in soup.select(".adattar_sor"):
            if "Születés" in sor.text:
                try:
                    birth = str2date(sor.text.split(", ")[-1])
                except: pass
            if "Pappá szentelés" in sor.text:
                try:
                    ordination = str2date(sor.text.split(", ")[-1])
                except: pass
            if "Diakónussá szentelés" in sor.text and not "Pappá szentelés" in sor.text:
                try:
                    ordination = str2date(sor.text.split(", ")[-1])
                except: pass

        return {
            "name": name, # A pap neve
            "img": imgSrc, # A kép linkje,
            "src": link,
            "birth": birth,
            "deacon": not "Pappá szentelés" in soup.text,
            "ordination": ordination,
            "bishop": name == "dr. Keresztes Szilárd" or name == "Kocsis Fülöp",
            "retired": "Nyugállományban" in soup.text
        }


def HdFEM(filename=None, year=None):
    # Replace this with the URL of the website you want to scrape
    url = 'https://hd.gorogkatolikus.hu/adattar-papjaink'
    response = requests.get(url, verify=False)
    # Check if the request was successful
    if response.status_code == 200:
        html_content = response.content
    else:
        print("Failed to fetch the website.")

    # Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
    papok = []
    for pap in soup.select(".adattar_cont"):
        papok.append("https://hd.gorogkatolikus.hu/"+pap['onclick'][15:-1])

    for pap in soup.select(".adattar_cont_left"):
        papok.append("https://hd.gorogkatolikus.hu/"+pap['onclick'][15:-1])



    
    paplista = process_map(processPriest, papok)

    paplista = [pap for pap in paplista if pap != None]

    if filename == None: return paplista
    else:
        with open(filename, "w") as outfile:
            outfile.write(json.dumps(paplista, default=str))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                        description='Hajdúdorogi főegyházmegye papjainak adatai')
    parser.add_argument('--filename', required=False, action="store", default=None, help="JSON to save. If not set, the result will be displayed on screen")

    args = parser.parse_args()

    if args.filename==None: print(HdFEM(args.filename))
    else: HdFEM(args.filename)