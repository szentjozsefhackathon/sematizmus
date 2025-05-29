import requests
from bs4 import BeautifulSoup
import re
from tqdm import tqdm
import  json
import argparse
import datetime
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
    nonBreakSpace = u'\xa0'
    reszek = [d.split(".")[0].strip() for d in datum.split("\n")[0].strip().split(nonBreakSpace)]
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
        imgSrc = ""
        try:
            imgSrc = "https://hd.gorogkatolikus.hu/" + soup.select_one(".kep-terkep img").get("src")
        except:
            pass
        if imgSrc == "https://hd.gorogkatolikus.hu/adattar/pap/nincs.jpg":
            imgSrc = None
        name = soup.select_one(".aloldal_cim").text
        birth = None
        ordination = None
        dutyStation = []
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
            if "Szolgálati helyek:" in sor.text:
                szolgHelyek = sor.select_one(".f400")
                for i in range(len(szolgHelyek.select("div"))):
                    if i % 2 == 1:
                        continue
                    szolgIdo = szolgHelyek.select("div")[i]
                    print(szolgIdo.text)
                    if not (szolgIdo.has_attr("class") and len(szolgIdo["class"]) == 1 and szolgIdo["class"][0] == "tolig"):
                        continue
                    if szolgIdo.text.endswith("-") or szolgIdo.text == f"{datetime.date.today().year}":
                        dutyStation.append(szolgHelyek.select("div")[i+1].text.strip())
        dutyStation = "; ".join(dutyStation)
        if len(dutyStation) == 0: dutyStation = None
        return {
            "name": name, 
            "img": imgSrc, 
            "src": link,
            "birth": birth,
            "deacon": not "Pappá szentelés" in soup.text,
            "ordination": ordination,
            "bishop": name == "dr. Keresztes Szilárd" or name == "Kocsis Fülöp",
            "retired": "Nyugállományban" in soup.select_one("#adattar-pap").text,
            "dutyStation": dutyStation, 
        }

@deleteDr
def HdFEM(filename=None, year=None):
    url = 'https://hd.gorogkatolikus.hu/adattar-papjaink'
    response = requests.get(url, verify=False)
    if response.status_code == 200:
        html_content = response.content
    else:
        print(f"{url} - Failed to fetch the website.")

    soup = BeautifulSoup(html_content, 'html.parser')
    papok = []
    for pap in soup.select(".adattar_cont"):
        papok.append("https://hd.gorogkatolikus.hu/"+pap['onclick'][15:-1])

    for pap in soup.select(".adattar_cont_left"):
        papok.append("https://hd.gorogkatolikus.hu/"+pap['onclick'][15:-1])
    
    paplista = process_map(processPriest, papok)

    paplista = [pap for pap in paplista if pap != None]
    paplista = list({v['src']:v for v in paplista}.values())

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