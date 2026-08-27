"""CSV -> parquet, into a NEW canonical substrate, with QA gates BEFORE anything is trusted.

Why a new substrate rather than extending scalping_lab/substrate/raw/NQ (directive s8):
the old 48 files are NOT uniform. 17 of them sit at exactly 12,000,000 rows - the v1 exporter's
cap - which means they are SILENTLY TRUNCATED mid-session (s20260206 ends 13:28:44 instead of
16:59:59). Three carry no quotes at all. Appending v4 output to that would produce one directory
whose files mean different things, which is exactly the drift CLAUDE.md s7 forbids.

The old substrate is left untouched so every prior wave stays bit-reproducible.

QA per session, all recorded, none of it optional:
    row counts by series, session span, quote coverage as a FRACTION OF SESSION MINUTES,
    trade coverage, out-of-order events, duplicate rows, gaps, price sanity, sha256.
A session that fails a HARD gate is quarantined, not silently included.
"""
from __future__ import annotations

import hashlib
import os
import sys

import numpy as np
import pandas as pd

ROOT = (r"D:\OneDrive - Washington University in St. Louis\TradingResearch"
        r"\systematic_research")
CSV = os.path.join(ROOT, "runs", "ORDERFLOW_EXPAND_20260827", "out", "csv")
SUB = os.path.join(ROOT, "research", "data_microstructure_v2")
RAW = os.path.join(SUB, "raw", "NQ")
QUAL = os.path.join(SUB, "quality")
HASH = os.path.join(SUB, "hashes")
for d in (RAW, QUAL, HASH):
    os.makedirs(d, exist_ok=True)

MAN = os.path.join(SUB, "MANIFEST.csv")
QA = os.path.join(QUAL, "qa.csv")
SEAL = "2026-08-01"

# HARD gates. A session failing any of these is quarantined.
MIN_ROWS = 50_000
MIN_SPAN_H = 20.0            # a real NQ session spans ~23 h
MAX_OOO_FRAC = 0.001         # out-of-order events within a series


def sha256(path, chunk=1 << 22):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def main():
    rl = pd.read_csv(os.path.join(ROOT, "runs", "ORDERFLOW_EXPAND_20260827",
                                  "out", "runlist.csv"))
    inst_of = dict(zip(rl["session"], rl["instrument"]))

    done = set()
    if os.path.exists(MAN):
        done = set(pd.read_csv(MAN)["session"])

    # ONLY convert sessions the exporter has CLOSED. v4 writes its manifest line inside
    # CloseCurrent(), after Flush()+Close(), so a manifest line proves the CSV is complete.
    # Globbing *_ticks.csv directly would happily read a file another running job is still
    # appending to, and the truncation would look like real data.
    closed = set()
    vman = os.path.join(CSV, "_manifest.csv")
    if os.path.exists(vman):
        with open(vman, encoding="ascii", errors="replace") as fh:
            for ln in fh.read().splitlines()[1:]:
                p = ln.split(",")
                if len(p) == 9 and p[0].startswith("s"):     # ignore any partial line
                    closed.add(p[0])
    files = sorted(f for f in os.listdir(CSV)
                   if f.endswith("_ticks.csv") and f.replace("_ticks.csv", "") in closed)
    print(f"  {len(closed)} sessions closed by exporter, {len(files)} CSVs ready to convert")
    rows, qas = [], []
    for f in files:
        tag = f.replace("_ticks.csv", "")
        out = os.path.join(RAW, tag + ".parquet")
        if tag in done and os.path.exists(out):
            print(f"  {tag} already in substrate, skipping")
            continue
        src = os.path.join(CSV, f)
        df = pd.read_csv(src, dtype={"bip": "int8", "price": "float64",
                                     "volume": "int32"}, parse_dates=["time"])
        n = len(df)
        t0, t1 = df["time"].min(), df["time"].max()
        span_h = (t1 - t0).total_seconds() / 3600.0

        # session date must be unique under the 18:00 roll
        sd = (df["time"] + pd.Timedelta(hours=6)).dt.normalize().unique()
        one_session = len(sd) == 1
        sess_date = str(pd.Timestamp(sd[0]).date()) if one_session else "MULTIPLE"

        c = df["bip"].value_counts()
        nL, nB, nA = int(c.get(0, 0)), int(c.get(1, 0)), int(c.get(2, 0))

        # coverage as a fraction of the session's minutes, per series
        m = df.set_index("time")
        minutes = pd.date_range(t0.floor("min"), t1.ceil("min"), freq="min")
        cov = {}
        for b, nm in ((0, "trade"), (1, "bid"), (2, "ask")):
            s = m[m["bip"] == b]
            cov[nm] = (0.0 if not len(s) else
                       round(s.index.floor("min").nunique() / max(len(minutes), 1), 4))

        ooo = 0
        for b in (0, 1, 2):
            s = df[df["bip"] == b]["time"].values
            if len(s) > 1:
                ooo += int((np.diff(s) < np.timedelta64(0)).sum())
        ooo_frac = ooo / max(n, 1)

        dup = int(df.duplicated().sum())
        bad_px = int((df["price"] <= 0).sum())
        # largest gap in the TRADE series, in minutes
        tt = df[df["bip"] == 0]["time"]
        gap = (0.0 if len(tt) < 2 else
               round(float(tt.diff().max().total_seconds()) / 60.0, 2))

        fail = []
        if n < MIN_ROWS:
            fail.append("too_few_rows")
        if span_h < MIN_SPAN_H:
            fail.append("short_span")
        if not one_session:
            fail.append("multi_session")
        if ooo_frac > MAX_OOO_FRAC:
            fail.append("out_of_order")
        if bad_px:
            fail.append("bad_price")
        if sess_date != "MULTIPLE" and sess_date >= SEAL:
            fail.append("SEALED")          # must never happen; belt and braces
        verdict = "OK" if not fail else "QUARANTINE:" + "|".join(fail)

        qas.append(dict(session=tag, session_date=sess_date, rows=n,
                        trades=nL, bid_ev=nB, ask_ev=nA,
                        t_min=str(t0), t_max=str(t1), span_h=round(span_h, 3),
                        cov_trade=cov["trade"], cov_bid=cov["bid"], cov_ask=cov["ask"],
                        max_trade_gap_min=gap, out_of_order=ooo, dup_rows=dup,
                        bad_price=bad_px, verdict=verdict))

        if fail:
            print(f"  {tag}  {verdict}")
            continue

        df.to_parquet(out, compression="zstd", index=False)
        chk = pd.read_parquet(out, columns=["bip"])
        assert len(chk) == n, tag
        h = sha256(out)
        rows.append(dict(session=tag, session_date=sess_date,
                         instrument=inst_of.get(tag, "NQ"), rows=n, trades=nL,
                         bid_ev=nB, ask_ev=nA, t_min=str(t0), t_max=str(t1),
                         cov_bid=cov["bid"], cov_ask=cov["ask"],
                         src="SWScalpTickExport_v4",
                         provider="NT8 local db/tick via RunStrategyBacktest",
                         parquet_mb=round(os.path.getsize(out) / 1e6, 2), sha256=h))
        os.remove(src)
        print(f"  {tag}  {n:>10,} rows  bid_cov {cov['bid']:.3f}  ask_cov {cov['ask']:.3f}  OK")

    for path, new in ((MAN, rows), (QA, qas)):
        if not new:
            continue
        D = pd.DataFrame(new)
        if os.path.exists(path):
            D = pd.concat([pd.read_csv(path), D], ignore_index=True)
        D = D.drop_duplicates(subset=["session"], keep="last").sort_values("session")
        D.to_csv(path, index=False)

    if rows:
        M = pd.read_csv(MAN)
        print(f"\n  substrate now holds {len(M)} sessions, "
              f"{M['parquet_mb'].sum()/1000:.2f} GB, "
              f"{M['rows'].sum()/1e6:.1f} M events")
    print("BATCH DONE")


if __name__ == "__main__":
    sys.exit(main())
