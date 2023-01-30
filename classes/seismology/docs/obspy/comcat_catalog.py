# %%
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from datetime import datetime

from libcomcat.dataframes import get_phase_dataframe, get_magnitude_data_frame, get_detail_data_frame, get_history_data_frame
from libcomcat.search import get_event_by_id
from libcomcat.search import search
from libcomcat.classes import DetailEvent, SummaryEvent
from libcomcat.utils import HEADERS, TIMEOUT

from obspy.io.quakeml.core import Unpickler

import pickle
import json
from pathlib import Path
import requests
import json
import functools


def download_catalog(event_id, event_path, phase_path, raw_event_path, raw_phase_path):

    detail = get_event_by_id(event_id, includesuperseded=True)

    # %%
    with open(raw_event_path / f"{event_id}.pkl", "wb") as f:
        pickle.dump(detail, f)

    # print(detail)
    # with open(raw_event_path / f"{event_id}.pkl", "rb") as f:
    #     x = pickle.load(f)
    # print(x)

    # %%
    def parse_pick(pick, type='pick'):
        tmp_pick = {}
        if type == 'pick':
            tmp_pick["resource_id"] = pick.resource_id
            tmp_pick["network"] = pick.waveform_id.network_code
            tmp_pick["station"] = pick.waveform_id.station_code
            tmp_pick["channel"] = pick.waveform_id.channel_code
            tmp_pick["location"] = pick.waveform_id.location_code
            tmp_pick["phase_time"] = pick.time.datetime.isoformat(timespec='milliseconds')
            tmp_pick["oneset"] = pick.onset
            tmp_pick["polarity"] = pick.polarity
            tmp_pick["evaluation_mode"] = pick.evaluation_mode
            tmp_pick["evaluation_status"] = pick.evaluation_status
        elif type == 'arrival':
            tmp_pick["resource_id"] = pick.pick_id
            tmp_pick["phase_type"] = pick.phase
            tmp_pick["azimuth"] = pick.azimuth
            tmp_pick["distance"] = pick.distance
            tmp_pick["takeoff_angle"] = pick.takeoff_angle
            tmp_pick["time_residual"] = pick.time_residual
            tmp_pick["time_weight"] = pick.time_weight
            tmp_pick["time_correction"] = pick.time_correction
        else:
            raise ValueError("type must be 'pick' or 'arrival'")

        return tmp_pick

    def add_pick(pick_dict, pick):

        if pick["resource_id"] not in pick_dict:
            pick_dict[pick["resource_id"]] = pick
        else:
            pick_dict[pick["resource_id"]].update(pick)
        
        return pick_dict

    # %%
    pick_df = []

    origins_phase = detail.getProducts('phase-data', source="all")
    # for origin in origins_phase:
    #     for k in origin.properties:
    #         print(k, origin[k])

    for origin in origins_phase:
        # for k in origin.properties:
        #     print(k, origin[k])
        
        quakeurl = origin.getContentURL('quakeml.xml')

        with open(raw_phase_path / f"{event_id}_{origin.source}.pkl", "wb") as f:
            pickle.dump(origin, f)

        # print(origin)
        # with open(raw_phase_path / f"{event_id}_{origin.source}.pkl", "rb") as f:
        #     x = pickle.load(f)
        # print(x)

        try:
            response = requests.get(quakeurl, timeout=TIMEOUT, headers=HEADERS)
            data = response.text.encode('utf-8')
        except Exception:
            continue

        unpickler = Unpickler()
        try:
            catalog = unpickler.loads(data)
        except Exception as e:
            fmt = 'Could not parse QuakeML from %s due to error: %s'
            continue
        
        pick_dict = {}
        for catevent in catalog.events:
            for pick in catevent.picks:
                pick = parse_pick(pick, type="pick")
                add_pick(pick_dict, pick)
            for tmp_origin in catevent.origins:
                for pick in tmp_origin.arrivals:
                    pick = parse_pick(pick, type="arrival")
                    add_pick(pick_dict, pick)
        pick_df.append(pd.DataFrame.from_dict(pick_dict, orient='index'))

    pick_df = pd.concat(pick_df)

    # %%
    pick_df.to_csv(phase_path/f'{event_id}.csv', index=False)

    # %%
    event_dict = {}

    for k in detail.properties:
        if k != "products":
            # print(k, detail[k])
            event_dict[k] = detail[k]


    # %%
    origins_fc = detail.getProducts('focal-mechanism')
    for origin in origins_fc:
        for k in origin.properties:
            # print(k, origin[k])
            event_dict[k] = origin[k]

    # %%
    origins_mt = detail.getProducts('moment-tensor')
    for origin in origins_mt:
        for k in origin.properties:
            # print(k, origin[k])
            event_dict[k] = origin[k]

    # %%
    # event_df = pd.DataFrame.from_dict(event_dict, orient='index').T
    # event_df.to_csv(event_path/f'{event_id}.csv', index=False)
    with open(event_path/f'{event_id}.json', 'w') as f:
        json.dump(event_dict, f, indent=2)

# %%

if __name__ == "__main__":
    # %%
    phase_path = Path("phase")
    if not phase_path.exists():
        phase_path.mkdir()
    event_path = Path("event")
    if not event_path.exists():
        event_path.mkdir()
    raw_event_path = Path("raw_event")
    if not raw_event_path.exists():
        raw_event_path.mkdir()
    raw_phase_path = Path("raw_phase")
    if not raw_phase_path.exists():
        raw_phase_path.mkdir()

    # %%
    event_id = 'nc73201181'
    download_catalog_ = functools.partial(download_catalog, phase_path=phase_path, event_path=event_path, raw_event_path=raw_event_path, raw_phase_path=raw_phase_path)
    download_catalog_(event_id)


# %%
# print(get_phase_dataframe(detail))

# %%
# print(get_magnitude_data_frame(detail, catalog="us", magtype="ml"))

# %%
# print(get_history_data_frame(detail))

# %%
# summary_events = search(starttime=datetime(1994, 1, 17, 12, 30), endtime=datetime(1994, 1, 18, 12, 35),
#                    maxradiuskm=2, latitude=34.213, longitude=-118.537)
# detail_df = get_detail_data_frame(summary_events)
# print(detail_df)

# %%



