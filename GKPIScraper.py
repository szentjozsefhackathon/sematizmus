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
def GKPI(filename=None, year=None):
    url = "https://szeminarium.gorogkatolikus.hu/papnovendekek/"
    response = requests.get(url, verify=False)
    if response.status_code == 200:
        html_content = response.content
    else:
        print(f"{url} - Failed to fetch the website.")

    soup = BeautifulSoup(html_content, 'html.parser')
    kispaplista = []
    for kispap in soup.select(".entry-content .wp-block-column figure"):
        imgSrc = kispap.select_one("img").get("src")
        if imgSrc == "https://szeminarium.gorogkatolikus.hu/wp-content/uploads/2023/03/john-doe.jpg":
            imgSrc = None
        kispaplista.append({
            "name": kispap.select_one("figcaption").text.split(" (")[0],
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
        description='Görögkatolikus Papnevelő Intézet papnövendékeinek adatai')
    parser.add_argument('--filename', required=False, action="store", default=None,
                        help="JSON to save. If not set, the result will be displayed on screen")

    args = parser.parse_args()

    if args.filename == None:
        print(GKPI(args.filename))
    else:
        GKPI(args.filename)
