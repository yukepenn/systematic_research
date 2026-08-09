"""V2 (MEGA PROMPT W0) -- overshoot ratio r, trailing-120-session window.
Mirrors monitor01_reading001.md methodology exactly (theta=179, 1-min sigma basis,
same band edges), only the window changes: trailing 120 sessions instead of trailing
4 calendar quarters. Read-only, zero alpha risk, pure diagnostic per MONITOR-01 protocol.
"""
import sys
import numpy as np
import pandas as pd

REPO = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, REPO + r"\src")
from analytics.dc_overshoot import dc_segments  # noqa: E402

TICK = 0.25
THETA = 179
SIGMA_WIN = 460
BANDS = [2.0, 3.0, 4.3, 6.4, 9.4]

df = pd.read_csv(REPO + r"\runs\B01A_BARS_1M\nq_1m_2022_2026.csv", parse_dates=["time"])
c = df["close"].to_numpy(float)
t = df["time"]
fbos = df["first_bar_of_session"].to_numpy()
sess_id = np.cumsum(fbos)  # 1-indexed session counter
n_sessions_total = sess_id[-1]
print(f"bars={len(c)} sessions_total={n_sessions_total} span={t.iloc[0]} .. {t.iloc[-1]}")

trailing_120_start_sess = n_sessions_total - 120 + 1
mask120 = sess_id >= trailing_120_start_sess
first_bar_120 = np.argmax(mask120)
print(f"trailing-120-session window: session {trailing_120_start_sess}..{n_sessions_total}, "
      f"bar {first_bar_120}..{len(c)-1}, time {t.iloc[first_bar_120]} .. {t.iloc[-1]}")

# causal sigma (1-min basis), computed over the FULL series so the window boundary doesn't
# truncate the trailing-460 lookback (identical convention to monitor01_reading001.md)
absd_ticks = np.abs(np.diff(c, prepend=c[0])) / TICK
sigma = pd.Series(absd_ticks).rolling(SIGMA_WIN, min_periods=SIGMA_WIN).mean().to_numpy()

seg = dc_segments(c, THETA, TICK)
seg["omega_ticks"] = seg["omega"] / TICK
seg["r"] = seg["omega_ticks"] / THETA
seg["sigma_b"] = sigma[seg["i_flip"].to_numpy()]
seg["ratio"] = THETA / seg["sigma_b"]

# full-history baseline (same as reading #1's "r full-hist 1m" column, recomputed for a check)
full = seg.dropna(subset=["sigma_b"])
print(f"\nfull-history segments with sigma: {len(full)}")

# window filter: segment attributed to window by EXIT bar (i_next), matching protocol's
# "segments assigned by exit-bar timestamp" convention
win = full[full.i_next.to_numpy() >= first_bar_120].copy()
print(f"trailing-120-session segments (by exit bar): {len(win)}")

def banded(frame, label):
    rows = []
    for lo, hi in zip(BANDS[:-1], BANDS[1:]):
        cell = frame[(frame.ratio > lo) & (frame.ratio <= hi)]
        if len(cell) == 0:
            continue
        se = cell.r.std(ddof=1) / np.sqrt(len(cell))
        rows.append({"band": f"({lo},{hi}]", "r": cell.r.mean(), "se": se, "n": len(cell)})
    out = pd.DataFrame(rows)
    pooled = frame[(frame.ratio > BANDS[0]) & (frame.ratio <= BANDS[-1])]
    print(f"\n=== {label} ===")
    print(out.round(4).to_string(index=False))
    if len(pooled):
        pse = pooled.r.std(ddof=1) / np.sqrt(len(pooled))
        print(f"pooled [{BANDS[0]},{BANDS[-1]}]: r={pooled.r.mean():.4f} se={pse:.4f} n={len(pooled)}")
    return out

full_bands = banded(full, "FULL-HISTORY baseline (2022-01..2026-07, sanity check vs reading #1)")
win_bands = banded(win, "TRAILING-120-SESSION window (new, V2 deliverable)")

# tick-basis (unbanded) pooled check, same as reading #1's "tick-basis check" line
print(f"\ntick-basis (unbanded) trailing-120-session: r={win.r.mean():.4f} "
      f"mean_omega={win.omega_ticks.mean():.2f} n={len(win)}")
print(f"tick-basis (unbanded) full-history: r={full.r.mean():.4f} "
      f"mean_omega={full.omega_ticks.mean():.2f} n={len(full)}")

# alarm check
print("\n=== alarm check (protocol rule: banded r < 1.05 in EITHER window) ===")
for _, row in win_bands.iterrows():
    flag = "ALARM" if row.r < 1.05 else "ok"
    print(f"  band {row.band}: r={row.r:.4f} n={int(row.n)} -> {flag}")
