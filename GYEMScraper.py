import requests
from bs4 import BeautifulSoup
import re
from tqdm import tqdm
import json
import argparse
import datetime
from orderAbbreviation import orderAbbreviation
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
@orderAbbreviation
def GYEM(filename=None, year=None):

    url = 'https://gyor.egyhazmegye.hu/api/priest?limit=116&offset=0'
    response = requests.get(url, verify=False)
    if response.status_code == 200:
        json_content = json.loads(response.content)
    else:
        print(f"{url} - Failed to fetch the website.")
    
    url = f'https://gyor.egyhazmegye.hu/api/priest?limit={json_content["totalElements"]}&offset=0' #Ezzel lesz időtálló
    response = requests.get(url, verify=False)
    if response.status_code == 200:
        json_content = json.loads(response.content)
    else:
        print(f"{url} -  to fetch the website.")
    paplista = []


    for pap in tqdm(json_content["items"]):
        soup = BeautifulSoup(pap["text"], 'html.parser')
        birth = None
        ordination = None
        for sor in soup.select("p"):
            if "Született" in sor.text:
                try:
                    birth = str2date(sor.text.split(", ")[1])
                except:
                    try:
                        birth = str2date(sor.text.split(", ")[2])
                    except: 
                        try:
                            birth = str2date(sor.text.split(": ")[1].split(", ")[0])
                        except:
                            try:
                                birth = str2date(" ".join(sor.text.split(" ")[-3:]))
                            except:
                                try: 
                                    birth = str2date(sor.text.split(",")[1])
                                except:
                                    try: 
                                        birth = str2date(" ".join(sor.text.split(" ")[-4:]))
                                    except: pass
            if "Papszentelés" in sor.text or "Pappá szentelték" in sor.text or "Pappá szentelés" in sor.text:
                try:
                    ordination = str2date(sor.text.split(", ")[1])
                except:
                    try:
                        ordination = str2date(sor.text.split(", ")[2])
                    except: 
                        try:
                            ordination = str2date(sor.text.split(": ")[1].split(", ")[0])
                        except:
                            try:
                                ordination = str2date(" ".join(sor.text.split(" ")[-3:]))
                            except:
                                try: 
                                    ordination = str2date(sor.text.split(",")[1])
                                except:
                                    try: 
                                        ordination = str2date(" ".join(sor.text.split(" ")[-4:]))
                                    except: pass
        if "ordainment" in pap and pap["ordainment"] != None:
            reszek =  pap["ordainment"].split("T")[0].split("-")
            ordination = datetime.date(int(reszek[0]), honapok[reszek[1]], int(reszek[2]))
            
        if "name" == "Sárai-Szabó Kelemen OSB":
            birth = datetime.date(1981, 2, 17)

        if ordination == None:
            print(f"https://gyor.egyhazmegye.hu/#/egyhazmegyenk/papok/{pap['id']} - Szentelés hiba")
        paplista.append({
            "name": pap["name"].strip(),
            "birth": birth,
            "img": pap["profileImageUrl"],
            "src": f"https://gyor.egyhazmegye.hu/#/egyhazmegyenk/papok/{pap['id']}",
            "retired": pap["type"] == "NYUGDIJAS",
            "bishop": pap["name"] == "Dr. Veres András" or pap["name"] == "Dr. Pápai Lajos ",
            "ordination": ordination
        })

    if filename == None:
        return paplista
    else:
        with open(filename, "w") as outfile:
            outfile.write(json.dumps(paplista,  default=str))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Győri egyházmegye papjainak adatai')
    parser.add_argument('--filename', required=False, action="store", default=None,
                        help="JSON to save. If not set, the result will be displayed on screen")

    args = parser.parse_args()

    if args.filename == None:
        print(GYEM(args.filename))
    else:
        GYEM(args.filename)
