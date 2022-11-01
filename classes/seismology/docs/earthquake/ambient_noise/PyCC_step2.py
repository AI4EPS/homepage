# This script does temporal normalization, spatial whitening, and cc in frequency domain
import glob
import os
import time

import h5py
import numpy as np
import pandas as pd
from tqdm import tqdm

from func_PyCC import *

#%% parameters
path_preprocessed = "./preprocessed/"
output_CC = "./CC/"
if not os.path.exists(output_CC):
    os.mkdir(output_CC)

# starting and ending dates to compute daily stacked CC
dates = [x.strftime("%Y%m%d") for x in pd.date_range(start="6/15/2021", end="6/15/2021", freq="1D")]

# Now give the No. of channel pairs to calculate CC.
# below is an example of common-shot
nch = 1250
pair_channel1 = 500 * np.ones(nch, dtype="int")
pair_channel2 = np.arange(nch)
npair = len(pair_channel1)
#############

f1, f2 = 0.1, 10  # frequency band in spectral whitening
fs = 25  # sampling frequency
window_freq = 0  # 0 means aggresive spectral whitening, otherwise running mean
max_lag = 30  # in sec, the time lag of the output CC
npts_lag = int(max_lag * fs)
xcorr_seg = 40  # in sec, the length of the segment to compute CC, slightly larger than max_lag is good
npts_seg = int(xcorr_seg * fs)

npair_chunk = 2000  # depends on # of channels, sampling frequency, and xcorr_seg, needs to be adaptive
nchunk = int(np.ceil(npair / npair_chunk))

device = "cuda:0"  # GPU device, needs to be changed to multi

#%% temporal normalization/ spectral whitening/ CC
for idate in tqdm(dates):

    ccall = np.zeros((npair, int(max_lag * fs * 2 + 1)))

    output_file_tmp = f"{output_CC}/{idate}.npy"
    if os.path.exists(output_file_tmp):
        print(output_file_tmp)
        continue

    filelist = glob.glob(os.path.join(path_preprocessed, idate + "*h5"))
    filelist.sort()
    filelist = filelist[:1]
    if len(filelist) == 0:
        print(f"{idate}: no file")
        continue
    flag_mean = 0
    # t1 = time.time()
    for ifile in filelist:
        fid = h5py.File(ifile, "r")
        data = fid["Data"][:]
        fid.close()

        nch = data.shape[0]
        npts = data.shape[1]

        npts = npts // npts_seg * npts_seg
        if npts < npts_seg:  # or nch!=nch_end:
            continue

        data = data[:, :npts]

        nseg = int(npts / npts_seg)
        flag_mean += nseg
        # print(time.time() - t1)

        #%%
        for ichunk in range(nchunk):

            ich1 = pair_channel1[npair_chunk * ichunk : npair_chunk * (ichunk + 1)]
            ich2 = pair_channel2[npair_chunk * ichunk : npair_chunk * (ichunk + 1)]
            data1 = torch.from_numpy(data[ich1, :].reshape(-1, npts_seg)).to(device)
            data2 = torch.from_numpy(data[ich2, :].reshape(-1, npts_seg)).to(device)

            whitening_params = [fs, window_freq, f1, f2]
            # t1 = time.time()
            cc = (
                cross_correlation(data1, data2, is_spectral_whitening=True, whitening_params=whitening_params)
                .cpu()
                .numpy()
            )
            cc = np.sum(cc.reshape(len(ich1), nseg, -1), 1)
            ccall[npair_chunk * ichunk : npair_chunk * (ichunk + 1), :] += cc[
                :, npts_seg - npts_lag - 1 : npts_lag - npts_seg + 1
            ]
        # print(time.time() - t1)
        # del data1, data2, cc
    if flag_mean > 0:
        ccall /= flag_mean
        # print('Cross correlation of', idate, time.time() - t1)
        np.save(output_file_tmp, ccall)


#%% plot

import matplotlib.pyplot as plt

ccall = np.load(output_file_tmp)
vmax = np.percentile(np.abs(ccall), 99)
plt.imshow(
    # filter(ccall, 25, 1, 10),
    ccall,
    aspect="auto",
    vmax=vmax,
    vmin=-vmax,
    # extent=(-max_lag, max_lag, ccall.shape[0], 0),
    cmap="RdBu",
)
plt.colorbar()
plt.savefig("cc.png", dpi=300, bbox_inches="tight")
plt.show()
