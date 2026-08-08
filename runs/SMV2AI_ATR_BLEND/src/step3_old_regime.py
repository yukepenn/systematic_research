"""SMV2AI sub_432 -- old-regime screen (DIAGNOSTIC, conditional on >=1
CANDIDATE from sub_431). IDENTICAL contingency structure to SMV2AD sub_417 /
SMV2AG sub_425.

Data check FIRST (per spec, do not approximate high/low from close-only data):
the SM06 hist substrate (research/scalping_lab/substrate/minute/NQ/
nq1m_2005_202605.parquet) carries columns
['time','open','high','low','close','volume'] -- verified below programmatically
before any TR is computed. If this check fails, this script aborts and
BLOCKED-BY-DATA is reported explicitly (see the assert below); it did NOT fail
in this run (columns confirmed present, see the printed check).

Methodological note (HYPOTHESIS/interpretive call, disclosed): R_SELECTED (the
ATR/sigma460 rescale ratio) is the FROZEN dev-derived scalar from sub_430, used
AS-IS on the hist substrate -- NOT re-derived on hist data. Re-deriving it on
hist would defeat the purpose of an out-of-sample structural check (this
mirrors SMV2AE's own discipline of freezing a rescale factor once and reusing
it, never re-fit per regime).
"""
import sys, os, json, time
import numpy as np, pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
from common import ROOT, OUT, atr_series, INCUMBENT_VMS
import sm01_solarsim as sm

TICK = 0.25; COMM = 2.18; PV = 20.0


def run_policy_hist(df, desired, comm, pv):
    """Verbatim runs/SMV2AD_VOLMULT_CEILING/src/sub417_old_regime.py
    run_policy_hist (SMV2H2 gate-B executor convention on the close-only hist
    substrate)."""
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


def battery(dl):
    net = dl.values; eqd = np.cumsum(net); pk = np.maximum.accumulate(eqd); dd = pk - eqd
    k = max(1, int(0.05 * len(net)))
    sd_ = net.std(ddof=1)
    return {"n_days": len(net), "net": net.sum(),
            "sharpe": net.mean() / sd_ * np.sqrt(252) if sd_ > 0 else np.nan,
            "maxDD_eod": dd.max(), "CDaR5": np.sort(dd)[::-1][:k].mean()}


sub431_v = json.load(open(os.path.join(OUT, "sub431_verdict.json")))
candidates = sub431_v["candidates"]

if not candidates:
    row = {
        "status": "NONE_QUALIFIED",
        "reason": "sub_431 produced zero CANDIDATEs -- old-regime screen is conditional "
                  "on >=1 CANDIDATE; none exists this wave, so nothing is rebuilt on the "
                  "SM06 hist substrate.",
        "sub431_candidates": str(candidates),
    }
    pd.DataFrame([row]).to_csv(os.path.join(OUT, "old_regime_screen.csv"), index=False)
    print(json.dumps(row, indent=2))
    print("sub_432: NONE_QUALIFIED -- no candidates to screen.", flush=True)
else:
    t0 = time.time()
    hist_path = os.path.join(ROOT, "research", "scalping_lab", "substrate", "minute", "NQ",
                              "nq1m_2005_202605.parquet")

    # ---- BLOCKED-BY-DATA check FIRST: verify OHLC (not close-only) ----
    hcols = pd.read_parquet(hist_path, columns=None).columns.tolist()
    required = {"open", "high", "low", "close"}
    has_ohlc = required.issubset(set(hcols))
    print(f"SM06 hist substrate columns: {hcols}", flush=True)
    print(f"OHLC present (required for TR): {has_ohlc}", flush=True)
    if not has_ohlc:
        row = {"status": "BLOCKED-BY-DATA",
               "reason": f"SM06 hist substrate columns {hcols} do NOT carry OHLC -- "
                         "cannot compute true range without high/low; per spec, high/low "
                         "is NOT approximated from close-only data."}
        pd.DataFrame([row]).to_csv(os.path.join(OUT, "old_regime_screen.csv"), index=False)
        print(json.dumps(row, indent=2))
        raise SystemExit("BLOCKED-BY-DATA: sub_432 aborted, see out/old_regime_screen.csv")

    h = pd.read_parquet(hist_path)
    h["time"] = pd.to_datetime(h["time"])
    h = h[h["time"] < "2022-01-01"].reset_index(drop=True)
    hist_bars = sm.resample_3m(h)
    print(f"hist bars (2006-2021): {len(hist_bars)}, {hist_bars['time'].min()} -> "
          f"{hist_bars['time'].max()}", flush=True)

    sig_hist = sm.sigma_series(hist_bars["close"].to_numpy())
    atr_hist, tr_hist = atr_series(hist_bars, vol_period=460, min_count=30)

    R_atr_meta = json.load(open(os.path.join(OUT, "atr_construction_meta.json")))
    R_SELECTED = R_atr_meta["R_SELECTED_whole_dev_median"]
    sigma_ATR_eff_hist = atr_hist / R_SELECTED
    print(f"R_SELECTED (frozen from dev sub_430, applied as-is to hist): {R_SELECTED:.6f}", flush=True)

    # ---- control (w=1.00, pure sigma460) on hist ----
    pend_ctrl = []
    for vm_ in INCUMBENT_VMS:
        is_up, flip, s_eff, anchor = sm.member_states(
            hist_bars["close"].to_numpy(), sig_hist, float(vm_), smin_ticks=40.0, smax_ticks=1200.0)
        _, _, p = sm.member_trades(hist_bars, is_up, flip, s_eff, anchor)
        pend_ctrl.append(p)
    pend_ctrl = np.column_stack(pend_ctrl)
    tgt_ctrl = sm.e10_target(pend_ctrl)
    dl_control_hist, _, _ = run_policy_hist(hist_bars, tgt_ctrl, COMM, PV)
    b_ctrl = battery(dl_control_hist)
    print(f"control (w=1.00) hist: net={b_ctrl['net']:.0f} sharpe={b_ctrl['sharpe']:.3f} "
          f"maxDD={b_ctrl['maxDD_eod']:.0f} CDaR5={b_ctrl['CDaR5']:.0f}", flush=True)

    ARM_W = {"arm_REPLACE": 0.00, "arm_BLEND_25": 0.25, "arm_BLEND_50": 0.50, "arm_BLEND_75": 0.75}

    rows = []
    for cand in candidates:
        w = ARM_W[cand]
        sig_arm_hist = w * sig_hist + (1.0 - w) * sigma_ATR_eff_hist
        pend = []
        for vm_ in INCUMBENT_VMS:
            is_up, flip, s_eff, anchor = sm.member_states(
                hist_bars["close"].to_numpy(), sig_arm_hist, float(vm_), smin_ticks=40.0, smax_ticks=1200.0)
            _, _, p = sm.member_trades(hist_bars, is_up, flip, s_eff, anchor)
            pend.append(p)
        pend = np.column_stack(pend)
        tgt = sm.e10_target(pend)
        dl, f, e = run_policy_hist(hist_bars, tgt, COMM, PV)
        b = battery(dl)
        c1 = b["net"] >= b_ctrl["net"] - 10000.0
        c2 = b["maxDD_eod"] <= 1.25 * b_ctrl["maxDD_eod"]
        row = {
            "arm": cand, "w_sigma460_weight": w,
            "net_hist": b["net"], "net_incumbent_hist": b_ctrl["net"],
            "net_gap": b["net"] - b_ctrl["net"],
            "sharpe_hist": b["sharpe"], "sharpe_incumbent_hist": b_ctrl["sharpe"],
            "maxDD_hist": b["maxDD_eod"], "maxDD_incumbent_hist": b_ctrl["maxDD_eod"],
            "maxDD_ratio": b["maxDD_eod"] / b_ctrl["maxDD_eod"],
            "CDaR5_hist": b["CDaR5"], "CDaR5_incumbent_hist": b_ctrl["CDaR5"],
            "pass_c1_net_ge_incumbent_minus_10k": bool(c1),
            "pass_c2_maxDD_le_1.25x_incumbent": bool(c2),
            "screen_pass": bool(c1 and c2),
        }
        rows.append(row)
        print(f"{cand}: net_hist={b['net']:.0f} (incumbent {b_ctrl['net']:.0f}, gap "
              f"{b['net']-b_ctrl['net']:.0f}) maxDD_hist={b['maxDD_eod']:.0f} "
              f"(1.25x incumbent={1.25*b_ctrl['maxDD_eod']:.0f}) screen_pass={c1 and c2}", flush=True)

    pd.DataFrame(rows).to_csv(os.path.join(OUT, "old_regime_screen.csv"), index=False)
    print("\n=== old_regime_screen.csv ===")
    print(pd.DataFrame(rows).to_string(index=False), flush=True)
    print("done sub_432", round(time.time() - t0, 1), "s", flush=True)
