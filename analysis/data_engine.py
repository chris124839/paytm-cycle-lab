from pathlib import Path
import pandas as pd

def norm(x):
    return "".join(c.lower() for c in str(x) if c.isalnum())

def load_ohlc(source):
    if hasattr(source, "read"):
        name = getattr(source, "name", "").lower()
        raw = pd.read_excel(source) if name.endswith(("xlsx","xls")) else pd.read_csv(source)
    else:
        p = Path(source)
        raw = pd.read_excel(p) if p.suffix.lower() in (".xlsx",".xls") else pd.read_csv(p)

    cols = {norm(c): c for c in raw.columns}
    aliases = {
        "date":["date","datetime","timestamp","time"],
        "open":["open","o"], "high":["high","h"], "low":["low","l"],
        "close":["close","closingprice","c","ltp"], "volume":["volume","vol","v"]
    }
    pick={}
    for k, names in aliases.items():
        for n in names:
            if norm(n) in cols:
                pick[k]=cols[norm(n)]
                break
    missing=[x for x in ["date","open","high","low","close"] if x not in pick]
    if missing:
        raise ValueError(f"Missing columns {missing}. Found: {list(raw.columns)}")

    out=pd.DataFrame({
        "Date":pd.to_datetime(raw[pick["date"]], errors="coerce"),
        "Open":pd.to_numeric(raw[pick["open"]], errors="coerce"),
        "High":pd.to_numeric(raw[pick["high"]], errors="coerce"),
        "Low":pd.to_numeric(raw[pick["low"]], errors="coerce"),
        "Close":pd.to_numeric(raw[pick["close"]], errors="coerce"),
    })
    if "volume" in pick:
        out["Volume"]=pd.to_numeric(raw[pick["volume"]], errors="coerce")
    out=out.dropna(subset=["Date","Open","High","Low","Close"]).sort_values("Date").drop_duplicates("Date")
    out=out.set_index("Date")
    if (out.High < out.Low).any():
        raise ValueError("Invalid OHLC: High < Low found.")
    return out
