import numpy as np
from scipy.signal import butter, lfilter, iirnotch, welch


def bandpass(x, fs, lo, hi, order=4):
    b, a = butter(order, [lo / (fs / 2), hi / (fs / 2)], btype='band')
    return lfilter(b, a, x)


def notch(x, fs, f0=60.0, Q=30.0):
    b, a = iirnotch(f0 / (fs / 2), Q)
    return lfilter(b, a, x)


def zscore(x):
    x = np.asarray(x)
    mu = x.mean() if x.size else 0.0
    sd = x.std() if x.size else 1.0
    return (x - mu) / (sd + 1e-9)


def psd(x, fs, nperseg=256):
    f, Pxx = welch(np.asarray(x), fs=fs, nperseg=min(nperseg, len(x)))
    return f.tolist(), Pxx.tolist()


def bandpower(f, Pxx, lo, hi):
    f = np.asarray(f); Pxx = np.asarray(Pxx)
    idx = (f >= lo) & (f <= hi)
    if not idx.any():
        return 0.0
    return float(np.trapz(Pxx[idx], f[idx]))
