# Standard Event Format for DAS Data



## Folder structure: 

- /EventData/Ridgecrest
	- data folder:
		- 38443183.h5
		- ...
	- phase_picks folder:
		- 38443183.csv
		- ...
	- das_info.csv
	- catalog.csv
	- meta_info.txt

## Waveform format in the *data* folder:

For simple explanation, we use the [M6.4 Ridgecrest earthquake](https://earthquake.usgs.gov/earthquakes/eventpage/ci38443183/executive) as an example. We recommand to store raw data without preprocessing such as filtering.

- File name: 38443183.h5
	- data: nt $\times$ nch (float32, unit: microstrain rate; float32)
	- data.attrs: 
		- “event_id”: 38443183 (str)
		- “event_time”: 2019-07-04T17:33:490000+00:00 (str)
		- “begin_time”: 2019-07-04T17:33:190000+00:00 (str)
		- “end_time”: 2019-07-04T17:34:190000+00:00 (str)
		- “latitude”: 35.705 (float)
		- “longitude”: -117.504 (float)
		- “depth_km”: 10.5 (float)
		- “magnitude”: 6.4 (float)
		- “magnitude_type”: mw (str)
		- “source”: CI (str)
		- “dt_s”: 0.01 (float)
		- “dx_m”: 8 (float)
		- “unit”: microstrain rate (str)
		- “das_array”: ridgecrest (str)

## Phase pick format in the *phase_picks* folder:

Fhe file name should be the same as the hdf5 file. We recommand use comma (,) as the delimiter of the CSV file. 

- File name:  ci38443183.csv
- Headers: channel_index,phase_index,phase_time,phase_score,phase_type
- dtype: int32,int32,str,float32,str
	- e.g.:1000,3000,2019-07-04T17:33:520000+00:00,0.98,P

## *das_info.csv* format:

The das_info file has the location information of the DAS array. We recommand use comma (,) as the delimiter of the CSV file. 

- Headers: index,latitude,longitude,elevation_m
- dtype: int32,float,float,float
	- e.g.: 1,35.695,-117.494,121.1

## *catalog.csv* format:

The cataloa.csv file lists the attrs information of h5 files, which makes it easy to select proper training data. We recommand use comma (,) as the delimiter of the CSV file. 

- Headers: event_id,event_time, latitude, longitude,depth_km,magnitude,magnitude_type,source
- dtype: str,str,float,float,float,float,str,str
	- e.g.:38443183,2019-07-04T17:33:490000+00:00,35.705,-117.504,10.5,6.4,mw,CI

## *meta_info.txt* format

This file contains other useful information about the dataset

e.g.:

Author: Weiqiang Zhu

Earthquake number: 145483

Time range: 2019-06-01T00:00:00.000000+00:00 - 2020-06-01T00:00:00.000000+00:00

Spatial range: 2 degree from (-117.504, 35.705)

Magnitude range: 0.0-8.0

Catalog source: SCEDC

