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
    distance1 = gdf6['distance'].iloc[1] - 693.68
    distance1 = abs(distance1)
    # asercja, że dystans obliczony przez geopandas w skrypcie jest w zasiegu 20 m do dystansu wyliczonego z google maps
    assert distance1 < 20

    distance2 = gdf6['distance'].iloc[3] - 1990
    distance2 = abs(distance2)
    assert distance2 < 20

    assert gdf6.shape == (4, 10)



# Kalkulowanie metrów na sekundę - dzielenie metrów na różnicę w czasie (timedeltas)

gdf7 = gdf6.copy()
gdf7 = spacial_data_analysis_ztm.calculate_mpers(gdf7)

def test_speed():
    # Dystans gmaps 693,68 m
    # szybkość 4 min = 240s
    # 693,68m / 240 s = 2,907 m/s

    speed1_diff = gdf7['speed_m_s'].iloc[1] - 2.907
    speed1_diff = abs(speed1_diff)
    # asercja, że szybkość obliczona przez geopandas w skrypcie jest w 0,5 m/s szybkości wyliczonej z dystansu google
    # podzielonego przez ilość sekund
    assert speed1_diff < 0.5

    # Dystans gmaps 1,99 km = 1990 m
    # szybkość 9 min = 540s
    # 1990m / 540s = 3,6851 m/s

    speed2_diff = gdf7['speed_m_s'].iloc[3] - 3.6851
    speed2_diff = abs(speed2_diff)
    # asercja, że dystans obliczony przez geopandas w skrypcie jest w zasiegu 20 m do dystansu wyliczonego z google maps
    assert speed2_diff < 0.5


    assert gdf7.shape == (4, 13)

print(gdf7)


# ### Ładowanie mapy Warszawy z dzielnicami

# Dane ze strony:
# https://github.com/andilabs/warszawa-dzielnice-geojson/
# Ściągnięte też do data/warsaw

# +
# dane ze strony
warsaw_file = "https://raw.githubusercontent.com/andilabs/warszawa-dzielnice-geojson/master/warszawa-dzielnice.geojson"

# dane z pliku w katalogu data/warsaw
# warsaw_file = "data/warsaw/warszawa-dzielnice.geojson"
-

warsaw = gpd.read_file(warsaw_file)

# usuwanie całej Warszawy (zostają dzielnice)
warsaw = warsaw.iloc[1:]

# Konwertowanie zapisu przestrzennego z CRS na projected CRS

projected_crs_poland = 'epsg:2178'

warsaw = warsaw.to_crs(projected_crs_poland)

