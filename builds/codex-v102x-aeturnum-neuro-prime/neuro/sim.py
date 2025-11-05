import numpy as np

def sine(fs, f, seconds, amp=1.0, phase=0.0):
    t = np.arange(0, int(fs * seconds)) / fs
    return t, amp * np.sin(2 * np.pi * f * t + phase)


def eeg_synth(fs=256, seconds=2.0, alpha=10.0, beta=20.0, gamma=40.0, noise=0.3, blink=False, seed=None):
    rng = np.random.default_rng(seed)
    t, a = sine(fs, alpha, seconds, amp=1.0)
    _, b = sine(fs, beta, seconds, amp=0.6)
    _, g = sine(fs, gamma, seconds, amp=0.3)
    x = a + b + g + noise * rng.standard_normal(len(a))
    if blink:
        idx = rng.integers(0, max(1, len(x) - int(0.2 * fs)))
        x[idx:idx + int(0.2 * fs)] += 2.5
    return t.tolist(), x.tolist()


def eeg_multichannel(n=8, fs=256, seconds=2.0, alpha=10.0, beta=20.0, gamma=40.0, noise=0.3, seed=None):
    rng = np.random.default_rng(seed)
    data = {}
    for ch in range(n):
        phase = rng.uniform(0, 2 * np.pi)
        _, x = eeg_synth(fs=fs, seconds=seconds, alpha=alpha, beta=beta, gamma=gamma, noise=noise, blink=(rng.random() < 0.1), seed=seed)
        # add slight phase offset per channel
        x = (np.array(x) * np.cos(phase)).tolist()
        data[f"CH{ch+1:02d}"] = x
    return {"fs": fs, "seconds": seconds, "channels": data}
