import numpy as np

def bandpower(signal, fs=256.0):
    s=np.array(signal, dtype=float)
    return {
        "mean": float(np.mean(s)),
        "std": float(np.std(s)),
        "power": float(np.sum(s**2)/len(s))
    }
