"""NT8 DAILY .ncd READER - the TSMOM data transport.

FORMAT, reverse-engineered and VALIDATED against GetBars on ES 12-11 (close AND volume matched
exactly on 2011-05-30 / 2011-09-08 / 2011-10-03 / 2011-12-15):

    header  28 bytes : int32 version | float64 tickSize | float64 firstPrice | int64 firstTicks
    record  48 bytes : int64 ticks | float64 open | float64 high | float64 low | float64 close
                       | int64 volume

    ticks are .NET DateTime ticks (100 ns since 0001-01-01).

WHY THIS FILE EXISTS - the finding that forced it (see TSMOM_DATA_CONTRACT.md):

    NT8 serves DIFFERENT DATA THROUGH DIFFERENT PATHS FOR THE SAME CONTRACT NAME.

      AddDataSeries / RunStrategyBacktest  ->  MERGE BACK ADJUSTED
      GetBars / the db/day .ncd store      ->  TRUE, UNMERGED CONTRACT DATA

    Measured on ES 03-11 / 06-11 / 09-11 / 12-11 over 2010:
      * all four "contracts" report IDENTICAL volume on 2010-01-04 (1,098,424) - they are the
        same front-month bar wearing four names;
      * ES 12-11 minus ES 03-11 is EXACTLY -16.000 with sd 0.0000 across all of 2010 - a constant
        offset, which is the definition of back-adjustment, and that constant IS THE ROLL BASIS;
      * merged equals true ONLY from the day the contract becomes front month (2011-09-08 for
        ESZ1). Before that, merged carries the THEN-FRONT contract's prices and volume
        (2011-06-01: merged vol 2,323,510 vs the contract's true 167).

    CONSEQUENCE, and it is fatal for this lane: a volume-crossover roll CANNOT be computed from
    the merged path, because the next contract's "volume" there is a copy of the current front's.
    The crossover can never fire, and the roll basis is already baked into the prices. Building
    TSMOM on it would have manufactured trend returns out of futures basis - exactly what
    directive s7 exists to prevent.

TRANSPORT NOTE. A GetBars call CACHES the downloaded range into db/day/<REQUESTED ID>/<YEAR>.Last.ncd
and `limit` shrinks only the RESPONSE, not the download. So one cheap call per contract triggers a
full-history fetch that this reader then consumes locally - no per-contract data round trip.

IDENTITY NOTE. The cache directory is named by the FULL REQUESTED CONTRACT ID ("ES 12-11"), not by
the decade-ambiguous display symbol (ESZ1 == both Dec-2011 and Dec-2021). Directive s5 satisfied by
construction: the directory name IS the key.
"""
from __future__ import annotations

import datetime
import os
import re

import numpy as np
import pandas as pd

DB_DAY = os.path.join(os.path.expanduser("~"), "Documents", "NinjaTrader 8", "db", "day")
HDR = 28
REC = np.dtype([("ts", "<i8"), ("o", "<f8"), ("h", "<f8"), ("l", "<f8"),
                ("c", "<f8"), ("v", "<i8")])
NET_EPOCH = np.datetime64("0001-01-01T00:00:00", "us")

MONTH_CODE = {1: "F", 2: "G", 3: "H", 4: "J", 5: "K", 6: "M",
              7: "N", 8: "Q", 9: "U", 10: "V", 11: "X", 12: "Z"}

# DIRECTIVE s5: the legal contract cycle is DECLARED PER ROOT, never inferred as "quarterly".
CYCLES = {
    **{r: [3, 6, 9, 12] for r in ("ES", "NQ", "YM", "RTY")},          # equity index
    **{r: [3, 6, 9, 12] for r in ("ZT", "ZF", "ZN", "ZB")},           # rates
    **{r: [3, 6, 9, 12] for r in ("6E", "6J", "6B", "6A", "6C", "6S")},  # FX
    "CL": list(range(1, 13)), "NG": list(range(1, 13)),               # energy, monthly
    "RB": list(range(1, 13)), "HO": list(range(1, 13)),
    "GC": [2, 4, 6, 8, 10, 12],                                       # gold
    "SI": [3, 5, 7, 9, 12], "HG": [3, 5, 7, 9, 12],                   # silver, copper
    "ZC": [3, 5, 7, 9, 12], "ZW": [3, 5, 7, 9, 12],                   # corn, wheat
    "ZM": [1, 3, 5, 7, 8, 9, 10, 12], "ZL": [1, 3, 5, 7, 8, 9, 10, 12],  # meal, oil
}
SECTOR = {
    **{r: "equity_index" for r in ("ES", "NQ", "YM", "RTY")},
    **{r: "rates" for r in ("ZT", "ZF", "ZN", "ZB")},
    **{r: "fx" for r in ("6E", "6J", "6B", "6A", "6C", "6S")},
    **{r: "energy" for r in ("CL", "NG", "RB", "HO")},
    **{r: "metals" for r in ("GC", "SI", "HG")},
    **{r: "ags" for r in ("ZC", "ZW", "ZM", "ZL")},
}
# CME point values (USD per 1.00 of quoted price)
PV = {"ES": 50, "NQ": 20, "RTY": 50, "YM": 5,
      "ZT": 2000, "ZF": 1000, "ZN": 1000, "ZB": 1000,
      "6E": 125000, "6J": 12500000, "6B": 62500, "6A": 100000, "6C": 100000, "6S": 125000,
      "CL": 1000, "NG": 10000, "RB": 42000, "HO": 42000,
      "GC": 100, "SI": 5000, "HG": 25000,
      "ZC": 50, "ZW": 50, "ZM": 100, "ZL": 600}
CORE = ["ES", "NQ", "YM", "ZT", "ZF", "ZN", "ZB", "6E", "6J", "6B", "6A", "6C", "6S",
        "CL", "NG", "GC", "SI", "ZC", "ZW", "ZM", "ZL"]          # 21, measured to reach 2009
EXTENDED = ["RTY", "RB", "HO", "HG"]


def contract_id(root: str, month: int, year: int) -> str:
    """NT8's full contract name. THIS is the key - never the display symbol."""
    return f"{root} {month:02d}-{year % 100:02d}"


def contracts_for(root: str, y0: int, y1: int):
    return [(contract_id(root, m, y), root, m, y)
            for y in range(y0, y1 + 1) for m in CYCLES[root]]


def read_ncd_day(path: str) -> pd.DataFrame:
    b = np.fromfile(path, dtype=np.uint8)
    if b.size < HDR + REC.itemsize:
        return pd.DataFrame(columns=["date", "open", "high", "low", "close", "volume"])
    tick = float(b[4:12].view("<f8")[0])
    n = (b.size - HDR) // REC.itemsize
    a = b[HDR:HDR + n * REC.itemsize].view(REC)
    d = pd.DataFrame({
        "date": (NET_EPOCH + (a["ts"] // 10).astype("timedelta64[us]")).astype("datetime64[ns]"),
        "open": a["o"], "high": a["h"], "low": a["l"], "close": a["c"],
        "volume": a["v"].astype("int64"),
    })
    d["tick_size"] = tick
    return d


def read_contract(cid: str) -> pd.DataFrame:
    """All cached years for one contract, concatenated and de-duplicated by date."""
    d = os.path.join(DB_DAY, cid)
    if not os.path.isdir(d):
        return pd.DataFrame()
    parts = []
    for f in sorted(os.listdir(d)):
        if re.match(r"^\d{4}\.Last\.ncd$", f):
            parts.append(read_ncd_day(os.path.join(d, f)))
    if not parts:
        return pd.DataFrame()
    x = pd.concat(parts, ignore_index=True).sort_values("date")
    x = x.drop_duplicates(subset=["date"], keep="last").reset_index(drop=True)
    x["contract_id"] = cid                       # the KEY, per s5
    return x


def cached_ids() -> set:
    if not os.path.isdir(DB_DAY):
        return set()
    return {n for n in os.listdir(DB_DAY) if os.path.isdir(os.path.join(DB_DAY, n))}
