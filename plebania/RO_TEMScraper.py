import requests
from bs4 import BeautifulSoup
import json
import argparse
from getPriest import get_priest

def RO_TEM(filename=None, year=None):
    url = 'https://gerhardus.ro/hu/plebaniak-2/'
    response = requests.get(url, verify=False)
    if response.status_code == 200:
        html_content = response.content
    else:
        print(f"{url} - Failed to fetch the website.")

    soup = BeautifulSoup(html_content, 'html.parser')
    plebanialista = []
    for plebania in soup.select(".fusion-panel"):
        for br in plebania.find_all("br"):
            br.replace_with("\n")
        parishioner = {}
        phones = []
        websites = []
        emails = []
        postalCode = ""
        settlement = ""
        address = ""

        for row in plebania.get_text().splitlines():
            if "segédlelkész" in row.lower() or "diakónus" in row.lower():
                break
            if "honlap" in row.lower():
                for ws in ":".join(row.split(":")[1:]).strip().replace(" ","").split(","):
                    websites.append(ws.strip())
            if "e-mail" in row.lower():
                for email in ":".join(row.split(":")[1:]).strip().replace(" ","").split(","):
                    emails.append(email.strip())


        for row in plebania.get_text(strip=True, separator="\n").splitlines():
            if "segédlelkész" in row.lower() or "diakónus" in row.lower():
                break
            if "plébános" in row.lower() or "plébániai kormányzó" in row.lower():
                try:
                    parishioner_name = " ".join([nev for nev in row.split(":")[1].strip().split("Ft.")[-1].split(" ") if nev!="" and nev[0].isupper()])
                    parishioner = get_priest("https://gerhardus.ro/hu/plebaniak-2/", parishioner_name, dontFind=True)
                except:
                    print(f"{url} - {row} - Plébános feldolgozási hiba")
            if ("telefon" in row.lower() or "tel" in row.lower()) and not "szentel" in row.lower():
                for phone in row.split(":")[-1].strip().replace(" / ", ",").replace(" ", "").replace("-", "").replace("/", "").replace("(", "").replace(")", "").replace(";",",").split(","):
                    _phone = "".join([p for p in phone if p.isdigit()])
                    if len(_phone) > 0:
                        phones.append(f'0040{_phone}')
            if "honlap" in row.lower():
                for ws in ":".join(row.split(":")[1:]).strip().replace(" ","").split(","):
                    websites.append(ws.strip())
            if "cím" in row.lower():
                try: 
                    fullAddress = row.split(":")[-1].strip()
                    postalCode = fullAddress.split(" ")[0]
                    settlement = " ".join(fullAddress.split(",")[0].split(" ")[1:])
                    address = fullAddress.split(f"{settlement},")[1].strip()
                except:
                    print(f"{url} - {row} - Cím feldolgozási hiba")
            if "e-mail" in row.lower():
                for email in ":".join(row.split(":")[1:]).strip().replace(" ","").split(","):
                    emails.append(email.strip())

        emails = list(set([email.strip() for email in emails if email.strip() != ""]))
        phones = list(set([phone.strip() for phone in phones if phone.strip() != ""]))
        websites = list(set([website.strip() for website in websites if website.strip() != ""]))
        plebanialista.append({
            "name": plebania.select_one("h4").text.strip(),
            "src": url,
            "postalCode": postalCode,
            "settlement": settlement,
            "address": address,
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
        description='Temesvári egyházmegye plébániáinak adatai')
    parser.add_argument('--filename', required=False, action="store", default=None,
                        help="JSON to save. If not set, the result will be displayed on screen")

    args = parser.parse_args()

    if args.filename == None:
        print(RO_TEM(args.filename))
    else:
        RO_TEM(args.filename)
