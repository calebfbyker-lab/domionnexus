import numpy as np
from scipy.signal import welch
def psd(x, fs, nperseg=256):
    f, Pxx = welch(np.asarray(x), fs=fs, nperseg=min(nperseg, len(x)))
    return f.tolist(), Pxx.tolist()
def bandpower(f, Pxx, lo, hi):
    f = np.asarray(f); Pxx = np.asarray(Pxx)
    idx = (f>=lo) & (f<=hi)
    if not idx.any(): return 0.0
    return float(np.trapz(Pxx[idx], f[idx]))
def zscore(x):
    x = np.asarray(x); mu=x.mean() if x.size else 0.0; sd=x.std() if x.size else 1.0
    return ((x-mu)/(sd+1e-9)).tolist()
