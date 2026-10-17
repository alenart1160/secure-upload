# WERSJA POPRAWIONA - zasada: serwer NIE wierzy niczemu, co przysłał użytkownik.
import os
import re
import uuid
from flask import Flask, abort, request, send_from_directory

app = Flask(__name__, static_folder=None)               # 3. brak publicznego katalogu static
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024      # 4. limit 2 MB (większy plik = błąd 413)

# 3. pliki zapisujemy POZA katalogiem aplikacji
UPLOAD_DIR = os.environ.get("UPLOAD_DIR", os.path.join(app.root_path, "..", "data"))
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 2. dozwolone rozszerzenia + "podpis" - jak musi się zaczynać prawdziwy plik tego typu
ALLOWED = {"png": b"\x89PNG", "jpg": b"\xff\xd8\xff", "pdf": b"%PDF"}


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/upload")
def upload():
    f = request.files.get("file")
    if f is None:
        abort(400)
    name = f.filename or ""
    if "/" in name or "\\" in name or ".." in name:        # 1. żadnych ścieżek w nazwie
        abort(400)
    ext = name.rsplit(".", 1)[-1].lower() if "." in name else ""
    if ext not in ALLOWED:                                  # 2. tylko dozwolone rozszerzenia
        abort(415)
    data = f.read()
    if not data.startswith(ALLOWED[ext]):                   # 2. zawartość musi pasować do rozszerzenia
        abort(415)
    file_id = uuid.uuid4().hex + "." + ext                  # 6. nazwę nadaje serwer (losowa)
    with open(os.path.join(UPLOAD_DIR, file_id), "xb") as out:   # "xb" = nigdy nie nadpisuj
        out.write(data)
    return {"file": file_id}, 201


@app.get("/download")
def download():
    name = request.args.get("name", "")
    if not re.fullmatch(r"[0-9a-f]{32}\.(png|jpg|pdf)", name):   # 5. tylko identyfikatory z naszego serwera
        abort(400)
    return send_from_directory(UPLOAD_DIR, name, as_attachment=True)
