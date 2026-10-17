# WERSJA PODATNA - celowo! Tylko lokalnie / w Dockerze, nigdy w internecie.
import os
from flask import Flask, request

app = Flask(__name__)
SECRET_KEY = "demo-secret-NOT-REAL"                      # sztuczny "sekret" do pokazania wycieku

UPLOAD_DIR = os.path.join(app.root_path, "static", "uploads")   # BŁĄD 3: katalog publiczny
os.makedirs(UPLOAD_DIR, exist_ok=True)
# BŁĄD 4: brak limitu rozmiaru pliku


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/upload")
def upload():
    f = request.files["file"]
    # BŁĄD 1: nazwa od użytkownika trafia prosto do ścieżki ("../" wyprowadza poza katalog)
    # BŁĄD 2: brak sprawdzenia typu i zawartości (html, php, tekst udający jpg)
    # BŁĄD 6: ta sama nazwa = nadpisanie istniejącego pliku
    f.save(os.path.join(UPLOAD_DIR, f.filename))
    return {"file": f.filename}, 201


@app.get("/download")
def download():
    # BŁĄD 5: ścieżka z danych użytkownika, np. name=../../app.py albo name=/etc/passwd
    with open(os.path.join(UPLOAD_DIR, request.args["name"]), "rb") as fh:
        return fh.read()
