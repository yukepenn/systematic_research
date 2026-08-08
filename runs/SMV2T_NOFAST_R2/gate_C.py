"""SMV2T_NOFAST_R2 — Gate C (old-regime, 2006-2021): rebuild both RAW CORES (no DUAL/HTF
overlay -- the spec text says "cores", distinct from the "decision object" tested in gates
A/D/E) on the SM06 hist substrate, per-member votes obtained by RE-RUNNING the verified
simulator (sm01_solarsim.member_states / member_trades) on the same underlying 1-min hist
data SM06's run_hist.py used (vote_state_3m_hist.parquet itself only stores the AGGREGATE
vote_pend, no per-member columns -- confirmed by inspection).

Executor: "same executor conventions as SMV2H2 gate B" (runs/SMV2H2_ONELOT_CONFIRM/
confirm_gate_b.py run_policy_hist) -- close-only substrate (no OHLC on the hist file):
decisions at 3m close, fills at NEXT 3m bar CLOSE +-1 tick (uncapped), session-close
flatten at last-bar close +-1 tick, dev ops windows kept verbatim (flatten decided 16:39,
freeze 16:30-18:03), NQ costs $2.18/side, point value $20.

Data: research/scalping_lab/substrate/minute/NQ/nq1m_2005_202605.parquet, filtered
< 2022-01-01 (identical filter to SM06's run_hist.py) -- entirely pre-2022, no VIRGIN
violation possible.
"""
import sys, os, json, time
import numpy as np, pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
import sm01_solarsim as sm

RUN = os.path.join(ROOT, "runs", "SMV2T_NOFAST_R2")
OUT = os.path.join(RUN, "out")
TICK = 0.25; COMM = 2.18; PV = 20.0

t0 = time.time()

# ---------------- rebuild per-member pend on hist (verbatim SM06 run_hist.py construction) ----------------
print("loading hist 1-min data ...", flush=True)
h = pd.read_parquet(os.path.join(ROOT, "research", "scalping_lab", "substrate", "minute", "NQ",
                                  "nq1m_2005_202605.parquet"))
h["time"] = pd.to_datetime(h["time"])
h = h[h["time"] < "2022-01-01"].reset_index(drop=True)
bars = sm.resample_3m(h)
print("hist 3m bars:", len(bars), bars.time.min(), "->", bars.time.max(), flush=True)

close = bars.close.to_numpy()
sig = sm.sigma_series(close)
POS, PEND = [], []
for vm in sm.VMS:
    is_up, flip, s_eff, anchor = sm.member_states(close, sig, float(vm))
    fills, pos, pend = sm.member_trades(bars, is_up, flip, s_eff, anchor)
    POS.append(pos); PEND.append(pend)
    print(f"vm{vm}: {len(fills)} fills", flush=True)
pos = np.column_stack(POS); pend = np.column_stack(PEND)

# ---------------- integrity check vs committed vote_state_3m_hist.parquet (aggregate only) ----------------
hd = pd.read_parquet(os.path.join(ROOT, "runs", "SM06_SOLAR_HISTORY", "out",
                                   "vote_state_3m_hist.parquet"))
assert len(hd) == len(bars), f"length mismatch {len(hd)} vs {len(bars)}"
assert (pd.to_datetime(hd["time"]).to_numpy() == bars["time"].to_numpy()).all(), "time axis mismatch"
my_vote_pend = pend.sum(axis=1)
vote_pend_match = float((my_vote_pend == hd["vote_pend"].to_numpy()).mean())
print("reconstructed vote_pend match vs committed hist substrate:", vote_pend_match, flush=True)
assert vote_pend_match >= 0.9999, "hist per-member reconstruction FAILED to reproduce committed aggregate"

VMS = list(sm.VMS)
FAST = [6, 8, 10, 12]
idx_nofast = [i for i, v in enumerate(VMS) if v not in FAST]
members_nofast = [VMS[i] for i in idx_nofast]

tgt_all_hist = sm.e10_target(pend)                       # ALL / incumbent core
tgt_nofast_hist = sm.e10_target(pend[:, idx_nofast])      # no-FAST core (9 members)

# cross-check ALL core reproduces SM06's own committed e10 target-driven daily curve
# (via the standard OHLC MNQ e10_sim, as an independent sanity check of pend fidelity --
# NOT the executor used for the gate C comparison itself, see below)
ref_daily_mnq = sm.e10_sim(bars, tgt_all_hist)  # default MNQ costs, OHLC-based fills
ref_committed = pd.read_csv(os.path.join(ROOT, "runs", "SM06_SOLAR_HISTORY", "out",
                                          "e10_daily_hist.csv"))
ref_committed["sess"] = pd.to_datetime(ref_committed["sess"]).dt.date
rd = ref_daily_mnq.copy(); rd["sess"] = pd.to_datetime(rd["sess"]).dt.date
jj = ref_committed.merge(rd, on="sess", suffixes=("_ref", "_my"))
mnq_check_max_dev = float(np.abs(jj["net_ref"] - jj["net_my"]).max())
print("ALL-core OHLC-MNQ e10_sim cross-check vs committed e10_daily_hist.csv, "
      f"max|dev| = {mnq_check_max_dev}, sessions matched {len(jj)}/{len(ref_committed)}", flush=True)

# ---------------- gate C executor: SMV2H2-gate-B convention (close-only, +-1 tick, ops windows, NQ) ----------------
def run_policy_hist(df, desired, comm, pv):
    n = len(df)
    c = df["close"].to_numpy(); last = df["is_last_of_sess"].to_numpy()
    tm = pd.to_datetime(df["time"])
    hm = tm.dt.hour.to_numpy() * 100 + tm.dt.minute.to_numpy()
    sd = df["sess_date"].to_numpy()
    cash = 0.0; p = 0; pend_ = 0; daily = {}; prev = 0.0
    fills = 0; entries = 0
    for t in range(n):
        if pend_ != p:
            d = pend_ - p; side = 1 if d > 0 else -1
            px = c[t] + side * TICK
            cash -= d * px * pv; cash -= abs(d) * comm
            if pend_ != 0:
                entries += 1
            p = pend_; fills += 1
        if last[t] and p != 0:
            side = -1 if p > 0 else 1
            px = c[t] + side * TICK
            cash += p * px * pv; cash -= abs(p) * comm
            fills += 1; p = 0; pend_ = 0
        else:
            want = int(desired[t])
            if hm[t] == 1639:
                pend_ = 0
            elif 1630 <= hm[t] < 1803:
                pend_ = p if hm[t] < 1639 else 0
            else:
                pend_ = want
        if last[t]:
            eqv = cash + p * c[t] * pv
            daily[sd[t]] = eqv - prev; prev = eqv
    dl = pd.Series(daily); dl.index = pd.to_datetime(dl.index)
    return dl, fills, entries

print("gate C replay (close +-1 tick, NQ-scaled, ops windows) ...", flush=True)
dl_all, f_all, e_all = run_policy_hist(bars, tgt_all_hist, COMM, PV)
dl_nofast, f_nofast, e_nofast = run_policy_hist(bars, tgt_nofast_hist, COMM, PV)
assert (dl_all.index == dl_nofast.index).all()
pd.DataFrame({"ALL_core": dl_all, "NOFAST_core": dl_nofast}).to_csv(
    os.path.join(OUT, "gate_C_hist_curves.csv"))

def battery(dl):
    net = dl.values; eqd = np.cumsum(net); pk = np.maximum.accumulate(eqd); dd = pk - eqd
    k = max(1, int(0.05 * len(net)))
    sd_ = net.std(ddof=1)
    return {"n_days": len(net), "net": net.sum(),
            "sharpe": net.mean() / sd_ * np.sqrt(252) if sd_ > 0 else np.nan,
            "maxDD_eod": dd.max(), "CDaR5": np.sort(dd)[::-1][:k].mean()}

yrs_span = (dl_all.index.max() - dl_all.index.min()).days / 365.25
b_all, b_nofast = battery(dl_all), battery(dl_nofast)

c1 = b_nofast["net"] >= b_all["net"] - 10000.0
c2 = b_nofast["maxDD_eod"] <= 1.25 * b_all["maxDD_eod"]
gateC_pass = bool(c1 and c2)

ya = dl_all.groupby(dl_all.index.year).sum(); yn = dl_nofast.groupby(dl_nofast.index.year).sum()
yearly = pd.DataFrame({"ALL_core": ya, "NOFAST_core": yn})
yearly["d_net"] = yearly["NOFAST_core"] - yearly["ALL_core"]
yearly.to_csv(os.path.join(OUT, "gate_C_yearly.csv"))

gate_c = pd.DataFrame([{
    "n_hist_bars": len(bars), "hist_start": str(bars.sess_date.min()), "hist_end": str(bars.sess_date.max()),
    "n_years": len(ya), "years_span": yrs_span,
    "vote_pend_reconstruction_match": vote_pend_match,
    "ALL_core_mnq_e10sim_crosscheck_max_abs_dev_$": mnq_check_max_dev,
    "net_ALL": b_all["net"], "net_NOFAST": b_nofast["net"], "net_gap": b_nofast["net"] - b_all["net"],
    "sharpe_ALL": b_all["sharpe"], "sharpe_NOFAST": b_nofast["sharpe"],
    "maxDD_ALL": b_all["maxDD_eod"], "maxDD_NOFAST": b_nofast["maxDD_eod"],
    "maxDD_ratio_NOFAST_over_ALL": b_nofast["maxDD_eod"] / b_all["maxDD_eod"],
    "CDaR5_ALL": b_all["CDaR5"], "CDaR5_NOFAST": b_nofast["CDaR5"],
    "fills_ALL": f_all, "fills_NOFAST": f_nofast,
    "entries_ALL": e_all, "entries_NOFAST": e_nofast,
    "gate_c1_net_ge_incumbent_minus_10k": bool(c1),
    "gate_c2_maxDD_le_1.25x_incumbent": bool(c2),
    "gateC_pass": gateC_pass,
    "worst_year_ALL": int(ya.idxmin()), "worst_year_ALL_net": float(ya.min()),
    "worst_year_NOFAST": int(yn.idxmin()), "worst_year_NOFAST_net": float(yn.min()),
    "runtime_s": round(time.time() - t0, 1),
}])
gate_c.to_csv(os.path.join(OUT, "gate_C.csv"), index=False)
print(gate_c.to_string(index=False), flush=True)
print("\nyearly:\n" + yearly.round(0).to_string(), flush=True)

json.dump({"gateC_pass": gateC_pass, "c1_net": bool(c1), "c2_dd": bool(c2),
           "vote_pend_reconstruction_match": vote_pend_match},
          open(os.path.join(OUT, "gate_C_summary.json"), "w"), indent=2)
print("\ndone gate C", flush=True)
