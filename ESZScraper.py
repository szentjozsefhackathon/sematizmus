import requests
from bs4 import BeautifulSoup
import re
from tqdm import tqdm
import json
import argparse
import datetime
from orderAbbreviation import orderAbbreviation
from deleteDr import deleteDr


@deleteDr
@orderAbbreviation
def ESZ(filename=None, year=None):
    url = "http://esztergomiszeminarium.eu/kispapok/"
    response = requests.get(url, verify=False)
    if response.status_code == 200:
        html_content = response.content
    else:
        print(f"{url} - Failed to fetch the website.")

    soup = BeautifulSoup(html_content, 'html.parser')
    kispaplista = []
    for kispap in soup.select(".gallery-item"):
        imgSrc = "?".join(kispap.select_one("img").get("src").split("?")[:-1])
        kispaplista.append({
            "name": kispap.select_one("figcaption").text,
            "img": imgSrc,
            "src": url,
            "seminarist": True
        })
    

    if filename == None:
        return kispaplista
    else:
        with open(filename, "w") as outfile:
            outfile.write(json.dumps(kispaplista, default=str))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Esztergomi Szeminárium papnövendékeinek adatai')
    parser.add_argument('--filename', required=False, action="store", default=None,
                        help="JSON to save. If not set, the result will be displayed on screen")

    args = parser.parse_args()

    if args.filename == None:
        print(ESZ(args.filename))
    else:
        ESZ(args.filename)
