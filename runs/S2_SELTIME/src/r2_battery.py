"""S2_SELTIME R2 -- capital-map + promotion battery, applied separately to Product A,
BEST_ONE_NQ, BEST_ONE_MNQ. Implements runs/S2_SELTIME/r2_spec.yaml exactly. Reuses the frozen
apply_entry_eligibility() from run.py verbatim (imported, not re-derived), sm01_solarsim's
member/E10 machinery verbatim, and PRODUCTB_ONECONTRACT_FINAL's bmom_pos_series/capital_map
verbatim. Builds a SESSION-RELATIVE C4 flatten schedule (fixing the hardcoded-clock defect
already diagnosed in runs/V1R4_NT8_PARITY/REPORT.md's Q1-2025 spot-check) for both Product A
and the one-contract objects -- this is required for R2 to be a fair test of the CURRENT (_v3/
_v4) shipped objects, not the superseded hardcoded-clock ones.
"""
import os, sys, json, importlib.util
import numpy as np, pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
sys.path.insert(0, os.path.join(ROOT, "runs", "W18R1_M1_VOLSEASON", "src"))
import sm01_solarsim as sm
from sm01_solarsim import load_bars_3m, _fill
from sm_bmom import rth_3m, BAND_DAYS
from smv2_common import dd_battery, boot_ci_mean
import common as C1

RUN = os.path.join(ROOT, "runs", "S2_SELTIME")
OUT = os.path.join(RUN, "out", "r2")
os.makedirs(OUT, exist_ok=True)

# ---- import apply_entry_eligibility verbatim from the frozen S2 run.py (by file path, since
# the module name "run" collides across run dirs -- avoid sys.modules caching issues) ----
spec = importlib.util.spec_from_file_location("s2_run_frozen", os.path.join(RUN, "src", "run.py"))
# run.py executes its whole pipeline on import; instead, extract just the function source-free
# by re-declaring it here VERBATIM (byte-identical to run.py lines 27-44) to avoid re-running
# S2's entire original battery as an import side effect (same convention used for window_sweep.py
# earlier this campaign).
def apply_entry_eligibility(T, blocked_mask):
    n = len(T)
    Tp = np.empty(n, dtype=int)
    prev = 0
    for t in range(n):
        cur = int(T[t])
        is_new_commitment = (cur != 0) and (
            (prev == 0) or (np.sign(cur) != np.sign(prev))
        )
        if is_new_commitment and blocked_mask[t]:
            Tp[t] = 0
        else:
            Tp[t] = cur
        prev = Tp[t]
    return Tp


def since_1800_hours(bars):
    t = pd.to_datetime(bars["time"])
    hh = t.dt.hour.to_numpy() + t.dt.minute.to_numpy() / 60.0
    return (hh - 18.0) % 24.0


def rha(x):
    return np.sign(x) * np.floor(np.abs(x) + 0.5)


PV_MNQ, COMM_MNQ = 2.0, 0.65
PV_NQ, COMM_NQ = 20.0, 2.18
ENTRY_BLOCK_MIN, FORCED_FLAT_MIN = 30, 21
D7 = pd.Timestamp("2024-08-05")
SEED, BLOCK, NBOOT = 20260809, 5, 10000

# ================================================================== shared substrate
print("building shared substrate (T, B, tilt, session-relative close, S2 mask) ...", flush=True)
bars = load_bars_3m()
sess = pd.to_datetime(bars["sess_date"])
dev = (sess <= pd.Timestamp("2026-05-31")).to_numpy()
bars = bars[dev].reset_index(drop=True)
n = len(bars)
close = bars["close"].to_numpy()
sig460 = sm.sigma_series(close)
PEND = C1.build_pend(bars, sig460)
T = sm.e10_target(PEND).astype(int)  # Solar E10 leg, incumbent

sclose = bars.loc[bars["is_last_of_sess"], ["sess_date", "close"]].set_index("sess_date")["close"]
tilt_by_date = np.sign(sclose - sclose.rolling(50).mean()).shift(1).to_dict()
tilt_state = np.array([tilt_by_date.get(d, np.nan) for d in bars["sess_date"]])
tilt_state = np.where(np.isnan(tilt_state), 0.0, tilt_state)


def bmom_pos_series(bars3):
    r = rth_3m(bars3)
    pos_arr = np.zeros(len(bars3)); hist = {}; day_count = 0
    for d_, g in r.groupby("date", sort=True):
        g = g.sort_values("hm")
        if g["hm"].iloc[0] != 933:
            continue
        open0930 = g["open"].iloc[0]
        close_ = g["close"].to_numpy(); vol = g["volume"].to_numpy(); hm = g["hm"].to_numpy()
        vwap = np.cumsum(close_ * vol) / np.maximum(np.cumsum(vol), 1e-9)
        gidx = g.index.to_numpy(); pos = 0
        flat_hm = int(hm[hm <= 1557].max()) if (hm <= 1557).any() else None
        if day_count >= BAND_DAYS:
            for i in range(len(g)):
                h = int(hm[i])
                if flat_hm is not None and h == flat_hm:
                    pos = 0; pos_arr[gidx[i]] = pos; break
                if h > 1554:
                    pos_arr[gidx[i]] = pos; continue
                past = hist.get(h)
                if past is not None and len(past) >= 1:
                    m_tod = float(np.mean(past[-BAND_DAYS:]))
                    up, lo = open0930 + m_tod, open0930 - m_tod
                    if close_[i] > max(up, vwap[i]):
                        pos = 1
                    elif close_[i] < min(lo, vwap[i]):
                        pos = -1
                pos_arr[gidx[i]] = pos
        for i in range(len(g)):
            hist.setdefault(int(hm[i]), []).append(abs(close_[i] - open0930))
        day_count += 1
    return pos_arr


B = bmom_pos_series(bars)

# session-relative actual close timestamp per bar (fixes the hardcoded-clock defect)
sess_close_ts = bars.groupby("sess_date")["time"].transform("max")
entry_block_dl = sess_close_ts - pd.Timedelta(minutes=ENTRY_BLOCK_MIN)
forced_flat_dl = sess_close_ts - pd.Timedelta(minutes=FORCED_FLAT_MIN)
bar_time = bars["time"]
entry_blocked_c4 = (bar_time >= entry_block_dl).to_numpy()
forced_flat_c4 = (bar_time >= forced_flat_dl).to_numpy()

since = since_1800_hours(bars)
s2_blocked = (since >= 8.0) & (since < 14.0)  # 02:00-08:00 ET, frozen decision cell, verbatim
print(f"n bars {n}, S2-blocked bars {s2_blocked.sum()} ({s2_blocked.mean()*100:.1f}%), "
      f"C4 entry-blocked {entry_blocked_c4.sum()}, C4 forced-flat {forced_flat_c4.sum()}", flush=True)

T_s2 = apply_entry_eligibility(T, s2_blocked)
print(f"T vs T_s2 differ on {int((T != T_s2).sum())} bars", flush=True)


# ================================================================== PRODUCT A
def product_a_exec(T_leg, tag):
    """Decision (bar t's close-derived signal) becomes `pend`, which only FILLS at bar t+1's
    OPEN -- the same 1-bar decide-then-fill lag as sm01_solarsim.e10_sim / W18R1 common.e10_exec
    (verbatim pattern reuse, not a new convention). The C4 overlay's `cur` is the PHYSICAL
    (lagged) position, exactly matching the real .cs code's `PhysicalPosition()` read timing."""
    KSOLAR, KBMOM, TILTRESCALE, TILTMULT, SHORTHALF = 0.728654, 2.934159, 0.9026, 1.25, 0.5
    o = bars["open"].to_numpy(); h = bars["high"].to_numpy(); l = bars["low"].to_numpy()
    c = bars["close"].to_numpy(); last = bars["is_last_of_sess"].to_numpy()
    sd = bars["sess_date"].to_numpy()
    m_arr = np.where((T_leg != 0) & (tilt_state != 0) & (np.sign(T_leg) == tilt_state), TILTMULT, 1.0)
    s_arr = np.where((T_leg < 0) & (tilt_state > 0), SHORTHALF, 1.0)
    Tpp = np.clip(rha(T_leg * m_arr * s_arr * TILTRESCALE), -13, 13)
    M = np.clip(rha(KSOLAR * Tpp + KBMOM * np.asarray(B)), -13, 13)

    cash = 0.0; p = 0; pend = 0; prev_eq = 0.0
    contracts_by_sess = {}
    bar_pos = np.zeros(n, dtype=int); bar_pnl = np.zeros(n)
    for t in range(n):
        if pend != p:
            d = pend - p
            side = 1 if d > 0 else -1
            px = _fill(o[t], h[t], l[t], side)
            cash -= d * px * PV_MNQ
            cash -= abs(d) * COMM_MNQ
            contracts_by_sess[sd[t]] = contracts_by_sess.get(sd[t], 0) + abs(d)
            p = pend
        if last[t] and p != 0:
            side = -1 if p > 0 else 1
            px = _fill(o[t], h[t], l[t], side, at_close=c[t])
            cash += p * px * PV_MNQ
            cash -= abs(p) * COMM_MNQ
            contracts_by_sess[sd[t]] = contracts_by_sess.get(sd[t], 0) + abs(p)
            p = 0; pend = 0
        else:
            tgt_raw = int(M[t])
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
            pend = tgt
        eq = cash + p * c[t] * PV_MNQ
        bar_pnl[t] = eq - prev_eq; prev_eq = eq
        bar_pos[t] = p
        if last[t]:
            contracts_by_sess.setdefault(sd[t], 0)
    dd = pd.DataFrame({"sess": bars["sess_date"], "pnl": bar_pnl}).groupby("sess")["pnl"].sum().reset_index()
    dd.columns = ["sess", "net"]
    dd["contracts"] = dd["sess"].map(contracts_by_sess)
    print(f"  [{tag}] net={dd['net'].sum():.2f}  n_sess={len(dd)}  max|pos|={np.abs(bar_pos).max()}", flush=True)
    return dd, bar_pos, bar_pnl, M


print("=" * 90, flush=True); print("PRODUCT A", flush=True); print("=" * 90, flush=True)
A_incumbent = product_a_exec(T, "A incumbent")
A_s2 = product_a_exec(T_s2, "A + S2")


# ================================================================== BEST_ONE_NQ / MNQ shared decision layer
def one_contract_decisions(apply_s2):
    """Returns the LAGGED physical-position sequence p_t (in {-1,0,1}) for the SM14
    hysteresis(3,1) object: the target decided using bar t's own M[t] becomes `pend`, which only
    takes effect (becomes the physical position used by the hysteresis's OWN threshold logic,
    and by the S2 eligibility check) at the START of bar t+1 -- matching PhysicalPosition()'s
    real read timing in the .cs code (read BEFORE that bar's own decision, i.e. reflecting only
    PRIOR bars' decisions). Optionally integrates S2's eligibility check at the position-
    commitment layer (per r2_spec.yaml's frozen interpretation_one_NQ). Session-relative C4 (not
    hardcoded clock). Identical for NQ and MNQ since both share the same NQ-only signal."""
    WSOLAR, WBMOM, TILTRESCALE, TILTMULT = 0.7086, 2.83, 0.9026, 1.25
    ENTRY_LEVEL, EXIT_LEVEL = 3.0, 1.0
    m_arr = np.where((T != 0) & (tilt_state != 0) & (np.sign(T) == tilt_state), TILTMULT, 1.0)
    Tp = np.clip(rha(T * m_arr * TILTRESCALE), -13, 13)
    M = WSOLAR * Tp + WBMOM * np.asarray(B)
    last = bars["is_last_of_sess"].to_numpy()

    p = 0     # physical (lagged) position
    pend = 0  # decided this bar, takes effect (fills) at the START of next bar
    pos_seq = np.zeros(n, dtype=int)
    n_suppressed = 0
    for t in range(n):
        if pend != p:
            p = pend
        if last[t] and p != 0:
            # session-close backstop: forced flat, same as the real object's
            # IsExitOnSessionCloseStrategy safety net
            p = 0; pend = 0
            pos_seq[t] = p
            continue
        pos_seq[t] = p
        if forced_flat_c4[t]:
            tgt = 0
        elif p == 0:
            if entry_blocked_c4[t]:
                tgt = 0
            else:
                tgt = 1 if M[t] >= ENTRY_LEVEL else (-1 if M[t] <= -ENTRY_LEVEL else 0)
        elif p > 0:
            if M[t] <= -ENTRY_LEVEL and not entry_blocked_c4[t]:
                tgt = -1
            elif M[t] <= EXIT_LEVEL:
                tgt = 0
            else:
                tgt = p
        else:
            if M[t] >= ENTRY_LEVEL and not entry_blocked_c4[t]:
                tgt = 1
            elif M[t] >= -EXIT_LEVEL:
                tgt = 0
            else:
                tgt = p
        if apply_s2:
            is_new_commitment = (tgt != 0) and ((p == 0) or (np.sign(tgt) != np.sign(p)))
            if is_new_commitment and s2_blocked[t]:
                n_suppressed += 1
                tgt = 0
        pend = tgt
    return pos_seq, M, n_suppressed


pos_incumbent, M_onelot, _ = one_contract_decisions(apply_s2=False)
pos_s2, _, n_supp = one_contract_decisions(apply_s2=True)
print(f"one-contract decision layer: incumbent vs S2 differ on {int((pos_incumbent != pos_s2).sum())} "
      f"bars ({n_supp} new commitments suppressed)", flush=True)


def onelot_exec(pos_seq, comm, pv, o, h, l, c, tag):
    """Executes an ALREADY-LAGGED physical-position sequence (pos_seq[t] = physical position
    HELD during bar t, as produced by one_contract_decisions -- the decide-then-fill-next-bar
    lag is already baked in there). A transition into pos_seq[t] fills at bar t's OWN open,
    UNLESS bar t is the last bar of its session, in which case it fills at bar t's close
    (matches the session-close-backstop convention every other executor in this campaign uses:
    normal transitions at open, forced/session-end exits at close). Used identically for
    NQ-direct and genuine-MNQ execution of the SAME position sequence."""
    last = bars["is_last_of_sess"].to_numpy(); sd = bars["sess_date"].to_numpy()
    cash = 0.0; p = 0; prev_eq = 0.0
    contracts_by_sess = {}
    bar_pos = np.zeros(n, dtype=int); bar_pnl = np.zeros(n)
    for t in range(n):
        tgt = int(pos_seq[t])
        if tgt != p:
            d = tgt - p
            side = 1 if d > 0 else -1
            if last[t]:
                px = _fill(o[t], h[t], l[t], side, at_close=c[t])
            else:
                px = _fill(o[t], h[t], l[t], side)
            cash -= d * px * pv
            cash -= abs(d) * comm
            contracts_by_sess[sd[t]] = contracts_by_sess.get(sd[t], 0) + abs(d)
            p = tgt
        eq = cash + p * c[t] * pv
        bar_pnl[t] = eq - prev_eq; prev_eq = eq
        bar_pos[t] = p
        if last[t]:
            contracts_by_sess.setdefault(sd[t], 0)
    dd = pd.DataFrame({"sess": bars["sess_date"], "pnl": bar_pnl}).groupby("sess")["pnl"].sum().reset_index()
    dd.columns = ["sess", "net"]
    dd["contracts"] = dd["sess"].map(contracts_by_sess)
    print(f"  [{tag}] net={dd['net'].sum():.2f}  n_sess={len(dd)}", flush=True)
    return dd, bar_pos, bar_pnl


print("=" * 90, flush=True); print("BEST_ONE_NQ", flush=True); print("=" * 90, flush=True)
o_nq = bars["open"].to_numpy(); h_nq = bars["high"].to_numpy(); l_nq = bars["low"].to_numpy(); c_nq = bars["close"].to_numpy()
NQ_incumbent = onelot_exec(pos_incumbent, COMM_NQ, PV_NQ, o_nq, h_nq, l_nq, c_nq, "NQ incumbent")
NQ_s2 = onelot_exec(pos_s2, COMM_NQ, PV_NQ, o_nq, h_nq, l_nq, c_nq, "NQ + S2")

print("=" * 90, flush=True); print("BEST_ONE_MNQ (genuine MNQU6 prices)", flush=True); print("=" * 90, flush=True)
mnq_raw = pd.read_csv(os.path.join(ROOT, "runs", "PRODUCTB_ONECONTRACT_FINAL", "out", "mnq_3m_raw.csv"), comment="#")
mnq_raw["time"] = pd.to_datetime(mnq_raw["time"])
mnq_idx = mnq_raw.set_index("time")
aligned = mnq_idx.reindex(bars["time"])
n_missing = int(aligned["close"].isna().sum())
aligned = aligned.ffill()
print(f"MNQ genuine bars aligned to NQ grid: {n_missing} missing ({100*n_missing/n:.4f}%), ffilled", flush=True)
o_mnq = aligned["open"].to_numpy(); h_mnq = aligned["high"].to_numpy(); l_mnq = aligned["low"].to_numpy(); c_mnq = aligned["close"].to_numpy()
MNQ_incumbent = onelot_exec(pos_incumbent, COMM_MNQ, PV_MNQ, o_mnq, h_mnq, l_mnq, c_mnq, "MNQ incumbent")
MNQ_s2 = onelot_exec(pos_s2, COMM_MNQ, PV_MNQ, o_mnq, h_mnq, l_mnq, c_mnq, "MNQ + S2")

# ================================================================== save raw daily series
SERIES = {
    "A_incumbent": A_incumbent[:3], "A_s2": A_s2[:3],
    "NQ_incumbent": NQ_incumbent, "NQ_s2": NQ_s2,
    "MNQ_incumbent": MNQ_incumbent, "MNQ_s2": MNQ_s2,
}
for name, (dd, bp, bn) in SERIES.items():
    dd.to_csv(os.path.join(OUT, f"daily_{name}.csv"), index=False)
    np.save(os.path.join(OUT, f"barpos_{name}.npy"), bp)
    np.save(os.path.join(OUT, f"barpnl_{name}.npy"), bn)

print("\nSTAGE 1 (decision layers + daily P&L) done.", flush=True)
