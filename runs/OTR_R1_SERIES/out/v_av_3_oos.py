"""TASK V1 part 3 — OUT-OF-SAMPLE: integrated model on Feb-2025 windows W0204 / W0209.

Per-window fresh state: parquet slice [start-1day 18:00, end 17:00], LATE-mode signals
regenerated on the slice only, engine = v_av_1_reimpl.sim (independent re-implementation),
T1-only stop-and-reverse, B1, comm 2.09/side.  Gate ON (X=1600,K=3,C=1000) vs OFF,
plus the 42/42-HARD-surviving alternative rules from part 2 for discrimination.

Targets (trader's own table, $4.18/RT):
  W0204 (2/4-5):  30 trades 15L/15S net -3805.40  LW 3255.82  LL -1024.18  hold 69.5m
  W0209 (2/9-11): 10 trades  4L/6S  net  -891.80                            hold 107.7m
"""
import os
import sys
from itertools import combinations

import numpy as np
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
OUT = os.path.join(ROOT, "runs", "OTR_R1_SERIES", "out")
sys.path.insert(0, OUT)
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
from v_av_1_reimpl import sim, agg  # noqa: E402
from solarwave import SolarWaveParams, solar_wave_full  # noqa: E402

df = pd.read_parquet(os.path.join(ROOT, "research", "scalping_lab", "substrate",
                                  "minute", "NQ", "nq1m_2005_202605.parquet"))
df["time"] = pd.to_datetime(df["time"])

WINDOWS = {
    "W0204": ("2025-02-03 18:00", "2025-02-05 17:00",
              dict(n=30, L=15, S=15, net=-3805.40, lw=3255.82, ll=-1024.18, hold=69.5)),
    "W0209": ("2025-02-08 18:00", "2025-02-11 17:00",
              dict(n=10, L=4, S=6, net=-891.80, hold=107.7)),
}


def make_bars(lo, hi):
    sub = df[(df["time"] >= lo) & (df["time"] <= hi)].reset_index(drop=True)
    t = sub["time"].values
    gap = np.diff(t).astype("timedelta64[m]").astype(np.int64)
    fb = np.zeros(len(sub), bool)
    fb[0] = True
    fb[1:] = gap > 60
    lb = np.zeros(len(sub), bool)
    lb[:-1] = fb[1:]
    lb[-1] = True
    r = solar_wave_full(sub["open"].values, sub["high"].values, sub["low"].values,
                        sub["close"].values, SolarWaveParams(pullback_early=False),
                        start_up=False)
    return {"time": t.astype("datetime64[s]"), "open": sub["open"].values,
            "high": sub["high"].values, "low": sub["low"].values,
            "close": sub["close"].values,
            "first_bar": fb, "last_bar": lb, "n": len(sub)}, \
        r.signal_trade.astype(np.int64), r.trailing_stop


def subset_diff(trades, tgt):
    """Can removing k trades reach the target counts/net?  (only if len>=tgt n)"""
    n_t = tgt["n"]
    k = len(trades) - n_t
    if k < 0:
        return f"IMPOSSIBLE: ours {len(trades)} < target {n_t} (missing {-k} trades)"
    if k > 8:
        return f"skip: would need to remove {k} trades"
    best = None
    for rem in combinations(range(len(trades)), k):
        keep = [t for j, t in enumerate(trades) if j not in rem]
        d = np.array([t["dir"] for t in keep])
        if int((d > 0).sum()) != tgt["L"] or int((d < 0).sum()) != tgt["S"]:
            continue
        p = np.array([t["pnl"] for t in keep])
        err = abs(p.sum() - tgt["net"])
        if "lw" in tgt:
            err += abs(p.max() - tgt["lw"]) + abs(p.min() - tgt["ll"])
        if best is None or err < best[0]:
            best = (err, rem, float(p.sum()))
    if best is None:
        return f"NOSOL at k={k} (L/S counts unreachable)"
    return f"best subset: rm {best[1]} -> net {best[2]:.2f} err ${best[0]:.2f}"


def eve(st, x_mins_open, prior_C=1000.0):
    return st["prior"] <= -prior_C and x_mins_open <= 360


# alternative gates as gate_fn(st, d, i, mins_open, mod) for sim()
def gf_reg(st, d, i, mo, md):
    if st["prior"] <= -1000 and mo[i] <= 360:
        return False
    if st["high"] >= 1600 and md[i] >= 720:
        if st["cum"] < 0 or st["consec"][d] >= 3:
            return False
    return True


def gf_gross(st, d, i, mo, md):
    if st["prior"] <= -1000 and mo[i] <= 360:
        return False
    if st["highg"] >= 1600 and md[i] >= 720:
        if st["gross"] < 0 or st["consec"][d] >= 3:
            return False
    return True


def gf_noon660(st, d, i, mo, md):
    if st["prior"] <= -1000 and mo[i] <= 360:
        return False
    if st["high"] >= 1600 and md[i] >= 660:
        if st["cum"] < 0 or st["consec"][d] >= 3:
            return False
    return True


def gf_x1450(st, d, i, mo, md):
    if st["prior"] <= -1000 and mo[i] <= 360:
        return False
    if st["high"] >= 1450 and md[i] >= 720:
        if st["cum"] < 0 or st["consec"][d] >= 3:
            return False
    return True


def gf_eve_anyred(st, d, i, mo, md):
    if st["prior"] < 0 and mo[i] <= 360:
        return False
    if st["high"] >= 1600 and md[i] >= 720:
        if st["cum"] < 0 or st["consec"][d] >= 3:
            return False
    return True


# loss_side needs extra state -> emulate with wrapper tracking outside sim: use closure
def mk_gf_loss_side(K=4):
    state = {"sess_start": None, "lossc": {1: 0, -1: 0}, "last_seen": None}
    # sim's st lacks per-side loss counts; recompute from consec impossible.
    return None


for wname, (lo, hi, tgt) in WINDOWS.items():
    bars, sig, ts = make_bars(lo, hi)
    print("=" * 78)
    print(f"{wname}: {lo} -> {hi}  bars={bars['n']}  sessions={int(bars['first_bar'].sum())}")
    print(f"TARGET: {tgt}")
    runs = {}
    for name, kw in [
        ("NOGATE", dict(use_gate=False)),
        ("GATE_REG", dict(gate_fn=gf_reg)),
        ("GATE_gross", dict(gate_fn=gf_gross)),
        ("GATE_noon660", dict(gate_fn=gf_noon660)),
        ("GATE_X1450", dict(gate_fn=gf_x1450)),
        ("GATE_eve_anyred", dict(gate_fn=gf_eve_anyred)),
    ]:
        tk, bk = sim(bars, sig, ts, use_b1=True, guard=0, **kw)
        runs[name] = tk
        a = agg(tk) if tk else {"n": 0}
        blocked_times = [b["entry_time"][5:16] for b in bk]
        print(f"  {name:16s} n={a.get('n',0):3d} L{a.get('L','-')}/S{a.get('S','-')} "
              f"net={a.get('net','-'):>9} hold={a.get('hold','-'):>6} "
              f"lw={a.get('lw','-'):>8} ll={a.get('ll','-'):>8}"
              + (f"  blocked={blocked_times}" if blocked_times else ""))
    # distances to target
    for name in ("NOGATE", "GATE_REG"):
        a = agg(runs[name])
        dn = a["n"] - tgt["n"]
        dnet = a["net"] - tgt["net"]
        dh = a["hold"] - tgt["hold"]
        print(f"  {name} vs target: dn={dn:+d} dnet={dnet:+.2f} dhold={dh:+.1f}")
        print(f"    subset-diff: {subset_diff(runs[name], tgt)}")
    # trade lists for the record
    for name in ("NOGATE", "GATE_REG"):
        print(f"  -- {name} trades:")
        for x in runs[name]:
            print(f"     {x['entry_time'][5:16]} {'L' if x['dir']>0 else 'S'} "
                  f"pnl={x['pnl']:>9.2f} hold={x['hold_min']:>6.1f} {x['exit_kind']}")
print("done")
