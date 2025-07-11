import requests
from bs4 import BeautifulSoup
import re
from tqdm import tqdm
import  json
import argparse
import datetime
from tqdm.contrib.concurrent import process_map
import urllib3
from getPriest import get_priest
urllib3.disable_warnings(category=urllib3.exceptions.InsecureRequestWarning)

def processParish(link):
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

        name = soup.select_one(".aloldal_cim").text
        parishioner = {}
        phones = []
        websites = []
        postalCode = ""
        settlement = ""
        address = ""
        emails = []
        for sor in soup.select(".adattar_sor"):
            if "A parókia címe" in sor.text:
                postalCode = sor.text.split(":")[1].strip().split(" ")[0].strip()
                settlement = sor.text.split(":")[1].strip().split(" ")[1].split(',')[0].strip().title()
                address = " ".join(sor.text.split(":")[1].strip().split(" ")[2:]).strip()
            if "Telefonszám" in sor.text:
                phones = [f'0036{sor.text.split(":")[1].strip().replace(" ", "").replace("(","").replace(")","").replace("-", "")}']
            if "Saját oldalak" in sor.text:
                for _link in sor.select("a"):
                    if _link.has_attr("href"):
                        websites.append(_link["href"])
            if "Szolgálattevő személy(ek):" in sor.text:
                szolgTevok = sor.select_one(".f400")
                for i in range(len(szolgTevok.select("div"))):
                    if i % 2 == 1:
                        continue
                    szolgIdo = szolgTevok.select("div")[i]
                    if not (szolgIdo.has_attr("class") and len(szolgIdo["class"]) == 1 and szolgIdo["class"][0] == "tolig"):
                        continue
                    if szolgIdo.text.endswith("-") or szolgIdo.text == f"{datetime.date.today().year}":
                        szolgalattevo = szolgTevok.select("div")[i+1]
                        if "parókus" in szolgalattevo.text.lower() or "szervezőlelkész" in szolgalattevo.text.lower():
                            try:
                                parishionerName = " ".join([nevresz for nevresz in szolgalattevo.text.strip().split(" ") if nevresz[0].isupper()])
                                parishionerName = " ".join([nevresz for nevresz in szolgalattevo.text.strip().split("\u00a0") if nevresz[0].isupper()])

                                parishioner = get_priest("https://hd.gorogkatolikus.hu/" + szolgalattevo.select_one("a")["href"], parishionerName)
                            except:
                                print(f"{link} - {name} - Plébános feldolgozási hiba")
        
        return {
            "name": name, # A plébánia neve
            "parishioner": parishioner, # A plébános
            "src": link,
            "phones": phones,
            "websites": websites, # Honlap
            "postalCode": postalCode, # Irányítószám
            "settlement": settlement, # Település
            "address": address, # Cím
            "emails": emails
        }


def HdFEM(filename=None, year=None):
    url = 'https://hd.gorogkatolikus.hu/adattar-parokiak'
    response = requests.get(url, verify=False)
    if response.status_code == 200:
        html_content = response.content
    else:
        print(f"{url} - Failed to fetch the website.")

    soup = BeautifulSoup(html_content, 'html.parser')
    parokiak = []
    for parokia in soup.select(".adattar_cont"):
        parokiak.append("https://hd.gorogkatolikus.hu/"+parokia['onclick'][15:-1])

    for parokia in soup.select(".adattar_cont_left"):
        parokiak.append("https://hd.gorogkatolikus.hu/"+parokia['onclick'][15:-1])
    
    parokialista = process_map(processParish, parokiak)

    parokialista = [parokia for parokia in parokialista if parokia != None]
    parokialista = list({v['src']:v for v in parokialista}.values())

    if filename == None: return parokialista
    else:
        with open(filename, "w") as outfile:
            outfile.write(json.dumps(parokialista, default=str))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                        description='Hajdúdorogi főegyházmegye parókiáinak adatai')
    parser.add_argument('--filename', required=False, action="store", default=None, help="JSON to save. If not set, the result will be displayed on screen")

    args = parser.parse_args()

    if args.filename==None: print(HdFEM(args.filename))
    else: HdFEM(args.filename)