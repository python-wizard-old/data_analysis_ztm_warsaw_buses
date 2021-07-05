import pytest
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import shapely
import spacial_data_analysis_ztm

plt.rcParams['figure.figsize'] = [16, 8]

# ### Instalowanie i importowanie własnej biblioteki



## Preparowanie specjanych danych do testowania
# Autobus 111, przystanki Foksal i Uniwersytet Warszawski
# autobus 117 przystanki Rondo Waszyngotna i Muzeum narodowe
# Foksal 52.23312749177165, 21.019626295412838
# Uniwersytet 52.239184825276396, 21.017303196032262
# Dystans gmaps 693,68 m

# Rondo Waszyngtona 52.237996088369876, 21.050034242560585
# Muzeum Narodowe 52.23226459286634, 21.022349324437076
# Dystans gmaps: 1,99 km

lines = ['111', '111', '117', '117', '520']
lat = [52.23312749177165, 52.239184825276396, 52.237996088369876, 52.23226459286634, 52.23312749177165]
lon = [21.019626295412838, 21.017303196032262, 21.050034242560585, 21.022349324437076, 21.019626295412838]

time = ['2021-06-27 15:00:00', '2021-06-27 15:04:00', '2021-06-27 15:00:00', '2021-06-27 15:09:00', '2021-06-27 15:00:00']

vehicleNumber = [1, 1, 2, 2, 3]
brigade = [1, 1, 2, 2, 3]

list_of_tuples = list(zip(lines, lon, vehicleNumber, time, brigade, lat))

df1 = pd.DataFrame(list_of_tuples, columns=['Lines', 'Lon', 'VehicleNumber', 'Time', 'Brigade', 'Lat'])

print("original df")
def test_df():
   assert df1.shape == (5, 6)

print(df1)
print(df1.shape)



# dublowanie df i zapis do csv
df2 = pd.concat([df1]*2)
df2.to_csv('test_data/test.csv')

print(df2)
print(df2.shape)

def test_df_duplicated():
   assert df2.shape == (10, 6)

# assert df.shape == (8, 6)


# Ładowanie wcześniej ściągniętych danych zapisanych ze środka nocy 28.06.2021
# Funkcja ta również usuwa duplikaty i konwertuje czas zapisany w ciągu znaków na pandas datetime

df3 = spacial_data_analysis_ztm.load_files_directory_into_df('test_data/')
print(df3)
print(df3.shape)

def test_df_load():
   assert df3.shape == (5, 7)


# Konwertowanie Lon i Lat (długość i szerokość geograficzna) z DataFrame na typ POINT w GeoDataFrame (rozbudowane DataFrame z biblioteki Geopandas).

# oryginalny CRS ze strony ztm crs='EPSG:4326'
ztm_crs = 'EPSG:4326'
df4 = df3.copy()
gdf = spacial_data_analysis_ztm.covert_long_lat_into_geodataframe(df4, ztm_crs)
print('After point: ')
print(gdf)
print(gdf.shape)

def test_df_after_Point():
    assert len(gdf.columns) == 8
    assert len(gdf) == 5
    geom_in = 'geometry' in list(gdf.columns)
    assert geom_in
    assert type(gdf['geometry'].iloc[0]) == shapely.geometry.point.Point


# Konwertowanie zapisu przestrzennego z CRS na projected CRS (potrzebne do obliczania odległości)
gdf = gdf.to_crs(epsg=2178)


#
# Sortowanie GeoDataFrame ze względu na kolumny VehicleNumber i Time
gdf2 = gdf.copy()

print('Test sort: ')
gdf2 = gdf2.reindex([0, 2, 4, 1, 3])
print(gdf2)
gdf2 = spacial_data_analysis_ztm.sort_vehicle_number_time(gdf)
print(gdf2)

def test_sort():
    # assert gdf2.index == (0,1,2,3,4)
    assert (list((gdf2.index == [0, 1, 2, 3, 4])) == [True,  True,  True,  True,  True]) == True

# Usuwanie duplikatów bazując na bazując na VehicleNumber i Time
print('Remove duplicates: ')
gdf3 = gdf2.copy()
gdf4 = pd.concat([gdf3]*2)
gdf4 = spacial_data_analysis_ztm.remove_duplicates(gdf4)
print(gdf4)

def test_rem_duplicates():
    assert gdf4.shape == (5, 8)

# Usuwanie tych pojazdów (vehlcle), które występują tylko jeden raz (nie da na nich nic policzyć; często jest to jakaś pozostałość, która zostaje w danych)
gdf5 = gdf.copy()
gdf5 = spacial_data_analysis_ztm.remove_vehicles_one_occurrence(gdf5)

def test_rem_one_occurence():

    assert len(gdf5) == 4

# Kalkulowanie dystansu pomiędzy punktami (POINT) w kolumnie geometry, oraz obliczanie różnic czasu na podstawie kolumny Time (TIMEDELTAS)
#
# Uwaga. Może zając kokoło minuty, im większe dane tym dłużej.

gdf6 = gdf5.copy()
gdf6 = spacial_data_analysis_ztm.calculate_distance_timedelta(gdf6)

# print(gdf['distance'].iloc[1])
print(gdf6)

def test_distance_timedeltas():
    # Dystans gmaps 693,68 m
    distance = gdf6['distance'].iloc[1] - 693.68
    distance = abs(distance)
    # asercja, że dystans obliczony przez geopandas w skrypcie jest w zasiegu 20 m do dystansu wyliczonego z google maps
    assert distance < 20

    distance = gdf6['distance'].iloc[3] - 1990
    distance = abs(distance)
    assert distance < 20

    assert gdf4.shape == (5, 8)

# Kalkulowanie metrów na sekundę - dzielenie metrów na różnicę w czasie (timedeltas)

gdf7 = gdf6.copy()
gdf7 = spacial_data_analysis_ztm.calculate_mpers(gdf7)


#
#
# # ## Dane z dnia
# # Ładowanie wcześniej ściągniętych danych zapisanych z dnia 28.06.2021.
# # Powtarzanie całego powyższego procesu dla danych z dnia (w przeciwieństwie do nocy).
#
# df_day = spacial_data_analysis_ztm.load_files_directory_into_df('data/28.06.2021_day_minute')
#
# # Konwertowanie Lon i Lat (długość i szerokość geograficzna) z DataFrame na typ POINT w GeoDataFrame (rozbudowane DataFrame z biblioteki Geopandas).
#
# gdf_day = spacial_data_analysis_ztm.covert_long_lat_into_geodataframe(df_day, ztm_crs)
#
# # Sprawdzanie czy dane zostały załadowanie
#
# gdf_day.head()
#
# # Konwertowanie zapisu przestrzennego z CRS na projected CRS (potrzebne do obliczania odległości)
#
# gdf_day = gdf_day.to_crs(epsg=2178)
#
# gdf_day.crs
#
# #
# # Sortowanie GeoDataFrame ze względu na kolumny VehicleNumber i Time
#
# gdf_day = spacial_data_analysis_ztm.sort_vehicle_number_time(gdf_day)
#
#
#
# # Usuwanie duplikotów bazując na bazując na VehicleNumber i Time
#
# gdf_day = spacial_data_analysis_ztm.remove_duplicates(gdf_day)
#
#
# # Usuwanie tych pojazdów (vehlcle), które występują tylko jeden raz (nie da się nic policzyć; często jest to jakaś pozostałość, która zostaje w danych)
#
# gdf_day = spacial_data_analysis_ztm.remove_vehicles_one_occurrence(gdf_day)
#
# # Kalkulowanie dystansu pomiędzy punktami (POINT) w kolumnie geometry, oraz obliczanie różnic czasu na podstawie kolumny Time (TIMEDELTAS)
#
# gdf_day = spacial_data_analysis_ztm.calculate_distance_timedelta(gdf_day)
#
# len(gdf_day)
#
# # Sprawdzanie pierwszych kilku wierszy
#
# gdf_day.head()
#
# # Kalkulowanie metrów na sekundę - dzielenie metrów na różnicę w czasie (timedeltas)
#
# gdf_day = spacial_data_analysis_ztm.calculate_mpers(gdf_day)
#
# gdf_day.head()
#
# # ### Ładowanie mapy Warszawy z dzielnicami
#
# # Dane ze strony:
# # https://github.com/andilabs/warszawa-dzielnice-geojson/
# # Ściągnięte też do data/warsaw
#
# # +
# # dane ze strony
# #warsaw_file = "https://raw.githubusercontent.com/andilabs/warszawa-dzielnice-geojson/master/warszawa-dzielnice.geojson"
#
# # dane z pliku w katalogu data/warsaw
# warsaw_file = "data/warsaw/warszawa-dzielnice.geojson"
# # -
#
# warsaw = gpd.read_file(warsaw_file)
#
# # usuwanie całej Warszawy (zostają dzielnice)
# warsaw = warsaw.iloc[1:]
#
# # Konwertowanie zapisu przestrzennego z CRS na projected CRS
#
# projected_crs_poland = 'epsg:2178'
#
# warsaw = warsaw.to_crs(projected_crs_poland)
#
#
#
# # #### Usuwanie prędkości zbyt dużych które muszą wynikać z błędów w danych
# #
# # Widać, że pewne prędkości są kompletnie błędne, wynika to z błędu w danych z api.
#
# # +
# fix, (ax1, ax2) = plt.subplots(ncols=2)
#
# gdf_night['speed_km_h'].plot(ax=ax1)
# gdf_day['speed_km_h'].plot(ax=ax2)
# _ = plt.plot()
# # -
#
# gdf_day = spacial_data_analysis_ztm.remove_vehicle_extreme_speed(gdf_day, 100)
#
# gdf_night = spacial_data_analysis_ztm.remove_vehicle_extreme_speed(gdf_night, 100)
#
# # Po usunięciu tych danych rozkłady powinny wyglądać "normalnie".
#
# # +
# fix, (ax1, ax2) = plt.subplots(ncols=2)
#
# gdf_night['speed_km_h'].hist(ax=ax1)
# gdf_day['speed_km_h'].hist(ax=ax2)
#
# _ = plt.plot()
# # -
#
# # #### Resetowanie indeksów
# #
# # Z usunięciem starego indeksu
#
# gdf_night = gdf_night.reset_index(drop=True)
#
# gdf_day = gdf_day.reset_index(drop=True)
#
#
#
# # #### Obliczanie na podstawie wartości POINT, do której dzielnicy należy dany punkt i dodawanie tej dzielnicy do kolumny District.
#
# # https://medium.com/analytics-vidhya/point-in-polygon-analysis-using-python-geopandas-27ea67888bff
# for i in warsaw.index:
#     pip = gdf_night.within(warsaw.loc[i, 'geometry'])
#     gdf_night.loc[pip, 'District'] = warsaw.loc[i, 'name']
#
# # https://medium.com/analytics-vidhya/point-in-polygon-analysis-using-python-geopandas-27ea67888bff
# for i in warsaw.index:
#     pip = gdf_day.within(warsaw.loc[i, 'geometry'])
#     gdf_day.loc[pip, 'District'] = warsaw.loc[i, 'name']
#
# gdf_night
#
# # ### Mapa Warszawy
#
# _ = warsaw.plot()
#
# # ##### Mapa z miejscami gdzie przekraczana jest prędkość
# # czerwony noc
# #
# # pomarańczowy dzień
#
# plt.rcParams['figure.figsize'] = [30, 15]
# fig, ax = plt.subplots()
# # ax.get_legend().remove()
# warsaw.plot(ax=ax, legend=False)
# gdf_night[gdf_night.speed_km_h > 50].plot(ax=ax, color='red', markersize=3, legend=False)
# gdf_day[gdf_day.speed_km_h > 50].plot(ax=ax, color='orange', markersize=2, legend=False)
# plt.plot(legend=False)
# plt.rcParams['figure.figsize'] = [16, 8]
#
#
#
#
#
# # ###### Porównanie najwiekszej prędkości i średniej prędkości (dla wszystkich autobusów) z dnia i tych samych wartości z nocy.
#
# # noc
# speed_max_night = gdf_night['speed_km_h'].max()
# # dzień
# speed_max_day = gdf_day['speed_km_h'].max()
# av_speed_night = gdf_night['speed_km_h'].mean()
# av_speed_day = gdf_day['speed_km_h'].mean()
#
# plt.rcParams['figure.figsize'] = [10, 5]
# plt.tight_layout()
# index = ['Top Speed', 'Average Speed']
# df_sp_av = pd.DataFrame({'Night': [speed_max_night, av_speed_night], 'Day': [speed_max_day, av_speed_day]}, index=index)
# _ = df_sp_av.plot.bar()
#
#
#
#
# # #### Procent pomiarów prędkości pojazdów powyżej 50 km/h
#
# speeding_vehicles_night = spacial_data_analysis_ztm.return_vehicles_above_speed(gdf_night, 50)
#
# speeding_vehicles_day = spacial_data_analysis_ztm.return_vehicles_above_speed(gdf_day, 50)
#
# speeding_vehicles_night
#
# speeding_vehicles_day
#
# plt.rcParams['figure.figsize'] = [10, 5]
# index = ['% \nspeeding vehicles']
# plt.tight_layout()
# df_sp_perc = pd.DataFrame({'Night': [speeding_vehicles_night], 'Day': [speeding_vehicles_day]}, index=index)
# _ = df_sp_perc.plot.bar()
#
#
#
# # ### Sortowanie czy sprawdzanie czy w której autobus jest dzielnicy (albo czy jest poza Warszawą)
#
# # Znajdowanie największych wartości prędkości speed_km_h pod względem dzielnic i pojazdów.
# #
# # konwertowanie series z poprzedniego kroku na DataFrame.
# #
# # Konwersja 'District' z  indeksu na kolumnę.
# #
# # Aplikowanie maski na prędkość, a potem zwracanie liczby wystąpień dla poszczególnych dzielnic.
# #
#
# districts_speeding_night = spacial_data_analysis_ztm.speeding_by_district(gdf_night)
# districts_speeding_day = spacial_data_analysis_ztm.speeding_by_district(gdf_day)
#
# extra = set(districts_speeding_day.index) ^ set(districts_speeding_night.index)
#
# if (len(districts_speeding_day.index) > len(districts_speeding_night.index)):
#     for e in extra:
#         districts_speeding_night[e] = 0
# elif (len(districts_speeding_day.index) < len(districts_speeding_night.index)):
#     for e in extra:
#         districts_speeding_day[e] = 0
# #         pd.concat(districts_speeding_night, {e: 0})
#
#
#
# speeding_df = pd.DataFrame([districts_speeding_day, districts_speeding_night], index=['Day', 'Night'])
#
# plt.tight_layout()
# _ = speeding_df.plot.bar()
#
# # W następujących dzielnicach więcej niż 5 pojazdów przekracza prędkość.
# #
# # Odpowiednio dla nocy i dnia.
#
# districts_speeding_night[districts_speeding_night > 5]
#
# districts_speeding_day[districts_speeding_day > 5]
#
# # #### Przekroczone prędkości nałożone na mapy
# #
#
# dis = districts_speeding_night.idxmax(axis=0, skipna=True)
#
# plt.rcParams['figure.figsize'] = [16, 8]
# fig, ax = plt.subplots()
# warsaw[warsaw['name'] == dis].plot(ax=ax, label=dis, legend=False)
# gdf_night[(gdf_night.speed_km_h > 50) & (gdf_night.District == dis)].plot(ax=ax, color='red', markersize=8, legend=False)
# _ = plt.plot(legend=False)
#
#
#
# dis = districts_speeding_day.idxmax(axis=0, skipna=True)
#
# plt.rcParams['figure.figsize'] = [16, 8]
# fig, ax = plt.subplots()
# warsaw[warsaw['name'] == dis].plot(ax=ax, label=dis, legend=False)
# gdf_day[(gdf_day.speed_km_h > 50) & (gdf_day.District == dis)].plot(ax=ax, color='red', markersize=8, legend=False)
# _ = plt.plot(legend=False)
#
# # Tutaj widać, że zdecydowana większość przekroczeń prędkości była na S8, co może oznaczać, że prędkość w sensie prawnym, nie była przekroczona.