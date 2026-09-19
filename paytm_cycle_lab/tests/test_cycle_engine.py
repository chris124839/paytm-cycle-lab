import numpy as np
import pandas as pd
from analysis.cycle_engine import analyze_cycles

def test_basic_cycle_detection():
    n=300; t=np.arange(n)
    s=100+0.03*t+3*np.sin(2*np.pi*t/20)
    r=analyze_cycles(pd.Series(s),20,5,60,3)
    assert r["components"]
