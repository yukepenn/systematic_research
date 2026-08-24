"""TASK V1 part 1 — ADVERSARIAL VERIFICATION: independent re-implementation of the D-gate.

Written from the gate DESCRIPTION only (hunt_D_result.md rule box + task brief), with an
independently coded event loop (not calling eng.run_wrapper / run_r1g.run_integrated).

Two configurations verified:
  A) "label config" = hunt_D base: ledger precomputed (EARLY-pullback) signals, T1-only
     stop-and-reverse, comm 2.09/side, NO B1, open-guard mins_open<3, evening rule
     (prior<=-1000, first 360min), armed-noon rule (X=1600, K=3).  Scored against the
     127-row label file (42 HARD).
  B) "master config" = run_r1g INT_T1only: LATE-mode regenerated signals
     (pullback_early=False), B1 first-bar drop, NO open guard, same gate constants.
     Compared against claimed n=5011 L2483/S2528 net=244589 wr=39.83 pf=1.127
     dd=-29077 hold 93.02 (105.61/80.65).
Also cross-checks: does config B still pass the 42 HARD labels?
"""
import csv
import os
import sys

import numpy as np

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
SRC = os.path.join(ROOT, "research", "original_trader_reconstruction", "solar_family", "src")
sys.path.insert(0, SRC)
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
from otr_engine import load_ledger  # noqa: E402  (data parsing only)
from solarwave import SolarWaveParams, solar_wave_full  # noqa: E402

OUT = os.path.join(ROOT, "runs", "OTR_R1_SERIES", "out")
LEDGER = os.path.join(ROOT, "research", "03_reverse_engineering", "ledgers", "t2_canonical_1m.csv")
LABELS = os.path.join(OUT, "r12f_flip_features.csv")

PV = 20.0
COMM = 2.09
BREQ = 20


def sim(bars, sig, ts, use_b1, guard, X=1600.0, K=3, C=1000.0, noon=720,
        eve_w=360, use_gate=True, gate_fn=None):
    """Independent event loop.  Decisions at bar close, fills next bar open,
    inclusive close-vs-TS exit, T1 stop-and-reverse, session-close flat.
    D-gate evaluated at the entry FILL bar with same-bar exits already realized.
    Records BLOCKED candidates too (for label scoring).
    gate_fn(state, d, i) -> bool(take) overrides the built-in gate when given.
    """
    n = bars["n"]
    opn, close = bars["open"], bars["close"]
    fb, lb = bars["first_bar"], bars["last_bar"]
    t = bars["time"]
    mod = ((t - t.astype("datetime64[D]")).astype("timedelta64[s]").astype(np.int64) // 60)
    # minutes since session open
    so = np.zeros(n, np.int64)
    cur = 0
    for i in range(n):
        if fb[i]:
            cur = i
        so[i] = cur
    mins_open = ((t - t[so]).astype("timedelta64[s]").astype(np.int64) // 60)

    taken, blocked = [], []
    pos = 0
    epx, ei = 0.0, -1
    p_exit = False
    p_rev = 0
    p_ent = 0
    st = {"cum": 0.0, "high": 0.0, "consec": {1: 0, -1: 0}, "prior": 0.0,
          "nloss": 0, "nwin": 0, "consec_any": 0, "bigwin": 0.0,
          "cum_pts": 0.0, "high_pts": 0.0, "gross": 0.0, "highg": 0.0}

    def realize(i, px, kind):
        nonlocal pos
        pts = pos * (px - epx)
        pnl = pts * PV - 2 * COMM
        taken.append({"dir": pos, "entry_i": ei, "exit_i": i,
                      "entry_time": str(t[ei]), "exit_time": str(t[i]),
                      "pnl": pnl, "exit_kind": kind,
                      "hold_min": (t[i] - t[ei]).astype("timedelta64[s]").astype(np.int64) / 60.0})
        st["cum"] += pnl
        st["high"] = max(st["high"], st["cum"])
        st["cum_pts"] += pts
        st["high_pts"] = max(st["high_pts"], st["cum_pts"])
        st["gross"] += pts * PV
        st["highg"] = max(st["highg"], st["gross"])
        if pnl < 0:
            st["consec"][pos] += 1
            st["nloss"] += 1
            st["consec_any"] += 1
        else:
            st["consec"][pos] = 0
            st["nwin"] += 1
            st["consec_any"] = 0
            st["bigwin"] = max(st["bigwin"], pnl)
        pos = 0

    def gate_ok(d, i):
        if not use_gate:
            return True
        if gate_fn is not None:
            return gate_fn(st, d, i, mins_open, mod)
        if guard and mins_open[i] < guard:
            return False
        if st["prior"] <= -C and mins_open[i] <= eve_w:
            return False
        if st["high"] >= X and mod[i] >= noon:
            if st["cum"] < 0:
                return False
            if st["consec"][d] >= K:
                return False
        return True

    for i in range(n):
        if fb[i]:
            st["prior"] = st["cum"]
            st["cum"] = st["high"] = 0.0
            st["consec"] = {1: 0, -1: 0}
            st["nloss"] = st["nwin"] = st["consec_any"] = 0
            st["bigwin"] = 0.0
            st["cum_pts"] = st["high_pts"] = 0.0
            st["gross"] = st["highg"] = 0.0
        # ---- fills (orders placed at previous bar close) ----
        if p_exit and pos != 0:
            realize(i, opn[i], "flip")
            p_exit = False
        if p_rev != 0:
            if pos != 0:
                realize(i, opn[i], "flip")
            if gate_ok(p_rev, i):
                pos = p_rev
                epx, ei = opn[i], i
            else:
                blocked.append({"dir": p_rev, "entry_i": i, "entry_time": str(t[i])})
            p_rev = 0
        if p_ent != 0 and pos == 0:
            if gate_ok(p_ent, i):
                pos = p_ent
                epx, ei = opn[i], i
            else:
                blocked.append({"dir": p_ent, "entry_i": i, "entry_time": str(t[i])})
        p_ent = 0
        # ---- decisions at this bar close ----
        s = sig[i]
        if lb[i]:
            if pos != 0:
                realize(i, close[i], "session_close")
            p_exit = False
            p_ent = 0
            p_rev = 0
            continue
        allowed = not (use_b1 and fb[i])
        if pos != 0:
            line = ts[i]
            if not np.isnan(line):
                hit = (pos > 0 and close[i] <= line) or (pos < 0 and close[i] >= line)
                if hit:
                    if allowed and s == -pos and abs(s) == 1 and i >= BREQ:
                        p_rev = s
                    else:
                        p_exit = True
                    continue
        if pos == 0 and abs(s) == 1 and i >= BREQ and allowed:
            p_ent = 1 if s > 0 else -1
    return taken, blocked


def agg(trades):
    p = np.array([x["pnl"] for x in trades])
    d = np.array([x["dir"] for x in trades])
    h = np.array([x["hold_min"] for x in trades])
    w = p > 0
    eq = np.cumsum(p)
    dd = eq - np.maximum.accumulate(np.concatenate([[0.0], eq]))[1:]
    return dict(n=len(p), L=int((d > 0).sum()), S=int((d < 0).sum()),
                net=round(float(p.sum()), 2), wr=round(float(w.mean() * 100), 2),
                pf=round(float(p[w].sum() / -p[~w].sum()), 4),
                dd=round(float(dd.min()), 2), hold=round(float(h.mean()), 2),
                holdL=round(float(h[d > 0].mean()), 2), holdS=round(float(h[d < 0].mean()), 2),
                lw=round(float(p.max()), 2), ll=round(float(p.min()), 2))


def score_labels(taken, blocked, labels):
    tk = {x["entry_time"][:16].replace(" ", "T") for x in taken}
    bk = {x["entry_time"][:16].replace(" ", "T") for x in blocked}
    res = {"HARD": [0, 0], "SOFT": [0, 0], "EPS": [0, 0]}
    fails = []
    for r in labels:
        key = r["entry_time"][:16]
        want = r["label"] == "TAKE"
        c = r["certainty"]
        if key in tk:
            got = True
        elif key in bk:
            got = False
        else:
            res[c][1] += 1
            fails.append((c, r["label"], key, "MISSING(no candidate)"))
            continue
        if got == want:
            res[c][0] += 1
        else:
            res[c][1] += 1
            fails.append((c, r["label"], key, "got TAKE" if got else "got SKIP"))
    return res, fails


def main():
    labels = list(csv.DictReader(open(LABELS, newline="")))
    bars = load_ledger(LEDGER)

    print("=" * 78)
    print("CONFIG A (label config: ledger EARLY signals, no B1, guard=3)")
    tkA, bkA = sim(bars, bars["signal_trade"], bars["trailing_stop"],
                   use_b1=False, guard=3)
    resA, failsA = score_labels(tkA, bkA, labels)
    print("labels:", {k: f"{v[0]}/{v[0]+v[1]}" for k, v in resA.items()})
    for f in failsA:
        print("  FAIL:", f)
    print("aggregate:", agg(tkA))
    # no-gate base for reference
    tk0, _ = sim(bars, bars["signal_trade"], bars["trailing_stop"],
                 use_b1=False, guard=0, use_gate=False)
    print("no-gate base:", agg(tk0))

    print("=" * 78)
    print("CONFIG B (master config: LATE regenerated signals, B1, no guard)")
    res = solar_wave_full(bars["open"], bars["high"], bars["low"], bars["close"],
                          SolarWaveParams(pullback_early=False), start_up=False)
    sigL = res.signal_trade.astype(np.int64)
    tsL = res.trailing_stop
    tkB, bkB = sim(bars, sigL, tsL, use_b1=True, guard=0)
    print("aggregate:", agg(tkB))
    print("CLAIMED:   n=5011 L2483/S2528 net=244589 wr=39.83 pf=1.127 dd=-29077 "
          "hold=93.02 (105.61/80.65)")
    resB, failsB = score_labels(tkB, bkB, labels)
    print("labels under config B:", {k: f"{v[0]}/{v[0]+v[1]}" for k, v in resB.items()})
    for f in failsB[:20]:
        print("  FAIL:", f)
    tkB0, _ = sim(bars, sigL, tsL, use_b1=True, guard=0, use_gate=False)
    print("no-gate late+B1:", agg(tkB0))


if __name__ == "__main__":
    main()
