import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import  json
import argparse
from getPriest import get_priest

def VFEM(filename=None, year=None):
    # Replace this with the URL of the website you want to scrape
    url = 'https://www.veszpremiersekseg.hu/plebaniak/'
    response = requests.get(url)
    # Check if the request was successful
    if response.status_code == 200:
        html_content = response.content
    else:
        print("VFEM - Failed to fetch the website.")

    # Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
    plebanialista = []
    for plebania in tqdm(soup.select("article")):
        rows = plebania.select_one(".tetel-tartalom").get_text(strip=True, separator="\n").split("\n")
        try:
            if len(rows) == 3:
                plebanialista.append({
                    "name": plebania.select_one(".entry-title").text.title(),
                    "src": "https://www.veszpremiersekseg.hu/plebaniak/",
                    "parishioner": get_priest("https://www.veszpremiersekseg.hu/papok/", rows[1].strip(), dontFind=True),
                    "postalCode": rows[2].split(" ")[0],
                    "settlement": rows[2].split(" ")[1].replace(",",""),
                    "address": " ".join(rows[2].split(" ")[2:]).strip(),
                })
            if len(rows) == 2:
                szamok = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]
                if not rows[1].startswith(tuple(szamok)):
                    plebanialista.append({
                        "name": plebania.select_one(".entry-title").text.title(),
                        "src": "https://www.veszpremiersekseg.hu/plebaniak/",
                        "parishioner": get_priest("https://www.veszpremiersekseg.hu/papok/", rows[1].strip(), dontFind=True),
                        "postalCode": "",
                        "settlement": "",
                        "address": "",
                    })
        except Exception as e:
            print(f"Error processing {plebania.select_one('.entry-title').text}: {e}")
            print(rows)
            continue




    if filename == None: return plebanialista
    else:
        with open(filename, "w") as outfile:
            outfile.write(json.dumps(plebanialista, default=str))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                        description='Veszprémi főegyházmegye plébániáinak adatai')
    parser.add_argument('--filename', required=False, action="store", default=None, help="JSON to save. If not set, the result will be displayed on screen")

    args = parser.parse_args()

    if args.filename==None: print(VFEM(args.filename))
    else: VFEM(args.filename)