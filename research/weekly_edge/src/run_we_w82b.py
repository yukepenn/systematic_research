"""WE_W82 amendment 2 - the fill audit, repaired on four counts found by the audit.

Spec: runs/WE_W82_FILLAUDIT/amendment_2.yaml, committed before this ran.

DEFECT 15  the corrected direct estimate ($24/RT) was run in an UNCOMMITTED shell heredoc.
           `out/direct_cost.csv` is 10 bytes - header only. The number existed only in prose.
           This file IS the artifact; it commits the code and writes the output.
DEFECT 18  four sessions carry frozen forward-filled feeds that the `(bid>0).mean() >= 0.5`
           filter cannot see (a dead feed scores 1.00). Added a frozen-run filter.
DEFECT 19b "one spread per round turn" over-charges THIS object: it buys after up-bars, and the
           minute's open sits closer to the ask after an up-minute, so the simulated fill already
           captures part of the spread. Measured and applied.
DEFECT 19a the $14.65 is measured on 45 sessions at NQ 21,000-24,000 and was generalised to
           sixteen years at NQ 1,600-16,000. Scope is now stated in the output itself.
"""
from __future__ import annotations

import glob
import os
import sys
import time as _time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_we_w01 as W1                                                  # noqa: E402
from run_we_w01 import ROOT, PV, COMM_RT                                 # noqa: E402
from run_we_w17 import load_deep                                         # noqa: E402
from run_we_w19 import MEMBERS, QS                                       # noqa: E402
from run_we_w26 import fills_daily                                       # noqa: E402
from run_we_w35 import fills_qexit                                       # noqa: E402
from run_we_w37 import causal_score                                      # noqa: E402
from run_we_w39 import WIN                                               # noqa: E402
from we_fastctx import fast_build_context                                # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W82_FILLAUDIT", "out")
W76OUT = os.path.join(ROOT, "runs", "WE_W76_FORWARD2026", "out")
G1S = os.path.join(ROOT, "research", "scalping_lab", "substrate", "grid1s", "NQ")
L13 = [6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30]
TICK = 0.25
A = np.datetime64("2022-07-01")
B = np.datetime64("2026-08-01")
FROZEN_S = 60          # a quote unchanged for > 60 consecutive seconds is a dead feed


def main():
    t0 = _time.time()
    out = open(os.path.join(OUT, "fillaudit_b.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out); out.flush()

    # ---------------------------------------------------------------- quotes, with the filter
    rows, frozen_rep = [], []
    for p in sorted(glob.glob(os.path.join(G1S, "*.parquet"))):
        q = pd.read_parquet(p, columns=["time", "bid", "ask", "last"])
        q["time"] = pd.to_datetime(q["time"])
        q = q[(q["bid"] > 0) & (q["ask"] > 0)]
        if len(q) < 1000:
            continue
        key = q["bid"].astype(str) + "|" + q["ask"].astype(str)
        grp = (key != key.shift()).cumsum()
        runlen = grp.map(grp.value_counts())
        q["frozen"] = runlen > FROZEN_S
        frozen_rep.append(dict(f=os.path.basename(p), n=len(q),
                               frozen_pct=100 * float(q["frozen"].mean()),
                               longest=int(runlen.max())))
        rows.append(q)
    Q = pd.concat(rows, ignore_index=True).sort_values("time").reset_index(drop=True)
    FR = pd.DataFrame(frozen_rep).sort_values("frozen_pct", ascending=False)
    FR.to_csv(os.path.join(OUT, "frozen_sessions.csv"), index=False)
    P_(f"=== DEFECT 18: FROZEN-FEED FILTER (a forward-filled dead quote passes `bid>0`) ===")
    P_(f"{'session':<24}{'seconds':>10}{'% frozen >60s':>15}{'longest run (s)':>18}")
    for _, r in FR.head(6).iterrows():
        P_(f"{r['f']:<24}{r['n']:>10,}{r['frozen_pct']:>14.1f}%{r['longest']:>18,}")
    P_(f"\n   overall: {100*float(Q['frozen'].mean()):.1f} % of {len(Q):,} second-quotes sit in "
       f"runs longer than {FROZEN_S}s")
    QC = Q[~Q["frozen"]].copy()
    P_(f"   after filtering: {len(QC):,} clean second-quotes "
       f"({QC['time'].min()} -> {QC['time'].max()})")

    for lab, df in (("UNFILTERED (as published)", Q), ("FILTERED (clean)", QC)):
        sp = (df["ask"] - df["bid"]) / TICK
        hm = df["time"].dt.hour * 60 + df["time"].dt.minute
        rth = (hm >= 570) & (hm < 960)
        P_(f"\n   {lab}: ALL median {sp.median():.2f} tk, mean {sp.mean():.3f}, "
           f"p90 {sp.quantile(.9):.2f}  |  RTH median {sp[rth].median():.2f}, "
           f"p90 {sp[rth].quantile(.9):.2f}")

    # ---------------------------------------------------------------- the object's fills
    D = load_deep("2025-07-01", "2026-07-31 17:00", extend=True)
    W1.DEV_END = pd.Timestamp("2026-07-31").date()
    n, tarr, sid = D["n"], D["t"], D["sid"]
    X = fast_build_context(D)
    from run_we_w01 import sm14_1m
    _, mem, bmom, tilt = sm14_1m(D, 460, volmults=L13, return_members=True)
    fb, se_ = D["fb"], D["sess_end"]
    blocked = tarr >= se_[sid] - np.timedelta64(30 * 60, "s")
    flatm = tarr >= se_[sid] - np.timedelta64(21 * 60, "s")
    im = {v: k for k, v in enumerate(L13)}

    def ra(x):
        return np.where(x >= 0, np.floor(x + 0.5), np.ceil(x - 0.5))

    def hyst(M):
        t_ = np.zeros(n, np.int8)
        for i in range(n):
            p = 0 if (i == 0 or fb[i]) else t_[i - 1]
            g = p
            if flatm[i]:
                g = 0
            elif p == 0:
                if not blocked[i]:
                    g = 1 if M[i] >= 3.0 else (-1 if M[i] <= -3.0 else p)
            elif p > 0:
                g = -1 if (M[i] <= -3.0 and not blocked[i]) else (0 if M[i] <= 1.0 else p)
            else:
                g = 1 if (M[i] >= 3.0 and not blocked[i]) else (0 if M[i] >= -1.0 else p)
            t_[i] = g
        return t_

    vs = []
    for name, vols in MEMBERS.items():
        cols = [im[v] for v in vols]
        s_ = mem[:, cols].sum(axis=1).astype(np.int32)
        T = np.clip(ra(s_ / float(len(cols)) * 10.0), -10, 10)
        ag = (np.sign(s_) == tilt) & (s_ != 0) & (tilt != 0)
        Tp = np.clip(ra(T * np.where(ag, 1.25, 1.0) * 0.9026), -13, 13)
        tg = hyst(0.7086 * Tp + 2.83 * bmom.astype(float))
        for q_ in QS:
            okv = np.ones(n, bool) if q_ is None else ((X["norm"] <= 0) | (X["ratio"] >= q_))
            for dg in (True, False):
                vs.append(np.where((tg > 0) & (okv & (X["dL"] if dg else True)), 1,
                                   0).astype(np.int8))
    pos = (np.vstack(vs).mean(axis=0) >= 0.5).astype(np.int8)
    del vs

    def i_of(ts):
        return int(min(np.searchsorted(tarr, np.datetime64(ts)), n - 1))

    base = fills_daily(D, pos, halt=1300, target=1000)
    ee = np.array([i_of(x["et"]) for x in base if A <= np.datetime64(x["et"]) < B])
    sc, _ = causal_score(X, ee, window=WIN)
    trl = [x for x in fills_qexit(D, pos, np.where(sc >= 3, 2, 1).astype(np.int8), sc)
           if A <= np.datetime64(x["et"]) < B]
    F = pd.DataFrame([dict(t=pd.Timestamp(x["et"]), side=+1) for x in trl]
                     + [dict(t=pd.Timestamp(x["xt"]), side=-1) for x in trl])
    P_(f"\n   P1: {len(trl):,} trades in the quote era [{_time.time()-t0:.0f}s]")

    # ---------------------------------------------------------------- DEFECT 15: the artifact
    P_(f"\n{'='*112}\n=== DEFECT 15: the DIRECT estimate, with code and output committed this time")
    P_(f"{'='*112}")
    P_("   The 1-minute substrate is BACK-ADJUSTED; the 1-second grid is RAW FRONT MONTH. The")
    P_("   per-session offset is removed before any level is compared. Both grids are bar-END")
    P_("   stamped, so a bar ending T has its open in the second at T-59s.")
    mopen = pd.Series(D["o"], index=pd.to_datetime(D["t"]))
    mclose = pd.Series(D["c"], index=pd.to_datetime(D["t"]))
    parts = []
    for p in sorted(glob.glob(os.path.join(G1S, "*.parquet"))):
        q = pd.read_parquet(p, columns=["time", "bid", "ask", "last"])
        q["time"] = pd.to_datetime(q["time"])
        q = q[(q["bid"] > 0) & (q["ask"] > 0)]
        if len(q) < 1000:
            continue
        key = q["bid"].astype(str) + "|" + q["ask"].astype(str)
        grp = (key != key.shift()).cumsum()
        q = q[grp.map(grp.value_counts()) <= FROZEN_S]
        if len(q) < 1000:
            continue
        off = float(np.nanmedian(mclose.reindex(q["time"]).to_numpy() - q["last"].to_numpy()))
        if not np.isfinite(off):
            continue
        qi = q.set_index("time")
        m = (F["t"] >= q["time"].min()) & (F["t"] <= q["time"].max())
        if not m.any():
            continue
        sub = F[m].copy()
        hit = qi.reindex(sub["t"] - pd.Timedelta(seconds=59))
        ok = hit["bid"].notna().to_numpy()
        if not ok.any():
            continue
        sub = sub[ok]
        parts.append(pd.DataFrame(dict(
            t=sub["t"].to_numpy(), side=sub["side"].to_numpy(),
            bid=hit["bid"].to_numpy()[ok] + off, ask=hit["ask"].to_numpy()[ok] + off,
            op=mopen.reindex(sub["t"]).to_numpy())))
    S = pd.concat(parts, ignore_index=True).dropna()
    S["sp"] = S["ask"] - S["bid"]
    S["inside"] = (S["op"] <= S["ask"] + 1e-9) & (S["op"] >= S["bid"] - 1e-9)
    S["loc"] = (S["op"] - S["bid"]) / np.maximum(S["sp"], 1e-9)
    S.to_csv(os.path.join(OUT, "direct_cost.csv"), index=False)
    ins = S[S["inside"]]
    P_(f"   {len(S):,} overlapping fills; open INSIDE the quote on {100*S['inside'].mean():.1f} %")
    if len(ins) >= 20:
        cost = np.where(ins["side"] > 0, ins["ask"] - ins["op"], ins["op"] - ins["bid"])
        P_(f"   on those {len(ins):,}: median spread {ins['sp'].median()/TICK:.2f} tk;")
        P_(f"      omitted cost per SIDE  median {np.median(cost)/TICK:.2f} tk "
           f"(${np.median(cost)*PV:.2f}), mean {cost.mean()/TICK:.2f} tk (${cost.mean()*PV:.2f})")
        P_(f"      -> ${2*cost.mean()*PV:.2f} per ROUND TURN")
        P_(f"   THIS IS A SELECTED SUBSAMPLE ({len(ins)} of {len(S)}) and is the pessimistic bound,")
        P_(f"   not the headline.")

    # ---------------------------------------------------------------- DEFECT 19b: direction
    P_(f"\n{'='*112}\n=== DEFECT 19b: does 'one full spread per round turn' over-charge THIS object?")
    P_(f"{'='*112}")
    P_("   If the minute's OPEN sits closer to the ask after an up-minute, and the object buys")
    P_("   after up-minutes, then the simulated fill already carries part of the spread and")
    P_("   charging a full spread double-counts.")
    prevc = mclose.shift(1)
    S["upbar"] = (mopen.reindex(S["t"]).to_numpy() > prevc.reindex(S["t"]).to_numpy())
    entries = S[S["side"] > 0]
    P_(f"\n   P1 enters after an UP minute on {100*float(entries['upbar'].mean()):.1f} % of entries")
    for lab, msk in (("after an UP minute", ins["op"].index.isin(
                        ins.index[ins.index.isin(S.index[S['upbar'].fillna(False)])])),):
        pass
    ii = ins.join(S[["upbar"]], rsuffix="_x") if "upbar" not in ins.columns else ins
    up = ii[ii["upbar"].fillna(False)]; dn = ii[~ii["upbar"].fillna(True)]
    if len(up) >= 10 and len(dn) >= 10:
        P_(f"   open's location in the quote (0 = bid, 1 = ask):")
        P_(f"      after an UP minute   {up['loc'].mean():.3f}   (n = {len(up):,})")
        P_(f"      after a DOWN minute  {dn['loc'].mean():.3f}   (n = {len(dn):,})")
        pu = float(entries["upbar"].mean())
        eff = pu * (1 - up["loc"].mean()) + (1 - pu) * (1 - dn["loc"].mean()) + 0.5
        P_(f"\n   direction-weighted spreads charged per round turn: {eff:.3f}")
        P_(f"   -> {eff*ins['sp'].median()/TICK:.3f} ticks = "
           f"${eff*ins['sp'].median()*PV:.2f}/RT at the measured median spread")
    else:
        P_("   too few classified fills to split by direction.")

    # ---------------------------------------------------------------- DEFECT 19a: scope
    P_(f"\n{'='*112}\n=== DEFECT 19a: SCOPE. What the $14.65 does and does not cover.")
    P_(f"{'='*112}")
    px = QC["last"]
    P_(f"   quote sample: {QC['time'].min().date()} -> {QC['time'].max().date()}, "
       f"NQ {px.min():,.0f} - {px.max():,.0f}")
    cov = len(S) / (2 * 2376)
    P_(f"   it covers {len(S):,} of P1's ~4,752 fills = {100*cov:.1f} % of its contract "
       f"round turns, ALL of them at 2025-26 price levels.")
    P_(f"   The repository holds NO NQ quote sample below {px.min():,.0f}. Applying a")
    P_(f"   POINT-denominated spread to 2006-2021 (NQ 1,600-16,000) is unsupported and every")
    P_(f"   deep-history re-quote made with it is WITHDRAWN pending an era-appropriate estimate.")

    # ---------------------------------------------------------------- DEFECT 16
    P_(f"\n{'='*112}\n=== DEFECT 16: stress must be charged PER CONTRACT, not per trade")
    P_(f"{'='*112}")
    net, st10 = 79076.48, -36493.52
    ctr = (net - st10) / 10.0
    P_(f"   W80 deep: net ${net:,.0f}, stress-net ${st10:,.0f} at $10/RT")
    P_(f"   -> implied {ctr:,.0f} CONTRACT round turns (W80 reported 9,557 TRADES)")
    P_(f"   my W82 report's '-$81,000' used 4.65 x 9,557 TRADES = ${net+st10-4.65*9557:,.0f} "
       f"- WRONG BASIS")
    P_(f"   correct at $14.65/RT per contract: ${net - 14.65*ctr:,.0f}")
    P_(f"   (and this figure is itself WITHDRAWN under defect 19a - wrong era for the estimate)")
    P_(f"\n=== STATUS: corrections. [{_time.time()-t0:.0f}s] ===")
    out.close()
    print(f"done [{_time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
