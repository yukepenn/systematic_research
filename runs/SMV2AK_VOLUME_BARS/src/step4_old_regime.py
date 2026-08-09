"""SMV2AK sub_441 -- old-regime screen (DIAGNOSTIC, conditional on the sub_440
arm qualifying as CANDIDATE). IDENTICAL contingency structure to SMV2AD
sub_417 / SMV2AI sub_432: if sub_440 produced zero CANDIDATEs, this screen is
explicitly N/A, disclosed via status=NONE_QUALIFIED (not silently skipped) --
out/old_regime_screen.csv is still written with a single explanatory row so
the required output artifact exists.

Retained machinery (not exercised this wave, since sub_440 has zero
candidates): if a future wave revisits this lead with a genuinely new
calibration and produces a CANDIDATE, this script's rebuild path is ready --
native 1-minute 2006-2021 substrate (research/scalping_lab/substrate/minute/
NQ/nq1m_2005_202605.parquet, confirmed available, SMV2AF gate C precedent),
session-tagged via the SAME gap-heuristic as the dev construction, volume
bars built with the IDENTICAL frozen V from sub_438 (NOT re-calibrated on
hist -- same discipline as every prior old-regime rescale reuse in this
program), DUAL_HTF-transformed (per spec: "rebuild the DUAL-transformed
decision object"), floor net >= incumbent - $10k AND maxDD <= 1.25x
incumbent, "incumbent" here being the hist 3m-control's OWN DUAL-transformed
result (not the raw non-DUAL hist control SMV2AD/SMV2AI's sub_417/432 used --
FLAGGED interpretive call, see REPORT: this spec's text explicitly says to
compare the DUAL-transformed decision object, a deliberate deviation from the
raw-target comparison those two precedent screens used).
"""
import os, json, time
import numpy as np, pandas as pd

import sys
sys.path.insert(0, os.path.dirname(__file__))
from common import (ROOT, OUT, INCUMBENT_VMS, HIST1M_PATH, tag_sessions,
                     build_volume_bars, dual_htf, htf_state, run_policy_hist, battery_hist)
import sm01_solarsim as sm

t0 = time.time()

sub440_v = json.load(open(os.path.join(OUT, "sub440_verdict.json")))
is_candidate = sub440_v["CANDIDATE"]

if not is_candidate:
    row = {
        "status": "NONE_QUALIFIED",
        "reason": "sub_440 produced ZERO CANDIDATEs (sharpe_volbar=0.4305 < sharpe_control=0.7092, "
                  "FAILS improve; CDaR_0.95_volbar=34249.5 > CDaR_0.95_control=27161.8, FAILS "
                  "improve; top10_day_retention=0.9421 < 0.95, FAILS retention) -- old-regime "
                  "screen is conditional on the sub_440 arm qualifying as CANDIDATE; it did not, "
                  "so nothing is rebuilt on the 2006-2021 native 1-minute substrate this wave.",
        "sub440_candidate": str(is_candidate),
    }
    pd.DataFrame([row]).to_csv(os.path.join(OUT, "old_regime_screen.csv"), index=False)
    print(json.dumps(row, indent=2))
    print("sub_441: NONE_QUALIFIED -- no candidate to screen. Rebuild machinery retained in this "
          "script for a future wave.", flush=True)
else:
    # ---- retained path, not exercised this wave (sub_440 produced zero candidates) ----
    hcols = pd.read_parquet(HIST1M_PATH, columns=None).columns.tolist()
    required = {"open", "high", "low", "close", "volume"}
    has_ohlcv = required.issubset(set(hcols))
    print(f"hist substrate columns: {hcols}, OHLCV present: {has_ohlcv}", flush=True)
    if not has_ohlcv:
        row = {"status": "BLOCKED-BY-DATA",
               "reason": f"hist substrate columns {hcols} do not carry OHLCV -- cannot build "
                         "volume bars without both a volume column and OHLC."}
        pd.DataFrame([row]).to_csv(os.path.join(OUT, "old_regime_screen.csv"), index=False)
        raise SystemExit("BLOCKED-BY-DATA: sub_441 aborted, see out/old_regime_screen.csv")

    meta_V = json.load(open(os.path.join(OUT, "V_frozen.json")))
    V = meta_V["V_frozen"]
    meta_v = json.load(open(os.path.join(OUT, "scale_ratio_volbar_meta.json")))
    R_volbar = meta_v["R_SELECTED_whole_dev_median"]
    N_volbar = meta_v["N_volume_bars"]
    VMS_VOLBAR = [v * R_volbar for v in sm.VMS]

    h = pd.read_parquet(HIST1M_PATH)
    h["time"] = pd.to_datetime(h["time"])
    h = h[h["time"] < "2022-01-01"].reset_index(drop=True)
    h_tagged = tag_sessions(h)
    print(f"hist 1m bars (2006-2021), session-tagged: {len(h_tagged)} rows, "
          f"{h_tagged['sess_id'].nunique()} sessions", flush=True)

    hist_bars3 = sm.resample_3m(h)
    hist_volbars = build_volume_bars(h_tagged, V)
    print(f"hist 3m bars: {len(hist_bars3)}; hist volume bars (V={V:.4f} frozen from dev, "
          f"NOT re-calibrated on hist): {len(hist_volbars)}", flush=True)

    sig_hist3 = sm.sigma_series(hist_bars3["close"].to_numpy())
    sig_hist_volbar = sm.sigma_series(hist_volbars["close"].to_numpy(), vol_period=N_volbar,
                                       min_count=30)

    def build_tgt(bars, sig, vms):
        pend = []
        for vmv in vms:
            is_up, flip, s_eff, anchor = sm.member_states(
                bars["close"].to_numpy(), sig, float(vmv), smin_ticks=40.0, smax_ticks=1200.0)
            _, _, p = sm.member_trades(bars, is_up, flip, s_eff, anchor)
            pend.append(p)
        return sm.e10_target(np.column_stack(pend))

    tgt_ctrl_hist = build_tgt(hist_bars3, sig_hist3, INCUMBENT_VMS)
    tgt_vb_hist = build_tgt(hist_volbars, sig_hist_volbar, VMS_VOLBAR)

    # DUAL_HTF transform on the raw hist targets, per spec ("rebuild the
    # DUAL-transformed decision object"), each on its own bar cadence
    st_ctrl = htf_state(hist_bars3)
    st_vb = htf_state(hist_volbars)
    Tpp_ctrl = dual_htf(tgt_ctrl_hist.astype(float), st_ctrl).astype(int)
    Tpp_vb = dual_htf(tgt_vb_hist.astype(float), st_vb).astype(int)

    dl_ctrl, _, _ = run_policy_hist(hist_bars3, Tpp_ctrl)
    dl_vb, _, _ = run_policy_hist(hist_volbars, Tpp_vb)
    b_ctrl = battery_hist(dl_ctrl)
    b_vb = battery_hist(dl_vb)

    c1 = b_vb["net"] >= b_ctrl["net"] - 10000.0
    c2 = b_vb["maxDD_eod"] <= 1.25 * b_ctrl["maxDD_eod"]
    row = {
        "arm": "volbar_DUAL6040_hist", "net_hist": b_vb["net"], "net_incumbent_hist": b_ctrl["net"],
        "net_gap": b_vb["net"] - b_ctrl["net"],
        "sharpe_hist": b_vb["sharpe"], "sharpe_incumbent_hist": b_ctrl["sharpe"],
        "maxDD_hist": b_vb["maxDD_eod"], "maxDD_incumbent_hist": b_ctrl["maxDD_eod"],
        "maxDD_ratio": b_vb["maxDD_eod"] / b_ctrl["maxDD_eod"],
        "CDaR5_hist": b_vb["CDaR5"], "CDaR5_incumbent_hist": b_ctrl["CDaR5"],
        "pass_c1_net_ge_incumbent_minus_10k": bool(c1),
        "pass_c2_maxDD_le_1.25x_incumbent": bool(c2),
        "screen_pass": bool(c1 and c2),
    }
    pd.DataFrame([row]).to_csv(os.path.join(OUT, "old_regime_screen.csv"), index=False)
    print(pd.DataFrame([row]).to_string(index=False), flush=True)

print(f"done sub_441, {round(time.time()-t0, 1)}s", flush=True)
