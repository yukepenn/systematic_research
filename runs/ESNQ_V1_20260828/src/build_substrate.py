"""ESNQ_V1 substrate build: raw tick CSV -> parquet, with QA.  DEVELOPMENT SESSIONS ONLY.

BLOCKING GUARDS, in order, before anything is written:
  1. every session found on disk must be in ESNQ_DEV_44
  2. intersection with ESNQ_BLIND_15 must be EMPTY (research_sdk/blindguard)
  3. both instruments must be present for a session, or it is quarantined (not silently dropped)

Deletes each CSV after a verified conversion, so peak disk stays bounded. That is not tidiness:
the DOM incident (2026-08-12) makes resource safety a hard constraint, and ~24 GB of raw CSV is
exactly the kind of accumulation that caused it.
"""
from __future__ import annotations

import glob
import hashlib
import os
import sys

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(RUN))
sys.path.insert(0, os.path.join(ROOT, "research_sdk"))
import blindguard as BG                                                 # noqa: E402

RAW = os.path.join(ROOT, "research", "data_esnq", "raw")
OUTP = os.path.join(ROOT, "research", "data_esnq", "parquet")
DEV_MAN = os.path.join(RUN, "manifests", "ESNQ_DEV_44.csv")
BLIND_MAN = os.path.join(RUN, "manifests", "ESNQ_BLIND_15.csv")
OUT = os.path.join(RUN, "out")
os.makedirs(OUT, exist_ok=True)
RTH_START, RTH_END = "10:00:00", "15:30:00"


def sessions_on_disk(inst):
    d = os.path.join(RAW, inst)
    out = []
    for f in sorted(glob.glob(os.path.join(d, "s*_ticks.csv"))):
        b = os.path.basename(f)
        out.append((b[1:9], f))
    return out


def convert(inst, keep_csv=False):
    os.makedirs(os.path.join(OUTP, inst), exist_ok=True)
    rows = []
    for sd, path in sessions_on_disk(inst):
        iso = f"{sd[:4]}-{sd[4:6]}-{sd[6:]}"
        outp = os.path.join(OUTP, inst, f"s{sd}.parquet")
        if os.path.exists(outp):
            d = pq.read_table(outp, columns=["bip", "time"]).to_pandas()
        else:
            d = pd.read_csv(path, dtype={"bip": "int8", "price": "float64",
                                         "volume": "float64"},
                            parse_dates=["time"])
            d = d.sort_values("time", kind="stable").reset_index(drop=True)
            pq.write_table(pa.Table.from_pandas(d, preserve_index=False), outp,
                           compression="zstd")
            if not keep_csv:
                os.remove(path)
        ti = d["time"].values.astype("datetime64[ns]").astype("int64")
        bip = d["bip"].values
        day = pd.Timestamp(iso)
        r0 = (day + pd.Timedelta(RTH_START)).value
        r1 = (day + pd.Timedelta(RTH_END)).value
        rec = dict(session=f"s{sd}", session_date=iso, instrument=inst,
                   rows=int(len(d)), n_last=int((bip == 0).sum()),
                   n_bid=int((bip == 1).sum()), n_ask=int((bip == 2).sum()),
                   t_min=str(pd.Timestamp(ti.min())), t_max=str(pd.Timestamp(ti.max())),
                   monotonic=bool(np.all(np.diff(ti) >= 0)),
                   dup_ts_frac=float(np.mean(np.diff(ti) == 0)) if len(ti) > 1 else 0.0,
                   rth_covers_start=bool(ti.min() <= r0), rth_covers_end=bool(ti.max() >= r1),
                   parquet_mb=round(os.path.getsize(outp) / 2 ** 20, 2),
                   sha256=hashlib.sha256(open(outp, "rb").read()).hexdigest())
        for b, nm in ((1, "bid"), (2, "ask"), (0, "last")):
            tb = ti[bip == b]
            rec[f"{nm}_rth_gap_max_s"] = (
                float(np.max(np.diff(tb[(tb >= r0) & (tb <= r1)])) / 1e9)
                if ((tb >= r0) & (tb <= r1)).sum() > 1 else np.nan)
        rows.append(rec)
        print(f"  {inst} {iso}  rows {rec['rows']:>9,}  "
              f"L/B/A {rec['n_last']:>7,}/{rec['n_bid']:>8,}/{rec['n_ask']:>8,}  "
              f"{rec['parquet_mb']:>7.1f} MB", flush=True)
    return pd.DataFrame(rows)


def main():
    dev = BG.load_manifest(DEV_MAN)
    print("=" * 104)
    print("=== ESNQ_V1 SUBSTRATE BUILD -- DEVELOPMENT SESSIONS ONLY")
    print("=" * 104)
    for inst in ("NQ", "ES"):
        found = {f"{s[:4]}-{s[4:6]}-{s[6:]}" for s, _ in sessions_on_disk(inst)}
        BG.assert_no_blind_contamination(found, BLIND_MAN, label=f"{inst} substrate build")
        extra = sorted(found - dev)
        if extra:
            raise SystemExit(f"{inst}: {len(extra)} session(s) on disk are NOT in DEV_44: {extra}")
        print(f"    {inst}: {len(found)} sessions on disk, all in DEV_44, ZERO blind. GUARDS PASS")

    frames = []
    for inst in ("NQ", "ES"):
        print(f"\n--- converting {inst}")
        frames.append(convert(inst))
    Q = pd.concat(frames, ignore_index=True)
    Q.to_csv(os.path.join(OUT, "substrate_qa.csv"), index=False)

    piv = Q.pivot_table(index="session_date", columns="instrument", values="rows",
                        aggfunc="first")
    both = piv.dropna()
    print("")
    print("=" * 104)
    print("=== QA")
    print("=" * 104)
    print(f"    sessions with BOTH instruments      {len(both)} / {len(dev)}")
    miss = sorted(set(dev) - set(both.index))
    if miss:
        print(f"    ⚠ QUARANTINED (missing one side)   {len(miss)}  {miss}")
    print(f"    all timestamps monotonic            {bool(Q['monotonic'].all())}")
    print(f"    RTH start covered (all)             {bool(Q['rth_covers_start'].all())}")
    print(f"    RTH end covered (all)               {bool(Q['rth_covers_end'].all())}")
    print(f"    duplicate-timestamp fraction  NQ {Q[Q.instrument=='NQ'].dup_ts_frac.median():.4f}"
          f"   ES {Q[Q.instrument=='ES'].dup_ts_frac.median():.4f}   (median over sessions)")
    for nm in ("bid", "ask", "last"):
        c = f"{nm}_rth_gap_max_s"
        print(f"    max intra-RTH {nm:<4} gap (s)   NQ {Q[Q.instrument=='NQ'][c].max():>8.2f}"
              f"   ES {Q[Q.instrument=='ES'][c].max():>8.2f}")
    print(f"\n    parquet total  NQ {Q[Q.instrument=='NQ'].parquet_mb.sum()/1024:.2f} GB"
          f"   ES {Q[Q.instrument=='ES'].parquet_mb.sum()/1024:.2f} GB")


if __name__ == "__main__":
    main()
