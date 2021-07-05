# Analiza danych o autobusach z API ZTM
## Spis Treści

* [General info](#general-info)
* [Technologies](#technologies)
* [Setup](#setup)

* [Funkcjonalność](#funkcjonalność)
* [Użyte biblioteki](#biblioteki)
* [Dane](#dane)
* [Testy](#testy)

## Funkcjonalność
Biblioteka i używający je zeszyt jupiterowy szuka ciekawych informacji na temat zanych z API.
Sprawdza jaki procent autobusów przekracza prędkość, w jakich dzielnicach najwięcej.
Te konkluzje bazują na tym co wylicza biblioteka, czyli prędkość pojazdu wyliczona na podstawie poprzedniego wystąpienia danego pojazdu w danych i czasu tego.


## Użyte biblioteki
Całość jest napisana w Pythonie 3.
Użyte biblioteki to Pandas i Geopandas. Geopandas rozbudowuje funkcje Pandasa do działań przestrzennych, używając shapely,

## Dane
Dane przechowywane są w katalogu data. Są to zapisane dane z API ZTM pod adresem:
https://api.um.warszawa.pl

W katalogu dane znajduję się również mapa Warszawy z dzielnicami, która służy do sprawdzania w której dzielnicy znajduje się autobus.

## Testy
Test biblioteki znajduje się w folderze tym co sama biblioteka, czyli:
spacial_data_analysis_ztm/sda_ztm/test_spacial_data_analysis_ztm.py

Przykładowy wynik powyższego testu zrobiony w środowisku Pycharm znajduje się w folderze:
/profiler_testing/Test Results - pytest_in_test_spacial_data_analysis_ztm_py.html