from DNYEMScraper import DNYEM
from EBFEMScraper import EBFEM
from EFEMScraper import EFEM
from GYEMScraper import GYEM
# from KEMScraper import KEM
# from KKFEMScraper import KKFEM
from PEMScraper import PEM
from SZCSEMScraper import SZCSEM
from SZFVEMScraper import SZFVEM
# from SZHEMScraper import SZHEM
from VEMScraper import VEM
from VFEMScraper import VFEM

# from HdFEMScraper import HdFEM
# from MEMScraper import MEM
# from NYEMScraper import NYEM


import json
import argparse


def parishList(year, filename=None):
    _dioceses = {
        "Esztergom-Budapesti főegyházmegye": EBFEM(year=year),
        "Győri egyházmegye": GYEM(year=year),
        "Székesfehérvári egyházmegye": SZFVEM(year=year),
        # "Kalocsa-Kecskeméti főegyházmegye": KKFEM(year=year),
        "Pécsi egyházmegye": PEM(year=year),
        "Szeged-Csanádi egyházmegye": SZCSEM(year=year),
        "Egri főegyházmegye": EFEM(year=year),
        "Váci egyházmegye": VEM(year=year),
        "Debrecen-Nyíregyházi egyházmegye": DNYEM(year=year),
        # "Veszprémi főegyházmegye": VFEM(year=year),
        # "Kaposvári egyházmegye": KEM(year=year),
        # "Szombathelyi egyházmegye": SZHEM(year=year),
        # "Hajdúdorogi főegyházmegye": HdFEM(year=year),
        # "Miskolci egyházmegye": MEM(year=year),
        # "Nyíregyházi egyházmegye": NYEM(year=year),
        # "Pannonhalmi területi főapátság": ,
    }

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
            "diocese": diocese
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
    parser.add_argument('--year', required=False,
                        action="store", default=2024, help="Actual year")
    args= parser.parse_args()


    if args.filename == None: print(parishList(int(args.year)))
    else: parishList(int(args.year), args.filename)
