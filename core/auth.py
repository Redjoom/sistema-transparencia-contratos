import json
import hashlib
import os
import sys

if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))

DATA_DIR = os.path.join(BASE_DIR, "data")
USERS_PATH = os.path.join(DATA_DIR, "users.json")

DEFAULT_USERS = {
    "admin": {
        "password_hash": hashlib.sha256("admin".encode()).hexdigest(),
        "nombre": "Administrador",
        "departamento": "Sistemas",
        "rol": "admin",
    }
}


def _ensure_users():
    if not os.path.exists(USERS_PATH):
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(USERS_PATH, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_USERS, f, indent=2, ensure_ascii=False)


def validate(username, password):
    _ensure_users()
    with open(USERS_PATH, "r", encoding="utf-8") as f:
        users = json.load(f)
    entry = users.get(username)
    if not entry:
        return None
    ph = hashlib.sha256(password.encode()).hexdigest()
    if ph != entry["password_hash"]:
        return None
    return {
        "username": username,
        "nombre": entry["nombre"],
        "departamento": entry["departamento"],
        "rol": entry.get("rol", "usuario"),
    }


def add_user(username, password, nombre, departamento, rol="usuario"):
    _ensure_users()
    with open(USERS_PATH, "r", encoding="utf-8") as f:
        users = json.load(f)
    users[username] = {
        "password_hash": hashlib.sha256(password.encode()).hexdigest(),
        "nombre": nombre,
        "departamento": departamento,
        "rol": rol,
    }
    with open(USERS_PATH, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2, ensure_ascii=False)
