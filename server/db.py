import socket
import struct
import json
import threading
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "db.json")

def load_db():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump({"Developer":{}, "User": {}, "Game":{}, "Room": {}}, f, indent=2)
    with open(DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_db(db):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=2)


def create(coll, key, value):
    db = load_db()
    if key in db[coll]:
        return {"status":"ERR","msg":f"{coll} already exists."}
    db[coll][key] = value
    save_db(db)
    return {"status":"OK","msg":"created"}

def read(coll, key):
    db = load_db()
    if key not in db[coll]:
        return {"status":"ERR","msg":f"{coll} not found."}
    result = db[coll][key]
    return {"status":"OK","msg":result}


def save(coll, key, value):
    db = load_db()
    if key in db[coll]:
        db[coll][key] = value
    save_db(db)
    return {"status":"OK","msg":"saved"}

def query(coll, key, value):
    db = load_db()
    result = []
    for name, info in db[coll].items():
        if info.get(key) == value:
            if coll == "Game":
                if info.get("valid") == 1:
                    result.append(name)
            else:
                result.append(name)
    return {"status":"OK","msg":result}

def remove(coll, key):
    db = load_db()
    if key in db[coll]:
        db[coll].pop(key)
    save_db(db)
    return {"status":"OK","msg":"removed"}