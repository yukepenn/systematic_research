"""R3 / G2_LIVE_HARDENING - measure the XM cross-market ALIGNMENT divergence.

QUESTION
--------
`WeeklyEdgeXMConflict_v2` reads `Closes[i][0]` for ES/RTY/YM inside the NQ (primary) bar
handler at the 09:31 anchor and the 09:45 decision.

  * The Python research object joins on the EXACT timestamp: it uses each secondary's own
    09:31 and 09:45 closes (export_xm_reference.py: `nq.join(d_..., how="left")`).
  * NT8's documented HISTORICAL processing order is: when several series share a timestamp,
    "your primary bars series will always be processed first, followed by the secondary bars
    series", and "secondary series data isn't available until the primary series finishes
    processing for that timestamp"
    (helpGuides/nt8/multi-time_frame__instruments.htm).
    => in a backtest the C# may see each secondary's PREVIOUS bar (09:30 / 09:44).
  * The same page states historical ordering "is NOT guaranteed to be the same sequence that
    these events occurred in real-time". In realtime each series' bar closes on ITS OWN first
    tick of the next minute, so whether ES's 09:45 bar has closed before NQ's 09:45 handler
    runs is a RACE, independently per secondary.

This script prices all three worlds on the full 2022-07 -> 2026-07 reference window:

  A  = SAME-BAR   (research object)              secondaries at 09:31 / 09:45
  B  = LAGGED     (NT8 documented historical)    secondaries at 09:30 / 09:44
  R  = RACE       (realtime)                     each secondary independently A or B, p=0.5

Outputs the desired_direction disagreement rate and the dollar consequence.

Read-only. Writes only into runs/G2_LIVE_HARDENING_20260830/out/.
"""
from __future__ import annotations

import os
import numpy as np
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
OUT = os.path.join(ROOT, "runs", "G2_LIVE_HARDENING_20260830", "out")
os.makedirs(OUT, exist_ok=True)

REF = os.path.join(ROOT, "research", "weekly_edge", "ninjascript", "reference",
                   "xm_reference_decisions.csv")
XM = {"ES": r"runs\SM1M_ES_SUBSTRATE\out\es_1m_2022_2026.parquet",
      "RTY": r"runs\SM1M_RTY_SUBSTRATE\out\rty_1m_2022_2026.parquet",
      "YM": r"runs\SM1M_YM_SUBSTRATE\out\ym_1m_2022_2026.parquet"}

SIG_LB, SIG_MIN = 60, 20
PV = 20.0            # NQ point value
COMM_RT = 4.36       # per contract round turn
SPREAD_RT = 12.50    # XM candidate modelled spread, CLAUDE.md sec.6

# minute-of-day keys, bar-END stamped ET
M_ANCH_A, M_DEC_A = 571, 585      # 09:31 / 09:45   (research)
M_ANCH_B, M_DEC_B = 570, 584      # 09:30 / 09:44   (one bar earlier)


def load_min(path):
    d = pd.read_parquet(os.path.join(ROOT, path), columns=["time", "close"])
    d["time"] = pd.to_datetime(d["time"])
    d["date"] = d["time"].dt.normalize()
    d["mod"] = d["time"].dt.hour * 60 + d["time"].dt.minute
    return d


def pivot(d, minutes):
    sub = d[d["mod"].isin(minutes)]
    p = sub.pivot_table(index="date", columns="mod", values="close", aggfunc="last")
    for m in minutes:
        if m not in p.columns:
            p[m] = np.nan
    return p


def main():
    ref = pd.read_csv(REF, parse_dates=["session_date"])
    ref = ref.sort_values("session_date").reset_index(drop=True)

    mins = [M_ANCH_A, M_DEC_A, M_ANCH_B, M_DEC_B]
    P = {}
    for k, path in XM.items():
        P[k] = pivot(load_min(path), mins)

    # calendar date of the RTH morning == the session_date used by the reference
    idx = ref["session_date"].dt.normalize()

    # per-market anchor/decision closes, both variants
    cols = {}
    for k in XM:
        pk = P[k].reindex(idx)
        cols[(k, "aA")] = pk[M_ANCH_A].to_numpy()
        cols[(k, "dA")] = pk[M_DEC_A].to_numpy()
        cols[(k, "aB")] = pk[M_ANCH_B].to_numpy()
        cols[(k, "dB")] = pk[M_DEC_B].to_numpy()

    n = len(ref)
    drive = ref["nq_drive"].to_numpy()
    ref_des = ref["desired_direction"].to_numpy().astype(int)
    ref_disq = ref["disqualified"].to_numpy().astype(bool)
    entry = ref["entry_px"].to_numpy()
    exit_nbo = ref["exit_px_open1546"].to_numpy()
    tradeable = np.isfinite(entry) & np.isfinite(exit_nbo)

    def logret(k, va):
        a = cols[(k, "a" + va)]
        d = cols[(k, "d" + va)]
        with np.errstate(invalid="ignore", divide="ignore"):
            r = np.log(d / a)
        r[(a <= 0) | (d <= 0)] = np.nan
        return r

    R = {(k, v): logret(k, v) for k in XM for v in ("A", "B")}

    def run_variant(pick):
        """pick[k] -> array of 'A'/'B' per session. Returns desired_direction array."""
        hist = {k: [] for k in XM}
        des = np.zeros(n, dtype=int)
        disq = np.zeros(n, dtype=bool)
        for s in range(n):
            rs, ok = {}, True
            for k in XM:
                r = R[(k, pick[k][s])][s]
                if not np.isfinite(r):
                    ok = False
                rs[k] = r
            if not ok:
                disq[s] = True
                continue
            acc, cnt = 0.0, 0
            for k in XM:
                h = hist[k]
                if len(h) >= SIG_MIN:
                    sg = float(np.std(h[-SIG_LB:], ddof=1))
                    if sg > 1e-12:
                        acc += rs[k] / sg
                        cnt += 1
                h.append(rs[k])
            if cnt == 0 or drive[s] == 0:
                continue
            comp = acc / cnt
            xs = np.sign(comp)
            if xs != 0 and xs != drive[s]:
                des[s] = int(drive[s])
        des = np.where(tradeable, des, 0)
        return des, disq

    allA = {k: np.array(["A"] * n) for k in XM}
    allB = {k: np.array(["B"] * n) for k in XM}
    desA, disqA = run_variant(allA)
    desB, disqB = run_variant(allB)

    def pnl(des):
        g = des * (exit_nbo - entry) * PV
        g = np.where(des != 0, g - COMM_RT - SPREAD_RT, 0.0)
        return np.nan_to_num(g)

    pA, pB = pnl(desA), pnl(desB)

    lines = []
    w = lines.append
    w("R3 XM CROSS-MARKET ALIGNMENT DIVERGENCE")
    w("=" * 72)
    w(f"sessions in reference        : {n}")
    w(f"window                       : {ref.session_date.min().date()} -> {ref.session_date.max().date()}")
    w("")
    w("-- reproduction check (variant A vs the committed reference) --")
    w(f"desired_direction agreement  : {(desA == ref_des).mean()*100:.4f}%  "
      f"({int((desA != ref_des).sum())} disagreements)")
    w(f"trades A / reference         : {int((desA != 0).sum())} / {int((ref_des != 0).sum())}")
    w("")
    w("-- A (same-bar, research) vs B (one-bar-lagged secondaries) --")
    w(f"trades A                     : {int((desA != 0).sum())}")
    w(f"trades B                     : {int((desB != 0).sum())}")
    dis = desA != desB
    w(f"sessions where desired differs: {int(dis.sum())}  ({dis.mean()*100:.2f}% of sessions)")
    both = (desA != 0) & (desB != 0)
    w(f"  both trade, SAME direction  : {int(((desA == desB) & both).sum())}")
    w(f"  both trade, OPPOSITE dir    : {int((both & (desA != desB)).sum())}")
    w(f"  A trades, B flat            : {int(((desA != 0) & (desB == 0)).sum())}")
    w(f"  B trades, A flat            : {int(((desB != 0) & (desA == 0)).sum())}")
    w(f"disqualified A / B            : {int(disqA.sum())} / {int(disqB.sum())}")
    w("")
    w(f"net $ variant A               : {pA.sum():,.0f}")
    w(f"net $ variant B               : {pB.sum():,.0f}")
    w(f"delta (B - A)                 : {pB.sum()-pA.sum():,.0f}  "
      f"({(pB.sum()-pA.sum())/max(abs(pA.sum()),1)*100:+.1f}% of A)")
    w(f"$ at risk on divergent sessions (|A|+|B|): "
      f"{np.abs(pA[dis]).sum()+np.abs(pB[dis]).sum():,.0f}")
    w("")

    # ---- R: the realtime race, each secondary independently A or B ----
    rng = np.random.default_rng(20260830)
    NDRAW = 200
    diff_rate = np.zeros(NDRAW)
    nets = np.zeros(NDRAW)
    ntr = np.zeros(NDRAW)
    for d_ in range(NDRAW):
        pick = {k: np.where(rng.random(n) < 0.5, "A", "B") for k in XM}
        desR, _ = run_variant(pick)
        diff_rate[d_] = (desR != desA).mean()
        nets[d_] = pnl(desR).sum()
        ntr[d_] = (desR != 0).sum()
    w("-- R: realtime RACE (each secondary independently same-bar/lagged, p=0.5) --")
    w(f"draws                         : {NDRAW}")
    w(f"sessions differing from A     : mean {diff_rate.mean()*100:.2f}%  "
      f"[p5 {np.percentile(diff_rate,5)*100:.2f}%, p95 {np.percentile(diff_rate,95)*100:.2f}%]")
    w(f"  -> per 250-session year     : {diff_rate.mean()*250:.1f} sessions")
    w(f"trades                        : mean {ntr.mean():.1f} "
      f"[{ntr.min():.0f}, {ntr.max():.0f}]   (A = {int((desA!=0).sum())})")
    w(f"net $                         : mean {nets.mean():,.0f} "
      f"[p5 {np.percentile(nets,5):,.0f}, p95 {np.percentile(nets,95):,.0f}]   "
      f"(A = {pA.sum():,.0f})")
    w(f"spread p95-p5 as % of A net   : "
      f"{(np.percentile(nets,95)-np.percentile(nets,5))/max(abs(pA.sum()),1)*100:.1f}%")
    w("")

    # ---- how often is a secondary bar simply MISSING at the decision minute? ----
    w("-- empty-minute frequency at the two decision minutes (per market) --")
    for k in XM:
        pk = P[k].reindex(idx)
        for m, lab in ((M_DEC_A, "09:45"), (M_DEC_B, "09:44"),
                       (M_ANCH_A, "09:31"), (M_ANCH_B, "09:30")):
            miss = (~np.isfinite(pk[m].to_numpy())).sum()
            w(f"  {k:<4} {lab}: missing on {miss:4d} / {n} sessions ({miss/n*100:.2f}%)")
    w("")

    txt = "\n".join(lines)
    print(txt)
    with open(os.path.join(OUT, "xm_alignment.txt"), "w", encoding="utf-8") as f:
        f.write(txt + "\n")

    pd.DataFrame({"session_date": ref["session_date"], "nq_drive": drive,
                  "desired_ref": ref_des, "desired_A": desA, "desired_B": desB,
                  "pnl_A": pA, "pnl_B": pB}).to_csv(
        os.path.join(OUT, "xm_alignment_sessions.csv"), index=False)


if __name__ == "__main__":
    main()
