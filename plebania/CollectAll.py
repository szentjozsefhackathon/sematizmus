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

from HdFEMScraper import HdFEM
from MEMScraper import MEM
from NYEMScraper import NYEM

from RO_TEMScraper import RO_TEM
from RO_SZEMScraper import RO_SZEM
from RO_NEMScraper import RO_NEM
from RO_GYFEMScraper import RO_GYFEM

import json
import argparse
import requests
from datetime import date


def parishList(year, filename=None, restore=False):
    old = []
    if restore:
        r = requests.get("https://szentjozsefhackathon.github.io/sematizmus/plebania/data.json")
        old = r.json()
    _dioceses = {
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
        "Temesvári egyházmegye": RO_TEM,
        "Szatmári egyházmegye": RO_SZEM,
        "Nagyváradi egyházmegye": RO_NEM,
        "Gyulafehérvári főegyházmegye": RO_GYFEM
        # "Pannonhalmi területi főapátság": ,
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

    parishes = []
    for diocese, data in _dioceses.items():
        print(f"{diocese}: {len(data)}")
        for parish in data:

            parishes.append({
            "name": parish["name"],  # A plébánia neve
            "parishioner": parish.get("parishioner", {}),
            "src": parish.get("src", ""),  # Forrás link
            "phones": parish.get("phones", []),  # Telefonszám
            "websites": parish.get("websites", []),  # Honlap
            "postalCode": parish.get("postalCode", ""),  # Irányítószám
            "settlement": parish.get("settlement", ""),  # Település
            "address": parish.get("address", ""),  # Cím
            "emails": parish.get("emails", []),
            "diocese": diocese,
            "restored": parish.get("restored", None),  # Dátum, mikor lett visszaállítva
            })

    if filename == None:
        return parishes
    else:
        with open(filename, "w") as outfile:
            outfile.write(json.dumps(parishes, default=str))

    print(len(parishes))

if __name__ == "__main__":
    parser= argparse.ArgumentParser(
                        description='Sematizmus')
    parser.add_argument('--filename', required=False, action="store", default=None,
                        help="JSON to save. If not set, the result will be displayed on screen")
    parser.add_argument('--restore', required=False, action="store_true", default=False,
                        help="Restore from the old data")
    parser.add_argument('--year', required=False,
                        action="store", default=2024, help="Actual year")
    args= parser.parse_args()


    if args.filename == None: print(parishList(int(args.year), restore=args.restore))
    else: parishList(int(args.year), args.filename, restore=args.restore)
