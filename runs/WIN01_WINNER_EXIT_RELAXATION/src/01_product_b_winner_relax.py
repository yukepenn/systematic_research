"""WIN01 -- Product B winner-qualified exit relaxation.

Merges health_substrate.build_pos_seq (decision) and health_substrate.onelot_exec (execution)
into a SINGLE causal forward pass so a running, online, block-local MFE (dollars) is available
to the decision step at each bar -- needed to make the winner-qualification predicate genuinely
causal (uses only bars already realized by t). Verified byte-identical to the original two-pass
implementation when qualification is set unreachable (correctness gate below) BEFORE any
relaxation cell is evaluated.
"""
import os, sys, json
import numpy as np, pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
sys.path.insert(0, os.path.join(ROOT, "runs", "W18R1_M1_VOLSEASON", "src"))
sys.path.insert(0, os.path.join(ROOT, "runs", "SA0_SYSTEM_STRUCTURE", "current_health", "src"))
from sm01_solarsim import _fill
import health_substrate as HS

OUT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "out")
os.makedirs(OUT, exist_ok=True)

n = HS.n
last = HS.last
entry_blocked_c4 = HS.entry_blocked_c4
forced_flat_c4 = HS.forced_flat_c4
M = HS.M
open_, high, low, close = HS.open_, HS.high, HS.low, HS.close
COMM_NQ, PV_NQ = HS.COMM_NQ, HS.PV_NQ
COMM_MNQ, PV_MNQ = HS.COMM_MNQ, HS.PV_MNQ
ENTRY_LEVEL, EXIT_LEVEL = HS.ENTRY_LEVEL, HS.EXIT_LEVEL
bars = HS.bars
sd = bars["sess_date"].to_numpy()
sd_dt = pd.to_datetime(pd.Series(sd))
year_arr = pd.to_datetime(sd_dt).dt.year.to_numpy()
CANONICAL_END = HS.CANONICAL_END
canon_mask = (sd_dt <= CANONICAL_END).to_numpy()


def winner_relaxed_sim(M_arr, qual_mfe_dollars, relaxed_exit_level,
                        entry_level=ENTRY_LEVEL, exit_level=EXIT_LEVEL,
                        entry_blocked=None, forced_flat=None,
                        comm=COMM_NQ, pv=PV_NQ, o=open_, h=high, l=low, c=close):
    """Single causal forward pass: decision (with winner-qualified exit relaxation) + execution
    interleaved. Returns pos_seq, bar_pnl, qualified_flag_by_bar, exit_reason_by_block (dict),
    block_id (sign-segmented, same convention as U0's segment_and_mfe_mae)."""
    entry_blocked = entry_blocked if entry_blocked is not None else entry_blocked_c4
    forced_flat = forced_flat if forced_flat is not None else forced_flat_c4
    p = 0; pend = 0
    cash = 0.0; prev_eq = 0.0
    pos_seq = np.zeros(n, dtype=int)
    bar_pnl = np.zeros(n)
    qualified_arr = np.zeros(n, dtype=bool)
    block_id = np.zeros(n, dtype=int)
    exit_reason = {}  # block_id -> reason string, recorded when block ends
    cur_block = 0
    run_pnl_block = 0.0; mfe_block = 0.0; qualified = False
    was_relaxed_active_this_block = False

    for t in range(n):
        if last[t]:
            if p != 0:
                d = -p
                side = -1 if p > 0 else 1
                px = _fill(o[t], h[t], l[t], side, at_close=c[t])
                cash -= d * px * pv
                cash -= abs(d) * comm
                exit_reason[cur_block] = "SESSION_CLOSE"
            p = 0; pend = 0
            pos_seq[t] = 0
            block_id[t] = cur_block
            eq = cash + 0.0 * c[t] * pv
            bar_pnl[t] = eq - prev_eq; prev_eq = eq
            run_pnl_block = 0.0; mfe_block = 0.0; qualified = False
            was_relaxed_active_this_block = False
            continue

        if pend != p:
            prior_sign = np.sign(p)
            d = pend - p
            side = 1 if d > 0 else -1
            px = _fill(o[t], h[t], l[t], side)
            cash -= d * px * pv
            cash -= abs(d) * comm
            p = pend
            if np.sign(p) != prior_sign:
                if prior_sign != 0 and cur_block not in exit_reason:
                    # only set the default M_EXIT/M_RELAXED_EXIT/REVERSAL reason if forced_flat
                    # didn't already tag this block C4_FORCED at the decision bar (see below) --
                    # forced_flat has absolute priority in the decision branch, so its tag must win.
                    reason = "REVERSAL" if p != 0 else ("M_RELAXED_EXIT" if was_relaxed_active_this_block else "M_EXIT")
                    exit_reason[cur_block] = reason
                cur_block += 1
                run_pnl_block = 0.0; mfe_block = 0.0; qualified = False
                was_relaxed_active_this_block = False

        pos_seq[t] = p
        block_id[t] = cur_block
        eq = cash + p * c[t] * pv
        bpnl_t = eq - prev_eq
        bar_pnl[t] = bpnl_t; prev_eq = eq

        if p != 0:
            run_pnl_block += bpnl_t
            mfe_block = max(mfe_block, max(run_pnl_block, 0.0))
            if not qualified and mfe_block >= qual_mfe_dollars:
                qualified = True
        qualified_arr[t] = qualified and p != 0
        exit_lvl_eff = relaxed_exit_level if (qualified and p != 0) else exit_level
        if qualified and p != 0 and relaxed_exit_level != exit_level:
            was_relaxed_active_this_block = True

        if forced_flat[t]:
            tgt = 0
            if p != 0:
                exit_reason[cur_block] = "C4_FORCED"
        elif p == 0:
            tgt = 0 if entry_blocked[t] else (1 if M_arr[t] >= entry_level else (-1 if M_arr[t] <= -entry_level else 0))
        elif p > 0:
            if M_arr[t] <= -entry_level and not entry_blocked[t]:
                tgt = -1
            elif M_arr[t] <= exit_lvl_eff:
                tgt = 0
            else:
                tgt = p
        else:
            if M_arr[t] >= entry_level and not entry_blocked[t]:
                tgt = 1
            elif M_arr[t] >= -exit_lvl_eff:
                tgt = 0
            else:
                tgt = p
        pend = tgt

    return pos_seq, bar_pnl, qualified_arr, block_id, exit_reason


# ============================================================= correctness gate
print("[WIN01-B] correctness gate: merged loop, qualification unreachable ...", flush=True)
pos_gate, bpnl_gate, _, _, _ = winner_relaxed_sim(M, qual_mfe_dollars=float("inf"), relaxed_exit_level=EXIT_LEVEL)
gate_net = float(bpnl_gate[canon_mask].sum())
assert abs(gate_net - 301915.92) < 1.0, f"WIN01-B correctness gate FAILED: {gate_net} != 301915.92"
print(f"[WIN01-B] correctness gate PASS: merged-loop no-op net = {gate_net:.2f} (certified 301915.92)", flush=True)

# cross-check against the ORIGINAL two-pass functions bar-for-bar
pos_orig = HS.build_pos_seq(M)
daily_orig, barpos_orig, bpnl_orig = HS.onelot_exec(pos_orig, COMM_NQ, PV_NQ, open_, high, low, close)
assert np.array_equal(pos_gate, pos_orig), "WIN01-B position sequence diverges from original build_pos_seq at qual=inf"
assert np.allclose(bpnl_gate, bpnl_orig), "WIN01-B bar_pnl diverges from original onelot_exec at qual=inf"
print("[WIN01-B] cross-check PASS: merged loop reproduces original build_pos_seq/onelot_exec bar-for-bar", flush=True)

# MNQ leg, informational only (NOT the primary product for this family -- NQ is the frozen
# baseline per CLAUDE.md). NOTE: this uses NQ OHLC for MNQ-leg fills (same convention as this
# file's own onelot_exec default args), which does NOT reproduce the certified $28,587.10 (that
# figure requires U0's genuine-MNQ-price alignment, out of scope here) -- disclosed, not a gate.
pos_gate_mnq, bpnl_gate_mnq, _, _, _ = winner_relaxed_sim(
    M, qual_mfe_dollars=float("inf"), relaxed_exit_level=EXIT_LEVEL, comm=COMM_MNQ, pv=PV_MNQ)
gate_net_mnq = float(bpnl_gate_mnq[canon_mask].sum())
print(f"[WIN01-B] MNQ leg (NQ-priced proxy, informational only, NOT the certified genuine-MNQ "
      f"net): {gate_net_mnq:.2f} (certified genuine-MNQ net is 28587.10, uses different price "
      f"array -- not reproduced here, NQ is this family's primary product)", flush=True)

CONTROL_POS, CONTROL_BPNL = pos_orig, bpnl_orig

CELLS = {
    "CONTROL": dict(qual_mfe_dollars=float("inf"), relaxed_exit_level=EXIT_LEVEL),
    "WINB_RELAX_050": dict(qual_mfe_dollars=1000.0, relaxed_exit_level=0.5),
    "WINB_RELAX_000": dict(qual_mfe_dollars=1000.0, relaxed_exit_level=0.0),
}

results = {}
for name, kw in CELLS.items():
    pos_c, bpnl_c, qual_c, blk_c, reason_c = winner_relaxed_sim(M, **kw)
    results[name] = dict(pos=pos_c, bpnl=bpnl_c, qual=qual_c, blk=blk_c, reason=reason_c)
    net_canon = float(bpnl_c[canon_mask].sum())
    net_ext = float(bpnl_c.sum())
    print(f"[WIN01-B] {name}: canonical net={net_canon:,.2f}  extended net={net_ext:,.2f}", flush=True)

# ============================================================= year-by-year + 2022-2025 delta
print("\n[WIN01-B] year-by-year ...", flush=True)
yby_rows = []
for name, r in results.items():
    for y in sorted(set(year_arr[canon_mask])):
        m = (year_arr == y) & canon_mask
        yby_rows.append({"cell": name, "year": int(y), "net": float(r["bpnl"][m].sum())})
yby = pd.DataFrame(yby_rows)
yby_piv = yby.pivot(index="year", columns="cell", values="net")
print(yby_piv.round(2))

net_2225_mask = canon_mask & (year_arr >= 2022) & (year_arr <= 2025)
control_2225 = float(CONTROL_BPNL[net_2225_mask].sum())
delta_2225 = {}
for name, r in results.items():
    if name == "CONTROL":
        continue
    net_2225 = float(r["bpnl"][net_2225_mask].sum())
    delta = net_2225 - control_2225
    delta_pct = delta / control_2225 * 100
    delta_2225[name] = dict(net_2225=net_2225, delta=delta, delta_pct=delta_pct)
    print(f"[WIN01-B] {name} 2022-2025: net={net_2225:,.2f}  control={control_2225:,.2f}  "
          f"delta={delta:+,.2f} ({delta_pct:+.3f}% of control)", flush=True)

# LOYO
print("\n[WIN01-B] LOYO (leave-one-year-out, 2022-2025) ...", flush=True)
loyo_rows = []
for name, r in results.items():
    if name == "CONTROL":
        continue
    for y_drop in [2022, 2023, 2024, 2025]:
        m = net_2225_mask & (year_arr != y_drop)
        c_net = float(CONTROL_BPNL[m].sum())
        cand_net = float(r["bpnl"][m].sum())
        d = cand_net - c_net
        loyo_rows.append({"cell": name, "drop_year": y_drop, "control_net": c_net,
                           "cand_net": cand_net, "delta": d, "delta_pct_of_control": d / c_net * 100})
loyo_df = pd.DataFrame(loyo_rows)
print(loyo_df.round(2).to_string(index=False))

# 2026 health-only extension, reported separately
print("\n[WIN01-B] 2026 health-only extension (2026-06-01..2026-07-31), SEPARATE, not blended ...", flush=True)
health_mask = ~canon_mask
control_health = float(CONTROL_BPNL[health_mask].sum())
for name, r in results.items():
    if name == "CONTROL":
        continue
    cand_health = float(r["bpnl"][health_mask].sum())
    print(f"[WIN01-B] {name} health-only: net={cand_health:,.2f}  control={control_health:,.2f}  "
          f"delta={cand_health - control_health:+,.2f}", flush=True)

# ============================================================= right-tail audit (top-20/bottom-20 blocks)
print("\n[WIN01-B] right-tail audit ...", flush=True)


def block_table(pos_arr, bpnl_arr, blk_arr, mask):
    df = pd.DataFrame({"blk": blk_arr[mask], "pnl": bpnl_arr[mask], "pos": pos_arr[mask], "sess": sd[mask]})
    df = df[df["pos"] != 0]
    g = df.groupby("blk").agg(net=("pnl", "sum"), n_bars=("pnl", "size"),
                               first_sess=("sess", "first"), last_sess=("sess", "last"),
                               sign=("pos", "first")).reset_index()
    return g


control_blocks = block_table(CONTROL_POS, CONTROL_BPNL, np.cumsum(np.r_[True, np.sign(CONTROL_POS)[1:] != np.sign(CONTROL_POS)[:-1]]), canon_mask)
tail_summary = {}
for name, r in results.items():
    blk = block_table(r["pos"], r["bpnl"], r["blk"], canon_mask)
    top20 = blk.nlargest(20, "net")
    bot20 = blk.nsmallest(20, "net")
    tail_summary[name] = dict(n_blocks=len(blk), top20_sum=float(top20["net"].sum()),
                               bot20_sum=float(bot20["net"].sum()),
                               top20=top20.to_dict("records"), bot20=bot20.to_dict("records"))
    print(f"[WIN01-B] {name}: n_blocks={len(blk)}  top20_sum={top20['net'].sum():,.2f}  "
          f"bot20_sum={bot20['net'].sum():,.2f}", flush=True)

print(f"[WIN01-B] CONTROL: n_blocks={len(control_blocks)}  "
      f"top20_sum={control_blocks.nlargest(20,'net')['net'].sum():,.2f}  "
      f"bot20_sum={control_blocks.nsmallest(20,'net')['net'].sum():,.2f}", flush=True)

# ============================================================= opportunity-occupancy attribution
print("\n[WIN01-B] opportunity-occupancy attribution (canonical window) ...", flush=True)
occ_summary = {}
for name, r in results.items():
    if name == "CONTROL":
        continue
    cand_pos = r["pos"]; cand_bpnl = r["bpnl"]
    agree = (cand_pos == CONTROL_POS)
    differ = ~agree & canon_mask
    # bucket a: control flat, candidate occupied -> pure extension
    ext_mask = differ & (CONTROL_POS == 0) & (cand_pos != 0)
    # bucket b: control occupied with something candidate is not in (candidate flat OR different value)
    occ_mask = differ & (CONTROL_POS != 0) & (cand_pos != CONTROL_POS)
    ext_pnl = float(cand_bpnl[ext_mask].sum())
    occ_cost = float(cand_bpnl[occ_mask].sum() - CONTROL_BPNL[occ_mask].sum())
    # per-block sign of extension segment: use candidate block id restricted to ext_mask bars
    ext_df = pd.DataFrame({"blk": r["blk"][ext_mask], "pnl": cand_bpnl[ext_mask]})
    per_block_ext = ext_df.groupby("blk")["pnl"].sum()
    added_winner = float(per_block_ext[per_block_ext > 0].sum())
    added_loser = float(per_block_ext[per_block_ext <= 0].sum())
    # reversal-specific subset of occ_mask: control's own action REVERSAL bars
    control_sign = np.sign(CONTROL_POS)
    control_prev_sign = np.r_[0, control_sign[:-1]]
    control_reversal_bar = (control_prev_sign != 0) & (control_sign != 0) & (control_prev_sign != control_sign)
    reversal_occ_mask = occ_mask & control_reversal_bar
    reversal_occ_cost = float(cand_bpnl[reversal_occ_mask].sum() - CONTROL_BPNL[reversal_occ_mask].sum())
    c4_occ_mask = occ_mask & forced_flat_c4
    c4_occ_cost = float(cand_bpnl[c4_occ_mask].sum() - CONTROL_BPNL[c4_occ_mask].sum())
    n_differ_bars = int(differ.sum())
    total_delta_canon = float(cand_bpnl[canon_mask].sum() - CONTROL_BPNL[canon_mask].sum())
    check = ext_pnl + occ_cost
    occ_summary[name] = dict(
        n_differ_bars=n_differ_bars, extension_pnl=ext_pnl, added_winner_dollars=added_winner,
        added_loser_dollars=added_loser, occupancy_blocked_cost=occ_cost,
        reversal_blocked_cost=reversal_occ_cost, c4_window_blocked_cost=c4_occ_cost,
        total_delta_canonical=total_delta_canon, ext_plus_occ_check=check,
    )
    print(f"[WIN01-B] {name}: differ_bars={n_differ_bars}  extension_pnl={ext_pnl:+,.2f} "
          f"(added_winner={added_winner:+,.2f}, added_loser={added_loser:+,.2f})  "
          f"occupancy_blocked_cost={occ_cost:+,.2f} (reversal_subset={reversal_occ_cost:+,.2f}, "
          f"c4_subset={c4_occ_cost:+,.2f})  total_delta={total_delta_canon:+,.2f}  "
          f"(ext+occ check={check:+,.2f})", flush=True)

# exit-reason distribution among candidate blocks that were EVER qualified/relaxed
print("\n[WIN01-B] exit-reason distribution for RELAXED blocks (blocks that reached qualification) ...", flush=True)
exit_reason_summary = {}
for name, r in results.items():
    if name == "CONTROL":
        continue
    qual_blocks = set(r["blk"][r["qual"] & canon_mask])
    reasons = [r["reason"].get(b, "OPEN_AT_DATA_END") for b in qual_blocks]
    vc = pd.Series(reasons).value_counts()
    exit_reason_summary[name] = vc.to_dict()
    print(f"[WIN01-B] {name}: n_qualified_blocks={len(qual_blocks)}  exit reasons: {vc.to_dict()}", flush=True)

# baseline C4-forced-exit win rate fact check on CONTROL for comparison
control_blk_id = np.cumsum(np.r_[True, np.sign(CONTROL_POS)[1:] != np.sign(CONTROL_POS)[:-1]])
_, _, _, _, control_reason = winner_relaxed_sim(M, qual_mfe_dollars=float("inf"), relaxed_exit_level=EXIT_LEVEL)
c4_blocks_control = [b for b, reason in control_reason.items() if reason == "C4_FORCED"]
cb = block_table(CONTROL_POS, CONTROL_BPNL, control_blk_id, canon_mask)
cb_c4 = cb[cb["blk"].isin(c4_blocks_control)]
if len(cb_c4) > 0:
    print(f"[WIN01-B] CONTROL C4-forced-exit blocks: n={len(cb_c4)}  win_rate={100*(cb_c4['net']>0).mean():.1f}%  "
          f"mean_pnl={cb_c4['net'].mean():,.2f}", flush=True)

# ============================================================= cost stress
print("\n[WIN01-B] cost stress (commission multiplier 1x/1.5x/2x, canonical window) ...", flush=True)
cost_rows = []
for name, kw in CELLS.items():
    for mult in [1.0, 1.5, 2.0]:
        pos_c, bpnl_c, _, _, _ = winner_relaxed_sim(M, comm=COMM_NQ * mult, **kw)
        net = float(bpnl_c[canon_mask].sum())
        cost_rows.append({"cell": name, "comm_mult": mult, "net": net})
cost_df = pd.DataFrame(cost_rows).pivot(index="comm_mult", columns="cell", values="net")
print(cost_df.round(2))
for name in CELLS:
    if name == "CONTROL":
        continue
    for mult in [1.0, 1.5, 2.0]:
        c_net = cost_df.loc[mult, "CONTROL"]
        cand_net = cost_df.loc[mult, name]
        print(f"[WIN01-B] {name} @ {mult}x commission: delta vs control = {cand_net - c_net:+,.2f} "
              f"({(cand_net - c_net) / c_net * 100:+.3f}% of control)", flush=True)

# trade count (n entries) comparison -- does relaxation change round-trip count?
print("\n[WIN01-B] trade count (n ENTRY events) ...", flush=True)
for name, r in results.items():
    sgn = np.sign(r["pos"][canon_mask])
    prev_sgn = np.r_[0, sgn[:-1]]
    n_entries = int(((prev_sgn == 0) & (sgn != 0)).sum())
    print(f"[WIN01-B] {name}: n_entries={n_entries}", flush=True)

# ============================================================= save outputs
out = {
    "correctness_gate": {"canonical_net_noop": gate_net, "canonical_net_noop_mnq": gate_net_mnq,
                          "matches_original_bar_for_bar": True},
    "canonical_nets": {name: float(r["bpnl"][canon_mask].sum()) for name, r in results.items()},
    "extended_nets": {name: float(r["bpnl"].sum()) for name, r in results.items()},
    "delta_2022_2025": delta_2225,
    "right_tail": {name: {"n_blocks": tail_summary[name]["n_blocks"],
                           "top20_sum": tail_summary[name]["top20_sum"],
                           "bot20_sum": tail_summary[name]["bot20_sum"]} for name in results},
    "control_right_tail": {"n_blocks": len(control_blocks),
                            "top20_sum": float(control_blocks.nlargest(20, "net")["net"].sum()),
                            "bot20_sum": float(control_blocks.nsmallest(20, "net")["net"].sum())},
    "opportunity_occupancy": occ_summary,
    "exit_reason_qualified_blocks": exit_reason_summary,
    "control_c4_forced_exit_stat": {"n": len(cb_c4), "win_rate_pct": float(100 * (cb_c4["net"] > 0).mean()) if len(cb_c4) else None,
                                     "mean_pnl": float(cb_c4["net"].mean()) if len(cb_c4) else None},
    "cost_stress": cost_df.to_dict(),
    "health_only_2026": {name: float(r["bpnl"][health_mask].sum()) for name, r in results.items()},
}
with open(os.path.join(OUT, "product_b_recon.json"), "w") as f:
    json.dump(out, f, indent=2, default=str)
yby_piv.to_csv(os.path.join(OUT, "product_b_year_by_year.csv"))
loyo_df.to_csv(os.path.join(OUT, "product_b_loyo.csv"), index=False)
for name in results:
    blk = block_table(results[name]["pos"], results[name]["bpnl"], results[name]["blk"], canon_mask)
    blk.to_csv(os.path.join(OUT, f"product_b_blocks_{name}.csv"), index=False)
control_blocks.to_csv(os.path.join(OUT, "product_b_blocks_CONTROL_verify.csv"), index=False)

print("\n[WIN01-B] done. Outputs saved to", OUT, flush=True)
