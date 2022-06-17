import matplotlib.pyplot as plt
import numpy as np
import scipy.signal
import streamlit as st
from collections import deque
import obspy
from obspy.clients.seedlink.easyseedlink import create_client

num = 1000
dt = 0.01
x = np.arange(0, num, 1) * dt
waveform = deque([np.nan] * num, maxlen=num)
st.set_page_config(layout="wide")
st_line = st.line_chart(np.array(waveform))
# normalize = lambda x: (x - np.min(x))/(np.max(x) - np.min(x))
# f, t, spectrogram = scipy.signal.stft(np.array(waveform))
# st_ft = st.image(normalize(spectrogram).T)

def update(trace):
    print(f'Received new data:\n {trace}')
    waveform.extendleft(list(trace.data))
    st_line.line_chart(np.array(waveform))
    # f, t, spectrogram = scipy.signal.stft(np.array(waveform))
    # st_ft.image(normalize(spectrogram).T)

def error():
    pass

url = "rs.local:18000/"
client = create_client(url, on_data=update, on_seedlink_error=error)
client.select_stream('AM', 'RE569', 'EHZ')
client.run()
