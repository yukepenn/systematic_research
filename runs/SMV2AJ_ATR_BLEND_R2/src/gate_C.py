"""SMV2AJ_ATR_BLEND_R2 -- Gate C: re-verify on the SM06 2006-2021 hist substrate,
at the DUAL-TRANSFORMED object this time. step0_verify.py already confirmed
(by direct source read of runs/SMV2AI_ATR_BLEND/src/step3_old_regime.py) that
SMV2AI's own sub_432 old-regime screen tested the RAW pre-DUAL-transform target
(sm.e10_target(pend) -> run_policy_hist directly, no dual_htf call anywhere in
that file) -- so THIS gate, which applies dual_htf on hist before replaying, is
a genuine re-test, not a duplicate of sub_432.

R_ATR_SELECTED = 2.025539235146222 reused verbatim from SMV2AI sub_430 (NOT
re-derived on hist -- same disclosed methodological choice SMV2AI itself made).

Executor: same convention as SMV2T_NOFAST_R2 gate_C.py / SMV2H2 gate B
(close-only substrate, fills at NEXT 3m bar CLOSE +-1 tick, session-close
flatten, ops windows kept verbatim (flatten decided 16:39, freeze 16:30-18:03),
NQ costs $2.18/side, point value $20) -- applied to the DUAL-transformed target
Tpp (not the raw target).

Bar: net >= incumbent - $10k AND maxDD <= 1.25x incumbent.
"""
import sys, os, json, time
import numpy as np, pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
sys.path.insert(0, os.path.join(ROOT, "runs", "SMV2AI_ATR_BLEND", "src"))
import sm01_solarsim as sm
from common import atr_series, INCUMBENT_VMS, dual_htf, rha

RUN = os.path.join(ROOT, "runs", "SMV2AJ_ATR_BLEND_R2")
OUT = os.path.join(RUN, "out")
TICK = 0.25; COMM = 2.18; PV = 20.0
W = 0.75

t0 = time.time()

# ---------------- hist substrate (identical filter/resample to SM06/SMV2AI sub_432) ----------------
print("loading hist 1-min data ...", flush=True)
h = pd.read_parquet(os.path.join(ROOT, "research", "scalping_lab", "substrate", "minute", "NQ",
                                  "nq1m_2005_202605.parquet"))
h["time"] = pd.to_datetime(h["time"])
h = h[h["time"] < "2022-01-01"].reset_index(drop=True)
hist_bars = sm.resample_3m(h)
print(f"hist bars (2006-2021): {len(hist_bars)}, {hist_bars['time'].min()} -> "
      f"{hist_bars['time'].max()}", flush=True)

close = hist_bars["close"].to_numpy()
sig_hist = sm.sigma_series(close)
atr_hist, tr_hist = atr_series(hist_bars, vol_period=460, min_count=30)

R_SELECTED = json.load(open(os.path.join(OUT, "step0_verify.json")))["R_SELECTED_reused_verbatim"]
sigma_ATR_eff_hist = atr_hist / R_SELECTED
print(f"R_SELECTED (frozen, reused verbatim from dev sub_430): {R_SELECTED:.9f}", flush=True)

sig_control_hist = sig_hist
sig_blend75_hist = W * sig_hist + (1.0 - W) * sigma_ATR_eff_hist

# ---------------- raw per-member pend + target on hist ----------------
def build_pend_hist(sig):
    PEND = []
    for vm_ in INCUMBENT_VMS:
        is_up, flip, s_eff, anchor = sm.member_states(close, sig, float(vm_), smin_ticks=40.0, smax_ticks=1200.0)
        _, _, p = sm.member_trades(hist_bars, is_up, flip, s_eff, anchor)
        PEND.append(p)
    return np.column_stack(PEND)

pend_control_hist = build_pend_hist(sig_control_hist)
pend_blend75_hist = build_pend_hist(sig_blend75_hist)
tgt_control_hist = sm.e10_target(pend_control_hist)
tgt_blend75_hist = sm.e10_target(pend_blend75_hist)

# ---- integrity check 1: reconstructed vote_pend (control/sigma460-only, ALL 13-member core)
#      matches the committed SM06 hist substrate aggregate (identical check to SMV2T gate_C.py) ----
hd = pd.read_parquet(os.path.join(ROOT, "runs", "SM06_SOLAR_HISTORY", "out",
                                   "vote_state_3m_hist.parquet"))
assert len(hd) == len(hist_bars), f"length mismatch {len(hd)} vs {len(hist_bars)}"
assert (pd.to_datetime(hd["time"]).to_numpy() == hist_bars["time"].to_numpy()).all(), "time axis mismatch"
my_vote_pend = pend_control_hist.sum(axis=1)
vote_pend_match = float((my_vote_pend == hd["vote_pend"].to_numpy()).mean())
print("reconstructed vote_pend (control) match vs committed hist substrate:", vote_pend_match, flush=True)
assert vote_pend_match >= 0.9999, "hist per-member reconstruction FAILED to reproduce committed aggregate"

# ---- integrity check 2: raw tgt_control_hist / tgt_blend75_hist reproduce SMV2AI sub_432's
#      own raw hist target curves (b_ctrl / arm_BLEND_75 rows in old_regime_screen.csv) by
#      running each through sub_432's OWN run_policy_hist and comparing net -- confirms our
#      pend/tgt construction here is identical to sub_432's, and isolates the DUAL-transform
#      step as the ONLY methodological difference from sub_432. ----
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

dl_ctrl_raw, _, _ = run_policy_hist(hist_bars, tgt_control_hist, COMM, PV)
dl_75_raw, _, _ = run_policy_hist(hist_bars, tgt_blend75_hist, COMM, PV)
ref_screen = pd.read_csv(os.path.join(ROOT, "runs", "SMV2AI_ATR_BLEND", "out", "old_regime_screen.csv"))
ref_row = ref_screen[ref_screen["arm"] == "arm_BLEND_75"].iloc[0]
raw_ctrl_net_dev = abs(dl_ctrl_raw.sum() - ref_row["net_incumbent_hist"])
raw_75_net_dev = abs(dl_75_raw.sum() - ref_row["net_hist"])
print(f"RAW hist net cross-check vs SMV2AI sub_432 old_regime_screen.csv: "
      f"control |dev|=${raw_ctrl_net_dev:.4f}, arm_BLEND_75 |dev|=${raw_75_net_dev:.4f}", flush=True)
assert raw_ctrl_net_dev < 1.0 and raw_75_net_dev < 1.0, \
    "raw hist target/executor reconstruction does not match SMV2AI sub_432 -- cannot isolate DUAL-transform effect"

# ---------------- DUAL_HTF transform on hist (prior-session close vs SMA50 of session closes) ----------------
sclose_hist = hist_bars.loc[hist_bars["is_last_of_sess"], ["sess_date", "close"]].set_index("sess_date")["close"]
htf_hist = np.sign(sclose_hist - sclose_hist.rolling(50).mean()).shift(1).to_dict()
st_bar_hist = np.array([htf_hist.get(d, np.nan) for d in hist_bars["sess_date"]])

Tpp_control_hist = dual_htf(tgt_control_hist.astype(float), st_bar_hist)
Tpp_blend75_hist = dual_htf(tgt_blend75_hist.astype(float), st_bar_hist)

print("gate C replay (DUAL-transformed, close +-1 tick, NQ-scaled, ops windows) ...", flush=True)
dl_control, f_control, e_control = run_policy_hist(hist_bars, Tpp_control_hist, COMM, PV)
dl_blend75, f_blend75, e_blend75 = run_policy_hist(hist_bars, Tpp_blend75_hist, COMM, PV)
assert (dl_control.index == dl_blend75.index).all()
pd.DataFrame({"DUAL_CONTROL_hist": dl_control, "DUAL_BLEND75_hist": dl_blend75}).to_csv(
    os.path.join(OUT, "gate_C_hist_curves.csv"))


def battery(dl):
    net = dl.values; eqd = np.cumsum(net); pk = np.maximum.accumulate(eqd); dd = pk - eqd
    k = max(1, int(0.05 * len(net)))
    sd_ = net.std(ddof=1)
    return {"n_days": len(net), "net": net.sum(),
            "sharpe": net.mean() / sd_ * np.sqrt(252) if sd_ > 0 else np.nan,
            "maxDD_eod": dd.max(), "CDaR5": np.sort(dd)[::-1][:k].mean()}


yrs_span = (dl_control.index.max() - dl_control.index.min()).days / 365.25
b_control, b_blend75 = battery(dl_control), battery(dl_blend75)

c1 = b_blend75["net"] >= b_control["net"] - 10000.0
c2 = b_blend75["maxDD_eod"] <= 1.25 * b_control["maxDD_eod"]
gateC_pass = bool(c1 and c2)

ya = dl_control.groupby(dl_control.index.year).sum(); yb = dl_blend75.groupby(dl_blend75.index.year).sum()
yearly = pd.DataFrame({"DUAL_CONTROL": ya, "DUAL_BLEND75": yb})
yearly["d_net"] = yearly["DUAL_BLEND75"] - yearly["DUAL_CONTROL"]
yearly.to_csv(os.path.join(OUT, "gate_C_yearly.csv"))

gate_c = pd.DataFrame([{
    "n_hist_bars": len(hist_bars), "hist_start": str(hist_bars.sess_date.min()),
    "hist_end": str(hist_bars.sess_date.max()),
    "n_years": len(ya), "years_span": yrs_span,
    "vote_pend_reconstruction_match": vote_pend_match,
    "raw_hist_crosscheck_control_max_abs_dev_$": raw_ctrl_net_dev,
    "raw_hist_crosscheck_blend75_max_abs_dev_$": raw_75_net_dev,
    "R_SELECTED_reused_verbatim": R_SELECTED,
    "net_CONTROL": b_control["net"], "net_BLEND75": b_blend75["net"], "net_gap": b_blend75["net"] - b_control["net"],
    "sharpe_CONTROL": b_control["sharpe"], "sharpe_BLEND75": b_blend75["sharpe"],
    "maxDD_CONTROL": b_control["maxDD_eod"], "maxDD_BLEND75": b_blend75["maxDD_eod"],
    "maxDD_ratio_BLEND75_over_CONTROL": b_blend75["maxDD_eod"] / b_control["maxDD_eod"],
    "CDaR5_CONTROL": b_control["CDaR5"], "CDaR5_BLEND75": b_blend75["CDaR5"],
    "fills_CONTROL": f_control, "fills_BLEND75": f_blend75,
    "entries_CONTROL": e_control, "entries_BLEND75": e_blend75,
    "gate_c1_net_ge_incumbent_minus_10k": bool(c1),
    "gate_c2_maxDD_le_1.25x_incumbent": bool(c2),
    "gateC_pass": gateC_pass,
    "worst_year_CONTROL": int(ya.idxmin()), "worst_year_CONTROL_net": float(ya.min()),
    "worst_year_BLEND75": int(yb.idxmin()), "worst_year_BLEND75_net": float(yb.min()),
    "runtime_s": round(time.time() - t0, 1),
}])
gate_c.to_csv(os.path.join(OUT, "gate_C.csv"), index=False)
print(gate_c.to_string(index=False), flush=True)
print("\nyearly:\n" + yearly.round(0).to_string(), flush=True)

json.dump({"gateC_pass": gateC_pass, "c1_net": bool(c1), "c2_dd": bool(c2),
           "vote_pend_reconstruction_match": vote_pend_match,
           "sub432_tested_raw_not_dual_confirmed": True},
          open(os.path.join(OUT, "gate_C_summary.json"), "w"), indent=2)
print("\ndone gate C", flush=True)
