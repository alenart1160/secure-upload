# Secure Upload

Dwie małe aplikacje Flask: **`vuln`** (celowo podatna) i **`fixed`** (poprawiona), plus 7 testów pytest.
Te same testy na `vuln` nie przechodzą (6 failed), a na `fixed` przechodzą (7 passed).

> ⚠️ `vuln` jest celowo niebezpieczna. Uruchamiaj ją tylko lokalnie (localhost / Docker). Testy używają wyłącznie sztucznych danych.

## Uruchomienie

```bash
docker compose up -d --build

docker compose run --rm tests pytest --target=vuln -v     # oczekiwane: 6 failed, 1 passed
docker compose run --rm tests pytest --target=fixed -v    # oczekiwane: 7 passed
```

Aplikacje: `vuln` – http://localhost:5001, `fixed` – http://localhost:5002 (sprawdzenie: `/health`; w PowerShellu użyj `curl.exe`).

Bez Dockera (Flask, trzy osobne terminale, w każdym po `pip install -r requirements.txt` w głównym folderze):

```bash
cd vuln  && flask --app app run -p 5001
cd fixed && flask --app app run -p 5002
pytest --target=vuln -v      # w głównym folderze
pytest --target=fixed -v
```

## Co sprawdzają testy

| Test | Atak | `vuln` | Poprawka w `fixed` |
|---|---|---|---|
| T1 | `../` w nazwie pliku | zapis poza katalogiem uploadu | odrzucenie nazwy ze ścieżką (400) |
| T2 | plik `.html` ze skryptem | skrypt działa w przeglądarce (XSS) | tylko png/jpg/pdf (415), zapis poza katalogiem publicznym |
| T3 | tekst nazwany `fake.jpg` | plik przyjęty | sprawdzenie początku pliku (415) |
| T4 | plik większy niż 2 MB | plik przyjęty | limit 2 MB (413) |
| T5 | pobranie `../../app.py` | wyciek kodu serwera | pobieranie tylko po losowym ID (400) |
| T6 | ta sama nazwa dwa razy | nadpisanie pliku | losowa nazwa (UUID), zapis w trybie `xb` |
| T+ | poprawny PNG | działa | nadal działa |

Zasada poprawki: serwer nie wierzy niczemu, co przysłał użytkownik.

## Pliki

- `vuln/app.py`, `fixed/app.py` – obie wersje aplikacji (błędy i poprawki 1–6 opisane komentarzami)
- `tests/` – testy pytest, flaga `--target=vuln|fixed`
- `docker-compose.yml`, `Dockerfile`, `requirements.txt` – uruchomienie i zależności

## Ograniczenia

`fixed` przyjmuje tylko png, jpg i pdf. Sprawdzenie początku pliku nie gwarantuje bezpiecznej zawartości. Brak antywirusa, logowania użytkowników i kontroli dostępu do pobierania.
