"""SMV2AD sub_415 -- ceiling sweep. 4 arms, existing 13-member VMS UNCHANGED, ONLY
smax_ticks varied: {1200 (incumbent control), 1600, 2000, 2400}; smin_ticks=40 fixed.
Re-simulate the full 13-member ensemble + E10 executor for each arm.

Report per arm: standalone net/Sharpe/maxDD/CDaR_0.95/top-10-day-sum/turnover;
vm30's %-bars-at-new-ceiling; portfolio blend (DAYONLY_DUAL6040 60/40 rebuild with
this Solar leg swapped in, B-MOM leg UNCHANGED, vol-matching scalars re-derived).

Verdict rule (frozen, mirrors SMV2R sub_383): CEILING-CANDIDATE iff arm improves BOTH
standalone Sharpe AND standalone CDaR_0.95 vs the 1200t control AND retains >=95% of
the control's top-10-day sum. No adoption this wave.
"""
import sys, os, json, time
import numpy as np, pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
from common import (ROOT, OUT, load_dev_bars, build_pend, e10_exec, metric_row,
                     INCUMBENT_VMS, build_portfolio_6040, champion_curve)
import sm01_solarsim as sm

t0 = time.time()
bars = load_dev_bars()
sig = np.load(os.path.join(OUT, "sigma460_dev.npy"))
close = bars["close"].to_numpy()

ARMS = [1200.0, 1600.0, 2000.0, 2400.0]
LO = 40 * sm.TICK

rows = []
dailies = {}
tgts = {}
vm30_ceiling_pct = {}
finite = np.isfinite(sig)

for smax in ARMS:
    label = f"smax_{int(smax)}t" + ("_control" if smax == 1200.0 else "")
    pend = build_pend(bars, sig, INCUMBENT_VMS, smax_ticks=smax, smin_ticks=40.0)
    tgt = sm.e10_target(pend)
    daily, bar_pos, bar_pnl = e10_exec(bars, tgt)
    dailies[smax] = daily
    tgts[smax] = tgt
    r = metric_row(label, daily, tgt)
    r["smax_ticks"] = smax
    # vm30's %-bars-at-new-ceiling: raw = 30*sigma (pts) >= smax_ticks*TICK
    hi_pts = smax * sm.TICK
    raw30 = 30.0 * sig
    at_hi = finite & (raw30 >= hi_pts)
    r["vm30_pct_bars_at_ceiling"] = float(at_hi.sum() / finite.sum() * 100)
    rows.append(r)
    print(label, f"net={r['net']:.0f} sharpe={r['sharpe']:.3f} CDaR={r['CDaR_0.95']:.0f} "
          f"vm30_ceiling%={r['vm30_pct_bars_at_ceiling']:.2f}", flush=True)

df = pd.DataFrame(rows)

# right-tail retention vs control (1200t), same convention as SMV2R sub_383 / SMV2T gate D
base = dailies[1200.0].set_index("sess")["net"]
top10 = base.nlargest(10)
ret = {}
for smax in ARMS:
    d = dailies[smax].set_index("sess")["net"]
    ret[smax] = float(d.reindex(top10.index).fillna(0).sum())
df["pnl_on_control_top10_days"] = df["smax_ticks"].map(ret)
df["retention_control_top10"] = df["pnl_on_control_top10_days"] / ret[1200.0]

ctrl = df[df.smax_ticks == 1200.0].iloc[0]
df["d_sharpe_vs_control"] = df["sharpe"] - ctrl["sharpe"]
df["d_CDaR_vs_control"] = ctrl["CDaR_0.95"] - df["CDaR_0.95"]  # + = challenger better (lower CDaR)
df["ceiling_candidate"] = (
    (df["sharpe"] > ctrl["sharpe"]) &
    (df["CDaR_0.95"] < ctrl["CDaR_0.95"]) &
    (df["retention_control_top10"] >= 0.95) &
    (df["smax_ticks"] != 1200.0)
)

df.to_csv(os.path.join(OUT, "ceiling_sweep.csv"), index=False)
for smax, d in dailies.items():
    d.to_csv(os.path.join(OUT, f"daily_ceiling_{int(smax)}.csv"), index=False)
print(df.to_string(index=False), flush=True)

# ---------------- portfolio blend per arm ----------------
port_rows = []
port_curves = {"sess": None}
champ = None
for smax in ARMS:
    label = f"smax_{int(smax)}t"
    DUAL, portfolio, SIG, Tpp = build_portfolio_6040(bars, tgts[smax], label)
    cal = DUAL.index
    if champ is None:
        champ = champion_curve(cal)
        port_curves["sess"] = cal
    from common import dd_battery
    b_port = dd_battery(cal, portfolio.values, label=f"PORT_{label}")
    b_champ = dd_battery(cal, champ.values, label="PORT_INCUMBENT_CHAMPION")
    d_sharpe = b_port["sharpe"] - b_champ["sharpe"]
    d_cdar = b_champ["CDaR5"] - b_port["CDaR5"]
    port_rows.append({
        "arm": label, "smax_ticks": smax,
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

pdf = pd.DataFrame(port_rows)
pdf.to_csv(os.path.join(OUT, "portfolio_blend_415.csv"), index=False)
pd.DataFrame(port_curves).to_csv(os.path.join(OUT, "portfolio_curves_415.csv"), index=False)
print(pdf.to_string(index=False), flush=True)

candidates = df[df.ceiling_candidate]["smax_ticks"].tolist()
json.dump({
    "arms": ARMS, "candidates_smax_ticks": candidates,
    "any_candidate": bool(len(candidates) > 0),
    "runtime_s": round(time.time() - t0, 1),
}, open(os.path.join(OUT, "sub415_verdict.json"), "w"), indent=2)
print("\nsub_415 CEILING-CANDIDATEs:", candidates, flush=True)
print("done sub_415", round(time.time() - t0, 1), "s", flush=True)
