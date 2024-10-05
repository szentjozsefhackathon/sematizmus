import json
import datetime

with open("lastUpdate.json", "w") as f:
    f.write(json.dumps({"lastUpdate": datetime.datetime.now()}, default=str))