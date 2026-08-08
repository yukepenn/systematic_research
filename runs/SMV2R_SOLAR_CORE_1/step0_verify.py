"""SMV2R_SOLAR_CORE_1 STEP ZERO — verify the committed Python V3 member simulator
(src/analytics/sm01_solarsim.py, the SM06 build engine) reproduces vote_pend on the
SM01 dev substrate (sessions <= 2026-05-31) on >= 99.99% of bars.

Also caches member pend/pos matrices + sigma460 + E10 target + instrumented E10
execution (daily net, daily contracts, bar-level position/pnl) for subtracks 382-385,
and cross-checks daily E10 net against runs/SM01_SUBSTRATE/out/e10_daily_py.csv.

NO data >= 2026-08-01 is read as market input; bars are truncated to sess_date <= 2026-05-31.
"""
import sys, os, json, time
import datetime as dt
import numpy as np
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
import sm01_solarsim as sm

RUN = os.path.join(ROOT, "runs", "SMV2R_SOLAR_CORE_1")
OUT = os.path.join(RUN, "out")
os.makedirs(OUT, exist_ok=True)
DEV_END = dt.date(2026, 5, 31)

t0 = time.time()

# ---- load dev bars (committed 3m substrate CSV), truncate to dev window ----
bars = sm.load_bars_3m(os.path.join(ROOT, "runs", "AUDIT03_BARS", "nq_3m_2022_2026.csv"))
bars = bars[bars["sess_date"] <= DEV_END].reset_index(drop=True)
print("dev bars:", len(bars), bars.time.min(), "->", bars.time.max(), flush=True)

close = bars.close.to_numpy()
sig = sm.sigma_series(close)  # incumbent N=460

POS, PEND = [], []
for vm in sm.VMS:
    is_up, flip, s_eff, anchor = sm.member_states(close, sig, float(vm))
    fills, pos, pend = sm.member_trades(bars, is_up, flip, s_eff, anchor)
    POS.append(pos); PEND.append(pend)
    print(f"vm{vm}: {len(fills)} fills", flush=True)
pos = np.column_stack(POS); pend = np.column_stack(PEND)

# ---- compare vs committed SM01 substrate on dev bars ----
v = pd.read_parquet(os.path.join(ROOT, "runs", "SM01_SUBSTRATE", "out", "vote_state_3m.parquet"))
v["sess_date"] = pd.to_datetime(v["sess_date"]).dt.date
v = v[v["sess_date"] <= DEV_END].reset_index(drop=True)
assert len(v) == len(bars), f"bar count mismatch {len(v)} vs {len(bars)}"
assert (pd.to_datetime(v["time"]).to_numpy() == bars["time"].to_numpy()).all(), "time axis mismatch"

my_vote_pend = pend.sum(axis=1)
my_vote_pos = pos.sum(axis=1)
n = len(bars)
match_pend = float((my_vote_pend == v["vote_pend"].to_numpy()).mean())
match_pos = float((my_vote_pos == v["vote_pos"].to_numpy()).mean())
sig_dev = float(np.nanmax(np.abs(sig - v["sigma460"].to_numpy())))
# per-member columns p6..p30: determine whether they are pos or pend
pm_pos = float(np.mean([ (pos[:, i] == v[f"p{vm}"].to_numpy()).mean() for i, vm in enumerate(sm.VMS) ]))
pm_pend = float(np.mean([ (pend[:, i] == v[f"p{vm}"].to_numpy()).mean() for i, vm in enumerate(sm.VMS) ]))

# ---- E10 target + instrumented execution (verbatim e10_sim semantics + telemetry) ----
tgt = sm.e10_target(pend)

def e10_exec(bars, tgt, comm_side=sm.MNQ_COMM_SIDE, point_value=sm.MNQ_POINT_VALUE):
    """Verbatim sm01_solarsim.e10_sim, instrumented: returns (daily_df, bar_pos,
    bar_pnl, daily_contracts). No semantic change."""
    n = len(bars)
    open_ = bars["open"].to_numpy(); high = bars["high"].to_numpy()
    low = bars["low"].to_numpy(); close = bars["close"].to_numpy()
    last_of_sess = bars["is_last_of_sess"].to_numpy()
    sess_date = bars["sess_date"].to_numpy()
    cash = 0.0; p = 0; pend_ = 0
    daily = {}; contracts = {}
    prev_equity = 0.0
    bar_pos = np.zeros(n, dtype=int)
    bar_pnl = np.zeros(n)
    prev_eq_bar = 0.0
    for t in range(n):
        if pend_ != p:
            d = pend_ - p
            side = 1 if d > 0 else -1
            px = sm._fill(open_[t], high[t], low[t], side)
            cash -= d * px * point_value
            cash -= abs(d) * comm_side
            contracts[sess_date[t]] = contracts.get(sess_date[t], 0) + abs(d)
            p = pend_
        if last_of_sess[t] and p != 0:
            side = -1 if p > 0 else 1
            px = sm._fill(open_[t], high[t], low[t], side, at_close=close[t])
            cash += p * px * point_value
            cash -= abs(p) * comm_side
            contracts[sess_date[t]] = contracts.get(sess_date[t], 0) + abs(p)
            p = 0; pend_ = 0
        else:
            pend_ = tgt[t]
        eq_bar = cash + p * close[t] * point_value
        bar_pnl[t] = eq_bar - prev_eq_bar
        prev_eq_bar = eq_bar
        bar_pos[t] = p
        if last_of_sess[t]:
            eq = cash + p * close[t] * point_value
            daily[sess_date[t]] = eq - prev_equity
            prev_equity = eq
            contracts.setdefault(sess_date[t], 0)
    dd = pd.DataFrame({"sess": list(daily.keys()), "net": list(daily.values())})
    dd["contracts"] = [contracts[s] for s in daily.keys()]
    return dd, bar_pos, bar_pnl

daily, bar_pos, bar_pnl = e10_exec(bars, tgt)

# cross-check vs committed SM01 daily
ref = pd.read_csv(os.path.join(ROOT, "runs", "SM01_SUBSTRATE", "out", "e10_daily_py.csv"))
ref["sess"] = pd.to_datetime(ref["sess"]).dt.date
ref = ref[ref["sess"] <= DEV_END]
mm = daily.copy(); mm["sess"] = pd.to_datetime(mm["sess"]).dt.date if not isinstance(daily["sess"].iloc[0], dt.date) else mm["sess"]
j = ref.merge(mm, on="sess", suffixes=("_ref", "_my"))
daily_max_dev = float(np.abs(j["net_ref"] - j["net_my"]).max()) if len(j) == len(ref) else np.nan

res = {
    "n_dev_bars": int(n),
    "dev_last_session": str(bars.sess_date.max()),
    "match_vote_pend": match_pend,
    "match_vote_pos": match_pos,
    "n_mismatch_pend": int((my_vote_pend != v["vote_pend"].to_numpy()).sum()),
    "sigma460_max_abs_dev": sig_dev,
    "per_member_col_match_as_pos": pm_pos,
    "per_member_col_match_as_pend": pm_pend,
    "e10_daily_sessions_matched": int(len(j)),
    "e10_daily_ref_sessions": int(len(ref)),
    "e10_daily_max_abs_dev_$": daily_max_dev,
    "verified": bool(match_pend >= 0.9999),
    "runtime_s": round(time.time() - t0, 1),
}
with open(os.path.join(OUT, "step0_verify.json"), "w") as f:
    json.dump(res, f, indent=2)
print(json.dumps(res, indent=2))

# ---- cache for subtracks ----
np.savez_compressed(
    os.path.join(OUT, "cache_incumbent.npz"),
    pos=pos, pend=pend, sigma460=sig, tgt=tgt, bar_pos=bar_pos, bar_pnl=bar_pnl,
)
daily.to_csv(os.path.join(OUT, "e10_daily_dev_incumbent.csv"), index=False)
print("cached.", flush=True)
