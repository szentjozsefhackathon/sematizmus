import requests
from bs4 import BeautifulSoup
import re
from tqdm import tqdm
import json
import argparse
import datetime
from orderAbbreviation import orderAbbreviation
honapok = {
    "jan": 1,
    "febr": 2,
    "feb": 2,
    "márc": 3,
    "már": 3,
    "ápr": 4,
    "máj": 5,
    "jún": 6,
    "június": 6,
    "júl": 7,
    "aug": 8,
    "szept": 9,
    "okt": 10,
    "nov": 11,
    "dec": 12
}

def str2date(datum):
    if datum == "1950. augusztus 7.":
        return datetime.date(1950, 8, 7)
    if datum == "1953. július 31.":
        return datetime.date(1953, 7, 31)
    if datum == "1944. október 20.":
        return datetime.date(1944, 10, 20)
    reszek = [d.strip() for d in datum.split(".")]
    return datetime.date(int(reszek[0]), honapok[reszek[1]], int(reszek[2]))

@orderAbbreviation
def KEM(filename=None, year=None):
    sources = [
        {
            "url": "https://kaposvar.egyhazmegye.hu/index.php/papok/aktiv-papok",
            "options": {
                "retired": False,
                "bishop": False,
                "deacon": False
            }
        },
        {
            "url": "https://kaposvar.egyhazmegye.hu/index.php/papok/diakonusok",
            "options": {
                "retired": False,
                "bishop": False,
                "deacon": True
            }
        },
        {
            "url": "https://kaposvar.egyhazmegye.hu/index.php/papok/nyugdijas-papok",
            "options": {
                "retired": True,
                "bishop": False,
                "deacon": False
            }
        },
    ]
    paplista = [{
        "name": "Varga László",
        "birth": datetime.date(1956, 8, 17),
        "ordination": datetime.date(1982, 4, 17),
        "img": "https://kaposvar.egyhazmegye.hu/images/Megyespuspok/Varga_Laszlo_megyespuspok.jpg",
        "src": "https://kaposvar.egyhazmegye.hu/index.php/papok/fopasztor",
        "bishop": True,
        "retired": False,
        "deacon": False
    }]
    for source in sources:
        response = requests.get(source["url"], verify=False)
        if response.status_code == 200:
            html_content = response.content
        else:
            print(f"{source["url"]} - Failed to fetch the website.")

        soup = BeautifulSoup(html_content, 'html.parser')

        for pap in soup.select(".qx-element-person"):
            ordination = None
            try:
                ordination = str2date(".".join(pap.select_one(".qx-person-description p").text.split("Szent.:")[1].split(".")[:3]).split(", ")[1])
            except:
                if pap.select_one("h4").text == "Csendes Sándor József ":
                    ordination = datetime.date(1998, 9, 19)
                if pap.select_one("h4").text == "Galambos Ferenc":
                    ordination = datetime.date(2003, 6, 28)
                if pap.select_one("h4").text == "Háda László Dr.":
                    ordination = datetime.date(2002, 6, 22)
                if pap.select_one("h4").text == "Kóré Mihály":
                    ordination = datetime.date(2002, 6, 29)
                if pap.select_one("h4").text == "Tölgyesi Dávid":
                    ordination = datetime.date(2019, 6, 29)
                if pap.select_one("h4").text == "Fliszár Károly":
                    ordination = datetime.date(1975, 6, 29)
                if pap.select_one("h4").text == "Kovács Jenő":
                    ordination = datetime.date(1975, 6, 23)
                if pap.select_one("h4").text == "Marics József":
                    ordination = datetime.date(1969, 6, 15)
            if ordination == None:
                print(f"{source["url"]}Szentelés hiba")
            options = {**source["options"]}
            if pap.select_one("h4").text == "Balás Béla":
                options["bishop"] = True
            imgSrc = f"https://kaposvar.egyhazmegye.hu{pap.select_one('img').get('src')}"
            paplista.append({
                "name": pap.select_one("h4").text,
                "birth": str2date(pap.select_one(".qx-person-description p").text.split("Szent.:")[0].split(", ")[1]),
                "ordination": ordination,
                "img": imgSrc,
                "src": source["url"],
                **options
            })
    

    if filename == None:
        return paplista
    else:
        with open(filename, "w") as outfile:
            outfile.write(json.dumps(paplista, default=str))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Kaposvári egyházmegye papjainak adatai')
    parser.add_argument('--filename', required=False, action="store", default=None,
                        help="JSON to save. If not set, the result will be displayed on screen")

    args = parser.parse_args()

    if args.filename == None:
        print(KEM(args.filename))
    else:
        KEM(args.filename)
