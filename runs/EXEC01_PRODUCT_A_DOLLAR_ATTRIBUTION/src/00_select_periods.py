"""EXEC01 -- Product A period selection for leg-by-leg dollar-attribution reconciliation.

Selection is computed ENTIRELY from the Python-side decision/target-exposure and mark-to-market
PnL series (never from where NT8 vs Python happen to disagree) -- see 00_period_selection.md for
the full disclosure. This script:

  1. Reuses (imports, does not re-derive) the already-certified Product-A decision layer via
     runs/SA0_SYSTEM_STRUCTURE/current_health/src/health_substrate.py (HS), which reproduces the
     certified canonical net exactly on import (its own internal assert). This is the SAME
     substrate runs/PRICE01_PRODUCT_A_GENUINE_MNQ/src/01_dual_truth_repricing.py imports.
  2. Re-implements product_a_exec_generalized as a byte-for-byte copy of the PRICE01 version
     (docstring there: "Verbatim-formula copy of pa0_substrate.product_a_exec / U0's
     product_a_exec_generalized") -- copied rather than imported because PRICE01's own module has
     unguarded top-level file-writes into runs/PRICE01_PRODUCT_A_GENUINE_MNQ/out/, and this task's
     governance constraints forbid writing into that read-only directory. The decision-layer
     formula itself is NOT re-derived, only copy-pasted verbatim from the file named in the task
     brief.
  3. Computes per-bar target exposure (bar_pos, contracts, MNQ units, clipped +/-13) and per-bar
     mark-to-market PnL (bar_pnl) for the full canonical window 2022-01-03 .. 2026-05-29 (the
     window already fully covered by real, already-run NT8 output per
     runs/V1R4_NT8_PARITY/out/chunks/A_E1..E7_trades.json).
  4. Aggregates to per-session (day) statistics: net PnL, max |position|, turnover (sum of
     |bar-to-bar position changes|, in contracts), n scale-in events, n scale-down events, n
     reversal events (bar-to-bar sign flip while both sides nonzero).
  5. Cross-references the CME early-close calendar already computed in
     runs/W17_C4_COMPLIANCE/out/v1d_session_calendar.csv (44 early-close sessions in-window).
  6. Writes out/day_stats.csv (full per-day table, for audit) and prints the extremes used to
     drive the written-up selection in out/00_period_selection.md.

Read-only w.r.t. runs/V1R4_NT8_PARITY/ and runs/PRICE01_PRODUCT_A_GENUINE_MNQ/ -- only reads from
those paths, writes only under this run's own out/ directory.
"""
import os, sys
import numpy as np, pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
sys.path.insert(0, os.path.join(ROOT, "runs", "W18R1_M1_VOLSEASON", "src"))
sys.path.insert(0, os.path.join(ROOT, "runs", "SA0_SYSTEM_STRUCTURE", "current_health", "src"))

OUT = os.path.join(ROOT, "runs", "EXEC01_PRODUCT_A_DOLLAR_ATTRIBUTION", "out")
os.makedirs(OUT, exist_ok=True)

import health_substrate as HS  # read-only import; no file writes in this module (verified by inspection)

bars = HS.bars
n = HS.n
close, open_, high, low = HS.close, HS.open_, HS.high, HS.low
last = HS.last
T, tilt_state, B = HS.T, HS.tilt_state, HS.B
entry_blocked_c4, forced_flat_c4 = HS.entry_blocked_c4, HS.forced_flat_c4
sd = bars["sess_date"].to_numpy()
CANONICAL_END = HS.CANONICAL_END
_fill = HS._fill

KSOLAR, KBMOM, TILTRESCALE, TILTMULT, SHORTHALF = 0.728654, 2.934159, 0.9026, 1.25, 0.5
PV_MNQ_A, COMM_MNQ_A = 2.0, 0.65


def rha(x):
    return np.sign(x) * np.floor(np.abs(x) + 0.5)


def product_a_exec_generalized(T_leg, tilt_state_, B_, entry_blocked_, forced_flat_,
                                o, h, l, c, last_, sd_, n_):
    """Verbatim copy of runs/PRICE01_PRODUCT_A_GENUINE_MNQ/src/01_dual_truth_repricing.py's
    product_a_exec_generalized -- NOT re-derived. Only the price arrays vary between callers;
    the decision layer (m_arr/s_arr/Tpp/M_a) depends solely on T_leg/tilt_state_/B_."""
    m_arr = np.where((T_leg != 0) & (tilt_state_ != 0) & (np.sign(T_leg) == tilt_state_), TILTMULT, 1.0)
    s_arr = np.where((T_leg < 0) & (tilt_state_ > 0), SHORTHALF, 1.0)
    Tpp = np.clip(rha(T_leg * m_arr * s_arr * TILTRESCALE), -13, 13)
    M_a = np.clip(rha(KSOLAR * Tpp + KBMOM * B_), -13, 13)

    cash = 0.0; p = 0; pend = 0; prev_eq = 0.0
    bar_pos = np.zeros(n_, dtype=int)
    bar_pnl = np.zeros(n_)
    for t in range(n_):
        if pend != p:
            d = pend - p
            side = 1 if d > 0 else -1
            px = _fill(o[t], h[t], l[t], side)
            cash -= d * px * PV_MNQ_A
            cash -= abs(d) * COMM_MNQ_A
            p = pend
        if last_[t] and p != 0:
            side = -1 if p > 0 else 1
            px = _fill(o[t], h[t], l[t], side, at_close=c[t])
            cash += p * px * PV_MNQ_A
            cash -= abs(p) * COMM_MNQ_A
            p = 0; pend = 0
        else:
            tgt_raw = int(M_a[t])
            if forced_flat_[t]:
                tgt = 0
            elif entry_blocked_[t]:
                if tgt_raw == 0 or p == 0:
                    tgt = 0
                elif np.sign(tgt_raw) != np.sign(p):
                    tgt = 0
                else:
                    tgt = p if abs(tgt_raw) > abs(p) else tgt_raw
            else:
                tgt = tgt_raw
            pend = tgt
        eq = cash + p * c[t] * PV_MNQ_A
        bar_pnl[t] = eq - prev_eq; prev_eq = eq
        bar_pos[t] = p
    return bar_pos, bar_pnl, M_a


print("[EXEC01] running Product A decision layer (legacy NQ-price fills, matches certified $177,924.40) ...", flush=True)
bar_pos, bar_pnl, M_a = product_a_exec_generalized(
    T, tilt_state, B, entry_blocked_c4, forced_flat_c4, open_, high, low, close, last, sd, n)

sd_dt = pd.to_datetime(pd.Series(sd))
canon_mask = (sd_dt <= CANONICAL_END).to_numpy()
net_canon = float(bar_pnl[canon_mask].sum())
assert abs(net_canon - 177924.40) < 1.0, f"EXEC01 correctness gate FAILED: {net_canon}"
print(f"[EXEC01] correctness gate PASS: canonical net == certified $177,924.40 (got {net_canon:.2f})", flush=True)

# ---------------------------------------------------------------- restrict to canonical window only
# (the window already fully covered by already-run NT8 chunk output, A_E1..E7)
sd_c = sd[canon_mask]
pos_c = bar_pos[canon_mask]
pnl_c = bar_pnl[canon_mask]
n_c = len(sd_c)

# bar-to-bar position delta WITHIN this masked (canonical) array; note this is a light approximation
# at the single seam bar between the last pre-canonical bar and the first canonical bar (immaterial:
# position is 0 at every session's last bar by construction, and canon_mask is session-aligned, so
# the seam bar is itself a fresh session's first bar with prev-session position already flattened).
delta = np.diff(pos_c, prepend=pos_c[0])
delta[0] = pos_c[0]  # first bar's "change" is just entering pos_c[0] from flat (or already flat)

turnover_contracts = np.abs(delta)
is_scale_in = (np.sign(delta) != 0) & (np.sign(pos_c) == np.sign(pos_c - delta)) & (pos_c - delta != 0) & (np.abs(pos_c) > np.abs(pos_c - delta))
is_scale_down = (np.sign(delta) != 0) & (np.sign(pos_c) == np.sign(pos_c - delta)) & (pos_c != 0) & (np.abs(pos_c) < np.abs(pos_c - delta))
is_reversal = (pos_c - delta != 0) & (pos_c != 0) & (np.sign(pos_c) != np.sign(pos_c - delta))

df = pd.DataFrame({
    "sess": sd_c, "pos": pos_c, "pnl": pnl_c, "turnover": turnover_contracts,
    "scale_in": is_scale_in.astype(int), "scale_down": is_scale_down.astype(int),
    "reversal": is_reversal.astype(int),
})

day = df.groupby("sess").agg(
    net_pnl=("pnl", "sum"),
    max_abs_pos=("pos", lambda s: int(np.abs(s).max())),
    turnover_contracts=("turnover", "sum"),
    n_scale_in=("scale_in", "sum"),
    n_scale_down=("scale_down", "sum"),
    n_reversal=("reversal", "sum"),
    n_bars=("pos", "size"),
).reset_index()
day["sess"] = pd.to_datetime(day["sess"])
day = day.sort_values("sess").reset_index(drop=True)

# ---------------------------------------------------------------- early-close calendar cross-reference
cal = pd.read_csv(os.path.join(ROOT, "runs", "W17_C4_COMPLIANCE", "out", "v1d_session_calendar.csv"))
cal["sopen"] = pd.to_datetime(cal["sopen"])
cal["sclose"] = pd.to_datetime(cal["sclose"])
cal["sess_date"] = cal["sclose"].dt.normalize()  # sclose's own date is the session's sess_date convention used elsewhere in this campaign
early = cal[cal["nbars"] < 400].copy()
day["is_early_close"] = day["sess"].isin(early["sess_date"])

day.to_csv(os.path.join(OUT, "day_stats.csv"), index=False)
print(f"[EXEC01] wrote {os.path.join(OUT, 'day_stats.csv')}  ({len(day)} sessions)", flush=True)

# ---------------------------------------------------------------- print the extremes
pd.set_option("display.width", 160)
print("\n=== top 10 winning days (Python mark-to-market) ===")
print(day.sort_values("net_pnl", ascending=False).head(10)[["sess", "net_pnl", "max_abs_pos", "turnover_contracts", "n_reversal", "is_early_close"]].to_string(index=False))

print("\n=== top 10 losing days (Python mark-to-market) ===")
print(day.sort_values("net_pnl").head(10)[["sess", "net_pnl", "max_abs_pos", "turnover_contracts", "n_reversal", "is_early_close"]].to_string(index=False))

print("\n=== top 10 highest-turnover days ===")
print(day.sort_values("turnover_contracts", ascending=False).head(10)[["sess", "net_pnl", "max_abs_pos", "turnover_contracts", "n_reversal", "is_early_close"]].to_string(index=False))

print("\n=== top 10 highest max|position| days ===")
print(day.sort_values("max_abs_pos", ascending=False).head(10)[["sess", "net_pnl", "max_abs_pos", "turnover_contracts", "n_reversal", "is_early_close"]].to_string(index=False))

print("\n=== top 10 most-reversal days ===")
print(day.sort_values("n_reversal", ascending=False).head(10)[["sess", "net_pnl", "max_abs_pos", "turnover_contracts", "n_reversal", "n_scale_in", "n_scale_down", "is_early_close"]].to_string(index=False))

print("\n=== top 10 most scale-in days ===")
print(day.sort_values("n_scale_in", ascending=False).head(10)[["sess", "net_pnl", "max_abs_pos", "turnover_contracts", "n_scale_in", "is_early_close"]].to_string(index=False))

print("\n=== top 10 most scale-down days ===")
print(day.sort_values("n_scale_down", ascending=False).head(10)[["sess", "net_pnl", "max_abs_pos", "turnover_contracts", "n_scale_down", "is_early_close"]].to_string(index=False))

print("\n=== early-close sessions, sorted by |net_pnl| desc (top 15) ===")
ec = day[day["is_early_close"]].copy()
ec["abs_net"] = ec["net_pnl"].abs()
print(ec.sort_values("abs_net", ascending=False).head(15)[["sess", "net_pnl", "max_abs_pos", "turnover_contracts", "n_reversal", "n_scale_in", "n_scale_down"]].to_string(index=False))

print(f"\n[EXEC01] n_early_close_sessions_in_canonical_window={int(day['is_early_close'].sum())}")
print(f"[EXEC01] canonical window: {day['sess'].min().date()} .. {day['sess'].max().date()}, n_sessions={len(day)}")

# window flags for periods already covered by the RICH detailed job (producta_v4_2024apr_2025mar.json)
rich_start, rich_end = pd.Timestamp("2024-04-01"), pd.Timestamp("2025-03-31")
day["in_rich_window"] = (day["sess"] >= rich_start) & (day["sess"] <= rich_end)
day.to_csv(os.path.join(OUT, "day_stats.csv"), index=False)  # rewrite with in_rich_window column

print("\n=== of the extremes above, how many fall inside the RICH (Apr2024-Mar2025, quantity-level) window? ===")
for label, sub in [
    ("top5 winning", day.sort_values("net_pnl", ascending=False).head(5)),
    ("top5 losing", day.sort_values("net_pnl").head(5)),
    ("top5 turnover", day.sort_values("turnover_contracts", ascending=False).head(5)),
    ("top5 max|pos|", day.sort_values("max_abs_pos", ascending=False).head(5)),
    ("top5 reversal", day.sort_values("n_reversal", ascending=False).head(5)),
]:
    print(label, "-> n_in_rich_window =", int(sub["in_rich_window"].sum()), list(sub["sess"].dt.date))

print("\n[EXEC01] done.")
