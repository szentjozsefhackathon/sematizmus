import json

def deleteMultiplications(priests):
    with open("multiplications.json", "r") as infile:
        multiplications = json.load(infile)
    for multiplication in multiplications:
        if multiplication[0] in priests:
            for i in range(1, len(multiplication)):
                if multiplication[i] in priests:
                    priests.remove(multiplication[i])
    return priests

if __name__ == "__main__":
    with open("data.json", "r") as infile:
        priests = json.load(infile)
    priests = deleteMultiplications(priests)
    with open("data.json", "w") as outfile:
        json.dump(priests, outfile)