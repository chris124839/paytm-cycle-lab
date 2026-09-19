from pathlib import Path
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from analysis.data_engine import load_ohlc
from analysis.cycle_engine import analyze_cycles
from analysis.breakout_engine import analyze_breakouts, phase_statistics

st.set_page_config(page_title="Paytm Cycle Lab",layout="wide")
st.title("Paytm Cycle Lab")
st.caption("Linear OHLC → statistical waves → circular phase → breakout research")

with st.sidebar:
    upload=st.file_uploader("Upload OHLC CSV/XLSX",type=["csv","xlsx","xls"])
    detrend_window=st.number_input("Detrend MA window",5,250,20)
    min_period=st.number_input("Minimum cycle period",2,200,5)
    max_period=st.number_input("Maximum cycle period",10,1000,120)
    harmonics=st.number_input("Dominant cycles",1,10,6)
    level_window=st.number_input("Support/resistance lookback",5,250,20)
    phase_buckets=st.number_input("Phase buckets",4,36,12)
    forward_bars=st.number_input("Forward bars",1,100,5)

source=upload if upload is not None else Path("data/paytm_ohlc.csv")
try:
    df=load_ohlc(source)
except Exception as e:
    st.error(str(e)); st.stop()

st.subheader("1. Price")
fig=go.Figure(go.Candlestick(x=df.index,open=df.Open,high=df.High,low=df.Low,close=df.Close))
fig.update_layout(height=500,xaxis_rangeslider_visible=False)
st.plotly_chart(fig,use_container_width=True)

st.write({"Rows":len(df),"Start":str(df.index.min()),"End":str(df.index.max()),"Latest close":float(df.Close.iloc[-1])})

cycle=analyze_cycles(df.Close,int(detrend_window),int(min_period),int(max_period),int(harmonics))

st.subheader("2. Detrended close")
fig=go.Figure(go.Scatter(x=df.index,y=cycle["detrended"],mode="lines",name="Detrended"))
fig.add_hline(y=0); fig.update_layout(height=350)
st.plotly_chart(fig,use_container_width=True)

st.subheader("3. Cycle spectrum")
sp=cycle["spectrum"]
fig=go.Figure(go.Scatter(x=sp.period,y=sp.power,mode="lines+markers"))
fig.update_xaxes(title="Period (bars)"); fig.update_yaxes(title="Power"); fig.update_layout(height=400)
st.plotly_chart(fig,use_container_width=True)

st.subheader("4. Dominant cycles")
st.dataframe(pd.DataFrame(cycle["components"]).round(4),use_container_width=True)

st.subheader("5. Combined wave")
fig=go.Figure()
fig.add_trace(go.Scatter(x=df.index,y=cycle["detrended"],name="Detrended"))
fig.add_trace(go.Scatter(x=df.index,y=cycle["reconstruction"],name="Combined wave"))
fig.update_layout(height=400)
st.plotly_chart(fig,use_container_width=True)

st.subheader("6. Circular phase")
phase_deg=np.degrees(cycle["phase"])%360
fig=go.Figure(go.Scatterpolar(r=df.Close,theta=phase_deg,mode="markers",text=df.index.strftime("%Y-%m-%d")))
fig.update_layout(polar={"angularaxis":{"direction":"clockwise","rotation":90}},height=600)
st.plotly_chart(fig,use_container_width=True)

signals=analyze_breakouts(df,cycle["phase"],int(level_window),int(forward_bars))
st.subheader("7. Breakout / breakdown counts")
st.dataframe(signals[["breakout_up","breakdown_down","false_breakout_up","failed_breakdown_down"]].sum().rename("Count").to_frame(),use_container_width=True)

st.subheader("8. Forward outcome by phase")
st.caption("Historical descriptive statistics; no phase is assumed to predict future price.")
st.dataframe(phase_statistics(signals,int(phase_buckets)).round(4),use_container_width=True)

st.subheader("9. Recent signals")
cols=["Close","resistance","support","breakout_up","breakdown_down","false_breakout_up","failed_breakdown_down","phase_deg","forward_return"]
st.dataframe(signals[[c for c in cols if c in signals]].tail(30).round(4),use_container_width=True)

st.download_button("Download analysis CSV",signals.reset_index().to_csv(index=False).encode(), "paytm_cycle_breakout_analysis.csv","text/csv")
