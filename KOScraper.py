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
    reszek = [d.split(".")[0].strip() for d in datum.strip().split(" ")]
    return datetime.date(int(reszek[0]), honapok[reszek[1]], int(reszek[2]))

def KO(filename=None, year=None):
    # Replace this with the URL of the website you want to scrape
    url = 'https://ktp.hu/js/ajax/listazo.php?url=lelkeszek%2Ftabori-lelkeszi-kar&fm=110&am=173'
    response = requests.get(url, verify=False)
    # Check if the request was successful
    if response.status_code == 200:
        html_content = response.content
    else:
        print(f"{url} - Failed to fetch the website.")

    # Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    papok = []
    for sor in soup.findAll("a"):
        papok.append(sor['href']) # Papi oldalak linkjei

    papok.append("/lelkeszek/takacs-tamas")
    papok.append("/lelkeszek/tabori-puspok/eletrajz")
    paplista = []
    for pap in tqdm(papok): # Nézze meg az összes pap linkjét

        try: # Kétszeri próbálkozásra szokott menni
            response = requests.get(f"https://ktp.hu{pap}", verify=False)
            if response.status_code == 200:
                html_content = response.content
            else:
                print(f"https://ktp.hu{pap} - Failed to fetch the website.")
        except:
            try:
                response = requests.get(f"https://ktp.hu{pap}", verify=False)
                if response.status_code == 200:
                    html_content = response.content
                else:
                    print(f"https://ktp.hu{pap} - Failed to fetch the website.")
            except:
                print(f"https://ktp.hu{pap} - Big error")
                continue
        

        soup = BeautifulSoup(html_content, 'html.parser')
        imgSrc = ""
        try:
            imgSrc = "https://ktp.hu" + soup.select_one(".bordo img").get("src")
        except:
            pass
        
        name = ""
        if pap == "/lelkeszek/tabori-lelkeszi-kar/mikus-tibor":
            name = "Mikus Tibor"
        elif pap == "/lelkeszek/tabori-puspok/eletrajz":
            name = "Berta Tibor"
            imgSrc = "https://ktp.hu/uploads/content/177/kepek/c_letoltes.png"
        else: 
            name = soup.select_one(".bordo:first-child").text
        

        delimiter = '###'                           # unambiguous string
        for line_break in soup.findAll('br'):       # loop through line break tags
            line_break.replaceWith(delimiter)       # replace br tags with delimiter
        strings = soup.get_text().split(delimiter)  # get list of strings
        birth = None
        ordination = None

        for row in soup.get_text().split(delimiter):
            for subrow in row.split("\n"):
                if "Születési helye és ideje:" in subrow or "Születési helye, ideje:" in subrow:
                    try:
                        birth = str2date(subrow.split(",")[-1].replace(".", ". ").replace("  "," ").strip())
                    except:
                        print(soup.get_text().split(delimiter))
                        print(f'https://ktp.hu{pap} - {subrow}')
                if "Pappá szentelés helye, ideje:" in subrow or "Pappá szentelés helye és ideje:" in subrow:
                    try:
                        ordination = str2date(subrow.split(",")[-1].replace(".", ". ").replace("  "," ").strip())
                    except:
                        print(soup.get_text().split(delimiter))
                        print(f'https://ktp.hu{pap} - {subrow}')

        paplista.append({
            "name": name.title().strip(), # A pap neve
            "img": imgSrc, # A kép linkje,
            "birth": birth,
            "ordination": ordination,
            "bishop": name == "Berta Tibor",
            "src": f"https://ktp.hu{pap}"
        })
    
    paplista.append({
        "name": "Bíró László",
        "img": "https://ktp.hu/uploads/content/196/kepek/c_biro.jpg",
        "birth": datetime.date(1950,10,31),
        "ordination": datetime.date(1974,6,23),
        "bishop": True,
        "retired": True,
        "src": "https://ktp.hu/lelkeszek/tabori-puspok/elodok/biro-laszlo"
    })
    if filename == None: return paplista
    else:
        with open(filename, "w") as outfile:
            outfile.write(json.dumps(paplista, default=str))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                        description='Tábori püspökség papjainak adatai')
    parser.add_argument('--filename', required=False, action="store", default=None, help="JSON to save. If not set, the result will be displayed on screen")

    args = parser.parse_args()

    if args.filename==None: print(KO(args.filename))
    else: KO(args.filename)