import requests
from bs4 import BeautifulSoup
from tqdm.contrib.concurrent import process_map
import  json
import argparse
from multiprocessing import Pool
from getPriest import get_priest

import urllib3
urllib3.disable_warnings(category=urllib3.exceptions.InsecureRequestWarning)

def processParish(link):
        try: # Kétszeri próbálkozásra szokott menni
            response = requests.post(link, data={"xajax": "acm_plebania_xr_create_acm_scms"}, verify=False)
            if response.status_code == 200:
                html_content = response.content
            else:
                print(f"{link} - Failed to fetch the website.")
        except:
            try:
                response = requests.post(link, data={"xajax": "acm_plebania_xr_create_acm_scms"}, verify=False)
                if response.status_code == 200:
                    html_content = response.content
                else:
                    print(f"{link} - Failed to fetch the website.")
            except:
                print(f"{link} - Big error")
                return


        soup = BeautifulSoup(html_content)
        xmlsoup = BeautifulSoup(html_content, features="xml")
        try:
            name = xmlsoup.select_one('[t="plebania_nev"]').text
            name = name.split("]]>")
            name = name[0]
            name = name.strip()
            name = name.split(" ")
            name = " ".join(name)
        except:
            print(f"Error processing name for {link}")
        if "lelkészség" in name:
            return None
        
        if soup.select_one('[t="plebania_vezeto"]') and "oldallagosan" in soup.select_one('[t="plebania_vezeto"]').text.lower():
            return None
        
        websites = [soup.select_one('[t="plebania_alapadatok"] a')['href']] if soup.select_one('[t="plebania_alapadatok"] a') else []
        parishioner_a = soup.select_one('[t="plebania_vezeto"] a')
        parishioner = {}
        if parishioner_a:
            parishioner = get_priest("http://sematizmus.vaciegyhazmegye.hu" + parishioner_a['href'], parishioner_a.text.strip())
        

        postalCode = ""
        settlement = ""
        address = ""
        phones = []

        for sor in soup.select("[t='plebania_hivatal'] tr"):
            if "telefon" in sor.select("td")[0].text.lower():
                phones.append(sor.select("td")[1].text.strip())
            if "cím" in sor.select("td")[0].text.lower() and postalCode == "":
                fullAddress = sor.select("td")[1].text.strip()
                if fullAddress != "":
                    postalCode = fullAddress.split(" ")[0]
                    settlement = fullAddress.split(",")[0].split(" ")[1]
                    address = fullAddress.split(",")[1].strip()
        phones = [f"0036{phone.replace(' ', '').replace('-', '').replace('/', '').replace('(','').replace(')','')}" for phone in phones]
        return {
            "name": name,
            "src": link,
            "websites": websites,
            "parishioner": parishioner,
            "emails": [],
            "phones": phones,
            "postalCode": postalCode,
            "settlement": settlement,
            "address": address
        }

        

def VEM(filename=None, year=None):
    # Replace this with the URL of the website you want to scrape
    url = 'http://sematizmus.vaciegyhazmegye.hu/plebania.php?lista=pl'
    response = requests.post(url, data={"xajax": "acm_plebania_lista_xr_create_acm_scms"}, verify=False)
    # Check if the request was successful
    if response.status_code == 200:
        html_content = response.content
    else:
        print(f"{url} - Failed to fetch the website.")

    # Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(html_content)
    plebaniak = []
    for plebania in soup.select(".grid-uri"): 
        plebaniak.append("http://sematizmus.vaciegyhazmegye.hu/"+plebania['href'])

            
    plebanialista = []
    plebanialista = process_map(processParish, plebaniak)

    plebanialista = [x for x in plebanialista if x is not None]
    if filename == None: return plebanialista
    else:
        with open(filename, "w") as outfile:
            outfile.write(json.dumps(plebanialista, default=str))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                        description='Váci egyházmegye plébániáinak adatai')
    parser.add_argument('--filename', required=False, action="store", default=None, help="JSON to save. If not set, the result will be displayed on screen")

    args = parser.parse_args()

    if args.filename==None: print(VEM(args.filename))
    else: VEM(args.filename)