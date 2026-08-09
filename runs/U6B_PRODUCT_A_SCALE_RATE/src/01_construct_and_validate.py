"""U6B -- Product-A scale-RATE conditioned on state quality. Reuses SA0/current_health's
health_substrate.py verbatim for T/B/HTF_tilt_state/entry_blocked_c4/forced_flat_c4/PEND/OHLC
(the same extended-through-2026-07-31 substrate U0 itself imports), then re-implements
product_a_exec with exactly ONE new step inserted (the rate limiter), everything else
byte-identical to pa0_substrate.product_a_exec / U0's product_a_exec_generalized. See
../spec.yaml for the full preregistered construction.
"""
import os, sys, json
import numpy as np, pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
sys.path.insert(0, os.path.join(ROOT, "runs", "W18R1_M1_VOLSEASON", "src"))
sys.path.insert(0, os.path.join(ROOT, "runs", "SA0_SYSTEM_STRUCTURE", "current_health", "src"))
from sm01_solarsim import _fill
from smv2_common import dd_battery
import health_substrate as HS  # extended (through 2026-07-31) shared substrate, self-verified on import

OUT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "out")
os.makedirs(OUT, exist_ok=True)
U0_PATH = os.path.join(ROOT, "runs", "U0_UNIFIED_STATE", "out", "u0_state_table.parquet")

KSOLAR, KBMOM, TILTRESCALE, TILTMULT, SHORTHALF = 0.728654, 2.934159, 0.9026, 1.25, 0.5
PV_MNQ_A, COMM_MNQ_A = 2.0, 0.65  # PA0's own convention: PV multiplier applied to NQ's OWN OHLC, no MNQ price series

n = HS.n
open_, high, low, close = HS.open_, HS.high, HS.low, HS.close
last = HS.last
sd = HS.sess_arr
hm = HS.hm
year_arr = HS.year_arr
T, B, tilt_state = HS.T, np.asarray(HS.B), HS.tilt_state
entry_blocked_c4, forced_flat_c4 = HS.entry_blocked_c4, HS.forced_flat_c4
PEND = HS.PEND
CANONICAL_END, HEALTH_END = HS.CANONICAL_END, HS.HEALTH_END
vote_dispersion = (PEND > 0).sum(axis=1) - (PEND < 0).sum(axis=1)
sess_dt = pd.to_datetime(pd.Series(sd))
canon_mask = (sess_dt <= CANONICAL_END).to_numpy()
r2225_mask = canon_mask & (sess_dt <= pd.Timestamp("2025-12-31")).to_numpy()  # 2022-2025-only slice (subset of canonical)
print(f"[U6B] n={n} bars, canonical={canon_mask.sum()}, health-only-extension={(~canon_mask).sum()}, "
      f"2022-2025-only={r2225_mask.sum()}", flush=True)


def rha(x):
    return np.sign(x) * np.floor(np.abs(x) + 0.5)


# ============================================================= VOTE_THRESH: fixed, preregistered,
# derived ONCE from u0_state_table's own INCUMBENT path (non-circular -- never re-derived per grid cell)
u0 = pd.read_parquet(U0_PATH)
assert len(u0) == n, f"u0_state_table row count ({len(u0)}) != health_substrate n ({n})"
assert (pd.to_datetime(u0["time"]).to_numpy() == pd.to_datetime(HS.bars["time"]).to_numpy()).all(), \
    "u0_state_table and health_substrate bar timestamps must be identical"
canon_events_u0 = u0[(~u0["is_health_only_bar"]) & (u0["action_A"].isin(["ENTRY", "SCALE_IN"]))]
change_sign_u0 = np.sign(canon_events_u0["target_exposure_A"].to_numpy())
vd_aligned_u0 = canon_events_u0["vote_dispersion"].to_numpy() * change_sign_u0
code_u0 = canon_events_u0["HTF_tilt_state"].to_numpy() * change_sign_u0
VOTE_THRESH = float(np.quantile(vd_aligned_u0, 2.0 / 3.0))
frac_htf_agree = float((code_u0 == 1).mean())
frac_vote_high = float((vd_aligned_u0 >= VOTE_THRESH).mean())
frac_quality_high = float(((code_u0 == 1) | (vd_aligned_u0 >= VOTE_THRESH)).mean())
print(f"[U6B] VOTE_THRESH (top-tercile cutoff of vote_dispersion_aligned, canonical ENTRY+SCALE_IN "
      f"population, n={len(canon_events_u0)}) = {VOTE_THRESH}", flush=True)
print(f"[U6B] base rates on that population: htf_agree_code==1 -> {frac_htf_agree:.4f}, "
      f"vote_dispersion_aligned>=VOTE_THRESH -> {frac_vote_high:.4f}, "
      f"quality==HIGH (union) -> {frac_quality_high:.4f}  (=> quality==LOW -> {1-frac_quality_high:.4f})",
      flush=True)


def product_a_exec_ratelimited(f, tag):
    """f=None reproduces the incumbent exactly (correctness-gate call). f in (0,1) inserts the
    rate limiter at scale-up bars reading quality=='low', per spec.yaml."""
    m_arr = np.where((T != 0) & (tilt_state != 0) & (np.sign(T) == tilt_state), TILTMULT, 1.0)
    s_arr = np.where((T < 0) & (tilt_state > 0), SHORTHALF, 1.0)
    Tpp = np.clip(rha(T * m_arr * s_arr * TILTRESCALE), -13, 13)
    M_a = np.clip(rha(KSOLAR * Tpp + KBMOM * B), -13, 13)

    cash = 0.0; p = 0; pend = 0; prev_eq = 0.0
    contracts_by_sess = {}
    bar_pos = np.zeros(n, dtype=int)
    bar_pnl = np.zeros(n)
    st = dict(n_scaleup=0, n_quality_low=0, n_quality_high_htf=0, n_quality_high_vote=0,
              n_rate_limited=0, n_floor_hit=0, total_contracts=0, n_fills=0)

    for t in range(n):
        if pend != p:
            d = pend - p
            side = 1 if d > 0 else -1
            px = _fill(open_[t], high[t], low[t], side)
            cash -= d * px * PV_MNQ_A
            cash -= abs(d) * COMM_MNQ_A
            contracts_by_sess[sd[t]] = contracts_by_sess.get(sd[t], 0) + abs(d)
            st["total_contracts"] += abs(d); st["n_fills"] += 1
            p = pend
        if last[t] and p != 0:
            side = -1 if p > 0 else 1
            px = _fill(open_[t], high[t], low[t], side, at_close=close[t])
            cash += p * px * PV_MNQ_A
            cash -= abs(p) * COMM_MNQ_A
            contracts_by_sess[sd[t]] = contracts_by_sess.get(sd[t], 0) + abs(p)
            st["total_contracts"] += abs(p); st["n_fills"] += 1
            p = 0; pend = 0
        else:
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
                tgt = tgt_raw

            # ---- rate limiter: only touches scale-up bars (ENTRY p==0->tgt!=0, or SCALE_IN
            # same-sign |tgt|>|p|), exactly PA0's own tgt/C4-gating output above, unchanged for
            # SCALE_DOWN/EXIT/HOLD/FLIP/FLAT ----
            is_scaleup = (tgt != 0) and ((p == 0) or (np.sign(tgt) == np.sign(p) and abs(tgt) > abs(p)))
            if is_scaleup:
                st["n_scaleup"] += 1
                change_sign = np.sign(tgt)
                code = tilt_state[t] * change_sign
                vd_aligned = vote_dispersion[t] * change_sign
                if code == 1:
                    st["n_quality_high_htf"] += 1
                if vd_aligned >= VOTE_THRESH:
                    st["n_quality_high_vote"] += 1
                is_high = (code == 1) or (vd_aligned >= VOTE_THRESH)
                if (f is not None) and (not is_high):
                    st["n_quality_low"] += 1
                    gap = tgt - p
                    naive_step = int(np.floor(f * abs(gap)))
                    step_mag = max(1, naive_step)
                    if naive_step == 0:
                        st["n_floor_hit"] += 1
                    if step_mag < abs(gap):
                        st["n_rate_limited"] += 1
                    tgt = p + int(np.sign(gap)) * step_mag
            pend = tgt
        eq = cash + p * close[t] * PV_MNQ_A
        bar_pnl[t] = eq - prev_eq; prev_eq = eq
        bar_pos[t] = p
        if last[t]:
            contracts_by_sess.setdefault(sd[t], 0)

    dd = pd.DataFrame({"sess": sd, "pnl": bar_pnl}).groupby("sess")["pnl"].sum().reset_index()
    dd.columns = ["sess", "net"]
    dd["contracts"] = dd["sess"].map(contracts_by_sess)
    return dd, bar_pos, bar_pnl, st


def battery_row(tag, dates, net):
    b = dd_battery(pd.to_datetime(dates), net, label=tag)
    return {"tag": tag, "n_days": b["n_days"], "net": b["net"], "sharpe": b["sharpe"],
            "sortino": b["sortino"], "calmar": b["calmar"], "maxDD_eod": b["maxDD_eod"],
            "CDaR95": b["CDaR5"], "worst_day": float(np.min(net)) if len(net) else np.nan,
            "worst_month": b["worst_month"], "pos_day_pct": b["pos_day_pct"]}


# ============================================================= CONTROL (f=None) -- correctness gate
print("[U6B] running CONTROL (f=None, rate limiter disabled) ...", flush=True)
daily_ctrl, barpos_ctrl, bpnl_ctrl, st_ctrl = product_a_exec_ratelimited(None, "CONTROL")
ctrl_net_canon = float(bpnl_ctrl[canon_mask].sum())
assert abs(ctrl_net_canon - 177924.40) < 1.0, f"U6B CONTROL canonical-slice net mismatch: {ctrl_net_canon}"
u0_target_A = u0["target_exposure_A"].to_numpy()
assert (barpos_ctrl == u0_target_A).all(), "U6B CONTROL bar_pos must equal u0_state_table target_exposure_A bar-for-bar"
print(f"[U6B] CORRECTNESS GATE PASSED: CONTROL canonical net = {ctrl_net_canon:.2f} "
      f"(certified $177,924.40); bar-for-bar position match against u0_state_table CONFIRMED.", flush=True)
print(f"[U6B] CONTROL full-window (canonical+extension) net = {bpnl_ctrl.sum():.2f}", flush=True)
print(f"[U6B] CONTROL scale-up bar count = {st_ctrl['n_scaleup']} "
      f"(quality-high-via-htf={st_ctrl['n_quality_high_htf']}, quality-high-via-vote={st_ctrl['n_quality_high_vote']})",
      flush=True)

# ============================================================= grid: f in {0.5, 0.7}
GRID = {"F0.5": 0.5, "F0.7": 0.7}
results = {"CONTROL": (daily_ctrl, barpos_ctrl, bpnl_ctrl, st_ctrl)}
for tag, f in GRID.items():
    print(f"[U6B] running candidate {tag} (f={f}) ...", flush=True)
    daily, barpos, bpnl, st = product_a_exec_ratelimited(f, tag)
    results[tag] = (daily, barpos, bpnl, st)
    print(f"[U6B] {tag}: full-window net={bpnl.sum():.2f}  canonical net={bpnl[canon_mask].sum():.2f}  "
          f"scale-up bars={st['n_scaleup']}  quality-low={st['n_quality_low']}  "
          f"rate-limited (step<full-gap)={st['n_rate_limited']}  floor-hit={st['n_floor_hit']}", flush=True)

# ============================================================= battery: canonical, 2022-2025-only (LOYO), year-by-year
grid_rows = []
year_rows = []
for tag, (daily, barpos, bpnl, st) in results.items():
    d = daily.copy(); d["dt"] = pd.to_datetime(d["sess"])
    canon_d = d[d["dt"] <= CANONICAL_END]
    r2225_d = d[d["dt"] <= pd.Timestamp("2025-12-31")]
    ext_d = d[d["dt"] > CANONICAL_END]

    row_canon = battery_row(f"{tag}_canonical", canon_d["sess"], canon_d["net"].to_numpy())
    row_2225 = battery_row(f"{tag}_2022-2025_LOYO", r2225_d["sess"], r2225_d["net"].to_numpy())
    row_ext = battery_row(f"{tag}_extension_JunJul2026", ext_d["sess"], ext_d["net"].to_numpy())
    for r, scope in ((row_canon, "canonical"), (row_2225, "2022-2025_LOYO"), (row_ext, "extension_JunJul2026_obs")):
        r["candidate"] = tag; r["scope"] = scope
        r["total_contracts"] = st["total_contracts"]; r["n_fills"] = st["n_fills"]
        r["n_scaleup_bars"] = st["n_scaleup"]; r["n_quality_low"] = st["n_quality_low"]
        r["n_rate_limited"] = st["n_rate_limited"]; r["n_floor_hit"] = st["n_floor_hit"]
        grid_rows.append(r)

    for yr in [2022, 2023, 2024, 2025, 2026]:
        yd = d[(d["dt"].dt.year == yr) & (d["dt"] <= CANONICAL_END)]  # canonical-only per year (2026 = Jan-May)
        if len(yd) == 0:
            continue
        yr_row = battery_row(f"{tag}_{yr}", yd["sess"], yd["net"].to_numpy())
        yr_row["candidate"] = tag; yr_row["year"] = yr
        year_rows.append(yr_row)
    daily.to_csv(os.path.join(OUT, f"{tag}_daily.csv"), index=False)

grid_df = pd.DataFrame(grid_rows)
year_df = pd.DataFrame(year_rows)
grid_df.to_csv(os.path.join(OUT, "u6b_grid_battery.csv"), index=False)
year_df.to_csv(os.path.join(OUT, "u6b_year_by_year.csv"), index=False)
print("\n[U6B] ==== GRID BATTERY (canonical / 2022-2025_LOYO / extension) ====")
print(grid_df[["candidate", "scope", "net", "sharpe", "sortino", "calmar", "maxDD_eod", "CDaR95",
                "worst_day", "worst_month", "pos_day_pct", "total_contracts", "n_fills"]].to_string(index=False))
print("\n[U6B] ==== YEAR BY YEAR (canonical only) ====")
print(year_df[["candidate", "year", "net", "sharpe", "maxDD_eod", "pos_day_pct"]].to_string(index=False))

# ============================================================= right-tail check (U6's own top/bottom-20 canonical blocks)
print("\n[U6B] ==== right-tail check on U6's published top-20 / bottom-20 canonical blocks ====", flush=True)
U6_TOP = pd.read_csv(os.path.join(ROOT, "runs", "U6_PRODUCT_A_PATH_DEPENDENCE", "out", "step3_top20_blocks.csv"))
U6_BOT = pd.read_csv(os.path.join(ROOT, "runs", "U6_PRODUCT_A_PATH_DEPENDENCE", "out", "step3_bottom20_blocks.csv"))

# pre-construction overlap diagnostic: under CONTROL's own path, what fraction of each block's
# own scale-up bars would read quality=='low' under this rule?
u0_action_A = u0["action_A"].to_numpy()
u0_tgt_A = u0["target_exposure_A"].to_numpy()
u0_htf = u0["HTF_tilt_state"].to_numpy()
u0_vd = u0["vote_dispersion"].to_numpy()
is_scaleup_u0 = np.isin(u0_action_A, ["ENTRY", "SCALE_IN"])
change_sign_full = np.where(is_scaleup_u0, np.sign(u0_tgt_A), 0)
code_full = u0_htf * change_sign_full
vd_aligned_full = u0_vd * change_sign_full
quality_low_full = is_scaleup_u0 & ~((code_full == 1) | (vd_aligned_full >= VOTE_THRESH))


def block_overlap_and_damage(blocks_df, label):
    rows = []
    for _, b in blocks_df.iterrows():
        t0, t1 = int(b["t_idx_start"]), int(b["t_idx_end"])
        sl = slice(t0, t1 + 1)
        n_scaleup_blk = int(is_scaleup_u0[sl].sum())
        n_qlow_blk = int(quality_low_full[sl].sum())
        ctrl_window_pnl = float(results["CONTROL"][2][sl].sum())
        row = {"block_id_A": b["block_id_A"], "start_sess_date": b["start_sess_date"],
               "net_pnl_control_block": b["net_pnl"], "ctrl_window_pnl_check": ctrl_window_pnl,
               "n_scaleup_bars_in_block": n_scaleup_blk, "n_quality_low_in_block": n_qlow_blk,
               "frac_quality_low_in_block": (n_qlow_blk / n_scaleup_blk) if n_scaleup_blk > 0 else np.nan}
        for tag, f in GRID.items():
            cand_window_pnl = float(results[tag][2][sl].sum())
            row[f"{tag}_window_pnl"] = cand_window_pnl
            row[f"{tag}_window_delta"] = cand_window_pnl - ctrl_window_pnl
        rows.append(row)
    out_df = pd.DataFrame(rows)
    out_df.to_csv(os.path.join(OUT, f"u6b_righttail_{label}.csv"), index=False)
    print(f"\n[U6B] {label} (n={len(out_df)}): mean frac_quality_low_in_block = "
          f"{out_df['frac_quality_low_in_block'].mean():.3f}", flush=True)
    for tag in GRID:
        tot_delta = out_df[f"{tag}_window_delta"].sum()
        n_damaged = (out_df[f"{tag}_window_delta"] < -1.0).sum()
        n_improved = (out_df[f"{tag}_window_delta"] > 1.0).sum()
        print(f"    {tag}: sum(window_delta) = {tot_delta:+.2f}  "
              f"(blocks damaged={n_damaged}, improved={n_improved}, unchanged={len(out_df)-n_damaged-n_improved})",
              flush=True)
    return out_df


top20_rt = block_overlap_and_damage(U6_TOP, "top20_winners")
bot20_rt = block_overlap_and_damage(U6_BOT, "bottom20_losers")

# ============================================================= summary json
summary = {
    "correctness_gate": {"ctrl_net_canonical": ctrl_net_canon, "certified": 177924.40,
                          "bar_for_bar_position_match_vs_u0": True},
    "VOTE_THRESH": VOTE_THRESH,
    "quality_base_rates_canonical_ENTRY_SCALE_IN_population": {
        "n_events": int(len(canon_events_u0)), "frac_htf_agree": frac_htf_agree,
        "frac_vote_high": frac_vote_high, "frac_quality_high": frac_quality_high,
        "frac_quality_low": 1 - frac_quality_high},
    "candidate_stats": {tag: results[tag][3] for tag in results},
    "full_window_net": {tag: float(results[tag][2].sum()) for tag in results},
    "canonical_net": {tag: float(results[tag][2][canon_mask].sum()) for tag in results},
    "delta_2022_2025_vs_control": {
        tag: float(results[tag][2][r2225_mask].sum() - results["CONTROL"][2][r2225_mask].sum())
        for tag in GRID},
    "top20_winners_total_window_delta": {tag: float(top20_rt[f"{tag}_window_delta"].sum()) for tag in GRID},
    "bottom20_losers_total_window_delta": {tag: float(bot20_rt[f"{tag}_window_delta"].sum()) for tag in GRID},
}
with open(os.path.join(OUT, "u6b_summary.json"), "w") as fh:
    json.dump(summary, fh, indent=2, default=float)
print("\n[U6B] SUMMARY:")
print(json.dumps(summary, indent=2, default=float))
print("\n[U6B] construction + validation complete.")
