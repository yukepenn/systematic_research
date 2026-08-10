"""GRID02 -- Solar member scale-range ENDPOINT perturbation. DIAGNOSTIC SCIENCE ONLY (campaign
directive sec97-98): report all results, select no winner, promote nothing. This script can
NEVER by itself create a new baseline candidate.

Member COUNT (13) and SPACING (2) held fixed; only the [lo, hi] endpoints of the VolMult scale
range move, one predefined step in each direction:
  [5,29]:  [5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29]
  [6,30]:  [6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30]   (INCUMBENT, center, == GRID01's G13)
  [7,31]:  [7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31]

Reuses grid_core.py verbatim (same shared substrate as GRID01: build_pend/member_states/
member_trades UNMODIFIED, B-MOM leg / HTF tilt / C4 clocks / Product A+B decoder constants all
held EXACTLY at governed values). Reports center vs each neighbor with the identical metric set
GRID01 uses, and explicitly names which neighbor is "worst" (largest deviation from center)
WITHOUT treating that as informative beyond the robustness question this axis is built to probe:
does the system monetize a broad VolMult scale band, or a narrow one anchored precisely at
[6,30]? Endpoints are NOT optimized -- only these three predefined choices are reported.
"""
import os, sys, json
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                                 "GRID01_SOLAR_RESOLUTION_CONVERGENCE", "src"))
import grid_core as G

OUT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "out")
os.makedirs(OUT, exist_ok=True)

GRIDS = {
    "endpoint_5_29": list(range(5, 30, 2)),    # 5,7,...,29 -- 13 members
    "endpoint_6_30": list(G.INCUMBENT_VMS),    # 6,8,...,30 -- 13 members, CENTER (== GRID01 G13)
    "endpoint_7_31": list(range(7, 32, 2)),    # 7,9,...,31 -- 13 members
}
CENTER = "endpoint_6_30"

for k, v in GRIDS.items():
    assert len(v) == 13, f"{k} has {len(v)} members, expected 13 (spacing must stay fixed at 2)"

WINDOWS = {
    "CANONICAL_2023_2025": G.CANON_MASK,   # CLAUDE.md primary reporting window
    "FULL_2022_2026": G.FULL_MASK,         # fuller available history (repo's own dev+health extent)
}

print(f"[GRID02] grids: " + ", ".join(f"{k}={v[0]}..{v[-1]}" for k, v in GRIDS.items()), flush=True)

# ---------------------------------------------------------------- build every grid's substrate
RESULTS = {}
for name, vms in GRIDS.items():
    print(f"[GRID02] building {name} ({len(vms)} members, span [{vms[0]},{vms[-1]}]) ...", flush=True)
    PEND, T, consensus = G.build_grid(vms)
    barposA1, bpnlA1, M_A = G.product_a_exec(T, ticks=1)
    barposA2, bpnlA2, _ = G.product_a_exec(T, ticks=2)
    barposA3, bpnlA3, _ = G.product_a_exec(T, ticks=3)
    posB, barposB1, bpnlB1, M_B = G.product_b_exec(T, ticks=1)
    _, _, bpnlB2, _ = G.product_b_exec(T, ticks=2)
    _, _, bpnlB3, _ = G.product_b_exec(T, ticks=3)
    daily_e10 = G.sm.e10_sim(G._bars, T)
    RESULTS[name] = dict(
        vms=vms, PEND=PEND, T=T, consensus=consensus,
        barposA=(barposA1, barposA2, barposA3), bpnlA=(bpnlA1, bpnlA2, bpnlA3),
        posB=posB, barposB=barposB1, bpnlB=(bpnlB1, bpnlB2, bpnlB3),
        daily_e10=daily_e10,
    )

ref = RESULTS[CENTER]


# ---------------------------------------------------------------- comparison metrics vs center
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
            "window": wname, "grid": name, "span": f"[{res['vms'][0]},{res['vms'][-1]}]",
            "consensus_score_corr": consensus_corr, "consensus_sign_agree_pct": sign_agree,
            "T_target_corr": T_corr, "T_target_exact_agree_pct": T_exact,
            "productA_position_corr": pA_corr, "productA_position_exact_agree_pct": pA_exact,
            "productB_desired_pos_corr": pB_corr, "productB_desired_pos_exact_agree_pct": pB_exact,
            "productB_n_entries": len(ent_x), "productB_n_entries_center": len(ent_ref),
            "productB_n_common_entries": len(inter), "productB_entry_jaccard": jaccard,
            "productA_daily_pnl_corr": dA_corr, "productB_daily_pnl_corr": dB_corr,
        })

agreement_df = pd.DataFrame(agreement_rows)
agreement_df.to_csv(os.path.join(OUT, "grid02_state_agreement_vs_center.csv"), index=False)
print(f"[GRID02] wrote grid02_state_agreement_vs_center.csv ({len(agreement_df)} rows)", flush=True)


# ---------------------------------------------------------------- performance table
def perf_row(window, grid, product, bpnl_base, bpnl_t2, bpnl_t3, mask, n_entries):
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
perf_df.to_csv(os.path.join(OUT, "grid02_performance.csv"), index=False)
print(f"[GRID02] wrote grid02_performance.csv ({len(perf_df)} rows)", flush=True)

# ---------------------------------------------------------------- deviation-from-center summary
# "worst" = largest |deviation| from center on canonical-window net P&L, per product. Reported
# for the robustness question only -- NOT treated as a ranking/selection signal.
dev_rows = []
canon_perf = perf_df[perf_df["window"] == "CANONICAL_2023_2025"]
for product in ("ProductA", "ProductB"):
    sub = canon_perf[canon_perf["product"] == product].set_index("grid")
    center_net = sub.loc[CENTER, "net_base_1tick"]
    for name in GRIDS:
        if name == CENTER:
            continue
        net = sub.loc[name, "net_base_1tick"]
        dev_rows.append({
            "product": product, "grid": name, "span": f"[{GRIDS[name][0]},{GRIDS[name][-1]}]",
            "net": net, "center_net": center_net,
            "abs_deviation_dollars": abs(net - center_net),
            "pct_deviation": (net - center_net) / center_net if center_net != 0 else float("nan"),
        })
dev_df = pd.DataFrame(dev_rows)
worst_by_product = {}
for product, g in dev_df.groupby("product"):
    worst_row = g.loc[g["abs_deviation_dollars"].idxmax()]
    worst_by_product[product] = {"grid": worst_row["grid"], "span": worst_row["span"],
                                  "abs_deviation_dollars": float(worst_row["abs_deviation_dollars"]),
                                  "pct_deviation": float(worst_row["pct_deviation"])}
dev_df.to_csv(os.path.join(OUT, "grid02_deviation_from_center.csv"), index=False)
print(f"[GRID02] wrote grid02_deviation_from_center.csv; worst-deviation neighbor per product "
      f"(descriptive only, not a selection signal): {worst_by_product}", flush=True)

# ---------------------------------------------------------------- full detail JSON
full_detail = {
    "grids": {k: v for k, v in GRIDS.items()},
    "center_grid": CENTER,
    "windows": {k: {"n_bars": int(v.sum())} for k, v in WINDOWS.items()},
    "canonical_window": {"start": str(G.CANON_START.date()), "end": str(G.CANON_END.date())},
    "full_window": {"start": str(pd.to_datetime(G.SD.min())), "end": str(pd.to_datetime(G.SD.max()))},
    "constants_held_fixed": {
        "sigma_vol_period": 460, "member_count": 13, "member_spacing": 2,
        "productA": {"KSolar": G.KSOLAR, "KBmom": G.KBMOM, "TiltRescale": G.TILTRESCALE,
                     "TiltMult": G.TILTMULT, "ShortHalf": G.SHORTHALF, "TiltSma": 50},
        "productB": {"WSolar": G.WSOLAR, "WBmom": G.WBMOM, "TiltRescale": G.TILTRESCALE,
                     "TiltMult": G.TILTMULT, "TiltSma": 50,
                     "EntryLevel": G.ENTRY_LEVEL, "ExitLevel": G.EXIT_LEVEL},
        "BAND_DAYS_bmom": 14,
    },
    "self_check": {"productA_dev_net": 177924.40, "productB_dev_net": 301915.92,
                    "dev_window_end": str(G.DEV_END.date())},
    "state_agreement_vs_center": agreement_rows,
    "performance": perf_rows,
    "deviation_from_center_canonical_window": dev_rows,
    "worst_deviation_neighbor_per_product_DESCRIPTIVE_ONLY": worst_by_product,
}
with open(os.path.join(OUT, "grid02_full_detail.json"), "w") as f:
    json.dump(full_detail, f, indent=2, default=str)
print("[GRID02] wrote grid02_full_detail.json", flush=True)

# ---------------------------------------------------------------- console summary
print("\n=== GRID02 canonical-window summary (vs center [6,30]) ===")
canon_agree = agreement_df[agreement_df["window"] == "CANONICAL_2023_2025"]
print(canon_agree[["grid", "span", "consensus_score_corr", "consensus_sign_agree_pct",
                    "T_target_exact_agree_pct", "productB_entry_jaccard",
                    "productA_daily_pnl_corr", "productB_daily_pnl_corr"]].to_string(index=False))
print("\n" + canon_perf[["grid", "product", "net_base_1tick", "sharpe", "maxDD_eod",
                          "retention_plus1tick", "retention_plus2tick"]].to_string(index=False))
print(f"\nworst-deviation neighbor per product (descriptive only): {worst_by_product}")
print("\n[GRID02] DIAGNOSTIC SCIENCE ONLY -- endpoints NOT optimized, no winner selected, "
      "nothing promoted.")
