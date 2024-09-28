import requests
from bs4 import BeautifulSoup
import re
from tqdm import tqdm
import  json
import argparse

def VFEM(filename=None, year=None):
    # Replace this with the URL of the website you want to scrape
    url = 'https://archiv.veszpremiersekseg.hu/kereso/'
    response = requests.get(url)
    # Check if the request was successful
    if response.status_code == 200:
        html_content = response.content
    else:
        print("Failed to fetch the website.")

    # Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
    papok = []
    for pap in soup.select_one(".priests-list").findAll("li"): 
        if "Érsek" in pap.text or "Nyugalomban" in pap.text: # Nyugállományban lévő papokat és a püspököket nem számítjul
            continue
        papok.append(pap.select_one('a')['href']) # Papi oldalak linkjei


    paplista = []
    for pap in tqdm(papok): # Nézze meg az összes pap linkjét
        try: # Kétszeri próbálkozásra szokott menni
            response = requests.get(url+pap, verify=False)
            if response.status_code == 200:
                html_content = response.content
            else:
                print("Failed to fetch the website.")
        except:
            try:
                response = requests.get(url+pap, verify=False)
                if response.status_code == 200:
                    html_content = response.content
                else:
                    print("Failed to fetch the website.")
            except:
                print("Big error")
                continue


        soup = BeautifulSoup(html_content, 'html.parser')
        imgSrc = ""
        try:
            imgSrc = soup.select_one("#maincontent img").get("src")
        except:
            pass
        nev = soup.select_one(".priest-details").select_one("h2").text.replace("  ", " ")
        if nev == "Bedy Imre": paplista.append({"name": "Bedy Imre", "birth": 1982, "img": imgSrc, "src": url + pap}) #Nem jó weboldal, vessző hiányzik
        elif nev == "Dékány Árpád Sixtus O. Cist": paplista.append({"name": "Dékány Árpád Sixtus O. Cist", "birth": 1969, "img": imgSrc, "src": url + pap}) #Forrás: https://hu.wikipedia.org/wiki/D%C3%A9k%C3%A1ny_Sixtus
        elif nev == "Holubák Attila": paplista.append({"name": "Holubák Attila", "birth": 1970, "img": imgSrc, "src": url + pap}) #Nem jó weboldal, vessző hiányzik
        elif nev == "Kulcsár Dávid dr.": paplista.append({"name": "Kulcsár Dávid dr.", "birth": 1990, "img": imgSrc, "src": url + pap}) #Nem jó weboldal, vessző hiányzik
        else: paplista.append({"name": nev, "birth": int(soup.select_one(".pap-profil").text.split("Született")[1].split(", ")[1].split(".")[0]), "img": imgSrc, "src": url + pap})



    if filename == None: return paplista
    else:
        with open(filename, "w") as outfile:
            outfile.write(json.dumps(paplista))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                        description='Veszprémi főegyházmegye papjainak adatai')
    parser.add_argument('--filename', required=False, action="store", default=None, help="JSON to save. If not set, the result will be displayed on screen")

    args = parser.parse_args()

    if args.filename==None: print(VFEM(args.filename))
    else: VFEM(args.filename)