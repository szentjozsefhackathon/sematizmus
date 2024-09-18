import requests
from bs4 import BeautifulSoup
import re
from tqdm import tqdm
import  json
import argparse

def VEM(filename=None, year=None):
    # Replace this with the URL of the website you want to scrape
    url = 'http://sematizmus.vaciegyhazmegye.hu/szemely.php?lista=cl'
    response = requests.post(url, data={"xajax": "acm_szemely_lista_xr_create_acm_scms"})
    # Check if the request was successful
    if response.status_code == 200:
        html_content = response.content
    else:
        print("Failed to fetch the website.")

    # Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(html_content, features="lxml")
    papok = []
    for pap in soup.select(".grid-uri"): 
        papok.append(pap['href']) # Papi oldalak linkjei


    paplista = []
    for pap in tqdm(papok): # Nézze meg az összes pap linkjét
        try: # Kétszeri próbálkozásra szokott menni
            response = requests.post("http://sematizmus.vaciegyhazmegye.hu/"+pap, data={"xajax": "acm_szemely_xr_create_acm_scms"})
            if response.status_code == 200:
                html_content = response.content
            else:
                print("Failed to fetch the website.")
        except:
            try:
                response = requests.post("http://sematizmus.vaciegyhazmegye.hu/"+pap, data={"xajax": "acm_szemely_xr_create_acm_scms"})
                if response.status_code == 200:
                    html_content = response.content
                else:
                    print("Failed to fetch the website.")
            except:
                print("Big error")
                continue


        soup = BeautifulSoup(html_content, features="lxml")
        imgSrc = ""
        try:
            imgSrc = "http://sematizmus.vaciegyhazmegye.hu" + re.search(r'<img src="([^"]+)" class="scm-szemely-fenykep"', str(html_content)).group(1)
        except:
            pass
        try:
            paplista.append({
                "name": soup.select_one('[t="szemely_nev"]').text.split("]]>")[0].strip(), # A pap neve
                "img": imgSrc, # A kép linkje,
                "src": f"http://sematizmus.vaciegyhazmegye.hu/{pap}"
            })
        except:
            print(f"http://sematizmus.vaciegyhazmegye.hu/{pap}")


    if filename == None: return paplista
    else:
        with open(filename, "w") as outfile:
            outfile.write(json.dumps(paplista))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                        description='Váci egyházmegye papjainak adatai')
    parser.add_argument('--filename', required=False, action="store", default=None, help="JSON to save. If not set, the result will be displayed on screen")

    args = parser.parse_args()

    if args.filename==None: print(VEM(args.filename))
    else: VEM(args.filename)