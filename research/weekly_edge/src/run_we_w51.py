"""WE_W51 DO-NOT-BE-LONG-TODAY (spec preregistered in runs/WE_W51_DONTTRADE/spec.yaml).

W50 measured the object exactly: it earns +18.53 pts/session on the 20.9 % of days that TREND
UP and gives back 3.70 on the other 79 %. Standing aside on TREND-DOWN + RANGE is worth
+4.36 pts/session (+29 %) AND those two classes are over-represented in the worst decile of
weeks. That is the only lever measured in this campaign that plausibly raises production and
cuts the tail at the same time.

W50's classes use END-OF-SESSION information and may not appear in any arm here. So:

  PHASE 1 asks the honest question first - how much of the +4.36 is still SAVEABLE at decision
  time m?  A perfect classifier at minute m can only save P&L that has not happened yet. This
  number has never existed in the campaign and it bounds every arm in phase 2.

  PHASE 2 tests gates whose SIGN IS FIXED A PRIORI BY MECHANISM, not by fitting: a long-only
  trend harvester should stand aside when price is below its own reference level. No threshold
  is chosen by looking at the answer. Arms whose direction is not fixed a priori (prior-session
  state, volatility regime) are run as DIAGNOSTICS and are explicitly not adoptable here.

Nothing is adopted in this file. Adoption requires the nulls in run_we_w51b.py.
"""
from __future__ import annotations

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
from run_we_w19 import weekly                                            # noqa: E402
from run_we_w26 import fills_daily                                       # noqa: E402
from run_we_w35 import fills_qexit                                       # noqa: E402
from run_we_w37 import causal_score                                      # noqa: E402
from run_we_w38 import targets, vote                                     # noqa: E402
from run_we_w39 import WIN                                               # noqa: E402
from we_features import build_universe                                   # noqa: E402
from we_quality import build_context                                     # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W51_DONTTRADE", "out")
os.makedirs(OUT, exist_ok=True)
A = np.datetime64("2022-07-01")
B = np.datetime64("2026-08-01")

# elapsed minutes into the session (session opens 18:00 ET, first bar stamped 18:01, so
# elapsed 0 = 18:01 and elapsed 929 = the 09:30 ET bar, i.e. the RTH opening bar's close)
HORIZONS = [(-1, "pre-session"), (120, "20:01"), (360, "00:01"), (600, "04:01"),
            (840, "08:01"), (929, "09:30 RTH open"), (959, "10:00"), (989, "10:30"),
            (1049, "11:30"), (1169, "13:30")]
BLOCK_CLASSES = ("TREND-DOWN", "RANGE")


# ------------------------------------------------------------------ session scaffolding
def session_frames(D):
    sid, n_sess, n = D["sid"], D["n_sess"], D["n"]
    st = np.searchsorted(sid, np.arange(n_sess), side="left")
    en = np.searchsorted(sid, np.arange(n_sess), side="right")          # exclusive
    t = D["t"]
    elapsed = (t - t[st[sid]]).astype("timedelta64[m]").astype(np.int64)
    return st, en, elapsed


def classify(D, st, en):
    """W50's session taxonomy, verbatim. DIAGNOSTIC ONLY - uses end-of-session facts."""
    o, c, h, l = D["o"], D["c"], D["h"], D["l"]
    out = []
    for s in range(D["n_sess"]):
        a, b = st[s], en[s]
        op, cl = o[a], c[b - 1]
        hi, lo = h[a:b].max(), l[a:b].min()
        rng, body = hi - lo, cl - op
        if rng <= 1e-9:
            k = "MIXED"
        elif abs(body) >= 0.60 * rng:
            k = "TREND-UP" if body > 0 else "TREND-DOWN"
        elif abs(body) <= 0.25 * rng:
            k = "RANGE"
        else:
            ih, il = int(np.argmax(h[a:b])), int(np.argmin(l[a:b]))
            k = "REVERSAL" if ((ih < il and (cl - lo) < 0.40 * rng) or
                               (il < ih and (hi - cl) < 0.40 * rng)) else "MIXED"
        out.append(k)
    return np.array(out)


def main():
    t0 = _time.time()
    D = load_deep("2022-01-01", "2026-07-31 17:00")
    W1.DEV_END = pd.Timestamp("2026-07-31").date()
    n, tarr = D["n"], D["t"]
    o, c, h, l = D["o"], D["c"], D["h"], D["l"]
    sid = D["sid"]
    X = build_context(D)
    TG = targets(D)
    st, en, elapsed = session_frames(D)
    wkmap = {s: D["wk"][s] for s in range(D["n_sess"])}
    out = open(os.path.join(OUT, "donttrade.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out)

    def i_of(ts):
        return int(min(np.searchsorted(tarr, np.datetime64(ts)), n - 1))

    def wk_of(ts):
        return wkmap[int(sid[i_of(ts)])]

    sess_in = np.array([s for s in range(D["n_sess"]) if A <= tarr[st[s]] < B])
    NS = len(sess_in)
    sess_yr = pd.to_datetime(D["sess_date"]).year.values

    # ---------------- the incumbent, rebuilt exactly ------------------------------------
    def build(pos):
        """The full P1 pipeline on an arbitrary per-bar desired-position array."""
        base = fills_daily(D, pos, halt=1300, target=1000)
        ent = np.array([i_of(x["et"]) for x in base if A <= np.datetime64(x["et"]) < B])
        if len(ent) < 300:
            return None, None
        sc, _ = causal_score(X, ent, window=WIN)
        sz = np.where(sc >= 3, 2, 1).astype(np.int8)
        return fills_qexit(D, pos, sz, sc), sc

    posL = (vote(TG, D, X, +1) >= 0.5).astype(np.int8)
    P1, sc0 = build(posL)
    trs0 = [x for x in P1 if A <= np.datetime64(x["et"]) < B]
    pts0 = sum(x["pnl"] for x in trs0) / PV / NS
    P_(f"=== B1 GATE: {pts0:.2f} pts/session over {NS} sessions (expect 14.72) -> "
       f"{'PASS' if abs(pts0 - 14.72) < 0.6 else 'FAIL - VOID'} [{_time.time()-t0:.0f}s]")
    if abs(pts0 - 14.72) >= 0.6:
        out.close(); return

    klass = classify(D, st, en)
    KS = ("TREND-UP", "TREND-DOWN", "REVERSAL", "RANGE", "MIXED")
    blocked_mask = np.isin(klass, BLOCK_CLASSES)

    # =================================================================================
    # PHASE 1 - THE CEILING BY DECISION TIME
    # =================================================================================
    P_(f"\n{'='*94}\n=== PHASE 1: THE CEILING BY DECISION TIME (diagnostic, nothing adopted)")
    P_(f"{'='*94}")
    P_("A perfect oracle at decision time m knows the session's final class but can only act")
    P_("on P&L that has not happened yet. Two action models are priced:")
    P_("  BLOCK  = refuse NEW entries from m onward (what every gate in phase 2 actually does)")
    P_("  FLATTEN= block AND close any position open at m (strictly stronger, needs an exit)")
    P_("")
    P_(f"{'decide at':<18}{'sessions':>10}{'BLOCK save':>12}{'as % of 4.36':>14}"
       f"{'FLATTEN save':>14}{'as % of 4.36':>14}{'oracle AUC':>12}")

    # per-session cut index for each horizon
    ceil_rows = []
    # causal separability features measured at the cut bar
    F, _C = build_universe(D)
    for hm, lbl in HORIZONS:
        save_b = 0.0
        save_f = 0.0
        cut = np.full(D["n_sess"], -1, np.int64)
        for s in sess_in:
            a, b = st[s], en[s]
            if hm < 0:
                cut[s] = a - 1                      # before the session exists
            else:
                e = elapsed[a:b]
                k = int(np.searchsorted(e, hm, side="right")) - 1
                cut[s] = a + k if k >= 0 else a - 1
        for x in trs0:
            e_i, x_i = i_of(x["et"]), i_of(x["xt"])
            s = int(sid[e_i])
            if not (A <= tarr[st[s]] < B) or not blocked_mask[s]:
                continue
            k = cut[s]
            u = x.get("u", 1)
            if e_i > k:                              # entry is after the decision -> blocked
                save_b -= x["pnl"]
            elif x_i > k and k >= st[s]:             # open across the decision
                # exact split at the decision bar's close; the exit price is recovered from
                # the trade's own P&L so session-close and next-open exits are both exact
                epx = o[e_i]
                exit_px = epx + (x["pnl"] + COMM_RT * u) / (u * PV)
                save_f -= u * (exit_px - c[k]) * PV
        ceil_b, ceil_f = save_b / PV / NS, save_f / PV / NS
        # oracle separability of blocked classes using ONLY information through the cut bar
        auc = np.nan
        if hm >= 0:
            kk = np.array([cut[s] for s in sess_in])
            ok = kk >= 0
            sgn = np.array([(c[cut[s]] - o[st[s]]) if cut[s] >= st[s] else 0.0
                            for s in sess_in])
            y = blocked_mask[sess_in]
            if ok.sum() > 50 and 0 < y.sum() < len(y):
                r = pd.Series(-sgn).rank().values          # lower signed move -> more likely bad
                n1, n0 = y.sum(), (~y).sum()
                auc = (r[y].sum() - n1 * (n1 + 1) / 2) / (n1 * n0)
        ceil_rows.append(dict(m=hm, label=lbl, block=round(ceil_b, 3),
                              flatten=round(ceil_f + ceil_b, 3), auc=round(float(auc), 3)))
        P_(f"{lbl:<18}{NS:>10}{ceil_b:>12.2f}{100*ceil_b/4.36:>13.0f}%"
           f"{ceil_b+ceil_f:>14.2f}{100*(ceil_b+ceil_f)/4.36:>13.0f}%"
           f"{('' if np.isnan(auc) else f'{auc:.3f}'):>12}")
    pd.DataFrame(ceil_rows).to_csv(os.path.join(OUT, "ceiling.csv"), index=False)
    P_("")
    P_("   The BLOCK column at 'pre-session' must reproduce +4.36 - that is phase 1's own B1.")
    P_("   AUC is a SINGLE causal feature (signed move so far); it is a floor on separability,")
    P_("   not a ceiling, and it is reported to show how early the information arrives.")

    # =================================================================================
    # PHASE 2 - CAUSAL GATES
    # =================================================================================
    idx = np.arange(n)
    atr = np.maximum(X["atr_l"], 1e-9)
    sopen = np.zeros(n)
    for s in range(D["n_sess"]):
        sopen[st[s]:en[s]] = o[st[s]]
    # running session high/low through bar i-1
    runhi = np.zeros(n); runlo = np.zeros(n)
    for s in range(D["n_sess"]):
        a, b = st[s], en[s]
        hh = np.maximum.accumulate(h[a:b]); ll = np.minimum.accumulate(l[a:b])
        runhi[a:b] = np.concatenate([[h[a]], hh[:-1]])
        runlo[a:b] = np.concatenate([[l[a]], ll[:-1]])
    c_l = np.concatenate([[c[0]], c[:-1]])
    span = np.maximum(runhi - runlo, 1e-9)
    pos_rng = (c_l - runlo) / span                       # 0..1, causal
    dist_open = X["dist_open"]                           # (c_{i-1} - session open) / atr
    dist_vwap = X["dist_vwap"]
    dist_50s = F["dist_50sess"]                          # HTF: close vs 50-session mean
    # RTH opening range (09:31..10:00 ET bars), decided once at 10:00, causal thereafter
    mod = ((tarr - tarr.astype("datetime64[D]")).astype("timedelta64[s]")
           .astype(np.int64) // 60)
    rth_or_pos = np.full(n, 0.5)
    rth_or_done = np.zeros(n, bool)
    for s in range(D["n_sess"]):
        a, b = st[s], en[s]
        m = idx[a:b]
        r = m[(mod[a:b] >= 570) & (mod[a:b] <= 600)]     # 09:30..10:00 ET
        if len(r) < 5:
            continue
        k = int(r[-1])
        hi_, lo_ = h[r].max(), l[r].min()
        w = max(hi_ - lo_, 1e-9)
        after = m[m > k]
        rth_or_pos[after] = (c_l[after] - lo_) / w
        rth_or_done[after] = True
    gap_atr = F["gap_atr"]
    prev_ret = X["prev_ret"]
    atr_rel = F["atr_rel"]

    ARMS = {}
    # ---- a-priori signed: a long-only trend harvester stands aside below its reference ----
    ARMS["A1 price >= session open"] = ("adoptable", (dist_open >= 0.0))
    ARMS["A2 price >= session VWAP"] = ("adoptable", (dist_vwap >= 0.0))
    ARMS["A3 price >= 50-sess mean"] = ("adoptable", (dist_50s >= 0.0))
    ARMS["A4 upper half of sess range"] = ("adoptable", (pos_rng >= 0.5))
    ARMS["A5 A1 and A3"] = ("adoptable", (dist_open >= 0.0) & (dist_50s >= 0.0))
    ARMS["A6 >=3 of A1..A4"] = ("adoptable",
                                ((dist_open >= 0).astype(int) + (dist_vwap >= 0).astype(int)
                                 + (dist_50s >= 0).astype(int)
                                 + (pos_rng >= 0.5).astype(int)) >= 3)
    ARMS["A7 >=2 of A1..A4"] = ("adoptable",
                                ((dist_open >= 0).astype(int) + (dist_vwap >= 0).astype(int)
                                 + (dist_50s >= 0).astype(int)
                                 + (pos_rng >= 0.5).astype(int)) >= 2)
    # ---- session-level, sign fixed a priori ----------------------------------------------
    ARMS["B1 gap up (whole session)"] = ("adoptable", (gap_atr >= 0.0))
    ARMS["B2 RTH-OR upper half"] = ("adoptable", (~rth_or_done) | (rth_or_pos >= 0.5))
    # ---- diagnostics: direction NOT fixed a priori, not adoptable in this wave ------------
    ARMS["D1 prev session up"] = ("diagnostic", (prev_ret >= 0.0))
    ARMS["D2 prev session down"] = ("diagnostic", (prev_ret <= 0.0))
    ARMS["D3 ATR below its norm"] = ("diagnostic", (atr_rel <= 1.0))
    ARMS["D4 ATR above its norm"] = ("diagnostic", (atr_rel >= 1.0))

    keys_w = sorted(weekly(trs0, wk_of, A, B))
    v0 = np.array([weekly(trs0, wk_of, A, B).get(k, 0.0) for k in keys_w])

    def sess_pnl(trl):
        d = np.zeros(D["n_sess"])
        for x in trl:
            if A <= np.datetime64(x["et"]) < B:
                d[int(sid[i_of(x["et"])])] += x["pnl"]
        return d

    def expo(trl):
        return float(sum(x.get("u", 1) * ((np.datetime64(x["xt"]) - np.datetime64(x["et"]))
                                          / np.timedelta64(1, "m"))
                         for x in trl if A <= np.datetime64(x["et"]) < B))

    def maxdd(v):
        cum = np.cumsum(v)
        return float((np.maximum.accumulate(cum) - cum).max())

    rows = []
    hdr = (f"{'arm':<30}{'trds':>6}{'pts':>7}{'wk$':>8}{'wk+%':>6}{'day+%':>7}{'trdDay+%':>9}"
           f"{'worst':>9}{'maxDD':>9}{'MAR':>6}{'annShrp':>8}{'eff':>7}{'cvEff':>7}"
           f"{'expo%':>7}{'stress':>8}")

    def rep(nm, trl, tag=""):
        d = weekly(trl, wk_of, A, B)
        v = np.array([d.get(k, 0.0) for k in keys_w])
        p = np.array([x["pnl"] for x in trl if A <= np.datetime64(x["et"]) < B])
        if len(p) == 0:
            p = np.array([0.0])
        sp = sess_pnl(trl)[sess_in]
        traded = sp != 0
        nw = max(1, int(np.ceil(0.05 * len(v))))
        cv = float(np.sort(v)[:nw].mean())
        s_ = float(v.mean() / v.std(ddof=1)) if v.std(ddof=1) > 0 else 0.0
        eff = float(v.mean() / abs(v.min())) if v.min() < 0 else 9.9
        cve = float(v.mean() / abs(cv)) if cv < 0 else 9.9
        stg = float(v.mean() - STRESS_RT * len(p) / len(v))
        dd = maxdd(v)
        r = dict(arm=nm, kind=tag, n=len(p), pts=round(float(p.sum() / PV / NS), 2),
                 wk=round(float(v.mean())), wkpos=round(100 * float((v > 0).mean()), 1),
                 daypos=round(100 * float((sp > 0).mean()), 1),
                 trddaypos=round(100 * float((sp[traded] > 0).mean()) if traded.any() else 0, 1),
                 worst=round(float(v.min())), maxdd=round(dd),
                 mar=round(float(v.sum() / max(dd, 1e-9)), 2),
                 annshrp=round(s_ * np.sqrt(52), 2), eff=round(eff, 3), cveff=round(cve, 3),
                 expo=round(expo(trl)), stress=round(stg))
        r["expo_pct"] = round(100 * r["expo"] / max(EXPO0, 1e-9), 1)
        P_(f"{nm:<30}{r['n']:>6}{r['pts']:>7.2f}{r['wk']:>8,.0f}{r['wkpos']:>6.1f}"
           f"{r['daypos']:>7.1f}{r['trddaypos']:>9.1f}{r['worst']:>9,.0f}{r['maxdd']:>9,.0f}"
           f"{r['mar']:>6.2f}{r['annshrp']:>8.2f}{r['eff']:>7.3f}{r['cveff']:>7.3f}"
           f"{r['expo_pct']:>7.1f}{r['stress']:>8,.0f}")
        rows.append(r); return r, sp

    EXPO0 = expo(trs0)
    P_(f"\n{'='*94}\n=== PHASE 2: CAUSAL GATES, entries otherwise frozen, sizing recomputed causally")
    P_(f"{'='*94}")
    P_("eff and annualised Sharpe are exposure-INVARIANT (scaling contracts multiplies weekly")
    P_("mean and worst week together), so a gate that only cuts exposure cannot win on them.")
    P_("expo% is the gate's contract-minutes as a share of the incumbent's - it is the number")
    P_("the count-matched null in run_we_w51b.py has to match.\n")
    P_(hdr)
    r0, sp0 = rep("P1 INCUMBENT", trs0, "incumbent")

    per_class = {"P1 INCUMBENT": {k: float(sp0[klass[sess_in] == k].sum() / PV / NS)
                                 for k in KS}}
    for nm, (kind, allow) in ARMS.items():
        pos_g = (posL.astype(bool) & np.asarray(allow, bool)).astype(np.int8)
        trl, _ = build(pos_g)
        if trl is None:
            P_(f"{nm:<30}  too few entries, skipped")
            continue
        trl = [x for x in trl if A <= np.datetime64(x["et"]) < B]
        r, sp = rep(nm, trl, kind)
        per_class[nm] = {k: float(sp[klass[sess_in] == k].sum() / PV / NS) for k in KS}
    R = pd.DataFrame(rows)
    R.to_csv(os.path.join(OUT, "gates.csv"), index=False)

    # ------------- did the gate find what it was aimed at? --------------------------------
    P_(f"\n=== WHERE THE CHANGE CAME FROM (pts/session by W50 class; diagnostic classes) ===")
    P_(f"{'arm':<30}" + "".join(f"{k:>13}" for k in KS) + f"{'total':>9}")
    for nm, dd in per_class.items():
        P_(f"{nm:<30}" + "".join(f"{dd[k]:>13.2f}" for k in KS)
           + f"{sum(dd.values()):>9.2f}")
    P_("")
    P_("   A gate aimed at TREND-DOWN + RANGE must IMPROVE those two columns while leaving")
    P_("   TREND-UP roughly intact. A gate that mostly shrinks TREND-UP is cutting exposure,")
    P_("   not finding the bad days.")
    pd.DataFrame(per_class).T.to_csv(os.path.join(OUT, "per_class.csv"))

    # =================================================================================
    # PHASE 3 - PER YEAR for anything that beat the incumbent on eff AND MAR
    # =================================================================================
    surv = R[(R["kind"] == "adoptable") & (R["eff"] > r0["eff"]) & (R["mar"] > r0["mar"])]
    P_(f"\n{'='*94}\n=== PHASE 3: PER YEAR (only arms that beat the incumbent on BOTH eff and MAR)")
    P_(f"{'='*94}")
    if not len(surv):
        P_("   NO ADOPTABLE ARM beat the incumbent on both. Per-year is not run.")
    else:
        yrs = sorted(set(sess_yr[sess_in]))
        P_(f"{'arm':<30}" + "".join(f"{y:>12}" for y in yrs))
        # rebuild survivors once more to get their per-session ledger
        for nm in ["P1 INCUMBENT"] + list(surv["arm"]):
            if nm == "P1 INCUMBENT":
                sp = sp0
            else:
                kind, allow = ARMS[nm]
                pos_g = (posL.astype(bool) & np.asarray(allow, bool)).astype(np.int8)
                trl, _ = build(pos_g)
                sp = sess_pnl([x for x in trl if A <= np.datetime64(x["et"]) < B])[sess_in]
            yv = [sp[sess_yr[sess_in] == y].sum() / PV / max((sess_yr[sess_in] == y).sum(), 1)
                  for y in yrs]
            P_(f"{nm:<30}" + "".join(f"{x:>12.2f}" for x in yv))

    P_(f"\n=== STATUS ===")
    P_("   Nothing is adopted in this file. run_we_w51b.py runs the two nulls (circular-shift")
    P_("   and EXPOSURE-matched count-matched) on whatever survived phase 2 and phase 3.")
    R.to_csv(os.path.join(OUT, "summary.csv"), index=False)
    out.close()
    print(f"done [{_time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
