import requests
import json

def download_priests():
    url = "https://szentjozsefhackathon.github.io/sematizmus/data.json"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            with open("./plebania/priests.json", "w") as f:
                json.dump(response.json(), f, indent=4, ensure_ascii=False)
            print("Priests data downloaded successfully.")
        else:
            print(f"Failed to download priests data. Status code: {response.status_code}")
    except Exception as e:
        print(f"An error occurred while downloading priests data: {e}")