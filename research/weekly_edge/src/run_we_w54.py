"""WE_W54 MASK ANOMALY (spec preregistered): why does a null beat the object it is a null for?

W51d's N1 - the E4 mask rolled by a random offset inside each session - averaged 15.59
pts/session and MAR 17.80 against the incumbent's 14.86 / 14.86, on 92 % of the exposure. That
is the only thing in three waves that improved production and the drawdown distribution at the
same time, and it has no mechanism.

Six prior measurements argue the mechanism is NOT "a delay buys a better price" (R2V1, R2B,
W31, W42, the scalping lab's passive fills, and the standing bar in RESEARCH_FRONTIER.md:23).
So this wave measures the three candidate mechanisms directly instead of writing arms:
  H1 duration selection - the mask deletes SHORT stretches and short trades lose money
  H2 sizing-pool interaction - thinning changes the trailing-250-entry quantiles
  H3 price / delay - matched flips genuinely get a better price
Nothing is adoptable here. The deliverable is a mechanism sentence and the next agenda.
"""
from __future__ import annotations

import os
import sys
import time as _time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from run_we_w01 import ROOT, PV                                          # noqa: E402
from run_we_w26 import fills_daily                                       # noqa: E402
from run_we_w35 import fills_qexit                                       # noqa: E402
from run_we_w37 import causal_score                                      # noqa: E402
from run_we_w38 import targets, vote                                     # noqa: E402
from run_we_w39 import WIN                                               # noqa: E402
from run_we_w51 import session_frames, A, B                              # noqa: E402
from run_we_w51c import setup, pos_range_feature, entry_only, dd_profile  # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W54_MASKANOMALY", "out")
os.makedirs(OUT, exist_ok=True)
NDRAW = 50
SEED = 20260851           # the seed W51d used, so these are literally its first 50 N1 draws


def main():
    t0 = _time.time()
    D, X, TG, st, en = setup()
    n, tarr, sid = D["n"], D["t"], D["sid"]
    o = D["o"]
    wkmap = {s: D["wk"][s] for s in range(D["n_sess"])}
    out = open(os.path.join(OUT, "maskanomaly.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out)

    def i_of(ts):
        return int(min(np.searchsorted(tarr, np.datetime64(ts)), n - 1))

    sess_in = np.array([s for s in range(D["n_sess"]) if A <= tarr[st[s]] < B])
    NS = len(sess_in)
    in_win = np.zeros(D["n_sess"], bool); in_win[sess_in] = True
    sess_wk = np.array([wkmap[s] for s in range(D["n_sess"])])
    keys_w = sorted(set(sess_wk[sess_in]))
    NW = len(keys_w)
    wpos = {k: j for j, k in enumerate(keys_w)}

    def keep(x):
        return bool(in_win[int(sid[i_of(x["et"])])])

    def build(pos, sizing=True):
        base = fills_daily(D, pos, halt=1300, target=1000)
        ent = np.array([i_of(x["et"]) for x in base if A <= np.datetime64(x["et"]) < B])
        if len(ent) < 200:
            return []
        sc, _ = causal_score(X, ent, window=WIN)
        sz = (np.where(sc >= 3, 2, 1) if sizing else np.ones(n)).astype(np.int8)
        return [x for x in fills_qexit(D, pos, sz, sc) if keep(x)]

    def summarise(trl):
        v = np.zeros(NW)
        cm = 0.0
        for x in trl:
            v[wpos[sess_wk[int(sid[i_of(x["et"])])]]] += x["pnl"]
            cm += x.get("u", 1) * ((np.datetime64(x["xt"]) - np.datetime64(x["et"]))
                                   / np.timedelta64(1, "m"))
        dp = dd_profile(v)
        return dict(pts=float(v.sum() / PV / NS), n=len(trl), expo=cm,
                    maxdd=dp["maxdd"], dd_top5=dp["dd_mean_top5"], ulcer=dp["ulcer"],
                    mar=float(v.sum() / max(dp["maxdd"], 1e-9)),
                    size2=float(np.mean([x.get("u", 1) == 2 for x in trl])) if trl else 0.0)

    posL = (vote(TG, D, X, +1) >= 0.5).astype(np.int8)
    trs0 = build(posL)
    r0 = summarise(trs0)
    trs0_1 = build(posL, sizing=False)
    r0_1 = summarise(trs0_1)
    P_(f"=== B1 GATE: {r0['pts']:.2f} pts/session over {NS} sessions (expect 14.72) -> "
       f"{'PASS' if abs(r0['pts'] - 14.72) < 0.6 else 'FAIL - VOID'} [{_time.time()-t0:.0f}s]")
    if abs(r0["pts"] - 14.72) >= 0.6:
        out.close(); return
    P_(f"   incumbent at a flat 1 lot: {r0_1['pts']:.2f} pts/session, "
       f"{r0_1['n']} trades, MAR {r0_1['mar']:.2f}")

    # ---------------- stretches: maximal runs of 'the object wants to be long' ------------
    want = np.zeros(n, np.int8)
    want[1:] = posL[:-1]
    want[D["fb"]] = 0
    starts, ends = [], []                                   # [start, end] inclusive, per session
    for s in sess_in:
        a, b = st[s], en[s]
        w = want[a:b]
        d = np.diff(np.concatenate([[0], w, [0]]))
        for u_, v_ in zip(np.where(d == 1)[0], np.where(d == -1)[0] - 1):
            starts.append(a + int(u_)); ends.append(a + int(v_))
    starts = np.array(starts); ends = np.array(ends)
    NSTR = len(starts)
    # map incumbent trades onto stretches by entry bar
    str_of_bar = np.full(n, -1, np.int64)
    for j in range(NSTR):
        str_of_bar[starts[j]:ends[j] + 1] = j
    tr_by_str = {}
    for x in trs0:
        j = int(str_of_bar[i_of(x["et"])])
        if j >= 0:
            tr_by_str.setdefault(j, []).append(x)
    P_(f"\n   {NSTR:,} long stretches in the window; {len(tr_by_str):,} of them produced an "
       f"incumbent trade (the rest are suppressed by the session box).")

    # =====================================================================================
    # PHASE 1 - THE DURATION LEDGER
    # =====================================================================================
    P_(f"\n{'='*104}\n=== PHASE 1: the incumbent's P&L by holding duration (exact, no backtest)")
    P_(f"{'='*104}")
    dur = np.array([(np.datetime64(x["xt"]) - np.datetime64(x["et"]))
                    / np.timedelta64(1, "m") for x in trs0], float)
    pnl = np.array([x["pnl"] for x in trs0], float)
    sz = np.array([x.get("u", 1) for x in trs0], float)
    qs = np.quantile(dur, np.arange(0, 1.01, 0.1))
    P_(f"{'decile':<10}{'minutes':>16}{'trades':>8}{'mean $':>10}{'total $':>12}"
       f"{'pts/session':>13}{'win %':>8}{'mean size':>11}")
    rows = []
    for k in range(10):
        lo, hi = qs[k], qs[k + 1]
        m = (dur >= lo) & (dur <= hi) if k == 9 else (dur >= lo) & (dur < hi)
        if not m.any():
            continue
        P_(f"{k+1:<10}{f'{lo:.0f}-{hi:.0f}':>16}{int(m.sum()):>8}{pnl[m].mean():>10,.0f}"
           f"{pnl[m].sum():>12,.0f}{pnl[m].sum()/PV/NS:>13.2f}"
           f"{100*float((pnl[m] > 0).mean()):>8.1f}{sz[m].mean():>11.2f}")
        rows.append(dict(decile=k + 1, lo=lo, hi=hi, n=int(m.sum()),
                         mean=float(pnl[m].mean()), total=float(pnl[m].sum()),
                         pts=float(pnl[m].sum() / PV / NS),
                         win=float((pnl[m] > 0).mean()), size=float(sz[m].mean())))
    pd.DataFrame(rows).to_csv(os.path.join(OUT, "duration.csv"), index=False)
    neg = [r for r in rows if r["pts"] < 0]
    P_(f"\n   deciles with NEGATIVE contribution: "
       + (", ".join(f"#{r['decile']} ({r['lo']:.0f}-{r['hi']:.0f} min, {r['pts']:+.2f})"
                    for r in neg) if neg else "none"))
    P_(f"   median hold {np.median(dur):.0f} min | mean {dur.mean():.0f} | "
       f"share under 30 min {100*float((dur < 30).mean()):.1f} % | "
       f"under 60 min {100*float((dur < 60).mean()):.1f} %")

    # =====================================================================================
    # the draws - regenerated with W51d's own seed, so these ARE its first 50 N1 masks
    # =====================================================================================
    pr = pos_range_feature(D, st, en)
    gate = (pr >= 0.5)
    RNG = np.random.default_rng(SEED)

    def draw_n1():
        m = np.empty(n, bool)
        for s in range(D["n_sess"]):
            a, b = st[s], en[s]
            m[a:b] = np.roll(gate[a:b], int(RNG.integers(0, max(b - a, 1))))
        return m
    masks = [draw_n1() for _ in range(NDRAW)]

    # =====================================================================================
    # PHASE 1b + 3 - what the masks delete, and what price the survivors get
    # =====================================================================================
    P_(f"\n{'='*104}\n=== PHASE 1b: what the masks DELETE, and PHASE 3: the price they pay")
    P_(f"{'='*104}")
    del_pnl, del_dur, kep_dur, imp_pts, imp_win, imp_los, ndel = [], [], [], [], [], [], []
    for m in masks:
        d_p, d_d, k_d, ip, iw, il = [], [], [], [], [], []
        for j in range(NSTR):
            a, b = starts[j], ends[j]
            hit = np.flatnonzero(m[a:b + 1])
            xs = tr_by_str.get(j, [])
            if len(hit) == 0:
                for x in xs:
                    d_p.append(x["pnl"])
                    d_d.append((np.datetime64(x["xt"]) - np.datetime64(x["et"]))
                               / np.timedelta64(1, "m"))
                continue
            e_new = a + int(hit[0])
            for x in xs:
                k_d.append((np.datetime64(x["xt"]) - np.datetime64(x["et"]))
                           / np.timedelta64(1, "m"))
                gain = float(o[i_of(x["et"])] - o[e_new])       # long: lower entry is better
                ip.append(gain)
                (iw if x["pnl"] > 0 else il).append(gain)
        del_pnl.append(np.sum(d_p)); ndel.append(len(d_p))
        del_dur.append(np.mean(d_d) if d_d else np.nan)
        kep_dur.append(np.mean(k_d) if k_d else np.nan)
        imp_pts.append(np.mean(ip) if ip else 0.0)
        imp_win.append(np.mean(iw) if iw else 0.0)
        imp_los.append(np.mean(il) if il else 0.0)
    P_(f"   trades deleted per draw : {np.mean(ndel):.0f} of {len(trs0)} "
       f"({100*np.mean(ndel)/len(trs0):.1f} %)")
    P_(f"   their mean duration     : {np.nanmean(del_dur):.0f} min   "
       f"vs kept {np.nanmean(kep_dur):.0f} min   "
       f"-> {'H1 deletion bias CONFIRMED' if np.nanmean(del_dur) < 0.8*np.nanmean(kep_dur) else 'no strong duration bias'}")
    P_(f"   their total P&L per draw: ${np.mean(del_pnl):,.0f}  "
       f"= {np.mean(del_pnl)/PV/NS:+.2f} pts/session REMOVED "
       f"({'a GAIN when removed' if np.mean(del_pnl) < 0 else 'a LOSS when removed'})")
    P_(f"\n   matched-flip entry price improvement (positive = the mask bought LOWER):")
    P_(f"      all matched stretches : {np.mean(imp_pts):+.3f} points")
    P_(f"      on eventual WINNERS   : {np.mean(imp_win):+.3f} points")
    P_(f"      on eventual LOSERS    : {np.mean(imp_los):+.3f} points")
    pd.DataFrame(dict(deleted=ndel, del_pnl=del_pnl, del_dur=del_dur, kep_dur=kep_dur,
                      imp=imp_pts, imp_win=imp_win,
                      imp_los=imp_los)).to_csv(os.path.join(OUT, "h3_matched.csv"), index=False)

    # =====================================================================================
    # PHASE 2 - H2: the same masks with the sizing layer OFF
    # =====================================================================================
    P_(f"\n{'='*104}\n=== PHASE 2 (H2): the same {NDRAW} masks, sizing layer OFF (flat 1 lot)")
    P_(f"{'='*104}")
    sized, flat = [], []
    for k, m in enumerate(masks):
        pg = entry_only(D, posL, m)
        sized.append(summarise(build(pg, sizing=True)))
        flat.append(summarise(build(pg, sizing=False)))
        if (k + 1) % 10 == 0:
            P_(f"   {k+1}/{NDRAW} draws [{_time.time()-t0:.0f}s]")
    S = pd.DataFrame(sized); F = pd.DataFrame(flat)
    S.to_csv(os.path.join(OUT, "h2_sized.csv"), index=False)
    F.to_csv(os.path.join(OUT, "h2_nosizing.csv"), index=False)
    P_(f"\n{'':<26}{'pts':>9}{'MAR':>9}{'maxDD':>10}{'top5DD':>10}{'trades':>9}"
       f"{'expo%':>8}{'size2%':>9}")
    P_(f"{'incumbent  SIZED':<26}{r0['pts']:>9.2f}{r0['mar']:>9.2f}{r0['maxdd']:>10,.0f}"
       f"{r0['dd_top5']:>10,.0f}{r0['n']:>9}{100.0:>8.1f}{100*r0['size2']:>9.1f}")
    P_(f"{'N1 masks   SIZED (mean)':<26}{S['pts'].mean():>9.2f}{S['mar'].mean():>9.2f}"
       f"{S['maxdd'].mean():>10,.0f}{S['dd_top5'].mean():>10,.0f}{S['n'].mean():>9.0f}"
       f"{100*S['expo'].mean()/r0['expo']:>8.1f}{100*S['size2'].mean():>9.1f}")
    P_(f"{'incumbent  FLAT 1 lot':<26}{r0_1['pts']:>9.2f}{r0_1['mar']:>9.2f}"
       f"{r0_1['maxdd']:>10,.0f}{r0_1['dd_top5']:>10,.0f}{r0_1['n']:>9}"
       f"{100*r0_1['expo']/r0['expo']:>8.1f}{0.0:>9.1f}")
    P_(f"{'N1 masks   FLAT (mean)':<26}{F['pts'].mean():>9.2f}{F['mar'].mean():>9.2f}"
       f"{F['maxdd'].mean():>10,.0f}{F['dd_top5'].mean():>10,.0f}{F['n'].mean():>9.0f}"
       f"{100*F['expo'].mean()/r0['expo']:>8.1f}{0.0:>9.1f}")
    d_sized = S["pts"].mean() - r0["pts"]
    d_flat = F["pts"].mean() - r0_1["pts"]
    P_(f"\n   delta with sizing ON : {d_sized:+.2f} pts/session")
    P_(f"   delta with sizing OFF: {d_flat:+.2f} pts/session")
    P_(f"   -> H2 verdict: "
       + ("the advantage is a SIZING-POOL artifact (it does not survive a flat lot)"
          if d_flat <= 0.1 * abs(d_sized) else
          "the advantage survives without sizing - H2 is eliminated as the sole explanation"))

    # =====================================================================================
    # PHASE 4 - THE DECOMPOSITION, done at a flat lot where it can close
    # =====================================================================================
    P_(f"\n{'='*104}\n=== PHASE 4: does the ledger close? (flat 1 lot, where the parts are clean)")
    P_(f"{'='*104}")
    # rebuild the flat-lot delta from its parts, per draw, on the incumbent's flat-lot trades
    dur1 = np.array([(np.datetime64(x["xt"]) - np.datetime64(x["et"]))
                     / np.timedelta64(1, "m") for x in trs0_1], float)
    tr1_by_str = {}
    for x in trs0_1:
        j = int(str_of_bar[i_of(x["et"])])
        if j >= 0:
            tr1_by_str.setdefault(j, []).append(x)
    part_del, part_px = [], []
    for m in masks:
        dp_, px_ = 0.0, 0.0
        for j in range(NSTR):
            a, b = starts[j], ends[j]
            hit = np.flatnonzero(m[a:b + 1])
            xs = tr1_by_str.get(j, [])
            if len(hit) == 0:
                dp_ -= sum(x["pnl"] for x in xs)          # removing them ADDS -pnl
            else:
                e_new = a + int(hit[0])
                for x in xs:
                    px_ += x.get("u", 1) * float(o[i_of(x["et"])] - o[e_new]) * PV
        part_del.append(dp_ / PV / NS); part_px.append(px_ / PV / NS)
    tot = d_flat
    pd_, pp_ = float(np.mean(part_del)), float(np.mean(part_px))
    P_(f"{'component':<44}{'pts/session':>14}")
    P_(f"{'measured delta (flat lot)':<44}{tot:>14.3f}")
    P_(f"{'  + deleted stretches (event effect)':<44}{pd_:>14.3f}")
    P_(f"{'  + entry price on matched stretches':<44}{pp_:>14.3f}")
    P_(f"{'  = ledger':<44}{pd_ + pp_:>14.3f}")
    resid = tot - (pd_ + pp_)
    P_(f"{'  residual (exit paths, box re-timing)':<44}{resid:>14.3f}")
    closes = abs(resid) <= 0.15 * max(abs(tot), 1e-9)
    P_(f"\n   ledger closes to {100*(1-abs(resid)/max(abs(tot),1e-9)):.0f} % -> "
       + ("ACCEPTED, the mechanism sentence below is licensed"
          if closes else "DOES NOT CLOSE (bar: 15 %) - NO mechanism claim is made, "
                         "per the preregistered falsifier"))
    pd.DataFrame(dict(deleted_pts=part_del, price_pts=part_px)).to_csv(
        os.path.join(OUT, "decomp.csv"), index=False)
    if closes:
        parts = {"deleted stretches (H1 event effect)": pd_,
                 "entry price on matched stretches (H3)": pp_}
        dom = max(parts, key=lambda k: abs(parts[k]))
        P_(f"   dominant component: {dom} ({parts[dom]:+.3f} of {tot:+.3f})")

    # =====================================================================================
    # PHASE 5 - is duration forecastable at entry? (diagnostic only, produces a number)
    # =====================================================================================
    P_(f"\n{'='*104}\n=== PHASE 5: is hold duration forecastable at entry? (number, not an arm)")
    P_(f"{'='*104}")
    ei = np.array([i_of(x["et"]) for x in trs0])
    feats = ["dist_open", "dist_vwap", "prev_ret", "runlen", "delta_mag", "ratio", "atr_l"]
    P_(f"{'causal feature at entry':<24}{'Spearman vs duration':>22}{'vs trade P&L':>16}")
    for f in feats:
        v = X[f][ei]
        ok = np.isfinite(v)
        rs = float(pd.Series(v[ok]).corr(pd.Series(dur[ok]), method="spearman"))
        rp = float(pd.Series(v[ok]).corr(pd.Series(pnl[ok]), method="spearman"))
        P_(f"{f:<24}{rs:>22.3f}{rp:>16.3f}")
    P_(f"\n   (a |Spearman| below about 0.10 on {len(ei)} entries is not tradeable information)")
    P_(f"\n=== STATUS: diagnostic wave, nothing adopted. ===")
    out.close()
    print(f"done [{_time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
