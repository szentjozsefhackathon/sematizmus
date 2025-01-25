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
    priestOrdinationAge = {"Országos": {}}
    deaconOrdinationAge = {"Országos": {}}
    stats = {
        "Országos": {
            "ordination": {},
            "birth": {},
            "deaconBirth": {},
            "deaconOrdination": {},
            "priestBirth": {},
            "priestOrdination": {},
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
            if i["deacon"] == True:
                if "deaconBirth" not in stats[i["diocese"]]:
                    stats[i["diocese"]]["deaconBirth"] = {}
                if "deaconOrdination" not in stats[i["diocese"]]:
                    stats[i["diocese"]]["deaconOrdination"] = {}
            else:
                if "priestBirth" not in stats[i["diocese"]]:
                    stats[i["diocese"]]["priestBirth"] = {}
                if "priestOrdination" not in stats[i["diocese"]]:
                    stats[i["diocese"]]["priestOrdination"] = {}

            ordYear = int(f"{i['ordination']}".split("-")[0])
            birthYear = int(f"{i['birth']}".split("-")[0])
            oa = ordYear - birthYear

            if ordYear not in ordinationAge["Országos"]:
                ordinationAge["Országos"][ordYear] = []
                
            ordinationAge["Országos"][ordYear].append(oa)
            if i["diocese"] not in ordinationAge:
                ordinationAge[i["diocese"]] = {}
            if ordYear not in ordinationAge[i["diocese"]]:
                ordinationAge[i["diocese"]][ordYear] = []
            ordinationAge[i["diocese"]][ordYear].append(oa)

            if i["deacon"] == True:
                if ordYear not in deaconOrdinationAge["Országos"]:
                    deaconOrdinationAge["Országos"][ordYear] = []
                deaconOrdinationAge["Országos"][ordYear].append(oa)
                if i["diocese"] not in deaconOrdinationAge:
                    deaconOrdinationAge[i["diocese"]] = {}
                if ordYear not in deaconOrdinationAge[i["diocese"]]:
                    deaconOrdinationAge[i["diocese"]][ordYear] = []
                deaconOrdinationAge[i["diocese"]][ordYear].append(oa)
            else:
                if ordYear not in priestOrdinationAge["Országos"]:
                    priestOrdinationAge["Országos"][ordYear] = []
                priestOrdinationAge["Országos"][ordYear].append(oa)
                if i["diocese"] not in priestOrdinationAge:
                    priestOrdinationAge[i["diocese"]] = {}
                if ordYear not in priestOrdinationAge[i["diocese"]]:
                    priestOrdinationAge[i["diocese"]][ordYear] = []
                priestOrdinationAge[i["diocese"]][ordYear].append(oa)

            stats[i["diocese"]]["ordination"][ordYear] = stats[i["diocese"]]["ordination"].get(ordYear, 0) + 1
            stats[i["diocese"]]["birth"][birthYear] = stats[i["diocese"]]["birth"].get(birthYear, 0) + 1
            stats["Országos"]["ordination"][ordYear] = stats["Országos"]["ordination"].get(ordYear, 0) + 1
            stats["Országos"]["birth"][birthYear] = stats["Országos"]["birth"].get(birthYear, 0) + 1

            if i["deacon"] == True:
                stats[i["diocese"]]["deaconOrdination"][ordYear] = stats[i["diocese"]]["deaconOrdination"].get(ordYear, 0) + 1
                stats[i["diocese"]]["deaconBirth"][birthYear] = stats[i["diocese"]]["deaconBirth"].get(birthYear, 0) + 1
                stats["Országos"]["deaconOrdination"][ordYear] = stats["Országos"]["deaconOrdination"].get(ordYear, 0) + 1
                stats["Országos"]["deaconBirth"][birthYear] = stats["Országos"]["deaconBirth"].get(birthYear, 0) + 1
            else:
                stats[i["diocese"]]["priestOrdination"][ordYear] = stats[i["diocese"]]["priestOrdination"].get(ordYear, 0) + 1
                stats[i["diocese"]]["priestBirth"][birthYear] = stats[i["diocese"]]["priestBirth"].get(birthYear, 0) + 1
                stats["Országos"]["priestOrdination"][ordYear] = stats["Országos"]["priestOrdination"].get(ordYear, 0) + 1
                stats["Országos"]["priestBirth"][birthYear] = stats["Országos"]["priestBirth"].get(birthYear, 0) + 1
            continue
        if i["birth"] != None:
            if "birth" not in stats[i["diocese"]]:
                stats[i["diocese"]]["birth"] = {}
            
            if i["deacon"] == True:
                if "deaconBirth" not in stats[i["diocese"]]:
                    stats[i["diocese"]]["deaconBirth"] = {}
            else:
                if "priestBirth" not in stats[i["diocese"]]:
                    stats[i["diocese"]]["priestBirth"] = {}
            birthYear = int(f"{i['birth']}".split("-")[0])
            stats[i["diocese"]]["birth"][birthYear] = stats[i["diocese"]]["birth"].get(birthYear, 0) + 1
            stats["Országos"]["birth"][birthYear] = stats["Országos"]["birth"].get(birthYear, 0) + 1
            if i["deacon"] == True:
                stats[i["diocese"]]["deaconBirth"][birthYear] = stats[i["diocese"]]["deaconBirth"].get(birthYear, 0) + 1
                stats["Országos"]["deaconBirth"][birthYear] = stats["Országos"]["deaconBirth"].get(birthYear, 0) + 1
            else:
                stats[i["diocese"]]["priestBirth"][birthYear] = stats[i["diocese"]]["priestBirth"].get(birthYear, 0) + 1
                stats["Országos"]["priestBirth"][birthYear] = stats["Országos"]["priestBirth"].get(birthYear, 0) + 1
            continue
        if i["ordination"] != None:
            if "ordination" not in stats[i["diocese"]]:
                stats[i["diocese"]]["ordination"] = {}
            if i["deacon"] == True:
                if "deaconOrdination" not in stats[i["diocese"]]:
                    stats[i["diocese"]]["deaconOrdination"] = {}
            else:
                if "priestOrdination" not in stats[i["diocese"]]:
                    stats[i["diocese"]]["priestOrdination"] = {}
            ordYear = int(f"{i['ordination']}".split("-")[0])
            stats[i["diocese"]]["ordination"][ordYear] = stats[i["diocese"]]["ordination"].get(ordYear, 0) + 1
            stats["Országos"]["ordination"][ordYear] = stats["Országos"]["ordination"].get(ordYear, 0) + 1
            if i["deacon"] == True:
                stats[i["diocese"]]["deaconOrdination"][ordYear] = stats[i["diocese"]]["deaconOrdination"].get(ordYear, 0) + 1
                stats["Országos"]["deaconOrdination"][ordYear] = stats["Országos"]["deaconOrdination"].get(ordYear, 0) + 1
            else:
                stats[i["diocese"]]["priestOrdination"][ordYear] = stats[i["diocese"]]["priestOrdination"].get(ordYear, 0) + 1
                stats["Országos"]["priestOrdination"][ordYear] = stats["Országos"]["priestOrdination"].get(ordYear, 0) + 1
            continue
    
    for src in ordinationAge:
        stats[src]["ordinationAge"] = {}
        for year in ordinationAge[src]:
            
            stats[src]["ordinationAge"][year] = int(sum(ordinationAge[src][year])/len(ordinationAge[src][year]))
    for src in deaconOrdinationAge:
        stats[src]["deaconOrdinationAge"] = {}
        for year in deaconOrdinationAge[src]:
            stats[src]["deaconOrdinationAge"][year] = int(sum(deaconOrdinationAge[src][year])/len(deaconOrdinationAge[src][year]))
    for src in priestOrdinationAge:
        stats[src]["priestOrdinationAge"] = {}
        for year in priestOrdinationAge[src]:
            stats[src]["priestOrdinationAge"][year] = int(sum(priestOrdinationAge[src][year])/len(priestOrdinationAge[src][year]))
    
    #order keys in stats
    stats = dict(sorted(stats.items()))
    for i in stats:
        stats[i] = dict(sorted(stats[i].items()))
        for j in stats[i]:
            stats[i][j] = dict(sorted(stats[i][j].items()))
            for k in range(min(stats[i][j].keys()), max(stats[i][j].keys())):
                if k not in stats[i][j]:
                    stats[i][j][k] = 0
    
    return stats

def saveStats():
    stats = createStats()
    with open('stat/stats.json', 'w') as f:
        json.dump(stats, f)
    
if __name__ == "__main__":
    saveStats()
    