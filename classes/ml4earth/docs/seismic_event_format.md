# Standard Event Format for Seismic Data



## Folder structure: 

- /SeismicEventData/Ridgecrest
	- waveform.h5
	- phase_picks.csv
	- stations.json
	- catalog.csv
	- meta_info.txt

## Waveform format in the data folder:

For simple explanation, we use the [M6.4 Ridgecrest earthquake](https://earthquake.usgs.gov/earthquakes/eventpage/ci38443183/executive) as an example. We recommand to store raw data without preprocessing such as filtering.

- File name: waveform.h5
	- "38443183": (group)
	
	- "38443183".attrs:
		- "event_id": 38443183 (str)
		- "event_time": 2019-07-04T17:33:490000+00:00 (str)
		- "event_time_index"[^1]: 2518 (int)
		- "event_latitude": 35.705 (float)
		- "event_longitude": -117.504 (float)
		- "event_depth_km": 10.5 (float)
		- "event_magnitude": 6.4 (float)
		- "event_magnitude_type": Mw (str)
		- "source": CI (str)
		
	- "38443183/CI.RJOB..EH":  (dataset; shape: nt$\times$3, unit: μm/s; float32)
	
	- "38443183/CI.RJOB..EH".attrs: 
		- "network": CI (str)
		- "station": RJOB (str)
		- "location": "" (str)
		- "component": [E,N,Z] (list of str)
		- "begin_time": 2019-07-04T17:33:190000+00:00 (str)
		- "end_time": 2019-07-04T17:34:190000+00:00 (str)
		- "distance_km": 19.2 (float32)
		- "azimuth": 35.3 (float32)
		- "station_latitude": 35.705 (float)
		- "station_longitude": -117.504 (float)
		- "station_elevation_m": 10.0 (float)
		- "dt_s": 0.01 (float)
		- "unit": um/s (str)
		- "snr": [1.1,2.3,2.0] (list of float)
		- "phase_type": [P,S,…] (list of str)
		- "phase_index": [3000,3023,…] (list of int)
		- "phase_time": [2022-04-26T13:50:65.160000+00:00, … ] (list of str)
		- "event_id": [38443183,38443183,] (list of str; multiple events in a window)
		
	- "38443183/..." (next station)
	
	- ... (next group)
	
[^1]: which data point in the event origin time)

## phase_picks.csv format:

The phase_pick.csv file lists the attrs information of h5 files, which makes it easy to select training data. We recommand use comma (,) as the delimiter of the CSV file. 

- Headers: event_id,station_id,phase_index,phase_time,phase_score,phase_type
- dtype: str,str,int,str,float,str
  - e.g.:38443183,CI.RJOB..EH,3000,2019-07-04T17:33:520000+00:00,0.98,P

## stations.json format:

The stations.json file contains station location information

```json
{
	"CI.CCC..BH": {
		"longitude": -117.36453,
		"latitude": 35.52495,
		"elevation_m": 670,
		"component": ["E","N","Z"],
		"response": [627368000.0,627368000.0,627368000.0],
		"unit": "m/s"
		},
	.... (next station)
}
```

## catalog.csv format:

The catalog.csv file contains earthquake event information

- Headers: event_id,time, latitude, longitude,depth_km,magnitude,magnitude_type,source
- dtype: str,str,float,float,float,float,str,str
  - e.g.:38443183,2019-07-04T17:33:490000+00:00,35.705,-117.504,10.5,6.4,Mw,CI

## meta_info.txt format

This file contains other useful information about the dataset

e.g.:

Author: Weiqiang Zhu

Earthquake number: 145483

Time range: 2019-06-01T00:00:00.000000+00:00 - 2020-06-01T00:00:00.000000+00:00

Spatial range: 2 degree from (-117.504, 35.705)

Magnitude range: 0.0-8.0

Catalog source: NCEDC

