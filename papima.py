import json

def papima(datafile):
    with open(datafile, "r") as infile:
        priests = json.load(infile)
    
    priests.sort(key=lambda x: x["name"])
    priests = list({v['src']:v for v in priests}.values())


    priests = list(filter(lambda x:( "deacon" in x and x["deacon"] != True) or (not "deacon" in x), priests))

    with open("papima.json", "w") as outfile:
        json.dump(priests, outfile, indent=4)

if __name__ == "__main__":
    papima("data.json")