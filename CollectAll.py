from DNYEMScraper import DNYEM
from EBFEMScraper import EBFEM
from EFEMScraper import EFEM
from GYEMScraper import GYEM
from KEMScraper import KEM
from PEMScraper import PEM
from SZFVEMScraper import SZFVEM
from SZHEMScraper import SZHEM
from VFEMScraper import VFEM
from TPScraper import TP

from HdFEMScraper import HdFEM
from MEMScraper import MEM
from NYEMScraper import NYEM

import json
import argparse
import numpy

def priestList(year, filename): 
    _dioceses = {
        "Esztergom-Budapesti főegyházmegye": EBFEM(year=year),
        "Győri egyházmegye": GYEM(year=year),
        "Székesfehérvári egyházmegye": SZFVEM(year=year),
        # "Kalocsa-Kecskeméti főegyházmegye": ,
        "Pécsi egyházmegye": PEM(year=year),
        #"Szeged-Csanádi egyházmegye": ,
        "Egri főegyházmegye": EFEM(year=year),
        #"Váci egyházmegye":,
        "Debrecen-Nyíregyházi egyházmegye": DNYEM(year=year),
        "Veszprémi főegyházmegye": VFEM(year=year),
        "Kaposvári egyházmegye": KEM(year=year),
        "Szombathelyi egyházmegye": SZHEM(year=year),
        "Hajdúdorogi főegyházmegye": HdFEM(year=year),
        "Miskolci egyházmegye": MEM(year=year),
        "Nyíregyházi egyházmegye": NYEM(year=year),
        #"Pannonhalmi területi főapátság": ,
        "Tábori Püspökség": TP(year=year)
    }

    priests = []
    for diocese, data in _dioceses.items():
        for priest in data:
            priests.append({"name": priest["name"], "diocese": diocese, "birth": priest.get("birth"), "img": priest.get("img")})



    
    if filename == None:
        return priests
    else:
        with open(filename, "w") as outfile:
            outfile.write(json.dumps(priests))
    print(len(priests))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                        description='Sematizmus')
    parser.add_argument('--filename', required=False, action="store", default=None, help="JSON to save. If not set, the result will be displayed on screen")
    parser.add_argument('--year', required=False, action="store", default=2024, help="Actual year")
    args = parser.parse_args()


    if args.filename==None: print(priestList(int(args.year)))
    else: priestList(int(args.year), args.filename)

