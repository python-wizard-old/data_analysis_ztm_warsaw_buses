import pandas as pd
import os

import geopandas as gpd
from shapely.geometry import Point

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

    # remove duplicates

    df = df.drop_duplicates()
    df['Time'] = pd.to_datetime(df['Time'])
    print('FInished importing files')
    return df


def covert_long_lat_into_geodataframe(df, crs='EPSG:4326'):
    geometry = [Point(xy) for xy in zip(df['Lon'], df['Lat'])]
    gdf = gpd.GeoDataFrame(df, geometry=geometry, crs=crs)  # “EPSG:4326”

    return gdf

def sort_vehicle_number_time(gdf):
    gdf = gdf.sort_values(['VehicleNumber', 'Time'], ascending=[True, True])
    return gdf

def remove_duplicates(gdf):
    gdf = gdf.drop_duplicates(subset=['VehicleNumber', 'Time'], keep='last')
    return gdf

def remove_vehicles_one_occurence(gdf):
    gdf = gdf[gdf.duplicated('VehicleNumber', keep=False)]
    return gdf



def calculate_distance_timedelta(gdf):

    ## to remove after testing
    set_vehicle_number = set(gdf["VehicleNumber"])
    to_check_list = []
    for n in set_vehicle_number:
        if len(gdf[gdf["VehicleNumber"] == n]) > 5:
            to_check_list.append(n)

    vehicles = to_check_list[:10]

    gdf_ = gpd.GeoDataFrame()
    for vehicle_num in to_check_list:
        print(vehicle_num, end=", ")
        # .loc[row_indexer, col_indexer] = value
        gdf.loc[gdf['VehicleNumber'] == vehicle_num, 'distance'] = gdf[gdf['VehicleNumber'] == vehicle_num].distance(gdf[gdf['VehicleNumber'] == vehicle_num].shift())
        gdf.loc[gdf['VehicleNumber'] == vehicle_num, 'TimeDelta'] = \
            gdf.loc[gdf['VehicleNumber'] == vehicle_num, 'Time'] - \
            gdf.loc[gdf['VehicleNumber'] == vehicle_num, 'Time'].shift()

        # vehicle['TimeDelta'] = vehicle['Time'] - vehicle['Time'].shift()

    return gdf

    #     vehicle = gdf[gdf['VehicleNumber'] == vehicle_num]
    #     vehicle['distance'] = vehicle.distance(vehicle.shift())
    # #     y = s - s.shift()
    #     vehicle['TimeDelta'] = vehicle['Time'] - vehicle['Time'].shift()
    #     # here calculate timedeltas
    #     gdf_ = pd.concat([gdf_, vehicle])
    #
    # return gdf_


def calculate_mpers(gdf):
    gdf['seconds'] = gdf['TimeDelta'].dt.total_seconds()
    gdf['speed_m/s'] = gdf['distance'] / gdf['seconds']
    gdf['speed_km/h'] = gdf['speed_m/s'] * 3.6

    return gdf


def assign_points_to_districts(gdf, city):

    for i in city.index:
        pip = gdf.within(city.loc[i, 'geometry'])
        gdf.loc[pip, 'Districs'] = city.loc[i, 'name']

    return gdf

