#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""BREADTH02 -- 00_download_curve.py: official treasury constant-maturity curve 2002-2026."""
import hashlib
import io
import json
import os
import time
import urllib.request

import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
DATA = os.path.join(ROOT, "research", "breadth_lab", "BREADTH02_CARRY", "data")
os.makedirs(DATA, exist_ok=True)

frames = []
for y in range(2002, 2027):
    url = (f"https://home.treasury.gov/resource-center/data-chart-center/interest-rates/"
           f"daily-treasury-rates.csv/{y}/all?type=daily_treasury_yield_curve"
           f"&field_tdr_date_value={y}&_format=csv")
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            raw = urllib.request.urlopen(req, timeout=60).read().decode()
            df = pd.read_csv(io.StringIO(raw))
            keep = ["Date"] + [c for c in df.columns if c.strip() in
                               ("3 Mo", "2 Yr", "10 Yr", "30 Yr")]
            frames.append(df[keep])
            print(y, len(df), flush=True)
            break
        except Exception as e:
            print(y, "retry", attempt, str(e)[:50], flush=True)
            time.sleep(3)
    time.sleep(0.3)

cur = pd.concat(frames)
cur.columns = [c.strip() for c in cur.columns]
cur["Date"] = pd.to_datetime(cur["Date"]).dt.date
for c in cur.columns[1:]:
    cur[c] = pd.to_numeric(cur[c], errors="coerce")
cur = cur.drop_duplicates("Date").sort_values("Date")
p = os.path.join(DATA, "treasury_curve.parquet")
cur.to_parquet(p, index=False)
h = hashlib.sha256(open(p, "rb").read()).hexdigest()[:16]
manifest = [{"symbol": "UST curve 3Mo/2Yr/10Yr/30Yr", "file": "treasury_curve.parquet",
             "rows": len(cur), "first": str(cur.Date.iloc[0]), "last": str(cur.Date.iloc[-1]),
             "sha256_16": h,
             "source": "home.treasury.gov daily_treasury_yield_curve yearly CSVs 2002-2026"}]
with open(os.path.join(DATA, "MANIFEST.json"), "w") as f:
    json.dump(manifest, f, indent=1)
print("TOTAL", len(cur), cur.Date.iloc[0], "->", cur.Date.iloc[-1], h, flush=True)
