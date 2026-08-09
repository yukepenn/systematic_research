"""U0 -- builds the unified, bar-level, causal Product-A/Product-B state table for the whole
CONTINUOUS SYSTEM EVOLUTION phase. Reuses SA0's health-extended Product-B substrate (through
2026-07-31) BY IMPORT (health_substrate.py already carries its own correctness gate). Adds a
generalized, verbatim-formula copy of PA0's product_a_exec (pa0_substrate.py's own function is
bound to its module-level canonical-only-window arrays and cannot be reused by import here) run
on the SAME extended arrays. Adds R4/R5's feature formulas, generalized from entry-bar-only to
every bar (needed for U3/U4/U6's path-dependent science). Adds session-phase clocks and
per-bar action-state labels for both products.

DISCLOSED APPROXIMATION: genuine MNQ OHLC prices are only present in this repo through
2026-05-29 (runs/PRODUCTB_ONECONTRACT_FINAL/out/mnq_3m_raw.csv). For the health-only extension
bars (2026-06-01..2026-07-31), Product-B's MNQ leg (BEST_ONE_MNQ) uses NQ OHLC as a proxy for
MNQ OHLC -- both instruments track the identical CME Nasdaq-100 index at the same price levels
(only the point-value/tick-dollar multiplier differs), and this repo's own parity docs already
document a small, disclosed NQ/MNQ fill-convention residual as an accepted approximation class.
This proxy is used ONLY for the June-July 2026 observational extension; the canonical-window
(<=2026-05-29) correctness gate below uses genuine MNQ prices exactly as substrate.py did, so
the proxy never touches any certified or promotion-gated figure. Product A needs no such proxy:
pa0_substrate.product_a_exec prices Product A on NQ's OWN OHLC throughout (PV_MNQ dollar
multiplier applied directly to NQ price levels, no separate MNQ price series at all) -- matched
here verbatim, so Product A's leg is genuine NQ data end-to-end, canonical and extended alike."""
import os, sys, json
import numpy as np, pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
sys.path.insert(0, os.path.join(ROOT, "runs", "W18R1_M1_VOLSEASON", "src"))
sys.path.insert(0, os.path.join(ROOT, "runs", "SA0_SYSTEM_STRUCTURE", "current_health", "src"))
from sm01_solarsim import _fill
import health_substrate as HS  # extended (through 2026-07-31) Product-B substrate, self-verified on import

OUT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "out")
os.makedirs(OUT, exist_ok=True)

bars = HS.bars
n = HS.n
close, open_, high, low = HS.close, HS.open_, HS.high, HS.low
volume = bars["volume"].to_numpy().astype(float)
last = HS.last
T, Tp, tilt_state, B, M = HS.T, HS.Tp, HS.tilt_state, HS.B, HS.M
entry_blocked_c4, forced_flat_c4 = HS.entry_blocked_c4, HS.forced_flat_c4
sig460 = HS.sig460
sd = bars["sess_date"].to_numpy()
hm = HS.hm
year_arr = HS.year_arr
PEND = HS.PEND
CANONICAL_END = HS.CANONICAL_END
print(f"[U0] loaded extended Product-B substrate: n={n} bars, "
      f"{bars['time'].min()} .. {bars['time'].max()}", flush=True)

# ============================================================= Product-B position/pricing (NQ)
pos_B = HS.build_pos_seq(M)
daily_B_nq, barpos_B_nq, bpnl_B_nq = HS.onelot_exec(pos_B, HS.COMM_NQ, HS.PV_NQ, open_, high, low, close)

# ---------------------------------------------------------------- MNQ prices (genuine <=2026-05-29, NQ-proxy after)
mnq_raw = pd.read_csv(os.path.join(ROOT, "runs", "PRODUCTB_ONECONTRACT_FINAL", "out", "mnq_3m_raw.csv"), comment="#")
mnq_raw["time"] = pd.to_datetime(mnq_raw["time"])
mnq_idx = mnq_raw.set_index("time")
aligned_raw = mnq_idx.reindex(bars["time"])  # NOT ffilled -- NaN marks genuinely-missing MNQ bars
is_mnq_genuine = aligned_raw["close"].notna().to_numpy()
o_mnq = np.where(is_mnq_genuine, aligned_raw["open"].to_numpy(), open_)
h_mnq = np.where(is_mnq_genuine, aligned_raw["high"].to_numpy(), high)
l_mnq = np.where(is_mnq_genuine, aligned_raw["low"].to_numpy(), low)
c_mnq = np.where(is_mnq_genuine, aligned_raw["close"].to_numpy(), close)
print(f"[U0] MNQ genuine bars: {int(is_mnq_genuine.sum())} / {n}  "
      f"(proxy-NQ bars: {int((~is_mnq_genuine).sum())})", flush=True)

daily_B_mnq, barpos_B_mnq, bpnl_B_mnq = HS.onelot_exec(pos_B, HS.COMM_MNQ, HS.PV_MNQ, o_mnq, h_mnq, l_mnq, c_mnq)

# ============================================================= Product-A leg (generalized product_a_exec)
KSOLAR, KBMOM, TILTRESCALE, TILTMULT, SHORTHALF = 0.728654, 2.934159, 0.9026, 1.25, 0.5
PV_MNQ_A, COMM_MNQ_A = 2.0, 0.65
ENTRY_BLOCK_MIN, FORCED_FLAT_MIN = 30, 21  # same C4 windows, already baked into entry_blocked_c4/forced_flat_c4


def rha(x):
    return np.sign(x) * np.floor(np.abs(x) + 0.5)


def product_a_exec_generalized(T_leg, tilt_state_, B_, entry_blocked_, forced_flat_,
                                o, h, l, c, last_, sd_, n_):
    """Verbatim-formula copy of pa0_substrate.product_a_exec (see that file for the original,
    canonical-window-bound version) -- re-parametrized to accept the extended-window arrays
    (and MNQ price series, genuine-or-proxy) since pa0_substrate's own function is closed over
    its own module-level canonical-only arrays and cannot be reused by import for this purpose."""
    m_arr = np.where((T_leg != 0) & (tilt_state_ != 0) & (np.sign(T_leg) == tilt_state_), TILTMULT, 1.0)
    s_arr = np.where((T_leg < 0) & (tilt_state_ > 0), SHORTHALF, 1.0)
    Tpp = np.clip(rha(T_leg * m_arr * s_arr * TILTRESCALE), -13, 13)
    M_a = np.clip(rha(KSOLAR * Tpp + KBMOM * B_), -13, 13)

    cash = 0.0; p = 0; pend = 0; prev_eq = 0.0
    contracts_by_sess = {}
    bar_pos = np.zeros(n_, dtype=int)
    bar_pnl = np.zeros(n_)
    for t in range(n_):
        if pend != p:
            d = pend - p
            side = 1 if d > 0 else -1
            px = _fill(o[t], h[t], l[t], side)
            cash -= d * px * PV_MNQ_A
            cash -= abs(d) * COMM_MNQ_A
            contracts_by_sess[sd_[t]] = contracts_by_sess.get(sd_[t], 0) + abs(d)
            p = pend
        if last_[t] and p != 0:
            side = -1 if p > 0 else 1
            px = _fill(o[t], h[t], l[t], side, at_close=c[t])
            cash += p * px * PV_MNQ_A
            cash -= abs(p) * COMM_MNQ_A
            contracts_by_sess[sd_[t]] = contracts_by_sess.get(sd_[t], 0) + abs(p)
            p = 0; pend = 0
        else:
            tgt_raw = int(M_a[t])
            if forced_flat_[t]:
                tgt = 0
            elif entry_blocked_[t]:
                if tgt_raw == 0 or p == 0:
                    tgt = 0
                elif np.sign(tgt_raw) != np.sign(p):
                    tgt = 0
                else:
                    tgt = p if abs(tgt_raw) > abs(p) else tgt_raw
            else:
                tgt = tgt_raw
            pend = tgt
        eq = cash + p * c[t] * PV_MNQ_A
        bar_pnl[t] = eq - prev_eq; prev_eq = eq
        bar_pos[t] = p
        if last_[t]:
            contracts_by_sess.setdefault(sd_[t], 0)
    return bar_pos, bar_pnl, M_a


print("[U0] running Product-A leg on extended window ...", flush=True)
# NOTE: pa0_substrate.product_a_exec prices Product A on NQ's OWN OHLC (PV_MNQ dollar multiplier
# applied to NQ price levels) -- it never loads a separate MNQ price series at all. Matched here
# verbatim (using MNQ genuine/proxy prices instead was tried first and broke the canonical-net
# correctness gate by exactly the small genuine-NQ-vs-genuine-MNQ price residual).
barpos_A, bpnl_A, M_A_raw = product_a_exec_generalized(
    T, tilt_state, B, entry_blocked_c4, forced_flat_c4, open_, high, low, close, last, sd, n)

# ---------------------------------------------------------------- correctness gates
sd_dt = pd.to_datetime(pd.Series(sd))
canon_mask = (sd_dt <= CANONICAL_END).to_numpy()
ctrl_net_B_nq = float(bpnl_B_nq[canon_mask].sum())
ctrl_net_B_mnq = float(bpnl_B_mnq[canon_mask].sum())
ctrl_net_A = float(bpnl_A[canon_mask].sum())
assert abs(ctrl_net_B_nq - 301915.92) < 1.0, f"U0 Product-B NQ canonical-slice mismatch: {ctrl_net_B_nq}"
assert abs(ctrl_net_B_mnq - 28587.10) < 1.0, f"U0 Product-B MNQ canonical-slice mismatch: {ctrl_net_B_mnq}"
assert abs(ctrl_net_A - 177924.40) < 1.0, f"U0 Product-A canonical-slice mismatch: {ctrl_net_A}"
print(f"[U0] VERIFIED: canonical-slice nets == certified  "
      f"(B-NQ={ctrl_net_B_nq:.2f}, B-MNQ={ctrl_net_B_mnq:.2f}, A={ctrl_net_A:.2f})", flush=True)
print(f"[U0] extended (through 2026-07-31) nets: "
      f"B-NQ={bpnl_B_nq.sum():.2f}, B-MNQ={bpnl_B_mnq.sum():.2f}, A={bpnl_A.sum():.2f}", flush=True)

# ============================================================= R4/R5-style features, generalized to every bar
print("[U0] computing R4/R5-generalized bar-level features ...", flush=True)
LOOKBACK = 20


def causal_slope(arr, t0, lb=LOOKBACK):
    if t0 < lb - 1:
        return np.nan
    y = arr[t0 - lb + 1: t0 + 1]
    x = np.arange(lb)
    return np.polyfit(x, y, 1)[0]


close_s = pd.Series(close)
M_s = pd.Series(M)
vol_avg20 = pd.Series(volume).rolling(20, min_periods=5).mean().to_numpy()
bar_range = high - low
range20 = pd.Series(bar_range).rolling(20, min_periods=5).sum().to_numpy()
range100 = pd.Series(bar_range).rolling(100, min_periods=20).sum().to_numpy()
roll_hi20 = pd.Series(high).rolling(20, min_periods=1).max().to_numpy()
roll_lo20 = pd.Series(low).rolling(20, min_periods=1).min().to_numpy()

# session VWAP distance (causal, cumulative within session)
cum_pv = pd.Series(close * np.nan_to_num(volume)).groupby(pd.Series(sd)).cumsum().to_numpy()
cum_v = pd.Series(np.nan_to_num(volume)).groupby(pd.Series(sd)).cumsum().to_numpy()
with np.errstate(invalid="ignore", divide="ignore"):
    sess_vwap = np.where(cum_v > 0, cum_pv / np.maximum(cum_v, 1e-9), close)
vwap_dist_pts = close - sess_vwap

M_change = np.r_[np.nan, np.diff(M)]
M_slope_20 = np.array([causal_slope(M, t) for t in range(n)])
close_slope_20 = np.array([causal_slope(close, t) for t in range(n)])
close_slope_20_atr = np.where(sig460 > 0, close_slope_20 / sig460, np.nan)

clv = np.where(bar_range > 0, (close - low) / bar_range, np.nan)
clv_signed = 2 * clv - 1

vol_surprise = np.full(n, np.nan)
vol_surprise[1:] = np.where(vol_avg20[:-1] > 0, volume[1:] / vol_avg20[:-1], np.nan)

dxv_raw = np.sign(close - open_) * vol_surprise  # direction-adjusted volume, no trade-side needed

vwap_disp_atr = np.where(sig460 > 0, vwap_dist_pts / sig460, np.nan)

short_term_vol_ratio = np.full(n, np.nan)
for t in range(4, n):
    if sig460[t] > 0:
        short_term_vol_ratio[t] = (bar_range[t - 4:t + 1].sum() / 5) / sig460[t]

vol_compression_ratio = np.full(n, np.nan)
valid = np.arange(1, n)
r100_prev = range100[valid - 1]
mask_v = r100_prev > 0
vol_compression_ratio[valid[mask_v]] = (range20[valid[mask_v] - 1] / 20) / (r100_prev[mask_v] / 100)

prior_hi = np.r_[np.nan, roll_hi20[:-1]]
prior_lo = np.r_[np.nan, roll_lo20[:-1]]
broke_upper = high > prior_hi
rejected_upper = broke_upper & (close < prior_hi)
broke_lower = low < prior_lo
rejected_lower = broke_lower & (close > prior_lo)

ret_1 = np.r_[np.nan, np.diff(close)]
ret_5 = close_s.diff(5).to_numpy()
ret_20 = close_s.diff(20).to_numpy()

abs_diff = np.abs(np.diff(close, prepend=close[0]))
sum_abs_diff_20 = pd.Series(abs_diff).rolling(20, min_periods=20).sum().to_numpy()
trend_efficiency_20 = np.where(sum_abs_diff_20 > 0, np.abs(ret_20) / sum_abs_diff_20, np.nan)
sum_range_20 = pd.Series(bar_range).rolling(20, min_periods=20).sum().to_numpy()
range_efficiency_20 = np.where(sum_range_20 > 0, np.abs(ret_20) / sum_range_20, np.nan)

# ============================================================= session-phase clocks + coarse labels
print("[U0] computing session-phase clocks ...", flush=True)
bar_time = bars["time"]
sess_open_ts = bars.groupby("sess_date")["time"].transform("min") - pd.Timedelta(minutes=3)
sess_close_ts = bars.groupby("sess_date")["time"].transform("max")
minutes_since_session_open = (bar_time - sess_open_ts).dt.total_seconds().to_numpy() / 60.0
minutes_to_session_close = (sess_close_ts - bar_time).dt.total_seconds().to_numpy() / 60.0

sess_date_dt = pd.to_datetime(bars["sess_date"])
anchor_930 = sess_date_dt + pd.Timedelta(hours=9, minutes=30)
anchor_1600 = sess_date_dt + pd.Timedelta(hours=16)
minutes_since_rth_open = (bar_time - anchor_930).dt.total_seconds().to_numpy() / 60.0
minutes_to_rth_close = (anchor_1600 - bar_time).dt.total_seconds().to_numpy() / 60.0
is_rth = (hm >= 933) & (hm <= 1600)


def phase_label(h):
    if 1900 <= h <= 2359 or 0 <= h < 300:
        return "ETH_ASIA"
    if 300 <= h < 800:
        return "ETH_EUROPE"
    if 800 <= h < 930:
        return "US_PREMARKET"
    if 930 <= h < 1000:
        return "RTH_OPEN"
    if 1000 <= h < 1530:
        return "RTH_MID"
    if 1530 <= h < 1600:
        return "RTH_CLOSE"
    return "POST_RTH"


session_phase = np.array([phase_label(int(h)) for h in hm])

# ============================================================= action-state labels
print("[U0] computing action-state labels ...", flush=True)
sign_B = np.sign(pos_B)
prev_sign_B = np.r_[0, sign_B[:-1]]
action_B = np.full(n, "FLAT", dtype=object)
action_B[(prev_sign_B == 0) & (sign_B != 0)] = "ENTRY"
action_B[(prev_sign_B != 0) & (sign_B == 0)] = "EXIT"
action_B[(prev_sign_B != 0) & (sign_B != 0) & (prev_sign_B != sign_B)] = "REVERSAL"
action_B[(prev_sign_B != 0) & (sign_B != 0) & (prev_sign_B == sign_B)] = "HOLD"

sign_A = np.sign(barpos_A)
prev_sign_A = np.r_[0, sign_A[:-1]]
prev_pos_A = np.r_[0, barpos_A[:-1]]
action_A = np.full(n, "FLAT", dtype=object)
action_A[(prev_sign_A == 0) & (sign_A != 0)] = "ENTRY"
action_A[(prev_sign_A != 0) & (sign_A == 0)] = "EXIT"
action_A[(prev_sign_A != 0) & (sign_A != 0) & (prev_sign_A != sign_A)] = "FLIP"
same_sign_A = (prev_sign_A != 0) & (sign_A != 0) & (prev_sign_A == sign_A)
action_A[same_sign_A & (np.abs(barpos_A) > np.abs(prev_pos_A))] = "SCALE_IN"
action_A[same_sign_A & (np.abs(barpos_A) < np.abs(prev_pos_A))] = "SCALE_DOWN"
action_A[same_sign_A & (np.abs(barpos_A) == np.abs(prev_pos_A))] = "HOLD"

# ============================================================= MFE/MAE/giveback ("trip" = contiguous same-sign run)
print("[U0] segmenting sign-blocks and computing MFE/MAE/giveback for both legs ...", flush=True)


def segment_and_mfe_mae(pos_arr, bar_pnl_arr):
    sgn = np.sign(pos_arr)
    change = np.r_[True, sgn[1:] != sgn[:-1]]
    block_id = np.cumsum(change)
    age = np.zeros(n, dtype=int)
    run_pnl = np.zeros(n); mfe = np.zeros(n); mae = np.zeros(n)
    df = pd.DataFrame({"block_id": block_id, "sgn": sgn, "pnl": bar_pnl_arr})
    for bid, g in df.groupby("block_id", sort=False):
        idx = g.index.to_numpy()
        if g["sgn"].iloc[0] == 0:
            continue
        cum = g["pnl"].cumsum().to_numpy()
        run_pnl[idx] = cum
        mfe[idx] = np.maximum.accumulate(np.maximum(cum, 0.0))
        mae[idx] = np.minimum.accumulate(np.minimum(cum, 0.0))
        age[idx] = np.arange(1, len(idx) + 1)
    giveback = np.where(mfe > 0, mfe - run_pnl, 0.0)
    giveback_ratio = np.where(mfe > 0, giveback / mfe, np.nan)
    return block_id, age, run_pnl, mfe, mae, giveback, giveback_ratio


block_id_B, age_B, run_pnl_B, mfe_B, mae_B, giveback_B, giveback_ratio_B = segment_and_mfe_mae(pos_B, bpnl_B_nq)
block_id_A, age_A, run_pnl_A, mfe_A, mae_A, giveback_A, giveback_ratio_A = segment_and_mfe_mae(barpos_A, bpnl_A)

# ============================================================= assemble table
print("[U0] assembling unified state table ...", flush=True)
tbl = pd.DataFrame({
    "t_idx": np.arange(n), "time": bars["time"].to_numpy(), "sess_date": sd, "hm": hm, "year": year_arr,
    "is_health_only_bar": (sd_dt > CANONICAL_END).to_numpy(),
    "is_mnq_genuine_price": is_mnq_genuine,
    "open": open_, "high": high, "low": low, "close": close, "volume": volume,
    # ---- shared causal drivers
    "T": T, "Tp": Tp, "HTF_tilt_state": tilt_state, "B": B, "M": M,
    "M_change": M_change, "M_slope_20": M_slope_20,
    "n_bullish": (PEND > 0).sum(axis=1), "n_bearish": (PEND < 0).sum(axis=1),
    "n_flat_members": (PEND == 0).sum(axis=1), "vote_dispersion": (PEND > 0).sum(axis=1) - (PEND < 0).sum(axis=1),
    "fast_member": PEND[:, 0], "slow_member": PEND[:, -1],
    "entry_blocked_c4": entry_blocked_c4, "forced_flat_c4": forced_flat_c4,
    # ---- volatility / range
    "sigma460_atr_proxy_pts": sig460, "bar_range_pts": bar_range,
    "range_over_atr": np.where(sig460 > 0, bar_range / sig460, np.nan),
    "short_term_vol_ratio": short_term_vol_ratio, "vol_compression_ratio": vol_compression_ratio,
    # ---- price-location / rejection
    "clv": clv, "clv_signed": clv_signed,
    "sess_vwap": sess_vwap, "vwap_dist_pts": vwap_dist_pts, "vwap_disp_atr": vwap_disp_atr,
    "roll_hi20": roll_hi20, "roll_lo20": roll_lo20,
    "rejected_upper_break": rejected_upper, "rejected_lower_break": rejected_lower,
    "close_slope_20": close_slope_20, "close_slope_20_atr": close_slope_20_atr,
    "trend_efficiency_20": trend_efficiency_20, "range_efficiency_20": range_efficiency_20,
    "ret_1": ret_1, "ret_5": ret_5, "ret_20": ret_20,
    # ---- volume
    "vol_avg20": vol_avg20, "vol_surprise": vol_surprise, "direction_x_volume": dxv_raw,
    # ---- session phase
    "session_phase": session_phase, "is_rth": is_rth,
    "minutes_since_session_open": minutes_since_session_open,
    "minutes_to_session_close": minutes_to_session_close,
    "minutes_since_rth_open": minutes_since_rth_open, "minutes_to_rth_close": minutes_to_rth_close,
    # ---- Product B (discrete {-1,0,1})
    "position_B": pos_B, "action_B": action_B, "block_id_B": block_id_B, "age_bars_B": age_B,
    "run_pnl_B_dollars": run_pnl_B, "MFE_B_dollars": mfe_B, "MAE_B_dollars": mae_B,
    "giveback_B_dollars": giveback_B, "giveback_ratio_B": giveback_ratio_B,
    "bar_pnl_B_nq_dollars": bpnl_B_nq, "bar_pnl_B_mnq_dollars": bpnl_B_mnq,
    # ---- Product A (continuous -13..13)
    "M_A_raw": M_A_raw, "target_exposure_A": barpos_A, "action_A": action_A,
    "block_id_A": block_id_A, "age_bars_A": age_A,
    "run_pnl_A_dollars": run_pnl_A, "MFE_A_dollars": mfe_A, "MAE_A_dollars": mae_A,
    "giveback_A_dollars": giveback_A, "giveback_ratio_A": giveback_ratio_A,
    "bar_pnl_A_dollars": bpnl_A,
})

out_path = os.path.join(OUT, "u0_state_table.parquet")
tbl.to_parquet(out_path, index=False)
print(f"[U0] saved: {out_path}  rows={len(tbl)}  cols={len(tbl.columns)}", flush=True)

recon = {
    "n_bars": int(n),
    "canonical_end": str(CANONICAL_END.date()),
    "health_end": str(HS.HEALTH_END.date()),
    "certified_gate": {
        "B_NQ_canonical_net": ctrl_net_B_nq, "B_MNQ_canonical_net": ctrl_net_B_mnq,
        "A_canonical_net": ctrl_net_A,
    },
    "extended_full_window_net": {
        "B_NQ": float(bpnl_B_nq.sum()), "B_MNQ": float(bpnl_B_mnq.sum()), "A": float(bpnl_A.sum()),
    },
    "n_mnq_proxy_bars": int((~is_mnq_genuine).sum()),
    "n_health_only_sessions": int(HS.n_health_only_sessions),
    "action_B_counts": {k: int(v) for k, v in pd.Series(action_B).value_counts().items()},
    "action_A_counts": {k: int(v) for k, v in pd.Series(action_A).value_counts().items()},
    "session_phase_counts": {k: int(v) for k, v in pd.Series(session_phase).value_counts().items()},
}
json.dump(recon, open(os.path.join(OUT, "u0_recon.json"), "w"), indent=2)
print("\nRECON:", json.dumps(recon, indent=2))
print("\nU0 state table build complete.")
