import requests
from bs4 import BeautifulSoup
import re
from tqdm import tqdm
import json
import argparse
from multiprocessing import Pool
from getPriest import get_priest

def processDeanDistrict(link):
        try:
            response = requests.get(link)
            if response.status_code == 200:
                html_content = response.content
            else:
                print(f"{link} - Failed to fetch the website.")
        except:
            try:
                response = requests.get(link)
                if response.status_code == 200:
                    html_content = response.content
                else:
                    print(f"{link} - Failed to fetch the website.")
            except:
                print(f"{link} - Big error")
                return

        soup = BeautifulSoup(html_content, 'html5lib')
        for hr in soup.select_one(".content-text").find_all("hr"):
            hr.replace_with("HRTORES12345")
        
        plebaniak_nyers = soup.select_one(".content-text").get_text().split("HRTORES12345")[1:]

        for i in range(len(plebaniak_nyers)):
            while plebaniak_nyers[i].count("\n\n") > 1:
                plebaniak_nyers[i] = plebaniak_nyers[i].replace("\n\n", "\n")
        plebaniak_nyers = [p.strip() for p in plebaniak_nyers if len(p.strip()) > 0]
        for i in range(len(plebaniak_nyers)):
            plebaniak_nyers[i] = plebaniak_nyers[i].splitlines()

        with open("plebaniak_nyers.json", "w") as f:
            f.write(json.dumps(plebaniak_nyers, indent=4, ensure_ascii=False)) 
        
        plebaniak = []
        for plebania in plebaniak_nyers:
            if "ellátja" in "".join(plebania).lower():
                continue
            if "közösségi ház" in plebania[0].lower():
                continue
            if "templom" in plebania[0].lower() and not "plébánia" in plebania[0].lower():
                continue
            parishioner = {}
            phones = []
            settlement = None
            emails = set()
            name = plebania[0].strip().replace("plébánia", "").replace("Plébánia", "").strip()
            postalCode = plebania[1].split("-")[0].replace("Cím:","").strip()
            settlement = plebania[1].split(",")[0].split("-")[1].strip()
            address = ",".join(plebania[1].split(",")[1:]).strip()

            for row in plebania[2:]:
                parishionerStarts = ["Plébános"]

                for start in parishionerStarts:
                    if row.startswith(start):
                        parishionerName = []
                        for s in row.replace("fr. ","").split(":")[1].strip().split(" "):
                            if len(s) > 0 and s[0].isupper():
                                parishionerName.append(s.split(",")[0].strip())
                            else:
                                break

                        parishionerName = " ".join(parishionerName)
                        parishioner = get_priest(None, parishionerName, dontFind=True)
                        break
                if row.startswith("Telefon"):
                    for p in row.split(":")[1].strip().replace(" ","").replace("/","").replace("-","").replace(";",",").split(","):
                        phones.append("0040" + p.strip())
                
        

                # if email address regexp in row, add email to emails
                email_regex = r'[a-zA-Z0-9._%+-]+@[A-Za-z0-9.-]+\.[a-zA-Z]{2,}'
                email_matches = re.findall(email_regex, row)
                if email_matches:
                    for email in email_matches:
                        emails.add(email.strip())

                
            try: 
                if parishioner != {}:
                    plebaniak.append({
                        "name": name, # A plébánia neve
                        "parishioner": parishioner, # A plébános
                        "src": link,
                        "emails": list(emails), # E-mail
                        "phones": phones, # Telefonszám
                        "websites": [], # Honlap
                        "postalCode": postalCode, # Irányítószám
                        "settlement": settlement, # Település
                        "address": address # Cím
                    })
            except:
                print(f"{link} - {name} - feldolgozási hiba") 
        return plebaniak


def RO_SZEM(filename=None, year=None):
    deanDistricts = [
        "https://www.szatmariegyhazmegye.ro/szatmari-foesperesseg/",
        "https://www.szatmariegyhazmegye.ro/Ugocsai-Esperesi-Kerulet/",
        "https://www.szatmariegyhazmegye.ro/Erdodi-Esperesi-Kerulet/",
        "https://www.szatmariegyhazmegye.ro/Nagykaroly-I-esperesi-kerulet/",
        "https://www.szatmariegyhazmegye.ro/Nagykaroly-II-Esperesi-Kerulet/",
        "https://www.szatmariegyhazmegye.ro/Nagybanyai-Esperesi-Kerulet/",
        "https://www.szatmariegyhazmegye.ro/Maramarosszigeti-esperesi-kerulet/"
    ]
    
    plebanialista = []

    with Pool() as p:
        plebanialista = p.map(processDeanDistrict, [(d) for d in deanDistricts])

    plebanialista = sum([x for x in plebanialista if x is not None], [])



    if filename == None:
        return plebanialista
    else:
        with open(filename, "w") as outfile:
            outfile.write(json.dumps(plebanialista, default=str))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Szatmári egyházmegye plébániáinak adatai')
    parser.add_argument('--filename', required=False, action="store", default=None,
                        help="JSON to save. If not set, the result will be displayed on screen")

    args = parser.parse_args()

    if args.filename == None:
        print(RO_SZEM(args.filename))
    else:
        RO_SZEM(args.filename)
