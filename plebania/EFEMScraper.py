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
                raise Exception(f"{link} - Failed to fetch the website.")
        except:
                response = requests.get(link)
                if response.status_code == 200:
                    html_content = response.content
                else:
                    raise Exception(f"{link} - Failed to fetch the website.")

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
            parishioner = {}
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
        "https://eger.egyhazmegye.hu/hivatal/eger-es-videke-esperesi-kerulet-115/eger-es-videke-esperesi-kerulet-1237",
        "https://eger.egyhazmegye.hu/hivatal/mezokovesdi-esperesi-kerulet-116/mezokovesdi-esperesi-kerulet",
        "https://eger.egyhazmegye.hu/hivatal/paradi-esperesi-kerulet-117/paradi-esperesi-kerulet-154",
        "https://eger.egyhazmegye.hu/hivatal/fuzesabony-hevesi-esperesi-kerulet-315/fuzesabony-hevesi-esperesi-kerulet-5013",
        "https://eger.egyhazmegye.hu/hivatal/gyongyosi-esperesi-kerulet/gyongyosi-esperesi-kerulet-157",
        "https://eger.egyhazmegye.hu/hivatal/patai-esperesi-kerulet/patai-esperesi-kerulet-158",
        "https://eger.egyhazmegye.hu/hivatal/miskolci-esperesi-kerulet-180/miskolci-esperesi-kerulet-159",
        "https://eger.egyhazmegye.hu/hivatal/onodi-esperesi-kerulet-181/onodi-esperesi-kerulet-160",
        "https://eger.egyhazmegye.hu/hivatal/ozdi-esperesi-kerulet-182/ozdi-esperesi-kerulet-161",
        "https://eger.egyhazmegye.hu/hivatal/szendroi-esperesi-kerulet-183/szendroi-esperesi-kerulet",
        "https://eger.egyhazmegye.hu/hivatal/jaszberenyi-esperesi-kerulet-184/jaszberenyi-esperesi-kerulet-163",
        "https://eger.egyhazmegye.hu/hivatal/jaszapati-esperesi-kerulet-185/jaszapati-esperesi-kerulet-164",
        "https://eger.egyhazmegye.hu/hivatal/torokszentmiklosi-esperesi-kerulet-187/torokszentmiklosi-esperesi-kerulet-165",
        "https://eger.egyhazmegye.hu/hivatal/gonci-esperesi-kerulet-188/gonci-esperesi-kerulet",
        "https://eger.egyhazmegye.hu/hivatal/szikszo-encsi-esperesi-kerulet-189/szikszo-encsi-esperesi-kerulet",
        "https://eger.egyhazmegye.hu/hivatal/szerencsi-esperesi-kerulet-190/szerencsi-esperesi-kerulet",
        "https://eger.egyhazmegye.hu/hivatal/sarospataki-esperesi-kerulet-191/sarospataki-esperesi-kerulet",
        "https://eger.egyhazmegye.hu/hivatal/satoraljaujhely-bodrogkozi-esperesi-kerulet-1/satoraljaujhely-bodrogkozi-esperesi-kerulet"
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
