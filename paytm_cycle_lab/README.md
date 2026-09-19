# Paytm Cycle Lab

Research dashboard for transforming linear OHLC prices into statistical waves/cycles and testing breakout behavior by cycle phase.

## Current dataset

The supplied Paytm historical file has been normalized to:

`data/paytm_ohlc.csv`

It contains 1,212 daily observations from 2021-11-18 through 2026-09-18 with Date, Series, Open, High, Low, Close and Volume.

## Pipeline

OHLC → close → detrending → spectral cycle detection → harmonic waves → Hilbert phase → circular representation → breakout/breakdown analysis → phase-conditioned forward returns.

The detected cycles are **statistical observations**, not assumed trading rules. The next stage is rolling/out-of-sample validation to test whether the apparent cycle structure persists.

## Run

```bash
pip install -r requirements.txt
streamlit run app.py
```

Upload another OHLC file later for IRCTC. The same engine is instrument-agnostic.

## GitHub

Push this folder to a GitHub repository. For the interactive Python dashboard, use Streamlit Community Cloud connected to the repository. GitHub Actions can later run the data update pipeline.

## Research question

Do breakouts occurring at different phases of a detected price cycle have measurably different subsequent returns, after controlling for the breakout definition and sample size?
