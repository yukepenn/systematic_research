"""PA0 substrate -- verbatim reuse of runs/S2_SELTIME/src/r2_battery.py's product_a_exec() and
its shared substrate (T/B/tilt_state), extracted (not imported top-level) to avoid re-running
that script's own S2/BEST_ONE_NQ side effects. Every formula checked byte-for-byte against the
source at construction time; the correctness gate at the bottom is the proof."""
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
ENTRY_BLOCK_MIN, FORCED_FLAT_MIN = 30, 21
KSOLAR, KBMOM, TILTRESCALE, TILTMULT, SHORTHALF = 0.728654, 2.934159, 0.9026, 1.25, 0.5


def rha(x):
    return np.sign(x) * np.floor(np.abs(x) + 0.5)


print("[pa0_substrate] loading bars + building signal layer ...", flush=True)
bars = load_bars_3m()
sess = pd.to_datetime(bars["sess_date"])
dev = (sess <= pd.Timestamp("2026-05-31")).to_numpy()
bars = bars[dev].reset_index(drop=True)
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


print("[pa0_substrate] building B-MOM leg ...", flush=True)
B = np.asarray(bmom_pos_series(bars))

sess_close_ts = bars.groupby("sess_date")["time"].transform("max")
entry_block_dl = sess_close_ts - pd.Timedelta(minutes=ENTRY_BLOCK_MIN)
forced_flat_dl = sess_close_ts - pd.Timedelta(minutes=FORCED_FLAT_MIN)
bar_time = bars["time"]
entry_blocked_c4 = (bar_time >= entry_block_dl).to_numpy()
forced_flat_c4 = (bar_time >= forced_flat_dl).to_numpy()
last = bars["is_last_of_sess"].to_numpy()
sd = bars["sess_date"].to_numpy()
hm = (pd.to_datetime(bars["time"]).dt.hour * 100 + pd.to_datetime(bars["time"]).dt.minute).to_numpy()
year_arr = pd.to_datetime(bars["sess_date"]).dt.year.to_numpy()


def product_a_exec(T_leg, tag, ksolar=KSOLAR, kbmom=KBMOM, apply_round_clamp=True):
    """Verbatim r2_battery.py product_a_exec, generalized with ksolar/kbmom/apply_round_clamp
    knobs for PA0's own decomposition (sec30) -- the DEFAULT call (ksolar=KSOLAR, kbmom=KBMOM,
    apply_round_clamp=True) is byte-identical to the original and is the correctness-gate call."""
    m_arr = np.where((T_leg != 0) & (tilt_state != 0) & (np.sign(T_leg) == tilt_state), TILTMULT, 1.0)
    s_arr = np.where((T_leg < 0) & (tilt_state > 0), SHORTHALF, 1.0)
    if apply_round_clamp:
        Tpp = np.clip(rha(T_leg * m_arr * s_arr * TILTRESCALE), -13, 13)
        M = np.clip(rha(ksolar * Tpp + kbmom * B), -13, 13)
    else:
        Tpp = T_leg * m_arr * s_arr * TILTRESCALE  # no round, no clamp -- continuous proxy
        M = ksolar * Tpp + kbmom * B               # no round, no clamp

    cash = 0.0; p = 0; pend = 0; prev_eq = 0.0
    contracts_by_sess = {}
    bar_pos = np.zeros(n, dtype=int if apply_round_clamp else float)
    bar_pnl = np.zeros(n)
    for t in range(n):
        if pend != p:
            d = pend - p
            side = 1 if d > 0 else -1
            px = _fill(open_[t], high[t], low[t], side)
            cash -= d * px * PV_MNQ
            cash -= abs(d) * COMM_MNQ
            contracts_by_sess[sd[t]] = contracts_by_sess.get(sd[t], 0) + abs(d)
            p = pend
        if last[t] and p != 0:
            side = -1 if p > 0 else 1
            px = _fill(open_[t], high[t], low[t], side, at_close=close[t])
            cash += p * px * PV_MNQ
            cash -= abs(p) * COMM_MNQ
            contracts_by_sess[sd[t]] = contracts_by_sess.get(sd[t], 0) + abs(p)
            p = 0; pend = 0
        else:
            tgt_raw = M[t] if apply_round_clamp else float(M[t])
            if apply_round_clamp:
                tgt_raw = int(tgt_raw)
            if forced_flat_c4[t]:
                tgt = 0
            elif entry_blocked_c4[t]:
                if tgt_raw == 0 or p == 0:
                    tgt = 0
                elif np.sign(tgt_raw) != np.sign(p):
                    tgt = 0
                else:
                    tgt = p if abs(tgt_raw) > abs(p) else tgt_raw
            else:
                tgt = tgt_raw
            pend = tgt
        eq = cash + p * close[t] * PV_MNQ
        bar_pnl[t] = eq - prev_eq; prev_eq = eq
        bar_pos[t] = p
        if last[t]:
            contracts_by_sess.setdefault(sd[t], 0)
    dd = pd.DataFrame({"sess": bars["sess_date"], "pnl": bar_pnl}).groupby("sess")["pnl"].sum().reset_index()
    dd.columns = ["sess", "net"]
    dd["contracts"] = dd["sess"].map(contracts_by_sess)
    return dd, bar_pos, bar_pnl, M


def battery_row(tag, daily):
    b = dd_battery(pd.to_datetime(daily["sess"]), daily["net"].to_numpy(), label=tag)
    return {"tag": tag, "n_days": b["n_days"], "net": b["net"], "sharpe": b["sharpe"],
            "sortino": b["sortino"], "calmar": b["calmar"], "maxDD_eod": b["maxDD_eod"],
            "CDaR95": b["CDaR5"], "worst_day": float(daily["net"].min()),
            "worst_month": b["worst_month"], "pos_day_pct": b["pos_day_pct"]}


print("[pa0_substrate] running correctness-gate call (byte-identical to r2_battery.py) ...", flush=True)
daily_ctrl, barpos_ctrl, bpnl_ctrl, M_ctrl = product_a_exec(T, "A incumbent")
ctrl_net = float(daily_ctrl["net"].sum())
assert abs(ctrl_net - 177924.40) < 1.0, f"PA0 substrate CONTROL does not reproduce certified Product A net: {ctrl_net}"
print(f"[pa0_substrate] verified: CONTROL net={ctrl_net:.2f}  n_bars={n}  "
      f"max|pos|={np.abs(barpos_ctrl).max()}", flush=True)

if __name__ == "__main__":
    print("pa0_substrate self-test OK")
