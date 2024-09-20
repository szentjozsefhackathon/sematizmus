import requests
from bs4 import BeautifulSoup
import re
from tqdm import tqdm
import json
import argparse
import datetime
honapok = {
    "jan": 1,
    "febr": 2,
    "feb": 2,
    "márc": 3,
    "már": 3,
    "ápr": 4,
    "máj": 5,
    "jún": 6,
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
    paplista = []
    for source in sources:
        response = requests.get(source["url"])
        if response.status_code == 200:
            html_content = response.content
        else:
            print("Failed to fetch the website.")

        soup = BeautifulSoup(html_content, 'html.parser')

        for pap in soup.select(".qx-element-person"):
            options = {**source["options"]}
            print(pap.select_one("h4").text)
            if pap.select_one("h4").text == "Balás Béla":
                options["bishop"] = True
            imgSrc = pap.select_one("img").get("src")
            paplista.append({
                "name": pap.select_one("h4").text,
                "birth": str2date(pap.select_one(".qx-person-description p").text.split("Szent.:")[0].split(", ")[1]),
                "img": imgSrc,
                "src": source["url"],
                **options
            })

    if filename == None:
        return paplista
    else:
        with open(filename, "w") as outfile:
            outfile.write(json.dumps(paplista))


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
