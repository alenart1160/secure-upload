"""
Testy opisują BEZPIECZNE zachowanie ("atak ma zostać odrzucony").
  pytest --target=vuln   -> T1..T6 CZERWONE (dowód BEFORE), T+ zielony
  pytest --target=fixed  -> wszystko ZIELONE (test ponowny AFTER)
"""
import base64

import requests

PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==")


def upload(base, name, data):
    return requests.post(f"{base}/upload", files={"file": (name, data)}, timeout=10)


def download(base, name):
    return requests.get(f"{base}/download", params={"name": name}, timeout=10)


def test_T1_traversal_w_nazwie_pliku(base):
    assert upload(base, "../pwned.png", PNG).status_code >= 400


def test_T2_xss_plik_html(base):
    assert upload(base, "xss.html", b"<script>alert(1)</script>").status_code >= 400


def test_T3_tekst_udajacy_jpg(base):
    assert upload(base, "fake.jpg", b"to nie jest obraz").status_code >= 400


def test_T4_za_duzy_plik(base):
    try:
        status = upload(base, "big.png", PNG + b"0" * 3_000_000).status_code   # limit = 2 MB
    except requests.exceptions.ConnectionError:
        return                                      # serwer zerwał połączenie = też odrzucenie
    assert status >= 400


def test_T5_pobranie_pliku_spoza_katalogu(base):
    r = download(base, "../../app.py")
    assert r.status_code >= 400 and "SECRET_KEY" not in r.text


def test_T6_nadpisanie_pliku(base):
    first = upload(base, "dup.png", PNG)
    upload(base, "dup.png", PNG + b"ZMIENIONE")       # druga wysyłka tej samej nazwy
    assert download(base, first.json()["file"]).content == PNG   # pierwszy plik ma zostać nietknięty


def test_Tplus_poprawny_png_dziala(base):
    r = upload(base, "ok.png", PNG)
    assert r.status_code == 201
    assert download(base, r.json()["file"]).content == PNG
