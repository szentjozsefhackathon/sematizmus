import json
import csv

def csvgenerator():
    with open("data.json") as infile:
        data = json.load(infile)
        maxEmail = max([len(p["emails"]) for p in data])
        maxPhone = max([len(p["phones"]) for p in data])
        maxWebsite = max([len(p["websites"]) for p in data])

        with open("data.csv", "w", newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                "name", "parishioner",
                "postalCode", "settlement", "address", "diocese"
            ] + [f"email_{i+1}" for i in range(maxEmail)] + \
              [f"phone_{i+1}" for i in range(maxPhone)] + \
              [f"website_{i+1}" for i in range(maxWebsite)]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for parish in data:
                row = {
                    "name": parish["name"],
                    "parishioner": parish.get("parishioner", {}).get("name", ""),
                    "postalCode": parish.get("postalCode", ""),
                    "settlement": parish.get("settlement", ""),
                    "address": parish.get("address", ""),
                    "diocese": parish.get("diocese", "")
                }
                emails = parish.get("emails", [])
                phones = parish.get("phones", [])
                websites = parish.get("websites", [])

                for i in range(maxEmail):
                    row[f"email_{i+1}"] = emails[i] if i < len(emails) else ""
                for i in range(maxPhone):
                    row[f"phone_{i+1}"] = phones[i] if i < len(phones) else ""
                for i in range(maxWebsite):
                    row[f"website_{i+1}"] = websites[i] if i < len(websites) else ""

                writer.writerow(row)


if __name__ == "__main__":
    csvgenerator()
    print("CSV file generated successfully.")