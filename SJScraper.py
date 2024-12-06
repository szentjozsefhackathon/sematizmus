import requests
from bs4 import BeautifulSoup
import re
from tqdm import tqdm
import json
import argparse
import datetime
from tqdm.contrib.concurrent import process_map
from deleteDr import deleteDr
import urllib3
urllib3.disable_warnings(category=urllib3.exceptions.InsecureRequestWarning)

def processPriest(pap):
        try: # Kétszeri próbálkozásra szokott menni
            response = requests.get(f"https://jezsuita.hu/api/api/portraits/{pap}", verify=False)
            if response.status_code == 200:
                json_content = json.loads(response.content)
            else:
                print(f"{pap} - Failed to fetch the website.")
        except:
            try:
                response = requests.get(f"https://jezsuita.hu/api/api/portraits/{pap}", verify=False)
                if response.status_code == 200:
                    json_content = json.loads(response.content)
                else:
                    print(f"{pap} - Failed to fetch the website.")
            except:
                print(f"{pap} - Big error")
                return

        birth = None

        try:
            birth = datetime.date(int(json_content["birthday"].split("-")[0]), int(json_content["birthday"].split("-")[1]), int(json_content["birthday"].split("-")[2]))
        except:
            pass

        retired = False
        try:
            retired = "nyugdíjas" in json_content["task"]
        except: pass
        return {
            "name": json_content["name"], # A pap neve
            "birth": birth, # Születési dátum
            "ordination": None,
            "img": f"https://jezsuita.hu{json_content['avatar']['url']}", # A kép linkje,
            "src": f"https://jezsuita.hu/arckepcsarnok/{pap}",
            "retired": retired,
            "bishop": False,
            "deacon": None,
            "orderAbbreviation": "SJ"
        }


@deleteDr
def SJ(filename=None, year=None):
    # Replace this with the URL of the website you want to scrape
    url = 'https://jezsuita.hu/api/api/portraits?status=ALIVE&type=PRIEST'
    response = requests.get(url, verify=False)
    # Check if the request was successful
    if response.status_code == 200:
        json_content = json.loads(response.content)
    else:
        print(f"{url} - Failed to fetch the website.")

    papok = [pap["slug"] for pap in json_content]

    paplista = process_map(processPriest, papok)
    paplista = [p for p in paplista if p != None]

    if filename == None: return paplista
    else:
        with open(filename, "w") as outfile:
            outfile.write(json.dumps(paplista, default=str))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                        description='Jézus Társasága papjainak adatai')
    parser.add_argument('--filename', required=False, action="store", default=None, help="JSON to save. If not set, the result will be displayed on screen")

    args = parser.parse_args()

    if args.filename==None: print(SJ(args.filename))
    else: SJ(args.filename)