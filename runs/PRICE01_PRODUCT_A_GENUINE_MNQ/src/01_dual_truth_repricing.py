"""PRICE01 -- Product-A genuine-MNQ dual-truth infrastructure (Master Directive v3 sec13).

Builds and compares two truths for the SAME Product-A decision sequence:
  LEGACY_RESEARCH_PROXY        -- NQ OHLC used as the fill price, MNQ's $2/pt multiplier applied
                                   directly to NQ price levels (pa0_substrate.py / U0's existing
                                   convention, byte-identical formula reused here verbatim).
  GENUINE_MNQ_EXECUTION_ECONOMICS -- identical decision sequence, but fills happen on MNQ's own
                                   genuine OHLC (runs/PRODUCTB_ONECONTRACT_FINAL/out/mnq_3m_raw.csv,
                                   the same file + alignment pattern U0 already uses for Product
                                   B's MNQ leg).

Per sec13: do NOT silently change canonical historical metrics. LEGACY stays the certified
$177,924.40 canonical net. GENUINE is a new, parallel number -- primary for execution-sensitive
candidate ranking going forward, reported alongside LEGACY, never silently substituted.
"""
import os, sys, json
import numpy as np, pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
sys.path.insert(0, os.path.join(ROOT, "runs", "W18R1_M1_VOLSEASON", "src"))
sys.path.insert(0, os.path.join(ROOT, "runs", "SA0_SYSTEM_STRUCTURE", "current_health", "src"))
from sm01_solarsim import _fill
import health_substrate as HS  # extended (through 2026-07-31) Product-B substrate, self-verified on import

OUT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "out")
os.makedirs(OUT, exist_ok=True)

bars = HS.bars
n = HS.n
close, open_, high, low = HS.close, HS.open_, HS.high, HS.low
last = HS.last
T, tilt_state, B = HS.T, HS.tilt_state, HS.B
entry_blocked_c4, forced_flat_c4 = HS.entry_blocked_c4, HS.forced_flat_c4
sd = bars["sess_date"].to_numpy()
year_arr = HS.year_arr
CANONICAL_END = HS.CANONICAL_END
print(f"[PRICE01] loaded extended substrate: n={n} bars, {bars['time'].min()} .. {bars['time'].max()}", flush=True)

# ---------------------------------------------------------------- genuine MNQ OHLC alignment (identical to U0's pattern)
mnq_raw = pd.read_csv(os.path.join(ROOT, "runs", "PRODUCTB_ONECONTRACT_FINAL", "out", "mnq_3m_raw.csv"), comment="#")
mnq_raw["time"] = pd.to_datetime(mnq_raw["time"])
mnq_idx = mnq_raw.set_index("time")
aligned_raw = mnq_idx.reindex(bars["time"])
is_mnq_genuine = aligned_raw["close"].notna().to_numpy()
o_mnq = np.where(is_mnq_genuine, aligned_raw["open"].to_numpy(), open_)
h_mnq = np.where(is_mnq_genuine, aligned_raw["high"].to_numpy(), high)
l_mnq = np.where(is_mnq_genuine, aligned_raw["low"].to_numpy(), low)
c_mnq = np.where(is_mnq_genuine, aligned_raw["close"].to_numpy(), close)
print(f"[PRICE01] MNQ genuine bars: {int(is_mnq_genuine.sum())} / {n}  "
      f"(proxy-NQ bars: {int((~is_mnq_genuine).sum())})", flush=True)

KSOLAR, KBMOM, TILTRESCALE, TILTMULT, SHORTHALF = 0.728654, 2.934159, 0.9026, 1.25, 0.5
PV_MNQ_A, COMM_MNQ_A = 2.0, 0.65


def rha(x):
    return np.sign(x) * np.floor(np.abs(x) + 0.5)


def product_a_exec_generalized(T_leg, tilt_state_, B_, entry_blocked_, forced_flat_,
                                o, h, l, c, last_, sd_, n_):
    """Verbatim-formula copy of pa0_substrate.product_a_exec / U0's product_a_exec_generalized.
    Only the o/h/l/c price arrays differ between the two calls below -- the decision layer
    (m_arr/s_arr/Tpp/M_a) depends solely on T_leg/tilt_state_/B_, never on price."""
    m_arr = np.where((T_leg != 0) & (tilt_state_ != 0) & (np.sign(T_leg) == tilt_state_), TILTMULT, 1.0)
    s_arr = np.where((T_leg < 0) & (tilt_state_ > 0), SHORTHALF, 1.0)
    Tpp = np.clip(rha(T_leg * m_arr * s_arr * TILTRESCALE), -13, 13)
    M_a = np.clip(rha(KSOLAR * Tpp + KBMOM * B_), -13, 13)

    cash = 0.0; p = 0; pend = 0; prev_eq = 0.0
    contracts_by_sess = {}
    bar_pos = np.zeros(n_, dtype=int)
    bar_pnl = np.zeros(n_)
    for t in range(n_):
        if pend != p:
            d = pend - p
            side = 1 if d > 0 else -1
            px = _fill(o[t], h[t], l[t], side)
            cash -= d * px * PV_MNQ_A
            cash -= abs(d) * COMM_MNQ_A
            contracts_by_sess[sd_[t]] = contracts_by_sess.get(sd_[t], 0) + abs(d)
            p = pend
        if last_[t] and p != 0:
            side = -1 if p > 0 else 1
            px = _fill(o[t], h[t], l[t], side, at_close=c[t])
            cash += p * px * PV_MNQ_A
            cash -= abs(p) * COMM_MNQ_A
            contracts_by_sess[sd_[t]] = contracts_by_sess.get(sd_[t], 0) + abs(p)
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
        if last_[t]:
            contracts_by_sess.setdefault(sd_[t], 0)
    return bar_pos, bar_pnl, M_a


print("[PRICE01] running LEGACY_RESEARCH_PROXY (NQ OHLC, matches pa0_substrate.py/U0 verbatim) ...", flush=True)
barpos_legacy, bpnl_legacy, M_legacy = product_a_exec_generalized(
    T, tilt_state, B, entry_blocked_c4, forced_flat_c4, open_, high, low, close, last, sd, n)

print("[PRICE01] running GENUINE_MNQ_EXECUTION_ECONOMICS (genuine MNQ OHLC) ...", flush=True)
barpos_genuine, bpnl_genuine, M_genuine = product_a_exec_generalized(
    T, tilt_state, B, entry_blocked_c4, forced_flat_c4, o_mnq, h_mnq, l_mnq, c_mnq, last, sd, n)

target_exposure_identical = bool(np.array_equal(barpos_legacy, barpos_genuine))
assert target_exposure_identical, (
    "target-exposure sequences differ between legacy and genuine-MNQ runs -- price should only "
    "affect fill economics, never the signal-driven decision layer. STOP: price is leaking into "
    "the decision layer somehow; investigate before reporting anything."
)
print(f"[PRICE01] VERIFIED: target-exposure sequences are byte-identical "
      f"(price affects fills only, not the decision layer)", flush=True)

sd_dt = pd.to_datetime(pd.Series(sd))
canon_mask = (sd_dt <= CANONICAL_END).to_numpy()

net_legacy_canon = float(bpnl_legacy[canon_mask].sum())
net_genuine_canon = float(bpnl_genuine[canon_mask].sum())
net_legacy_ext = float(bpnl_legacy.sum())
net_genuine_ext = float(bpnl_genuine.sum())

assert abs(net_legacy_canon - 177924.40) < 1.0, f"PRICE01 LEGACY control mismatch: {net_legacy_canon}"
print(f"[PRICE01] correctness gate PASS: legacy canonical net == certified $177,924.40", flush=True)

print(f"[PRICE01] CANONICAL (<= {CANONICAL_END.date()}): legacy={net_legacy_canon:.2f}  "
      f"genuine={net_genuine_canon:.2f}  diff={net_genuine_canon - net_legacy_canon:+.2f} "
      f"({(net_genuine_canon / net_legacy_canon - 1) * 100:+.2f}%)", flush=True)
print(f"[PRICE01] EXTENDED (through {HS.HEALTH_END.date()}): legacy={net_legacy_ext:.2f}  "
      f"genuine={net_genuine_ext:.2f}  diff={net_genuine_ext - net_legacy_ext:+.2f} "
      f"({(net_genuine_ext / net_legacy_ext - 1) * 100:+.2f}%)", flush=True)

# ---------------------------------------------------------------- year-by-year (canonical years only, clean calendar buckets)
rows = []
for y in sorted(set(year_arr[canon_mask])):
    m = (year_arr == y) & canon_mask
    if m.sum() == 0:
        continue
    lg, gn = float(bpnl_legacy[m].sum()), float(bpnl_genuine[m].sum())
    rows.append({"year": int(y), "legacy_net": lg, "genuine_net": gn, "diff": gn - lg,
                 "diff_pct": (gn / lg - 1) * 100 if lg != 0 else float("nan")})
yby = pd.DataFrame(rows)

# ---------------------------------------------------------------- cross-check vs V1R4 NT8 parity gap
NT8_STITCHED_CANONICAL = 197329.70  # V1R4_NT8_PARITY/FULL_HISTORY_CERTIFICATION.md, real genuine-MNQ NT8 execution
nt8_vs_legacy_gap = NT8_STITCHED_CANONICAL - net_legacy_canon
nt8_vs_genuine_gap = NT8_STITCHED_CANONICAL - net_genuine_canon
pct_of_gap_explained_by_price_basis = (
    (net_genuine_canon - net_legacy_canon) / nt8_vs_legacy_gap * 100 if nt8_vs_legacy_gap != 0 else float("nan")
)

# ---------------------------------------------------------------- save daily series for downstream candidate repricing
daily_legacy = pd.DataFrame({"sess": sd, "pnl": bpnl_legacy}).groupby("sess")["pnl"].sum().reset_index()
daily_genuine = pd.DataFrame({"sess": sd, "pnl": bpnl_genuine}).groupby("sess")["pnl"].sum().reset_index()
daily_legacy.to_csv(os.path.join(OUT, "daily_legacy_proxy.csv"), index=False)
daily_genuine.to_csv(os.path.join(OUT, "daily_genuine_mnq.csv"), index=False)
yby.to_csv(os.path.join(OUT, "year_by_year_comparison.csv"), index=False)

recon = {
    "target_exposure_sequences_identical": target_exposure_identical,
    "correctness_gate": "PASS -- legacy canonical net matches certified $177,924.40",
    "canonical": {
        "legacy": round(net_legacy_canon, 2), "genuine": round(net_genuine_canon, 2),
        "diff": round(net_genuine_canon - net_legacy_canon, 2),
        "diff_pct": round((net_genuine_canon / net_legacy_canon - 1) * 100, 4),
    },
    "extended_through_2026_07_31": {
        "legacy": round(net_legacy_ext, 2), "genuine": round(net_genuine_ext, 2),
        "diff": round(net_genuine_ext - net_legacy_ext, 2),
        "diff_pct": round((net_genuine_ext / net_legacy_ext - 1) * 100, 4),
    },
    "nt8_parity_crosscheck": {
        "nt8_stitched_canonical_net": NT8_STITCHED_CANONICAL,
        "gap_nt8_vs_legacy_proxy": round(nt8_vs_legacy_gap, 2),
        "gap_nt8_vs_genuine_mnq": round(nt8_vs_genuine_gap, 2),
        "pct_of_nt8_vs_legacy_gap_explained_by_price_basis": round(pct_of_gap_explained_by_price_basis, 2),
    },
    "n_mnq_genuine_bars": int(is_mnq_genuine.sum()), "n_bars": int(n),
}
json.dump(recon, open(os.path.join(OUT, "price01_recon.json"), "w"), indent=2)
print("\nRECON:", json.dumps(recon, indent=2))
print("\nPRICE01 dual-truth repricing complete.")
