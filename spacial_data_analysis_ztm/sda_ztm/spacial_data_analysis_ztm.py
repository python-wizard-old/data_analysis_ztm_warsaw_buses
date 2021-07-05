import pandas as pd
import os

import geopandas as gpd
import numpy as np
from shapely.geometry import Point


# imports for API savings
import time
from datetime import datetime
# to handle  data retrieval
import urllib3
from urllib3 import request# to handle certificate verification
import certifi# to manage json data
import json# for pandas dataframes
import pandas as pd# uncomment below if installation needed (not necessary in Colab)
#!pip install certifi


# function getting one request from api and saving it to file
def load_api_save_file(directory=''):
    r = http.request('GET', url)
    print(r.status)

    # decode json data into a dict object
    data = json.loads(r.data.decode('utf-8'))

    if (type(data['result']) == list):
        df = pd.json_normalize(data, 'result')
        df.head(10)

        # datetime object containing current date and time
        now = datetime.now()

        # dd/mm/YY H:M:S
        dt_string = now.strftime("%d-%m-%Y %H:%M:%S")
        print("date and time =", dt_string)

        file_name = "ztm_bus_data_"
        file_name += dt_string
        file = directory + '/' + file_name

        df.to_csv(file)

# function getting data from API and saving it to file
def get_save_bulk(url, wait_seconds, amount_requests, directory=''):
    http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
    for i in range(amount_requests):
        load_api_save_file(directory)
        time.sleep(wait_seconds)

def load_files_directory_into_df(directory='./'):

    df = pd.DataFrame(columns=['Lines', 'Lon', 'VehicleNumber', 'Time', 'Lat', 'Brigade'])

    # print directory
    print(directory)

    # iterate over files in
    # that directory
    for filename in os.listdir(directory):
        f = os.path.join(directory, filename)
        # checking if it is a file
        if os.path.isfile(f):
            # print(f)
            df_from_file = pd.read_csv(f)
            df = pd.concat([df, df_from_file], ignore_index=True)

    # removing duplicates

    df = df.drop_duplicates()

    # converting time in string to time in pandas datetime
    df['Time'] = pd.to_datetime(df['Time'])
    print('FInished importing files')
    return df


# converting longitude and latitude into geodataframe
# ztm crs='EPSG:4326'
def covert_long_lat_into_geodataframe(df, crs):
    geometry = [Point(xy) for xy in zip(df['Lon'], df['Lat'])]
    gdf = gpd.GeoDataFrame(df, geometry=geometry, crs=crs)  # “EPSG:4326”

    return gdf


# sort table by VehicleNumber and Time
def sort_vehicle_number_time(gdf):
    gdf = gdf.sort_values(['VehicleNumber', 'Time'], ascending=[True, True])
    return gdf


# removing duplicates taking into account VehicleNumber and Time (which are key)
def remove_duplicates(gdf):
    gdf = gdf.drop_duplicates(subset=['VehicleNumber', 'Time'], keep='last')
    return gdf


# removing vehicles with just one occurrence (you can't calculate anything)
def remove_vehicles_one_occurrence(gdf):
    gdf = gdf[gdf.duplicated('VehicleNumber', keep=False)]
    return gdf


# calculating distance between POINTS in the geometry column inside the GeoDataFrame and calculating timedeltas
def calculate_distance_timedelta(gdf):

    set_vehicle_number = set(gdf["VehicleNumber"])
    to_check_list = []
    for n in set_vehicle_number:
        if len(gdf[gdf["VehicleNumber"] == n]) > 1:
            to_check_list.append(n)

    # vehicles = to_check_list[:10]

    # gdf_ = gpd.GeoDataFrame()
    print('[', end="")
    i = 0
    if len(to_check_list) < 50:
        dot = 1
    else:
        dot = int(len(to_check_list)/50)
    for vehicle_num in to_check_list:
        if (i % dot) == 0:
            print('.', end="")
        i += 1
        # print(vehicle_num, end=", ")
        # .loc[row_indexer, col_indexer] = value
        gdf.loc[gdf['VehicleNumber'] == vehicle_num, 'distance'] = \
            gdf[gdf['VehicleNumber'] == vehicle_num].distance(gdf[gdf['VehicleNumber'] == vehicle_num].shift())

        gdf.loc[gdf['VehicleNumber'] == vehicle_num, 'TimeDelta'] = \
            gdf.loc[gdf['VehicleNumber'] == vehicle_num, 'Time'] - \
            gdf.loc[gdf['VehicleNumber'] == vehicle_num, 'Time'].shift()

        # vehicle['TimeDelta'] = vehicle['Time'] - vehicle['Time'].shift()

    print(']', end="")
    return gdf

# calculate meters per second nad hours per second
def calculate_mpers(gdf):
    gdf['seconds'] = gdf['TimeDelta'].dt.total_seconds()
    gdf['speed_m_s'] = gdf['distance'] / gdf['seconds']
    gdf['speed_km_h'] = gdf['speed_m_s'] * 3.6

    return gdf


# assign points to districts
def assign_points_to_districts(gdf, city):

    for i in city.index:
        pip = gdf.within(city.loc[i, 'geometry'])
        gdf.loc[pip, 'Districs'] = city.loc[i, 'name']

    return gdf


# remove vehicles with extraodinary high speed (default 150 km_h)
def remove_vehicle_extreme_speed(gdf, speed_max=150):
    set_vehicles = gdf.VehicleNumber.unique()
    remove = []
    for v in set_vehicles:
        if gdf[gdf["VehicleNumber"] == v].speed_km_h.max() > speed_max:
            remove.append(v)

    print("Removing following VehicleNumbers from the DataFrame: ", remove)

    list_indexes = np.array([], dtype='int64')
    for r in remove:
        index_names = gdf[gdf['VehicleNumber'] == r].index
        list_indexes = np.concatenate([list_indexes, index_names.values])

    gdf = gdf.drop(list_indexes)

    return gdf


# calculate percentage of vehicles that to above speed limit at least once
def return_vehicles_above_speed(gdf, speed_limit):
    vehicles_above = 0
    for v in gdf.VehicleNumber.unique():
        if gdf[gdf['VehicleNumber'] == v]['speed_km_h'].max() > speed_limit:
            vehicles_above += 1

    speeding_vehicles = (vehicles_above / len(gdf.VehicleNumber.unique())) * 100
    return speeding_vehicles


# function returning amount of speeding by district
def speeding_by_district(gdf):

    # Finding biggest values of speed_km_h with respect to District and VehicleNumber
    df_speed_vehicle_district = gdf.groupby(['District', "VehicleNumber"]).speed_km_h.max()

    # converting series from previous step back to DataFrame
    df_speed_vehicle_district = pd.DataFrame(df_speed_vehicle_district)

    # Converting District from index to column
    df_speed_vehicle_district.reset_index(inplace=True, level = ['District'])

    # Aplying mast for speed_km_h, and returning how many cases of speeding were found in each district
    df_speed_vehicle_district = df_speed_vehicle_district[df_speed_vehicle_district.speed_km_h > 50].District.value_counts()

    return df_speed_vehicle_district
