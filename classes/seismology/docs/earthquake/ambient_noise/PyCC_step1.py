# This script does preprocessing for ambient noise cross-correlation, including:
# differentiation, detrend, bandpass filter, decimation,
# demean (of channels), temporal normalization
# Yan Yang 2022-07-10

import glob
import os
from time import time

import h5py
import numpy as np
from joblib import Parallel, delayed
from tqdm import tqdm

from func_PyCC import *

#%% parameters for Ridgecrest_ODH3
output_preprocessed = "./preprocessed/"
filelist = glob.glob("/kuafu/DASdata/Ridgecrest_ODH3_2_Hourly/*.h5")
filelist.sort()
# filelist = filelist[:2]
filelist = filelist[:1]
print(filelist)

fs = 50  # sampling frequency
f1, f2 = 0.1, 10  # bandpass filter in preprocessing
Decimation = 2  # if not 1, decimation after filtering
Diff = True  # whether differentiate strain to strain rate
ram_win = 2  # temporal normalization windowm, usually  1/f1/5 ~ 1/f1/2 #
min_length = 60  # length of the segment in preprocessing, in sec, if shorter than this length, skip the file
min_npts = int(min_length * fs)
njobs = 5  # number f jobs if parallel


def preprocess(x, fs, f1, f2, Decimation, Diff=Diff, ram_win=ram_win):
    """
    :param x: input data shape (nch, npts)
    :param fs, f1, f2, Decimation, Diff, ram_win: see above
    :return:
    """
    if Diff:
        x = np.gradient(x, axis=-1) * fs
    x = detrend(x, axis=-1)
    x = filter(x, fs, f1, f2)
    x = x[:, ::Decimation]
    fs_deci = fs / Decimation
    x = x - np.median(x, 0)
    x = temporal_normalization(x, fs_deci, ram_win)
    x = x.astype("float32")
    return x


#%% Preprocessing: read raw data, decimation, differentiation, bandpass filter, demean
if not os.path.exists(output_preprocessed):
    os.mkdir(output_preprocessed)

for ifile in tqdm(filelist):
    outputname = os.path.join(
        output_preprocessed,
        ifile.split("_")[-1]
        .replace("-", "")
        .replace("T", "")
        .replace(":", "")
        .replace("Z", "")
        .replace(" ", "")
        .replace("T", "")
        .replace(":", "")[-17:],
    )
    # try not overlap
    # if os.path.exists(outputname):
    #     print(outputname, "exists")
    #     continue

    fid = h5py.File(ifile, "r")
    fs_data = fid["Data"].attrs["fs"]
    nt_data = fid["Data"].attrs["nt"]
    if fs_data != fs:
        print(f"wrong fs: {ifile}")
        fid.close()
        continue
    if nt_data < min_npts:
        print(f"too short file: {ifile}")
        fid.close()
        continue

    # t1 = time()

    data = fid["Data"][:]
    nch = data.shape[0]
    npts = data.shape[1]
    fid.close()

    # print('read', time() - t1)
    # t1 = time()

    nchunk = int(np.ceil(npts / min_npts))
    out = Parallel(n_jobs=njobs)(
        delayed(preprocess)(data[:, int(min_length * fs * i) : int(min_length * fs * (i + 1))], fs, f1, f2, Decimation)
        for i in range(nchunk)
    )
    data_out = np.concatenate(out, axis=-1)
    # print('parallel', time() - t1)

    # t1 = time()
    fs_deci = fs / Decimation
    output_h5 = h5py.File(outputname, "w")
    output_data = output_h5.create_dataset("Data", data=data_out)
    output_data.attrs["fs"] = fs_deci
    output_data.attrs["dt"] = 1 / fs_deci
    output_data.attrs["nt"] = data_out.shape[1]
    output_data.attrs["nCh"] = data_out.shape[0]
    output_h5.close()
    # print(ifile,'save', time() - t1)
