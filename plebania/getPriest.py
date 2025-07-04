
import json

def get_priest(url, name, dontFind = False):
    priests = []
    try:
        with open("priests.json", "r") as f:
            priests = json.load(f)
        if not dontFind:
            return next(p for p in priests if p["src"] == url)
    finally:
        priest = {
                "name": name, 
                "diocese": None, 
                "birth": None, 
                "img": "https://szentjozsefhackathon.github.io/sematizmus/ftPlaceholder.png",
                "src": url,
                "ordination": None,
                "retired": None,
                "bishop": None,
                "deacon": None,
                "orderAbbreviation": None,
                "doctor": None,
                "seminarist": None,
                "dutyStation": None
        }
        return priest
    
