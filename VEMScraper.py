import requests
from bs4 import BeautifulSoup
import re
from tqdm import tqdm
import  json
import argparse
import datetime
from multiprocessing import Pool
from orderAbbreviation import orderAbbreviation
import urllib3
urllib3.disable_warnings(category=urllib3.exceptions.InsecureRequestWarning)

honapok = {
    "I": 1,
    "II": 2,
    "III": 3,
    "IV": 4,
    "V": 5,
    "VI": 6,
    "VII": 7,
    "VIII": 8,
    "IX": 9,
    "X": 10,
    "XI": 11,
    "XII": 12
}
def str2date(datum):
    reszek = [d.strip() for d in datum.split(".")]
    if reszek[0] == "1987 –": # Görbe József
        return 1987
    return datetime.date(int(reszek[0]), honapok[reszek[1]], int(reszek[2]))
def processPriest(link, retired):
        try: # Kétszeri próbálkozásra szokott menni
            response = requests.post(link, data={"xajax": "acm_szemely_xr_create_acm_scms"}, verify=False)
            if response.status_code == 200:
                html_content = response.content
            else:
                print(f"{link} - Failed to fetch the website.")
        except:
            try:
                response = requests.post(link, data={"xajax": "acm_szemely_xr_create_acm_scms"}, verify=False)
                if response.status_code == 200:
                    html_content = response.content
                else:
                    print(f"{link} - Failed to fetch the website.")
            except:
                print(f"{link} - Big error")
                return


        soup = BeautifulSoup(html_content, features="lxml")

        ordination = None
        try:
            for feladat in soup.select('[t="szemely_feladatkor_ellatasok"] tr'):
                if "Papi igazolvány sorszáma" in str(soup.text) and "Áldozópap" in feladat.text:
                    ordination = str2date(re.search(r'\(([^)]+)\)', feladat.text).group(1))
                    continue
                if "Diakónus igazolvány sorszáma" in str(soup.text) and "Állandó diakónus" in feladat.text:
                    ordination = str2date(re.search(r'\(([^)]+)\)', feladat.text.split("(állandó nős diakónus)")[1].strip()).group(1))

        except Exception as e:
            print(link)
            print(soup.select_one('[t="szemely_nev"]').text.split("]]>")[0].strip())
            print(e)                

        imgSrc = ""
        try:
            imgSrc = "http://sematizmus.vaciegyhazmegye.hu" + re.search(r'<img src="([^"]+)" class="scm-szemely-fenykep"', str(html_content)).group(1)
        except:
            pass
        try:
            name = (" ".join([n for n in soup.select_one('[t="szemely_nev"]').text.split("]]>")[0].strip().split(" ") if n[0].isupper()])).split(",")[0].split("P.")[-1].strip()
            return {
                "name": name, # A pap neve
                "img": imgSrc, # A kép linkje,
                "src": link,
                "deacon": "Diakónus igazolvány sorszáma" in str(soup.text),
                "bishop": "feladatkor.php?id=243" in str(soup) or "feladatkor_kategoria.php?id=15&egyhazmegye=true" in str(soup),
                "retired": retired,
                "ordination": ordination,
            }
        except Exception as e:
            print(e)
            print(link)
        return

@orderAbbreviation
def VEM(filename=None, year=None):
    # Replace this with the URL of the website you want to scrape
    url = 'http://sematizmus.vaciegyhazmegye.hu/szemely.php?lista=cl'
    response = requests.post(url, data={"xajax": "acm_szemely_lista_xr_create_acm_scms"}, verify=False)
    # Check if the request was successful
    if response.status_code == 200:
        html_content = response.content
    else:
        print(f"{url} - Failed to fetch the website.")

    # Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(html_content, features="lxml")
    papok = {}
    for pap in soup.select(".grid-uri"): 
        papok["http://sematizmus.vaciegyhazmegye.hu/"+pap['href']] = False # Papi oldalak linkjei

    url = 'http://sematizmus.vaciegyhazmegye.hu/szemely.php?lista=ny'
    response = requests.post(url, data={"xajax": "acm_szemely_lista_xr_create_acm_scms"}, verify=False)
    # Check if the request was successful
    if response.status_code == 200:
        html_content = response.content
    else:
        print(f"{url} - Failed to fetch the website.")
    
    # Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(html_content, features="lxml")
    for pap in soup.select(".grid-uri"):
        papok["http://sematizmus.vaciegyhazmegye.hu/"+pap['href']] = True # Aki nyugdíjas tegye nyugdíjba
    
    url = 'http://sematizmus.vaciegyhazmegye.hu/szemely.php?lista=tr'
    response = requests.post(url, data={"xajax": "acm_szemely_lista_xr_create_acm_scms"}, verify=False)
    # Check if the request was successful
    if response.status_code == 200:
        html_content = response.content
    else:
        print(f"{url} - Failed to fetch the website.")
    
    # Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(html_content, features="lxml")
    for pap in soup.select(".grid-uri"):
        papok.pop("http://sematizmus.vaciegyhazmegye.hu/"+pap['href'], None) # Aki elhunyt, vegye ki

            
    paplista = []
    with Pool() as p:
        paplista = p.starmap(processPriest, list(papok.items()))

    paplista = [x for x in paplista if x is not None]
    if filename == None: return paplista
    else:
        with open(filename, "w") as outfile:
            outfile.write(json.dumps(paplista, default=str))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                        description='Váci egyházmegye papjainak adatai')
    parser.add_argument('--filename', required=False, action="store", default=None, help="JSON to save. If not set, the result will be displayed on screen")

    args = parser.parse_args()

    if args.filename==None: print(VEM(args.filename))
    else: VEM(args.filename)