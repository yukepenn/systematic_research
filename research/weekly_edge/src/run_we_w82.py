"""WE_W82 - what does a round turn ACTUALLY cost? The first quote-level fill audit.

Spec: runs/WE_W82_FILLAUDIT/spec.yaml, committed before this ran.

Every number in 82 waves is net of $4.36/RT with NO spread cost, and the "stress line" adds
$10/RT on the stated assumption of "2 NQ ticks". That assumption has never been checked against a
quote, and P1 takes 59.7 % of its net overnight where the spread is widest.
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
from run_we_w01 import ROOT, PV, COMM_RT, STRESS_RT                      # noqa: E402
from run_we_w17 import load_deep                                         # noqa: E402
from run_we_w19 import MEMBERS, QS                                       # noqa: E402
from run_we_w26 import fills_daily                                       # noqa: E402
from run_we_w35 import fills_qexit                                       # noqa: E402
from run_we_w37 import causal_score                                      # noqa: E402
from run_we_w39 import WIN                                               # noqa: E402
from we_fastctx import fast_build_context                                # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W82_FILLAUDIT", "out")
os.makedirs(OUT, exist_ok=True)
W76OUT = os.path.join(ROOT, "runs", "WE_W76_FORWARD2026", "out")
G1S = os.path.join(ROOT, "research", "scalping_lab", "substrate", "grid1s", "NQ")
L13 = [6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30]
TICK = 0.25
A = np.datetime64("2022-07-01")
B = np.datetime64("2026-08-01")


def main():
    t0 = _time.time()
    out = open(os.path.join(OUT, "fillaudit.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out); out.flush()

    # ---------------------------------------------------------------- 1-second quote grid
    files = sorted(glob.glob(os.path.join(G1S, "*.parquet")))
    parts = []
    skipped = []
    for p in files:
        d = pd.read_parquet(p, columns=["time", "bid", "ask", "last", "spread_t",
                                        "sflow", "bid_upd", "ask_upd", "trades", "vol"])
        d["time"] = pd.to_datetime(d["time"])
        if float((d["bid"] > 0).mean()) < 0.5:
            skipped.append(os.path.basename(p)); continue
        parts.append(d)
    Q = pd.concat(parts, ignore_index=True).sort_values("time").reset_index(drop=True)
    Q = Q[(Q["bid"] > 0) & (Q["ask"] > 0)]
    P_(f"=== quote grid: {len(files)} files, {len(skipped)} excluded for missing quotes "
       f"({', '.join(skipped)}), {len(Q):,} second-bars with a two-sided quote")
    P_(f"    {Q['time'].min()} -> {Q['time'].max()} [{_time.time()-t0:.0f}s]")
    Q["sp_pts"] = Q["ask"] - Q["bid"]
    Q["sp_tk"] = Q["sp_pts"] / TICK
    hm = Q["time"].dt.hour * 60 + Q["time"].dt.minute
    Q["mod"] = hm

    def seg(m):
        return np.where((m >= 570) & (m < 960), "RTH 09:30-16:00",
                        np.where((m >= 960) & (m < 1020), "POST 16:00-17:00",
                                 "OVERNIGHT 18:00-09:29"))
    Q["seg"] = seg(Q["mod"].to_numpy())
    P_(f"\n=== PHASE 1a: the raw spread, by session segment (2025-08 -> 2026-05) ===")
    P_(f"{'segment':<24}{'seconds':>12}{'median tk':>11}{'mean tk':>10}{'p90 tk':>9}"
       f"{'median $/RT':>14}")
    for s in ("OVERNIGHT 18:00-09:29", "RTH 09:30-16:00", "POST 16:00-17:00"):
        q = Q[Q["seg"] == s]
        if not len(q):
            continue
        P_(f"{s:<24}{len(q):>12,}{q['sp_tk'].median():>11.2f}{q['sp_tk'].mean():>10.2f}"
           f"{q['sp_tk'].quantile(0.9):>9.2f}{q['sp_tk'].median()*TICK*PV:>14,.2f}")
    P_(f"{'ALL':<24}{len(Q):>12,}{Q['sp_tk'].median():>11.2f}{Q['sp_tk'].mean():>10.2f}"
       f"{Q['sp_tk'].quantile(0.9):>9.2f}{Q['sp_tk'].median()*TICK*PV:>14,.2f}")

    prof = Q.groupby("mod")["sp_tk"].median()
    prof.to_csv(os.path.join(OUT, "spread_by_minute.csv"))

    # ---------------------------------------------------------------- P1's fills
    D = load_deep("2022-01-01", "2026-07-31 17:00", extend=True)
    W1.DEV_END = pd.Timestamp("2026-07-31").date()
    n, tarr, sid = D["n"], D["t"], D["sid"]
    X = fast_build_context(D)
    z = np.load(os.path.join(W76OUT, "mem_ext.npz"))
    mem, bmom, tilt = z["mem"], z["bmom"], z["tilt"]
    fb, sess_end = D["fb"], D["sess_end"]
    blocked = tarr >= sess_end[sid] - np.timedelta64(30 * 60, "s")
    flatm = tarr >= sess_end[sid] - np.timedelta64(21 * 60, "s")
    idx_l13 = {v: k for k, v in enumerate(L13)}

    def ra(x):
        return np.where(x >= 0, np.floor(x + 0.5), np.ceil(x - 0.5))

    def hyst(M):
        tgt = np.zeros(n, np.int8)
        for i in range(n):
            p = 0 if (i == 0 or fb[i]) else tgt[i - 1]
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
            tgt[i] = g
        return tgt

    TG = {}
    for name, vols in MEMBERS.items():
        cols = [idx_l13[v] for v in vols]
        s_ = mem[:, cols].sum(axis=1).astype(np.int32)
        T = np.clip(ra(s_ / float(len(cols)) * 10.0), -10, 10)
        ag = (np.sign(s_) == tilt) & (s_ != 0) & (tilt != 0)
        Tp = np.clip(ra(T * np.where(ag, 1.25, 1.0) * 0.9026), -13, 13)
        TG[name] = hyst(0.7086 * Tp + 2.83 * bmom.astype(float))
    vs = []
    for name in MEMBERS:
        tg = TG[name]
        for q_ in QS:
            okv = np.ones(n, bool) if q_ is None else ((X["norm"] <= 0) | (X["ratio"] >= q_))
            for dg in (True, False):
                vs.append(np.where((tg > 0) & (okv & (X["dL"] if dg else True)), 1,
                                   0).astype(np.int8))
    pos = (np.vstack(vs).mean(axis=0) >= 0.5).astype(np.int8)
    del vs
    base = fills_daily(D, pos, halt=1300, target=1000)

    def i_of(ts):
        return int(min(np.searchsorted(tarr, np.datetime64(ts)), n - 1))

    ee = np.array([i_of(x["et"]) for x in base if A <= np.datetime64(x["et"]) < B])
    sc, _ = causal_score(X, ee, window=WIN)
    trl = [x for x in fills_qexit(D, pos, np.where(sc >= 3, 2, 1).astype(np.int8), sc)
           if A <= np.datetime64(x["et"]) < B]
    P_(f"\n    P1: {len(trl):,} trades on the extended window [{_time.time()-t0:.0f}s]")

    F = pd.DataFrame([dict(t=pd.Timestamp(x["et"]), side=+1, u=x["u"]) for x in trl]
                     + [dict(t=pd.Timestamp(x["xt"]), side=-1, u=x["u"]) for x in trl])
    F["mod"] = F["t"].dt.hour * 60 + F["t"].dt.minute
    F["seg"] = seg(F["mod"].to_numpy())
    P_(f"\n=== PHASE 0: where P1's {len(F):,} fills sit in the day ===")
    P_(f"{'segment':<24}{'fills':>9}{'share':>9}")
    for s in ("OVERNIGHT 18:00-09:29", "RTH 09:30-16:00", "POST 16:00-17:00"):
        k = int((F["seg"] == s).sum())
        P_(f"{s:<24}{k:>9,}{100*k/len(F):>8.1f}%")

    # ---------------------------------------------------------------- weighted estimate
    P_(f"\n=== PHASE 1b: THE WEIGHTED ESTIMATE (the one the spec says counts) ===")
    P_("    P1's own fill time-of-day distribution x the spread profile from all 3.9 M seconds.")
    w = F["mod"].value_counts(normalize=True)
    common = prof.index.intersection(w.index)
    wt = w.loc[common] / w.loc[common].sum()
    tk = float((prof.loc[common] * wt).sum())
    P_(f"\n    spread at P1's trading times = {tk:.2f} ticks = ${tk*TICK*PV:.2f} per round turn")
    P_(f"    (a round turn crosses once: buy the ask, sell the bid)")
    P_(f"    campaign assumptions: headline $0.00, C1 stress line $10.00 (= 2 ticks)")
    for s in ("OVERNIGHT 18:00-09:29", "RTH 09:30-16:00"):
        ws = F[F["seg"] == s]["mod"].value_counts(normalize=True)
        cc = prof.index.intersection(ws.index)
        if not len(cc):
            continue
        tks = float((prof.loc[cc] * (ws.loc[cc] / ws.loc[cc].sum())).sum())
        P_(f"       {s:<24} {tks:>5.2f} ticks = ${tks*TICK*PV:>6.2f}/RT")

    # ---------------------------------------------------------------- direct estimate
    P_(f"\n=== PHASE 2: THE DIRECT MEASUREMENT at overlapping fills ===")
    qi = Q.set_index("time")
    ft = F["t"] - pd.Timedelta(seconds=60)          # bar end-stamp T -> its open at T-60s
    hit = qi.reindex(ft)
    ok = hit["bid"].notna().to_numpy()
    P_(f"    {int(ok.sum()):,} of {len(F):,} fills fall inside the 47 quote sessions "
       f"({100*ok.mean():.1f} %)")
    if ok.sum() >= 30:
        opx = np.array([D["o"][i_of(np.datetime64(t))] for t in F["t"]])
        sub = pd.DataFrame(dict(bid=hit["bid"].to_numpy(), ask=hit["ask"].to_numpy(),
                                sp=(hit["ask"] - hit["bid"]).to_numpy(),
                                side=F["side"].to_numpy(), op=opx))[ok]
        outside = float(((sub["op"] > sub["ask"]) | (sub["op"] < sub["bid"])).mean())
        P_(f"    the simulated open sits OUTSIDE the quote on {100*outside:.1f} % of them "
           f"(minute grid vs second grid disagreement - disclosed, not averaged away)")
        ins = sub[(sub["op"] <= sub["ask"]) & (sub["op"] >= sub["bid"])]
        cost = np.where(ins["side"] > 0, ins["ask"] - ins["op"], ins["op"] - ins["bid"])
        P_(f"    on the {len(ins):,} fills where they agree, the cost the simulation OMITS is")
        P_(f"       median {np.median(cost)/TICK:.2f} ticks = ${np.median(cost)*PV:.2f} per SIDE")
        P_(f"       mean   {cost.mean()/TICK:.2f} ticks = ${cost.mean()*PV:.2f} per side")
        P_(f"       -> ${2*cost.mean()*PV:.2f} per ROUND TURN (both sides)")
        P_(f"    direct median spread at those fills: {ins['sp'].median()/TICK:.2f} ticks")
        pd.DataFrame(dict(cost_pts=cost)).to_csv(os.path.join(OUT, "direct_cost.csv"),
                                                 index=False)
        direct_rt = float(2 * cost.mean() * PV)
    else:
        P_("    too few overlapping fills for a direct estimate.")
        direct_rt = np.nan

    # ---------------------------------------------------------------- repricing
    ALLIN = tk * TICK * PV
    P_(f"\n{'='*118}\n=== PHASE 3: P1 RE-QUOTED AT THE MEASURED COST")
    P_(f"{'='*118}")
    md = pd.read_csv(os.path.join(W76OUT, "streams_extended.csv"))
    md["date"] = pd.to_datetime(md["date"])
    iso = md["date"].dt.isocalendar()
    wk = (iso["year"].astype(str) + "-W" + iso["week"].astype(str).str.zfill(2)).to_numpy()
    NWk = len(set(wk))
    ntr_units = sum(x["u"] for x in trl) * 2 / 2          # round turns weighted by size
    rt_per_week = sum(x["u"] for x in trl) / NWk
    P_(f"    P1: {len(trl):,} trades, {sum(x['u'] for x in trl):,} contract round turns, "
       f"{rt_per_week:.2f} per week")
    P_(f"\n{'cost line':<34}{'$/RT extra':>12}{'$/week':>10}"
       f"{'full-window wk$':>18}{'trailing-12m wk$':>19}{'2026 wk$':>12}")
    ds = md["date"]
    per = {"full": np.ones(len(md), bool),
           "t12": (ds >= pd.Timestamp("2025-08-01")).to_numpy(),
           "y26": (ds.dt.year == 2026).to_numpy()}
    base_wk = {}
    for k, m in per.items():
        v = pd.Series(md["P1"].to_numpy()[m]).groupby(wk[m]).sum()
        base_wk[k] = (float(v.mean()), len(v))
    for lab, extra in (("headline (commission only)", 0.0),
                       ("C1 stress line (assumed 2 tk)", STRESS_RT),
                       (f"MEASURED ({tk:.2f} ticks)", ALLIN)):
        cw = extra * rt_per_week
        P_(f"{lab:<34}{extra:>12,.2f}{cw:>10,.0f}"
           f"{base_wk['full'][0]-cw:>18,.0f}{base_wk['t12'][0]-cw:>19,.0f}"
           f"{base_wk['y26'][0]-cw:>12,.0f}")
    P_(f"\n    annualised at 1 unit: full {52*(base_wk['full'][0]-ALLIN*rt_per_week):,.0f}  |  "
       f"trailing-12m {52*(base_wk['t12'][0]-ALLIN*rt_per_week):,.0f}  |  "
       f"2026 {52*(base_wk['y26'][0]-ALLIN*rt_per_week):,.0f}")

    # ---------------------------------------------------------------- power test
    P_(f"\n{'='*118}\n=== PHASE 4: MICROSTRUCTURE PREDICTIVE POWER")
    P_(f"{'='*118}")
    ent = pd.DataFrame([dict(t=pd.Timestamp(x["et"]), pnl=x["pnl"] / max(x["u"], 1))
                        for x in trl])
    et2 = ent["t"] - pd.Timedelta(seconds=60)
    hh = qi.reindex(et2)
    m2 = hh["bid"].notna().to_numpy()
    N = int(m2.sum())
    P_(f"    POWER FIRST (method rule 25): {N} of {len(ent):,} entries have quote data.")
    if N < 10:
        P_("    -> nothing to test.")
    else:
        det = 2.0 / np.sqrt(N)
        P_(f"    smallest |Spearman| detectable at t = 2 is 2/sqrt({N}) = {det:.3f}")
        P_(f"    W55's ceiling across 16 minute-level features was |rho| < 0.11.")
        P_(f"    -> this test is {'UNDERPOWERED for effects of the size this problem produces' if det > 0.11 else 'adequately powered'}")
        e = ent[m2].copy()
        for c in ("bid", "ask", "sflow", "bid_upd", "ask_upd", "trades", "vol"):
            e[c] = hh[c].to_numpy()[m2]
        e["spread"] = (e["ask"] - e["bid"]) / TICK
        e["qimb"] = (e["bid_upd"] - e["ask_upd"]) / np.maximum(e["bid_upd"] + e["ask_upd"], 1)
        e["updint"] = e["bid_upd"] + e["ask_upd"]
        P_(f"\n{'feature':<14}{'Spearman rho':>15}{'|t|':>8}{'':>12}")
        rows = []
        for c in ("spread", "sflow", "qimb", "updint", "trades", "vol"):
            r = float(e[[c, "pnl"]].corr(method="spearman").iloc[0, 1])
            tv = abs(r) * np.sqrt(max(N - 2, 1)) / np.sqrt(max(1 - r * r, 1e-9))
            P_(f"{c:<14}{r:>+15.3f}{tv:>8.2f}"
               f"{('' if tv < 2 else '  <- |t|>2'):>12}")
            rows.append(dict(feature=c, rho=r, t=tv, n=N))
        pd.DataFrame(rows).to_csv(os.path.join(OUT, "power.csv"), index=False)
        P_(f"\n    Reported as DESCRIPTIVE ONLY where the detectable size exceeds the effects")
        P_(f"    this problem is known to produce. 47 sessions cannot settle this question, and")
        P_(f"    the useful output of this wave is the fill cost above, not this table.")

    P_(f"\n=== STATUS: measurement. [{_time.time()-t0:.0f}s] ===")
    out.close()
    print(f"done [{_time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
