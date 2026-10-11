# Analiza wibracji przejścia — logika obliczeń

Moduł jest oddzielony od wyznaczania sześciu punktów profilu urodzenia. Wartość `0` jest wynikiem wyłącznie warunków metod analizy przejścia; nie jest dodawana jako zwykły punkt matrycy urodzenia ani nie zastępuje wibracji `22` w dotychczasowym słowniku.

## Metoda 1 — Wskaźnik Dopełnienia Cyklu
1. Zsumuj cyfry pełnej daty urodzenia i zredukuj do 1–9.
2. Zsumuj cyfry pełnej daty śmierci i zredukuj do 1–9.
3. Oblicz wartość bezwzględną różnicy tych wibracji.
4. Jeśli różnica wynosi `0`, pokaż interpretację „Gmar Tikkun / czysta karta” w ramach tej symbolicznej metody.

## Metoda 2 — Wyzerowanie Roku Osobistego
1. Zsumuj cyfry dnia i miesiąca urodzenia oraz roku śmierci; zredukuj do 1–9.
2. Zsumuj cyfry dnia i miesiąca śmierci; zredukuj do 1–9.
3. Jeśli oba wyniki wynoszą `9`, metoda zwraca `0` i pokazuje interpretację „Gmar Tikkun / czysta karta”. W przeciwnym razie nie przypisuje wyniku `0`.

## Ważne korekty arytmetyczne w przykładach
- W Metodzie 1 data śmierci 24.08.2016 daje `2+4+0+8+2+0+1+6 = 23`, a `2+3 = 5`, nie 25 i 7. Data urodzenia 12.05.1970 daje 25 → 7. W konsekwencji różnica w podanym przykładzie wynosi `|7−5| = 2`, a nie 0.
- W Metodzie 2 dla daty urodzenia 12.05 i roku śmierci 2016: `1+2+0+5+2+0+1+6 = 17`, a `1+7 = 8`, nie 9. Dlatego ten przykład nie daje roku osobistego 9.

Wynik obliczany przez aplikację wynika z cyfr, nie z oczekiwanego opisu. Dla kontroli warunku 9–9 przykładowe daty 27.09.1980 i 27.09.2016 dają rok osobisty 9 oraz wibrację dnia i miesiąca śmierci 9.

Interpretacje duchowe są wyświetlane jako treść przyjętej metody symbolicznej, a nie jako weryfikowalny fakt o stanie duszy lub skutkach dla potomków.


## Walidacja i testy kodu
Funkcja nie wykonuje analizy, jeśli brakuje którejś daty albo data śmierci jest wcześniejsza niż data urodzenia. Testy automatyczne znajdują się w `tests/test_analiza_wibracji_przejscia.py`; uruchom je z katalogu projektu poleceniem `python -m unittest discover -s tests`.


## Warstwa opisowa raportu

Raport prezentuje obie metody pełnym opisem: przedstawia archetyp wibracji urodzenia i odejścia, wyjaśnia różnicę oraz opisuje wynik w języku metaforycznym. W Metodzie 2 szczególnie opisany jest układ rok osobisty 9 i wibracja dnia/miesiąca 1 jako symboliczna klamra zamknięcia i nowego początku. Niespełnienie warunku 0 nie oznacza automatycznie karmicznego długu ani obciążenia potomków.
