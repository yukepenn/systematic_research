"""CURRENT-HEALTH substrate -- EXTENDS the canonical dev window (2022-01-03..2026-05-29, used
for every formal comparison in this campaign) forward to 2026-07-31, the latest bar data already
present in this repo's own price file that is NOT still locked-forward (>=2026-08-01 remains
sealed per research/operational/LOCKED_FORWARD.md). 2026-06-01..2026-07-31 was already read once
for a different purpose in SM11_HOLDOUT_READ (`CURRENT_TRUTH.md` Wave-18 sec E-1: "nothing left
to seal" for that window) -- reusing it here for OBSERVATIONAL health monitoring, not tuning, is
consistent with that prior determination. This is a CONTINUATION run from the same 2022-01-03
start (WARMUP_STANDARD.md's mandatory convention), not a fresh-start slice, so no new warmup
artifact is introduced.

This file is a DELIBERATE near-duplicate of ../../src/substrate.py with only the end-date changed
-- kept separate (not parametrized into the original) so the canonical run and the current-health
run stay visibly, structurally distinct per the owner's own addendum sec3 instruction ("Clearly
distinguish canonical comparison window from current-health window"). Every formula is verified
byte-identical by construction (copied, not re-derived) and the CANONICAL-window correctness gate
below (slicing this extended run back to 2026-05-29 and re-checking against the certified net) is
the proof that extending the window introduced no change to already-certified history."""
import os, sys
import numpy as np, pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
sys.path.insert(0, os.path.join(ROOT, "runs", "W18R1_M1_VOLSEASON", "src"))
import sm01_solarsim as sm
from sm01_solarsim import load_bars_3m, _fill
from sm_bmom import rth_3m, BAND_DAYS
from smv2_common import dd_battery
import common as C1

PV_MNQ, COMM_MNQ = 2.0, 0.65
PV_NQ, COMM_NQ = 20.0, 2.18
ENTRY_LEVEL, EXIT_LEVEL = 3.0, 1.0
WSOLAR, WBMOM, TILTRESCALE, TILTMULT = 0.7086, 2.83, 0.9026, 1.25
CANONICAL_END = pd.Timestamp("2026-05-31")   # matches substrate.py exactly
HEALTH_END = pd.Timestamp("2026-07-31")      # latest already-available, not-locked-forward data


def rha(x):
    return np.sign(x) * np.floor(np.abs(x) + 0.5)


print("[health_substrate] loading bars through 2026-07-31 ...", flush=True)
bars = load_bars_3m()
sess = pd.to_datetime(bars["sess_date"])
ext = (sess <= HEALTH_END).to_numpy()
bars = bars[ext].reset_index(drop=True)
n = len(bars)
close = bars["close"].to_numpy(); open_ = bars["open"].to_numpy()
high = bars["high"].to_numpy(); low = bars["low"].to_numpy()
sig460 = sm.sigma_series(close)
PEND = C1.build_pend(bars, sig460)
T = sm.e10_target(PEND).astype(int)

sclose = bars.loc[bars["is_last_of_sess"], ["sess_date", "close"]].set_index("sess_date")["close"]
tilt_by_date = np.sign(sclose - sclose.rolling(50).mean()).shift(1).to_dict()
tilt_state = np.array([tilt_by_date.get(d, np.nan) for d in bars["sess_date"]])
tilt_state = np.where(np.isnan(tilt_state), 0.0, tilt_state)


def bmom_pos_series(bars3):
    r = rth_3m(bars3)
    pos_arr = np.zeros(len(bars3)); hist = {}; day_count = 0
    for d_, g in r.groupby("date", sort=True):
        g = g.sort_values("hm")
        if g["hm"].iloc[0] != 933:
            continue
        open0930 = g["open"].iloc[0]
        close_ = g["close"].to_numpy(); vol = g["volume"].to_numpy(); hm = g["hm"].to_numpy()
        vwap = np.cumsum(close_ * vol) / np.maximum(np.cumsum(vol), 1e-9)
        gidx = g.index.to_numpy(); pos = 0
        flat_hm = int(hm[hm <= 1557].max()) if (hm <= 1557).any() else None
        if day_count >= BAND_DAYS:
            for i in range(len(g)):
                h = int(hm[i])
                if flat_hm is not None and h == flat_hm:
                    pos = 0; pos_arr[gidx[i]] = pos; break
                if h > 1554:
                    pos_arr[gidx[i]] = pos; continue
                past = hist.get(h)
                if past is not None and len(past) >= 1:
                    m_tod = float(np.mean(past[-BAND_DAYS:]))
                    up, lo = open0930 + m_tod, open0930 - m_tod
                    if close_[i] > max(up, vwap[i]):
                        pos = 1
                    elif close_[i] < min(lo, vwap[i]):
                        pos = -1
                pos_arr[gidx[i]] = pos
        for i in range(len(g)):
            hist.setdefault(int(hm[i]), []).append(abs(close_[i] - open0930))
        day_count += 1
    return pos_arr


print("[health_substrate] building B-MOM leg ...", flush=True)
B = bmom_pos_series(bars)

sess_close_ts = bars.groupby("sess_date")["time"].transform("max")
entry_block_dl = sess_close_ts - pd.Timedelta(minutes=30)
forced_flat_dl = sess_close_ts - pd.Timedelta(minutes=21)
bar_time = bars["time"]
entry_blocked_c4 = (bar_time >= entry_block_dl).to_numpy()
forced_flat_c4 = (bar_time >= forced_flat_dl).to_numpy()
last = bars["is_last_of_sess"].to_numpy()

m_arr = np.where((T != 0) & (tilt_state != 0) & (np.sign(T) == tilt_state), TILTMULT, 1.0)
Tp = np.clip(rha(T * m_arr * TILTRESCALE), -13, 13)
M = WSOLAR * Tp + WBMOM * np.asarray(B)

hm = (pd.to_datetime(bars["time"]).dt.hour * 100 + pd.to_datetime(bars["time"]).dt.minute).to_numpy()
sess_arr = bars["sess_date"].to_numpy()
year_arr = pd.to_datetime(bars["sess_date"]).dt.year.to_numpy()


def build_pos_seq(M_arr, entry_level=ENTRY_LEVEL, exit_level=EXIT_LEVEL,
                   entry_blocked=None, forced_flat=None):
    entry_blocked = entry_blocked if entry_blocked is not None else entry_blocked_c4
    forced_flat = forced_flat if forced_flat is not None else forced_flat_c4
    p = 0; pend = 0
    pos_seq = np.zeros(n, dtype=int)
    for t in range(n):
        if pend != p:
            p = pend
        if last[t] and p != 0:
            p = 0; pend = 0
            pos_seq[t] = p
            continue
        pos_seq[t] = p
        if forced_flat[t]:
            tgt = 0
        elif p == 0:
            tgt = 0 if entry_blocked[t] else (1 if M_arr[t] >= entry_level else (-1 if M_arr[t] <= -entry_level else 0))
        elif p > 0:
            if M_arr[t] <= -entry_level and not entry_blocked[t]:
                tgt = -1
            elif M_arr[t] <= exit_level:
                tgt = 0
            else:
                tgt = p
        else:
            if M_arr[t] >= entry_level and not entry_blocked[t]:
                tgt = 1
            elif M_arr[t] >= -exit_level:
                tgt = 0
            else:
                tgt = p
        pend = tgt
    return pos_seq


def onelot_exec(pos_seq, comm, pv, o, h, l, c):
    cash = 0.0; p = 0; prev_eq = 0.0
    bar_pos = np.zeros(n, dtype=int); bar_pnl = np.zeros(n)
    for t in range(n):
        tgt = int(pos_seq[t])
        if tgt != p:
            d = tgt - p
            side = 1 if d > 0 else -1
            if last[t]:
                px = _fill(o[t], h[t], l[t], side, at_close=c[t])
            else:
                px = _fill(o[t], h[t], l[t], side)
            cash -= d * px * pv
            cash -= abs(d) * comm
            p = tgt
        eq = cash + p * c[t] * pv
        bar_pnl[t] = eq - prev_eq; prev_eq = eq
        bar_pos[t] = p
    dd = pd.DataFrame({"sess": bars["sess_date"], "pnl": bar_pnl}).groupby("sess")["pnl"].sum().reset_index()
    dd.columns = ["sess", "net"]
    return dd, bar_pos, bar_pnl


def battery_row(tag, daily):
    b = dd_battery(pd.to_datetime(daily["sess"]), daily["net"].to_numpy(), label=tag)
    return {"tag": tag, "n_days": b["n_days"], "net": b["net"], "sharpe": b["sharpe"],
            "sortino": b["sortino"], "calmar": b["calmar"], "maxDD_eod": b["maxDD_eod"],
            "CDaR95": b["CDaR5"], "worst_day": float(daily["net"].min()),
            "worst_month": b["worst_month"], "pos_day_pct": b["pos_day_pct"]}


pos_full = build_pos_seq(M)
daily_nq, barpos_nq, bpnl_nq = onelot_exec(pos_full, COMM_NQ, PV_NQ, open_, high, low, close)

# correctness gate: sliced back to the canonical window, must reproduce the certified net exactly
sess_ext = pd.to_datetime(bars["sess_date"])
canon_bar_mask = (sess_ext <= CANONICAL_END).to_numpy()
canon_net = float(bpnl_nq[canon_bar_mask].sum())
assert abs(canon_net - 301915.92) < 1.0, f"health substrate canonical-slice net mismatch: {canon_net}"
print(f"[health_substrate] verified: canonical-window slice reproduces certified net exactly "
      f"({canon_net:.2f}); extended net through 2026-07-31 = {daily_nq['net'].sum():.2f}, "
      f"n_bars={n}, n_sessions={bars['sess_date'].nunique()}", flush=True)

is_health_window = (sess_ext > CANONICAL_END).to_numpy()  # the NEW June-July 2026 observation bars
n_health_only_sessions = int(bars.loc[is_health_window, "sess_date"].nunique())

if __name__ == "__main__":
    print("health_substrate self-test OK")
