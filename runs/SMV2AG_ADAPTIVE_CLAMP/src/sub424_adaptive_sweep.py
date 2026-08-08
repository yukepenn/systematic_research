"""SMV2AG sub_424 -- adaptive-ceiling sweep. 6 arms, 2x3 grid: percentile P in
{90,95,99} x window N in {460,920} (bars), existing 13-member VMS UNCHANGED,
smin_ticks=40 fixed. Control = incumbent fixed 1200t, REUSED VERBATIM from
runs/SMV2AD_VOLMULT_CEILING/out/e10_daily_dev_control_1200.csv +
out/cache_control_1200.npz (NOT re-simulated), per spec instruction.

Report per arm: standalone net/Sharpe/maxDD/CDaR_0.95/top-10-day-sum/turnover;
effective ceiling distribution actually realized (median/p90/p99 of ceil_m(t) for
vm30, over dev and by year); %-bars where the adaptive ceiling differs from the
fixed 1200t incumbent ceiling; portfolio blend (DAYONLY_DUAL6040 60/40).

Verdict rule (frozen, SAME AND-rule as SMV2AD, no loosening): an arm is an
ADAPTIVE-CEILING-CANDIDATE only if it improves BOTH standalone Sharpe AND
standalone CDaR_0.95 vs the 1200t control AND retains >=95% of the control's
top-10-day sum. No adoption this wave.
"""
import sys, os, json, time
import numpy as np, pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
from common import (ROOT, OUT, SMV2AD_OUT, load_dev_bars, e10_exec, metric_row,
                     INCUMBENT_VMS, build_portfolio_6040, champion_curve, dd_battery,
                     CEILING_FLOOR_PTS)
import sm01_solarsim as sm
import adaptive as ad

t0 = time.time()
bars = load_dev_bars()
n = len(bars)

# ---- sigma460: verbatim reuse of SMV2AD's cached dev-window sigma (pure function
# of price data alone; unaffected by the ceiling mechanism; identical dev window
# 2022-01-03 -> 2026-05-29) ----
sig = np.load(os.path.join(SMV2AD_OUT, "sigma460_dev.npy"))
assert len(sig) == n, f"sigma length {len(sig)} != bars {n} -- dev-window mismatch, BLOCKED"

# ---- integrity check: adaptive machinery with a constant hi_arr=300.0 must
# reproduce the fixed-1200t control bit-for-bit (verifies member_states_adaptive
# is a true no-op superset of member_states when the ceiling never widens) ----
close = bars["close"].to_numpy()
hi_const = np.full(n, CEILING_FLOOR_PTS)
vm_check = 30.0
is_up_a, flip_a, s_eff_a, anchor_a = ad.member_states_adaptive(close, sig, vm_check, hi_const, smin_ticks=40.0)
is_up_f, flip_f, s_eff_f, anchor_f = sm.member_states(close, sig, vm_check, smin_ticks=40.0, smax_ticks=1200.0)
integrity_ok = (np.array_equal(is_up_a, is_up_f) and np.array_equal(flip_a, flip_f)
                and np.allclose(s_eff_a, s_eff_f) and np.allclose(anchor_a, anchor_f))
print("INTEGRITY CHECK (adaptive w/ const ceiling == fixed 1200t control, vm=30):", integrity_ok, flush=True)
assert integrity_ok, "adaptive member_states_adaptive FAILED to reproduce fixed control -- BLOCKED"

# ---- control: reused verbatim from SMV2AD (NOT re-simulated) ----
cache_ctrl = np.load(os.path.join(SMV2AD_OUT, "cache_control_1200.npz"))
tgt_control = cache_ctrl["tgt"]
daily_control_check, _, _ = e10_exec(bars, tgt_control)
daily_control_cached = pd.read_csv(os.path.join(SMV2AD_OUT, "e10_daily_dev_control_1200.csv"))
# cross-check re-execution of the cached control tgt against the cached daily curve
# (both derived from the same simulator; this just confirms e10_exec is unchanged)
# sess dtype: daily_control_check carries python date objects (from bars["sess_date"]),
# daily_control_cached carries strings (round-tripped through csv) -- normalize both
# to string before merging so the join actually matches rows.
dcc = daily_control_check.copy(); dcc["sess"] = dcc["sess"].astype(str)
dca = daily_control_cached.copy(); dca["sess"] = dca["sess"].astype(str)
mrg = dcc.merge(dca, on="sess", suffixes=("_reexec", "_cached"))
max_dev = float(np.abs(mrg["net_reexec"] - mrg["net_cached"]).max())
print(f"control re-exec vs SMV2AD cached daily curve, max|dev|=${max_dev:.4f} ({len(mrg)} sessions)", flush=True)
assert max_dev < 1e-6, "control re-exec mismatch vs SMV2AD cache -- BLOCKED"
daily_control = daily_control_cached
r_control = metric_row("control_1200t_fixed", daily_control, tgt_control)
r_control["P"] = np.nan; r_control["N"] = np.nan

sess_dates = bars["sess_date"].to_numpy()
years = np.array([d.year for d in sess_dates])  # per-bar year via session date

GRID = [(P, N) for P in (90, 95, 99) for N in (460, 920)]

rows = [dict(r_control)]
dailies = {"control": daily_control}
tgts = {"control": tgt_control}
eff_ceiling_rows = []
pct_differ_rows = []

for P, N in GRID:
    label = f"P{P}_N{N}"
    pend, ceil_by_member, rq = ad.build_pend_adaptive(bars, sig, INCUMBENT_VMS, N, float(P))
    tgt = sm.e10_target(pend)
    daily, bar_pos, bar_pnl = e10_exec(bars, tgt)
    dailies[label] = daily
    tgts[label] = tgt
    r = metric_row(label, daily, tgt)
    r["P"] = P; r["N"] = N
    rows.append(r)

    # ---- effective ceiling distribution diagnostic (vm30, the slowest member) ----
    ceil30 = ceil_by_member[30]
    warm_n = N + ad.MIN_COUNT
    post_warm = ceil30[warm_n:]
    yrs_post = years[warm_n:]
    eff_ceiling_rows.append({
        "arm": label, "P": P, "N": N, "member_vm30": 30,
        "n_bars_post_warmup": int(len(post_warm)),
        "median_ceil_pts": float(np.median(post_warm)),
        "p90_ceil_pts": float(np.percentile(post_warm, 90)),
        "p99_ceil_pts": float(np.percentile(post_warm, 99)),
        "max_ceil_pts": float(np.max(post_warm)),
        "median_ceil_ticks": float(np.median(post_warm) / sm.TICK),
        "p90_ceil_ticks": float(np.percentile(post_warm, 90) / sm.TICK),
        "p99_ceil_ticks": float(np.percentile(post_warm, 99) / sm.TICK),
    })
    for yr in sorted(set(yrs_post.tolist())):
        m = yrs_post == yr
        seg = post_warm[m]
        if len(seg) == 0:
            continue
        eff_ceiling_rows.append({
            "arm": label, "P": P, "N": N, "member_vm30": 30,
            "n_bars_post_warmup": int(len(seg)), "year": int(yr),
            "median_ceil_pts": float(np.median(seg)),
            "p90_ceil_pts": float(np.percentile(seg, 90)),
            "p99_ceil_pts": float(np.percentile(seg, 99)),
            "max_ceil_pts": float(np.max(seg)),
            "median_ceil_ticks": float(np.median(seg) / sm.TICK),
            "p90_ceil_ticks": float(np.percentile(seg, 90) / sm.TICK),
            "p99_ceil_ticks": float(np.percentile(seg, 99) / sm.TICK),
        })

    # ---- %-bars where the adaptive ceiling differs from the fixed 1200t control
    # (i.e. ceil_m(t) > 300.0, since it is floored at exactly 300.0 -- so "differs"
    # <=> "actually widened") -- reported for vm30 and pooled across all 13 members ----
    differs30 = (ceil30 > CEILING_FLOOR_PTS)
    pct_differ_vm30 = float(differs30.mean() * 100)
    pct_differ_vm30_post_warm = float(differs30[warm_n:].mean() * 100)
    all_differs = np.concatenate([(ceil_by_member[vm_] > CEILING_FLOOR_PTS) for vm_ in INCUMBENT_VMS])
    pct_differ_pooled = float(all_differs.mean() * 100)
    pct_differ_rows.append({
        "arm": label, "P": P, "N": N,
        "pct_bars_ceiling_differs_vm30_all": pct_differ_vm30,
        "pct_bars_ceiling_differs_vm30_post_warmup": pct_differ_vm30_post_warm,
        "pct_bars_ceiling_differs_pooled_13members_all": pct_differ_pooled,
    })

    print(f"{label}: net={r['net']:.0f} sharpe={r['sharpe']:.3f} CDaR={r['CDaR_0.95']:.0f} "
          f"vm30_pct_widened={pct_differ_vm30:.2f}%", flush=True)

df = pd.DataFrame(rows)

# right-tail retention vs control, same convention as SMV2AD. sess dtype: the
# control daily curve (loaded from csv) carries string sess dates; the challenger
# arms' daily curves (freshly computed by e10_exec off bars["sess_date"]) carry
# python date objects -- normalize both to string before the top10-day reindex,
# otherwise every challenger silently reindexes to all-NaN/0 (dtype mismatch bug
# caught and fixed here, verified below via non-zero retention values).
base = dailies["control"].copy(); base["sess"] = base["sess"].astype(str)
base = base.set_index("sess")["net"]
top10 = base.nlargest(10)
ret = {}
for k, d in dailies.items():
    dd_ = d.copy(); dd_["sess"] = dd_["sess"].astype(str)
    dd_ = dd_.set_index("sess")["net"]
    ret[k] = float(dd_.reindex(top10.index).fillna(0).sum())
ret["control_1200t_fixed"] = ret.pop("control")
df["pnl_on_control_top10_days"] = df["arm"].map(ret)
df["retention_control_top10"] = df["pnl_on_control_top10_days"] / ret["control_1200t_fixed"]

ctrl_row = df[df.arm == "control_1200t_fixed"].iloc[0]
df["d_sharpe_vs_control"] = df["sharpe"] - ctrl_row["sharpe"]
df["d_CDaR_vs_control"] = ctrl_row["CDaR_0.95"] - df["CDaR_0.95"]  # + = challenger better (lower CDaR)
df["adaptive_ceiling_candidate"] = (
    (df["sharpe"] > ctrl_row["sharpe"]) &
    (df["CDaR_0.95"] < ctrl_row["CDaR_0.95"]) &
    (df["retention_control_top10"] >= 0.95) &
    (df["arm"] != "control_1200t_fixed")
)

df.to_csv(os.path.join(OUT, "adaptive_sweep.csv"), index=False)
for k, d in dailies.items():
    if k != "control":
        d.to_csv(os.path.join(OUT, f"daily_adaptive_{k}.csv"), index=False)
print(df.to_string(index=False), flush=True)

eff_df = pd.DataFrame(eff_ceiling_rows)
eff_df.to_csv(os.path.join(OUT, "effective_ceiling_distribution.csv"), index=False)
print(eff_df.to_string(index=False), flush=True)

pct_df = pd.DataFrame(pct_differ_rows)
pct_df.to_csv(os.path.join(OUT, "pct_bars_ceiling_differs.csv"), index=False)
print(pct_df.to_string(index=False), flush=True)

# ---------------- portfolio blend per arm ----------------
port_rows = []
port_curves = {"sess": None}
champ = None
for P, N in GRID:
    label = f"P{P}_N{N}"
    DUAL, portfolio, SIG, Tpp = build_portfolio_6040(bars, tgts[label], label)
    cal = DUAL.index
    if champ is None:
        champ = champion_curve(cal)
        port_curves["sess"] = cal
    b_port = dd_battery(cal, portfolio.values, label=f"PORT_{label}")
    b_champ = dd_battery(cal, champ.values, label="PORT_INCUMBENT_CHAMPION")
    d_sharpe = b_port["sharpe"] - b_champ["sharpe"]
    d_cdar = b_champ["CDaR5"] - b_port["CDaR5"]
    port_rows.append({
        "arm": label, "P": P, "N": N,
        "SIG_DUAL_leg_std": SIG,
        "net_portfolio_6040": b_port["net"], "sharpe_portfolio_6040": b_port["sharpe"],
        "CDaR5_portfolio_6040": b_port["CDaR5"], "maxDD_portfolio_6040": b_port["maxDD_eod"],
        "net_champion_6040": b_champ["net"], "sharpe_champion_6040": b_champ["sharpe"],
        "CDaR5_champion_6040": b_champ["CDaR5"], "maxDD_champion_6040": b_champ["maxDD_eod"],
        "d_sharpe_vs_champion": d_sharpe, "d_CDaR_vs_champion": d_cdar,
        "portfolio_beats_champion": bool(d_sharpe > 0 and d_cdar > 0),
    })
    port_curves[f"DUAL_{label}"] = DUAL.values
    port_curves[f"PORT_{label}"] = portfolio.values
    print(f"portfolio {label}: SIG={SIG:.1f} net={b_port['net']:.0f} sharpe={b_port['sharpe']:.3f} "
          f"vs champion sharpe={b_champ['sharpe']:.3f}", flush=True)

# also blend the control for reference (not a spec-required arm, but useful context
# in the report to show what "no adaptive ceiling" looks like in the same blend)
DUAL_c, portfolio_c, SIG_c, Tpp_c = build_portfolio_6040(bars, tgt_control, "control_1200t_fixed")
b_port_c = dd_battery(DUAL_c.index, portfolio_c.values, label="PORT_control")
b_champ_c = dd_battery(DUAL_c.index, champ.reindex(DUAL_c.index).values, label="PORT_INCUMBENT_CHAMPION")
port_rows.append({
    "arm": "control_1200t_fixed", "P": np.nan, "N": np.nan,
    "SIG_DUAL_leg_std": SIG_c,
    "net_portfolio_6040": b_port_c["net"], "sharpe_portfolio_6040": b_port_c["sharpe"],
    "CDaR5_portfolio_6040": b_port_c["CDaR5"], "maxDD_portfolio_6040": b_port_c["maxDD_eod"],
    "net_champion_6040": b_champ_c["net"], "sharpe_champion_6040": b_champ_c["sharpe"],
    "CDaR5_champion_6040": b_champ_c["CDaR5"], "maxDD_champion_6040": b_champ_c["maxDD_eod"],
    "d_sharpe_vs_champion": b_port_c["sharpe"] - b_champ_c["sharpe"],
    "d_CDaR_vs_champion": b_champ_c["CDaR5"] - b_port_c["CDaR5"],
    "portfolio_beats_champion": bool((b_port_c["sharpe"] - b_champ_c["sharpe"]) > 0 and
                                      (b_champ_c["CDaR5"] - b_port_c["CDaR5"]) > 0),
})
port_curves["DUAL_control_1200t_fixed"] = DUAL_c.reindex(port_curves["sess"]).values
port_curves["PORT_control_1200t_fixed"] = portfolio_c.reindex(port_curves["sess"]).values

pdf = pd.DataFrame(port_rows)
pdf.to_csv(os.path.join(OUT, "portfolio_blend_424.csv"), index=False)
pd.DataFrame(port_curves).to_csv(os.path.join(OUT, "portfolio_curves_424.csv"), index=False)
print(pdf.to_string(index=False), flush=True)

candidates = df[df.adaptive_ceiling_candidate][["P", "N", "arm"]].to_dict("records")
json.dump({
    "grid": [{"P": P, "N": N} for P, N in GRID],
    "candidates": candidates,
    "candidate_arms": [c["arm"] for c in candidates],
    "any_candidate": bool(len(candidates) > 0),
    "runtime_s": round(time.time() - t0, 1),
}, open(os.path.join(OUT, "sub424_verdict.json"), "w"), indent=2)
print("\nsub_424 ADAPTIVE-CEILING-CANDIDATEs:", candidates, flush=True)
print("done sub_424", round(time.time() - t0, 1), "s", flush=True)
