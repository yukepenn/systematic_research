"""Family C pass 4: higher-timeframe Solar Wave state + MA-slope dead-zone gates.

For P-minute resampled closes (P in grid), run the same solar recurrence
(90/179/5/10/10) and map the last-completed-HT-bar state onto each 1-min signal
bar. Features per flip: HT dir match, HT weak, d*(close-TS_HT), d*(close-TV_HT),
bars since HT flip, HT bse. Plus SMA/EMA slope features with dead zones.
Scan singles and pairs for perfect separation: 8/8 HARD skips vs 0/112 takes.
"""
import os, sys, itertools
import numpy as np
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.join(ROOT, r"research\original_trader_reconstruction\solar_family\src"))
sys.path.insert(0, os.path.join(ROOT, r"src\analytics"))
sys.path.insert(0, os.path.join(ROOT, r"runs\OTR_R1_SERIES\out"))

from otr_engine import load_ledger
from solarwave import SolarWaveParams, solar_wave
from hunt_C import instrumented_state, jan_slice, base_trades

LEDGER = os.path.join(ROOT, r"research\03_reverse_engineering\ledgers\t2_canonical_1m.csv")
FEAT = os.path.join(ROOT, r"runs\OTR_R1_SERIES\out\r12f_flip_features.csv")
OUT = os.path.join(ROOT, r"runs\OTR_R1_SERIES\out")

bars = load_ledger(LEDGER)
n = bars["n"]
o, h, l, c = bars["open"], bars["high"], bars["low"], bars["close"]
time = bars["time"]

# ---------- HT solar ----------
# resample: group 1-min bars into P-bar blocks within the full series (index-based,
# like an NT8 P-minute series built from the same data; block boundary = every P bars
# from series start is NOT how NT8 does it (NT8 uses clock time), so use clock-time
# blocks: floor(epoch_minutes / P).
epoch_min = time.astype("datetime64[m]").astype(np.int64)


def ht_state_features(P):
    grp = epoch_min // P
    # last 1-min bar of each block
    is_last = np.zeros(n, bool)
    is_last[:-1] = grp[1:] != grp[:-1]
    is_last[-1] = True
    idx_last = np.flatnonzero(is_last)
    cP = c[idx_last]
    r = solar_wave(cP, SolarWaveParams())
    # HT-bar index applicable at 1-min bar j = last completed block strictly before j's block
    # nt8: at the close of 1-min bar j, the P-min series' current bar closes only if j is last of block.
    # Use state as of the most recent COMPLETED HT bar at time of bar j's close (inclusive if j closes the block).
    ht_i_for_bar = np.searchsorted(idx_last, np.arange(n))  # first idx_last >= j
    ht_i_for_bar = np.where(idx_last[np.minimum(ht_i_for_bar, len(idx_last)-1)] == np.arange(n),
                            ht_i_for_bar, ht_i_for_bar - 1)  # inclusive close else previous
    ht_i_for_bar = np.clip(ht_i_for_bar, 0, len(idx_last) - 1)
    flipP = np.abs(r.signal_trade) == 1
    flip_pos = np.flatnonzero(flipP)

    def feats(j):
        hi = ht_i_for_bar[j]
        sgn = 1 if r.is_up[hi] else -1
        ts_ = r.trailing_stop[hi]; tv_ = r.trend_vector[hi]
        last_flips = flip_pos[flip_pos <= hi]
        since_flip = hi - last_flips[-1] if len(last_flips) else 10**6
        return dict(sgn=sgn, weak=int(abs(r.signal_trend[hi]) == 1),
                    ts=ts_, tv=tv_, since_flip=int(since_flip),
                    wave=int(abs(r.signal_wave[hi])))
    return feats


# ---------- MA slopes ----------
csum = np.cumsum(c)
smas = {}
for N in (20, 30, 50, 60, 90, 120, 180, 240, 360, 480):
    s = np.full(n, np.nan)
    s[N-1:] = (csum[N-1:] - np.concatenate([[0.0], csum[:-N]])) / N
    smas[N] = s

# ---------- trades & labels ----------
sl = jan_slice(bars)
trades = base_trades(sl)
lab = pd.read_csv(FEAT)[["entry_time", "label", "certainty"]]
lmap = dict(zip(lab.entry_time, zip(lab.label, lab.certainty)))

rows = []
ht_feats = {P: ht_state_features(P) for P in (2, 3, 4, 5, 10, 15, 30, 60, 120)}
for t in trades:
    j = t["entry_i"] - 1
    d = 1 if t["dir"] > 0 else -1
    lb, ct = lmap[t["entry_time"]]
    row = dict(entry_time=t["entry_time"], d=d, label=lb, certainty=ct)
    for P, f in ht_feats.items():
        ft = f(j)
        row[f"HT{P}_match"] = d * ft["sgn"]                 # +1 with-HT, -1 against
        row[f"HT{P}_weak"] = ft["weak"]
        row[f"HT{P}_dTS"] = d * (c[j] - ft["ts"])
        row[f"HT{P}_dTV"] = d * (c[j] - ft["tv"])
        row[f"HT{P}_sinceflip"] = ft["since_flip"]
        row[f"HT{P}_wave"] = ft["wave"]
        row[f"HT{P}_match_or_weak"] = 1 if (d * ft["sgn"] > 0 or ft["weak"]) else 0
        row[f"HT{P}_match_and_strong"] = 1 if (d * ft["sgn"] > 0 and not ft["weak"]) else 0
    for N, s in smas.items():
        for k in (10, 20, 30, 60):
            if j - k >= N:
                row[f"slope{N}_{k}"] = d * (s[j] - s[j-k])
        row[f"dist{N}"] = d * (c[j] - s[N-1] if np.isnan(s[j]) else c[j] - s[j])
    rows.append(row)

df = pd.DataFrame(rows)
df.to_csv(os.path.join(OUT, "hunt_C_htf_features.csv"), index=False)

y = (df.label == "SKIP") & (df.certainty == "HARD")
takes = df.label == "TAKE"
mask = y | takes          # exclude SOFT skips from the constraint set
sub = df[mask]
ys = y[mask].to_numpy()

atoms = {}
for cname in sub.columns:
    if cname in ("entry_time", "label", "certainty", "d"):
        continue
    v = sub[cname].astype(float)
    arr = v.to_numpy()
    vals = np.unique(arr[np.isfinite(arr)])
    if len(vals) < 2:
        continue
    mids = (vals[:-1] + vals[1:]) / 2
    if len(mids) > 60:
        mids = np.quantile(mids, np.linspace(0, 1, 60))
    for thr in mids:
        atoms[f"{cname}<={thr:.3f}"] = arr <= thr
        atoms[f"{cname}>={thr:.3f}"] = arr >= thr

names = list(atoms.keys())
mat = np.array([atoms[nm] for nm in names])
nskip = int(ys.sum())
print(f"constraint set: {len(sub)} trades, {nskip} HARD skips; atoms: {len(names)}")

singles = [nm for i, nm in enumerate(names)
           if (mat[i] & ys).sum() == nskip and (mat[i] & ~ys).sum() == 0]
print(f"perfect singles: {len(singles)}")
for s_ in singles[:50]:
    print("  ", s_)

clean = [i for i in range(len(names)) if (mat[i] & ~ys).sum() == 0 and (mat[i] & ys).sum() > 0]
covers = [i for i in range(len(names)) if (mat[i] & ys).sum() == nskip]
print(f"clean atoms: {len(clean)}, covering atoms: {len(covers)}")
hits = []
cm = mat[clean]; cov = mat[covers]
for ii in range(len(clean)):
    for jj in range(ii + 1, len(clean)):
        p = cm[ii] | cm[jj]
        if (p & ys).sum() == nskip:
            hits.append(("OR", names[clean[ii]], names[clean[jj]]))
for ii in range(len(covers)):
    for jj in range(ii + 1, len(covers)):
        p = cov[ii] & cov[jj]
        if (p & ys).sum() == nskip and (p & ~ys).sum() == 0:
            hits.append(("AND", names[covers[ii]], names[covers[jj]]))
print(f"perfect pairs: {len(hits)}")
for hh in hits[:80]:
    print("  ", hh)

# best partial: clean atoms by coverage
best = sorted(((int((mat[i] & ys).sum()), names[i]) for i in clean), reverse=True)[:25]
print("\nbest clean atoms (coverage/8):")
for tp, nm in best:
    lab_times = [sub.entry_time.iloc[kk][5:16] for kk in np.flatnonzero(atoms[nm] & ys)]
    print(f"  {tp}/8 {nm} -> {lab_times}")
