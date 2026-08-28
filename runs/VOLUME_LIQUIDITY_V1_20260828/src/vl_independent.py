"""VOLUME_LIQUIDITY_V1 -- INDEPENDENT implementation.  EXPLICIT CHRONOLOGICAL LOOP.

SPEC 6E.  This file is structurally different from the primary in every mechanism that matters:

    PRIMARY                                  INDEPENDENT (this file)
    ------------------------------------     ------------------------------------------------
    reads VOLUME00's derived `vol` column     re-derives ROOT_TOTAL by summing the RAW
                                              contract-day panel itself
    pandas rolling().median()/.apply()        explicit numpy slices over a compacted index
    pd.merge_asof for the weekly cutoff       bisect over each root's own eligible-date array
    groupby().transform() for the demean      an explicit per-sector accumulation loop
    vectorized shift()/diff() for turnover    a day-by-day state machine carrying prev_n

It may share CERTIFIED RAW DATA and FROZEN CONSTANTS.  It does NOT import vl_primary -- verified
by AST, not by grep, because a docstring once matched a grep in this repo.  The constants are
RE-DECLARED literally rather than imported, so that a typo in either file fails parity instead of
cancelling out.
"""
from __future__ import annotations

import bisect
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(RUN))
sys.path.insert(0, os.path.join(ROOT, "research", "multi_market", "src"))
import ncd_day as NC                                                         # noqa: E402

# ---- RE-DECLARED FROM THE SPEC, NOT IMPORTED --------------------------------------------
LB = 63
MADK = 1.4826
FLOOR = 1e-6
CLIP3 = 3.0
SIGWIN = 63
BUDGET = 1000.0
CAP = 0.40
COMM = 4.36
SLIP1, SLIP2 = 1.0, 2.0
STALE = 7
SEAL = pd.Timestamp("2026-08-01")
TICKSZ = {"ES": 0.25, "NQ": 0.25, "YM": 1.0, "ZT": 1.0 / 128, "ZF": 1.0 / 128, "ZN": 1.0 / 64,
          "ZB": 1.0 / 32, "6E": 0.00005, "6J": 0.0000005, "6B": 0.0001, "6A": 0.0001,
          "6C": 0.00005, "6S": 0.0001, "CL": 0.01, "NG": 0.001, "GC": 0.1, "SI": 0.005,
          "ZC": 0.25, "ZW": 0.25, "ZM": 0.1, "ZL": 0.01}


def _side(rt, slip):
    return (COMM + slip * TICKSZ[rt] * NC.PV[rt]) / 2.0


def _monday(ts):
    return ts - pd.Timedelta(days=int(ts.weekday()))


def run(slip=SLIP1, sign=+1.0, date_max=None, roots=None):
    # ---------------- RAW inputs, re-derived
    pan = pd.read_parquet(os.path.join(ROOT, "runs", "VOLUME00_20260828", "out", "panel.parquet"),
                          columns=["root", "date", "volume"])
    pan = pan[pan["date"] < SEAL]
    er = pd.read_parquet(os.path.join(ROOT, "research", "multi_market", "out",
                                      "economic_returns.parquet"),
                         columns=["date", "root", "sector", "ret_usd", "eligible", "rolled"])
    er = er[er["date"] < SEAL]
    if date_max is not None:                 # structural window protection, applied AT LOAD
        pan, er = pan[pan["date"] < date_max], er[er["date"] < date_max]
    if roots is not None:
        pan, er = pan[pan["root"].isin(roots)], er[er["root"].isin(roots)]
    # ROOT_TOTAL, computed here rather than taken from VOLUME00's pivot
    rt = pan.groupby(["root", "date"], sort=True)["volume"].sum().reset_index()

    elig_key = set(map(tuple, er.loc[er["eligible"], ["root", "date"]].values))
    sectorof = er.groupby("root")["sector"].first().to_dict()

    # ---------------- per-root arrays
    LVD, LVV, RD, RR, REL, RRO = {}, {}, {}, {}, {}, {}
    for r, g in rt.groupby("root", sort=True):
        g = g.sort_values("date")
        keep = [(d, v) for d, v in zip(g["date"], g["volume"])
                if v is not None and v > 0 and (r, d) in elig_key]
        LVD[r] = [d for d, _ in keep]
        LVV[r] = np.log1p(np.array([float(v) for _, v in keep]))
    for r, g in er.groupby("root", sort=True):
        g = g.sort_values("date")
        RD[r] = list(g["date"])
        RR[r] = g["ret_usd"].values.astype(float)
        REL[r] = g["eligible"].values.astype(bool)
        RRO[r] = g["rolled"].values.astype(int)
    RIDX = {r: {d: i for i, d in enumerate(RD[r])} for r in RD}

    # ---------------- the (root, week) grid, from eligible sessions only
    grid = {}
    for r in RD:
        for i, d in enumerate(RD[r]):
            if REL[r][i]:
                grid.setdefault(_monday(d), set()).add(r)
    mondays = sorted(grid)
    if date_max is not None:
        mondays = [m for m in mondays if m < date_max]

    # ---------------- CHRONOLOGICAL LOOP: one week at a time
    POS = {}
    for mon in mondays:
        cand = {}
        for r in sorted(grid[mon]):
            dl = LVD[r]
            k = bisect.bisect_left(dl, mon) - 1              # last eligible obs STRICTLY before
            if k < LB:
                continue
            if (mon - dl[k]).days > STALE:                   # R1 staleness
                continue
            win = LVV[r][k - LB:k]                           # 63 values strictly before k
            med = float(np.median(win))
            mad = float(np.median(np.abs(win - med)))
            z = (float(LVV[r][k]) - med) / max(MADK * mad, FLOOR)
            j = RIDX[r].get(dl[k])
            if j is None or j < SIGWIN:
                continue
            sw = RR[r][j - SIGWIN:j]
            sg = float(np.std(sw, ddof=1))
            if not np.isfinite(sg) or sg <= 0:
                continue
            cand[r] = (z, sg)
        if not cand:
            continue
        # ---- explicit per-sector accumulation for the demean
        acc = {}
        for r, (z, _) in cand.items():
            s = sectorof[r]
            a = acc.setdefault(s, [0.0, 0])
            a[0] += z
            a[1] += 1
        raw, gross_i = {}, {}
        for r, (z, sg) in cand.items():
            s = sectorof[r]
            relz = z - acc[s][0] / acc[s][1]
            S = min(CLIP3, max(-CLIP3, sign * (-relz)))
            rs = S / CLIP3
            raw[r] = rs * BUDGET / sg
            gross_i[r] = abs(rs) * BUDGET
        # ---- sector cap, ONE pass, CAP DOWN ONLY
        gs, gt = {}, 0.0
        for r, gi in gross_i.items():
            gs[sectorof[r]] = gs.get(sectorof[r], 0.0) + gi
            gt += gi
        for r in raw:
            s = sectorof[r]
            sc = CAP * gt / gs[s] if (gt > 0 and gs[s] / gt > CAP) else 1.0
            POS[(r, mon)] = raw[r] * sc

    # ---------------- turnover state machine, then daily accrual
    prev_n = {r: 0.0 for r in RD}
    sides_at = {}
    for mon in mondays:
        for r in sorted(grid[mon]):
            n = POS.get((r, mon), 0.0)
            sides_at[(r, mon)] = abs(n - prev_n[r])
            prev_n[r] = n

    rows = []
    for r in sorted(RD):
        seen_week = set()
        for i, d in enumerate(RD[r]):
            if not REL[r][i]:
                continue
            mon = _monday(d)
            # DEFECT FOUND BY THE 6E PARITY GATE, 2026-08-28.  This line originally filtered on
            # `mon >= date_max`, i.e. on the WEEK LABEL.  The week stamped Monday 2018-12-31 runs
            # to 2019-01-04, so 47 sessions of the HELD-BACK window were being accrued into the
            # development result.  The window boundary is a SESSION-DATE boundary, not a week
            # boundary.  The primary always filtered on `date`; the independent did not, and the
            # parity gate is what surfaced it.
            if date_max is not None and d >= date_max:
                continue
            n = POS.get((r, mon), 0.0)
            sd = 0.0
            if mon not in seen_week:                       # first eligible session of the week
                seen_week.add(mon)
                sd += sides_at.get((r, mon), 0.0)
            if RRO[r][i] == 1:
                sd += 2.0 * abs(n)
            g = n * RR[r][i]
            c = sd * _side(r, slip)
            rows.append((r, sectorof[r], d, mon, n, RR[r][i], g, sd, c, g - c))
    daily = pd.DataFrame(rows, columns=["root", "sector", "date", "monday", "n", "ret_usd",
                                        "pnl_gross", "sides", "cost", "pnl_net"])
    daily = daily.sort_values(["date", "root"]).reset_index(drop=True)
    wk = daily.groupby("monday").agg(gross=("pnl_gross", "sum"), cost=("cost", "sum"),
                                     net=("pnl_net", "sum")).sort_index()
    pos = pd.DataFrame([dict(monday=m, root=r, n=v) for (r, m), v in POS.items()])
    if date_max is not None and len(daily):
        assert daily["date"].max() < date_max, "WINDOW VIOLATION in the independent path"
    return dict(daily=daily, weekly=wk,
                pos=pos.sort_values(["monday", "root"]).reset_index(drop=True))
