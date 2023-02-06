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
TIMEOUT = 60 * 60

from obspy.io.quakeml.core import Unpickler

import pickle
import json
from pathlib import Path
import requests
import json
import functools
import multiprocessing as mp
from tqdm import tqdm
import time
import random

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

def download_catalog(event_id, event_path, phase_path, raw_event_path, raw_phase_path):

    if (event_path/f'{event_id}.json').exists():
        print(f"{event_id}.json already exists")
        return 0

    try:
        detail = get_event_by_id(event_id, includesuperseded=True)
        print(f"vv Success: {event_id}")
    except Exception as e:
        print(f"xx Failed: {event_id}")
        # print(f"{e}")
        time.sleep(1)
        return -1

    # tires = 0
    # max_tires = 10
    # while tires < max_tires:
    #     try:
    #         detail = get_event_by_id(event_id, includesuperseded=True)
    #         break
    #     except Exception as e:
    #         print(f"{tires}: {e}")
    #         tires += 1
    #         time.sleep(60)

    # %%
    with open(raw_event_path / f"{event_id}.pkl", "wb") as f:
        pickle.dump(detail, f)

    # print(detail)
    # with open(raw_event_path / f"{event_id}.pkl", "rb") as f:
    #     x = pickle.load(f)
    # print(x)

    # %%
    pick_df = []

    try:
        origins_phase = detail.getProducts('phase-data', source="all")
    except Exception as e:
        print(f"xx Failed: {event_id} {e}")
        # print(f"{e}")
        time.sleep(1)
        return -1
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

    if len(pick_df) == 0:
        print(f"xx Failed to download picks: {event_id}")
        return -1

    try:
        pick_df = pd.concat(pick_df)
        pick_df.sort_values(by=["network","station","location","channel","phase_type"], inplace=True)
        pick_df.to_csv(phase_path/f'{event_id}.csv', index=False)
    except Exception as e:
        print(f"xx Failed to download picks: {event_id}")
        time.sleep(1)
        return -1

    # %%
    event_dict = {}

    for k in detail.properties:
        if k != "products":
            # print(k, detail[k])
            event_dict[k] = detail[k]


    # %%
    try:
        origins_fc = detail.getProducts('focal-mechanism')
        for origin in origins_fc:
            for k in origin.properties:
                # print(k, origin[k])
                event_dict[k] = origin[k]
    except Exception as e:
        # print(f"{e}")
        pass

    # %%
    try:
        origins_mt = detail.getProducts('moment-tensor')
        for origin in origins_mt:
            for k in origin.properties:
                # print(k, origin[k])
                event_dict[k] = origin[k]
    except Exception as e:
        # print(f"{e}")
        pass

    # %%
    # event_df = pd.DataFrame.from_dict(event_dict, orient='index').T
    # event_df.to_csv(event_path/f'{event_id}.csv', index=False)
    with open(event_path/f'{event_id}.json', 'w') as f:
        json.dump(event_dict, f, indent=2)

    # time.sleep(1)

    return 0

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
    # event_id = 'nc73201181'
    # download_catalog(event_id, phase_path=phase_path, event_path=event_path, raw_event_path=raw_event_path, raw_phase_path=raw_phase_path)

    # %%
    with open("event_id.json", "r") as f:
        tmp = json.load(f)
    event_ids = ["nc"+tmp[k] for k in tmp]
    event_ids = sorted(event_ids)[::-1]
    
    download_catalog_ = functools.partial(download_catalog, phase_path=phase_path, event_path=event_path, raw_event_path=raw_event_path, raw_phase_path=raw_phase_path)
    # download_catalog_(event_id)

    for _ in range(10):
        random.shuffle(event_ids)
        for event_id in tqdm(event_ids, mininterval=100):
            download_catalog(event_id, phase_path=phase_path, event_path=event_path, raw_event_path=raw_event_path, raw_phase_path=raw_phase_path)
        #   download_catalog_(event_id)
        #     break

    # ncpu = mp.cpu_count()
    # ncpu = 4
    # with mp.Pool(ncpu) as p:
    #     p.map(download_catalog_, event_ids)


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



