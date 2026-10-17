# Obrona (10–12 min + 3 min pytań)

## Scenariusz demo
1. **Problem (1 min):** „Upload plików ufa temu, co wyśle użytkownik. Pokażemy 6 ataków i poprawkę.”
2. **Model (2 min):** rysunek z raportu (użytkownik → serwer → katalog), granica zaufania, tabela ryzyka.
3. **Demo BEFORE (4 min), port 5001:**
   - wyciek kodu przez `name=../../app.py` (T5),
   - wgranie `xss.html` i otwarcie w przeglądarce, widać alert (T2),
   - `pytest --target=vuln -v`: 6 czerwonych.
4. **Poprawka + retest (2 min), port 5002:** te same komendy dają odmowę (400/415), `pytest --target=fixed -v`: 7 zielonych, pokazać 2–3 miejsca w `fixed/app.py`.
5. **Wnioski (1 min):** zasada „serwer nie wierzy użytkownikowi”, ograniczenia z raportu.

## Pytania, które mogą paść
**Co to jest path traversal?** Użytkownik wpisuje `../` w nazwie albo ścieżce i wychodzi poza katalog, w którym aplikacja chciała go trzymać.

**Dlaczego nie ufamy nazwie i typowi pliku?** Wysyła je użytkownik, więc może wpisać cokolwiek. Dlatego sprawdzamy rozszerzenie z listy dozwolonych i początek pliku.

**Po co losowa nazwa pliku?** Znika problem ze ścieżkami w nazwie i z nadpisywaniem. Użytkownik nie decyduje, jak plik się nazywa.

**Po co zapis poza katalogiem publicznym?** Nawet gdyby coś niebezpiecznego przeszło, nie da się tego otworzyć wprost przez adres URL.

**Co to jest XSS?** Cudzy skrypt wykonuje się w przeglądarce użytkownika, bo serwer podał go jako stronę. U nas zabezpiecza to zakaz plików HTML.

**Skąd wiecie, że poprawka działa?** Te same testy, które były czerwone, są zielone. Test T+ pokazuje, że poprawny plik nadal przechodzi.

**Co ta poprawka NIE załatwia?** Nie sprawdza całej zawartości pliku, nie ma antywirusa ani logowania użytkowników. Opisane w ograniczeniach raportu.

**Jakie standardy wykorzystaliście?** Top 10:2025 mówi, co jest ryzykiem (A01, A05, A06), a WSTG 4.2 mówi, jak to przetestować.
