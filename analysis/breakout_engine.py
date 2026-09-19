import numpy as np
import pandas as pd

def analyze_breakouts(df, phase, level_window=20, forward_bars=5):
    o=df.copy()
    o["resistance"]=o.High.rolling(level_window).max().shift(1)
    o["support"]=o.Low.rolling(level_window).min().shift(1)
    o["breakout_up"]=o.Close>o.resistance
    o["breakdown_down"]=o.Close<o.support
    o["false_breakout_up"]=(o.High>o.resistance)&(o.Close<=o.resistance)
    o["failed_breakdown_down"]=(o.Low<o.support)&(o.Close>=o.support)
    if "Volume" in o:
        o["volume_ratio"]=o.Volume/o.Volume.rolling(20).mean()
        o["volume_confirmed"]=o.volume_ratio>=1.20
    o["phase_deg"]=np.degrees(phase)%360
    o["forward_return"]=o.Close.shift(-forward_bars)/o.Close-1
    return o

def phase_statistics(signals,buckets=12):
    x=signals.copy()
    x["phase_bucket"]=np.floor(x.phase_deg/(360/buckets)).astype("Int64")
    rows=[]
    for b,g in x.groupby("phase_bucket",dropna=True):
        up=g[g.breakout_up&g.forward_return.notna()]
        dn=g[g.breakdown_down&g.forward_return.notna()]
        rows.append({
            "phase_bucket":int(b),
            "start_deg":b*360/buckets,"end_deg":(b+1)*360/buckets,
            "breakout_n":len(up),
            "breakout_avg_fwd":up.forward_return.mean() if len(up) else np.nan,
            "breakout_positive_rate":(up.forward_return>0).mean() if len(up) else np.nan,
            "breakdown_n":len(dn),
            "breakdown_avg_fwd":dn.forward_return.mean() if len(dn) else np.nan,
            "breakdown_negative_rate":(dn.forward_return<0).mean() if len(dn) else np.nan,
        })
    return pd.DataFrame(rows).sort_values("phase_bucket")
