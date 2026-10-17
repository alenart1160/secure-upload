# Raport – P6 Secure Upload

Zespół: Mikołaj Calik (50465), Andrii Babii (51301), Arkadiusz Lenart (53601), Benjamin Buyukozturk (50667)
Repozytorium: [WSTAW LINK]
> Raport ma mieć 8–12 stron. Po wstawieniu zrzutów, opisów i krótkich fragmentów kodu zwykle wychodzi dokładnie tyle.

## 1. Cel i zakres
Cel: pokazać, jak niebezpieczny jest upload plików, który ufa danym od użytkownika, a następnie go naprawić i potwierdzić to testem ponownym.
W zakresie: własna aplikacja Flask (dwie wersje), endpointy `POST /upload` i `GET /download`, syntetyczne pliki testowe.
Poza zakresem: cudze systemy, prawdziwy malware, dane rzeczywiste, testy wydajnościowe.
Oświadczenie: wszystkie testy wykonano wyłącznie na własnych maszynach / w kontenerach Docker.

## 2. Środowisko
Python 3, Flask, gunicorn, pytest, Docker / docker compose, curl (wersje z `requirements.txt`).
Uruchomienie: `docker compose up -d --build`, potem komendy z README. [WSTAW: wersja Dockera i system]

## 3. Model zagrożeń (prosty)
```
 Użytkownik (NIEZAUFANY)  ──nazwa, typ, treść pliku──►  Serwer Flask  ──zapis/odczyt──►  Katalog z plikami
                                                         (granica zaufania)
```
Wszystko, co przychodzi od użytkownika (nazwa pliku, typ, treść, parametr `name`), jest niezaufane.
Zasoby do ochrony: kod i sekrety serwera, pliki innych użytkowników, miejsce na dysku, bezpieczeństwo przeglądarki użytkowników.

## 4. Macierz dozwolonych typów plików
| Typ | Rozszerzenie | Dozwolony | Warunek |
|---|---|---|---|
| PNG | `.png` | tak | plik zaczyna się od `\x89PNG` |
| JPEG | `.jpg` | tak | plik zaczyna się od `\xff\xd8\xff` |
| PDF | `.pdf` | tak | plik zaczyna się od `%PDF` |
| HTML, SVG, PHP, EXE, inne | – | **nie** | odrzucone (415) |

## 5. Wyniki testów BEFORE → AFTER
| Test | Atak | BEFORE (`vuln`) | AFTER (`fixed`) |
|---|---|---|---|
| T1 | `../` w nazwie pliku | zapis poza katalogiem (201) | 400 |
| T2 | plik HTML ze skryptem | przyjęty, skrypt uruchamia się w przeglądarce | 415 |
| T3 | tekst jako `fake.jpg` | przyjęty (201) | 415 |
| T4 | plik 3 MB | przyjęty (201) | 413 |
| T5 | `../../app.py` | wyciek kodu serwera (200) | 400 |
| T6 | ta sama nazwa dwa razy | nadpisanie pierwszego pliku | pierwszy plik nietknięty |
| T+ | poprawny PNG | działa | działa |
Wynik pytest: `vuln` 6 failed / 1 passed → `fixed` 7 passed. [WSTAW zrzuty ekranu: pytest BEFORE, pytest AFTER, curl T5 BEFORE/AFTER, alert XSS]

## 6. Opis poprawek (po jednym akapicie, z fragmentem kodu z `fixed/app.py`)
1. Nazwa pliku ze ścieżką jest odrzucana (T1).
2. Allowlista rozszerzeń + sprawdzenie początku pliku (T2, T3).
3. Zapis poza katalogiem publicznym, brak folderu `static` (T2).
4. Limit rozmiaru 2 MB (T4).
5. Pobieranie tylko po losowym identyfikatorze z serwera (T5).
6. Nazwy losowe (UUID) i zapis w trybie „nie nadpisuj” (T6).
[WSTAW fragmenty kodu i krótki komentarz do każdego]

## 7. Ocena ryzyka i standardy
| Test | Ryzyko | Uzasadnienie | OWASP Top 10:2025 | OWASP WSTG 4.2 |
|---|---|---|---|---|
| T5 | wysokie | każdy może odczytać kod i pliki serwera | A01 Broken Access Control | WSTG-ATHZ-01 |
| T1 | wysokie | zapis plików w dowolnym miejscu | A01 Broken Access Control | WSTG-ATHZ-01 |
| T2 | średnie | skrypt w przeglądarce ofiary, wymaga otwarcia pliku | A05 Injection | WSTG-INPV-02 |
| T3 | średnie | pozwala ukryć niebezpieczny plik pod fałszywym typem | A06 Insecure Design | WSTG-BUSL-08 |
| T6 | średnie | utrata cudzych plików | A06 Insecure Design | WSTG-BUSL-09 |
| T4 | średnie | możliwość zapchania serwera | A06 Insecure Design | WSTG-BUSL-09 |

Priorytet naprawy: T5 i T1 (najwyższy wpływ), potem T6, T4, T2, T3.
Wykorzystane standardy: Top 10:2025 (co jest ryzykiem) i WSTG 4.2 (jak to testować).
> Karta projektu ma zaznaczone też ASVS 5.0.0 i CWE/CVSS. Albo je odznaczcie, albo dopiszcie, zgodnie z uzgodnieniem z prowadzącym. Minimum to dwa źródła. Sprawdźcie identyfikatory WSTG na wstg.owasp.org i kategorie Top 10 na top10.owasp.org/2025.

## 8. Ograniczenia
Sprawdzenie początku pliku nie gwarantuje, że cała zawartość jest bezpieczna. Brak antywirusa, logowania użytkowników i kontroli, kto może pobrać dany plik. Limit rozmiaru w produkcji ustawia się też na serwerze pośredniczącym.

## 9. Wnioski
[WSTAW 3–5 zdań: czego się nauczyliście, który błąd był najgroźniejszy, co zrobilibyście dalej]

## 10. Wkład członków zespołu
[WSTAW: kto co zrobił, zgodnie z kartą projektu]
