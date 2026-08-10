"""W5_PROTECTED_CONFIRMATION Family 2, step_c (constructed net/Sharpe/maxDD delta, tick-covered
dates only) + step_d (right-tail check vs U6's own top20/bottom20 canonical Product-A blocks) +
falsification_condition (e) (quality_low_auction realized rate vs 2x drift band).

Mechanism is BYTE-IDENTICAL IN SHAPE to runs/U6B_PRODUCT_A_SCALE_RATE/src/01_construct_and_validate.py's
product_a_exec_ratelimited (same KSOLAR/KBMOM/TILTRESCALE/TILTMULT/SHORTHALF, same rha(), same
Tpp/M_a target generation, same C4 forced-flat/entry-blocked gating, same fill mechanics, same
minimum-step-of-1 floor), with ONLY the trigger condition swapped per
runs/AUCTION02_ACTION_RELEVANCE/spec.yaml's own construction: quality_low_auction = (RTH+liquid
domain) AND (|value_dist_ticks| >= CUT_FAR_TICKS), CUT_FAR_TICKS=315.3333333333333 reused VERBATIM
(never recomputed on the confirmation pool). domain is restricted, by construction, to the 8
confirmation-pool sessions' RTH+liquid bars (the ONLY bars where value_dist_ticks exists in this
run) -- on every other bar in Product A's ~2022-2026 history, quality_low_auction=FALSE by
definition (fail-safe default = unrestricted = CONTROL behavior), exactly per spec.yaml's
domain_restriction clause.
"""
import os, sys, json
import numpy as np, pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
sys.path.insert(0, os.path.join(ROOT, "runs", "W18R1_M1_VOLSEASON", "src"))
sys.path.insert(0, os.path.join(ROOT, "runs", "SA0_SYSTEM_STRUCTURE", "current_health", "src"))
from sm01_solarsim import _fill
from smv2_common import dd_battery
import health_substrate as HS

OUT = os.path.join(ROOT, "runs", "W5_PROTECTED_CONFIRMATION", "results", "out")
U0_PATH = os.path.join(ROOT, "runs", "U0_UNIFIED_STATE", "out", "u0_state_table.parquet")
POC_PATH = os.path.join(OUT, "poc_1s_full_CONFIRM.parquet")

CUT_FAR_TICKS = 315.3333333333333  # FROZEN, reused verbatim, never recomputed
CONFIRMATION_DATES = {"20250819", "20250912", "20251028", "20251125",
                       "20260217", "20260302", "20260422", "20260512"}
for d in CONFIRMATION_DATES:
    assert d < "20260801", "date-firewall violation"

KSOLAR, KBMOM, TILTRESCALE, TILTMULT, SHORTHALF = 0.728654, 2.934159, 0.9026, 1.25, 0.5
PV_MNQ_A, COMM_MNQ_A = 2.0, 0.65

n = HS.n
open_, high, low, close = HS.open_, HS.high, HS.low, HS.close
last = HS.last
sd = HS.sess_arr
T, B, tilt_state = HS.T, np.asarray(HS.B), HS.tilt_state
entry_blocked_c4, forced_flat_c4 = HS.entry_blocked_c4, HS.forced_flat_c4
PEND = HS.PEND
CANONICAL_END = HS.CANONICAL_END
bar_time = pd.to_datetime(HS.bars["time"]).to_numpy()
print(f"[step_cd] n={n} bars, CANONICAL_END={CANONICAL_END}", flush=True)


def rha(x):
    return np.sign(x) * np.floor(np.abs(x) + 0.5)


# ============================================================= build the full-length,
# domain-restricted quality_low_auction array by merge_asof(backward, tol=2s) of the
# confirmation-pool causal 1s POC layer onto HS's own 3-min bar timestamps.
poc = pd.read_parquet(POC_PATH, columns=["time", "sess_tag", "value_dist_ticks", "bid_upd", "ask_upd"])
poc = poc.sort_values("time").reset_index(drop=True)
poc["bbo_upd"] = poc["bid_upd"].fillna(0) + poc["ask_upd"].fillna(0)
poc["liq60"] = poc.groupby("sess_tag")["bbo_upd"].transform(lambda s: s.rolling(60, min_periods=1).sum())

bars_df = pd.DataFrame({"time": bar_time, "t_idx": np.arange(n)}).sort_values("time")
merged = pd.merge_asof(bars_df, poc[["time", "value_dist_ticks", "liq60"]],
                        on="time", direction="backward", tolerance=pd.Timedelta("2s"))
merged = merged.sort_values("t_idx").reset_index(drop=True)
assert (merged["t_idx"].to_numpy() == np.arange(n)).all()

value_dist_full = merged["value_dist_ticks"].to_numpy()
liq60_full = merged["liq60"].to_numpy()
matched_full = ~np.isnan(value_dist_full)

hm_full = pd.DatetimeIndex(bar_time)
tod = hm_full.time
rth_full = (tod >= pd.Timestamp("09:30:00").time()) & (tod < pd.Timestamp("16:00:00").time())
liquid_full = np.nan_to_num(liq60_full, nan=0.0) > 0
domain_restricted_full = matched_full & rth_full & liquid_full
quality_low_auction_full = domain_restricted_full & (np.abs(value_dist_full) >= CUT_FAR_TICKS)

n_matched = int(matched_full.sum())
n_domain = int(domain_restricted_full.sum())
n_qlow = int(quality_low_auction_full.sum())
print(f"[step_cd] bars matched to confirmation-pool tick data (any, incl. non-RTH/illiquid): {n_matched}", flush=True)
print(f"[step_cd] bars in RTH+liquid domain on confirmation-pool dates: {n_domain}", flush=True)
print(f"[step_cd] bars with quality_low_auction==TRUE (domain AND |value_dist|>=CUT_FAR_TICKS): {n_qlow}", flush=True)

# sanity: confirm the matched bars land only on the 8 authorized SESSIONS (governance check).
# Uses sd (health_substrate's own per-bar SESSION date label, sess 18:00->17:00 ET per this
# campaign's standing convention -- NOT the raw bar timestamp's calendar date, which for evening
# bars is one calendar day earlier than the session tag) -- matches CLAUDE.md's own restatement
# of this convention exactly.
sd_str = np.array([d.strftime("%Y%m%d") for d in sd])
matched_sessions = set(sd_str[matched_full])
assert matched_sessions <= CONFIRMATION_DATES, f"UNEXPECTED session(s) matched: {matched_sessions - CONFIRMATION_DATES}"
print(f"[step_cd] governance check PASSED: matched bars land only on sessions {sorted(matched_sessions)} "
      f"(subset of the 8 authorized confirmation dates)", flush=True)
# recompute tick_covered_mask on SESSION date too (used later for step_c date restriction)
tick_covered_mask = np.isin(sd_str, list(CONFIRMATION_DATES))


def product_a_exec_ratelimited_auction(f, tag):
    """BYTE-IDENTICAL IN SHAPE to U6B's product_a_exec_ratelimited; trigger swapped from
    HTF/vote-based quality_low to quality_low_auction_full (value_dist_ticks-based, domain-gated).
    f=None reproduces the incumbent exactly (correctness-gate call)."""
    m_arr = np.where((T != 0) & (tilt_state != 0) & (np.sign(T) == tilt_state), TILTMULT, 1.0)
    s_arr = np.where((T < 0) & (tilt_state > 0), SHORTHALF, 1.0)
    Tpp = np.clip(rha(T * m_arr * s_arr * TILTRESCALE), -13, 13)
    M_a = np.clip(rha(KSOLAR * Tpp + KBMOM * B), -13, 13)

    cash = 0.0; p = 0; pend = 0; prev_eq = 0.0
    contracts_by_sess = {}
    bar_pos = np.zeros(n, dtype=int)
    bar_pnl = np.zeros(n)
    st = dict(n_scaleup=0, n_scaleup_in_domain=0, n_quality_low=0,
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

            is_scaleup = (tgt != 0) and ((p == 0) or (np.sign(tgt) == np.sign(p) and abs(tgt) > abs(p)))
            if is_scaleup:
                st["n_scaleup"] += 1
                if domain_restricted_full[t]:
                    st["n_scaleup_in_domain"] += 1
                is_low = bool(quality_low_auction_full[t])
                if is_low:
                    st["n_quality_low"] += 1
                if (f is not None) and is_low:
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


# ============================================================= CONTROL correctness gate
print("[step_cd] running CONTROL (f=None) ...", flush=True)
daily_ctrl, barpos_ctrl, bpnl_ctrl, st_ctrl = product_a_exec_ratelimited_auction(None, "CONTROL")
sess_dt = pd.to_datetime(pd.Series(sd))
canon_mask = (sess_dt <= CANONICAL_END).to_numpy()
ctrl_net_canon = float(bpnl_ctrl[canon_mask].sum())
assert abs(ctrl_net_canon - 177924.40) < 1.0, f"CORRECTNESS GATE FAILED: CONTROL canonical net {ctrl_net_canon}"
u0 = pd.read_parquet(U0_PATH, columns=["target_exposure_A"])
u0_target_A = u0["target_exposure_A"].to_numpy()
assert (barpos_ctrl == u0_target_A).all(), "CONTROL bar_pos must equal u0_state_table target_exposure_A bar-for-bar"
print(f"[step_cd] CORRECTNESS GATE PASSED: CONTROL canonical net={ctrl_net_canon:.2f} (certified $177,924.40); "
      f"bar-for-bar position match against u0_state_table CONFIRMED.", flush=True)

GRID = {"F0.5": 0.5, "F0.7": 0.7}
results = {"CONTROL": (daily_ctrl, barpos_ctrl, bpnl_ctrl, st_ctrl)}
for tag, f in GRID.items():
    print(f"[step_cd] running candidate {tag} (f={f}) ...", flush=True)
    daily, barpos, bpnl, st = product_a_exec_ratelimited_auction(f, tag)
    results[tag] = (daily, barpos, bpnl, st)
    print(f"[step_cd] {tag}: scale-up bars={st['n_scaleup']} in-domain={st['n_scaleup_in_domain']} "
          f"quality-low={st['n_quality_low']} rate-limited={st['n_rate_limited']} floor-hit={st['n_floor_hit']}",
          flush=True)

# ============================================================= step_c: delta restricted to the
# 8 confirmation-pool tick-covered SESSIONS only (per this bundle's explicit interpretation of
# spec.yaml's "tick-covered dates" scope for a confirmation-only pass -- see report for the
# disclosed interpretation note). tick_covered_mask (by SESSION date, sd_str) computed above.
n_tick_bars = int(tick_covered_mask.sum())
print(f"\n[step_cd] tick-covered-date bars (8 confirmation sessions, ALL bars not just RTH/liquid): {n_tick_bars}", flush=True)

step_c = {}
for tag in ["CONTROL"] + list(GRID.keys()):
    daily, barpos, bpnl, st = results[tag]
    net_restricted = float(bpnl[tick_covered_mask].sum())
    step_c[tag] = {"net_over_tick_covered_dates": net_restricted,
                    "n_bars": n_tick_bars, "stats": st}
    print(f"[step_cd] {tag}: net over 8 tick-covered dates = {net_restricted:+.2f}", flush=True)

ctrl_net_restricted = step_c["CONTROL"]["net_over_tick_covered_dates"]
for tag in GRID:
    cand_net = step_c[tag]["net_over_tick_covered_dates"]
    delta = cand_net - ctrl_net_restricted
    wash_thresh = 0.01 * abs(ctrl_net_restricted)
    step_c[tag]["delta_vs_control"] = delta
    step_c[tag]["is_wash_or_negative"] = bool(delta < wash_thresh)
    print(f"[step_cd] {tag} delta vs CONTROL (tick-covered dates only) = {delta:+.2f} "
          f"(1%-of-CONTROL wash threshold = {wash_thresh:+.2f}) "
          f"-> {'WASH/NEGATIVE (falsification a TRIGGERED)' if delta < wash_thresh else 'clears wash threshold'}",
          flush=True)

# ---- per-session battery (Sharpe/maxDD only meaningful with >1 day; reported descriptively,
# 8 sessions is far too few for a stable Sharpe/DD estimate -- disclosed, not hidden) ----
per_sess_rows = []
for tag in ["CONTROL"] + list(GRID.keys()):
    daily, barpos, bpnl, st = results[tag]
    d = daily.copy(); d["dt"] = pd.to_datetime(d["sess"])
    d8 = d[d["dt"].dt.strftime("%Y%m%d").isin(CONFIRMATION_DATES)].sort_values("dt")
    for _, row in d8.iterrows():
        per_sess_rows.append({"candidate": tag, "sess": row["sess"], "net": row["net"], "contracts": row["contracts"]})
per_sess_df = pd.DataFrame(per_sess_rows)
per_sess_df.to_csv(os.path.join(OUT, "step_c_per_session_CONFIRM.csv"), index=False)
print("\n[step_cd] per-session net (8 confirmation dates):")
print(per_sess_df.pivot(index="sess", columns="candidate", values="net").to_string())

# turnover delta
for tag in GRID:
    dctrl = per_sess_df[per_sess_df.candidate == "CONTROL"]["contracts"].sum()
    dcand = per_sess_df[per_sess_df.candidate == tag]["contracts"].sum()
    step_c[tag]["total_contracts_control"] = float(dctrl)
    step_c[tag]["total_contracts_candidate"] = float(dcand)
    step_c[tag]["contracts_delta"] = float(dcand - dctrl)
    step_c[tag]["commission_delta"] = float((dcand - dctrl) * COMM_MNQ_A)
    print(f"[step_cd] {tag}: contracts delta (8 dates) = {dcand-dctrl:+.0f}, "
          f"commission delta = {(dcand-dctrl)*COMM_MNQ_A:+.2f}", flush=True)

# ============================================================= falsification condition (e):
# quality_low_auction realized rate on the pool vs discovery's 33.3% (tercile construction),
# by more than 2x (<16.7% or >66.7%)
scaleup_in_domain = st_ctrl["n_scaleup_in_domain"]
qlow_rate = (st_ctrl["n_quality_low"] / scaleup_in_domain) if scaleup_in_domain > 0 else float("nan")
print(f"\n[step_cd] falsification (e) check: quality_low_auction rate among in-domain scale-up bars "
      f"= {qlow_rate:.4f} ({st_ctrl['n_quality_low']}/{scaleup_in_domain}) vs discovery's 33.3% "
      f"tercile-construction rate. 2x band = [16.7%, 66.7%].", flush=True)
falsif_e_triggered = (scaleup_in_domain > 0) and (qlow_rate < 0.167 or qlow_rate > 0.667)
if scaleup_in_domain == 0:
    print("[step_cd] falsification (e): N/A -- zero scale-up bars fall in the RTH+liquid domain on "
          "the 8 confirmation dates (data-limited, not evaluable).", flush=True)

# ============================================================= step_d: right-tail check
print("\n[step_cd] ==== step_d: right-tail check vs U6's published top20/bottom20 blocks ====", flush=True)
U6_TOP = pd.read_csv(os.path.join(ROOT, "runs", "U6_PRODUCT_A_PATH_DEPENDENCE", "out", "step3_top20_blocks.csv"))
U6_BOT = pd.read_csv(os.path.join(ROOT, "runs", "U6_PRODUCT_A_PATH_DEPENDENCE", "out", "step3_bottom20_blocks.csv"))
U6_TOP["start_sess_date"] = pd.to_datetime(U6_TOP["start_sess_date"])
U6_BOT["start_sess_date"] = pd.to_datetime(U6_BOT["start_sess_date"])
conf_dates_ts = pd.to_datetime(sorted(CONFIRMATION_DATES), format="%Y%m%d")

top_overlap = U6_TOP[U6_TOP["start_sess_date"].isin(conf_dates_ts)]
bot_overlap = U6_BOT[U6_BOT["start_sess_date"].isin(conf_dates_ts)]
print(f"[step_cd] top20 blocks intersecting the 8 confirmation dates: {len(top_overlap)}", flush=True)
print(f"[step_cd] bottom20 blocks intersecting the 8 confirmation dates: {len(bot_overlap)}", flush=True)

step_d_rows = []
if len(top_overlap) == 0 and len(bot_overlap) == 0:
    print("[step_cd] step_d: N/A -- no top20/bottom20 block intersects the 8 confirmation dates "
          "(reported explicitly per spec.yaml's own instruction not to fabricate a check).", flush=True)
else:
    for label, block_set in [("top20_winner", top_overlap), ("bottom20_loser", bot_overlap)]:
        for _, b in block_set.iterrows():
            t0, t1 = int(b["t_idx_start"]), int(b["t_idx_end"])
            sl = slice(t0, t1 + 1)
            ctrl_window_pnl = float(bpnl_ctrl[sl].sum())
            row = {"label": label, "block_id_A": b["block_id_A"], "start_sess_date": str(b["start_sess_date"].date()),
                   "net_pnl_control_block_U6_published": b["net_pnl"], "ctrl_window_pnl_recomputed": ctrl_window_pnl}
            for tag, f in GRID.items():
                cand_window_pnl = float(results[tag][2][sl].sum())
                row[f"{tag}_window_pnl"] = cand_window_pnl
                row[f"{tag}_window_delta"] = cand_window_pnl - ctrl_window_pnl
            step_d_rows.append(row)
            print(f"[step_cd] {label} block {b['block_id_A']} ({b['start_sess_date'].date()}): "
                  f"CONTROL window pnl={ctrl_window_pnl:+.2f} " +
                  " ".join(f"{tag}_delta={row[f'{tag}_window_delta']:+.2f}" for tag in GRID), flush=True)
    step_d_df = pd.DataFrame(step_d_rows)
    step_d_df.to_csv(os.path.join(OUT, "step_d_righttail_CONFIRM.csv"), index=False)

# ============================================================= summary
summary = {
    "correctness_gate": {"ctrl_net_canonical": ctrl_net_canon, "certified": 177924.40, "bar_for_bar_match": True},
    "CUT_FAR_TICKS_reused_verbatim": CUT_FAR_TICKS,
    "n_bars_matched_to_confirmation_tick_data": n_matched,
    "n_bars_rth_liquid_domain_confirmation_dates": n_domain,
    "n_bars_quality_low_auction": n_qlow,
    "step_c": {k: v for k, v in step_c.items()},
    "falsification_e": {"scaleup_in_domain": int(scaleup_in_domain), "n_quality_low": int(st_ctrl["n_quality_low"]),
                         "rate": (float(qlow_rate) if scaleup_in_domain > 0 else None),
                         "triggered": (bool(falsif_e_triggered) if scaleup_in_domain > 0 else None)},
    "step_d_n_blocks_overlap": {"top20": int(len(top_overlap)), "bottom20": int(len(bot_overlap))},
}
with open(os.path.join(OUT, "step_c_d_summary_CONFIRM.json"), "w") as fh:
    json.dump(summary, fh, indent=2, default=float)
print("\nSTEP_C_D_CONFIRM DONE")
