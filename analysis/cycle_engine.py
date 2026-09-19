import numpy as np
import pandas as pd
from scipy.signal import detrend, hilbert, periodogram

def analyze_cycles(close, detrend_window=20, min_period=5, max_period=120, n_harmonics=6):
    s=pd.Series(close).astype(float).interpolate().ffill().bfill()
    ma=s.rolling(detrend_window,min_periods=1).mean()
    residual=(s-ma).to_numpy()
    x=detrend(residual)
    f,p=periodogram(x,detrend=False)
    periods=np.divide(1,f,out=np.full_like(f,np.inf),where=f!=0)
    mask=np.isfinite(periods)&(periods>=min_period)&(periods<=min(max_period,len(s)/2))
    spectrum=pd.DataFrame({"period":periods[mask],"power":p[mask]}).sort_values("power",ascending=False)

    selected=[]
    for r in spectrum.itertuples(index=False):
        if all(abs(r.period-q)/q>0.10 for q in selected):
            selected.append(float(r.period))
        if len(selected)>=n_harmonics: break

    t=np.arange(len(s),dtype=float)
    reconstruction=np.zeros(len(s))
    components=[]
    for period in selected:
        w=2*np.pi/period
        X=np.column_stack([np.cos(w*t),np.sin(w*t)])
        beta,*_=np.linalg.lstsq(X,x,rcond=None)
        wave=X@beta
        reconstruction += wave
        components.append({
            "period":period,
            "amplitude":float(np.hypot(beta[0],beta[1])),
            "phase_deg":float(np.degrees(np.arctan2(-beta[1],beta[0]))%360)
        })

    phase=np.unwrap(np.angle(hilbert(x)))%(2*np.pi)
    return {"detrended":residual,"spectrum":spectrum.sort_values("period").reset_index(drop=True),
            "components":components,"reconstruction":reconstruction,"phase":phase}
