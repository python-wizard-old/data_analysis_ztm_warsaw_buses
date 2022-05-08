# Przekraczanie prędkości przez autobusy ZTM.
Analiza prędkości autobusów i innych danych z API ZTM.

## Spis Treści

* [Funkcjonalność](#funkcjonalność)
* [Wyniki i konkluzje](#wyniki_konkluzje)
* [Użyte biblioteki](#biblioteki)
* [Dane](#dane)
* [Testy](#testy)
* [Profiler](#profiler)

## Funkcjonalność
Biblioteka łącząca, już istniejące narzędzia, i używający ją zeszyt jupiterowy szuka ciekawych informacji na temat zanych z API.
Sprawdza jaki procent autobusów przekracza prędkość, w jakich dzielnicach najwięcej do tego dochodzi.
Te konkluzje bazują na tym co wylicza biblioteka, czyli prędkość pojazdu wyliczona na podstawie poprzedniego wystąpienia danego pojazdu w danych i czasu tego wystąpienia.

## Wyniki i konkluzje
W zeszycie jupiterowym [ztm_bus_data_analysis.ipynb](ztm_bus_data_analysis.ipynb).

## Użyte biblioteki
Całość jest napisana w Pythonie 3.
Użyte biblioteki to Pandas i Geopandas. Geopandas rozbudowuje funkcje Pandasa do działań przestrzennych, używając Shapely.
Oczywiście Pandas samo wykorzystuje wiele narzędzi, np używa tablic Numpy do przechowywania części danych.

## Dane
Dane przechowywane są w katalogu data. Są to zapisane dane z API ZTM w dniu 28.06.2021.
Dane w czasie rzeczywistym można pobrać pod adresem:
https://api.um.warszawa.pl

W katalogu dane znajduję się również mapa Warszawy z dzielnicami, która służy do sprawdzania w której dzielnicy znajduje się autobus.
Mapa dostępna jest na:
https://raw.githubusercontent.com/andilabs/warszawa-dzielnice-geojson/master/warszawa-dzielnice.geojson


## Testy
Test biblioteki znajduje się w folderze tym co sama biblioteka, czyli:
spacial_data_analysis_ztm/sda_ztm/test_spacial_data_analysis_ztm.py

Przykładowy wynik powyższego testu zrobiony w środowisku Pycharm znajduje się w folderze:
/profiler_testing/Test Results - pytest_in_test_spacial_data_analysis_ztm_py.html

## Profiler
Wywołany w środowisku Pycharm. Wyniki zapisane w katalogu profiler_tesitng.