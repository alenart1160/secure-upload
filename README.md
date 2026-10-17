# P6 – Secure Upload (wersja minimalna)

Dwie małe aplikacje Flask: **`vuln`** (celowo podatna) i **`fixed`** (poprawiona), plus 7 testów.
Te same testy: na `vuln` **czerwone** (dowód BEFORE), na `fixed` **zielone** (test ponowny AFTER).

> ⚠️ `vuln` jest celowo niebezpieczna. Uruchamiać tylko lokalnie / w Dockerze.

## Uruchomienie

```bash
docker compose up -d --build

docker compose run --rm tests pytest --target=vuln -v     # oczekiwane: 6 failed, 1 passed
docker compose run --rm tests pytest --target=fixed -v    # oczekiwane: 7 passed
```

Bez Dockera (Linux/macOS/WSL):
```bash
pip install -r requirements.txt
(cd vuln  && gunicorn -b 127.0.0.1:5001 app:app) &
(cd fixed && gunicorn -b 127.0.0.1:5002 app:app) &
pytest --target=vuln -v
pytest --target=fixed -v
```

## 6 ataków (po jednym zdaniu)

| Test | Atak | Co się dzieje w `vuln` | Poprawka w `fixed` |
|---|---|---|---|
| T1 | w nazwie pliku jest `../` | plik zapisuje się **poza** katalogiem uploadu | odrzucamy nazwy ze ścieżką (400) |
| T2 | wgranie pliku `.html` ze skryptem | skrypt uruchamia się w przeglądarce (XSS) | tylko png/jpg/pdf (415) + zapis poza katalogiem publicznym |
| T3 | tekst nazwany `fake.jpg` | serwer wierzy nazwie i przyjmuje plik | sprawdzamy, czy plik naprawdę zaczyna się jak JPG (415) |
| T4 | plik większy niż 2 MB | serwer przyjmuje dowolnie duży plik | limit 2 MB (413) |
| T5 | pobranie `../../app.py` | wyciek kodu serwera (i np. `/etc/passwd`) | pobieranie tylko po losowym ID z serwera (400) |
| T6 | dwa razy ta sama nazwa | drugi plik kasuje pierwszy | serwer nadaje losową nazwę i nie nadpisuje |
| T+ | poprawny PNG | działa | **nadal działa** (poprawka nie zepsuła funkcji) |

**Jedna zasada poprawki:** serwer nie wierzy niczemu, co przysłał użytkownik. Sam nadaje nazwę, sam sprawdza typ, sam ustala limit i sam wybiera miejsce zapisu.

## Dowody do raportu (3 rzeczy)

1. **Zrzut ekranu terminala** z `pytest --target=vuln -v` (czerwone) i `pytest --target=fixed -v` (zielone).
2. **Wyciek kodu (T5)**, a potem to samo na `fixed`:
   ```bash
   curl -i -G --data-urlencode "name=../../app.py" localhost:5001/download   # vuln: 200 + kod
   curl -i -G --data-urlencode "name=../../app.py" localhost:5002/download   # fixed: 400
   ```
3. **Alert XSS (T2)**:
   ```bash
   echo '<script>alert(1)</script>' > xss.html
   curl -F "file=@xss.html" localhost:5001/upload      # vuln: 201
   # otwórz w przeglądarce: http://localhost:5001/static/uploads/xss.html  -> okienko alert, zrób zrzut ekranu
   curl -i -F "file=@xss.html" localhost:5002/upload   # fixed: 415
   ```

Dowody bez prawdziwych haseł i sekretów. Używamy tylko sztucznych danych.

## Pliki

| Plik | Po co |
|---|---|
| `vuln/app.py` | aplikacja podatna (błędy 1–6 opisane komentarzami) |
| `fixed/app.py` | aplikacja poprawiona (poprawki 1–6 opisane komentarzami) |
| `tests/test_upload.py` | 7 testów |
| `RAPORT.md` | gotowy szkielet raportu z uzupełnionymi tabelami |
| `OBRONA.md` | scenariusz demo i pytania z odpowiedziami |
