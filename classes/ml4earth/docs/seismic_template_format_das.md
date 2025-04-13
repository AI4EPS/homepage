# Standard Format for Template Matching of DAS Data

For simple explanation, we use the [M6.4 Ridgecrest earthquake](https://earthquake.usgs.gov/earthquakes/eventpage/ci38443183/executive) as an example. 

File name: 38443183.h5

- "template": (group)
- "template".attrs:
	- “event_id”: 38443183 (str)
	- “event_time”: 2019-07-04T17:33:490000+00:00 (str)
	- “latitude”: 35.705 (float)
	- “longitude”: -117.504 (float)
	- “depth_km”: 10.5 (float)
	- “magnitude”: 6.4 (float)
	- “magnitude_type”: Mw (str)
	- “source”: CI (str)
- "template/P": (group)
	- "data": (dataset)
	- "data".attrs:
		- "nt": 400 (int)
		- "nx": 1250 (int)
		- "dt_s": 0.01 (float)
		- "dx_m": 8 (float)
		- “time_reference”: 2019-07-04T17:35:160000+00:00 (str)
		- "time_before": 2 (int)
		- "time_after": 2 (int)
		- "unit": microstrain/s (str)
	- "snr": signal-to-noise ratio of each channel (dataset)
	- "shift_index": shifted time index of each channel based on traveltime (dataset)
	- "travel_time": phase traveltime in seconds (dataset, float32)
	- "travel_time".attrs:
		- "type": 'phasenet' or 1D model name e.g., MAM (str)
		- "tref": the minimal UTCTime of travel times (srt)
- "template/S": (same formart for S phase) 
- "template/event": (same formart for the whole event waveform)
