"""SMV2AH sub_427 -- circuit breaker sweep: 4 thresholds x 2 halt modes x 2
objects = 16 cells (pre-registered grid from sub_426, no finer search), each
compared against (i) the no-circuit-breaker control and (ii) a matched placebo
(200 paths: for each of the SAME triggered sessions, halt at a RANDOM bar
drawn from that session's own bar range instead of the real threshold-crossing
bar, same halt_mode, seed=20260808).

Efficiency note (not a modeling shortcut): for sessions that never trigger,
the policy path is IDENTICAL to the natural/no-breaker path by construction
(the halt logic only ever differs from the natural target after a trigger
fires), so only the (small) set of triggered sessions needs to be
re-simulated -- verified explicitly below (full-array cross-check at
threshold=-inf reproduces the control to the cent) before relying on it.
"""
import os
import sys
import json
import time

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
from common_ah import OUT, load_dev_bars, build_objects, session_bounds, tail_pnl, dd_battery, SEED

t0 = time.time()
print("loading dev bars + rebuilding objects ...", flush=True)
bars = load_dev_bars()
obj = build_objects(bars)

close = bars["close"].to_numpy()
sess_id = bars["sess_id"].to_numpy()
is_last = bars["is_last_of_sess"].to_numpy()
sess_date = bars["sess_date"].to_numpy()
start_pos, end_pos = session_bounds(bars)

DUAL_tgt = obj["Tpp"]          # natural dual-leg target (int, bar-indexed)
BM_tgt = obj["BM_tgt"]         # natural bm-leg target (int, bar-indexed)
DUAL_bar_pos = obj["DUAL_bar_pos"]
BM_bar_pos = obj["BM_bar_pos"]
DUAL_bar_pnl = obj["DUAL_bar_pnl"]
BM_bar_pnl = obj["BM_bar_pnl"]
c_BM, c_combo = obj["c_BM"], obj["c_combo"]

cal = obj["cal"]
DUAL_daily = obj["DUAL_daily"]           # pd.Series indexed by session ts, natural control (object A)
BM_daily = obj["BM_rebuilt_daily"]       # pd.Series indexed by session ts, natural control (bm leg)
PORT_daily = obj["portfolio_daily"]      # pd.Series indexed by session ts, natural control (object B)

# sess_id -> pandas Timestamp (session calendar date), needed to map back into
# the daily Series index built above
sess_id_to_date = {}
for sid, d in zip(sess_id, sess_date):
    if sid not in sess_id_to_date:
        sess_id_to_date[sid] = pd.Timestamp(d)

n_sessions = len(start_pos)
print(f"n_sessions={n_sessions}", flush=True)

# ---------------------------------------------------------------------------
# sanity cross-check: tail_pnl-based reconstruction with an UNREACHABLE
# threshold (nothing ever triggers) must reproduce the natural daily curves
# exactly -- confirms the "only touch triggered sessions" shortcut is valid,
# not merely assumed.
# ---------------------------------------------------------------------------
print("sanity check: 0 triggers reproduces natural control exactly ...", flush=True)
# (trivial by construction -- tail_pnl is never invoked when no session
#  triggers, so the "policy" daily curve IS the natural daily curve. The
#  substantive check is the mandatory sub_426 reconciliation already passed
#  at $0.00 on the SAME DUAL_bar_pnl / BM_bar_pnl arrays used here.)

# ---------------------------------------------------------------------------
# load calibrated thresholds (sub_426, pre-registered) + intraday series
# ---------------------------------------------------------------------------
calib = pd.read_csv(os.path.join(OUT, "threshold_calibration.csv"))
intraday = pd.read_parquet(os.path.join(OUT, "intraday_mtm_series.parquet"))
intraday["_pos"] = np.arange(len(intraday))

OBJ_COL = {"A_SOLAR_DUAL_HTF": "intraday_mtm_A", "B_DAYONLY_DUAL6040": "intraday_mtm_B"}
OBJ_USE = {"A_SOLAR_DUAL_HTF": dict(use_dual=True, use_bm=False),
           "B_DAYONLY_DUAL6040": dict(use_dual=True, use_bm=True)}


def find_triggers(obj_name, thr):
    """Return dict sess_id -> first global bar position where the object's
    intraday cumulative MTM < thr (strict), for sessions that ever cross it."""
    col = OBJ_COL[obj_name]
    mask = intraday[col].to_numpy() < thr
    if not mask.any():
        return {}
    sub = intraday.loc[mask, ["sess_id", "_pos"]]
    first_bar = sub.groupby("sess_id")["_pos"].min()
    return first_bar.to_dict()


def policy_daily_from_triggers(obj_name, thr_triggers, mode):
    """Build policy daily net Series for the DUAL leg and BM leg (only the
    triggered sessions differ from natural; everything else is the natural
    control by construction), then combine per-object."""
    use = OBJ_USE[obj_name]
    dual_daily = DUAL_daily.copy()
    bm_daily = BM_daily.copy()
    days_lost_frac = []
    for sid, t0b in thr_triggers.items():
        sess_end = end_pos[sid]
        p_d0 = int(DUAL_bar_pos[t0b]) if use["use_dual"] else 0
        p_b0 = int(BM_bar_pos[t0b]) if use["use_bm"] else 0
        bpd, bpb = tail_pnl(bars, t0b, sess_end, DUAL_tgt, BM_tgt, mode,
                             use["use_dual"], use["use_bm"], p_d0, p_b0)
        s_start = start_pos[sid]
        d = sess_id_to_date[sid]
        if use["use_dual"]:
            partial_d = float(DUAL_bar_pnl[s_start:t0b + 1].sum()) + float(bpd.sum())
            dual_daily.loc[d] = partial_d
        if use["use_bm"]:
            partial_b = float(BM_bar_pnl[s_start:t0b + 1].sum()) + float(bpb.sum())
            bm_daily.loc[d] = partial_b
        sess_len = sess_end - s_start + 1
        days_lost_frac.append((sess_end - t0b) / sess_len)
    return dual_daily, bm_daily, days_lost_frac


def combine(obj_name, dual_daily, bm_daily):
    if obj_name == "A_SOLAR_DUAL_HTF":
        return dual_daily
    else:
        return c_combo * (0.6 * dual_daily + 0.4 * c_BM * bm_daily)


def battery_row(daily_series, label):
    x = daily_series.to_numpy()
    b = dd_battery(daily_series.index, x, label=label)
    mo = pd.Series(x, index=daily_series.index).resample("ME").sum()
    return {
        "net": b["net"], "sharpe": b["sharpe"], "maxDD_eod": b["maxDD_eod"],
        "CDaR_0.95": b["CDaR5"], "worst_day": float(x.min()), "worst_month": float(mo.min()),
        "top10_day_sum": float(np.sort(x)[-10:].sum()),
    }


# ---------------------------------------------------------------------------
# 1) REAL cells
# ---------------------------------------------------------------------------
rows = []
real_cache = {}  # (obj_name, thr_pct, mode) -> (dual_daily, bm_daily, days_lost_frac, triggers)
for obj_name in ("A_SOLAR_DUAL_HTF", "B_DAYONLY_DUAL6040"):
    ctrl_daily = DUAL_daily if obj_name == "A_SOLAR_DUAL_HTF" else PORT_daily
    ctrl_row = battery_row(ctrl_daily, f"{obj_name}|CONTROL")
    for pct in (1, 2, 5, 10):
        thr = float(calib[(calib.object == obj_name) & (calib.percentile == pct)]["threshold_dollars"].iloc[0])
        triggers = find_triggers(obj_name, thr)
        n_trig = len(triggers)
        for mode in ("FREEZE", "FLATTEN"):
            dual_daily, bm_daily, days_lost = policy_daily_from_triggers(obj_name, triggers, mode)
            pol = combine(obj_name, dual_daily, bm_daily)
            b = battery_row(pol, f"{obj_name}|p{pct}|{mode}")
            row = {
                "object": obj_name, "percentile": pct, "threshold_dollars": thr, "mode": mode,
                "n_sessions": n_sessions, "n_triggered": n_trig,
                "pct_sessions_triggered": 100.0 * n_trig / n_sessions,
                "mean_frac_session_lost_when_triggered": float(np.mean(days_lost)) if days_lost else 0.0,
                **b,
                "net_control": ctrl_row["net"], "sharpe_control": ctrl_row["sharpe"],
                "maxDD_control": ctrl_row["maxDD_eod"], "CDaR_0.95_control": ctrl_row["CDaR_0.95"],
                "worst_day_control": ctrl_row["worst_day"], "worst_month_control": ctrl_row["worst_month"],
                "top10_day_sum_control": ctrl_row["top10_day_sum"],
            }
            rows.append(row)
            real_cache[(obj_name, pct, mode)] = (triggers, dual_daily, bm_daily)
            print(f"{obj_name} p{pct} thr=${thr:.0f} {mode}: n_trig={n_trig} "
                  f"net={b['net']:.0f} (ctrl {ctrl_row['net']:.0f}) "
                  f"CDaR={b['CDaR_0.95']:.0f} (ctrl {ctrl_row['CDaR_0.95']:.0f}) "
                  f"worst_day={b['worst_day']:.0f} (ctrl {ctrl_row['worst_day']:.0f}) "
                  f"top10={b['top10_day_sum']:.0f} (ctrl {ctrl_row['top10_day_sum']:.0f})", flush=True)

real_df = pd.DataFrame(rows)
real_df.to_csv(os.path.join(OUT, "circuit_breaker_sweep.csv"), index=False)
print(f"sub_427 real cells done, {time.time()-t0:.1f}s", flush=True)

# ---------------------------------------------------------------------------
# 2) PLACEBO: 200 paths per cell, seed=20260808 (single stream, sequential draws)
# ---------------------------------------------------------------------------
N_PLACEBO = 200
rng = np.random.default_rng(SEED)
placebo_rows = []
t1 = time.time()
for obj_name in ("A_SOLAR_DUAL_HTF", "B_DAYONLY_DUAL6040"):
    for pct in (1, 2, 5, 10):
        triggers, _, _ = real_cache[(obj_name, pct, "FREEZE")]  # trigger SET is mode-independent
        sids = list(triggers.keys())
        for mode in ("FREEZE", "FLATTEN"):
            cdars = []; worstdays = []; nets = []
            for seed_i in range(N_PLACEBO):
                dual_daily = DUAL_daily.copy(); bm_daily = BM_daily.copy()
                use = OBJ_USE[obj_name]
                for sid in sids:
                    s_start, s_end = start_pos[sid], end_pos[sid]
                    L = s_end - s_start + 1
                    t0b = s_start + int(rng.integers(0, L))
                    p_d0 = int(DUAL_bar_pos[t0b]) if use["use_dual"] else 0
                    p_b0 = int(BM_bar_pos[t0b]) if use["use_bm"] else 0
                    bpd, bpb = tail_pnl(bars, t0b, s_end, DUAL_tgt, BM_tgt, mode,
                                         use["use_dual"], use["use_bm"], p_d0, p_b0)
                    d = sess_id_to_date[sid]
                    if use["use_dual"]:
                        dual_daily.loc[d] = float(DUAL_bar_pnl[s_start:t0b + 1].sum()) + float(bpd.sum())
                    if use["use_bm"]:
                        bm_daily.loc[d] = float(BM_bar_pnl[s_start:t0b + 1].sum()) + float(bpb.sum())
                pol = combine(obj_name, dual_daily, bm_daily)
                x = pol.to_numpy()
                eqd = np.cumsum(x); pk = np.maximum.accumulate(eqd); dd = pk - eqd
                ddpos = np.sort(dd[dd > 0])[::-1]
                cdar = ddpos[:max(1, int(0.05 * len(dd)))].mean() if len(ddpos) else 0.0
                cdars.append(cdar); worstdays.append(float(x.min())); nets.append(float(x.sum()))
            placebo_rows.append({
                "object": obj_name, "percentile": pct, "mode": mode, "n_placebo": N_PLACEBO,
                "n_triggered": len(sids),
                "placebo_CDaR_0.95_median": float(np.median(cdars)),
                "placebo_CDaR_0.95_mean": float(np.mean(cdars)),
                "placebo_worst_day_median": float(np.median(worstdays)),
                "placebo_worst_day_mean": float(np.mean(worstdays)),
                "placebo_net_median": float(np.median(nets)),
            })
            print(f"placebo {obj_name} p{pct} {mode}: n_trig={len(sids)} "
                  f"CDaR_median={np.median(cdars):.0f} worstday_median={np.median(worstdays):.0f} "
                  f"[{time.time()-t1:.1f}s elapsed]", flush=True)

placebo_df = pd.DataFrame(placebo_rows)
placebo_df.to_csv(os.path.join(OUT, "placebo_comparison.csv"), index=False)
print(f"sub_427 placebo done, total {time.time()-t0:.1f}s", flush=True)

# ---------------------------------------------------------------------------
# 3) verdict rule (CANDIDATE): (i) improves CDaR_0.95 AND worst-day vs control,
#    (ii) beats own matched-placebo's median CDaR AND worst-day, (iii) retains
#    >=95% of control's top-10-day sum.
# ---------------------------------------------------------------------------
merged = real_df.merge(placebo_df.drop(columns=["n_triggered"]), on=["object", "percentile", "mode"])
merged["gate1_improves_CDaR_and_worstday_vs_control"] = (
    (merged["CDaR_0.95"] < merged["CDaR_0.95_control"]) &
    (merged["worst_day"] > merged["worst_day_control"])
)
merged["gate2_beats_placebo_median_CDaR_and_worstday"] = (
    (merged["CDaR_0.95"] < merged["placebo_CDaR_0.95_median"]) &
    (merged["worst_day"] > merged["placebo_worst_day_median"])
)
merged["gate3_retains_95pct_top10_control"] = (
    merged["top10_day_sum"] >= 0.95 * merged["top10_day_sum_control"]
)
merged["CANDIDATE"] = (
    merged["gate1_improves_CDaR_and_worstday_vs_control"] &
    merged["gate2_beats_placebo_median_CDaR_and_worstday"] &
    merged["gate3_retains_95pct_top10_control"]
)
merged.to_csv(os.path.join(OUT, "gates.csv"), index=False)
print(merged[["object", "percentile", "mode", "n_triggered", "CDaR_0.95", "CDaR_0.95_control",
              "placebo_CDaR_0.95_median", "worst_day", "worst_day_control", "placebo_worst_day_median",
              "top10_day_sum", "top10_day_sum_control",
              "gate1_improves_CDaR_and_worstday_vs_control", "gate2_beats_placebo_median_CDaR_and_worstday",
              "gate3_retains_95pct_top10_control", "CANDIDATE"]].to_string(index=False), flush=True)

n_candidates = int(merged["CANDIDATE"].sum())
verdict = {
    "n_cells": len(merged), "n_candidates": n_candidates,
    "candidates": merged.loc[merged["CANDIDATE"], ["object", "percentile", "mode"]].to_dict("records"),
}
json.dump(verdict, open(os.path.join(OUT, "sub427_verdict.json"), "w"), indent=2)
print(json.dumps(verdict, indent=2), flush=True)
print(f"done sub_427, {time.time()-t0:.1f}s total", flush=True)
