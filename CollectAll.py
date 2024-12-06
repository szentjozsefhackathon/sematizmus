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

import json
import argparse
import numpy

def priestList(year, filename=None): 
    _dioceses = {
        "Esztergom-Budapesti főegyházmegye": EBFEM(year=year),
        "Győri egyházmegye": GYEM(year=year),
        "Székesfehérvári egyházmegye": SZFVEM(year=year),
        "Kalocsa-Kecskeméti főegyházmegye": KKFEM(year=year),
        "Pécsi egyházmegye": PEM(year=year),
        "Szeged-Csanádi egyházmegye": SZCSEM(year=year),
        "Egri főegyházmegye": EFEM(year=year),
        "Váci egyházmegye": VEM(year=year),
        "Debrecen-Nyíregyházi egyházmegye": DNYEM(year=year),
        "Veszprémi főegyházmegye": VFEM(year=year),
        "Kaposvári egyházmegye": KEM(year=year),
        "Szombathelyi egyházmegye": SZHEM(year=year),
        "Hajdúdorogi főegyházmegye": HdFEM(year=year),
        "Miskolci egyházmegye": MEM(year=year),
        "Nyíregyházi egyházmegye": NYEM(year=year),
        #"Pannonhalmi területi főapátság": ,
        "Katonai Ordinariátus": KO(year=year),
        "Jézus Társasága": SJ(year=year)
    }

    priests = []
    for diocese, data in _dioceses.items():
        print(f"{diocese}: {len(data)}")
        for priest in data:
            priests.append({
                "name": priest["name"], 
                "diocese": diocese, 
                "birth": priest.get("birth"), 
                "img": priest.get("img"),
                "src": priest.get("src"),
                "ordination": priest.get("ordination"),
                "retired": priest.get("retired"),
                "bishop": priest.get("bishop"),
                "deacon": priest.get("deacon"),
                "orderAbbreviation": priest.get("orderAbbreviation"),
                "doctor": priest.get("doctor")
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
    parser.add_argument('--year', required=False, action="store", default=2024, help="Actual year")
    args = parser.parse_args()


    if args.filename==None: print(priestList(int(args.year)))
    else: priestList(int(args.year), args.filename)

