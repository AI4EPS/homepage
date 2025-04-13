# Standard Format for Template Matching of DAS Data

For simple explanation, we use the [M6.4 Ridgecrest earthquake](https://earthquake.usgs.gov/earthquakes/eventpage/ci38443183/executive) as an example. 

File name: template.h5

- "ci38443183": (group, format: event_id)
- "ci38443183".attrs:
	- “event_id”: ci38443183 (str)
	- “event_time”: 2019-07-04T17:33:490000+00:00 (str)
	- “latitude”: 35.705 (float)
	- “longitude”: -117.504 (float)
	- “depth_km”: 10.5 (float)
	- “magnitude”: 6.4 (float)
	- “magnitude_type”: Mw (str)
	- “source”: CI (str)
- "ci38443183/P_Z": (group, format: {phase}_{component})
	- "data": (dataset; shape: [nx, nt]; unit: μm/s; float32)
	- "data".attrs:
		- "nt": 400 (int)
		- "nx": 1250 (int)
		- "dt_s": 0.01 (float)
		- "dx_m": 8 (float)
		- "time_before_s": 2 (int)
		- "time_after_s": 2 (int)
		- "unit": microstrain/s (str)
	- "travel_time": (dataset; shape: [nx,];  float32)
	- "travel_time_index": (dataset; shape: [nx,]; int)
	- "travel_time_type": (dataset; shape: [nx,]; int)
	- "travel_time_type".attrs:
		- "0": "predicted"
		- "1": "auto_picked"
		- "2": "manual_picked"
	- "station_id": (dataset; shape: [nx,]; str)
	- "snr": (dataset, shape: nx)
- "ci38443183/S_E": (same formart for S phase)
- "ci38443183/S_H": (same formart for S phase)