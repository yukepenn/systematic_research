"""Rebuilds the shared Product-B decision-layer signal trace (T, B, tilt_state, M, entry-blocked
C4 mask) exactly as runs/S2_SELTIME/src/r2_battery.py's one_contract_decisions() does (verbatim
formula reuse -- already independently adversarially verified this campaign), WITHOUT re-running
S2's whole R2 battery. Saves per-bar arrays for reuse by V1R4 event-forensics scripts."""
import os, sys
import numpy as np, pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
sys.path.insert(0, os.path.join(ROOT, "runs", "W18R1_M1_VOLSEASON", "src"))
import sm01_solarsim as sm
from sm01_solarsim import load_bars_3m
from sm_bmom import rth_3m, BAND_DAYS
import common as C1

OUT = os.path.join(ROOT, "runs", "V1R4_NT8_PARITY", "out", "one_nq_events")
os.makedirs(OUT, exist_ok=True)

bars = load_bars_3m()
sess = pd.to_datetime(bars["sess_date"])
dev = (sess <= pd.Timestamp("2026-05-31")).to_numpy()
bars = bars[dev].reset_index(drop=True)
n = len(bars)
close = bars["close"].to_numpy()
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


B = bmom_pos_series(bars)


def rha(x):
    return np.sign(x) * np.floor(np.abs(x) + 0.5)


WSOLAR, WBMOM, TILTRESCALE, TILTMULT = 0.7086, 2.83, 0.9026, 1.25
m_arr = np.where((T != 0) & (tilt_state != 0) & (np.sign(T) == tilt_state), TILTMULT, 1.0)
Tp = np.clip(rha(T * m_arr * TILTRESCALE), -13, 13)
M = WSOLAR * Tp + WBMOM * np.asarray(B)

sess_close_ts = bars.groupby("sess_date")["time"].transform("max")
entry_block_dl = sess_close_ts - pd.Timedelta(minutes=30)
entry_blocked_c4 = (bars["time"] >= entry_block_dl).to_numpy()

np.save(os.path.join(OUT, "sig_T.npy"), T)
np.save(os.path.join(OUT, "sig_B.npy"), B)
np.save(os.path.join(OUT, "sig_tilt_state.npy"), tilt_state)
np.save(os.path.join(OUT, "sig_M.npy"), M)
np.save(os.path.join(OUT, "sig_entry_blocked_c4.npy"), entry_blocked_c4)
bars[["time", "sess_date", "open", "high", "low", "close", "is_last_of_sess"]].to_csv(
    os.path.join(OUT, "sig_bars.csv"), index=False)
print("saved signal trace,", n, "bars")
