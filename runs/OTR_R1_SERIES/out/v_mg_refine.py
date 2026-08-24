"""V3 MASTER-GAP HUNTER — bounded refinements on top of the D-gate.

Method: entry gates only REMOVE legs and never change other legs' prices/times
(T1-only flip chains; certified by hunt_D and reused here), so any equity-state
gate can be replayed exactly over the once-generated leg stream.

Two leg streams:
  LATE  = run_r1g run_integrated(use_gate=False, entry_types=(1,), B1) — the
          registered INT_T1only signal stream; used for MASTER aggregates.
  EARLY = hunt_D_base_trades.json cache (early-mode T1+reverse) — the stream the
          42 HARD Jan labels are keyed to; used for the label constraint with
          hunt_D semantics (guard=3, eve window 360).

Candidate gate = D base (X,K,C) + extensions:
  X2    second armed threshold active pre-noon
  eveP  evening block unless |prior| <= eveP
  cd    reentry cooldown bars after a taken pure touch-exit
  capM  max taken entries per session
  stopN consecutive losses ANY side -> block all (optional re-enable after R min)
  lossN total session losses -> block all (latch)

Hard constraint: 42/42 HARD labels. Selection: master-closeness score.
Writes v_mg_refine.json. No existing file modified.
"""
import json
import os
import sys
from collections import defaultdict
from itertools import combinations

import numpy as np

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
SRC = os.path.join(ROOT, "research", "original_trader_reconstruction", "solar_family", "src")
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
sys.path.insert(0, SRC)
from otr_engine import load_ledger, POINT_VALUE, BARS_REQUIRED  # noqa: E402
from solarwave import SolarWaveParams, solar_wave_full  # noqa: E402

OUT = os.path.join(ROOT, "runs", "OTR_R1_SERIES", "out")

# ---------------------------------------------------------------- late leg stream
print("[v_mg_refine] building LATE-mode leg stream ...", flush=True)
b = load_ledger(os.path.join(ROOT, "research", "03_reverse_engineering", "ledgers", "t2_canonical_1m.csv"))
res = solar_wave_full(b["open"], b["high"], b["low"], b["close"],
                      SolarWaveParams(pullback_early=False), start_up=False)
st = res.signal_trade.astype(np.int64)
ts_arr = res.trailing_stop
n = b["n"]
close, opn = b["close"], b["open"]
first_bar, last_bar = b["first_bar"], b["last_bar"]
tarr = b["time"]
mod = ((tarr - tarr.astype("datetime64[D]")).astype("timedelta64[s]").astype(np.int64) // 60).astype(np.int64)
sess_id = b["session_id"]
sess_open_i = np.zeros(n, dtype=np.int64)
cur = 0
for i in range(n):
    if first_bar[i]:
        cur = i
    sess_open_i[i] = cur
mins_open = ((tarr - tarr[sess_open_i]).astype("timedelta64[s]").astype(np.int64) // 60).astype(np.int64)
COMM = 2.09
last_idx = {}
for i in range(n):
    last_idx[sess_id[i]] = i
sess_end_day = {sid: str(tarr[i])[:10] for sid, i in last_idx.items()}


def gen_legs_late():
    """run_r1g.run_integrated with use_gate=False, entry_types=(1,), B1 on."""
    trades = []
    pos = 0
    entry_px = 0.0
    entry_i = -1
    pend_entry = 0
    pend_exit = False
    pend_reverse = 0

    def realize(i_exit, px_exit, kind):
        nonlocal pos
        pnl = pos * (px_exit - entry_px) * POINT_VALUE - 2 * COMM
        trades.append({"dir": pos, "entry_i": entry_i, "exit_i": i_exit, "pnl": pnl,
                       "exit_kind": kind,
                       "hold_min": float((tarr[i_exit] - tarr[entry_i]).astype("timedelta64[s]").astype(np.int64)) / 60.0})
        pos = 0

    for i in range(n):
        if pend_exit and pos != 0:
            realize(i, opn[i], "flip")
            pend_exit = False
        if pend_reverse != 0:
            if pos != 0:
                realize(i, opn[i], "flip")
            pos = pend_reverse
            entry_px, entry_i = opn[i], i
            pend_reverse = 0
        if pend_entry != 0 and pos == 0:
            pos = pend_entry
            entry_px, entry_i = opn[i], i
            pend_entry = 0
        pend_entry = 0
        sig = st[i]
        if last_bar[i]:
            if pos != 0:
                realize(i, close[i], "session_close")
            pend_exit = False
            pend_entry = 0
            pend_reverse = 0
            continue
        decision_allowed = not first_bar[i]
        if pos != 0:
            line = ts_arr[i]
            if not np.isnan(line):
                hit = (pos > 0 and close[i] <= line) or (pos < 0 and close[i] >= line)
                if hit:
                    if decision_allowed and sig == -pos and abs(sig) == 1 and i >= BARS_REQUIRED:
                        pend_reverse = sig
                    else:
                        pend_exit = True
                    continue
        if pos == 0 and sig != 0 and i >= BARS_REQUIRED and decision_allowed:
            if abs(sig) == 1:
                pend_entry = 1 if sig > 0 else -1
    return trades


late_raw = gen_legs_late()
print(f"[v_mg_refine] late nogate legs: {len(late_raw)}", flush=True)


def annotate(trades):
    for j, t in enumerate(trades):
        ei = t["entry_i"]
        t["session"] = int(sess_id[ei])
        t["mins_open"] = int(mins_open[ei])
        t["mod"] = int(mod[ei])
        t["exit_day"] = sess_end_day[int(sess_id[t["exit_i"]])]
        prev = trades[j - 1] if j > 0 else None
        nxt = trades[j + 1] if j + 1 < len(trades) else None
        t["prev_j"] = j - 1 if (prev is not None and prev["exit_i"] == ei
                                and prev["session"] == t["session"]) else None
        t["rev_exit"] = bool(nxt is not None and nxt["entry_i"] == t["exit_i"])
        t["touch_exit"] = (t["exit_kind"] != "session_close") and not t["rev_exit"]
    return trades


LATE = annotate(late_raw)

# ---------------------------------------------------------------- early stream + labels
with open(os.path.join(OUT, "hunt_D_base_trades.json")) as f:
    EARLY = json.load(f)["trades"]
for j, t in enumerate(EARLY):
    prev = EARLY[j - 1] if j > 0 else None
    nxt = EARLY[j + 1] if j + 1 < len(EARLY) else None
    t["rev_exit"] = bool(nxt is not None and nxt["entry_i"] == t["exit_i"])
    t["touch_exit"] = (t["exit_kind"] != "session_close") and not t["rev_exit"]
print(f"[v_mg_refine] early base trades: {len(EARLY)}", flush=True)

import csv  # noqa: E402
HARD = {}
with open(os.path.join(OUT, "r12f_flip_features.csv"), newline="") as f:
    for r in csv.DictReader(f):
        if r["certainty"] == "HARD":
            HARD[r["entry_time"]] = r["label"]
assert len(HARD) == 42, len(HARD)


# ---------------------------------------------------------------- gate replay
def replay(trades, cfg, early_mode=False):
    """Replay gate over a leg stream. Returns (taken_list, decisions dict by entry_time
    if early_mode)."""
    X = cfg.get("X", 1600.0)
    K = cfg.get("K", 3)
    C = cfg.get("C", 1000.0)
    X2 = cfg.get("X2")
    eveP = cfg.get("eveP")
    cd = cfg.get("cd", 0)
    capM = cfg.get("capM")
    stopN = cfg.get("stopN")
    stopR = cfg.get("stopR")           # re-enable minutes for stopN (None = latch)
    lossN = cfg.get("lossN")
    guard = 3 if early_mode else 0     # hunt_D guard on early stream; B1 already in late

    taken = []
    decisions = {}
    cur_s = None
    cum = high = 0.0
    consec = {1: 0, -1: 0}
    consec_any = 0
    losses = 0
    n_taken_sess = 0
    last_touch_exit_i = None
    last_loss_exit_t = None            # np.datetime64 of last loss exit (for stopR)
    sess_net = {}
    taken_flags = [False] * len(trades)

    for j, t in enumerate(trades):
        s = t["session"]
        if s != cur_s:
            if cur_s is not None:
                sess_net[cur_s] = cum
            cur_s = s
            cum = high = 0.0
            consec = {1: 0, -1: 0}
            consec_any = 0
            losses = 0
            n_taken_sess = 0
            last_touch_exit_i = None
            last_loss_exit_t = None
        prior = sess_net.get(s - 1, 0.0)
        d = t["dir"]
        blocked = False
        why = None
        if guard and t["mins_open"] < guard:
            blocked, why = True, "guard"
        if not blocked and t["mins_open"] <= 360 and prior <= -C:
            blocked, why = True, "eveC"
        if not blocked and eveP is not None and t["mins_open"] <= 360 and abs(prior) > eveP:
            blocked, why = True, "eveP"
        armed = (high >= X and t["mod"] >= 720) or (X2 is not None and high >= X2)
        if not blocked and armed:
            if cum < 0:
                blocked, why = True, "armed_red"
            elif consec[d] >= K:
                blocked, why = True, "armed_dir"
        if not blocked and cd:
            is_rev_cont = (t["prev_j"] is not None and taken_flags[t["prev_j"]]) if not early_mode else \
                          (j > 0 and trades[j - 1]["exit_i"] == t["entry_i"] and taken_flags[j - 1])
            if (not is_rev_cont and last_touch_exit_i is not None
                    and (t["entry_i"] - last_touch_exit_i) < cd):
                blocked, why = True, "cooldown"
        if not blocked and capM is not None and n_taken_sess >= capM:
            blocked, why = True, "cap"
        if not blocked and stopN is not None and consec_any >= stopN:
            ok_re = False
            if stopR is not None and last_loss_exit_t is not None:
                age = (np.datetime64(t["entry_time"]) - last_loss_exit_t).astype("timedelta64[s]").astype(np.int64) / 60.0 \
                    if early_mode else (tarr[t["entry_i"]] - last_loss_exit_t).astype("timedelta64[s]").astype(np.int64) / 60.0
                if age >= stopR:
                    ok_re = True
                    consec_any = 0
            if not ok_re:
                blocked, why = True, "stopN"
        if not blocked and lossN is not None and losses >= lossN:
            blocked, why = True, "lossN"

        if early_mode:
            decisions[t["entry_time"]] = ("SKIP" if blocked else "TAKE", why)
        if not blocked:
            taken_flags[j] = True
            taken.append(t)
            n_taken_sess += 1
            pnl = t["pnl"]
            cum += pnl
            high = max(high, cum)
            if pnl <= 0:
                consec[d] += 1
                consec_any += 1
                losses += 1
                last_loss_exit_t = (np.datetime64(t["exit_time"]) if early_mode
                                    else tarr[t["exit_i"]])
            else:
                consec[d] = 0
                consec_any = 0
            if t["touch_exit"]:
                last_touch_exit_i = t["exit_i"]
    return taken, decisions


def label_check(cfg):
    _, dec = replay(EARLY, cfg, early_mode=True)
    bad = []
    for et, lab in HARD.items():
        got = dec.get(et, ("MISSING", None))[0]
        if got != lab:
            bad.append((et, lab, got))
    return len(HARD) - len(bad), bad


def agg(trades):
    p = np.array([t["pnl"] for t in trades])
    d = np.array([t["dir"] for t in trades])
    h = np.array([t["hold_min"] for t in trades])
    w = p > 0
    gl = p[~w].sum()
    eq = np.cumsum(p)
    dd = eq - np.maximum.accumulate(np.concatenate([[0.0], eq]))[1:]
    return {"n": len(trades), "L": int((d > 0).sum()), "S": int((d < 0).sum()),
            "net": round(float(p.sum()), 2), "wr": round(float(w.mean() * 100), 2),
            "pf": round(float(p[w].sum() / -gl), 3) if gl < 0 else None,
            "dd": round(float(dd.min()), 2), "hold": round(float(h.mean()), 2),
            "holdL": round(float(h[d > 0].mean()), 2), "holdS": round(float(h[d < 0].mean()), 2),
            "lnet": round(float(p[d > 0].sum()), 2), "snet": round(float(p[d < 0].sum()), 2),
            "lw": round(float(p.max()), 2), "ll": round(float(p.min()), 2)}


T = {"n": 4351, "L": 2166, "S": 2185, "net": 292172.82, "wr": 40.29, "pf": 1.18,
     "dd": -32677.42, "holdL": 105.85, "holdS": 82.56, "lnet": 214911.12, "snet": 77261.70}


def score(a):
    return (2 * abs(a["n"] - T["n"]) / T["n"]
            + 2 * abs(a["net"] - T["net"]) / T["net"]
            + abs(a["wr"] - T["wr"]) / T["wr"]
            + abs(a["pf"] - T["pf"]) / T["pf"]
            + abs(a["dd"] - T["dd"]) / abs(T["dd"])
            + abs(a["holdL"] - T["holdL"]) / T["holdL"]
            + abs(a["holdS"] - T["holdS"]) / T["holdS"]
            + 0.5 * abs(a["lnet"] - T["lnet"]) / T["lnet"]
            + 0.5 * abs(a["snet"] - T["snet"]) / abs(T["snet"]))


# jan subset-match (r1g semantics) for finalists
TGT = {"2023-01-03": (4, 5863.28, 8, -6163.44, 3050.82, -1179.18),
       "2023-01-04": (5, 3859.10, 9, -5007.60, 1865.82, -899.18),
       "2023-01-05": (2, 2611.64, 4, -2641.72, 2310.82, -889.18),
       "2023-01-06": (5, 6314.10, 5, -3320.90, 4210.82, -1384.18),
       "2023-01-09": (2, 6116.64, 1, -854.18, 3170.82, -854.18),
       "2023-01-10": (5, 3744.10, 4, -2551.72, 1370.82, -1084.18),
       "2023-01-11": (2, 3106.64, 2, -1338.36, 2190.82, -749.18),
       "2023-01-12": (5, 4704.10, 11, -8025.98, 1535.82, -1204.18),
       "2023-01-13": (3, 3337.46, 3, -1912.54, 1885.82, -809.18),
       "2023-01-16": (2, 641.64, 1, -34.18, 555.82, -34.18),
       "2023-01-17": (3, 1322.46, 3, -1737.54, 590.82, -1089.18)}


def jan_score(trades):
    by = defaultdict(list)
    for t in trades:
        if t["exit_day"] in TGT:
            by[t["exit_day"]].append(t)
    total_rm, cents, nosol = 0, 0, 0
    for day in sorted(TGT):
        nW, gW, nL, gL, LW, LL = TGT[day]
        ours = by.get(day, [])
        n_t = nW + nL
        k = len(ours) - n_t
        best = None
        if 0 <= k <= 7:
            for rem in combinations(range(len(ours)), k):
                keep = [t for jj, t in enumerate(ours) if jj not in rem]
                p = [t["pnl"] for t in keep]
                w = [x for x in p if x > 0]
                l = [x for x in p if x <= 0]
                if len(w) != nW or len(l) != nL:
                    continue
                if abs(max(w) - LW) > 75 or abs(min(l) - LL) > 75:
                    continue
                err = abs(sum(w) - gW) + abs(sum(l) - gL) + abs(max(w) - LW) + abs(min(l) - LL)
                if best is None or err < best[0]:
                    best = (err, rem)
        if best is None:
            nosol += 1
        else:
            total_rm += len(best[1])
            if best[0] < 0.02:
                cents += 1
    return total_rm, cents, nosol


# ---------------------------------------------------------------- sanity: reproduce
base_cfg = {"X": 1600.0, "K": 3, "C": 1000.0}
tk, _ = replay(LATE, base_cfg)
a0 = agg(tk)
print(f"[sanity] base replay: n={a0['n']} net={a0['net']} (expect 5011 / 244589.02)", flush=True)
ok42, bad = label_check(base_cfg)
print(f"[sanity] base label check: {ok42}/42 {bad[:4]}", flush=True)
assert a0["n"] == 5011 and abs(a0["net"] - 244589.02) < 0.5
assert ok42 == 42, bad

# ---------------------------------------------------------------- stage 1 sweeps
grid = []
for X in (1550, 1600, 1650, 1700, 1750, 1800, 1850, 1900, 1937):
    for C in (300.2, 500, 700, 1000, 1328.5):
        grid.append({"X": float(X), "K": 3, "C": float(C), "fam": "XC"})
for X2 in (2000, 2500, 3000, 3500, 4000):
    grid.append({"X2": float(X2), "fam": "X2"})
for eveP in (300, 500, 1000, 1500, 2000, 3000):
    grid.append({"eveP": float(eveP), "fam": "eveP"})
for cd in (2, 3, 5, 8, 10, 15, 20, 30):
    grid.append({"cd": cd, "fam": "cd"})
for capM in (16, 17, 18, 20, 22, 25, 30):
    grid.append({"capM": capM, "fam": "cap"})
for stopN in (3, 4, 5, 6, 8):
    for stopR in (None, 60, 120):
        grid.append({"stopN": stopN, "stopR": stopR, "fam": "stopN"})
for lossN in (8, 10, 11, 12, 14, 16, 20):
    grid.append({"lossN": lossN, "fam": "lossN"})

rows = []
for g in grid:
    cfg = {"X": 1600.0, "K": 3, "C": 1000.0}
    cfg.update({k: v for k, v in g.items() if k != "fam"})
    okN, bad = label_check(cfg)
    tk, _ = replay(LATE, cfg)
    a = agg(tk)
    sc = score(a)
    rows.append({"cfg": {k: v for k, v in cfg.items()}, "fam": g["fam"], "hard": okN,
                 "agg": a, "score": round(sc, 4)})

rows.sort(key=lambda r: (r["hard"] != 42, r["score"]))
print("\n=== STAGE 1 (top 30; PASS=42/42 hard) ===")
print(f"[base]                            score={score(a0):.4f} n={a0['n']} net={a0['net']:.0f}")
for r in rows[:30]:
    c = r["cfg"]
    tag = {k: v for k, v in c.items() if not (k == "X" and v == 1600.0)
           and not (k == "K" and v == 3) and not (k == "C" and v == 1000.0)}
    a = r["agg"]
    status = "PASS" if r["hard"] == 42 else "FAIL" + str(r["hard"])
    print(f"{status} {r['fam']:6} {str(tag):42} "
          f"score={r['score']:.4f} n={a['n']} net={a['net']:9.0f} wr={a['wr']} pf={a['pf']} "
          f"dd={a['dd']:.0f} hold={a['holdL']}/{a['holdS']}")

# family-wise winners that pass labels and beat base
base_score = score(a0)
passers = [r for r in rows if r["hard"] == 42 and r["score"] < base_score]
best_by_fam = {}
for r in passers:
    f = r["fam"]
    if f not in best_by_fam or r["score"] < best_by_fam[f]["score"]:
        best_by_fam[f] = r
print("\n=== family winners (pass + beat base) ===")
for f, r in best_by_fam.items():
    print(f"{f}: {r['cfg']} score={r['score']}")

# ---------------------------------------------------------------- stage 2 combos
def merge(*cfgs):
    out = {"X": 1600.0, "K": 3, "C": 1000.0}
    for c in cfgs:
        for k, v in c.items():
            if k in ("X", "K", "C") and v in (1600.0, 3, 1000.0):
                continue
            out[k] = v
    return out


fams = list(best_by_fam.keys())
combo_rows = []
# pairwise + triple combos of family winners; also allow 2nd-best per family
cand_per_fam = defaultdict(list)
for r in passers:
    cand_per_fam[r["fam"]].append(r)
for f in cand_per_fam:
    cand_per_fam[f] = sorted(cand_per_fam[f], key=lambda r: r["score"])[:2]

import itertools  # noqa: E402
for k in (2, 3):
    for fs in itertools.combinations(fams, k):
        pools = [cand_per_fam[f] for f in fs]
        for picks in itertools.product(*pools):
            cfg = merge(*[p["cfg"] for p in picks])
            okN, bad = label_check(cfg)
            if okN != 42:
                combo_rows.append({"cfg": cfg, "hard": okN, "agg": None, "score": 99})
                continue
            tk, _ = replay(LATE, cfg)
            a = agg(tk)
            combo_rows.append({"cfg": cfg, "hard": 42, "agg": a, "score": round(score(a), 4)})

combo_rows.sort(key=lambda r: r["score"])
print("\n=== STAGE 2 combos (top 20) ===")
for r in combo_rows[:20]:
    if r["agg"] is None:
        continue
    a = r["agg"]
    tag = {k: v for k, v in r["cfg"].items() if not (k == "X" and v == 1600.0)
           and not (k == "K" and v == 3) and not (k == "C" and v == 1000.0)}
    print(f"score={r['score']:.4f} {str(tag):55} n={a['n']} net={a['net']:9.0f} wr={a['wr']} "
          f"pf={a['pf']} dd={a['dd']:.0f} hold={a['holdL']}/{a['holdS']} "
          f"L/S={a['L']}/{a['S']} lnet={a['lnet']:.0f} snet={a['snet']:.0f}")

# finalists: jan subset check
final = ([r for r in combo_rows if r["agg"] is not None][:5]
         + [r for r in rows if r["hard"] == 42][:5])
seen = set()
print("\n=== FINALISTS with Jan subset-match (base: rm6 cents5 nosol2) ===")
out_final = []
for r in final:
    key = json.dumps(r["cfg"], sort_keys=True)
    if key in seen:
        continue
    seen.add(key)
    tk, _ = replay(LATE, r["cfg"])
    rm, cents, nosol = jan_score(tk)
    a = r["agg"]
    print(f"score={r['score']:.4f} {r['cfg']} | jan rm={rm} cents={cents} nosol={nosol}")
    out_final.append({"cfg": r["cfg"], "score": r["score"], "agg": a,
                      "jan": {"rm": rm, "cents": cents, "nosol": nosol}})

tk0, _ = replay(LATE, base_cfg)
rm0, c0, ns0 = jan_score(tk0)
print(f"[base jan] rm={rm0} cents={c0} nosol={ns0}")

with open(os.path.join(OUT, "v_mg_refine.json"), "w") as f:
    json.dump({"base": {"cfg": base_cfg, "agg": a0, "score": round(base_score, 4),
                        "jan": {"rm": rm0, "cents": c0, "nosol": ns0}},
               "stage1": rows, "stage2_top": combo_rows[:40], "finalists": out_final},
              f, indent=1, default=str)
print("[v_mg_refine] done", flush=True)
