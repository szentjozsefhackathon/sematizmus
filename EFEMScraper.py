import requests
from bs4 import BeautifulSoup
import re
from tqdm import tqdm
import  json
import argparse
import datetime

honapok = {
    "1": 1,
    "2": 2,
    "3": 3,
    "4": 4,
    "5": 5,
    "6": 6,
    "7": 7,
    "8": 8,
    "9": 9,
    "10": 10,
    "11": 11,
    "12": 12,
    "01": 1,
    "02": 2,
    "03": 3,
    "04": 4,
    "05": 5,
    "06": 6,
    "07": 7,
    "08": 8,
    "09": 9,
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
    datum = datum.replace(".", ". ").replace("  ", " ")
    reszek = datum.split("-") if "-" in datum and len(datum.split(" "))<4 else [d.split(".")[0].strip() for d in datum.strip().split(" ")]
    print(reszek)
    return datetime.date(int(reszek[0]), honapok[reszek[1]], int(reszek[2]))

def EFEM(filename=None, year=None):
    papok = []
    def papkereso(link, deacon=False):
        response = requests.get(link, verify=False)
        if response.status_code == 200:
            html_content = response.content
        else:
            print("Failed to fetch the website.")
        soup = BeautifulSoup(html_content, 'html.parser')
        _papok = []
        for _pap in soup.select(".container > .row .article"):
            pap = _pap.select_one(".row")

            if not pap:
                continue

            _papok.append({"url": pap.select_one("h2 a")["href"], "deacon": deacon})
        return _papok
    
    for i in tqdm(range(1,13,1)):
        papok += papkereso(f"https://eger.egyhazmegye.hu/hitelet/papsag?page={i}")

    paplista = []
    for pap in tqdm(papok):
        try:
            response = requests.get(pap["url"], verify=False)
            if response.status_code == 200:
                html_content = response.content
            else:
                print("Failed to fetch the website.")
        except:
            try:
                response = requests.get(pap["url"], verify=False)
                if response.status_code == 200:
                    html_content = response.content
                else:
                    print("Failed to fetch the website.")
            except:
                print("Big error")
                continue

        soup = BeautifulSoup(html_content, 'html.parser')
        print(soup.select_one(".article h2").text)
        imgSrc = soup.select_one(".article img").get("src")
        bishop = "egri érsek" in soup.text.lower() or "segédpüspök" in soup.text.lower()
        birth = None
        ordination = None
        for p in soup.select(".data-container p"):
            if "életút" in p.text.lower():
                continue
            if "született" in p.text.lower():
                birth = str2date(p.text.split(",")[-1].strip())

            if "pappá szentelték" in p.text.lower():
                ordination = str2date(p.text.split(":")[1].split("-én")[0].split("-án")[0].split(",")[-1].strip())

        for div in soup.select(".data-container div"):
            if "életút" in div.text.lower():
                continue
            if "született" in div.text.lower():
                birth = str2date(div.text.split(",")[-1].strip())
            if "pappá szentelték" in div.text.lower():
                ordination = str2date(div.text.split(":")[1].split("-én")[0].split("-án")[0].split(",")[-1].strip())
        
        paplista.append({
            "name": soup.select_one(".article h2").text,
            "birth": birth,
            "ordination": ordination,
            "img": imgSrc,
            "src": pap["url"],
            "bishop": bishop,
            "deacon": pap["deacon"],
            "retired": "nyugállományban" in soup.text.lower()
        })
        





    if filename == None: return paplista
    else:
        with open(filename, "w") as outfile:
            outfile.write(json.dumps(paplista))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                        description='Egri főegyházmegye papjainak adatai')
    parser.add_argument('--filename', required=False, action="store", default=None, help="JSON to save. If not set, the result will be displayed on screen")

    args = parser.parse_args()

    if args.filename==None: print(EFEM(args.filename))
    else: EFEM(args.filename)