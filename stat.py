# open data.json
# read data
# return data

import json

def read_data():
    with open('data.json') as f:
        data = json.load(f)

    return data

def createStats(): 
    ordinationAge = {"Országos": {}}
    stats = {
        "Országos": {
            "ordination": {},
            "birth": {}
        }
    }
    data = read_data()
    for i in data:
        if i["seminarist"] == True:
            continue
        if i["diocese"] not in stats:
            stats[i["diocese"]] = {}
        if i["birth"] != None and i["ordination"]!=None:
            if "birth" not in stats[i["diocese"]]:
                stats[i["diocese"]]["birth"] = {}
            if "ordination" not in stats[i["diocese"]]:
                stats[i["diocese"]]["ordination"] = {}
            ordYear = int(f"{i["ordination"]}".split("-")[0])
            birthYear = int(f"{i["birth"]}".split("-")[0])
            oa = ordYear - birthYear

            if ordYear not in ordinationAge["Országos"]:
                ordinationAge["Országos"][ordYear] = []
                
            ordinationAge["Országos"][ordYear].append(oa)
            if i["diocese"] not in ordinationAge:
                ordinationAge[i["diocese"]] = {}
            if ordYear not in ordinationAge[i["diocese"]]:
                ordinationAge[i["diocese"]][ordYear] = []
            ordinationAge[i["diocese"]][ordYear].append(oa)

            stats[i["diocese"]]["ordination"][ordYear] = stats[i["diocese"]]["ordination"].get(ordYear, 0) + 1
            stats[i["diocese"]]["birth"][birthYear] = stats[i["diocese"]]["birth"].get(birthYear, 0) + 1
            stats["Országos"]["ordination"][ordYear] = stats["Országos"]["ordination"].get(ordYear, 0) + 1
            stats["Országos"]["birth"][birthYear] = stats["Országos"]["birth"].get(birthYear, 0) + 1
            continue
        if i["birth"] != None:
            if "birth" not in stats[i["diocese"]]:
                stats[i["diocese"]]["birth"] = {}
            birthYear = int(f"{i["birth"]}".split("-")[0])
            stats[i["diocese"]]["birth"][birthYear] = stats[i["diocese"]]["birth"].get(birthYear, 0) + 1
            stats["Országos"]["birth"][birthYear] = stats["Országos"]["birth"].get(birthYear, 0) + 1
            continue
        if i["ordination"] != None:
            if "ordination" not in stats[i["diocese"]]:
                stats[i["diocese"]]["ordination"] = {}
            ordYear = int(f"{i["ordination"]}".split("-")[0])
            stats[i["diocese"]]["ordination"][ordYear] = stats[i["diocese"]]["ordination"].get(ordYear, 0) + 1
            stats["Országos"]["ordination"][ordYear] = stats["Országos"]["ordination"].get(ordYear, 0) + 1
            continue
    
    for src in ordinationAge:
        stats[src]["ordinationAge"] = {}
        for year in ordinationAge[src]:
            
            stats[src]["ordinationAge"][year] = int(sum(ordinationAge[src][year])/len(ordinationAge[src][year]))
    
    #order keys in stats
    stats = dict(sorted(stats.items()))
    for i in stats:
        stats[i] = dict(sorted(stats[i].items()))
        for j in stats[i]:
            stats[i][j] = dict(sorted(stats[i][j].items()))
    
    return stats

def saveStats():
    stats = createStats()
    with open('stat/stats.json', 'w') as f:
        json.dump(stats, f)
    
if __name__ == "__main__":
    saveStats()
    