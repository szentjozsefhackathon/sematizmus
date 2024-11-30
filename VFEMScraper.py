import requests
from bs4 import BeautifulSoup
import re
from tqdm import tqdm
import  json
import argparse
import datetime

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

def VFEM(filename=None, year=None):
    # Replace this with the URL of the website you want to scrape
    url = 'https://www.veszpremiersekseg.hu/papok/'
    response = requests.get(url)
    # Check if the request was successful
    if response.status_code == 200:
        html_content = response.content
    else:
        print("VFEM - Failed to fetch the website.")

    # Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
    paplista = []
    for pap in tqdm(soup.select("article")):
        birth = None
        ordination = None

        for p in pap.select("p"):
            if "Született" in p.text or "zületett" in p.text:
                try:
                    birth = str2date(p.text.split(",")[-1].strip())
                except:
                    try:
                        birth = str2date(" ".join(p.text.split(" ")[-3:]))
                    except:
                        try:
                            birth = str2date(p.text.split(": ")[1].split("-")[0])
                        except:
                            try:
                                birth = str2date(p.text.split(",")[-1].split("-")[0])
                            except Exception as e:
                                if pap.select_one(".entry-title").text=="Mail József dr.":
                                    birth = datetime.date(1949,8,15)
                                    continue
                                raise e

            if "Pappá szentelték" in p.text:
                try:
                    ordination = str2date(p.text.split(",")[-1])
                except:
                    try:
                        ordination = str2date(" ".join(p.text.split(" ")[-3:]))
                    except:
                        ordination = str2date(p.text.split(": ")[1].split("-")[0])
        imgSrc = None
        try:
            imgSrc = pap.select_one("img").get("src")
        except: pass
        paplista.append({
            "name": pap.select_one(".entry-title").text,
            "img": imgSrc,
            "src": "https://www.veszpremiersekseg.hu/papok/",
            "birth": birth,
            "ordination": ordination,
            "retired": "ny." in pap.text.lower() or "nyugalomban" in pap.text.lower(),
            "bishop": "Udvardy György dr." in pap.select_one(".entry-title").text or "Márfi Gyula" in pap.select_one(".entry-title").text
        })



    if filename == None: return paplista
    else:
        with open(filename, "w") as outfile:
            outfile.write(json.dumps(paplista, default=str))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                        description='Veszprémi főegyházmegye papjainak adatai')
    parser.add_argument('--filename', required=False, action="store", default=None, help="JSON to save. If not set, the result will be displayed on screen")

    args = parser.parse_args()

    if args.filename==None: print(VFEM(args.filename))
    else: VFEM(args.filename)