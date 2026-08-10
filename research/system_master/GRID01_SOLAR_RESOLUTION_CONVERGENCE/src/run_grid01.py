"""GRID01 -- Solar member-resolution convergence. DIAGNOSTIC SCIENCE ONLY (campaign directive
sec97-98): report all results, select no winner, promote nothing. This script can NEVER by
itself create a new baseline candidate.

Four member grids, all mechanically defined BEFORE looking at any performance:
  G7:  [6, 10, 14, 18, 22, 26, 30]                          (7 members, incumbent spacing x2)
  G13: [6, 8, 10, ..., 30]                                  (13 members, INCUMBENT)
  G25: [6, 7, 8, ..., 30]                                   (25 members, every integer)
  G49: 24 uniformly-spaced non-integer half-steps 6.5..29.5 (spec-verify-disclosed, mechanically
       valid per exhaustive grep of member_states/member_trades + every NinjaScript VolMult
       consumer -- vol_mult is a genuine continuous double throughout; see
       research/system_master/PERT01_STRUCTURAL_INVARIANCE/out/00_spec_verify_notes.md sec3).
       Named "G49" per the task's own codename; it has 24 members, not 49 -- disclosed as-is.

For each grid: build the member ensemble (build_pend/member_states/member_trades UNMODIFIED,
only `vms` varies) -> feed the resulting consensus state through the CURRENT, unperturbed
Product A and Product B decoders -> compare against G13 (state correlation, sign agreement,
target/position agreement, Product-B entry-set Jaccard, daily P&L correlation) and report a
full performance table (net, Sharpe, Sortino, Calmar, maxDD, cost-stress retention at +1/+2
ticks/side, canonical commission as the base case). NO winner is selected.
"""
import os, sys, json
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
import grid_core as G

OUT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "out")
os.makedirs(OUT, exist_ok=True)

GRIDS = {
    "G7": [6, 10, 14, 18, 22, 26, 30],
    "G13": list(G.INCUMBENT_VMS),
    "G25": list(range(6, 31)),
    "G49": [round(6.5 + 1.0 * i, 1) for i in range(24)],   # 6.5..29.5, 24 members
}
REF = "G13"   # incumbent, comparison anchor

WINDOWS = {
    "CANONICAL_2023_2025": G.CANON_MASK,   # CLAUDE.md primary reporting window
    "FULL_2022_2026": G.FULL_MASK,         # fuller available history (repo's own dev+health extent)
}

print(f"[GRID01] grid sizes: " + ", ".join(f"{k}={len(v)}" for k, v in GRIDS.items()), flush=True)
for k, v in GRIDS.items():
    assert len(v) == len(set(v)), f"{k} has duplicate members"

# ---------------------------------------------------------------- build every grid's substrate
RESULTS = {}
for name, vms in GRIDS.items():
    print(f"[GRID01] building {name} ({len(vms)} members) ...", flush=True)
    PEND, T, consensus = G.build_grid(vms)
    barposA1, bpnlA1, M_A = G.product_a_exec(T, ticks=1)
    barposA2, bpnlA2, _ = G.product_a_exec(T, ticks=2)
    barposA3, bpnlA3, _ = G.product_a_exec(T, ticks=3)
    posB, barposB1, bpnlB1, M_B = G.product_b_exec(T, ticks=1)
    _, _, bpnlB2, _ = G.product_b_exec(T, ticks=2)
    _, _, bpnlB3, _ = G.product_b_exec(T, ticks=3)
    # raw Solar E10-only leg (context only, MNQ economics, ticks=1) -- NOT a required "product"
    daily_e10 = G.sm.e10_sim(G._bars, T)
    RESULTS[name] = dict(
        vms=vms, PEND=PEND, T=T, consensus=consensus,
        barposA=(barposA1, barposA2, barposA3), bpnlA=(bpnlA1, bpnlA2, bpnlA3),
        posB=posB, barposB=barposB1, bpnlB=(bpnlB1, bpnlB2, bpnlB3),
        daily_e10=daily_e10,
    )

ref = RESULTS[REF]


# ---------------------------------------------------------------- comparison metrics vs G13
def safe_corr(a, b, mask):
    a = np.asarray(a, dtype=float)[mask]; b = np.asarray(b, dtype=float)[mask]
    if a.std() == 0 or b.std() == 0:
        return float("nan")
    return float(np.corrcoef(a, b)[0, 1])


def entry_events(pos_arr, mask):
    sgn = np.sign(pos_arr)
    prev = np.r_[0, sgn[:-1]]
    is_entry = (sgn != 0) & (sgn != prev)
    idx = np.where(is_entry & mask)[0]
    return set(zip(idx.tolist(), sgn[idx].astype(int).tolist()))


def daily_corr(bpnl_x, bpnl_ref, mask):
    dx = G.daily_net(bpnl_x, mask); dr = G.daily_net(bpnl_ref, mask)
    idx = dx.index.intersection(dr.index)
    if len(idx) < 3:
        return float("nan")
    return float(np.corrcoef(dx.loc[idx].to_numpy(), dr.loc[idx].to_numpy())[0, 1])


agreement_rows = []
for wname, wmask in WINDOWS.items():
    for name, res in RESULTS.items():
        consensus_corr = safe_corr(res["consensus"], ref["consensus"], wmask)
        sign_agree = float((np.sign(res["consensus"])[wmask] == np.sign(ref["consensus"])[wmask]).mean())
        T_corr = safe_corr(res["T"], ref["T"], wmask)
        T_exact = float((res["T"][wmask] == ref["T"][wmask]).mean())
        pA_corr = safe_corr(res["barposA"][0], ref["barposA"][0], wmask)
        pA_exact = float((res["barposA"][0][wmask] == ref["barposA"][0][wmask]).mean())
        pB_corr = safe_corr(res["posB"], ref["posB"], wmask)
        pB_exact = float((res["posB"][wmask] == ref["posB"][wmask]).mean())
        ent_x = entry_events(res["posB"], wmask)
        ent_ref = entry_events(ref["posB"], wmask)
        inter = ent_x & ent_ref
        union = ent_x | ent_ref
        jaccard = float(len(inter) / len(union)) if union else float("nan")
        dA_corr = daily_corr(res["bpnlA"][0], ref["bpnlA"][0], wmask)
        dB_corr = daily_corr(res["bpnlB"][0], ref["bpnlB"][0], wmask)
        agreement_rows.append({
            "window": wname, "grid": name, "n_members": len(res["vms"]),
            "consensus_score_corr": consensus_corr, "consensus_sign_agree_pct": sign_agree,
            "T_target_corr": T_corr, "T_target_exact_agree_pct": T_exact,
            "productA_position_corr": pA_corr, "productA_position_exact_agree_pct": pA_exact,
            "productB_desired_pos_corr": pB_corr, "productB_desired_pos_exact_agree_pct": pB_exact,
            "productB_n_entries": len(ent_x), "productB_n_entries_G13": len(ent_ref),
            "productB_n_common_entries": len(inter), "productB_entry_jaccard": jaccard,
            "productA_daily_pnl_corr": dA_corr, "productB_daily_pnl_corr": dB_corr,
        })

agreement_df = pd.DataFrame(agreement_rows)
agreement_df.to_csv(os.path.join(OUT, "grid01_state_agreement_vs_G13.csv"), index=False)
print(f"[GRID01] wrote grid01_state_agreement_vs_G13.csv ({len(agreement_df)} rows)", flush=True)


# ---------------------------------------------------------------- performance table
def perf_row(window, grid, product, bpnl_base, bpnl_t2, bpnl_t3, mask, n_entries):
    """Full-detail performance row: every dd_battery field (house-frozen Sharpe/Sortino/Calmar/
    CDaR/ulcer/TUW/worst-month-quarter/streak battery) PLUS the cost-stress retention block."""
    b = dict(G.battery(bpnl_base, mask, label=f"{grid}_{product}_{window}"))
    b.pop("label", None)
    net_base = b.get("net", 0.0)
    d = G.daily_net(bpnl_base, mask)
    worst_day = float(d.min()) if len(d) else float("nan")
    net_t2 = float(np.asarray(bpnl_t2)[mask].sum())
    net_t3 = float(np.asarray(bpnl_t3)[mask].sum())
    ret2 = net_t2 / net_base if net_base != 0 else float("nan")
    ret3 = net_t3 / net_base if net_base != 0 else float("nan")
    row = {"window": window, "grid": grid, "product": product, "n_entries": n_entries,
           "worst_day": worst_day}
    row.update(b)
    row["net_base_1tick"] = row.pop("net")
    row["net_stress_plus1tick"] = net_t2
    row["net_stress_plus2tick"] = net_t3
    row["retention_plus1tick"] = ret2
    row["retention_plus2tick"] = ret3
    return row


perf_rows = []
for wname, wmask in WINDOWS.items():
    for name, res in RESULTS.items():
        entA = entry_events(res["barposA"][0], wmask)
        perf_rows.append(perf_row(wname, name, "ProductA", *res["bpnlA"], wmask, len(entA)))
        entB = entry_events(res["posB"], wmask)
        perf_rows.append(perf_row(wname, name, "ProductB", *res["bpnlB"], wmask, len(entB)))

perf_df = pd.DataFrame(perf_rows)
perf_df.to_csv(os.path.join(OUT, "grid01_performance.csv"), index=False)
print(f"[GRID01] wrote grid01_performance.csv ({len(perf_df)} rows)", flush=True)

# ---------------------------------------------------------------- Solar E10-only context (bonus, not a product)
e10_rows = []
for wname, wmask in WINDOWS.items():
    for name, res in RESULTS.items():
        d = res["daily_e10"]
        d_dt = pd.to_datetime(d["sess"])
        keep = d_dt.isin(pd.to_datetime(pd.Series(G.SD[wmask]).unique()))
        dd = d[keep.to_numpy()]
        if len(dd) == 0:
            continue
        b = G.dd_battery(pd.to_datetime(dd["sess"]), dd["net"].to_numpy(), label=f"{name}_{wname}")
        e10_rows.append({"window": wname, "grid": name, "n_days": b["n_days"], "net": b["net"],
                          "sharpe": b["sharpe"], "maxDD_eod": b["maxDD_eod"]})
e10_df = pd.DataFrame(e10_rows)
e10_df.to_csv(os.path.join(OUT, "grid01_solar_e10_only_context.csv"), index=False)
print(f"[GRID01] wrote grid01_solar_e10_only_context.csv ({len(e10_df)} rows) [context only, "
      f"MNQ economics, ticks=1, NOT one of the two required product decoders]", flush=True)


# ---------------------------------------------------------------- full detail JSON
full_detail = {
    "grids": {k: v for k, v in GRIDS.items()},
    "reference_grid": REF,
    "windows": {k: {"n_bars": int(v.sum())} for k, v in WINDOWS.items()},
    "canonical_window": {"start": str(G.CANON_START.date()), "end": str(G.CANON_END.date())},
    "full_window": {"start": str(pd.to_datetime(G.SD.min())), "end": str(pd.to_datetime(G.SD.max()))},
    "constants_held_fixed": {
        "sigma_vol_period": 460,
        "productA": {"KSolar": G.KSOLAR, "KBmom": G.KBMOM, "TiltRescale": G.TILTRESCALE,
                     "TiltMult": G.TILTMULT, "ShortHalf": G.SHORTHALF, "TiltSma": 50},
        "productB": {"WSolar": G.WSOLAR, "WBmom": G.WBMOM, "TiltRescale": G.TILTRESCALE,
                     "TiltMult": G.TILTMULT, "TiltSma": 50,
                     "EntryLevel": G.ENTRY_LEVEL, "ExitLevel": G.EXIT_LEVEL},
        "BAND_DAYS_bmom": 14,
    },
    "self_check": {"productA_dev_net": 177924.40, "productB_dev_net": 301915.92,
                    "dev_window_end": str(G.DEV_END.date())},
    "state_agreement_vs_G13": agreement_rows,
    "performance": perf_rows,
    "solar_e10_only_context": e10_rows,
}
with open(os.path.join(OUT, "grid01_full_detail.json"), "w") as f:
    json.dump(full_detail, f, indent=2, default=str)
print("[GRID01] wrote grid01_full_detail.json", flush=True)

# ---------------------------------------------------------------- console summary (canonical window)
print("\n=== GRID01 canonical-window summary (vs G13) ===")
canon_agree = agreement_df[agreement_df["window"] == "CANONICAL_2023_2025"]
print(canon_agree[["grid", "n_members", "consensus_score_corr", "consensus_sign_agree_pct",
                    "T_target_exact_agree_pct", "productB_entry_jaccard",
                    "productA_daily_pnl_corr", "productB_daily_pnl_corr"]].to_string(index=False))
canon_perf = perf_df[perf_df["window"] == "CANONICAL_2023_2025"]
print("\n" + canon_perf[["grid", "product", "net_base_1tick", "sharpe", "maxDD_eod",
                          "retention_plus1tick", "retention_plus2tick"]].to_string(index=False))
print("\n[GRID01] DIAGNOSTIC SCIENCE ONLY -- no winner selected, nothing promoted.")
