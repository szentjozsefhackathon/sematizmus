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
        for p in soup.select(".article p"):
            szamok = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]
            for strong in p.select("strong"):
                for szam in szamok:
                    if strong.text.startswith(szam):
                        if elsoPlebania:
                            plebania = []
                            elsoPlebania = False
                        else:
                            if len(plebania) > 0:
                                plebaniak_nyers.append(plebania)
                            plebania = []

            plebania.append(p.text.strip())
        if len(plebania) > 0:
            plebaniak_nyers.append(plebania)

        for plebaniai in range(len(plebaniak_nyers)):
            for sori in range(len(plebaniak_nyers[plebaniai])):
                if plebaniak_nyers[plebaniai][sori] == "Plébános:" or plebaniak_nyers[plebaniai][sori] == "Plébániai kormányzó:":
                    plebaniak_nyers[plebaniai][sori] = "Plébános: " + plebaniak_nyers[plebaniai][sori+1]
                    plebaniak_nyers[plebaniai][sori+1] = ""
                if "Tel.:" in plebaniak_nyers[plebaniai][sori] and not plebaniak_nyers[plebaniai][sori].startswith("Tel.:"):
                    plebaniak_nyers[plebaniai].append(None)
                    for i in range(sori+1, len(plebaniak_nyers[plebaniai])-1):
                        plebaniak_nyers[plebaniai][i+1] = plebaniak_nyers[plebaniai][i]
                    
                    plebaniak_nyers[plebaniai][sori+1] = "Tel.: " + plebaniak_nyers[plebaniai][sori].split("Tel.:")[1].strip()
                    plebaniak_nyers[plebaniai][sori] = plebaniak_nyers[plebaniai][sori].split("Tel.:")[0].strip()

        plebaniak = []
        for rows in plebaniak_nyers:
            if "Ellátja:" in "".join(rows):
                continue
            parishioner = None
            phones = None
            websites = []
            postalCode = None
            settlement = None
            address = None
            emails = set()
            name = ".".join(rows[0].split(".")[1:]).strip().split("Római Katolikus Plébánia")[0].strip()
            for row in rows[1:]:
                addressStarts = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]
                parishionerStarts = ["Plébános", "Plébániai kormányzó"]
                for start in addressStarts:
                    try: 
                        if address != None:
                            break
                        if row.startswith(start):
                            fullAddress = row.strip()
                            if "vármegye" in fullAddress:
                                fullAddress = " ".join(fullAddress.split(" ")[:-2])
                            postalCode = fullAddress.split(" ")[0]
                            settlement = fullAddress.split(" ")[1].split(",")[0].strip()
                            address = ' '.join(fullAddress.split(" ")[2:]).strip()
                            break
                    except:
                        print(f"{link} - {row} - cím")
                        break
                for start in parishionerStarts:
                    if row.startswith(start):
                        parishionerName = []
                        for s in row.split(":")[1].strip().split(" "):
                            if len(s) > 0 and s[0].isupper():
                                parishionerName.append(s.split(",")[0].strip())
                            else:
                                break
                        parishionerName = " ".join(parishionerName)
                        parishioner = get_priest(None, parishionerName, dontFind=True)
                        break
                if row.startswith("Honlap:"):
                    for ws in row.split(":")[1:]:
                        for sws in ws.split(","):
                            if "e-mail" not in sws.lower() and "email" not in sws.lower() and not "@" in sws and "." in sws:
                                websites.append(sws.strip().replace("/",""))
                if row.startswith("E-mail:") or row.startswith("Email:"):
                    email = row.split(":")[1].strip()
                if row.startswith("Tel.:") or row.startswith("Mobil:"):
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
                plebaniak.append({
                    "name": name, # A plébánia neve
                    "parishioner": parishioner, # A plébános
                    "src": link,
                    "emails": list(emails), # E-mail
                    "phones": phone_format(phones), # Telefonszám
                    "websites": list(set(websites)), # Honlap
                    "postalCode": postalCode, # Irányítószám
                    "settlement": settlement, # Település
                    "address": address # Cím
                })
            except:
                print(f"{link} - {row}")
        return plebaniak


def EFEM(filename=None, year=None):
    deanDistricts = [
        "https://eger.egyhazmegye.hu/hitelet/eger-es-videke-esperesi-kerulet-150/eger-es-videke-esperesi-kerulet",
        "https://eger.egyhazmegye.hu/hitelet/mezokovesdi-esperesi-kerulet-153/mezokovesdi-esperesi-kerulet-121",
        "https://eger.egyhazmegye.hu/hitelet/paradi-esperesi-kerulet-154/paradi-esperesi-kerulet",
        "https://eger.egyhazmegye.hu/hitelet/fuzesabonyi-esperesi-kerulet-155/fuzesabonyi-esperesi-kerulet",
        "https://eger.egyhazmegye.hu/hitelet/hevesi-esperesi-kerulet-156/hevesi-esperesi-kerulet",
        "https://eger.egyhazmegye.hu/hitelet/gyongyosi-esperesi-kerulet-157/gyongyosi-esperesi-kerulet",
        "https://eger.egyhazmegye.hu/hitelet/patai-esperesi-kerulet-158/patai-esperesi-kerulet",
        "https://eger.egyhazmegye.hu/hitelet/miskolci-esperesi-kerulet/miskolci-esperesi-kerulet-148",
        "https://eger.egyhazmegye.hu/hitelet/onodi-esperesi-kerulet/onodi-esperesi-kerulet",
        "https://eger.egyhazmegye.hu/hitelet/ozdi-esperesi-kerulet/ozdi-esperesi-kerulet",
        "https://eger.egyhazmegye.hu/hitelet/szendroi-esperesi-kerulet/szendroi-esperesi-kerulet-1246",
        "https://eger.egyhazmegye.hu/hitelet/jaszberenyi-esperesi-kerulet/jaszberenyi-esperesi-kerulet",
        "https://eger.egyhazmegye.hu/hitelet/jaszapati-esperesi-kerulet/jaszapati-esperesi-kerulet",
        "https://eger.egyhazmegye.hu/hitelet/torokszentmiklosi-esperesi-kerulet/torokszentmiklosi-esperesi-kerulet",
        "https://eger.egyhazmegye.hu/hitelet/gonci-esperesi-kerulet/gonci-esperesi-kerulet-1215",
        "https://eger.egyhazmegye.hu/hitelet/szikszo-encsi-esperesi-kerulet/szikszo-encsi-esperesi-kerulet-1242",
        "https://eger.egyhazmegye.hu/hitelet/szerencsi-esperesi-kerulet/szerencsi-esperesi-kerulet-1222",
        "https://eger.egyhazmegye.hu/hitelet/sarospataki-esperesi-kerulet/sarospataki-esperesi-kerulet-1224",
        "https://eger.egyhazmegye.hu/hitelet/satoraljaujhely-bodrogkozi-esperesi-kerulet/satoraljaujhely-bodrogkozi-esperesi-kerulet-1227"
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
        description='Egri főegyházmegye plébániáinak adatai')
    parser.add_argument('--filename', required=False, action="store", default=None,
                        help="JSON to save. If not set, the result will be displayed on screen")

    args = parser.parse_args()

    if args.filename == None:
        print(EFEM(args.filename))
    else:
        EFEM(args.filename)
