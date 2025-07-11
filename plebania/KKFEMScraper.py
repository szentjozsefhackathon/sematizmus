import requests
from bs4 import BeautifulSoup
import re
from tqdm import tqdm
import json
import argparse
import datetime
from multiprocessing import Pool

from getPriest import get_priest
def phone_format(phone):
    szamok = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"]
    phones = []
    if phone == None:
        return []
    phone = phone.replace("és", ";").replace("/", "").replace(" ", "").replace("-","").replace("+36","").replace(",",";")
    for p in phone.split(";"):
        _phone = "0036"
        for s in p.strip():
            if s in szamok:
                _phone += s
        if _phone!="0036":
            phones.append(_phone)
    return phones

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

        soup = BeautifulSoup(html_content, 'html.parser')
        plebaniak_nyers = []
        plebania = []
        elsoPlebania = True
        for div in soup.select("article div div div"):
            szamok = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]
            rows = div.get_text().splitlines()
            for row in rows:

                if (row.strip().startswith(tuple(szamok)) and row.strip()[1]==".") or (row.strip().startswith(tuple(szamok)) and row.strip()[1] in szamok and row.strip()[2]=="."):
                    if elsoPlebania:
                        plebania = []
                        elsoPlebania = False
                    else:
                        if len(plebania) > 0:
                            plebaniak_nyers.append(plebania)
                        plebania = []
                
                if len(row.strip()) > 0:
                    plebania.append(row.strip())
                    if "mobil" in row.lower():
                        print("Mobil")

        if len(plebania) > 0:
            plebaniak_nyers.append(plebania)
        
        

        for plebaniai in range(len(plebaniak_nyers)):
            for sori in range(len(plebaniak_nyers[plebaniai])):
                if "Tel.:" in plebaniak_nyers[plebaniai][sori] and not plebaniak_nyers[plebaniai][sori].startswith("Tel.:"):
                    plebaniak_nyers[plebaniai].append(None)
                    for i in range(sori+1, len(plebaniak_nyers[plebaniai])-1):
                        plebaniak_nyers[plebaniai][i+1] = plebaniak_nyers[plebaniai][i]
                    
                    plebaniak_nyers[plebaniai][sori+1] = "Tel.: " + plebaniak_nyers[plebaniai][sori].split("Tel.:")[1].strip()
                    plebaniak_nyers[plebaniai][sori] = plebaniak_nyers[plebaniai][sori].split("Tel.:")[0].strip()
                
                if "tel.:" in plebaniak_nyers[plebaniai][sori] and not plebaniak_nyers[plebaniai][sori].startswith("tel.:"):
                    plebaniak_nyers[plebaniai].append(None)
                    for i in range(sori+1, len(plebaniak_nyers[plebaniai])-1):
                        plebaniak_nyers[plebaniai][i+1] = plebaniak_nyers[plebaniai][i]
                    
                    plebaniak_nyers[plebaniai][sori+1] = "tel.: " + plebaniak_nyers[plebaniai][sori].split("tel.:")[1].strip()
                    plebaniak_nyers[plebaniai][sori] = plebaniak_nyers[plebaniai][sori].split("tel.:")[0].strip()
        plebaniak = []
        for rows in plebaniak_nyers:

            parishioner = {}
            phones = ""
            settlement = None
            emails = set()
            name = rows[0].split(".")[1].strip().replace(" - ","-").replace("plébánia","").replace("lelkészség","").strip()
            postalCode = rows[1].strip().replace("Pf.:","Pf.").split(":")[-1].strip().split(" ")[0]
            settlement = name.split("-")[0].strip()
            address = " ".join(rows[1].strip().replace("Pf.:","Pf.").split(":")[-1].strip().split(" ")[1:]).strip()

            for row in rows[2:]:
                parishionerStarts = ["Adminisztrátor",  "Plébános", "Pléb. korm.", "Plébániai kormányzó", "Administrator is spiritualibus", "Mb. adminisztrátor", "Plébánia vezető"]

                for start in parishionerStarts:
                    if row.startswith(start):
                        parishionerName = []
                        try:
                            for s in row.split(":")[1].strip().split(" "):
                                if len(s) > 0 and s[0].isupper():
                                    parishionerName.append(s.split(",")[0].strip())
                                else:
                                    break
                        except:
                            try: 
                                _row = row.split(start)[0].strip()
                                for s in _row.strip().split(" "):
                                    if len(s) > 0 and s[0].isupper():
                                        parishionerName.append(s.split(",")[0].strip())
                                    else:
                                        break
                            except:
                                print(f"{link} - {rows[0]} - parishioner")
                        parishionerName = " ".join(parishionerName)
                        parishioner = get_priest(link, parishionerName, dontFind=True)
                        break
                if row.startswith("E-mail:") or row.startswith("Email:"):
                    email = row.split(":")[1].strip()
                if row.startswith("Tel.:") or row.startswith("Mobil:") and phones == "":
                    phones = row.split(":")[1].strip()
                
                if "templomigazgató" in row.lower():
                    break
                if "kápolnaigazgató" in row.lower():
                    break
                if "káplán" in row.lower() and not "pápai káplán" in row.lower():
                    break
                if "lelkész" in row.lower() and not "egyetemi lelkész" in row.lower() and not "kórházlelkész" in row.lower() and not "iskolalelkész" in row.lower():
                    break
                if "diakónus" in row.lower():
                    break

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
                        "phones": phone_format(phones), # Telefonszám
                        "websites": [], # Honlap
                        "postalCode": postalCode, # Irányítószám
                        "settlement": settlement, # Település
                        "address": address # Cím
                    })
            except:
                print(f"{link} - {name} - feldolgozási hiba") 
        return plebaniak


def KKFEM(filename=None, year=None):
    deanDistricts = [
        "https://asztrik.hu/index.php/teruleti-beosztas/kalocsai-esperesi-kerulet",
        "https://asztrik.hu/index.php/teruleti-beosztas/keceli-esperesi-kerulet",
        "https://asztrik.hu/index.php/teruleti-beosztas/bacsalmasi-esperesi-kerulet",
        "https://asztrik.hu/index.php/teruleti-beosztas/janoshalmi-esperesi-kerulet",
        "https://asztrik.hu/index.php/teruleti-beosztas/bajai-esperesi-kerulet",
        "https://asztrik.hu/index.php/teruleti-beosztas/hajosi-esperesi-kerulet",
        "https://asztrik.hu/index.php/teruleti-beosztas/kecskemeti-esperesi-kerulet",
        "https://asztrik.hu/index.php/teruleti-beosztas/felegyhazi-esperesi-kerulet",
        "https://asztrik.hu/index.php/teruleti-beosztas/majsai-esperesi-kerulet",
        "https://asztrik.hu/index.php/teruleti-beosztas/solti-esperesi-kerulet"
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
        description='Kalocsa-Kecskeméti főegyházmegye plébániáinak adatai')
    parser.add_argument('--filename', required=False, action="store", default=None,
                        help="JSON to save. If not set, the result will be displayed on screen")

    args = parser.parse_args()

    if args.filename == None:
        print(KKFEM(args.filename))
    else:
        KKFEM(args.filename)
