"""SMV2AD sub_416 -- extended cohort. Uses whichever smax_ticks from sub_415 is a
CEILING-CANDIDATE; sub_415 produced ZERO candidates (every raised-ceiling arm improved
Sharpe but WORSENED CDaR_0.95 vs the 1200t control -- see sub415_verdict.json), so per
spec this sub-test uses 2000t as a disclosed reasonable default (HYPOTHESIS flagged:
2000t chosen as the mid-sweep value from sub_415, not re-optimized here; applied to
BOTH arms' full member set including the incumbent 6-30 members, so the extended-cohort
test is not confounded by the un-relieved 1200t ceiling on the fast/mid members either).

arm_ADD: 18 members = incumbent 13 (VMS 6..30) + 5 NEW slower members {34,38,42,46,50}.
arm_REPLACE: 13 members = drop 5 FASTEST (6,8,10,12,14) + add {34,38,42,46,50}.

Both arms vs the 1200t/13-member control (TRUE incumbent, not a sub_415 rebuild).
Verdict rule: identical to sub_415 (Sharpe AND CDaR improve, top-10-day retention
>=95%) -> EXTENSION-CANDIDATE -> R2_CONFIRMATION later. No adoption this wave.
"""
import sys, os, json, time
import numpy as np, pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
from common import (ROOT, OUT, load_dev_bars, build_pend, e10_exec, metric_row,
                     INCUMBENT_VMS, build_portfolio_6040, champion_curve, dd_battery)
import sm01_solarsim as sm

t0 = time.time()
bars = load_dev_bars()
sig = np.load(os.path.join(OUT, "sigma460_dev.npy"))

sub415_verdict = json.load(open(os.path.join(OUT, "sub415_verdict.json")))
candidates = sub415_verdict["candidates_smax_ticks"]
if candidates:
    SMAX_USE = float(candidates[0])
    smax_flag = f"sub_415 CEILING-CANDIDATE {SMAX_USE}t used"
else:
    SMAX_USE = 2000.0
    smax_flag = ("HYPOTHESIS: sub_415 produced ZERO CEILING-CANDIDATEs; using 2000t as "
                 "the disclosed reasonable default per spec instruction (not re-optimized).")
print(smax_flag, flush=True)

NEW_SLOW = [34, 38, 42, 46, 50]
FAST5 = [6, 8, 10, 12, 14]
VMS_ADD = INCUMBENT_VMS + NEW_SLOW                                  # 18 members
VMS_REPLACE = [v for v in INCUMBENT_VMS if v not in FAST5] + NEW_SLOW  # 13 members

ARMS = {"arm_ADD": VMS_ADD, "arm_REPLACE": VMS_REPLACE}

# ---------------- control: TRUE incumbent (1200t / 13-member), reload from step0 cache ----------------
cache_ctrl = np.load(os.path.join(OUT, "cache_control_1200.npz"))
tgt_control = cache_ctrl["tgt"]
daily_control, _, _ = e10_exec(bars, tgt_control)
r_control = metric_row("1200t_13member_control", daily_control, tgt_control)

rows = [dict(r_control, smax_ticks=1200.0, n_members=13, members="incumbent VMS 6..30")]
dailies = {"control": daily_control}
tgts = {"control": tgt_control}

for arm, vms in ARMS.items():
    pend = build_pend(bars, sig, vms, smax_ticks=SMAX_USE, smin_ticks=40.0)
    tgt = sm.e10_target(pend)
    daily, bar_pos, bar_pnl = e10_exec(bars, tgt)
    dailies[arm] = daily
    tgts[arm] = tgt
    r = metric_row(arm, daily, tgt)
    r["smax_ticks"] = SMAX_USE
    r["n_members"] = len(vms)
    r["members"] = "/".join(map(str, vms))
    rows.append(r)
    print(arm, f"n_members={len(vms)} smax={SMAX_USE} net={r['net']:.0f} sharpe={r['sharpe']:.3f} "
          f"CDaR={r['CDaR_0.95']:.0f}", flush=True)

df = pd.DataFrame(rows)

base = dailies["control"].set_index("sess")["net"]
top10 = base.nlargest(10)
ret = {}
for k, d in dailies.items():
    dd_ = d.set_index("sess")["net"]
    ret[k] = float(dd_.reindex(top10.index).fillna(0).sum())
df["pnl_on_control_top10_days"] = df["arm"].map(ret)
df["retention_control_top10"] = df["pnl_on_control_top10_days"] / ret["control" if "control" in ret else "1200t_13member_control"]
# fix label mapping (arm col uses metric_row label, control row uses same string)
df.loc[df["arm"] == "1200t_13member_control", "retention_control_top10"] = 1.0

ctrl_row = df[df.arm == "1200t_13member_control"].iloc[0]
df["d_sharpe_vs_control"] = df["sharpe"] - ctrl_row["sharpe"]
df["d_CDaR_vs_control"] = ctrl_row["CDaR_0.95"] - df["CDaR_0.95"]
df["extension_candidate"] = (
    (df["sharpe"] > ctrl_row["sharpe"]) &
    (df["CDaR_0.95"] < ctrl_row["CDaR_0.95"]) &
    (df["retention_control_top10"] >= 0.95) &
    (df["arm"] != "1200t_13member_control")
)
df["smax_ticks_used_note"] = smax_flag

df.to_csv(os.path.join(OUT, "extended_cohort.csv"), index=False)
for k, d in dailies.items():
    if k != "control":
        d.to_csv(os.path.join(OUT, f"daily_cohort_{k}.csv"), index=False)
print(df.to_string(index=False), flush=True)

# ---------------- portfolio blend per arm ----------------
port_rows = []
port_curves = {}
champ = None
for arm in ARMS:
    DUAL, portfolio, SIG, Tpp = build_portfolio_6040(bars, tgts[arm], arm)
    cal = DUAL.index
    if champ is None:
        champ = champion_curve(cal)
        port_curves["sess"] = cal
    b_port = dd_battery(cal, portfolio.values, label=f"PORT_{arm}")
    b_champ = dd_battery(cal, champ.values, label="PORT_INCUMBENT_CHAMPION")
    d_sharpe = b_port["sharpe"] - b_champ["sharpe"]
    d_cdar = b_champ["CDaR5"] - b_port["CDaR5"]
    port_rows.append({
        "arm": arm, "smax_ticks": SMAX_USE, "n_members": len(ARMS[arm]),
        "SIG_DUAL_leg_std": SIG,
        "net_portfolio_6040": b_port["net"], "sharpe_portfolio_6040": b_port["sharpe"],
        "CDaR5_portfolio_6040": b_port["CDaR5"], "maxDD_portfolio_6040": b_port["maxDD_eod"],
        "net_champion_6040": b_champ["net"], "sharpe_champion_6040": b_champ["sharpe"],
        "CDaR5_champion_6040": b_champ["CDaR5"], "maxDD_champion_6040": b_champ["maxDD_eod"],
        "d_sharpe_vs_champion": d_sharpe, "d_CDaR_vs_champion": d_cdar,
        "portfolio_beats_champion": bool(d_sharpe > 0 and d_cdar > 0),
    })
    port_curves[f"DUAL_{arm}"] = DUAL.values
    port_curves[f"PORT_{arm}"] = portfolio.values
    print(f"portfolio {arm}: SIG={SIG:.1f} net={b_port['net']:.0f} sharpe={b_port['sharpe']:.3f} "
          f"vs champion sharpe={b_champ['sharpe']:.3f}", flush=True)

pdf = pd.DataFrame(port_rows)
pdf.to_csv(os.path.join(OUT, "portfolio_blend_416.csv"), index=False)
pd.DataFrame(port_curves).to_csv(os.path.join(OUT, "portfolio_curves_416.csv"), index=False)
print(pdf.to_string(index=False), flush=True)

ext_candidates = df[df.get("extension_candidate", False) == True]["arm"].tolist()
json.dump({
    "smax_ticks_used": SMAX_USE, "smax_flag": smax_flag,
    "arms": list(ARMS.keys()), "candidates": ext_candidates,
    "any_candidate": bool(len(ext_candidates) > 0),
    "runtime_s": round(time.time() - t0, 1),
}, open(os.path.join(OUT, "sub416_verdict.json"), "w"), indent=2)
print("\nsub_416 EXTENSION-CANDIDATEs:", ext_candidates, flush=True)
print("done sub_416", round(time.time() - t0, 1), "s", flush=True)
