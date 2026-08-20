#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""BREADTH01 -- 00_download.py: fetch daily adjusted data (Yahoo v8) + sha256 manifest."""
from __future__ import annotations

import datetime
import hashlib
import json
import os
import time
import urllib.request

import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
RUN = os.path.join(ROOT, "research", "breadth_lab", "BREADTH01_TSMOM_REPLICATION")
DATA = os.path.join(RUN, "data")
os.makedirs(DATA, exist_ok=True)

SYMS = ["SPY", "QQQ", "IWM", "EFA", "EEM", "TLT", "IEF", "GLD", "SLV", "USO", "UNG",
        "DBC", "FXE", "FXY", "UUP", "^IRX"]


def fetch(sym):
    p2 = int(time.time())
    url = (f"https://query1.finance.yahoo.com/v8/finance/chart/{urllib.parse.quote(sym)}"
           f"?period1=0&period2={p2}&interval=1d&events=div%2Csplit")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    j = json.loads(urllib.request.urlopen(req, timeout=30).read())
    r = j["chart"]["result"][0]
    ts = r["timestamp"]
    q = r["indicators"]["quote"][0]
    adj = r["indicators"].get("adjclose", [{}])[0].get("adjclose", q["close"])
    df = pd.DataFrame({
        "date": [datetime.datetime.utcfromtimestamp(t).date() for t in ts],
        "open": q["open"], "high": q["high"], "low": q["low"], "close": q["close"],
        "adjclose": adj, "volume": q["volume"]})
    df = df.dropna(subset=["adjclose"]).drop_duplicates("date").sort_values("date")
    return df


manifest = []
for s in SYMS:
    df = fetch(s)
    fn = s.replace("^", "_") + ".parquet"
    path = os.path.join(DATA, fn)
    df.to_parquet(path, index=False)
    h = hashlib.sha256(open(path, "rb").read()).hexdigest()[:16]
    manifest.append({"symbol": s, "file": fn, "rows": len(df),
                     "first": str(df.date.iloc[0]), "last": str(df.date.iloc[-1]),
                     "sha256_16": h,
                     "downloaded_utc": datetime.datetime.utcnow().isoformat() + "Z",
                     "source": "Yahoo Finance v8 chart API, adjclose"})
    print(f"{s:6s} {len(df):6d} rows  {df.date.iloc[0]} -> {df.date.iloc[-1]}  {h}", flush=True)
    time.sleep(0.5)

with open(os.path.join(DATA, "MANIFEST.json"), "w") as f:
    json.dump(manifest, f, indent=1)
print("manifest written", flush=True)
