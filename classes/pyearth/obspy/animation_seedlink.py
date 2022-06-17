import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
from collections import deque
import obspy
from obspy.clients.seedlink.easyseedlink import create_client

num = 1000
dt = 0.01
x = np.arange(0, num, 1) * dt
waveform = deque([np.nan] * num, maxlen=num)
st_line = st.line_chart(np.array(waveform))


def update(trace):
    print(f'Received new data:\n {trace}')
    waveform.extendleft(list(trace.data))
    st_line.line_chart(np.array(waveform))


url = "rs.local:18000/"
client = create_client(url, update)
client.select_stream('AM', 'RE569', 'EHZ')
client.run()
