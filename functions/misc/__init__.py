import datetime
import json
import os


def json_serial(obj):
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()
    if isinstance(obj, datetime.date):
        return obj.isoformat()
    if isinstance(obj, set):
        return list(obj)
    raise TypeError(f"Type {type(obj)} is not JSON-serializable")
                

def save_json(filename: str, obj, dir=None):
    # default dir for saving json
    if not dir:
        from config import JSON_DEFAULT
        dir = JSON_DEFAULT
    os.makedirs(dir, exist_ok=True)
    if not filename.endswith(".json"):
        filename = f"{filename}.json"
    with open(dir / filename, "w") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2, default=json_serial)
        

def load_json(filename: str, dir=None):
    # default dir for loading json
    if not dir:
        from config import JSON_CONFIG
        dir = JSON_CONFIG
    if not filename.endswith(".json"):
        filename = f"{filename}.json"
    with open(dir / filename, "r") as f:
        obj = json.load(f)
    return obj