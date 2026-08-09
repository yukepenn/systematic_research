"""P0 -- builds the full-dev-window, bar-level, causal trade-state ledger for the Product-B
shared decision core (BEST_ONE_NQ / pos_incumbent). Reuses already-certified arrays verbatim
(see spec.yaml); does not re-derive the decision layer or re-run any backtest engine."""
import os, sys
import numpy as np, pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
sys.path.insert(0, os.path.join(ROOT, "runs", "W18R1_M1_VOLSEASON", "src"))
import sm01_solarsim as sm
import common as C1

RUN = os.path.join(ROOT, "runs", "P0_TRADESTATE_AUTOPSY")
OUT = os.path.join(RUN, "out")
os.makedirs(OUT, exist_ok=True)
SIGDIR = os.path.join(ROOT, "runs", "V1R4_NT8_PARITY", "out", "one_nq_events")
R2DIR = os.path.join(ROOT, "runs", "S2_SELTIME", "out", "r2")

ENTRY_LEVEL, EXIT_LEVEL = 3.0, 1.0
POINT_VALUE_NQ = 20.0

print("loading bars (full dev window) ...", flush=True)
bars = sm.load_bars_3m()
sess = pd.to_datetime(bars["sess_date"])
dev = (sess <= pd.Timestamp("2026-05-31")).to_numpy()
bars = bars[dev].reset_index(drop=True)
n = len(bars)
print(f"  {n} bars, {bars['time'].min()} .. {bars['time'].max()}", flush=True)

pos = np.load(os.path.join(R2DIR, "barpos_NQ_incumbent.npy"))
barpnl = np.load(os.path.join(R2DIR, "barpnl_NQ_incumbent.npy"))
assert len(pos) == n and len(barpnl) == n, "length mismatch vs certified arrays"

T = np.load(os.path.join(SIGDIR, "sig_T.npy"))
B = np.load(os.path.join(SIGDIR, "sig_B.npy"))
tilt_state = np.load(os.path.join(SIGDIR, "sig_tilt_state.npy"))
M = np.load(os.path.join(SIGDIR, "sig_M.npy"))
entry_blocked_c4 = np.load(os.path.join(SIGDIR, "sig_entry_blocked_c4.npy"))
assert len(T) == n and len(M) == n, "signal-layer length mismatch"

# T' (post-tilt Solar leg feeding M) -- same formula as one_contract_decisions()
def rha(x):
    return np.sign(x) * np.floor(np.abs(x) + 0.5)
TILTRESCALE, TILTMULT = 0.9026, 1.25
m_arr = np.where((T != 0) & (tilt_state != 0) & (np.sign(T) == tilt_state), TILTMULT, 1.0)
Tp = np.clip(rha(T * m_arr * TILTRESCALE), -13, 13)

# ---------------------------------------------------------------- 13-member ensemble
print("building 13-member ensemble states ...", flush=True)
close = bars["close"].to_numpy()
open_ = bars["open"].to_numpy()
high = bars["high"].to_numpy()
low = bars["low"].to_numpy()
volume = bars["volume"].to_numpy() if "volume" in bars.columns else np.full(n, np.nan)
sig460 = sm.sigma_series(close)
PEND = C1.build_pend(bars, sig460)  # (n, 13) signed member state feeding T
n_bull = (PEND > 0).sum(axis=1)
n_bear = (PEND < 0).sum(axis=1)
n_flat = 13 - n_bull - n_bear
vote_dispersion = n_bull - n_bear  # +13 unanimous bull .. -13 unanimous bear
fast_member = PEND[:, 0]    # VM=6, most reactive
slow_member = PEND[:, -1]   # VM=30, least reactive

# ---------------------------------------------------------------- session VWAP distance
sess_arr = bars["sess_date"].to_numpy()
cum_pv = pd.Series(close * np.nan_to_num(volume)).groupby(pd.Series(sess_arr)).cumsum().to_numpy()
cum_v = pd.Series(np.nan_to_num(volume)).groupby(pd.Series(sess_arr)).cumsum().to_numpy()
with np.errstate(invalid="ignore", divide="ignore"):
    sess_vwap = np.where(cum_v > 0, cum_pv / np.maximum(cum_v, 1e-9), close)
vwap_dist = close - sess_vwap

bar_range = high - low
range_over_atr = np.where(sig460 > 0, bar_range / sig460, np.nan)

# recent 20-bar high/low (inclusive of current bar; causal)
roll_hi20 = pd.Series(high).rolling(20, min_periods=1).max().to_numpy()
roll_lo20 = pd.Series(low).rolling(20, min_periods=1).min().to_numpy()
dist_from_hi20 = close - roll_hi20
dist_from_lo20 = close - roll_lo20

hm = (pd.to_datetime(bars["time"]).dt.hour * 100 + pd.to_datetime(bars["time"]).dt.minute).to_numpy()

# ---------------------------------------------------------------- position-block segmentation
print("segmenting position-blocks and computing causal MFE/MAE/giveback ...", flush=True)
change = np.r_[True, pos[1:] != pos[:-1]]
block_id_all = np.cumsum(change)  # every bar gets a block id, including flat (pos==0) runs
entry_time = np.empty(n, dtype=object)
entry_price = np.full(n, np.nan)
age_bars = np.zeros(n, dtype=int)
run_pnl = np.zeros(n)
mfe = np.zeros(n)
mae = np.zeros(n)

df = pd.DataFrame({"block_id": block_id_all, "pos": pos, "pnl": barpnl,
                    "open": open_, "time": bars["time"].to_numpy()})
for bid, g in df.groupby("block_id", sort=False):
    idx = g.index.to_numpy()
    p0 = g["pos"].iloc[0]
    if p0 == 0:
        continue  # flat run, not a position-block; leave defaults
    cum = g["pnl"].cumsum().to_numpy()
    run_pnl[idx] = cum
    mfe[idx] = np.maximum.accumulate(np.maximum(cum, 0.0))
    mae[idx] = np.minimum.accumulate(np.minimum(cum, 0.0))
    entry_time[idx] = g["time"].iloc[0]
    entry_price[idx] = g["open"].iloc[0]
    age_bars[idx] = np.arange(1, len(idx) + 1)

giveback = np.where(mfe > 0, mfe - run_pnl, 0.0)
giveback_ratio = np.where(mfe > 0, giveback / mfe, np.nan)

ledger = pd.DataFrame({
    "t_idx": np.arange(n),
    "time": bars["time"].to_numpy(),
    "sess_date": sess_arr,
    "hm": hm,
    "open": open_, "high": high, "low": low, "close": close, "volume": volume,
    "position": pos,
    "entry_time": entry_time, "entry_price": entry_price,
    "age_bars": age_bars, "age_minutes": age_bars * 3,
    "T": T, "Tp": Tp, "HTF_tilt_state": tilt_state, "B": B, "M": M,
    "EntryLevel": ENTRY_LEVEL, "ExitLevel": EXIT_LEVEL,
    "entry_blocked_c4": entry_blocked_c4,
    "n_bullish": n_bull, "n_bearish": n_bear, "n_flat_members": n_flat,
    "vote_dispersion": vote_dispersion,
    "fast_member": fast_member, "slow_member": slow_member,
    "run_pnl_dollars": run_pnl, "run_pnl_points": run_pnl / POINT_VALUE_NQ,
    "MFE_dollars": mfe, "MAE_dollars": mae,
    "MFE_points": mfe / POINT_VALUE_NQ, "MAE_points": mae / POINT_VALUE_NQ,
    "giveback_dollars": giveback, "giveback_ratio": giveback_ratio,
    "sigma460_atr_proxy_pts": sig460,
    "bar_range_pts": bar_range, "range_over_atr": range_over_atr,
    "sess_vwap": sess_vwap, "vwap_dist_pts": vwap_dist,
    "roll_hi20": roll_hi20, "roll_lo20": roll_lo20,
    "dist_from_hi20_pts": dist_from_hi20, "dist_from_lo20_pts": dist_from_lo20,
    "bar_pnl_dollars": barpnl,
})
ledger["block_id"] = block_id_all

out_path = os.path.join(OUT, "ledger_full.parquet")
ledger.to_parquet(out_path, index=False)
print(f"saved ledger: {out_path}  rows={len(ledger)}  cols={len(ledger.columns)}", flush=True)

# reconciliation self-check: sum of bar_pnl must equal the certified net
recon = {
    "sum_bar_pnl": float(barpnl.sum()),
    "n_position_blocks": int(df.loc[df["pos"] != 0, "block_id"].nunique()),
    "n_bars_in_position": int((pos != 0).sum()),
    "n_bars_flat": int((pos == 0).sum()),
}
print("RECONCILIATION:", recon, flush=True)
import json
json.dump(recon, open(os.path.join(OUT, "ledger_recon.json"), "w"), indent=2)
