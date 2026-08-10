"""WIN01 -- Product A winner-qualified exposure-decay throttle.

Decision layer (target_exposure_A path) is computed ONCE per cell using LEGACY (NQ-priced)
mark-to-market bar P&L to drive the causal, online winner-qualification signal (exactly mirroring
u0_state_table's MFE_A_dollars definition, just computed online instead of post-hoc). The SAME
realized target_exposure_A path is then re-priced on genuine MNQ OHLC (PRICE01's own dual-truth
pattern: one decision sequence, two price bases) to report GENUINE_MNQ_EXECUTION_ECONOMICS
alongside LEGACY_RESEARCH_PROXY, per directive sec13/77.
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
T, tilt_state, B = HS.T, HS.tilt_state, HS.B
open_, high, low, close = HS.open_, HS.high, HS.low, HS.close
bars = HS.bars
sd = bars["sess_date"].to_numpy()
sd_dt = pd.to_datetime(pd.Series(sd))
year_arr = pd.to_datetime(sd_dt).dt.year.to_numpy()
CANONICAL_END = HS.CANONICAL_END
canon_mask = (sd_dt <= CANONICAL_END).to_numpy()

KSOLAR, KBMOM, TILTRESCALE, TILTMULT, SHORTHALF = 0.728654, 2.934159, 0.9026, 1.25, 0.5
PV_MNQ_A, COMM_MNQ_A = 2.0, 0.65


def rha(x):
    return np.sign(x) * np.floor(np.abs(x) + 0.5)


# ---------------------------------------------------------------- genuine MNQ OHLC alignment (identical to U0/PRICE01)
mnq_raw = pd.read_csv(os.path.join(ROOT, "runs", "PRODUCTB_ONECONTRACT_FINAL", "out", "mnq_3m_raw.csv"), comment="#")
mnq_raw["time"] = pd.to_datetime(mnq_raw["time"])
mnq_idx = mnq_raw.set_index("time")
aligned_raw = mnq_idx.reindex(bars["time"])
is_mnq_genuine = aligned_raw["close"].notna().to_numpy()
o_mnq = np.where(is_mnq_genuine, aligned_raw["open"].to_numpy(), open_)
h_mnq = np.where(is_mnq_genuine, aligned_raw["high"].to_numpy(), high)
l_mnq = np.where(is_mnq_genuine, aligned_raw["low"].to_numpy(), low)
c_mnq = np.where(is_mnq_genuine, aligned_raw["close"].to_numpy(), close)
print(f"[WIN01-A] MNQ genuine bars: {int(is_mnq_genuine.sum())} / {n}", flush=True)


def product_a_winner_relax(qual_mfe_dollars, mechanism, cap_contracts=None, floor_frac=None,
                            pv=PV_MNQ_A, comm=COMM_MNQ_A, o=open_, h=high, l=low, c=close):
    """Single causal forward pass (decision + LEGACY-price execution + online qualification)."""
    m_arr = np.where((T != 0) & (tilt_state != 0) & (np.sign(T) == tilt_state), TILTMULT, 1.0)
    s_arr = np.where((T < 0) & (tilt_state > 0), SHORTHALF, 1.0)
    Tpp = np.clip(rha(T * m_arr * s_arr * TILTRESCALE), -13, 13)
    M_a = np.clip(rha(KSOLAR * Tpp + KBMOM * B), -13, 13)

    cash = 0.0; p = 0; pend = 0; prev_eq = 0.0
    bar_pos = np.zeros(n, dtype=int)
    bar_pnl = np.zeros(n)
    qualified_arr = np.zeros(n, dtype=bool)
    block_id = np.zeros(n, dtype=int)
    cur_block = 0
    run_pnl_block = 0.0; mfe_block = 0.0; qualified = False
    peak_abs_exp_block = 0

    for t in range(n):
        if pend != p:
            prior_sign = np.sign(p)
            d = pend - p
            side = 1 if d > 0 else -1
            px = _fill(o[t], h[t], l[t], side)
            cash -= d * px * pv
            cash -= abs(d) * comm
            p = pend
            if np.sign(p) != prior_sign:
                cur_block += 1
                run_pnl_block = 0.0; mfe_block = 0.0; qualified = False; peak_abs_exp_block = 0

        if last[t] and p != 0:
            side = -1 if p > 0 else 1
            px = _fill(o[t], h[t], l[t], side, at_close=c[t])
            cash += p * px * pv
            cash -= abs(p) * comm
            p = 0; pend = 0
            bar_pos[t] = 0
            eq = cash + 0.0 * c[t] * pv
            bar_pnl[t] = eq - prev_eq; prev_eq = eq
            run_pnl_block = 0.0; mfe_block = 0.0; qualified = False; peak_abs_exp_block = 0
            block_id[t] = cur_block
            continue

        bar_pos[t] = p
        eq = cash + p * c[t] * pv
        bpnl_t = eq - prev_eq
        bar_pnl[t] = bpnl_t; prev_eq = eq
        block_id[t] = cur_block

        if p != 0:
            run_pnl_block += bpnl_t
            mfe_block = max(mfe_block, max(run_pnl_block, 0.0))
            peak_abs_exp_block = max(peak_abs_exp_block, abs(p))
            if not qualified and mfe_block >= qual_mfe_dollars:
                qualified = True
        qualified_arr[t] = qualified and p != 0

        tgt_raw = int(M_a[t])
        if forced_flat_c4[t]:
            tgt = 0
        elif entry_blocked_c4[t]:
            if tgt_raw == 0 or p == 0:
                tgt = 0
            elif np.sign(tgt_raw) != np.sign(p):
                tgt = 0
            else:
                tgt = p if abs(tgt_raw) > abs(p) else tgt_raw
        else:
            is_decay = (p != 0) and (abs(tgt_raw) < abs(p)) and (tgt_raw == 0 or np.sign(tgt_raw) == np.sign(p))
            if is_decay and qualified:
                if mechanism == "cap":
                    dec = min(abs(p) - abs(tgt_raw), cap_contracts)
                    tgt = int(p - np.sign(p) * dec)
                elif mechanism == "floor":
                    floor_mag = int(np.floor(floor_frac * peak_abs_exp_block + 1e-9))
                    if abs(tgt_raw) < floor_mag:
                        tgt = int(np.sign(p) * floor_mag)
                    else:
                        tgt = tgt_raw
                else:
                    tgt = tgt_raw
            else:
                tgt = tgt_raw
        pend = tgt

    return bar_pos, bar_pnl, qualified_arr, block_id, M_a


def reprice(target_path, o, h, l, c, pv, comm):
    """Replay a FIXED, already-decided position path on a different price series (PRICE01's
    dual-truth pattern) -- no re-deciding, fill economics only."""
    n_ = len(target_path)
    cash = 0.0; p = 0; prev_eq = 0.0
    bar_pnl = np.zeros(n_)
    for t in range(n_):
        pend = int(target_path[t])
        if pend != p:
            d = pend - p
            side = 1 if d > 0 else -1
            px = _fill(o[t], h[t], l[t], side)
            cash -= d * px * pv
            cash -= abs(d) * comm
            p = pend
        if last[t] and p != 0:
            side = -1 if p > 0 else 1
            px = _fill(o[t], h[t], l[t], side, at_close=c[t])
            cash += p * px * pv
            cash -= abs(p) * comm
            p = 0
        eq = cash + p * c[t] * pv
        bar_pnl[t] = eq - prev_eq; prev_eq = eq
    return bar_pnl


# ============================================================= correctness gate
print("[WIN01-A] correctness gate: qualification unreachable ...", flush=True)
pos_gate, bpnl_gate, _, _, _ = product_a_winner_relax(qual_mfe_dollars=float("inf"), mechanism="none")
gate_net = float(bpnl_gate[canon_mask].sum())
assert abs(gate_net - 177924.40) < 1.0, f"WIN01-A correctness gate FAILED: {gate_net} != 177924.40"
print(f"[WIN01-A] correctness gate PASS: LEGACY canonical net = {gate_net:.2f} (certified 177924.40)", flush=True)

# reprice function self-check: repricing CONTROL's own path on NQ prices must reproduce the same net
bpnl_reprice_check = reprice(pos_gate, open_, high, low, close, 2.0, 0.65)
recheck_net = float(bpnl_reprice_check[canon_mask].sum())
assert abs(recheck_net - gate_net) < 1.0, f"WIN01-A reprice() self-check FAILED: {recheck_net} vs {gate_net}"
print(f"[WIN01-A] reprice() self-check PASS: {recheck_net:.2f} == {gate_net:.2f}", flush=True)

CELLS = {
    "CONTROL": dict(qual_mfe_dollars=float("inf"), mechanism="none"),
    "WINA_CAP1": dict(qual_mfe_dollars=1000.0, mechanism="cap", cap_contracts=1),
    "WINA_FLOOR050": dict(qual_mfe_dollars=1000.0, mechanism="floor", floor_frac=0.5),
}

results = {}
for name, kw in CELLS.items():
    pos_c, bpnl_legacy, qual_c, blk_c, M_a = product_a_winner_relax(**kw)
    bpnl_genuine = reprice(pos_c, o_mnq, h_mnq, l_mnq, c_mnq, PV_MNQ_A, COMM_MNQ_A)
    results[name] = dict(pos=pos_c, bpnl_legacy=bpnl_legacy, bpnl_genuine=bpnl_genuine, qual=qual_c, blk=blk_c)
    print(f"[WIN01-A] {name}: LEGACY canonical={bpnl_legacy[canon_mask].sum():,.2f}  "
          f"GENUINE canonical={bpnl_genuine[canon_mask].sum():,.2f}  "
          f"LEGACY extended={bpnl_legacy.sum():,.2f}  GENUINE extended={bpnl_genuine.sum():,.2f}", flush=True)

assert abs(float(results["CONTROL"]["bpnl_legacy"][canon_mask].sum()) - 177924.40) < 1.0
CONTROL_POS = results["CONTROL"]["pos"]
CONTROL_BPNL_L = results["CONTROL"]["bpnl_legacy"]
CONTROL_BPNL_G = results["CONTROL"]["bpnl_genuine"]

# ============================================================= year-by-year + 2022-2025 delta (both price bases)
print("\n[WIN01-A] year-by-year (LEGACY) ...", flush=True)
for basis, ctrl_bpnl, key in [("LEGACY", CONTROL_BPNL_L, "bpnl_legacy"), ("GENUINE", CONTROL_BPNL_G, "bpnl_genuine")]:
    yby_rows = []
    for name, r in results.items():
        for y in sorted(set(year_arr[canon_mask])):
            m = (year_arr == y) & canon_mask
            yby_rows.append({"cell": name, "year": int(y), "net": float(r[key][m].sum())})
    yby = pd.DataFrame(yby_rows).pivot(index="year", columns="cell", values="net")
    print(f"-- {basis} --")
    print(yby.round(2))
    yby.to_csv(os.path.join(OUT, f"product_a_year_by_year_{basis}.csv"))

net_2225_mask = canon_mask & (year_arr >= 2022) & (year_arr <= 2025)
delta_2225 = {}
for basis, ctrl_bpnl, key in [("LEGACY", CONTROL_BPNL_L, "bpnl_legacy"), ("GENUINE", CONTROL_BPNL_G, "bpnl_genuine")]:
    control_2225 = float(ctrl_bpnl[net_2225_mask].sum())
    for name, r in results.items():
        if name == "CONTROL":
            continue
        net_2225 = float(r[key][net_2225_mask].sum())
        delta = net_2225 - control_2225
        delta_pct = delta / control_2225 * 100
        delta_2225[f"{name}_{basis}"] = dict(net_2225=net_2225, control_2225=control_2225, delta=delta, delta_pct=delta_pct)
        print(f"[WIN01-A] {name} {basis} 2022-2025: net={net_2225:,.2f}  control={control_2225:,.2f}  "
              f"delta={delta:+,.2f} ({delta_pct:+.3f}% of control)", flush=True)

# LOYO (LEGACY basis, primary for this diagnostic; GENUINE follows the same signal path so same pattern expected)
print("\n[WIN01-A] LOYO (LEGACY, 2022-2025) ...", flush=True)
loyo_rows = []
for name, r in results.items():
    if name == "CONTROL":
        continue
    for y_drop in [2022, 2023, 2024, 2025]:
        m = net_2225_mask & (year_arr != y_drop)
        c_net = float(CONTROL_BPNL_L[m].sum())
        cand_net = float(r["bpnl_legacy"][m].sum())
        d = cand_net - c_net
        loyo_rows.append({"cell": name, "drop_year": y_drop, "control_net": c_net,
                           "cand_net": cand_net, "delta": d, "delta_pct_of_control": d / c_net * 100})
loyo_df = pd.DataFrame(loyo_rows)
print(loyo_df.round(2).to_string(index=False))
loyo_df.to_csv(os.path.join(OUT, "product_a_loyo.csv"), index=False)

# 2026 health-only extension, separate
print("\n[WIN01-A] 2026 health-only extension, SEPARATE ...", flush=True)
health_mask = ~canon_mask
for basis, ctrl_bpnl, key in [("LEGACY", CONTROL_BPNL_L, "bpnl_legacy"), ("GENUINE", CONTROL_BPNL_G, "bpnl_genuine")]:
    control_health = float(ctrl_bpnl[health_mask].sum())
    for name, r in results.items():
        if name == "CONTROL":
            continue
        cand_health = float(r[key][health_mask].sum())
        print(f"[WIN01-A] {name} {basis} health-only: net={cand_health:,.2f}  control={control_health:,.2f}  "
              f"delta={cand_health - control_health:+,.2f}", flush=True)

# ============================================================= right-tail audit (blocks, LEGACY pricing)
print("\n[WIN01-A] right-tail audit (LEGACY) ...", flush=True)


def block_table_a(pos_arr, bpnl_arr, blk_arr, mask):
    df = pd.DataFrame({"blk": blk_arr[mask], "pnl": bpnl_arr[mask], "pos": pos_arr[mask], "sess": sd[mask]})
    df = df[df["pos"] != 0]
    g = df.groupby("blk").agg(net=("pnl", "sum"), n_bars=("pnl", "size"), peak_abs=("pos", lambda s: s.abs().max()),
                               first_sess=("sess", "first"), last_sess=("sess", "last"),
                               sign=("pos", "first")).reset_index()
    return g


control_blk_id_a = np.cumsum(np.r_[True, np.sign(CONTROL_POS)[1:] != np.sign(CONTROL_POS)[:-1]])
control_blocks_a = block_table_a(CONTROL_POS, CONTROL_BPNL_L, control_blk_id_a, canon_mask)
print(f"[WIN01-A] CONTROL: n_blocks={len(control_blocks_a)}  "
      f"top20_sum={control_blocks_a.nlargest(20,'net')['net'].sum():,.2f}  "
      f"bot20_sum={control_blocks_a.nsmallest(20,'net')['net'].sum():,.2f}", flush=True)
tail_summary_a = {}
for name, r in results.items():
    blk = block_table_a(r["pos"], r["bpnl_legacy"], r["blk"], canon_mask)
    tail_summary_a[name] = dict(n_blocks=len(blk), top20_sum=float(blk.nlargest(20, "net")["net"].sum()),
                                 bot20_sum=float(blk.nsmallest(20, "net")["net"].sum()))
    blk.to_csv(os.path.join(OUT, f"product_a_blocks_{name}.csv"), index=False)
    print(f"[WIN01-A] {name}: n_blocks={len(blk)}  top20_sum={tail_summary_a[name]['top20_sum']:,.2f}  "
          f"bot20_sum={tail_summary_a[name]['bot20_sum']:,.2f}", flush=True)

# ============================================================= opportunity-occupancy attribution (LEGACY)
print("\n[WIN01-A] opportunity-occupancy attribution (LEGACY, canonical window) ...", flush=True)
occ_summary_a = {}
for name, r in results.items():
    if name == "CONTROL":
        continue
    cand_pos = r["pos"]; cand_bpnl = r["bpnl_legacy"]
    agree = (cand_pos == CONTROL_POS)
    differ = ~agree & canon_mask
    ext_mask = differ & (CONTROL_POS == 0) & (cand_pos != 0)
    occ_mask = differ & (CONTROL_POS != 0) & (cand_pos != CONTROL_POS)
    ext_pnl = float(cand_bpnl[ext_mask].sum())
    occ_cost = float(cand_bpnl[occ_mask].sum() - CONTROL_BPNL_L[occ_mask].sum())
    ext_df = pd.DataFrame({"blk": r["blk"][ext_mask], "pnl": cand_bpnl[ext_mask]})
    per_block_ext = ext_df.groupby("blk")["pnl"].sum()
    added_winner = float(per_block_ext[per_block_ext > 0].sum())
    added_loser = float(per_block_ext[per_block_ext <= 0].sum())
    n_differ_bars = int(differ.sum())
    total_delta_canon = float(cand_bpnl[canon_mask].sum() - CONTROL_BPNL_L[canon_mask].sum())
    check = ext_pnl + occ_cost
    occ_summary_a[name] = dict(n_differ_bars=n_differ_bars, extension_pnl=ext_pnl,
                                added_winner_dollars=added_winner, added_loser_dollars=added_loser,
                                occupancy_blocked_cost=occ_cost, total_delta_canonical=total_delta_canon,
                                ext_plus_occ_check=check)
    print(f"[WIN01-A] {name}: differ_bars={n_differ_bars}  extension_pnl={ext_pnl:+,.2f} "
          f"(added_winner={added_winner:+,.2f}, added_loser={added_loser:+,.2f})  "
          f"occupancy_blocked_cost={occ_cost:+,.2f}  total_delta={total_delta_canon:+,.2f}  "
          f"(ext+occ check={check:+,.2f})", flush=True)

# scale-in (opportunity to grow) suppressed by throttle? -- compare n SCALE_IN events (magnitude growth) count
print("\n[WIN01-A] SCALE_IN event counts (does throttling change willingness/ability to scale in later?) ...", flush=True)
for name, r in results.items():
    pos_c = r["pos"][canon_mask]
    d = np.diff(pos_c, prepend=0)
    n_scale_in = int(((np.sign(d) == np.sign(pos_c)) & (d != 0) & (pos_c != 0) &
                       (np.abs(pos_c) > np.abs(np.r_[0, pos_c[:-1]]))).sum())
    n_entries = int(((np.r_[0, pos_c[:-1]] == 0) & (pos_c != 0)).sum())
    print(f"[WIN01-A] {name}: n_entries={n_entries}  n_scale_in_events={n_scale_in}", flush=True)

# ============================================================= cost stress (LEGACY basis, commission mult)
print("\n[WIN01-A] cost stress (commission multiplier 1x/1.5x/2x, LEGACY canonical) ...", flush=True)
cost_rows = []
for name, kw in CELLS.items():
    for mult in [1.0, 1.5, 2.0]:
        kw2 = dict(kw); kw2["comm"] = COMM_MNQ_A * mult
        pos_c, bpnl_c, _, _, _ = product_a_winner_relax(**kw2)
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
        print(f"[WIN01-A] {name} @ {mult}x commission: delta vs control = {cand_net - c_net:+,.2f} "
              f"({(cand_net - c_net) / c_net * 100:+.3f}% of control)", flush=True)

# ============================================================= save outputs
out = {
    "correctness_gate": {"legacy_canonical_net_noop": gate_net, "reprice_selfcheck_net": recheck_net},
    "canonical_nets": {name: {"legacy": float(r["bpnl_legacy"][canon_mask].sum()),
                               "genuine": float(r["bpnl_genuine"][canon_mask].sum())} for name, r in results.items()},
    "extended_nets": {name: {"legacy": float(r["bpnl_legacy"].sum()),
                              "genuine": float(r["bpnl_genuine"].sum())} for name, r in results.items()},
    "delta_2022_2025": delta_2225,
    "right_tail": tail_summary_a,
    "control_right_tail": {"n_blocks": len(control_blocks_a),
                            "top20_sum": float(control_blocks_a.nlargest(20, "net")["net"].sum()),
                            "bot20_sum": float(control_blocks_a.nsmallest(20, "net")["net"].sum())},
    "opportunity_occupancy": occ_summary_a,
    "cost_stress": cost_df.to_dict(),
}
with open(os.path.join(OUT, "product_a_recon.json"), "w") as f:
    json.dump(out, f, indent=2, default=str)
control_blocks_a.to_csv(os.path.join(OUT, "product_a_blocks_CONTROL_verify.csv"), index=False)

print("\n[WIN01-A] done. Outputs saved to", OUT, flush=True)
