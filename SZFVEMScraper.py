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
    "december": 12,
    "01": 1,
    "02": 2,
    "03": 3,
    "04": 4,
    "05": 5,
    "06": 6,
    "07": 7,
    "08": 8,
    "09": 9,
    "10": 10,
    "11": 11,
    "12": 12
}

def str2date(datum):
    datum = datum.replace(".", ". ").replace("  ", " ")
    reszek = [d.split(".")[0].strip() for d in datum.strip().split(" ")]
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

        adatlapText = soup.select_one(".adatlap").text

        nev = soup.select_one("h1").text
        szul = None
        szent = None
        tartalomText = soup.select_one(".tartalom").text.split("\n")
        for sor in tartalomText:
            if nev == "Szemere János":
                szul = 1977 #https://metropolita.hu/2017/05/interju-egy-papnovendekkel/
            if "Született" in sor:
                try:
                    szul = str2date(sor.replace(u'\xa0', u' ').split(", ")[1])
                except:
                    try:
                        szul = str2date(sor.replace(u'\xa0', u' ').split(" ")[-1])
                    except:
                        try:
                            szul = str2date(sor.replace(u'\xa0', u' ').split("Született: ")[-1].split("\n")[0])
                        except: 
                            if nev == "Ugrits Tamás":
                                szul = datetime.date(1961,2,7)
            if "Szentelés" in sor:
                try:
                    szent = str2date(sor.split(", ")[1])
                except:
                    szent = str2date(sor.split("Szentelés: ")[1].split(", ")[1])

        imgSrc = ""
        try:
            imgSrc = "https://www.szfvar.katolikus.hu" + soup.select_one(".adatkepb img").get("src")
        except:
            pass
        return {
            "name": nev,
            "birth": szul,
            "img": imgSrc,
            "src": link,
            "bishop": "megyés püspök" in adatlapText,
            "retired": "nyugállományban" in adatlapText,
            "ordination": szent
        }

def SZFVEM(filename=None, year=None):
    url = "https://www.szfvar.katolikus.hu/"
    papok = []
    def papkereso(link):
        response = requests.get(link, verify=False)
        if response.status_code == 200:
            html_content = response.content
        else:
            print("Failed to fetch the website.")
        soup = BeautifulSoup(html_content, 'html.parser')
        _papok = []
        for pap in soup.select_one(".adattar").select(".listadoboz"):
            _papok.append(url+pap.select_one("h3 a")["href"])
        
        return _papok
    
    papok += papkereso("https://www.szfvar.katolikus.hu/adattar/papok/?min=0")
    papok += papkereso("https://www.szfvar.katolikus.hu/adattar/papok/?min=50")


    paplista = process_map(processPriest, papok)

    if filename == None: return paplista
    else:
        with open(filename, "w") as outfile:
            outfile.write(json.dumps(paplista, default=str))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                        description='Székesfehérvári egyházmegye papjainak adatai')
    parser.add_argument('--filename', required=False, action="store", default=None, help="JSON to save. If not set, the result will be displayed on screen")

    args = parser.parse_args()

    if args.filename==None: print(SZFVEM(args.filename))
    else: SZFVEM(args.filename)