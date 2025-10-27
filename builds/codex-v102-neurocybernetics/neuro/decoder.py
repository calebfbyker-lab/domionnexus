import pandas as pd
from neuro.signal_models import bandpower

def decode_csv(path:str)->dict:
    df=pd.read_csv(path)
    feats=[]
    for _,row in df.iterrows():
        ch = [float(x) for x in row.values[2:]]
        feats.append(bandpower(ch))
    avg_power = sum(f['power'] for f in feats)/max(1,len(feats))
    label = "rest" if avg_power < 0.05 else "active"
    return {"n_samples": len(df), "features_summary": {"avg_power": avg_power}, "label_demo": label}
