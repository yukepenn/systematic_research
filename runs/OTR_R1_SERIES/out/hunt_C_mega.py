"""Family C pass 8: mega feature table + beam search (1-3 atom rules).

Constraints: rule must flag all 8 HARD skips and zero of the 112 takes.
SOFT skips scored separately. Atoms are thresholded features, optionally
direction-conditioned.
"""
import os, sys
import numpy as np
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.join(ROOT, r"research\original_trader_reconstruction\solar_family\src"))
sys.path.insert(0, os.path.join(ROOT, r"src\analytics"))
sys.path.insert(0, os.path.join(ROOT, r"runs\OTR_R1_SERIES\out"))

from otr_engine import load_ledger
from solarwave import SolarWaveParams
from hunt_C import instrumented_state, jan_slice, base_trades

LEDGER = os.path.join(ROOT, r"research\03_reverse_engineering\ledgers\t2_canonical_1m.csv")
FEAT = os.path.join(ROOT, r"runs\OTR_R1_SERIES\out\r12f_flip_features.csv")
OUT = os.path.join(ROOT, r"runs\OTR_R1_SERIES\out")

bars = load_ledger(LEDGER)
n = bars["n"]
o, h, l, c, v = bars["open"], bars["high"], bars["low"], bars["close"], bars["volume"]
time = bars["time"]
first_bar = bars["first_bar"]

# session high/low so far, session open
sess_hi = np.empty(n); sess_lo = np.empty(n); sess_op = np.empty(n)
prev_sess_close = np.empty(n)
hi = lo = op = c[0]; pc = np.nan
for i in range(n):
    if first_bar[i]:
        pc = c[i - 1] if i > 0 else np.nan
        hi, lo, op = h[i], l[i], o[i]
    hi = max(hi, h[i]); lo = min(lo, l[i])
    sess_hi[i] = hi; sess_lo[i] = lo; sess_op[i] = op
    prev_sess_close[i] = pc

sl = jan_slice(bars)
trades = base_trades(sl)
lab = pd.read_csv(FEAT)[["entry_time", "label", "certainty"]]
lmap = dict(zip(lab.entry_time, zip(lab.label, lab.certainty)))

# truth-world state per trade (using labels: only TAKE trades update state)
truth_state = []
cal_day_pnl = {}
last_exit_time = None
last_pnl = None
consec_losses = 0
for t in trades:
    lb, ct = lmap[t["entry_time"]]
    et = np.datetime64(t["entry_time"])
    # calendar-day realized pnl before this signal (exit-timestamped)
    day = str(et.astype("datetime64[D]"))
    cum_day = cal_day_pnl.get(day, 0.0)
    flat_min = ((et - last_exit_time) / np.timedelta64(1, "m")) if last_exit_time is not None else 1e6
    truth_state.append(dict(cum_day=cum_day, consec_losses=consec_losses,
                            last_pnl=(last_pnl if last_pnl is not None else 0.0),
                            flat_min=flat_min))
    if lb == "TAKE":
        xt = np.datetime64(t["exit_time"])
        xday = str(xt.astype("datetime64[D]"))
        cal_day_pnl[xday] = cal_day_pnl.get(xday, 0.0) + t["pnl"]
        last_exit_time = xt
        last_pnl = t["pnl"]
        consec_losses = consec_losses + 1 if t["pnl"] < 0 else 0

extra = []
for t, ts in zip(trades, truth_state):
    j = t["entry_i"] - 1
    d = 1 if t["dir"] > 0 else -1
    rng = sess_hi[j] - sess_lo[j]
    pos = (c[j] - sess_lo[j]) / rng if rng > 0 else 0.5
    wd = int((time[j].astype("datetime64[D]").astype(np.int64) + 4) % 7)  # 0=Mon? check unnecessary
    extra.append(dict(
        entry_time=t["entry_time"],
        rng_pos=pos, rng_pos_dir=pos if d > 0 else 1 - pos,
        d_to_sesshi=d * (sess_hi[j] - c[j]), d_to_sesslo=d * (c[j] - sess_lo[j]),
        sess_range=rng,
        d_vs_sessopen=d * (c[j] - sess_op[j]),
        d_vs_prevclose=d * (c[j] - prev_sess_close[j]),
        truth_cumday=ts["cum_day"], truth_consec=ts["consec_losses"],
        truth_lastpnl=ts["last_pnl"], truth_flatmin=min(ts["flat_min"], 5000),
        weekday=wd,
    ))
extra = pd.DataFrame(extra)

m1 = pd.read_csv(os.path.join(OUT, "hunt_C_flip_features.csv"))
m2 = pd.read_csv(os.path.join(OUT, "hunt_C_htf_features.csv")).drop(columns=["label", "certainty", "d"])
m3 = pd.read_csv(os.path.join(OUT, "hunt_C_vol_features.csv")).drop(columns=["label", "certainty", "d"])
mega = m1.merge(m2, on="entry_time").merge(m3, on="entry_time").merge(extra, on="entry_time")
mega.to_csv(os.path.join(OUT, "hunt_C_mega_features.csv"), index=False)

use = mega[(mega.label == "TAKE") | (mega.certainty == "HARD")].reset_index(drop=True)
ys = ((use.label == "SKIP")).to_numpy()
print(f"mega: {mega.shape[1]} cols; constraint set {len(use)} rows, {ys.sum()} skips")

skipcols = {"entry_time", "dir", "label", "certainty", "dir_lab", "pnl", "close_j",
            "leg_id", "a1", "a2", "a3", "a4"}
atoms = {}
dl = (use["d"] == 1).to_numpy()
for cname in use.columns:
    if cname in skipcols:
        continue
    vals_raw = use[cname]
    if vals_raw.dtype == object:
        continue
    arr = vals_raw.astype(float).to_numpy()
    finite = np.isfinite(arr)
    vv = np.unique(arr[finite])
    if len(vv) < 2:
        continue
    mids = (vv[:-1] + vv[1:]) / 2
    if len(mids) > 40:
        mids = np.unique(np.quantile(mids, np.linspace(0, 1, 40)))
    for thr in mids:
        le = arr <= thr
        ge = arr >= thr
        atoms[f"{cname}<={thr:.4g}"] = le
        atoms[f"{cname}>={thr:.4g}"] = ge
        atoms[f"[L]{cname}<={thr:.4g}"] = dl & le
        atoms[f"[S]{cname}<={thr:.4g}"] = (~dl) & le
        atoms[f"[L]{cname}>={thr:.4g}"] = dl & ge
        atoms[f"[S]{cname}>={thr:.4g}"] = (~dl) & ge

names = list(atoms.keys())
mat = np.array([atoms[k] for k in names])
nskip = int(ys.sum())
tp = (mat & ys).sum(axis=1)
fp = (mat & ~ys).sum(axis=1)

singles = np.flatnonzero((tp == nskip) & (fp == 0))
print(f"atoms: {len(names)}; perfect singles: {len(singles)}")
for i in singles[:40]:
    print("  SINGLE", names[i])

clean = np.flatnonzero((fp == 0) & (tp > 0))
# dedupe clean atoms by coverage pattern
seen = {}
for i in clean:
    key = mat[i][ys].tobytes()
    if key not in seen or tp[i] > tp[seen[key]]:
        seen[key] = i
cleanu = sorted(seen.values(), key=lambda i: -tp[i])
print(f"clean atoms: {len(clean)} ({len(cleanu)} unique skip-patterns)")
print("top unique clean patterns:")
for i in cleanu[:15]:
    times = [use.entry_time.iloc[k][5:16] for k in np.flatnonzero(mat[i] & ys)]
    print(f"  {tp[i]}/8 {names[i]} -> {times}")

# OR-pairs and OR-triples over unique clean atoms
hits2 = []
cu = cleanu[:400]
for a_i in range(len(cu)):
    for b_i in range(a_i + 1, len(cu)):
        pat = mat[cu[a_i]] | mat[cu[b_i]]
        if (pat & ys).sum() == nskip:
            hits2.append((names[cu[a_i]], names[cu[b_i]]))
print(f"perfect OR-pairs: {len(hits2)}")
for hh in hits2[:30]:
    print("  OR2", hh)

if not hits2:
    # triples: beam by pattern coverage
    hits3 = []
    for a_i in range(len(cu)):
        pa = mat[cu[a_i]]
        ca = (pa & ys)
        if ca.sum() < 2:
            continue
        for b_i in range(a_i + 1, len(cu)):
            pab = pa | mat[cu[b_i]]
            need = nskip - (pab & ys).sum()
            if need <= 0 or need > 4:
                continue
            for c_i in range(b_i + 1, len(cu)):
                pat = pab | mat[cu[c_i]]
                if (pat & ys).sum() == nskip:
                    hits3.append((names[cu[a_i]], names[cu[b_i]], names[cu[c_i]]))
        if len(hits3) > 500:
            break
    print(f"perfect OR-triples: {len(hits3)} (showing 40)")
    for hh in hits3[:40]:
        print("  OR3", hh)

# AND-pairs over covering atoms
covers = np.flatnonzero(tp == nskip)
order = np.argsort(fp[covers])
covers = covers[order][:600]
hitsA = []
for a_i in range(len(covers)):
    pa = mat[covers[a_i]]
    for b_i in range(a_i + 1, len(covers)):
        pat = pa & mat[covers[b_i]]
        if (pat & ys).sum() == nskip and (pat & ~ys).sum() == 0:
            hitsA.append((names[covers[a_i]], names[covers[b_i]]))
print(f"perfect AND-pairs: {len(hitsA)}")
for hh in hitsA[:30]:
    print("  AND2", hh)
