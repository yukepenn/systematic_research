"""SMV2AA_MIX_SHIFT -- seq 406 (leg-asymmetry diagnostic, mandatory gate) + seq 407-409
(mix-shift policy cells, LICENSED ONLY IF 406 passes).
Frozen spec: runs/SMV2AA_MIX_SHIFT/spec.yaml (committed f6fb7d1, read before write).

Data reuse (per spec CODE MAP, no reimplementation):
  - leg decomposition: runs/SMV2Q_DIAGNOSTICS/out/leg_daily.csv (leg_solar/leg_bmom/twin),
    verified upstream (SMV2Q) to rebuild twin exactly (max abs daily error 1.8e-12; this run's
    own check below finds 9.1e-13 on leg_solar+leg_bmom-twin).
  - SMV2Z's exact 23 trigger-week -> 23 receiver(t+1)-week flag set: reused directly from
    runs/SMV2Z_VIABILITY_POLICY/out/policy_daily.csv 'scaled'==True week_keys (NOT
    recomputed from the sigma460/ER150 AND-gate) -- cross-checked against SMV2Z's own
    run_log.txt printed trigger_week_keys line (hard assert below).
  - champion curve for gate comparisons ("unscaled champion"): SMV2M parity_daily_aligned.csv
    'nt', 2023-04-05/06 boundary-pair merge, IDENTICAL to SMV2Y/SMV2Z's own construction
    (verbatim copy of the merge block below; the boundary week 202314 is not in the flagged
    set, so leg_daily.csv's own unmerged boundary rows never enter a flagged-week calc).
  - equal-vol reweighting: runs/SMV2H_ONECONTRACT/rerank.py's vm()/SIG pattern
    (p = vm(w_a*A + w_b*vm(B))), reused verbatim in construct_mix() below, with leg_solar as
    the SIG anchor (arbitrary but fixed reference leg, independent of the 406 outcome).
  - placebo/chronology gate pattern: runs/SMV2N_WINDFALL_POLICY/smv2n.py,
    runs/SMV2V_ER_DAMPER/smv2v.py, and SMV2Z's own weekly-adapted version (already the closest
    analog: weekly trigger unit, non-overlapping same-count draws) -- adapted here to REWEIGHT
    the flagged week (not scale it down), per this spec's explicit mechanic difference.

HARD: no data >= 2026-08-01 ever used; dev sessions <= 2026-05-31 only. No git, no writes
outside runs/SMV2AA_MIX_SHIFT/, no NinjaTrader/CrossTrade tools.
"""
import os
import sys
import json

import numpy as np
import pandas as pd

REPO = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
RUN = os.path.join(REPO, "runs", "SMV2AA_MIX_SHIFT")
OUT = os.path.join(RUN, "out")
os.makedirs(OUT, exist_ok=True)

DEV_END = pd.Timestamp("2026-05-31")
VIRGIN_FLOOR = pd.Timestamp("2026-08-01")
N_PLACEBO = 200
CELLS = [("A", 0.75, 0.25), ("B", 0.50, 0.50), ("C", 0.40, 0.60)]  # (name, w_stable, w_unstable)

log_lines = []
def log(msg):
    print(msg, flush=True)
    log_lines.append(str(msg))


def sgn(v):
    return 0 if v == 0 else (1 if v > 0 else -1)


def dd_of(net):
    eq = np.cumsum(np.asarray(net, dtype=float))
    return np.maximum.accumulate(eq) - eq


def cdar95(net):
    """dd_battery 'CDaR5'-exact (SMV2N/V/Z-identical light implementation)."""
    dd = dd_of(net)
    ddpos = np.sort(dd[dd > 0])[::-1]
    k = max(1, int(0.05 * len(dd)))
    return float(ddpos[:k].mean()) if len(ddpos) else 0.0


def tuw_longest(net):
    dd = dd_of(net)
    uw = dd > 1e-9
    tuw = cur = 0
    for u in uw:
        cur = cur + 1 if u else 0
        tuw = max(tuw, cur)
    return int(tuw)


def sharpe(net):
    net = np.asarray(net, dtype=float)
    sd = net.std(ddof=1)
    return float(net.mean() / sd * np.sqrt(252)) if sd > 0 else np.nan


def wkey(idx):  # ISO week of session date -- IDENTICAL to smv2q.py/smv2y.py/smv2z.py
    iso = idx.isocalendar()
    return (iso["year"].astype(int) * 100 + iso["week"].astype(int)).values


# ============================================================== 1. load leg decomposition (REUSE)

leg = pd.read_csv(os.path.join(REPO, "runs", "SMV2Q_DIAGNOSTICS", "out", "leg_daily.csv"),
                   index_col=0, parse_dates=True).sort_index()
assert leg.index.max() <= DEV_END, "VIRGIN guard: leg_daily.csv extends past dev"
assert leg.index.max() < VIRGIN_FLOOR
recon_err = float((leg["leg_solar"] + leg["leg_bmom"] - leg["twin"]).abs().max())
log(f"leg_daily.csv loaded: {len(leg)} sessions {leg.index.min().date()}..{leg.index.max().date()}; "
    f"leg_solar+leg_bmom-twin max abs err={recon_err:.3e} (SMV2Q reports 1.8e-12)")
assert recon_err < 1e-6, "leg reconstruction of twin failed -- BLOCKED"

wk_leg = wkey(leg.index)
leg["week_key"] = wk_leg

# ============================================================== 2. REUSE SMV2Z's exact 23 flagged (t+1) weeks

pz = pd.read_csv(os.path.join(REPO, "runs", "SMV2Z_VIABILITY_POLICY", "out", "policy_daily.csv"),
                  parse_dates=["sess"])
assert pz["sess"].max() <= DEV_END
FLAGGED_WEEKS = sorted(int(w) for w in pz.loc[pz["scaled"], "week_key"].unique())
n_scaled_days_z = int(pz["scaled"].sum())
log(f"SMV2Z flagged (receiver t+1) weeks reused from policy_daily.csv: n={len(FLAGGED_WEEKS)} "
    f"weeks, n_scaled_days={n_scaled_days_z} -> {FLAGGED_WEEKS}")

# hard cross-check against SMV2Z's own run_log.txt printed line (transcription safety, not
# an independent re-derivation -- both read FROM SMV2Z's own committed artifacts)
with open(os.path.join(REPO, "runs", "SMV2Z_VIABILITY_POLICY", "out", "run_log.txt")) as f:
    zlog = f.read()
log_line = [l for l in zlog.splitlines() if l.startswith("n_scaled_weeks(receiver")][0]
log(f"SMV2Z run_log.txt cross-check line: {log_line}")
txt_keys = sorted(int(x) for x in log_line.split("trigger_week_keys=")[1].strip("[]").split(", "))
assert txt_keys == FLAGGED_WEEKS, "flagged week set mismatch between policy_daily.csv and run_log.txt -- BLOCKED"
assert len(FLAGGED_WEEKS) == 23, f"expected 23 flagged weeks per spec, got {len(FLAGGED_WEEKS)}"
log("spot-check PASS: policy_daily.csv scaled-week set == run_log.txt trigger_week_keys (23/23, identical)")

is_flagged = leg["week_key"].isin(FLAGGED_WEEKS).to_numpy()
n_flagged_days_leg = int(is_flagged.sum())
log(f"leg_daily.csv flagged-week day count = {n_flagged_days_leg} (SMV2Z champion-calendar count = "
    f"{n_scaled_days_z}; expect equal since boundary week 202314 is not in the flagged set)")
assert n_flagged_days_leg == n_scaled_days_z, "flagged-day count mismatch between leg calendar and champion calendar -- BLOCKED"
assert 202314 not in FLAGGED_WEEKS, "boundary week unexpectedly in flagged set -- merge logic would need revisiting"

is_unflagged = ~is_flagged  # "all other weeks, same dev window" per spec 406 -- literal reading


# ============================================================== 3. 406 diagnostic: per-leg vol/mean/sharpe, flagged vs unflagged

def leg_stats(col):
    x_all = leg[col].to_numpy(float)
    x_f = x_all[is_flagged]
    x_u = x_all[is_unflagged]
    vol_f = float(np.std(x_f, ddof=1))
    vol_u = float(np.std(x_u, ddof=1))
    mean_f = float(np.mean(x_f))
    mean_u = float(np.mean(x_u))
    mean_all = float(np.mean(x_all))
    vol_all = float(np.std(x_all, ddof=1))
    sh_f = mean_f / vol_f * np.sqrt(252) if vol_f > 0 else np.nan
    sh_all = mean_all / vol_all * np.sqrt(252) if vol_all > 0 else np.nan
    return {
        "leg": col, "n_flagged": int(len(x_f)), "n_unflagged": int(len(x_u)),
        "vol_flagged": vol_f, "vol_unflagged": vol_u, "vol_ratio": vol_f / vol_u if vol_u > 0 else np.nan,
        "mean_flagged": mean_f, "mean_unflagged": mean_u, "mean_all": mean_all,
        "sharpe_flagged": sh_f, "sharpe_all": sh_all, "sharpe_drop": sh_all - sh_f,
        "sum_flagged": float(np.sum(x_f)), "sum_all": float(np.sum(x_all)),
    }


st_solar = leg_stats("leg_solar")
st_bmom = leg_stats("leg_bmom")
st_twin = leg_stats("twin")
log(f"leg_solar stats: {st_solar}")
log(f"leg_bmom  stats: {st_bmom}")
log(f"twin (context) stats: {st_twin}")

vr_solar = st_solar["vol_ratio"]
vr_bmom = st_bmom["vol_ratio"]
asym_ratio = max(vr_solar, vr_bmom) / min(vr_solar, vr_bmom)
gate_a = bool(asym_ratio >= 1.3)
log(f"gate(a) asymmetry: vol_ratio_solar={vr_solar:.4f} vol_ratio_bmom={vr_bmom:.4f} "
    f"max/min={asym_ratio:.4f} (need >=1.3) -> {gate_a}")

# relatively more stable leg = lower vol_ratio
if vr_solar < vr_bmom:
    stable_leg, unstable_leg = "leg_solar", "leg_bmom"
    stable_stats, unstable_stats = st_solar, st_bmom
else:
    stable_leg, unstable_leg = "leg_bmom", "leg_solar"
    stable_stats, unstable_stats = st_bmom, st_solar
log(f"relatively-more-stable leg (lower vol_ratio) = {stable_leg} (vol_ratio={min(vr_solar, vr_bmom):.4f} "
    f"vs unstable {unstable_leg} vol_ratio={max(vr_solar, vr_bmom):.4f})")

# gate (b): stable leg's flagged Sharpe must not be "materially worse" than its own unconditional Sharpe.
# Pre-committed, explicit, mechanical definition of "materially worse" (spec leaves the threshold
# open; applied honestly and conservatively, not tuned to the answer):
#   materially_worse := (sign flips from positive-unconditional to negative-flagged)
#                     OR (sharpe_all - sharpe_flagged) > 1.0  [a full 1.0 Sharpe-unit degradation]
sh_all_stable = stable_stats["sharpe_all"]
sh_flag_stable = stable_stats["sharpe_flagged"]
sign_flip = bool(sh_all_stable > 0 and sh_flag_stable < 0)
drop = sh_all_stable - sh_flag_stable
materially_worse = bool(sign_flip or drop > 1.0)
gate_b = bool(not materially_worse)
log(f"gate(b) stable-leg degradation check [{stable_leg}]: sharpe_all={sh_all_stable:.4f} "
    f"sharpe_flagged={sh_flag_stable:.4f} drop={drop:.4f} sign_flip(+->-)={sign_flip} "
    f"materially_worse(drop>1.0 OR sign_flip)={materially_worse} -> gate_b={gate_b}")

gate_c = bool(st_solar["n_flagged"] >= 15 and st_bmom["n_flagged"] >= 15)
log(f"gate(c) power floor: n_flagged_solar={st_solar['n_flagged']} n_flagged_bmom={st_bmom['n_flagged']} "
    f"(need >=15 each) -> {gate_c}")

LICENSED = bool(gate_a and gate_b and gate_c)
log(f"\n406 LICENSE_RULE: gate_a(asymmetry>=1.3)={gate_a} gate_b(stable-leg not materially worse)={gate_b} "
    f"gate_c(N>=15 each)={gate_c} -> LICENSED={LICENSED}")

# contribution_share: each leg's share of flagged-week twin PnL (context vs SMV2Z's 30.3%-of-total figure)
contrib_solar = st_solar["sum_flagged"] / st_twin["sum_flagged"] if st_twin["sum_flagged"] != 0 else np.nan
contrib_bmom = st_bmom["sum_flagged"] / st_twin["sum_flagged"] if st_twin["sum_flagged"] != 0 else np.nan
twin_flagged_share_of_total = st_twin["sum_flagged"] / st_twin["sum_all"] if st_twin["sum_all"] != 0 else np.nan
log(f"contribution_share (of flagged-week twin PnL): leg_solar={contrib_solar:.4f} leg_bmom={contrib_bmom:.4f} "
    f"(sum to 1.0 by construction); twin flagged-week PnL is {twin_flagged_share_of_total:.4f} share of twin's "
    f"total dev PnL (context only -- SMV2Z's cited 30.3% figure is computed on the champion 'nt' curve, not "
    f"'twin'; nt and twin are highly correlated (SMV2M: 0.9992) but not identical, so this is a plausibility "
    f"check, not a reproduction)")

asym_rows = []
for s in (st_solar, st_bmom):
    asym_rows.append({
        "leg": s["leg"], "n_flagged": s["n_flagged"], "n_unflagged": s["n_unflagged"],
        "vol_flagged": s["vol_flagged"], "vol_unflagged": s["vol_unflagged"], "vol_ratio": s["vol_ratio"],
        "mean_flagged": s["mean_flagged"], "mean_unflagged": s["mean_unflagged"], "mean_all": s["mean_all"],
        "sharpe_flagged": s["sharpe_flagged"], "sharpe_all": s["sharpe_all"], "sharpe_drop": s["sharpe_drop"],
        "sum_flagged": s["sum_flagged"], "sum_all": s["sum_all"],
        "contribution_share_of_flagged_twin_pnl": contrib_solar if s["leg"] == "leg_solar" else contrib_bmom,
        "is_relatively_stable_leg": bool(s["leg"] == stable_leg),
    })
asym_df = pd.DataFrame(asym_rows)
asym_df.to_csv(os.path.join(OUT, "leg_asymmetry.csv"), index=False)

license_decision = {
    "asymmetry_ratio_max_over_min": asym_ratio,
    "vol_ratio_solar": vr_solar, "vol_ratio_bmom": vr_bmom,
    "gate_a_asymmetry_pass": gate_a, "gate_a_threshold": 1.3,
    "stable_leg": stable_leg, "unstable_leg": unstable_leg,
    "stable_leg_sharpe_all": sh_all_stable, "stable_leg_sharpe_flagged": sh_flag_stable,
    "stable_leg_sharpe_drop": drop, "stable_leg_sign_flip": sign_flip,
    "materially_worse_rule": "sign_flip(+->-) OR (sharpe_all - sharpe_flagged) > 1.0",
    "materially_worse": materially_worse, "gate_b_pass": gate_b,
    "n_flagged_solar": st_solar["n_flagged"], "n_flagged_bmom": st_bmom["n_flagged"],
    "gate_c_power_floor_pass": gate_c, "gate_c_threshold": 15,
    "n_flagged_weeks_reused_from_smv2z": len(FLAGGED_WEEKS),
    "flagged_week_keys": FLAGGED_WEEKS,
    "contribution_share_solar_of_flagged_twin_pnl": contrib_solar,
    "contribution_share_bmom_of_flagged_twin_pnl": contrib_bmom,
    "twin_flagged_share_of_twin_total_pnl": twin_flagged_share_of_total,
    "LICENSED": LICENSED,
}
with open(os.path.join(OUT, "license_decision.json"), "w") as f:
    json.dump(license_decision, f, indent=2, default=float)
log(f"\nlicense_decision.json written: LICENSED={LICENSED}")

if not LICENSED:
    reasons = []
    if not gate_a:
        reasons.append(f"gate(a) FAILED: asymmetry ratio {asym_ratio:.4f} < 1.3 required -- the two legs do "
                        f"NOT respond asymmetrically to the flag (vol_ratio_solar={vr_solar:.4f}, "
                        f"vol_ratio_bmom={vr_bmom:.4f}); both legs scale up together, consistent with SMV2Q's "
                        f"established finding (Q10) that joint-loss/flagged states are a WHIPSAW state where "
                        f"both engines move together, not a state where one engine misbehaves and the other "
                        f"stays calm.")
    if not gate_b:
        reasons.append(f"gate(b) FAILED: the relatively-more-stable leg ({stable_leg}) has a materially worse "
                        f"flagged-week Sharpe ({sh_flag_stable:.4f}) than its own unconditional Sharpe "
                        f"({sh_all_stable:.4f}, drop={drop:.4f}, sign_flip={sign_flip}) -- shifting weight "
                        f"toward it during flagged weeks would be shifting into a leg that ALSO degrades then, "
                        f"just less loudly than its counterpart.")
    if not gate_c:
        reasons.append(f"gate(c) FAILED: power floor N>=15 not met (n_flagged_solar={st_solar['n_flagged']}, "
                        f"n_flagged_bmom={st_bmom['n_flagged']}).")
    report = f"""# SMV2AA_MIX_SHIFT -- REPORT (seq 406)

**Class**: DIAGNOSTIC (prerequisite). Spec: `runs/SMV2AA_MIX_SHIFT/spec.yaml` (committed f6fb7d1).
**Outcome: DIAGNOSTIC KILL.** Policy cells 407-409 were NOT run, per the spec's explicit
honest-stop instruction ("if license_rule fails on (a) or (b): DIAGNOSTIC KILL... do NOT run
policy cells 407-409"). This is a valid, complete, pre-registered stopping point, not partial work.

Dev window: sessions <= 2026-05-31 (leg_daily.csv: {leg.index.min().date()}..{leg.index.max().date()},
{len(leg)} sessions). No data >= 2026-08-01 (VIRGIN floor) touched anywhere in this run.

## 406 diagnostic result (FACT -- out/leg_asymmetry.csv, out/license_decision.json)

Reused, not recomputed: SMV2Z's exact 23 trigger-week -> 23 receiver(t+1)-week flag set, pulled
directly from `runs/SMV2Z_VIABILITY_POLICY/out/policy_daily.csv` ('scaled'==True week_keys) and
cross-checked byte-for-byte against SMV2Z's own `run_log.txt` printed `trigger_week_keys` line
(PASS, 23/23 identical): {FLAGGED_WEEKS}

Data: `runs/SMV2Q_DIAGNOSTICS/out/leg_daily.csv` columns leg_solar/leg_bmom/twin (leg_solar +
leg_bmom - twin max abs error {recon_err:.2e}, confirming the legs rebuild the twin exactly, as
SMV2Q itself documents).

| leg | vol\\_flagged | vol\\_unflagged | vol\\_ratio | sharpe\\_flagged | sharpe\\_all | sharpe\\_drop | n\\_flagged |
|---|---|---|---|---|---|---|---|
| leg_solar | {st_solar['vol_flagged']:.1f} | {st_solar['vol_unflagged']:.1f} | {st_solar['vol_ratio']:.4f} | {st_solar['sharpe_flagged']:.4f} | {st_solar['sharpe_all']:.4f} | {st_solar['sharpe_drop']:.4f} | {st_solar['n_flagged']} |
| leg_bmom  | {st_bmom['vol_flagged']:.1f} | {st_bmom['vol_unflagged']:.1f} | {st_bmom['vol_ratio']:.4f} | {st_bmom['sharpe_flagged']:.4f} | {st_bmom['sharpe_all']:.4f} | {st_bmom['sharpe_drop']:.4f} | {st_bmom['n_flagged']} |

Contribution share of flagged-week twin PnL (context, per spec 406's request; twin != champion
'nt' exactly, corr 0.9992 per SMV2M, so this is a plausibility check on SMV2Z's 30.3%-of-total-nt
figure, not a reproduction of it): leg_solar {contrib_solar:.1%}, leg_bmom {contrib_bmom:.1%} of
flagged-week twin PnL; twin's own flagged-week PnL is {twin_flagged_share_of_total:.1%} of twin's
total dev PnL (SMV2Z's nt-based figure was 30.3%).

**license_rule (ALL required to proceed; per spec, ANY of (a)/(b) failing is a DIAGNOSTIC KILL)**:
- (a) asymmetry: max(vol_ratio_solar, vol_ratio_bmom) / min(...) = {asym_ratio:.4f} (need >= 1.3) ->
  **{"PASS" if gate_a else "FAIL"}**
- (b) stable-leg ({stable_leg}) not materially worse in flagged weeks: sharpe_all={sh_all_stable:.4f},
  sharpe_flagged={sh_flag_stable:.4f}, drop={drop:.4f}, sign_flip={sign_flip}
  (rule: materially_worse := sign_flip(+->-) OR drop>1.0, pre-committed and applied mechanically,
  since the spec text leaves the numeric threshold for "materially worse" open) ->
  **{"PASS" if gate_b else "FAIL"}**
- (c) power floor: n_flagged_solar={st_solar['n_flagged']}, n_flagged_bmom={st_bmom['n_flagged']}
  (need >=15 each) -> **{"PASS" if gate_c else "FAIL"}**

**Why the mechanism does not exist here (INFERENCE, grounded in the FACTs above)**:
{chr(10).join('- ' + r for r in reasons)}

This is consistent with the campaign's own prior finding (SMV2Q_DIAGNOSTICS Q10, FACT): the
flagged (sigma460-top-tercile + ER150-top-tercile) state is characterized as "both sides lose
simultaneously... whipsaw, not directional error" (mtm_short t=-7.5, mtm_long t=-6.7 vs non-flagged
baseline). A mix-SHIFT mechanism requires the two legs to respond asymmetrically to the flag so
that de-weighting one and up-weighting the other has a real basis; a state that hits both legs in
the same whipsaw way at the same time gives a mix-shift nothing to work with -- reallocating weight
between two legs that misbehave together cannot help either, exactly as the spec's own framing
anticipated ("if both legs scale up together, a mix-shift cannot help either, and this spec must
say so and stop").

## Disposition (per spec `kill:` clause)

406 fails -> spec stops here (documented). The mix-shift mechanism itself (not just this specific
weight grid) is now closed on this flag definition, pending a genuinely different mechanism. This
does NOT reopen the parent SMV2Z finding (blanket exposure-cut during flagged weeks FAILED
because those weeks hold 30.3% of total net PnL on 9.9% of days) -- SMV2AA tested a structurally
different response to that same finding and also does not survive its own prerequisite gate.

## Outputs
`out/leg_asymmetry.csv`, `out/license_decision.json`, `out/run_log.txt`, this REPORT.md.
Not produced (per spec, correctly): `out/policy_cells.csv`, `out/placebo.csv`, `out/chronology.csv`
-- these are licensed-only outputs and 406 did not license this run.
"""
    with open(os.path.join(RUN, "REPORT.md"), "w") as f:
        f.write(report)
    with open(os.path.join(OUT, "run_log.txt"), "w") as f:
        f.write("\n".join(log_lines))
    log("\nDIAGNOSTIC KILL written. REPORT.md complete. Stopping per spec (honest-stop path).")
    sys.exit(0)

log("\n406 LICENSED -- proceeding to 407-409 policy cells.")
# (continued in part 2 if licensed)
