import requests
from bs4 import BeautifulSoup
import json
import argparse
from getPriest import get_priest

def KEM(filename=None, year=None):
    url = 'https://kaposvar.egyhazmegye.hu/index.php/plebaniak/plebaniak'
    response = requests.get(url, verify=False)
    if response.status_code == 200:
        html_content = response.content
    else:
        print(f"{url} - Failed to fetch the website.")

    soup = BeautifulSoup(html_content, 'html.parser')
    plebanialista = []
    for plebania in soup.select(".qx-element-person"):
        if "Ellátja: " in plebania.text:
            continue
        description = plebania.select_one(".qx-person-description")
        for br in description.find_all("br"):
            br.replace_with("\n")
        rows = description.text.splitlines()
        parishioner = {}
        phones = []
        websites = []
        emails = []

        for row in rows:
            if "diakónus" in row.lower():
                break
            if row.lower().startswith("plébános:") or row.lower().startswith("plébániai kormányzó:"):
                parishioner_name = " ".join([nev for nev in row.split(":")[1].strip().split(" ") if nev!="" and nev[0].isupper()])
                parishioner = get_priest(None, parishioner_name, dontFind=True)
            if row.lower().startswith("tel.:"):
                fullRow = row.split(":")[1].split("(")[0].replace(" ", "").replace("/","").replace("-","").replace("+36","").split(",")
                for phone in fullRow:
                    if phone.strip() != "":
                        phones.append("0036" + phone.strip())
            if row.lower().startswith("web:"):
                websites = ":".join(row.split(":")[1:]).strip().replace(" ", "").split(",")
            if row.lower().startswith("e-mail:"):
                emails = row.split(":")[1].strip().replace(" ", "").split(",")

        plebanialista.append({
            "name": plebania.select_one("h4").text.split("Plébánia")[-1].strip(),
            "src": url,
            "postalCode": rows[0].split(" ")[0].strip() if rows[0].split(" ")[0].isdigit() else "",
            "settlement": rows[0].split(" ")[1].strip().title() if rows[0].split(" ")[0].isdigit() else "",
            "address": rows[1].strip() if rows[0].split(" ")[0].isdigit() else "",
            "phones": phones,
            "websites": websites,
            "emails": emails,
            "parishioner": parishioner
        })
    

    if filename == None:
        return plebanialista
    else:
        with open(filename, "w") as outfile:
            outfile.write(json.dumps(plebanialista, default=str))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Kaposvári egyházmegye plébániáinak adatai')
    parser.add_argument('--filename', required=False, action="store", default=None,
                        help="JSON to save. If not set, the result will be displayed on screen")

    args = parser.parse_args()

    if args.filename == None:
        print(KEM(args.filename))
    else:
        KEM(args.filename)
