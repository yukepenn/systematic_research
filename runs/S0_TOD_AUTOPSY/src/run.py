"""S0_TOD_AUTOPSY — purely descriptive time-of-day map. Frozen spec.yaml (committed 3a21a82,
BEFORE W19R1_SELECTIVITY was executed or read). No gates, no verdict, no promotion.
"""
import os, sys, json, datetime as dt
import numpy as np, pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
sys.path.insert(0, os.path.join(ROOT, "runs", "W18R1_M1_VOLSEASON", "src"))
import sm01_solarsim as sm
from smv2_common import dd_battery
import common as C1

RUN = os.path.join(ROOT, "runs", "S0_TOD_AUTOPSY")
OUT = os.path.join(RUN, "out")
os.makedirs(OUT, exist_ok=True)
DEV_END = dt.date(2026, 5, 29)

BLOCKS = [   # (name, start_et_HHMM_inclusive, end_et_HHMM_exclusive); wraps midnight for EVENING_ASIA
    ("EVENING_ASIA",     1800, 200),
    ("EUROPE_PREUS",      200, 800),
    ("US_OPEN",           800, 1000),
    ("LATE_MORNING",     1000, 1200),
    ("LUNCH",            1200, 1330),
    ("AFTERNOON",        1330, 1545),
    ("CLOSING_APPROACH", 1545, 1700),
]


def block_of_hm(hm):
    """hm = hour*100+minute, e.g. 935 for 09:35. Vectorised block assignment.

    BUG FOUND AND FIXED during this run (self-check caught it, per S0 spec §4's mandatory
    reconciliation requirement): the naive [a,b) wraparound partition on raw hm left bars
    timestamped EXACTLY 17:00 (bar-end convention -> session-close/forced-flatten bars, ~1 per
    normal-length session, ~1,095 of the 1,139 dev sessions) UNASSIGNED to any block, because
    17:00 is simultaneously ">= EVENING_ASIA's wrap start (18:00)"=False and "< CLOSING_APPROACH's
    end (17:00)"=False. Fixed by mapping hm to minutes-elapsed-since-that-session's-own-18:00-open
    (0..1380, a genuinely non-wrapping scale) and making ONLY the final block's upper bound
    inclusive (1380 min = 17:00 = the session's last possible bar). No boundary was moved to
    change any P&L outcome -- this is a partition-coverage fix, not a re-fit.
    """
    hh = hm // 100
    mm = hm % 100
    total_min = hh * 60 + mm
    since_1800 = (total_min - 18 * 60) % (24 * 60)   # 0 = 18:00 open ... 1380 = 17:00 close (max
                                                        # value that occurs in real data; the
                                                        # session is 23h long, 1380..1439 never occur)
    out = np.full(len(hm), "UNASSIGNED", dtype=object)
    for i, (name, a, b) in enumerate(BLOCKS):
        a_m = (a // 100 * 60 + a % 100 - 18 * 60) % (24 * 60)
        b_m = (b // 100 * 60 + b % 100 - 18 * 60) % (24 * 60)
        is_last_block = (i == len(BLOCKS) - 1)
        m = (since_1800 >= a_m) & (since_1800 <= b_m if is_last_block else since_1800 < b_m)
        out[m] = name
    return out


def hm_of(ts):
    t = pd.to_datetime(ts)
    return (t.dt.hour * 100 + t.dt.minute).to_numpy()


# ============================================================== load + build SOLAR_E10 (control)
bars = C1.load_dev_bars()
n = len(bars)
sess = bars["sess_date"].to_numpy()
close = bars["close"].to_numpy()
sig460 = sm.sigma_series(close)
PEND = C1.build_pend(bars, sig460)
T = sm.e10_target(PEND)
daily, bar_pos, bar_pnl = C1.e10_exec(bars, T)

hm = hm_of(bars["time"])
block = block_of_hm(hm)
np.save(os.path.join(OUT, "block_assignment.npy"), block)

# position-blocks: maximal runs of bars with constant nonzero bar_pos (the "trade" unit for
# MAE/MFE and win-rate, since the E10 target is continuously rebalanced rather than discrete
# round-trip trades -- disclosed in spec.yaml §3 as "the available construction")
def position_blocks(pos, bar_pnl, block, sess):
    change = np.r_[True, pos[1:] != pos[:-1]]
    block_id = np.cumsum(change)
    df = pd.DataFrame({"block_id": block_id, "pos": pos, "pnl": bar_pnl, "tod_block": block, "sess": sess})
    df = df[df["pos"] != 0]
    if len(df) == 0:
        return pd.DataFrame()
    g = df.groupby("block_id")
    rows = g.agg(n_bars=("pnl", "size"), net_pnl=("pnl", "sum"),
                 tod_block_open=("tod_block", "first"), sess_open=("sess", "first"),
                 side=("pos", "first")).reset_index()
    # MAE/MFE from cumulative pnl path within each position-block
    mae, mfe = [], []
    for _, grp in g:
        cum = grp["pnl"].cumsum().to_numpy()
        mfe.append(float(cum.max()) if len(cum) else 0.0)
        mae.append(float(cum.min()) if len(cum) else 0.0)
    rows["MFE"] = mfe
    rows["MAE"] = mae
    return rows

pblocks = position_blocks(bar_pos, bar_pnl, block, sess)
pblocks.to_csv(os.path.join(OUT, "position_blocks_solar.csv"), index=False)

# path efficiency: |net displacement| / |total absolute travel| of close price, per block, per
# session, averaged -- a MARKET descriptor (close-price based), not a strategy statistic.
def path_efficiency_by_block(bars, block):
    df = pd.DataFrame({"sess": bars["sess_date"].to_numpy(), "block": block,
                        "close": bars["close"].to_numpy()})
    rows = []
    for (s, b), g in df.groupby(["sess", "block"]):
        if len(g) < 2:
            continue
        disp = abs(g["close"].iloc[-1] - g["close"].iloc[0])
        travel = g["close"].diff().abs().sum()
        if travel > 0:
            rows.append({"sess": s, "block": b, "path_eff": disp / travel})
    return pd.DataFrame(rows).groupby("block")["path_eff"].mean()

path_eff = path_efficiency_by_block(bars, block)

# member flips by block (13-member ensemble), and E10 target-change rate by block
_, FLIPS = C1.build_pend_with_flips(bars, sig460)
flip_per_bar = (FLIPS != 0).sum(axis=1)
tgt_change = np.r_[0, (np.diff(T) != 0).astype(int)]

# worst-day / worst-week attribution: which blocks contributed to the worst 1%/5% SESSION days
sess_net = daily.set_index(daily["sess"].astype(str))["net"]
n_days = len(sess_net)
k1 = max(1, int(0.01 * n_days)); k5 = max(1, int(0.05 * n_days))
worst1 = set(sess_net.sort_values().index[:k1])
worst5 = set(sess_net.sort_values().index[:k5])
sess_str = pd.Series(sess.astype(str))
is_worst1 = sess_str.isin(worst1).to_numpy()
is_worst5 = sess_str.isin(worst5).to_numpy()

# maxDD / CDaR episode attribution: bars belonging to sessions inside a drawdown episode of the
# EOD equity curve (episode = contiguous run of sessions with EOD drawdown > 0), and separately
# the CDaR_0.95 tail-episode session set (worst 5% EOD-drawdown days by the standard house metric).
eq = np.cumsum(sess_net.to_numpy())
peak = np.maximum.accumulate(eq)
dd = peak - eq
dd_days = sess_net.index[dd > 1e-9]
cdar_k = max(1, int(0.05 * n_days))
cdar_days = set(sess_net.index[np.argsort(dd)[::-1][:cdar_k]])
is_dd_episode = sess_str.isin(set(dd_days)).to_numpy()
is_cdar_episode = sess_str.isin(cdar_days).to_numpy()

# top-50 single-bar P&L moves (both directions) -- link to D-WINNER-1, descriptive only here
top50_idx = np.argsort(np.abs(bar_pnl))[-50:]
top50_block = pd.Series(block[top50_idx]).value_counts()

# ============================================================== per-block table, SOLAR_E10
rows = []
total_net = bar_pnl.sum()
total_flip = flip_per_bar.sum()
total_tgtchg = tgt_change.sum()
for name, a, b_ in BLOCKS:
    m = block == name
    n_bars = int(m.sum())
    pnl_here = bar_pnl[m]
    pb = pblocks[pblocks["tod_block_open"] == name] if len(pblocks) else pblocks
    wins = pb[pb["net_pnl"] > 0]["net_pnl"] if len(pb) else pd.Series(dtype=float)
    losses = pb[pb["net_pnl"] <= 0]["net_pnl"] if len(pb) else pd.Series(dtype=float)
    rows.append({
        "block": name, "et_window": f"{a:04d}-{b_:04d}", "n_bars": n_bars,
        "n_position_blocks_opened": int(len(pb)),
        "gross_pnl": float(pnl_here[pnl_here > 0].sum()),
        "gross_loss": float(pnl_here[pnl_here < 0].sum()),
        "net_pnl": float(pnl_here.sum()),
        "net_pnl_share_of_total": float(pnl_here.sum() / total_net) if total_net else np.nan,
        "sharpe_contribution_share": float(pnl_here.sum() / total_net) if total_net else np.nan,
        "win_rate_position_blocks": float((pb["net_pnl"] > 0).mean()) if len(pb) else np.nan,
        "avg_win": float(wins.mean()) if len(wins) else np.nan,
        "avg_loss": float(losses.mean()) if len(losses) else np.nan,
        "member_flip_count": int(flip_per_bar[m].sum()),
        "member_flip_share": float(flip_per_bar[m].sum() / total_flip) if total_flip else np.nan,
        "e10_target_change_count": int(tgt_change[m].sum()),
        "e10_target_change_share": float(tgt_change[m].sum() / total_tgtchg) if total_tgtchg else np.nan,
        "path_efficiency_close_price": float(path_eff.get(name, np.nan)),
        "MFE_mean": float(pb["MFE"].mean()) if len(pb) else np.nan,
        "MAE_mean": float(pb["MAE"].mean()) if len(pb) else np.nan,
        "long_pnl": float(bar_pnl[m & (bar_pos > 0)].sum()),
        "short_pnl": float(bar_pnl[m & (bar_pos < 0)].sum()),
        "top50_bar_participation_count": int(top50_block.get(name, 0)),
        "top50_bar_participation_share": float(top50_block.get(name, 0) / 50),
        "worst1pct_days_pnl_contribution": float(bar_pnl[m & is_worst1].sum()),
        "worst5pct_days_pnl_contribution": float(bar_pnl[m & is_worst5].sum()),
        "dd_episode_pnl_contribution": float(bar_pnl[m & is_dd_episode].sum()),
        "cdar_episode_pnl_contribution": float(bar_pnl[m & is_cdar_episode].sum()),
    })
solar_profile = pd.DataFrame(rows)
solar_profile.to_csv(os.path.join(OUT, "block_profile_solar.csv"), index=False)
print("=== SOLAR_E10 by block ===")
print(solar_profile[["block", "et_window", "n_bars", "net_pnl", "net_pnl_share_of_total",
                      "win_rate_position_blocks", "member_flip_share", "path_efficiency_close_price",
                      "worst5pct_days_pnl_contribution", "cdar_episode_pnl_contribution"]]
      .to_string(index=False), flush=True)

# reconciliation self-check (spec §4: totals must reconcile to known full-sample figures)
recon = {
    "sum_block_net_pnl": float(solar_profile["net_pnl"].sum()),
    "actual_total_net": float(total_net),
    "match": bool(abs(solar_profile["net_pnl"].sum() - total_net) < 1e-6),
    "sum_block_flips": int(solar_profile["member_flip_count"].sum()),
    "actual_total_flips": int(total_flip),
    "flips_match": bool(solar_profile["member_flip_count"].sum() == total_flip),
    "n_bars_sum": int(solar_profile["n_bars"].sum()), "n_bars_total": int(n),
    "n_bars_match": bool(solar_profile["n_bars"].sum() == n),
}
json.dump(recon, open(os.path.join(OUT, "reconciliation_selfcheck.json"), "w"), indent=2)
print("\n=== RECONCILIATION SELF-CHECK ===\n" + json.dumps(recon, indent=2), flush=True)
assert recon["match"] and recon["flips_match"] and recon["n_bars_match"], "S0 reconciliation FAILED"

# ============================================================== per-3min-slot profile (visualization only)
slot = ((pd.to_datetime(bars["time"]).dt.hour * 60 + pd.to_datetime(bars["time"]).dt.minute) // 3).astype(int)
slot_df = pd.DataFrame({"slot": slot, "pnl": bar_pnl}).groupby("slot")["pnl"].agg(["sum", "count"])
slot_df.columns = ["net_pnl", "n_bars"]
slot_df.to_csv(os.path.join(OUT, "slot_profile_3min.csv"))

# ============================================================== BMOM (trade-level, entry-time attribution)
bm = pd.read_parquet(os.path.join(ROOT, "runs", "SMV2B_BMOM_EXEC_AUDIT", "out", "ledger_E2_next_open.parquet"))
bm_hm_entry = bm["entry_hm"].to_numpy()
bm_hm_exit = bm["exit_hm"].to_numpy()
bm_block_entry = block_of_hm(bm_hm_entry)
bm_block_exit = block_of_hm(bm_hm_exit)
bm_net = bm["net_c1_ticks"].to_numpy() * 5.0   # NQ $/tick=5 at this ledger's convention (C1 friction)
bm_rows = []
for name, a, b_ in BLOCKS:
    m = bm_block_entry == name
    x = bm_net[m]
    bm_rows.append({
        "block": name, "et_window": f"{a:04d}-{b_:04d}",
        "n_entries": int(m.sum()), "n_exits": int((bm_block_exit == name).sum()),
        "gross_pnl": float(x[x > 0].sum()), "gross_loss": float(x[x < 0].sum()),
        "net_pnl": float(x.sum()),
        "net_pnl_share_of_total": float(x.sum() / bm_net.sum()) if bm_net.sum() else np.nan,
        "win_rate": float((x > 0).mean()) if len(x) else np.nan,
        "avg_win": float(x[x > 0].mean()) if (x > 0).any() else np.nan,
        "avg_loss": float(x[x < 0].mean()) if (x < 0).any() else np.nan,
        "long_pnl": float(x[bm.loc[m, "side"].to_numpy() == "L"].sum()) if m.any() else 0.0,
        "short_pnl": float(x[bm.loc[m, "side"].to_numpy() == "S"].sum()) if m.any() else 0.0,
    })
bmom_profile = pd.DataFrame(bm_rows)
bmom_profile.to_csv(os.path.join(OUT, "block_profile_bmom.csv"), index=False)
print("\n=== BMOM by block (entry-time attribution -- trade-level object, not bar-continuous) ===")
print(bmom_profile[["block", "n_entries", "net_pnl", "net_pnl_share_of_total", "win_rate"]]
      .to_string(index=False), flush=True)
bm_recon = {"sum_block_net": float(bmom_profile["net_pnl"].sum()), "actual_total": float(bm_net.sum()),
            "match": bool(abs(bmom_profile["net_pnl"].sum() - bm_net.sum()) < 1e-6)}
assert bm_recon["match"], "BMOM reconciliation FAILED"

# ============================================================== combined (Solar + BMOM), bar/trade pooled by block
combined_rows = []
for name, a, b_ in BLOCKS:
    s_net = solar_profile.set_index("block").loc[name, "net_pnl"]
    b_net = bmom_profile.set_index("block").loc[name, "net_pnl"]
    combined_rows.append({"block": name, "solar_net": s_net, "bmom_net": b_net,
                           "combined_net": s_net + b_net})
combined_profile = pd.DataFrame(combined_rows)
combined_profile.to_csv(os.path.join(OUT, "block_profile_combined.csv"), index=False)

# ============================================================== PRODUCT_A day-only secondary column
# Day-only overlay applied to the SOLAR leg only (context column; not a full Product A rebuild):
# block NEW entries in the last 30 min before close, force flat in the last 21 min before close.
# Approximated on this 3-minute NQ grid (17:00 ET normal close) as hm>=1630 blocks new entries,
# hm>=1639 forces flat -- matching SolarWaveOneContractNQ_v4.cs's EntryBlockMinutesBeforeClose=30 /
# ForcedFlatMinutesBeforeClose=21 constants exactly on a normal-length session (early closes are a
# small minority of sessions and are NOT specially handled here -- disclosed, not a Track-E parity
# claim, this is a descriptive diagnostic only).
is_last_of_sess = bars["is_last_of_sess"].to_numpy()
T_dayonly = T.copy()
# crude forced-flat/no-new-entry mask by absolute hm (does not re-derive true session end per C4's
# SessionIterator convention; sufficient for a descriptive block-level diagnostic, disclosed above)
entry_block_mask = hm >= 1630
force_flat_mask = hm >= 1639
T_dayonly = np.where(force_flat_mask, 0, T_dayonly)
# no-new-entry: within entry_block window, position may not go from 0 to nonzero, but may still exit
prev = np.r_[0, T_dayonly[:-1]]
bad_new_entry = entry_block_mask & (prev == 0) & (T_dayonly != 0)
T_dayonly = np.where(bad_new_entry, 0, T_dayonly)
daily_dayonly, barpos_dayonly, barpnl_dayonly = C1.e10_exec(bars, T_dayonly)
dayonly_rows = []
for name, a, b_ in BLOCKS:
    m = block == name
    dayonly_rows.append({"block": name, "net_pnl_dayonly": float(barpnl_dayonly[m].sum()),
                          "net_pnl_full_eth": float(bar_pnl[m].sum()),
                          "delta_from_dayonly_overlay": float(barpnl_dayonly[m].sum() - bar_pnl[m].sum())})
dayonly_profile = pd.DataFrame(dayonly_rows)
dayonly_profile.to_csv(os.path.join(OUT, "block_profile_producta_dayonly.csv"), index=False)
print("\n=== DAY-ONLY OVERLAY CONTEXT (Solar leg only, descriptive approximation) ===")
print(dayonly_profile.to_string(index=False), flush=True)

print("\n=== S0 DONE ===", flush=True)
