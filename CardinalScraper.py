import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import  json
import re
import argparse
import datetime
from orderAbbreviation import orderAbbreviation
from deleteDr import deleteDr

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
}

def str2date(datum):
    datum = datum.replace(".", ". ").replace("  ", " ")
    reszek = [d.split(".")[0].strip() for d in datum.strip().split(" ")]
    return datetime.date(int(reszek[0]), honapok[reszek[1]], int(reszek[2]))

# @deleteDr
# @orderAbbreviation
def Cardinal(filename=None, year=None):
    # Replace this with the URL of the website you want to scrape
    url = 'https://hu.wikipedia.org/wiki/A_harmadik_%C3%A9vezred_b%C3%ADborosainak_list%C3%A1ja'
    response = requests.get(url)
    # Check if the request was successful
    if response.status_code == 200:
        html_content = response.content
    else:
        print("Cardinal - Failed to fetch the website.")

    # Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
    biboroslista = []
    for tablazat in tqdm(soup.select("table.wikitable")):
        fejlecek = [th.text.strip().split('[')[0] for th in tablazat.find_all('th')]
        if not (len(fejlecek) >= 3 and "Név" in fejlecek):
            continue

        sorok = tablazat.find_all('tr')[1:]
        for sor in sorok:

            oszlopok = sor.find_all('td')
            if len(oszlopok) < 3:
                continue

            nev = re.sub(r'\[.*?\]', '', oszlopok[2].text.strip()).replace("\n", ", ")
            
            szuletes = str2date(oszlopok[5].text.strip())
            imgSrc = ""
            try:
                imgSrc = oszlopok[0].find("img").get("src")
            except:
                pass
            src = ""
            try:
                src = "https://hu.wikipedia.org" + oszlopok[2].find("a").get("href")
            except:
                src = url
                pass
            if "#" in src:
                src = url
            biboroslista.append({
                "name": nev,
                "birth": szuletes,
                "img": imgSrc,
                "src": src,
                "seminarist": False
            })
    # print(biboroslista)
    if filename == None: return biboroslista
    else:
        with open(filename, "w") as outfile:
            outfile.write(json.dumps(biboroslista, default=str))



if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                        description='Bíboroosok adatai')
    parser.add_argument('--filename', required=False, action="store", default=None, help="JSON to save. If not set, the result will be displayed on screen")

    args = parser.parse_args()

    if args.filename==None: print(Cardinal(args.filename))
    else: Cardinal(args.filename)