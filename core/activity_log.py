import os
import json
import datetime
import sys

if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))

DATA_DIR = os.path.join(BASE_DIR, "data")
LOG_PATH = os.path.join(DATA_DIR, "actividad.jsonl")


def log(user_info, action, detail=""):
    entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "usuario": user_info["username"],
        "nombre": user_info["nombre"],
        "departamento": user_info["departamento"],
        "accion": action,
        "detalle": detail,
    }
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return entry


def read_recent(limit=50):
    if not os.path.exists(LOG_PATH):
        return []
    entries = []
    with open(LOG_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                entries.append(json.loads(line))
    return entries[-limit:]
