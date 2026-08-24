"""FAMILY D hunt: risk/equity wrapper with hysteresis.

Approach: the base policy (T1 + reverse_on_flip, comm 2.09/side) generates a
deterministic sequence of independent "legs" (entry fill -> exit fill); an entry
gate only removes legs, it never changes other legs' prices/times.  So any
equity-state gate can be replayed self-consistently over the base trade list.

Candidate rule (from hand analysis of r12f labels):
  * state keyed to the TRADING SESSION (resets at 18:00 ET), realized basis,
    with a trade's PnL realized at its exit FILL bar (reversal exits realize
    at the same bar as the next entry fill -> included in that entry's state).
  * ARMED when session realized high-water mark >= X  (X ~ 1600-1900 $).
  * If ARMED and time-of-day >= noon:
      - block ALL entries while session realized < 0        ("gave back to red")
      - block direction d when d has >= K consecutive losses (per-dir consec)
  * session-open guard: no entries in the first G minutes of a session.
  * evening rule E1: block entries in the first W minutes of a session
    (evening 18:00->midnight for W=360) when the PRIOR session's net <= -C.
"""
from __future__ import annotations

import csv
import json
import os
import sys
from itertools import product

import numpy as np

SRC = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research\research\original_trader_reconstruction\solar_family\src"
sys.path.insert(0, SRC)
import otr_engine as eng  # noqa: E402

OUT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research\runs\OTR_R1_SERIES\out"
LEDGER = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research\research\03_reverse_engineering\ledgers\t2_canonical_1m.csv"
LABELS = os.path.join(OUT, "r12f_flip_features.csv")
BASE_CACHE = os.path.join(OUT, "hunt_D_base_trades.json")


def get_base(bars):
    if os.path.exists(BASE_CACHE):
        with open(BASE_CACHE) as f:
            return json.load(f)
    pol = eng.WrapperPolicy(name="D_base", entry_types=(1,), reverse_on_flip=True, comm_side=2.09)
    res = eng.run_wrapper(bars, pol)
    trades = res["trades"]
    # annotate session info
    sid = bars["session_id"]
    time_arr = bars["time"]
    first_idx = np.flatnonzero(bars["first_bar"])
    sess_open_time = {int(sid[i]): str(time_arr[i]) for i in first_idx}
    for t in trades:
        s = int(sid[t["entry_i"]])
        t["session"] = s
        ot = np.datetime64(sess_open_time[s])
        t["mins_open"] = int((np.datetime64(t["entry_time"]) - ot).astype("timedelta64[s]").astype(np.int64) // 60)
        et = np.datetime64(t["entry_time"])
        t["mod"] = int((et - et.astype("datetime64[D]")).astype("timedelta64[s]").astype(np.int64) // 60)
    def clean(o):
        if isinstance(o, dict):
            return {k: clean(v) for k, v in o.items()}
        if isinstance(o, list):
            return [clean(v) for v in o]
        if isinstance(o, (np.integer,)):
            return int(o)
        if isinstance(o, (np.floating,)):
            return float(o)
        return o
    trades = clean(trades)
    with open(BASE_CACHE, "w") as f:
        json.dump({"trades": trades, "fingerprint": clean(res["fingerprint"])}, f)
    return {"trades": trades, "fingerprint": res["fingerprint"]}


def load_labels():
    rows = []
    with open(LABELS, newline="") as f:
        for r in csv.DictReader(f):
            rows.append(r)
    return rows


def gate_replay(trades, X=1600.0, K=2, noon=720, guard=3, eve_W=0, eve_C=None,
                eve_band=None):
    """Self-consistent replay. Returns list of (trade, taken_bool)."""
    out = []
    cur_s = None
    cum = high = 0.0
    dir_consec = {1: 0, -1: 0}
    sess_net = {}
    for t in trades:
        s = t["session"]
        if s != cur_s:
            if cur_s is not None:
                sess_net[cur_s] = cum
            cur_s = s
            cum = high = 0.0
            dir_consec = {1: 0, -1: 0}
        blocked = False
        # session-open guard
        if guard and t["mins_open"] < guard:
            blocked = True
        # evening rule
        if not blocked and eve_W:
            prior = sess_net.get(s - 1, 0.0)
            if t["mins_open"] <= eve_W:
                if eve_C is not None and prior <= -eve_C:
                    blocked = True
                if eve_band is not None and (-eve_band[1] < prior <= -eve_band[0]):
                    blocked = True
        # armed noon rules
        if not blocked and high >= X and t["mod"] >= noon:
            if cum < 0:
                blocked = True
            elif dir_consec[t["dir"]] >= K:
                blocked = True
        out.append((t, not blocked))
        if not blocked:
            cum += t["pnl"]
            high = max(high, cum)
            if t["pnl"] < 0:
                dir_consec[t["dir"]] += 1
            else:
                dir_consec[t["dir"]] = 0
    sess_net[cur_s] = cum
    return out


def score(replay, labels):
    taken = {t["entry_time"][:16].replace(" ", "T"): tk for t, tk in replay}
    res = {"HARD": [0, 0], "SOFT": [0, 0], "EPS": [0, 0]}
    fails = []
    for r in labels:
        key = r["entry_time"][:16]
        want_take = r["label"] == "TAKE"
        cert = r["certainty"]
        if key not in taken:
            fails.append((cert, r["label"], key, r["dir"], "MISSING_FROM_BASE"))
            res[cert][1] += 1
            continue
        got = taken[key]
        ok = got == want_take
        res[cert][0 if ok else 1] += 0 if not ok else 1
        res[cert][1] += 0 if ok else 1
        if not ok:
            fails.append((cert, r["label"], key, r["dir"], "got TAKE" if got else "got SKIP"))
    # res[cert] = [passes, fails]
    for cert in res:
        n = sum(1 for r in labels if r["certainty"] == cert)
        res[cert][0] = n - res[cert][1]
    return res, fails


def fingerprint(replay):
    pnl = np.array([t["pnl"] for t, tk in replay if tk])
    dirs = np.array([t["dir"] for t, tk in replay if tk])
    holds = np.array([t["hold_min"] for t, tk in replay if tk])
    wins = pnl > 0
    eq = np.cumsum(pnl)
    dd = eq - np.maximum.accumulate(np.concatenate([[0.0], eq]))[1:]
    gw = pnl[wins].sum()
    gl = pnl[~wins].sum()
    return {
        "trades": len(pnl), "net": round(float(pnl.sum()), 2),
        "L": int((dirs > 0).sum()), "S": int((dirs < 0).sum()),
        "WR": round(float(wins.mean() * 100), 2), "PF": round(float(gw / -gl), 3),
        "DD": round(float(dd.min()), 2), "hold": round(float(holds.mean()), 2),
        "hold_L": round(float(holds[dirs > 0].mean()), 2),
        "hold_S": round(float(holds[dirs < 0].mean()), 2),
        "max_win": round(float(pnl.max()), 2), "max_loss": round(float(pnl.min()), 2),
    }


def main():
    bars = eng.load_ledger(LEDGER)
    base = get_base(bars)
    trades = base["trades"]
    labels = load_labels()
    print("base fingerprint:", base["fingerprint"]["trades"], base["fingerprint"]["net"])

    # sanity: base Jan trades vs label rows
    jan = [t for t in trades if t["entry_time"] < "2023-01-21"]
    print(f"base Jan trades: {len(jan)}  label rows: {len(labels)}")

    mode = sys.argv[1] if len(sys.argv) > 1 else "sweep"
    if mode == "sweep":
        results = []
        for X, K, guard, eveC in product(
                [1450, 1550, 1600, 1700, 1800, 1900, 1937.46],
                [2, 3, 4], [0, 3],
                [None, 350, 500, 750, 1000, 1300]):
            rep = gate_replay(trades, X=X, K=K, guard=guard,
                              eve_W=360 if eveC else 0, eve_C=eveC)
            sc, fails = score(rep, labels)
            results.append(((sc["HARD"][1], sc["SOFT"][1], sc["EPS"][1]),
                            dict(X=X, K=K, guard=guard, eveC=eveC), sc, fails))
        results.sort(key=lambda r: r[0])
        for fkey, cfg, sc, fails in results[:12]:
            print(cfg, "HARD", sc["HARD"], "SOFT", sc["SOFT"], "EPS", sc["EPS"])
        best = results[0]
        print("\nBEST", best[1])
        for f in best[3]:
            print("  FAIL:", f)
        rep = gate_replay(trades, X=best[1]["X"], K=best[1]["K"], guard=best[1]["guard"],
                          eve_W=360 if best[1]["eveC"] else 0, eve_C=best[1]["eveC"])
        print("master:", fingerprint(rep))
    else:
        cfg = json.loads(mode)
        rep = gate_replay(trades, **cfg)
        sc, fails = score(rep, labels)
        print(cfg, "HARD", sc["HARD"], "SOFT", sc["SOFT"], "EPS", sc["EPS"])
        for f in fails:
            print("  FAIL:", f)
        print("master:", fingerprint(rep))


if __name__ == "__main__":
    main()
