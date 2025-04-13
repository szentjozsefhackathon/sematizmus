import requests
from bs4 import BeautifulSoup
import re
from tqdm import tqdm
import  json
import argparse
import datetime
from multiprocessing import Pool
from orderAbbreviation import orderAbbreviation
from deleteDr import deleteDr
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
    return datetime.date(int(reszek[0]), honapok[reszek[1]], int(reszek[2]))

def processPriest(link, deacon):
        try:
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
        imgSrc = soup.select_one(".article img").get("src")
        bishop = ("egri érsek" in soup.select_one(".data-container").text.lower() and not "egri érseki" in soup.select_one(".data-container").text.lower()) or "segédpüspök" in soup.select_one(".data-container").text.lower()
        birth = None
        ordination = None
        for p in soup.select(".data-container p"):
            if "életút" in p.text.lower() and not deacon:
                continue
            elif deacon and "életút" in p.text.lower() and "diakónussá szentelték" in p.text.lower():
                ordination = str2date(".".join(p.text.split(".")[:3]).replace("-",".").split(",")[1])
            if "született" in p.text.lower():
                birth = str2date(p.text.split(",")[-1].strip())

            if "pappá szentelték" in p.text.lower():
                ordination = str2date(p.text.split(":")[1].split("-én")[0].split("-án")[0].split(",")[-1].strip())

        for div in soup.select(".data-container div"):
            if "életút" in div.text.lower() and not deacon:
                continue
            elif deacon and "életút" in div.text.lower() and "diakónussá szentelték" in div.text.lower():
                ordination = str2date(".".join(div.text.replace("-",".").split(".")[:3]).split(",")[1])
            if "született" in div.text.lower():
                birth = str2date(div.text.split(",")[-1].strip())
            if "pappá szentelték" in div.text.lower():
                ordination = str2date(div.text.split(":")[1].split("-én")[0].split("-án")[0].split(",")[-1].strip())
        
        return {
            "name": soup.select_one(".article h2").text,
            "birth": birth,
            "ordination": ordination,
            "img": imgSrc,
            "src": link,
            "bishop": bishop,
            "deacon": deacon,
            "retired": "nyugállományban" in soup.select_one(".article").text.lower() or "nyugalmazott" in soup.select_one(".article").text.lower()
        }

def papkereso(link, deacon=False):
        response = requests.get(link, verify=False)
        if response.status_code == 200:
            html_content = response.content
        else:
            print(f"{link} - Failed to fetch the website.")
        soup = BeautifulSoup(html_content, 'html.parser')
        _papok = []
        for _pap in soup.select(".container > .row .article"):
            pap = _pap.select_one(".row")

            if not pap:
                continue

            _papok.append({"url": pap.select_one("h2 a")["href"], "deacon": deacon})
        return _papok

@deleteDr
@orderAbbreviation
def EFEM(filename=None, year=None):
    papok = []

    
    with Pool() as p:
        papok = p.starmap(papkereso, [(f"https://eger.egyhazmegye.hu/hitelet/papsag?page={i}", False) for i in range(1,13,1)])
    
    papok = sum(papok, [])
    
    papok+=papkereso("https://eger.egyhazmegye.hu/hitelet/papsag/allando-diakonusok", deacon=True)

    papok = [(pap["url"], pap["deacon"]) for pap in papok]


    with Pool() as p:
        paplista = p.starmap(processPriest, papok)

    paplista = [x for x in paplista if x is not None]
        

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