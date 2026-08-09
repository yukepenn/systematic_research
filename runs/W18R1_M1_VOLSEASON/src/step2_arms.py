"""W18R1 STEP 2 — the mechanism. arm_FULL is the ONLY decision cell; arm_HALF is
DISCLOSURE ONLY and cannot be promoted (frozen spec §3).

Verdict rule (frozen before execution): arm_FULL is a CANDIDATE iff
  Sharpe(FULL) > Sharpe(control) AND CDaR_0.95(FULL) < CDaR_0.95(control)
  AND top-10-day retention >= 95%.
No adoption this wave regardless of outcome.
"""
import os, json
import numpy as np, pandas as pd

import common as C
import sm01_solarsim as sm

bars = C.load_dev_bars()
n = len(bars)
sigma = np.load(os.path.join(C.OUT, "sigma460_dev.npy"))

f_bar, snaps = C.causal_seasonal_factor(bars)
np.save(os.path.join(C.OUT, "f_causal.npy"), f_bar)

# --- causality assertions (a leak here would invalidate everything downstream) ---
sess = bars["sess_date"].to_numpy()
uniq = pd.unique(sess)
assert len(snaps) == len(uniq), "one factor snapshot per session"
warm_mask = np.array([list(uniq).index(s) < C.WARMUP_SESSIONS for s in sess])
assert np.allclose(f_bar[warm_mask], 1.0), "warmup sessions must run f==1 (== incumbent)"
for s in uniq[:5]:
    assert np.allclose(snaps[s], 1.0), "early sessions must be f==1"
# f must be constant within a session (it is re-estimated only at session boundaries)
tmp = pd.DataFrame({"sess": sess, "slot": C.slot_index(bars), "f": f_bar})
assert tmp.groupby(["sess", "slot"])["f"].nunique().max() == 1
fac_stats = {
    "warmup_sessions": C.WARMUP_SESSIONS,
    "n_sessions": int(len(uniq)),
    "n_bars_at_f_eq_1_warmup": int(warm_mask.sum()),
    "f_mean_over_all_post_warmup_bars": float(f_bar[~warm_mask].mean()),
    "f_min": float(f_bar[~warm_mask].min()), "f_max": float(f_bar[~warm_mask].max()),
    "f_final_session_min": float(snaps[uniq[-1]].min()),
    "f_final_session_max": float(snaps[uniq[-1]].max()),
}
print("=== causal factor ===\n" + json.dumps(fac_stats, indent=2), flush=True)
json.dump(fac_stats, open(os.path.join(C.OUT, "f_causal_stats.json"), "w"), indent=2)

ARMS = {
    "control":  sigma,
    "arm_FULL": sigma * f_bar,
    "arm_HALF": sigma * np.sqrt(f_bar),
}

rows, curves, flipcounts, tgts = [], {}, {}, {}
for label, sig in ARMS.items():
    PEND, FLIPS = C.build_pend_with_flips(bars, sig)
    tgt = sm.e10_target(PEND)
    daily, bar_pos, bar_pnl = C.e10_exec(bars, tgt)
    daily.to_csv(os.path.join(C.OUT, f"daily_{label}.csv"), index=False)
    rows.append(C.metric_row(label, daily, tgt))
    curves[label] = daily.set_index(daily["sess"].astype(str))["net"]
    flipcounts[label] = FLIPS
    tgts[label] = tgt
    np.save(os.path.join(C.OUT, f"tgt_{label}.npy"), tgt)
    print(f"{label:10s} net {daily['net'].sum():>12,.0f}  "
          f"sharpe {rows[-1]['sharpe']:.4f}  CDaR {rows[-1]['CDaR_0.95']:>10,.0f}", flush=True)

met = pd.DataFrame(rows).set_index("arm")
cal = curves["control"].index

# ---------------------------------------------------------------- GATES
ctrl = curves["control"].to_numpy()
top10_idx = np.argsort(ctrl)[-10:]           # the 10 best CONTROL days
ctrl_top10 = ctrl[top10_idx].sum()

gates = []
for label in ("arm_FULL", "arm_HALF"):
    x = curves[label].reindex(cal).to_numpy()
    ret = float(x[top10_idx].sum() / ctrl_top10)
    g_sharpe = bool(met.loc[label, "sharpe"] > met.loc["control", "sharpe"])
    g_cdar = bool(met.loc[label, "CDaR_0.95"] < met.loc["control", "CDaR_0.95"])
    g_top10 = bool(ret >= 0.95)
    gates.append({
        "arm": label,
        "decision_cell": label == "arm_FULL",
        "sharpe": met.loc[label, "sharpe"], "sharpe_control": met.loc["control", "sharpe"],
        "d_sharpe": met.loc[label, "sharpe"] - met.loc["control", "sharpe"],
        "CDaR_0.95": met.loc[label, "CDaR_0.95"], "CDaR_control": met.loc["control", "CDaR_0.95"],
        "d_CDaR_pos_is_better": met.loc["control", "CDaR_0.95"] - met.loc[label, "CDaR_0.95"],
        "top10_retention": ret,
        "net": met.loc[label, "net"], "net_control": met.loc["control", "net"],
        "gate_sharpe": g_sharpe, "gate_CDaR": g_cdar, "gate_top10": g_top10,
        "AND_RULE_PASS": bool(g_sharpe and g_cdar and g_top10),
    })
gates = pd.DataFrame(gates)
gates.to_csv(os.path.join(C.OUT, "gates.csv"), index=False)
met.to_csv(os.path.join(C.OUT, "metrics.csv"))
print("\n=== GATES ===")
print(gates.to_string(index=False), flush=True)

# ---------------------------------------------------------------- CHURN (disclosure)
slot = C.slot_index(bars)
hh = pd.to_datetime(bars["time"]).dt.hour.to_numpy()
cohort = np.where(hh >= 18, "EVENING", np.where(hh < 9, "OVERNIGHT", "RTH"))
churn = []
for label in ARMS:
    F = flipcounts[label]
    tot = int((F != 0).sum())
    hold = float(np.abs(np.diff(tgts[label])).astype(bool).mean())
    row = {"arm": label, "member_flips_total": tot,
           "tgt_change_bars_pct": float((np.diff(tgts[label]) != 0).mean() * 100)}
    per_bar = (F != 0).sum(axis=1)
    for c in ("EVENING", "OVERNIGHT", "RTH"):
        row[f"flips_{c}"] = int(per_bar[cohort == c].sum())
    churn.append(row)
churn = pd.DataFrame(churn)
for c in ("EVENING", "OVERNIGHT", "RTH"):
    base = churn.loc[churn["arm"] == "control", f"flips_{c}"].iloc[0]
    churn[f"flips_{c}_vs_ctrl"] = churn[f"flips_{c}"] / base - 1.0
churn.to_csv(os.path.join(C.OUT, "churn.csv"), index=False)
print("\n=== CHURN ===")
print(churn.to_string(index=False), flush=True)

# ---------------------------------------------------------------- P&L BY COHORT per arm
pnl_rows = []
for label in ARMS:
    _, _, bp = C.e10_exec(bars, tgts[label])
    for c in ("EVENING", "OVERNIGHT", "RTH"):
        pnl_rows.append({"arm": label, "cohort": c, "net_pnl": float(bp[cohort == c].sum())})
pd.DataFrame(pnl_rows).pivot(index="arm", columns="cohort", values="net_pnl").to_csv(
    os.path.join(C.OUT, "pnl_by_cohort.csv"))

# ---------------------------------------------------------------- PORTFOLIO (disclosure)
port_rows, port_curves = [], {}
for label in ARMS:
    DUAL, PORT, SIG, Tpp = C.build_portfolio_6040(bars, tgts[label])
    port_curves[label] = PORT
    x = PORT.to_numpy()
    eq = np.cumsum(x); dd = np.maximum.accumulate(eq) - eq
    k = max(1, int(0.05 * len(x)))
    port_rows.append({"arm": label, "net": float(x.sum()),
                      "sharpe": float(x.mean() / x.std(ddof=1) * np.sqrt(252)),
                      "maxDD": float(dd.max()),
                      "CDaR_0.95": float(np.sort(dd)[::-1][:k].mean())})
port = pd.DataFrame(port_rows)
port.to_csv(os.path.join(C.OUT, "portfolio.csv"), index=False)
pd.DataFrame(port_curves).to_csv(os.path.join(C.OUT, "portfolio_curves.csv"))
print("\n=== PORTFOLIO DAYONLY_DUAL6040 (disclosure, not a gate) ===")
print(port.to_string(index=False), flush=True)

# ---------------------------------------------------------------- RECENCY TIERS
# V6 §3 mandatory disclosure, NOT selection. Every row is a CONTINUATION number (V7 §F).
tiers = {"full_dev": ("2022-01-03", "2026-05-29"),
         "trailing_2yr": ("2024-05-30", "2026-05-29"),
         "trailing_1yr": ("2025-05-30", "2026-05-29")}
tr = []
for label in ARMS:
    s = curves[label]
    for tname, (a, b) in tiers.items():
        x = s[(s.index >= a) & (s.index <= b)].to_numpy()
        eq = np.cumsum(x); dd = np.maximum.accumulate(eq) - eq
        k = max(1, int(0.05 * len(x)))
        tr.append({"arm": label, "tier": tname, "basis": "CONTINUATION (V7 §F)",
                   "n_days": len(x), "net": float(x.sum()),
                   "sharpe": float(x.mean() / x.std(ddof=1) * np.sqrt(252)),
                   "CDaR_0.95": float(np.sort(dd)[::-1][:k].mean())})
pd.DataFrame(tr).to_csv(os.path.join(C.OUT, "recency_tiers.csv"), index=False)
print("\n=== RECENCY TIERS (disclosure, not selection; all CONTINUATION numbers) ===")
print(pd.DataFrame(tr).to_string(index=False), flush=True)

verdict = {
    "decision_cell": "arm_FULL",
    "AND_RULE_PASS": bool(gates.loc[gates.arm == "arm_FULL", "AND_RULE_PASS"].iloc[0]),
    "arm_HALF_pass_DISCLOSURE_ONLY": bool(gates.loc[gates.arm == "arm_HALF", "AND_RULE_PASS"].iloc[0]),
    "note": "arm_HALF cannot be promoted under any outcome (frozen spec §3).",
}
json.dump(verdict, open(os.path.join(C.OUT, "verdict.json"), "w"), indent=2)
print("\n=== VERDICT ===\n" + json.dumps(verdict, indent=2), flush=True)
