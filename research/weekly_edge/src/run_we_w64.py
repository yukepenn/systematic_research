"""WE_W64 - why was 2023 bad, and does it matter?

The owner asked whether the object can make $3,000/week stably. The arithmetic says the AVERAGE
can, at ~2.6 contracts and a ~$41,000 drawdown - and that 2023 becomes $626/WEEK FOR A WHOLE
YEAR at that size. Everything else about the object is strong. 2023 is the single fact that
makes the word "stably" false, and no wave has asked why.

Phase 1 is exact accounting in the object's own vocabulary. Phase 4 exists because the most
likely honest answer is that a bad year is the price of the edge rather than a fixable defect,
and in that case the deliverable is a DISTRIBUTION, not a rule.
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
from run_we_w51 import session_frames, classify, A, B                    # noqa: E402
from run_we_w51c import setup, dd_profile                                # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W64_BADYEAR", "out")
os.makedirs(OUT, exist_ok=True)
KS = ("TREND-UP", "TREND-DOWN", "REVERSAL", "RANGE", "MIXED")
CONTRACTS = 2.6            # the size at which the full-window average is ~$3,000/week


def main():
    t0 = _time.time()
    D, X, TG, st, en = setup()
    n, tarr, sid = D["n"], D["t"], D["sid"]
    o, c, h, l = D["o"], D["c"], D["h"], D["l"]
    wkmap = {s: D["wk"][s] for s in range(D["n_sess"])}
    out = open(os.path.join(OUT, "badyear.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out)

    def i_of(ts):
        return int(min(np.searchsorted(tarr, np.datetime64(ts)), n - 1))

    sess_in = np.array([s for s in range(D["n_sess"]) if A <= tarr[st[s]] < B])
    NS = len(sess_in)
    in_win = np.zeros(D["n_sess"], bool); in_win[sess_in] = True
    sess_wk = np.array([wkmap[s] for s in range(D["n_sess"])])
    keys_w = sorted(set(sess_wk[sess_in]))
    wk_idx = np.array([keys_w.index(sess_wk[s]) for s in sess_in])
    NW = len(keys_w)
    sdate = pd.to_datetime(D["sess_date"])[sess_in]
    yr = sdate.year.values
    yrs = sorted(set(yr))

    posL = (vote(TG, D, X, +1) >= 0.5).astype(np.int8)
    base = fills_daily(D, posL, halt=1300, target=1000)
    e = np.array([i_of(x["et"]) for x in base if A <= np.datetime64(x["et"]) < B])
    sc, _ = causal_score(X, e, window=WIN)
    sz = np.where(sc >= 3, 2, 1).astype(np.int8)
    P1 = [x for x in fills_qexit(D, posL, sz, sc) if in_win[int(sid[i_of(x["et"])])]]
    sp = np.zeros(D["n_sess"])
    cm = np.zeros(D["n_sess"])
    for x in P1:
        s_ = int(sid[i_of(x["et"])])
        sp[s_] += x["pnl"]
        cm[s_] += x.get("u", 1) * ((np.datetime64(x["xt"]) - np.datetime64(x["et"]))
                                   / np.timedelta64(1, "m"))
    sp, cm = sp[sess_in], cm[sess_in]
    pts = sp.sum() / PV / NS
    P_(f"=== B1 GATE: {pts:.2f} pts/session over {NS} sessions (expect 14.72) -> "
       f"{'PASS' if abs(pts - 14.72) < 0.6 else 'FAIL - VOID'} [{_time.time()-t0:.0f}s]")
    if abs(pts - 14.72) >= 0.6:
        out.close(); return

    klass = classify(D, st, en)[sess_in]
    # available movement per session (perfect-foresight single trade), as in W50
    avail = np.zeros(NS)
    body = np.zeros(NS); rng_ = np.zeros(NS)
    for j, s_ in enumerate(sess_in):
        a_, b_ = st[s_], en[s_]
        run_min = np.minimum.accumulate(l[a_:b_])
        run_max = np.maximum.accumulate(h[a_:b_])
        avail[j] = max(float((h[a_:b_] - run_min).max()), float((run_max - l[a_:b_]).max()))
        body[j] = c[b_ - 1] - o[a_]
        rng_[j] = h[a_:b_].max() - l[a_:b_].min()

    # =====================================================================================
    # PHASE 1 - WHAT 2023 WAS, in the object's own vocabulary
    # =====================================================================================
    P_(f"\n{'='*118}\n=== PHASE 1a: the session-class MIX per year (was 2023 short of trend days?)")
    P_(f"{'='*118}")
    P_(f"{'year':<8}{'sessions':>10}" + "".join(f"{k:>13}" for k in KS))
    mix = []
    for y in yrs:
        m = yr == y
        P_(f"{y:<8}{int(m.sum()):>10}"
           + "".join(f"{100*float((klass[m] == k).mean()):>12.1f}%" for k in KS))
        mix.append(dict(year=y, n=int(m.sum()),
                        **{k: float((klass[m] == k).mean()) for k in KS}))
    P_(f"{'ALL':<8}{NS:>10}" + "".join(f"{100*float((klass == k).mean()):>12.1f}%" for k in KS))

    P_(f"\n=== PHASE 1b: were the trend days SMALLER, and did we capture less of them? ===")
    P_(f"{'year':<8}{'avail/ses':>11}{'TREND-UP avail':>16}{'our pts/ses':>13}"
       f"{'TREND-UP pts':>14}{'capture on TU':>15}{'$/wk @1.27':>12}")
    rows = []
    for y in yrs:
        m = yr == y
        tu = m & (klass == "TREND-UP")
        capt = 100 * sp[tu].sum() / PV / max(avail[tu].sum(), 1e-9)
        wkn = len(set(np.array(keys_w)[wk_idx[m]]))
        P_(f"{y:<8}{avail[m].mean():>11.1f}{avail[tu].mean() if tu.any() else 0:>16.1f}"
           f"{sp[m].sum()/PV/max(m.sum(),1):>13.2f}"
           f"{sp[tu].sum()/PV/max(tu.sum(),1) if tu.any() else 0:>14.2f}"
           f"{capt:>14.2f}%{sp[m].sum()/max(wkn,1):>12,.0f}")
        rows.append(dict(year=y, avail=float(avail[m].mean()),
                         tu_avail=float(avail[tu].mean()) if tu.any() else 0.0,
                         pts=float(sp[m].sum() / PV / max(m.sum(), 1)),
                         tu_pts=float(sp[tu].sum() / PV / max(tu.sum(), 1)) if tu.any() else 0.0,
                         tu_capture=float(capt), weekly=float(sp[m].sum() / max(wkn, 1))))
    pd.DataFrame(rows).to_csv(os.path.join(OUT, "peryear.csv"), index=False)
    pd.DataFrame(mix).to_csv(os.path.join(OUT, "classmix.csv"), index=False)

    P_(f"\n=== PHASE 1c: did the object SIT OUT more in 2023? ===")
    P_(f"{'year':<8}{'trades':>9}{'flat sess %':>13}{'contract-min':>14}{'per session':>13}"
       f"{'hit %':>8}{'mean win $':>12}{'mean loss $':>13}{'top-5% share':>14}")
    for y in yrs:
        m = yr == y
        tr = [x for x in P1 if pd.Timestamp(D["sess_date"][int(sid[i_of(x["et"])])]).year == y]
        pn = np.array([x["pnl"] for x in tr]) if tr else np.array([0.0])
        s_ = sp[m]
        k5 = max(1, int(np.ceil(0.05 * m.sum())))
        top5 = np.sort(s_)[-k5:].sum()
        P_(f"{y:<8}{len(tr):>9}{100*float((s_ == 0).mean()):>12.1f}%{cm[m].sum():>14,.0f}"
           f"{cm[m].sum()/max(m.sum(),1):>13.1f}"
           f"{100*float((pn > 0).mean()):>7.1f}%{pn[pn > 0].mean() if (pn > 0).any() else 0:>12,.0f}"
           f"{pn[pn < 0].mean() if (pn < 0).any() else 0:>13,.0f}"
           f"{100*top5/max(s_.sum(), 1e-9):>13.0f}%")

    # =====================================================================================
    # PHASE 2 - was it visible causally, DURING the year?
    # =====================================================================================
    P_(f"\n{'='*118}\n=== PHASE 2: was 2023 visible in TRAILING data while it was happening?")
    P_(f"{'='*118}")
    P_("Trailing 60-session measures, lagged, so each value is knowable before the session it")
    P_("describes. The bar this campaign's four regime-identification failures set: the variable")
    P_("must be low DURING the bad stretch in the trailing data, not merely correlated after.\n")
    tu = (klass == "TREND-UP").astype(float)
    S = pd.DataFrame(dict(date=sdate, yr=yr, pnl=sp, avail=avail, tu=tu,
                          rng=rng_, absbody=np.abs(body)))
    for col in ("tu", "avail", "rng", "absbody"):
        S[f"tr_{col}"] = S[col].rolling(60, min_periods=30).mean().shift(1)
    P_(f"{'year':<8}{'trailing TREND-UP share':>26}{'trailing avail/ses':>21}"
       f"{'trailing range':>17}{'realised $/wk':>15}")
    for y in yrs:
        m = (S["yr"] == y).values
        wkn = len(set(np.array(keys_w)[wk_idx[m]]))
        P_(f"{y:<8}{100*S.loc[m, 'tr_tu'].mean():>25.1f}%{S.loc[m, 'tr_avail'].mean():>21.1f}"
           f"{S.loc[m, 'tr_rng'].mean():>17.1f}{sp[m].sum()/max(wkn,1):>15,.0f}")
    ok = S["tr_avail"].notna()
    P_(f"\n   correlation of the TRAILING measure with the SAME session's P&L:")
    for col in ("tr_tu", "tr_avail", "tr_rng", "tr_absbody"):
        P_(f"      {col:<14} Spearman {float(S.loc[ok, col].corr(S.loc[ok, 'pnl'], method='spearman')):+.3f}")
    P_(f"\n   and at the WEEKLY level, trailing measure vs that week's P&L:")
    wv = np.bincount(wk_idx, weights=sp, minlength=NW)
    for col in ("tr_tu", "tr_avail", "tr_rng"):
        wm = np.bincount(wk_idx, weights=np.nan_to_num(S[col].values), minlength=NW) / \
            np.maximum(np.bincount(wk_idx, minlength=NW), 1)
        good = np.bincount(wk_idx, minlength=NW) > 0
        P_(f"      {col:<14} Spearman "
           f"{float(pd.Series(wm[good]).corr(pd.Series(wv[good]), method='spearman')):+.3f}")

    # =====================================================================================
    # PHASE 4 - the honest distribution (run regardless; it is the fallback deliverable)
    # =====================================================================================
    P_(f"\n{'='*118}\n=== PHASE 4: the distribution the owner actually needs")
    P_(f"{'='*118}")
    v = np.bincount(wk_idx, weights=sp, minlength=NW)
    v = v[np.bincount(wk_idx, minlength=NW) > 0]
    k = CONTRACTS / 1.27
    vk = v * k
    P_(f"   at {CONTRACTS:.1f} contracts (the size at which the full-window average is "
       f"~$3,000/week):")
    P_(f"      mean ${vk.mean():,.0f}/wk | median ${np.median(vk):,.0f} | "
       f"positive weeks {100*float((vk > 0).mean()):.1f} %")
    P_(f"      worst week ${vk.min():,.0f} | best week ${vk.max():,.0f} | "
       f"max drawdown ${dd_profile(v)['maxdd']*k:,.0f}")
    P_(f"\n   rolling 52-week windows at that size ({max(0, len(vk)-51)} of them):")
    roll = np.array([vk[i:i + 52].mean() for i in range(len(vk) - 51)])
    for q in (0, 5, 10, 25, 50, 75, 100):
        P_(f"      {q:>3}th percentile of the 52-week average: ${np.percentile(roll, q):,.0f}/wk")
    P_(f"      fraction of 52-week windows below $2,000/wk: "
       f"{100*float((roll < 2000).mean()):.0f} %   below $1,000/wk: "
       f"{100*float((roll < 1000).mean()):.0f} %")
    b = m_ = 0
    for z in vk:
        b = b + 1 if z < 0 else 0
        m_ = max(m_, b)
    P_(f"\n   longest run of losing weeks: {m_}")
    cum = np.cumsum(vk)
    uw = np.maximum.accumulate(cum) - cum
    P_(f"   weeks spent under water: {100*float((uw > 0).mean()):.0f} % | "
       f"longest under-water stretch {int(max((len(list(g)) for k2, g in __import__('itertools').groupby(uw > 0) if k2), default=0))} weeks")
    pd.DataFrame(dict(week=np.arange(len(vk)), weekly=vk)).to_csv(
        os.path.join(OUT, "distribution.csv"), index=False)
    P_(f"\n=== STATUS: diagnostic. Nothing adopted. ===")
    out.close()
    print(f"done [{_time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
