"""U6B risk_panel Part 3 substrate -- bar-level (3-min) equity construction under GENUINE MNQ
pricing, for CONTROL/F0.5/F0.7. This is a RE-INSTRUMENTATION of
runs/U6B_PRODUCT_A_SCALE_RATE/src/02_genuine_mnq_repricing.py's own product_a_exec_ratelimited
decision loop -- the decision logic (M_a, tgt, is_scaleup, quality, step_mag, C4 gating) is
copied VERBATIM, unchanged. The only addition is that this script keeps the full per-bar
(bar_pos, bar_pnl, sess_id, is_last_of_sess) arrays and writes them to disk, plus builds the
cumulative-from-session-open MTM column that primary_objective_v2's intraday leg
(build_session_logpath) requires. No new backtest engine; same correctness gate re-applied.

ABSOLUTE RULE (per directive): never touch data dated >= 2026-08-01. health_substrate.py's own
HEALTH_END=2026-07-31 already enforces this upstream; canonical cutoff for THIS risk panel is
<= 2026-05-29 (sess_date), matching every other certified U6B artifact. Bars from 2026-05-30
through 2026-07-31 are kept and written out SEPARATELY, tagged is_health_only_bar=True, and are
never blended into any promotion-relevant statistic -- observational only, per spec.yaml's own
validation_battery convention for the June-July-2026 extension.
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
U0_PATH = os.path.join(ROOT, "runs", "U0_UNIFIED_STATE", "out", "u0_state_table.parquet")

KSOLAR, KBMOM, TILTRESCALE, TILTMULT, SHORTHALF = 0.728654, 2.934159, 0.9026, 1.25, 0.5
PV_MNQ_A, COMM_MNQ_A = 2.0, 0.65

CANONICAL_CUTOFF = pd.Timestamp("2026-05-29")   # matches every other certified U6B artifact
LOCKED_FORWARD_START = pd.Timestamp("2026-08-01")

n = HS.n
open_, high, low, close = HS.open_, HS.high, HS.low, HS.close
last = HS.last
sd = HS.sess_arr
T, B, tilt_state = HS.T, np.asarray(HS.B), HS.tilt_state
entry_blocked_c4, forced_flat_c4 = HS.entry_blocked_c4, HS.forced_flat_c4
PEND = HS.PEND
vote_dispersion = (PEND > 0).sum(axis=1) - (PEND < 0).sum(axis=1)
bar_time = pd.to_datetime(HS.bar_time) if hasattr(HS, "bar_time") else pd.to_datetime(HS.bars["time"])
sess_dt = pd.to_datetime(pd.Series(sd))

assert (sess_dt < LOCKED_FORWARD_START).all(), \
    "STOP: substrate contains bars on/after 2026-08-01 -- LOCKED_FORWARD violation"
canon_mask = (sess_dt <= CANONICAL_CUTOFF).to_numpy()
print(f"[risk_panel] total bars={n}  canonical bars={int(canon_mask.sum())}  "
      f"health-only bars={int((~canon_mask).sum())}", flush=True)

# ---------------------------------------------------------------- genuine MNQ OHLC (identical pattern to 02_ script)
mnq_raw = pd.read_csv(os.path.join(ROOT, "runs", "PRODUCTB_ONECONTRACT_FINAL", "out", "mnq_3m_raw.csv"), comment="#")
mnq_raw["time"] = pd.to_datetime(mnq_raw["time"])
mnq_idx = mnq_raw.set_index("time")
aligned_raw = mnq_idx.reindex(HS.bars["time"])
is_mnq_genuine = aligned_raw["close"].notna().to_numpy()
o_mnq = np.where(is_mnq_genuine, aligned_raw["open"].to_numpy(), open_)
h_mnq = np.where(is_mnq_genuine, aligned_raw["high"].to_numpy(), high)
l_mnq = np.where(is_mnq_genuine, aligned_raw["low"].to_numpy(), low)
c_mnq = np.where(is_mnq_genuine, aligned_raw["close"].to_numpy(), close)
print(f"[risk_panel] MNQ genuine bars: {int(is_mnq_genuine.sum())} / {n}", flush=True)

# ---------------------------------------------------------------- VOTE_THRESH: identical derivation to 01_/02_ scripts
u0 = pd.read_parquet(U0_PATH)
assert len(u0) == n
canon_events_u0 = u0[(~u0["is_health_only_bar"]) & (u0["action_A"].isin(["ENTRY", "SCALE_IN"]))]
change_sign_u0 = np.sign(canon_events_u0["target_exposure_A"].to_numpy())
vd_aligned_u0 = canon_events_u0["vote_dispersion"].to_numpy() * change_sign_u0
VOTE_THRESH = float(np.quantile(vd_aligned_u0, 2.0 / 3.0))
print(f"[risk_panel] VOTE_THRESH (identical to 01_/02_ scripts) = {VOTE_THRESH}", flush=True)


def rha(x):
    return np.sign(x) * np.floor(np.abs(x) + 0.5)


def product_a_exec_ratelimited(f, o, h, l, c):
    """VERBATIM copy of 02_genuine_mnq_repricing.py's decision loop (byte-identical formulas).
    Only addition: returns bar_pos/bar_pnl as before (unchanged), used downstream to build the
    cumulative-from-session-open MTM column."""
    m_arr = np.where((T != 0) & (tilt_state != 0) & (np.sign(T) == tilt_state), TILTMULT, 1.0)
    s_arr = np.where((T < 0) & (tilt_state > 0), SHORTHALF, 1.0)
    Tpp = np.clip(rha(T * m_arr * s_arr * TILTRESCALE), -13, 13)
    M_a = np.clip(rha(KSOLAR * Tpp + KBMOM * B), -13, 13)

    cash = 0.0; p = 0; pend = 0; prev_eq = 0.0
    bar_pos = np.zeros(n, dtype=int)
    bar_pnl = np.zeros(n)

    for t in range(n):
        if pend != p:
            d = pend - p
            side = 1 if d > 0 else -1
            px = _fill(o[t], h[t], l[t], side)
            cash -= d * px * PV_MNQ_A
            cash -= abs(d) * COMM_MNQ_A
            p = pend
        if last[t] and p != 0:
            side = -1 if p > 0 else 1
            px = _fill(o[t], h[t], l[t], side, at_close=c[t])
            cash += p * px * PV_MNQ_A
            cash -= abs(p) * COMM_MNQ_A
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
                change_sign = np.sign(tgt)
                code = tilt_state[t] * change_sign
                vd_aligned = vote_dispersion[t] * change_sign
                is_high = (code == 1) or (vd_aligned >= VOTE_THRESH)
                if (f is not None) and (not is_high):
                    gap = tgt - p
                    naive_step = int(np.floor(f * abs(gap)))
                    step_mag = max(1, naive_step)
                    tgt = p + int(np.sign(gap)) * step_mag
            pend = tgt
        eq = cash + p * c[t] * PV_MNQ_A
        bar_pnl[t] = eq - prev_eq; prev_eq = eq
        bar_pos[t] = p

    return bar_pos, bar_pnl


GRID = {"CONTROL": None, "F0.5": 0.5, "F0.7": 0.7}
CERTIFIED_CANON = {"CONTROL": 178687.39999999898, "F0.5": 178988.70000000065, "F0.7": 179302.30000000086}

summary_rows = []
for tag, f in GRID.items():
    print(f"[risk_panel] running {tag} GENUINE (MNQ) bar-level ...", flush=True)
    barpos, bpnl = product_a_exec_ratelimited(f, o_mnq, h_mnq, l_mnq, c_mnq)

    # correctness gate: canonical-window net must reproduce the already-certified genuine-MNQ net
    canon_net = float(bpnl[canon_mask].sum())
    cert = CERTIFIED_CANON[tag]
    status = "PASS" if abs(canon_net - cert) < 1.0 else "MISMATCH"
    print(f"[risk_panel] {tag} correctness gate: got={canon_net:.2f} certified={cert:.2f} [{status}]", flush=True)
    if status == "MISMATCH":
        raise AssertionError(f"risk_panel bar-level reconstruction MISMATCH for {tag}: {canon_net} vs {cert}")

    df = pd.DataFrame({
        "time": HS.bars["time"].to_numpy(),
        "sess_date": sd,
        "is_last_of_sess": last,
        "bar_pos": barpos,
        "bar_pnl": bpnl,
        "is_health_only_bar": ~canon_mask,
    })
    # cumulative-from-session-open MTM: cumsum of bar_pnl WITHIN each session (session id = sess_date,
    # data already in time order so groupby-cumsum reproduces the from-open running MTM exactly).
    df["mtm_from_open"] = df.groupby("sess_date", sort=False)["bar_pnl"].cumsum()

    # per-session daily net reconciliation (last bar of each session == that session's daily P&L)
    sess_last = df[df["is_last_of_sess"]].set_index("sess_date")["mtm_from_open"]
    sess_pnl_direct = df.groupby("sess_date", sort=False)["bar_pnl"].sum()
    recon_diff = float((sess_last - sess_pnl_direct).abs().max())
    print(f"[risk_panel] {tag}: max |last-bar mtm_from_open - session sum(bar_pnl)| = {recon_diff:.3e}", flush=True)
    assert recon_diff < 1e-6, f"{tag}: intraday reconciliation FAILED ({recon_diff})"

    canon_df = df[~df["is_health_only_bar"]].reset_index(drop=True)
    ext_df = df[df["is_health_only_bar"]].reset_index(drop=True)
    canon_df.to_parquet(os.path.join(OUT, f"{tag}_barlevel_GENUINE_MNQ_canonical.parquet"), index=False)
    ext_df.to_parquet(os.path.join(OUT, f"{tag}_barlevel_GENUINE_MNQ_extension.parquet"), index=False)

    summary_rows.append({
        "candidate": tag, "n_bars_total": len(df), "n_bars_canonical": len(canon_df),
        "n_bars_extension": len(ext_df), "n_sessions_canonical": int(canon_df["sess_date"].nunique()),
        "n_sessions_extension": int(ext_df["sess_date"].nunique()),
        "canonical_net_reconstructed": canon_net, "canonical_net_certified": cert,
        "max_bars_per_session_canonical": int(canon_df.groupby("sess_date").size().max()),
        "min_bars_per_session_canonical": int(canon_df.groupby("sess_date").size().min()),
        "intraday_reconciliation_max_abs_diff": recon_diff,
    })

summary_df = pd.DataFrame(summary_rows)
summary_df.to_csv(os.path.join(OUT, "barlevel_construction_summary.csv"), index=False)
print("\n[risk_panel] ==== BAR-LEVEL CONSTRUCTION SUMMARY ====")
print(summary_df.to_string(index=False))
print("\n[risk_panel] bar-level construction complete.")
