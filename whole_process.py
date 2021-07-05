# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.11.3
#   kernelspec:
#     display_name: nlp
#     language: python
#     name: nlp
# ---

# # Analiza danych przejazdów autobusów ZTM

# Importowanie bibliotek

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

plt.rcParams['figure.figsize'] = [16, 8]

# ### Instalowanie i importowanie własnej biblioteki

pip install ./spacial_data_analysis_ztm

import spacial_data_analysis_ztm

# +
#spacial_data_analysis_ztm.__file__
# -

# Ładowanie wcześniej ściągniętych danych zapisanych ze środka nocy 28.06.2021
# Funkcja ta również usuwa duplikaty i konwertuje czas zapisany w ciągu znaków na pandas datetime

df_night = spacial_data_analysis_ztm.load_files_directory_into_df('data/28.06.2021_night_minute')

df_night = df_night.drop(columns = ['Unnamed: 0'])

# Konwertowanie Lon i Lat (długość i szerokość geograficzna) z DataFrame na typ POINT w GeoDataFrame (rozbudowane DataFrame z biblioteki Geopandas).

# oryginalny CRS ze strony ztm crs='EPSG:4326'
ztm_crs = 'EPSG:4326'
gdf_night = spacial_data_analysis_ztm.covert_long_lat_into_geodataframe(df_night, ztm_crs)

# Sprawdzanie czy dane zostały załadowanie

gdf_night.head()

# Konwertowanie zapisu przestrzennego z CRS na projected CRS (potrzebne do obliczania odległości)

gdf_night = gdf_night.to_crs(epsg=2178)

gdf_night.crs

#
# Sortowanie GeoDataFrame ze względu na kolumny VehicleNumber i Time

gdf_night = spacial_data_analysis_ztm.sort_vehicle_number_time(gdf_night)

# Usuwanie duplikatów bazując na bazując na VehicleNumber i Time

gdf_night = spacial_data_analysis_ztm.remove_duplicates(gdf_night)


# Usuwanie tych pojazdów (vehlcle), które występują tylko jeden raz (nie da na nich nic policzyć; często jest to jakaś pozostałość, która zostaje w danych)

gdf_night = spacial_data_analysis_ztm.remove_vehicles_one_occurrence(gdf_night)

# Kalkulowanie dystansu pomiędzy punktami (POINT) w kolumnie geometry, oraz obliczanie różnic czasu na podstawie kolumny Time (TIMEDELTAS)
#
# Uwaga. Może zając kokoło minuty, im większe dane tym dłużej.

gdf_night = spacial_data_analysis_ztm.calculate_distance_timedelta(gdf_night)

len(gdf_night)

# Sprawdzanie pierwszych kilku wierszy

type(gdf_night.VehicleNumber.iloc[0])

gdf_night.columns

# Kalkulowanie metrów na sekundę - dzielenie metrów na różnicę w czasie (timedeltas)

gdf_night = spacial_data_analysis_ztm.calculate_mpers(gdf_night)

gdf_night.head()



# ## Dane z dnia
# Ładowanie wcześniej ściągniętych danych zapisanych z dnia 28.06.2021.
# Powtarzanie całego powyższego procesu dla danych z dnia (w przeciwieństwie do nocy).

df_day = spacial_data_analysis_ztm.load_files_directory_into_df('data/28.06.2021_day_minute')

# Konwertowanie Lon i Lat (długość i szerokość geograficzna) z DataFrame na typ POINT w GeoDataFrame (rozbudowane DataFrame z biblioteki Geopandas).

df_day = df_day.drop(columns = ['Unnamed: 0'])

gdf_day = spacial_data_analysis_ztm.covert_long_lat_into_geodataframe(df_day, ztm_crs)

# Sprawdzanie czy dane zostały załadowanie

gdf_day.head()

# Konwertowanie zapisu przestrzennego z CRS na projected CRS (potrzebne do obliczania odległości)

gdf_day = gdf_day.to_crs(epsg=2178)

gdf_day.crs

#
# Sortowanie GeoDataFrame ze względu na kolumny VehicleNumber i Time

gdf_day = spacial_data_analysis_ztm.sort_vehicle_number_time(gdf_day)



# Usuwanie duplikotów bazując na bazując na VehicleNumber i Time

gdf_day = spacial_data_analysis_ztm.remove_duplicates(gdf_day)


# Usuwanie tych pojazdów (vehlcle), które występują tylko jeden raz (nie da się nic policzyć; często jest to jakaś pozostałość, która zostaje w danych)

gdf_day = spacial_data_analysis_ztm.remove_vehicles_one_occurrence(gdf_day)

# Kalkulowanie dystansu pomiędzy punktami (POINT) w kolumnie geometry, oraz obliczanie różnic czasu na podstawie kolumny Time (TIMEDELTAS)

gdf_day = spacial_data_analysis_ztm.calculate_distance_timedelta(gdf_day)

len(gdf_day)

# Sprawdzanie pierwszych kilku wierszy

gdf_day.head()

# Kalkulowanie metrów na sekundę - dzielenie metrów na różnicę w czasie (timedeltas)

gdf_day = spacial_data_analysis_ztm.calculate_mpers(gdf_day)

gdf_day.head()

# ### Ładowanie mapy Warszawy z dzielnicami

# Dane ze strony:
# https://github.com/andilabs/warszawa-dzielnice-geojson/
# Ściągnięte też do data/warsaw

# +
# dane ze strony
#warsaw_file = "https://raw.githubusercontent.com/andilabs/warszawa-dzielnice-geojson/master/warszawa-dzielnice.geojson"

# dane z pliku w katalogu data/warsaw
warsaw_file = "data/warsaw/warszawa-dzielnice.geojson"
# -

warsaw = gpd.read_file(warsaw_file)

# usuwanie całej Warszawy (zostają dzielnice)
warsaw = warsaw.iloc[1:]

# Konwertowanie zapisu przestrzennego z CRS na projected CRS

projected_crs_poland = 'epsg:2178'

warsaw = warsaw.to_crs(projected_crs_poland)



# #### Usuwanie prędkości zbyt dużych które muszą wynikać z błędów w danych
#
# Widać, że pewne prędkości są kompletnie błędne, wynika to z błędu w danych z api.

# +
fix, (ax1, ax2) = plt.subplots(ncols=2) 

gdf_night['speed_km_h'].plot(ax=ax1)
gdf_day['speed_km_h'].plot(ax=ax2)
_ = plt.plot()
# -

gdf_day = spacial_data_analysis_ztm.remove_vehicle_extreme_speed(gdf_day, 100)

gdf_night = spacial_data_analysis_ztm.remove_vehicle_extreme_speed(gdf_night, 100)

# Po usunięciu tych danych rozkłady powinny wyglądać "normalnie".

# +
fix, (ax1, ax2) = plt.subplots(ncols=2) 

gdf_night['speed_km_h'].hist(ax=ax1)
gdf_day['speed_km_h'].hist(ax=ax2)

_ = plt.plot()
# -

# #### Resetowanie indeksów
#
# Z usunięciem starego indeksu

gdf_night = gdf_night.reset_index(drop=True)

gdf_day = gdf_day.reset_index(drop=True)



# #### Obliczanie na podstawie wartości POINT, do której dzielnicy należy dany punkt i dodawanie tej dzielnicy do kolumny District.

# https://medium.com/analytics-vidhya/point-in-polygon-analysis-using-python-geopandas-27ea67888bff
for i in warsaw.index:
    pip = gdf_night.within(warsaw.loc[i, 'geometry'])
    gdf_night.loc[pip, 'District'] = warsaw.loc[i, 'name']

# https://medium.com/analytics-vidhya/point-in-polygon-analysis-using-python-geopandas-27ea67888bff
for i in warsaw.index:
    pip = gdf_day.within(warsaw.loc[i, 'geometry'])
    gdf_day.loc[pip, 'District'] = warsaw.loc[i, 'name']

gdf_night

# ### Mapa Warszawy

_ = warsaw.plot()

# ##### Mapa z miejscami gdzie przekraczana jest prędkość
# czerwony noc
#
# pomarańczowy dzień

plt.rcParams['figure.figsize'] = [30, 15]
fig, ax = plt.subplots()
# ax.get_legend().remove()
warsaw.plot(ax=ax, legend=False)
gdf_night[gdf_night.speed_km_h > 50].plot(ax=ax, color='red', markersize=3, legend=False)
gdf_day[gdf_day.speed_km_h > 50].plot(ax=ax, color='orange', markersize=2, legend=False)
plt.plot(legend=False)
plt.rcParams['figure.figsize'] = [16, 8]





# ###### Porównanie najwiekszej prędkości i średniej prędkości (dla wszystkich autobusów) z dnia i tych samych wartości z nocy.

# noc
speed_max_night = gdf_night['speed_km_h'].max()
# dzień
speed_max_day = gdf_day['speed_km_h'].max()
av_speed_night = gdf_night['speed_km_h'].mean()
av_speed_day = gdf_day['speed_km_h'].mean()

plt.rcParams['figure.figsize'] = [10, 5]
plt.tight_layout()
index = ['Top Speed', 'Average Speed']
df_sp_av = pd.DataFrame({'Night': [speed_max_night, av_speed_night], 'Day': [speed_max_day, av_speed_day]}, index=index)
_ = df_sp_av.plot.bar()




# #### Procent pomiarów prędkości pojazdów powyżej 50 km/h

speeding_vehicles_night = spacial_data_analysis_ztm.return_vehicles_above_speed(gdf_night, 50)

speeding_vehicles_day = spacial_data_analysis_ztm.return_vehicles_above_speed(gdf_day, 50)

speeding_vehicles_night

speeding_vehicles_day

plt.rcParams['figure.figsize'] = [10, 5]
index = ['% \nspeeding vehicles']
plt.tight_layout()
df_sp_perc = pd.DataFrame({'Night': [speeding_vehicles_night], 'Day': [speeding_vehicles_day]}, index=index)
_ = df_sp_perc.plot.bar()



# ### Sortowanie czy sprawdzanie czy w której autobus jest dzielnicy (albo czy jest poza Warszawą)

# Znajdowanie największych wartości prędkości speed_km_h pod względem dzielnic i pojazdów.
#
# konwertowanie series z poprzedniego kroku na DataFrame.
#
# Konwersja 'District' z  indeksu na kolumnę.
#
# Aplikowanie maski na prędkość, a potem zwracanie liczby wystąpień dla poszczególnych dzielnic.
#

districts_speeding_night = spacial_data_analysis_ztm.speeding_by_district(gdf_night)
districts_speeding_day = spacial_data_analysis_ztm.speeding_by_district(gdf_day)

extra = set(districts_speeding_day.index) ^ set(districts_speeding_night.index)

if (len(districts_speeding_day.index) > len(districts_speeding_night.index)):
    for e in extra:
        districts_speeding_night[e] = 0
elif (len(districts_speeding_day.index) < len(districts_speeding_night.index)):
    for e in extra:
        districts_speeding_day[e] = 0
#         pd.concat(districts_speeding_night, {e: 0})



speeding_df = pd.DataFrame([districts_speeding_day, districts_speeding_night], index=['Day', 'Night'])

plt.tight_layout()
_ = speeding_df.plot.bar()

# W następujących dzielnicach więcej niż 5 pojazdów przekracza prędkość.
#
# Odpowiednio dla nocy i dnia.

districts_speeding_night[districts_speeding_night > 5]

districts_speeding_day[districts_speeding_day > 5]

# #### Przekroczone prędkości nałożone na mapy
#

dis = districts_speeding_night.idxmax(axis=0, skipna=True)

plt.rcParams['figure.figsize'] = [16, 8]
fig, ax = plt.subplots()
warsaw[warsaw['name'] == dis].plot(ax=ax, label=dis, legend=False)
gdf_night[(gdf_night.speed_km_h > 50) & (gdf_night.District == dis)].plot(ax=ax, color='red', markersize=8, legend=False)
_ = plt.plot(legend=False)



dis = districts_speeding_day.idxmax(axis=0, skipna=True)

plt.rcParams['figure.figsize'] = [16, 8]
fig, ax = plt.subplots()
warsaw[warsaw['name'] == dis].plot(ax=ax, label=dis, legend=False)
gdf_day[(gdf_day.speed_km_h > 50) & (gdf_day.District == dis)].plot(ax=ax, color='red', markersize=8, legend=False)
_ = plt.plot(legend=False)

# Tutaj widać, że zdecydowana większość przekroczeń prędkości była na S8, co może oznaczać, że prędkość w sensie prawnym, nie była przekroczona.


