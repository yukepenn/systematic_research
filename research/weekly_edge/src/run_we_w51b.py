"""WE_W51b - amendment_1: mechanism first, then entry-only gates, then the CAUSAL
re-derivation of the prior-session conditional, then the two nulls.

The finding this file exists to attack: in W51 phase 2 the prior session's SIGN split the
object's money 90/14 across 64/35 of the exposure, cut max drawdown 46 % and raised MAR 67 %.
That is exactly what the owner asked for - more money per unit of drawdown - and exactly the
shape of result this campaign has been fooled by four times, because `prev_ret` with a
mean-reversion sign is one of the quality score's five features and that SIGN was picked by
W33/W34 on a full-sample scan of this same window.

So the order here is deliberate: prove the mechanism exists in the MARKET (phase A) before
spending a single backtest defending it, then re-derive the sign causally (phase C), then
null it (phase D). If the causal version loses the advantage, the advantage was the sign.
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
from run_we_w01 import ROOT, PV, STRESS_RT                               # noqa: E402
from run_we_w17 import load_deep                                         # noqa: E402
from run_we_w26 import fills_daily                                       # noqa: E402
from run_we_w35 import fills_qexit                                       # noqa: E402
from run_we_w37 import causal_score                                      # noqa: E402
from run_we_w38 import targets, vote                                     # noqa: E402
from run_we_w39 import WIN                                               # noqa: E402
from run_we_w51 import session_frames, classify, A, B                    # noqa: E402
from we_features import build_universe                                   # noqa: E402
from we_quality import build_context                                     # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W51_DONTTRADE", "out")
os.makedirs(OUT, exist_ok=True)
RNG = np.random.default_rng(20260851)
NDRAW = 1000
LEARN_WIN = 250          # trailing sessions the causal sign learner may look at
LEARN_MIN = 250          # no gate at all until this much history exists


def main():
    t0 = _time.time()
    D = load_deep("2022-01-01", "2026-07-31 17:00")
    W1.DEV_END = pd.Timestamp("2026-07-31").date()
    n, tarr = D["n"], D["t"]
    o, c = D["o"], D["c"]
    sid = D["sid"]
    X = build_context(D)
    TG = targets(D)
    st, en, elapsed = session_frames(D)
    wkmap = {s: D["wk"][s] for s in range(D["n_sess"])}
    out = open(os.path.join(OUT, "w51b.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out)

    def i_of(ts):
        return int(min(np.searchsorted(tarr, np.datetime64(ts)), n - 1))

    sess_in = np.array([s for s in range(D["n_sess"]) if A <= tarr[st[s]] < B])
    NS = len(sess_in)
    sess_wk = np.array([wkmap[s] for s in range(D["n_sess"])])
    sess_yr = pd.to_datetime(D["sess_date"]).year.values

    def build(pos):
        base = fills_daily(D, pos, halt=1300, target=1000)
        ent = np.array([i_of(x["et"]) for x in base if A <= np.datetime64(x["et"]) < B])
        if len(ent) < 300:
            return None
        sc, _ = causal_score(X, ent, window=WIN)
        sz = np.where(sc >= 3, 2, 1).astype(np.int8)
        return [x for x in fills_qexit(D, pos, sz, sc)
                if A <= np.datetime64(x["et"]) < B]

    posL = (vote(TG, D, X, +1) >= 0.5).astype(np.int8)
    trs0 = build(posL)
    pts0 = sum(x["pnl"] for x in trs0) / PV / NS
    P_(f"=== B1 GATE: {pts0:.2f} pts/session over {NS} sessions (expect 14.72) -> "
       f"{'PASS' if abs(pts0 - 14.72) < 0.6 else 'FAIL - VOID'} [{_time.time()-t0:.0f}s]")
    if abs(pts0 - 14.72) >= 0.6:
        out.close(); return

    klass = classify(D, st, en)
    KS = ("TREND-UP", "TREND-DOWN", "REVERSAL", "RANGE", "MIXED")

    # per-session ledgers of the incumbent -------------------------------------------------
    sp0 = np.zeros(D["n_sess"]); cm0 = np.zeros(D["n_sess"])
    for x in trs0:
        s = int(sid[i_of(x["et"])])
        sp0[s] += x["pnl"]
        cm0[s] += x.get("u", 1) * ((np.datetime64(x["xt"]) - np.datetime64(x["et"]))
                                   / np.timedelta64(1, "m"))
    sess_ret = np.array([c[en[s] - 1] - o[st[s]] for s in range(D["n_sess"])])
    prev_sign = np.concatenate([[0.0], np.sign(sess_ret[:-1])])          # known at session open

    # =====================================================================================
    # PHASE A - IS THE CONDITIONAL IN THE MARKET, OR ONLY IN OUR P&L?
    # =====================================================================================
    P_(f"\n{'='*100}\n=== PHASE A1: P(session class | prior session sign) vs the base rate")
    P_(f"{'='*100}")
    P_("If the prior session's sign does not shift the probability of TREND-UP - the only class")
    P_("we are paid on - then the D2 result is a P&L artifact and the arm dies here.\n")
    ki = klass[sess_in]; ps = prev_sign[sess_in]
    P_(f"{'prior session':<18}{'sessions':>10}" + "".join(f"{k:>13}" for k in KS))
    base = {k: float((ki == k).mean()) for k in KS}
    P_(f"{'ALL (base rate)':<18}{len(ki):>10}" + "".join(f"{100*base[k]:>12.1f}%" for k in KS))
    rowsA = []
    for lab, m in (("DOWN", ps < 0), ("UP", ps > 0)):
        q = ki[m]
        P_(f"{'prev ' + lab:<18}{len(q):>10}"
           + "".join(f"{100*float((q == k).mean()):>12.1f}%" for k in KS))
        rowsA.append(dict(prev=lab, n=int(m.sum()),
                          **{k: round(float((q == k).mean()), 4) for k in KS}))
    lift = (float((ki[ps < 0] == "TREND-UP").mean()) - float((ki[ps > 0] == "TREND-UP").mean()))
    # exact two-sided permutation test on the TREND-UP share difference
    y = (ki == "TREND-UP").astype(float); g = (ps < 0)
    obs = y[g].mean() - y[~g].mean()
    perm = np.array([(lambda p: y[p].mean() - y[~p].mean())(
        RNG.permutation(g)) for _ in range(2000)])
    pval = float((np.abs(perm) >= abs(obs)).mean())
    P_(f"\n   TREND-UP share after a DOWN session minus after an UP session: "
       f"{100*lift:+.1f} pp   permutation p = {pval:.4f}  "
       f"({'MARKET FACT' if pval < 0.05 else 'NOT SIGNIFICANT - the arm is a P&L artifact'})")
    # and the complementary question: is the DOWN-day damage also conditional?
    tdn = (ki == "TREND-DOWN").astype(float)
    obs2 = tdn[g].mean() - tdn[~g].mean()
    perm2 = np.array([(lambda p: tdn[p].mean() - tdn[~p].mean())(
        RNG.permutation(g)) for _ in range(2000)])
    P_(f"   TREND-DOWN share, same comparison: {100*obs2:+.1f} pp   "
       f"permutation p = {float((np.abs(perm2) >= abs(obs2)).mean()):.4f}")
    pd.DataFrame(rowsA).to_csv(os.path.join(OUT, "mechanism.csv"), index=False)

    P_(f"\n{'='*100}\n=== PHASE A2: the incumbent's P&L by TIME OF DAY x class (never measured)")
    P_(f"{'='*100}")
    mod = ((tarr - tarr.astype("datetime64[D]")).astype("timedelta64[s]")
           .astype(np.int64) // 60)
    BUCK = [("18:00-20:00", 1080, 1200), ("20:00-00:00", 1200, 1440),
            ("00:00-04:00", 0, 240), ("04:00-08:00", 240, 480),
            ("08:00-09:30", 480, 570), ("09:30-10:30", 570, 630),
            ("10:30-12:00", 630, 720), ("12:00-14:00", 720, 840),
            ("14:00-17:00", 840, 1020)]

    def buck_of(i):
        m_ = mod[i]
        for j, (_, a_, b_) in enumerate(BUCK):
            if a_ <= m_ < b_:
                return j
        return len(BUCK) - 1
    tod = np.zeros((len(BUCK), len(KS)))
    for x in trs0:
        e = i_of(x["et"])
        tod[buck_of(e), KS.index(klass[int(sid[e])])] += x["pnl"] / PV / NS
    P_(f"{'entry window (ET)':<20}" + "".join(f"{k:>13}" for k in KS) + f"{'total':>10}")
    for j, (lab, _, _) in enumerate(BUCK):
        P_(f"{lab:<20}" + "".join(f"{tod[j, m]:>13.2f}" for m in range(len(KS)))
           + f"{tod[j].sum():>10.2f}")
    P_(f"{'TOTAL':<20}" + "".join(f"{tod[:, m].sum():>13.2f}" for m in range(len(KS)))
       + f"{tod.sum():>10.2f}")
    pd.DataFrame(tod, index=[b[0] for b in BUCK], columns=list(KS)).to_csv(
        os.path.join(OUT, "tod.csv"))

    # =====================================================================================
    # metric plumbing
    # =====================================================================================
    keys_w = sorted(set(sess_wk[sess_in]))
    wk_idx = np.array([keys_w.index(sess_wk[s]) for s in sess_in])
    NW = len(keys_w)

    def wk_vec(sp):
        return np.bincount(wk_idx, weights=sp, minlength=NW)

    def maxdd(v):
        cum = np.cumsum(v)
        return float((np.maximum.accumulate(cum) - cum).max())

    def metrics(sp, ntr, name="", cm=None):
        v = wk_vec(sp)
        nw = max(1, int(np.ceil(0.05 * len(v))))
        cv = float(np.sort(v)[:nw].mean())
        sd = v.std(ddof=1)
        dd = maxdd(v)
        traded = sp != 0
        return dict(arm=name, n=ntr, pts=round(float(sp.sum() / PV / NS), 2),
                    wk=round(float(v.mean())),
                    wkpos=round(100 * float((v > 0).mean()), 1),
                    daypos=round(100 * float((sp > 0).mean()), 1),
                    trddaypos=round(100 * float((sp[traded] > 0).mean())
                                    if traded.any() else 0.0, 1),
                    worst=round(float(v.min())), maxdd=round(dd),
                    mar=round(float(v.sum() / max(dd, 1e-9)), 2),
                    annshrp=round(float(v.mean() / sd * np.sqrt(52)) if sd > 0 else 0.0, 2),
                    eff=round(float(v.mean() / abs(v.min())) if v.min() < 0 else 9.9, 3),
                    cveff=round(float(v.mean() / abs(cv)) if cv < 0 else 9.9, 3),
                    stress=round(float(v.mean() - STRESS_RT * ntr / len(v))),
                    expo=round(float(cm.sum()) if cm is not None else 0.0))

    HDR = (f"{'arm':<34}{'trds':>6}{'pts':>7}{'wk$':>8}{'wk+%':>6}{'day+%':>7}{'trdD+%':>8}"
           f"{'worst':>9}{'maxDD':>9}{'MAR':>7}{'annShrp':>8}{'eff':>7}{'cvEff':>7}"
           f"{'expo%':>7}{'stress':>8}")
    rows = []

    def show(r, expo0):
        r["expo_pct"] = round(100 * r["expo"] / max(expo0, 1e-9), 1)
        P_(f"{r['arm']:<34}{r['n']:>6}{r['pts']:>7.2f}{r['wk']:>8,.0f}{r['wkpos']:>6.1f}"
           f"{r['daypos']:>7.1f}{r['trddaypos']:>8.1f}{r['worst']:>9,.0f}{r['maxdd']:>9,.0f}"
           f"{r['mar']:>7.2f}{r['annshrp']:>8.2f}{r['eff']:>7.3f}{r['cveff']:>7.3f}"
           f"{r['expo_pct']:>7.1f}{r['stress']:>8,.0f}")
        rows.append(r)

    def ledger(trl):
        sp = np.zeros(D["n_sess"]); cm = np.zeros(D["n_sess"])
        for x in trl:
            s = int(sid[i_of(x["et"])])
            sp[s] += x["pnl"]
            cm[s] += x.get("u", 1) * ((np.datetime64(x["xt"]) - np.datetime64(x["et"]))
                                      / np.timedelta64(1, "m"))
        return sp[sess_in], cm[sess_in]

    sp0i, cm0i = ledger(trs0)
    EXPO0 = float(cm0i.sum())
    r_inc = metrics(sp0i, len(trs0), "P1 INCUMBENT", cm0i)

    # =====================================================================================
    # PHASE B - ENTRY-ONLY GATES (the gate may not close a position it did not prevent)
    # =====================================================================================
    F, _C = build_universe(D)
    runhi = np.zeros(n); runlo = np.zeros(n); sopen = np.zeros(n)
    h_, l_ = D["h"], D["l"]
    for s in range(D["n_sess"]):
        a, b = st[s], en[s]
        sopen[a:b] = o[a]
        hh = np.maximum.accumulate(h_[a:b]); ll = np.minimum.accumulate(l_[a:b])
        runhi[a:b] = np.concatenate([[h_[a]], hh[:-1]])
        runlo[a:b] = np.concatenate([[l_[a]], ll[:-1]])
    c_l = np.concatenate([[c[0]], c[:-1]])
    pos_rng = (c_l - runlo) / np.maximum(runhi - runlo, 1e-9)

    def entry_only(pos, allow):
        """The gate blocks NEW entries; once open the object exits on its own terms."""
        held = np.zeros(n, np.int8)
        h0 = 0
        for i in range(n):
            if D["fb"][i]:
                h0 = 0
            if pos[i] == 0:
                h0 = 0
            elif h0 == 0 and allow[i]:
                h0 = 1
            held[i] = h0
        return held

    GATES = {"E1 entry-only price>=open": (X["dist_open"] >= 0.0),
             "E2 entry-only price>=VWAP": (X["dist_vwap"] >= 0.0),
             "E3 entry-only >=50-sess mean": (F["dist_50sess"] >= 0.0),
             "E4 entry-only upper half range": (pos_rng >= 0.5)}
    P_(f"\n{'='*100}\n=== PHASE B: ENTRY-ONLY gates (event count preserved; no forced exit)")
    P_(f"{'='*100}")
    P_(HDR)
    show(r_inc, EXPO0)
    for nm, allow in GATES.items():
        pg = entry_only(posL, np.asarray(allow, bool))
        trl = build(pg)
        if trl is None:
            P_(f"{nm:<34}  too few entries"); continue
        sp, cm = ledger(trl)
        show(metrics(sp, len(trl), nm, cm), EXPO0)
    pd.DataFrame(rows).to_csv(os.path.join(OUT, "entryonly.csv"), index=False)

    # =====================================================================================
    # PHASE C - CAUSAL RE-DERIVATION of the prior-session conditional
    # =====================================================================================
    P_(f"\n{'='*100}\n=== PHASE C: the prior-session bit, with the SIGN learned causally")
    P_(f"{'='*100}")
    P_("C1 uses the sign W33/W34 picked on a full-sample scan and is reference only.")
    P_("C2 learns the sign from the trailing 250 sessions of the INCUMBENT's realised P&L,")
    P_("   which is information the object already had; no gate at all before 250 sessions.")
    P_("C3 additionally moves the split point to the trailing-250 median of prev_ret.\n")

    def sess_gate_to_bars(gate_sess):
        g = np.zeros(n, bool)
        for s in range(D["n_sess"]):
            g[st[s]:en[s]] = gate_sess[s]
        return g

    # C2 / C3: learn per session, strictly from earlier sessions
    prev_ret_s = np.concatenate([[0.0], sess_ret[:-1]])
    gate2 = np.ones(D["n_sess"], bool)
    gate3 = np.ones(D["n_sess"], bool)
    order = np.argsort(sess_in)
    seq = sess_in[order]
    pnl_seq = sp0[seq]
    pr_seq = prev_ret_s[seq]
    for j in range(len(seq)):
        if j < LEARN_MIN:
            continue
        lo = max(0, j - LEARN_WIN)
        hp, pp = pnl_seq[lo:j], pr_seq[lo:j]
        dn = pp < 0
        if dn.sum() < 30 or (~dn).sum() < 30:
            continue
        favour_down = hp[dn].mean() > hp[~dn].mean()
        gate2[seq[j]] = (pr_seq[j] < 0) if favour_down else (pr_seq[j] >= 0)
        med = float(np.median(pp))
        gate3[seq[j]] = (pr_seq[j] < med) if favour_down else (pr_seq[j] >= med)
    gate1 = (prev_ret_s < 0)

    P_(HDR)
    show(r_inc, EXPO0)
    survivors = {}
    for nm, gs in (("C1 prev down (contaminated)", gate1),
                   ("C2 causal sign learner", gate2),
                   ("C3 causal sign + threshold", gate3)):
        pg = (posL.astype(bool) & sess_gate_to_bars(gs)).astype(np.int8)
        trl = build(pg)
        if trl is None:
            P_(f"{nm:<34}  too few entries"); continue
        sp, cm = ledger(trl)
        r = metrics(sp, len(trl), nm, cm)
        show(r, EXPO0)
        survivors[nm] = (gs, r, sp)
    P_(f"\n   causal learner agreed with the fixed sign on "
       f"{100*float((gate2[sess_in] == gate1[sess_in]).mean()):.1f} % of sessions; "
       f"it chose 'favour prev-down' on "
       f"{100*float((gate2[seq[LEARN_MIN:]] == (pr_seq[LEARN_MIN:] < 0)).mean()):.1f} % "
       f"of the sessions it gated.")

    # per-year for the causal arms
    yrs = sorted(set(sess_yr[sess_in]))
    P_(f"\n=== PER YEAR (pts/session) ===")
    P_(f"{'arm':<34}" + "".join(f"{y:>12}" for y in yrs))
    P_(f"{'P1 INCUMBENT':<34}"
       + "".join(f"{sp0i[sess_yr[sess_in] == y].sum()/PV/max((sess_yr[sess_in]==y).sum(),1):>12.2f}"
                 for y in yrs))
    for nm, (gs, r, sp) in survivors.items():
        P_(f"{nm:<34}"
           + "".join(f"{sp[sess_yr[sess_in] == y].sum()/PV/max((sess_yr[sess_in]==y).sum(),1):>12.2f}"
                     for y in yrs))
    pd.DataFrame([r for _, (_, r, _) in survivors.items()]).to_csv(
        os.path.join(OUT, "causal.csv"), index=False)

    # =====================================================================================
    # PHASE D - NULLS (analytic session-removal path, validated against the full pipeline)
    # =====================================================================================
    P_(f"\n{'='*100}\n=== PHASE D: NULLS")
    P_(f"{'='*100}")

    def analytic(gs):
        keep = gs[sess_in]
        return sp0i * keep, cm0i * keep, int(round(len(trs0) * keep.mean()))
    # validate the analytic path against the full pipeline on C1
    if "C1 prev down (contaminated)" in survivors:
        gs1, r1, _ = survivors["C1 prev down (contaminated)"]
        spa, cma, na = analytic(gs1)
        ra = metrics(spa, na, "C1 analytic", cma)
        err = abs(ra["pts"] - r1["pts"]) / max(abs(r1["pts"]), 1e-9)
        P_(f"   analytic vs full pipeline on C1: pts {ra['pts']:.2f} vs {r1['pts']:.2f} "
           f"({100*err:.1f} % error), maxDD {ra['maxdd']:,} vs {r1['maxdd']:,}, "
           f"MAR {ra['mar']:.2f} vs {r1['mar']:.2f}")
        P_(f"   -> analytic nulls are {'ACCEPTED' if err < 0.05 else 'REJECTED (rerun full)'}"
           f" (bar: < 5 % error)\n")

    null_rows = []
    for nm, (gs, r, sp) in survivors.items():
        keep = gs[sess_in]
        tgt_block_cm = float(cm0i[~keep].sum())
        nblock = int((~keep).sum())
        # ---- N1 circular shift of the session gate ----
        n1 = []
        for _ in range(NDRAW):
            k = int(RNG.integers(20, NS - 20))
            kp = np.roll(keep, k)
            n1.append(metrics(sp0i * kp, int(round(len(trs0) * kp.mean())), cm=cm0i * kp))
        # ---- N2 count- AND exposure-matched random session blocking ----
        n2 = []
        for _ in range(NDRAW):
            p = RNG.permutation(NS)
            cum = np.cumsum(cm0i[p])
            j = int(np.searchsorted(cum, tgt_block_cm)) + 1
            kp = np.ones(NS, bool); kp[p[:min(j, NS)]] = False
            n2.append(metrics(sp0i * kp, int(round(len(trs0) * kp.mean())), cm=cm0i * kp))
        P_(f"{nm}   blocks {nblock} of {NS} sessions, "
           f"{100*tgt_block_cm/EXPO0:.1f} % of contract-minutes")
        P_(f"{'metric':<12}{'arm':>10}{'N1 mean':>10}{'N1 pct':>9}"
           f"{'N2 mean':>10}{'N2 pct':>9}{'verdict':>12}")
        for key, better_high in (("pts", True), ("wk", True), ("maxdd", False),
                                ("mar", True), ("eff", True), ("cveff", True),
                                ("annshrp", True), ("worst", True)):
            a1 = np.array([x[key] for x in n1], float)
            a2 = np.array([x[key] for x in n2], float)
            val = float(r[key])
            p1 = 100 * float((a1 < val).mean() if better_high else (a1 > val).mean())
            p2 = 100 * float((a2 < val).mean() if better_high else (a2 > val).mean())
            P_(f"{key:<12}{val:>10.3f}{a1.mean():>10.3f}{p1:>8.1f}%"
               f"{a2.mean():>10.3f}{p2:>8.1f}%"
               f"{('PASS' if p2 >= 95 else 'fail'):>12}")
            null_rows.append(dict(arm=nm, metric=key, value=val,
                                  n1_mean=round(float(a1.mean()), 4), n1_pct=round(p1, 1),
                                  n2_mean=round(float(a2.mean()), 4), n2_pct=round(p2, 1)))
        P_("")
    pd.DataFrame(null_rows).to_csv(os.path.join(OUT, "nulls.csv"), index=False)
    out.close()
    print(f"done [{_time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
