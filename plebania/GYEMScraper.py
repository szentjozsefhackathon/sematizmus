import requests
from tqdm import tqdm
import json
import argparse
from getPriest import get_priest

honapok = {
    "január": 1,
    "február": 2,
    "március": 3,
    "április": 4,
    "május": 5,
    "június": 6,
    "július": 7,
    "augusztus": 8,
    "szeptember": 9,
    "október": 10,
    "november": 11,
    "december": 12,
    "01": 1,
    "02": 2,
    "03": 3,
    "04": 4,
    "05": 5,
    "06": 6,
    "07": 7,
    "08": 8,
    "09": 9,
    "10": 10,
    "11": 11,
    "12": 12
}

def GYEM(filename=None, year=None):

    url = 'https://gyor.egyhazmegye.hu/api/church?limit=279&offset=0'
    response = requests.get(url, verify=False)
    if response.status_code == 200:
        json_content = json.loads(response.content)
    else:
        print(f"{url} - Failed to fetch the website.")
    
    url = f'https://gyor.egyhazmegye.hu/api/church?limit={json_content["totalElements"]}&offset=0' #Ezzel lesz időtálló
    response = requests.get(url, verify=False)
    if response.status_code == 200:
        json_content = json.loads(response.content)
    else:
        print(f"{url} - Failed to fetch the website.")
    plebanialista = []


    for plebania_talalat in tqdm(json_content["items"]):

        response = requests.get(f'https://gyor.egyhazmegye.hu/api/church/{plebania_talalat["id"]}', verify=False)
        if response.status_code == 200:
            plebania = json.loads(response.content)
        else:
            print(f"https://gyor.egyhazmegye.hu/api/church/{plebania_talalat['id']} - Failed to fetch the website.")
            continue

        if plebania["parentChurch"] != None:
            continue
        if plebania["type"] != "PLEBANIA":
            continue
        if plebania["name"].strip() == "teszt":
            continue

        parishioner = {}
        
        for priest in plebania["priests"]:
            if priest["post"] == "PLEBANOS" or priest["post"]=="PLEBANIAI_KORMANYZO":
                parishioner = get_priest(f"https://gyor.egyhazmegye.hu/#/egyhazmegyenk/papok/{priest['id']}", priest["name"].strip())
                break

        plebanialista.append({
            "name": plebania["name"].strip(),
            "src": f"https://gyor.egyhazmegye.hu/#/egyhazmegyenk/plebaniak/{plebania['id']}",
            "emails": [plebania["email"].strip()] if plebania["email"] != None and plebania["email"] != "" else [],
            "phones": [f"0036{telefon.strip() if not telefon.strip().startswith('06') else telefon.strip()[2:]}" for telefon in plebania['phone'].strip().replace('/', '').replace('-','').replace("+36", "").replace(",",";").replace(" ","").split(";")] if plebania["phone"] != None and plebania["phone"] != "" else [],
            "websites": [plebania["web"].strip()] if plebania["web"] != None and plebania["web"] != "" else [],
            "postalCode": f"{plebania['zip']}",
            "settlement": plebania["city"]["name"].strip() if plebania["city"] != None and plebania["city"]["name"] != None else "",
            "address": plebania["address"].strip() if plebania["address"] != None else "",
            "parishioner": parishioner
        })

    if filename == None:
        return plebanialista
    else:
        with open(filename, "w") as outfile:
            outfile.write(json.dumps(plebanialista,  default=str))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Győri egyházmegye plébániáinak adatai')
    parser.add_argument('--filename', required=False, action="store", default=None,
                        help="JSON to save. If not set, the result will be displayed on screen")

    args = parser.parse_args()

    if args.filename == None:
        print(GYEM(args.filename))
    else:
        GYEM(args.filename)
