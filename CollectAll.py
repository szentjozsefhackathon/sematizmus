from CardinalScraper import Cardinal

from DNYEMScraper import DNYEM
from EBFEMScraper import EBFEM
from EFEMScraper import EFEM
from GYEMScraper import GYEM
from KEMScraper import KEM
from KKFEMScraper import KKFEM
from PEMScraper import PEM
from SZCSEMScraper import SZCSEM
from SZFVEMScraper import SZFVEM
from SZHEMScraper import SZHEM
from VEMScraper import VEM
from VFEMScraper import VFEM

from KOScraper import KO

from HdFEMScraper import HdFEM
from MEMScraper import MEM
from NYEMScraper import NYEM


from SJScraper import SJ
from SDBScraper import SDB
from SPScraper import SP

from ESZScraper import ESZ
from KSZScraper import KSZ
from GKPIScraper import GKPI
from GYSZScraper import GYSZ

import json
import argparse
import requests
from datetime import date

def priestList(year, filename=None, restore=False): 
    old = []
    if restore:
        r = requests.get("https://szentjozsefhackathon.github.io/sematizmus/data.json")
        old = r.json()
    _dioceses = {
        # "Bíborosi Kar": Cardinal(year=year),
        "Esztergom-Budapesti főegyházmegye": EBFEM,
        "Győri egyházmegye": GYEM,
        "Székesfehérvári egyházmegye": SZFVEM,
        "Kalocsa-Kecskeméti főegyházmegye": KKFEM,
        "Pécsi egyházmegye": PEM,
        "Szeged-Csanádi egyházmegye": SZCSEM,
        "Egri főegyházmegye": EFEM,
        "Váci egyházmegye": VEM,
        "Debrecen-Nyíregyházi egyházmegye": DNYEM,
        "Veszprémi főegyházmegye": VFEM,
        "Kaposvári egyházmegye": KEM,
        "Szombathelyi egyházmegye": SZHEM,
        "Hajdúdorogi főegyházmegye": HdFEM,
        "Miskolci egyházmegye": MEM,
        "Nyíregyházi egyházmegye": NYEM,
        #"Pannonhalmi területi főapátság": ,
        "Katonai Ordinariátus": KO,
        "Jézus Társasága Magyarországi Rendtartománya": SJ,
        "Szent Istvánról elnevezett Magyar Szalézi Tartomány": SDB,
        "Piarista Rend Magyar Tartománya": SP,
        "Esztergomi Szeminárium": ESZ,
        "Központi Szeminárium": KSZ,
        "Görögkatolikus Papnevelő Intézet": GKPI,
        "Győri Szeminárium": GYSZ
    }
    for key in _dioceses.keys():
        try:
            _dioceses[key] = _dioceses[key](year=year)
        except:
            _dioceses[key] = []
            for d in old:
                if d["diocese"] == key:
                    _dioceses[key].append(d)
                    if _dioceses[key][-1].get("restored", None) is None:
                        _dioceses[key][-1]["restored"] = date.today().isoformat()


    priests = []
    for diocese, data in _dioceses.items():
        print(f"{diocese}: {len(data)}")
        for priest in data:
            priests.append({
                "name": priest["name"], 
                "diocese": diocese, 
                "birth": priest.get("birth"), 
                "img": priest.get("img", "https://szentjozsefhackathon.github.io/sematizmus/ftPlaceholder.png") or "https://szentjozsefhackathon.github.io/sematizmus/ftPlaceholder.png",
                "src": priest.get("src"),
                "ordination": priest.get("ordination"),
                "retired": priest.get("retired"),
                "bishop": priest.get("bishop"),
                "deacon": priest.get("deacon"),
                "orderAbbreviation": priest.get("orderAbbreviation"),
                "doctor": priest.get("doctor"),
                "seminarist": priest.get("seminarist"),
                "dutyStation": priest.get("dutyStation"),
                "restored": priest.get("restored", None),  # Dátum, mikor lett visszaállítva
            })

    if filename == None:
        return priests
    else:
        with open(filename, "w") as outfile:
            outfile.write(json.dumps(priests, default=str))
        
    print(len(priests))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                        description='Sematizmus')
    parser.add_argument('--filename', required=False, action="store", default=None, help="JSON to save. If not set, the result will be displayed on screen")
    parser.add_argument('--restore', required=False, action="store_true", default=False, help="Restore from the old data")
    parser.add_argument('--year', required=False, action="store", default=2024, help="Actual year")
    args = parser.parse_args()


    if args.filename==None: print(priestList(int(args.year), restore=args.restore))
    else: priestList(int(args.year), args.filename, restore=args.restore)

