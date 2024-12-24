import json

def papima(datafile):
    with open(datafile, "r") as infile:
        priests = json.load(infile)
    
    priests.sort(key=lambda x: x["name"])

    priests = list(filter(lambda x: x["deacon"]==None or x["deacon"]==False, priests))
    priests = list(filter(lambda x: x["seminarist"]==None or x["seminarist"]==False, priests))
    print(len(priests))
    with open("papima.json", "w") as outfile:
        json.dump(priests, outfile, indent=4)

if __name__ == "__main__":
    papima("data.json")