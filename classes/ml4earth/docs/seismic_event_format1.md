# Standard Format for Seismic Event Data

## Folder structure: 

- /SeismicEventData/
	- waveform.h5
	- phase_picks.csv
	- stations.json
	- catalog.csv
	- meta_info.txt

## *waveform.h5* format:

For simple explanation, we use the [M6.4 Ridgecrest earthquake](https://earthquake.usgs.gov/earthquakes/eventpage/ci38443183/executive) as an example. We recommand to store raw data without preprocessing such as filtering. In the dataset we are using, we put the first P pick of all stations at 30s and cut a window size of 120s. This convection can be changed according to different seismic networks.

- File name: waveform.h5
	- "ci38443183": (group)
	- "ci38443183".attrs:
		- "event_id": ci38443183 (str)
		- "event_time": 2019-07-04T17:33:490000+00:00 (str)
		- "event_time_index"[^1]: 2518 (int)
		- "begin_time": 2019-07-04T17:33:190000+00:00 (str)
		- "end_time": 2019-07-04T17:35:190000+00:00 (str)
		- "latitude": 35.705 (float)
		- "longitude": -117.504 (float)
		- "depth_km": 10.5 (float)
		- "magnitude": 6.4 (float)
		- "magnitude_type": Mw (str)
		- "sampling_rate": 100 (int)
		- "nt": 1200 (int)
   		- "nx"[^2]: 15 (int)
		- "source": CI (str)
	- "ci38443183/CI.RJOB..EH":  (dataset; shape: 3$\times$nt, unit: μm/s; float32)
	- "ci38443183/CI.RJOB..EH".attrs: 
		- "network": CI (str)
		- "station": RJOB (str)
		- "location": "" (str)
		- "instrument": "EH" (str)
 		- "component": "ENZ" (str)
		- "latitude": 35.705 (float)
		- "longitude": -117.504 (float)
		- "elevation_m": 10.0 (float）
		- “local_depth_m”[^3]: -3.0 (float)
		- "distance_km": 19.2 (float32)
		- "takeoff_angle: 13.0 (float32)
		- "azimuth": 35.3 (float32)
		- "back_azimuth": 152.1 (float32)
		- "dt_s": 0.01 (float)
		- "unit": 1e-6 m/s (str)
		- "snr": [1.1, 2.3, 2.0] (list of float)
		- "p_phase_index": 3000 (int)
		- "s_phase_index": 3023 (int)
   		- "p_phase_score": 1.0 (float32)
		- "s_phase_score": 0.9 (float32)
   		- "p_phase_time": "2022-04-26T13:50:65.160000+00:00" (str)
   		- "s_phase_time": "2022-04-26T13:50:65.390000+00:00" (str)
   		- "p_phase_polarity": U (str)
		- "s_phase_polarity": N (str)
		- "p_phase_status": automatic (str)
		- "s_phase_status": manual (str)
		- "phase_type": [P, S, …] (list of str)
		- "phase_index"[^4]: [3000, 3023, …] (list of int)
		- "phase_score": [1.0, 0.9, …] (list of float)
		- "phase_time": [2022-04-26T13:50:65.160000+00:00, … ] (list of str)
		- "phase_polarity": [U, D, N, …][^5] (list of str)
		- "event_id": [ci38443183, ci38443183, ...] (list of str; multiple events in a window)
	- "ci38443183/..." (next station)
	- ... (next group)
	
[^1]: which data point in the event origin time
[^2]: number of stations
[^3]: the depth of borehole data to the surface
[^4]: which data point is the picked phase time
[^5]: U: upgoing; D: downgoing; N: unknown

## *phase_picks.csv* format:

The phase_pick.csv file lists the attrs information of h5 files, which makes it easy to select training data. We recommand use comma (,) as the delimiter of the CSV file. 

- Headers: event_id,station_id,phase_index,phase_time,phase_score,phase_type,phase_polarity
- dtype: str,str,int,str,float,str,str
  - e.g.:ci38443183,CI.RJOB..EH,3000,2019-07-04T17:33:520000+00:00,0.98,P,U

## *stations.json* format:

The stations.json file contains station location information

```json
{
	"CI.CCC..BH": {
		"longitude": -117.36453,
		"latitude": 35.52495,
		"elevation_m": 670,
		"local_depth_m": -3.0,
		"component": ["E","N","Z"],
		"sensitivity": [627368000.0, 627368000.0, 627368000.0],
		"unit": "m/s"
		},
	.... (next station)
}
```

## *catalog.csv* format:

The catalog.csv file contains earthquake event information

- Headers: event_id,time, latitude, longitude,depth_km,magnitude,magnitude_type,source
- dtype: str,str,float,float,float,float,str,str
  - e.g.:ci38443183,2019-07-04T17:33:490000+00:00,35.705,-117.504,10.5,6.4,Mw,CI

## *meta_info.txt* format

This file contains other useful information about the dataset

e.g.:

Earthquake number: 145483

Time range: 2019-06-01T00:00:00.000000+00:00 - 2020-06-01T00:00:00.000000+00:00

Spatial range: (min_latitude, max_latitude, min_longitude, max_longitude) = (-122 -112, 30, 40)

Magnitude range: (-1.0, 8.0)

