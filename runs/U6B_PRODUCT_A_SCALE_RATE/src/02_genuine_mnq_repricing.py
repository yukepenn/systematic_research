"""U6B genuine-MNQ dual-truth repricing (Master Directive v4 sec5). Re-runs the EXACT frozen
U6B rate-limiter construction (verbatim from 01_construct_and_validate.py -- decision logic
untouched) on genuine MNQ OHLC instead of the NQ-proxy, for CONTROL/F0.5/F0.7. Verifies the
exposure decision path is byte-identical between the two pricing conventions (price should only
affect fill economics, never the rate-limiter's own scale-up/quality decisions -- those depend
only on T/B/tilt_state/vote_dispersion, all NQ-signal-derived, never on price).
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

OUT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "out")
os.makedirs(OUT, exist_ok=True)
U0_PATH = os.path.join(ROOT, "runs", "U0_UNIFIED_STATE", "out", "u0_state_table.parquet")

KSOLAR, KBMOM, TILTRESCALE, TILTMULT, SHORTHALF = 0.728654, 2.934159, 0.9026, 1.25, 0.5
PV_MNQ_A, COMM_MNQ_A = 2.0, 0.65

n = HS.n
open_, high, low, close = HS.open_, HS.high, HS.low, HS.close
last = HS.last
sd = HS.sess_arr
year_arr = HS.year_arr
T, B, tilt_state = HS.T, np.asarray(HS.B), HS.tilt_state
entry_blocked_c4, forced_flat_c4 = HS.entry_blocked_c4, HS.forced_flat_c4
PEND = HS.PEND
CANONICAL_END, HEALTH_END = HS.CANONICAL_END, HS.HEALTH_END
vote_dispersion = (PEND > 0).sum(axis=1) - (PEND < 0).sum(axis=1)
sess_dt = pd.to_datetime(pd.Series(sd))
canon_mask = (sess_dt <= CANONICAL_END).to_numpy()
r2225_mask = canon_mask & (sess_dt <= pd.Timestamp("2025-12-31")).to_numpy()

# ---------------------------------------------------------------- genuine MNQ OHLC (identical pattern to PRICE01/U0)
mnq_raw = pd.read_csv(os.path.join(ROOT, "runs", "PRODUCTB_ONECONTRACT_FINAL", "out", "mnq_3m_raw.csv"), comment="#")
mnq_raw["time"] = pd.to_datetime(mnq_raw["time"])
mnq_idx = mnq_raw.set_index("time")
aligned_raw = mnq_idx.reindex(HS.bars["time"])
is_mnq_genuine = aligned_raw["close"].notna().to_numpy()
o_mnq = np.where(is_mnq_genuine, aligned_raw["open"].to_numpy(), open_)
h_mnq = np.where(is_mnq_genuine, aligned_raw["high"].to_numpy(), high)
l_mnq = np.where(is_mnq_genuine, aligned_raw["low"].to_numpy(), low)
c_mnq = np.where(is_mnq_genuine, aligned_raw["close"].to_numpy(), close)
print(f"[U6B-MNQ] MNQ genuine bars: {int(is_mnq_genuine.sum())} / {n}  "
      f"(proxy-NQ bars: {int((~is_mnq_genuine).sum())})", flush=True)

# ---------------------------------------------------------------- VOTE_THRESH: identical derivation to 01_ script
u0 = pd.read_parquet(U0_PATH)
assert len(u0) == n
canon_events_u0 = u0[(~u0["is_health_only_bar"]) & (u0["action_A"].isin(["ENTRY", "SCALE_IN"]))]
change_sign_u0 = np.sign(canon_events_u0["target_exposure_A"].to_numpy())
vd_aligned_u0 = canon_events_u0["vote_dispersion"].to_numpy() * change_sign_u0
VOTE_THRESH = float(np.quantile(vd_aligned_u0, 2.0 / 3.0))
print(f"[U6B-MNQ] VOTE_THRESH (identical to 01_ script) = {VOTE_THRESH}", flush=True)


def rha(x):
    return np.sign(x) * np.floor(np.abs(x) + 0.5)


def product_a_exec_ratelimited(f, o, h, l, c):
    """Verbatim rate-limiter logic from 01_construct_and_validate.py -- ONLY the o/h/l/c price
    arrays passed to _fill()/cash-flow differ between the legacy and genuine-MNQ calls below.
    The decision layer (M_a, tgt, is_scaleup, quality, step_mag) never reads price."""
    m_arr = np.where((T != 0) & (tilt_state != 0) & (np.sign(T) == tilt_state), TILTMULT, 1.0)
    s_arr = np.where((T < 0) & (tilt_state > 0), SHORTHALF, 1.0)
    Tpp = np.clip(rha(T * m_arr * s_arr * TILTRESCALE), -13, 13)
    M_a = np.clip(rha(KSOLAR * Tpp + KBMOM * B), -13, 13)

    cash = 0.0; p = 0; pend = 0; prev_eq = 0.0
    contracts_by_sess = {}
    bar_pos = np.zeros(n, dtype=int)
    bar_pnl = np.zeros(n)

    for t in range(n):
        if pend != p:
            d = pend - p
            side = 1 if d > 0 else -1
            px = _fill(o[t], h[t], l[t], side)
            cash -= d * px * PV_MNQ_A
            cash -= abs(d) * COMM_MNQ_A
            contracts_by_sess[sd[t]] = contracts_by_sess.get(sd[t], 0) + abs(d)
            p = pend
        if last[t] and p != 0:
            side = -1 if p > 0 else 1
            px = _fill(o[t], h[t], l[t], side, at_close=c[t])
            cash += p * px * PV_MNQ_A
            cash -= abs(p) * COMM_MNQ_A
            contracts_by_sess[sd[t]] = contracts_by_sess.get(sd[t], 0) + abs(p)
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
        if last[t]:
            contracts_by_sess.setdefault(sd[t], 0)

    return bar_pos, bar_pnl


def battery_row(tag, dates, net):
    b = dd_battery(pd.to_datetime(dates), net, label=tag)
    return {"tag": tag, "n_days": b["n_days"], "net": b["net"], "sharpe": b["sharpe"],
            "sortino": b["sortino"], "calmar": b["calmar"], "maxDD_eod": b["maxDD_eod"],
            "CDaR95": b["CDaR5"], "worst_day": float(np.min(net)) if len(net) else np.nan,
            "worst_month": b["worst_month"], "pos_day_pct": b["pos_day_pct"]}


GRID = {"CONTROL": None, "F0.5": 0.5, "F0.7": 0.7}
legacy_results = {}
genuine_results = {}
identity_check = {}

for tag, f in GRID.items():
    print(f"[U6B-MNQ] running {tag} LEGACY (NQ-proxy) ...", flush=True)
    barpos_leg, bpnl_leg = product_a_exec_ratelimited(f, open_, high, low, close)
    print(f"[U6B-MNQ] running {tag} GENUINE (MNQ) ...", flush=True)
    barpos_gen, bpnl_gen = product_a_exec_ratelimited(f, o_mnq, h_mnq, l_mnq, c_mnq)
    legacy_results[tag] = (barpos_leg, bpnl_leg)
    genuine_results[tag] = (barpos_gen, bpnl_gen)
    identical = bool(np.array_equal(barpos_leg, barpos_gen))
    identity_check[tag] = identical
    print(f"[U6B-MNQ] {tag}: exposure-path identical (legacy vs genuine) = {identical}", flush=True)
    assert identical, f"U6B-MNQ STOP: {tag} exposure path differs between legacy/genuine pricing -- price is leaking into the decision layer, investigate before reporting anything"

# ---------------------------------------------------------------- correctness gate
ctrl_leg_canon = float(legacy_results["CONTROL"][1][canon_mask].sum())
assert abs(ctrl_leg_canon - 177924.40) < 1.0, f"U6B-MNQ CONTROL legacy canonical net mismatch: {ctrl_leg_canon}"
print(f"\n[U6B-MNQ] CORRECTNESS GATE PASSED: CONTROL legacy canonical net = {ctrl_leg_canon:.2f} (certified $177,924.40)", flush=True)

# ---------------------------------------------------------------- headline table: legacy vs genuine, canonical + 2022-2025-only
rows = []
for tag in GRID:
    bpnl_leg = legacy_results[tag][1]
    bpnl_gen = genuine_results[tag][1]
    net_leg_canon = float(bpnl_leg[canon_mask].sum())
    net_gen_canon = float(bpnl_gen[canon_mask].sum())
    net_leg_2225 = float(bpnl_leg[r2225_mask].sum())
    net_gen_2225 = float(bpnl_gen[r2225_mask].sum())
    net_leg_ext = float(bpnl_leg.sum())
    net_gen_ext = float(bpnl_gen.sum())
    rows.append({
        "candidate": tag,
        "legacy_canonical_net": net_leg_canon, "genuine_canonical_net": net_gen_canon,
        "genuine_minus_legacy_canonical": net_gen_canon - net_leg_canon,
        "legacy_2022_2025_net": net_leg_2225, "genuine_2022_2025_net": net_gen_2225,
        "legacy_extended_net": net_leg_ext, "genuine_extended_net": net_gen_ext,
    })
headline = pd.DataFrame(rows)

# deltas vs control, under each convention, 2022-2025-only (the campaign's standing wash test)
ctrl_leg_2225 = float(legacy_results["CONTROL"][1][r2225_mask].sum())
ctrl_gen_2225 = float(genuine_results["CONTROL"][1][r2225_mask].sum())
delta_rows = []
for tag in ["F0.5", "F0.7"]:
    leg_2225 = float(legacy_results[tag][1][r2225_mask].sum())
    gen_2225 = float(genuine_results[tag][1][r2225_mask].sum())
    delta_rows.append({
        "candidate": tag,
        "legacy_delta_2022_2025": leg_2225 - ctrl_leg_2225,
        "legacy_delta_pct": (leg_2225 - ctrl_leg_2225) / ctrl_leg_2225 * 100,
        "genuine_delta_2022_2025": gen_2225 - ctrl_gen_2225,
        "genuine_delta_pct": (gen_2225 - ctrl_gen_2225) / ctrl_gen_2225 * 100,
        "verdict_flips": bool(np.sign(leg_2225 - ctrl_leg_2225) != np.sign(gen_2225 - ctrl_gen_2225)),
    })
delta_df = pd.DataFrame(delta_rows)

print("\n[U6B-MNQ] ==== HEADLINE: legacy vs genuine ====")
print(headline.to_string(index=False))
print("\n[U6B-MNQ] ==== 2022-2025-only DELTA vs CONTROL (wash threshold <1% of control's own 2022-2025 net) ====")
print(f"control 2022-2025 net: legacy={ctrl_leg_2225:.2f}  genuine={ctrl_gen_2225:.2f}")
print(delta_df.to_string(index=False))

# ---------------------------------------------------------------- full battery under GENUINE convention (for downstream capital/DD/forward-readiness work)
battery_rows = []
year_rows = []
for tag in GRID:
    bpnl_gen = genuine_results[tag][1]
    d = pd.DataFrame({"sess": sd, "pnl": bpnl_gen})
    d["dt"] = pd.to_datetime(d["sess"])
    canon_d = d[d["dt"] <= CANONICAL_END]
    r2225_d = d[d["dt"] <= pd.Timestamp("2025-12-31")]
    ext_d = d[d["dt"] > CANONICAL_END]
    for dd_, scope in [(canon_d, "canonical"), (r2225_d, "2022-2025_LOYO"), (ext_d, "extension_JunJul2026_obs")]:
        gsess = dd_.groupby("sess")["pnl"].sum().reset_index()
        r = battery_row(f"{tag}_{scope}_GENUINE", gsess["sess"], gsess["pnl"].to_numpy())
        r["candidate"] = tag; r["scope"] = scope; r["pricing"] = "GENUINE_MNQ"
        battery_rows.append(r)
    for yr in [2022, 2023, 2024, 2025, 2026]:
        yd = d[(d["dt"].dt.year == yr) & (d["dt"] <= CANONICAL_END)]
        if len(yd) == 0:
            continue
        gsess = yd.groupby("sess")["pnl"].sum().reset_index()
        yr_row = battery_row(f"{tag}_{yr}_GENUINE", gsess["sess"], gsess["pnl"].to_numpy())
        yr_row["candidate"] = tag; yr_row["year"] = yr; yr_row["pricing"] = "GENUINE_MNQ"
        year_rows.append(yr_row)
    # save genuine-MNQ daily series for downstream use (capital frontier, intraday DD, forward-readiness)
    gsess_full = d.groupby("sess")["pnl"].sum().reset_index()
    gsess_full.columns = ["sess", "net"]
    gsess_full.to_csv(os.path.join(OUT, f"{tag}_daily_GENUINE_MNQ.csv"), index=False)

battery_df = pd.DataFrame(battery_rows)
year_df = pd.DataFrame(year_rows)
battery_df.to_csv(os.path.join(OUT, "u6b_mnq_grid_battery.csv"), index=False)
year_df.to_csv(os.path.join(OUT, "u6b_mnq_year_by_year.csv"), index=False)

print("\n[U6B-MNQ] ==== GENUINE-MNQ GRID BATTERY ====")
print(battery_df[["candidate", "scope", "net", "sharpe", "sortino", "calmar", "maxDD_eod", "CDaR95",
                   "worst_day", "worst_month", "pos_day_pct"]].to_string(index=False))

recon = {
    "exposure_path_identical_legacy_vs_genuine": identity_check,
    "correctness_gate": {"control_legacy_canonical_net": ctrl_leg_canon, "certified": 177924.40},
    "headline": headline.to_dict(orient="records"),
    "delta_2022_2025_vs_control": delta_df.to_dict(orient="records"),
    "n_mnq_genuine_bars": int(is_mnq_genuine.sum()), "n_bars": int(n),
}
with open(os.path.join(OUT, "u6b_mnq_repricing_recon.json"), "w") as fh:
    json.dump(recon, fh, indent=2, default=float)
print("\n[U6B-MNQ] RECON:")
print(json.dumps(recon, indent=2, default=float))
print("\n[U6B-MNQ] genuine-MNQ dual-truth repricing complete.")
