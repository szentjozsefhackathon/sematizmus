import json
import datetime

with open("lastUpdate.json", "w") as f:
    f.write(json.dumps({"lastUpdate": datetime.now()}, default=str))