# How many public busses are speeding in Warsaw

Data analysis of Public Transport Authority (ZTM) buses in Warsaw, Poland.

English version.

For Polish version of readme click below:

[Przekraczanie prędkości przez autobusy ZTM](readme_pl.md) - 
Analiza prędkości autobusów i innych danych z API ZTM.

## Functionality
I'm trying to find interesting information (data exploration/analysis) about public service buses in Warsaw, Poland using public API. I ended up analyzing how big the percentage of buses are speeding, in what districts and at what time of day/night.

To calculate all that I wrote a small library which is located in the spacial_data_analysis_ztm library, where I calculate the speed of the bus based on change of place and location from the data from the API.

## Results and conclusions
In jupyter notebook [ztm_bus_data_analysis.ipynb](ztm_bus_data_analysis.ipynb).
For now it's in Polish, but I'm planning to translate it to English.

## Used Libraries
As a whole the project is written in Python 3. The main libraries I use are Pandas and Geopandas. Pandas is an open source data analysis and manipulation tool written for Python. Pandas offers data structures and operations for manipulating numerical tables and time series. Geopandas expands on Pandas and adds functionality when it comes to spatial data, inside using another Python ecosystem library: Shapely.

## Data
Data is stored in the data/ folder. This data is received and saved from the ZTM API on 28 June 2021. Real time live data is available at this link: https://api.um.warszawa.pl

Additionally, I'm using a map of Warsaw with division to specific districts, which is used by Geopandas to find out in which district the bus can be written.

The map in available here: 
https://raw.githubusercontent.com/andilabs/warszawa-dzielnice-geojson/master/warszawa-dzielnice.geojson


## Tests
The tests are saved in the library folder, specifically:
[./spacial_data_analysis_ztm/sda_ztm/test_spacial_data_analysis_ztm.py](./spacial_data_analysis_ztm/sda_ztm/test_spacial_data_analysis_ztm.py)

Example result of above test executed in the Pycharm environment can be found here:

[./profiler_testing/TestResults-pytest_in_test_spacial_data_analysis_ztm_py.html](./profiler_testing/TestResults-pytest_in_test_spacial_data_analysis_ztm_py.html).


## Profiler
Executed in the Pycharm environment. Results saved in folder: [./profiler_testing](./profiler_testing).