"""SM05_BMOM_PORTFOLIO — portfolio measurement per runs/SM05_BMOM_PORTFOLIO/spec.yaml.

Frozen protocol: union session calendar 2022-01..2026-05-31, zero-fill; each leg
vol-matched to SOLAR dev daily vol; risk-share grid [0,.2,.25,.333,.4,.5] per
challenger + three-way (thirds, 0.5/0.3/0.2); every portfolio rescaled to SOLAR
dev vol before metrics; block bootstrap (5, 10000, seed 20260808) dSharpe/dlogG;
H1 2022-01..2024-03 / H2 2024-04..2026-05 sign check; preregistered gates applied
mechanically. Outputs -> runs/SM05_BMOM_PORTFOLIO/out/.
"""
import sys, os, json
import numpy as np
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
from sm_metrics import metrics, block_bootstrap_delta, ANN, BASE, _dd_series

OUT = os.path.join(ROOT, "runs", "SM05_BMOM_PORTFOLIO", "out")
os.makedirs(OUT, exist_ok=True)

DEV_START = pd.Timestamp("2022-01-01")
DEV_END   = pd.Timestamp("2026-05-31")
H1_END    = pd.Timestamp("2024-03-31")
SEED, BLOCK, NBOOT = 20260808, 5, 10000

# ---------------- load legs ----------------
solar = pd.read_csv(os.path.join(ROOT, "runs", "SM01_SUBSTRATE", "out", "e10_daily_py.csv"),
                    parse_dates=["sess"])
solar_dev = solar[(solar.sess >= DEV_START) & (solar.sess <= DEV_END)].set_index("sess")["net"]

bmom = pd.read_csv(os.path.join(ROOT, "research", "scalping_lab", "artifacts", "w8_bmom",
                                "w8bmom_w14_daily.csv"), parse_dates=["sess"])
bmom_dev = bmom[(bmom.sess >= DEV_START) & (bmom.sess <= DEV_END)].set_index("sess")["net_c1_usd"]

b1 = pd.read_csv(os.path.join(ROOT, "research", "scalping_lab", "artifacts", "w9_b1",
                              "w9b1_nightly.csv"), parse_dates=["exit_session_date"])
b1["usd"] = b1["net2.0_usd"]  # $ at 2.0t friction, $5/tick (verified: net2.0_t*5)
b1_dev_rows = b1[(b1.exit_session_date >= DEV_START) & (b1.exit_session_date <= DEV_END)]
b1_dev = b1_dev_rows.groupby("exit_session_date")["usd"].sum()
b1_dup_nights = int(b1_dev_rows.groupby("exit_session_date").size().gt(1).sum())

# historical (pre-2022) diagnostics
bmom_hist = pd.read_csv(os.path.join(ROOT, "research", "scalping_lab", "artifacts",
                                     "w10_bmom_hist", "w10bmom_daily.csv"), parse_dates=["sess"])
bmom_hist = bmom_hist[bmom_hist.sess < DEV_START].set_index("sess")["net_c1_usd"]
b1_hist_rows = b1[b1.exit_session_date < DEV_START]
b1_hist = b1_hist_rows.groupby("exit_session_date")["usd"].sum()

# B-FADE appendix (in-sample-characterized, correlation only)
bfade = pd.read_csv(os.path.join(ROOT, "research", "scalping_lab", "artifacts", "w8_bfade",
                                 "w8bfade_trades.csv"), parse_dates=["date"])
bfade_rel = bfade[bfade.group == "release"].copy()

# ---------------- union dev calendar, zero-fill ----------------
cal = pd.DatetimeIndex(sorted(set(solar_dev.index) | set(bmom_dev.index) | set(b1_dev.index)))
S = solar_dev.reindex(cal).fillna(0.0)
M = bmom_dev.reindex(cal).fillna(0.0)
B = b1_dev.reindex(cal).fillna(0.0)

solar_sd = S.std(ddof=1)
sM = solar_sd / M.std(ddof=1)
sB = solar_sd / B.std(ddof=1)

facts = {
    "n_union_sessions": int(len(cal)),
    "cal_start": str(cal[0].date()), "cal_end": str(cal[-1].date()),
    "n_solar_active": int((solar_dev != 0).sum()), "n_solar_sessions": int(len(solar_dev)),
    "n_bmom_active": int(len(bmom_dev)), "n_b1_nights": int(len(b1_dev_rows)),
    "n_b1_exit_sessions": int(len(b1_dev)), "b1_dup_exit_sessions": b1_dup_nights,
    "solar_dev_daily_sd": float(solar_sd),
    "bmom_daily_sd": float(M.std(ddof=1)), "b1_daily_sd": float(B.std(ddof=1)),
    "scale_bmom_to_solar_vol": float(sM), "scale_b1_to_solar_vol": float(sB),
    "sessions_only_bmom_or_b1_not_solar": int(len(set(cal) - set(solar_dev.index))),
}

# ---------------- (1) standalone metrics ----------------
rows = []
for name, ser, sc in [("SOLAR", S, 1.0), ("BMOM", M, sM), ("B1", B, sB)]:
    r = {"leg": name, "scaling": "unscaled", "scale": 1.0}
    r.update(metrics(ser)); rows.append(r)
    r = {"leg": name, "scaling": "vol_matched_to_solar", "scale": float(sc)}
    r.update(metrics(ser * sc)); rows.append(r)
standalone = pd.DataFrame(rows)
standalone.to_csv(os.path.join(OUT, "standalone_metrics.csv"), index=False)

# ---------------- helpers ----------------
def sharpe_stat(v):
    sd = v.std(ddof=1)
    return v.mean() / sd * np.sqrt(ANN) if sd > 0 else 0.0

def logG_stat(v):
    return float(np.log(max(BASE + v.sum(), 1.0) / BASE))

def make_port(w_solar, legs):  # legs: list of (weight, scaled_series)
    raw = w_solar * S
    for w, ser in legs:
        raw = raw + w * ser
    rescale = solar_sd / raw.std(ddof=1)
    return raw * rescale, float(rescale)

solar_only = metrics(S)
Sh1, Sh2 = S[S.index <= H1_END], S[S.index > H1_END]

W_GRID = [0.0, 0.2, 0.25, 1.0/3.0, 0.4, 0.5]
cells = []  # (label, challenger, w_label, port_series, rescale, leg_weights_desc)
for chal_name, ser_scaled in [("BMOM", M * sM), ("B1", B * sB)]:
    for w in W_GRID:
        port, rs = make_port(1.0 - w, [(w, ser_scaled)])
        cells.append((f"SOLAR+{chal_name} w={w:.3f}", chal_name, round(w, 3), port, rs))
p3a, rs3a = make_port(1/3, [(1/3, M * sM), (1/3, B * sB)])
cells.append(("SOLAR+BMOM+B1 thirds", "3WAY_THIRDS", 0.333, p3a, rs3a))
p3b, rs3b = make_port(0.5, [(0.3, M * sM), (0.2, B * sB)])
cells.append(("SOLAR+BMOM+B1 0.5/0.3/0.2", "3WAY_532", 0.5, p3b, rs3b))

# ---------------- (2)+(4) grid metrics + bootstrap + halves + gates ----------------
Sv = S.to_numpy()
grid_rows = []
for label, chal, w, port, rs in cells:
    r = {"portfolio": label, "challenger": chal, "risk_share_w": w, "port_rescale": rs}
    r.update(metrics(port))
    is_base = (w == 0.0)
    Pv = port.to_numpy()
    if not is_base:
        bs_sh = block_bootstrap_delta(Pv, Sv, block=BLOCK, n_boot=NBOOT, seed=SEED, stat=sharpe_stat)
        bs_lg = block_bootstrap_delta(Pv, Sv, block=BLOCK, n_boot=NBOOT, seed=SEED, stat=logG_stat)
        Ph1, Ph2 = port[port.index <= H1_END], port[port.index > H1_END]
        r.update({
            "dSharpe": bs_sh["delta"], "p_dSharpe_leq0": bs_sh["p_leq_0"],
            "dSharpe_ci_lo": bs_sh["ci_lo"], "dSharpe_ci_hi": bs_sh["ci_hi"],
            "dlogG": bs_lg["delta"], "p_dlogG_leq0": bs_lg["p_leq_0"],
            "dlogG_ci_lo": bs_lg["ci_lo"], "dlogG_ci_hi": bs_lg["ci_hi"],
            "dSharpe_H1": sharpe_stat(Ph1.to_numpy()) - sharpe_stat(Sh1.to_numpy()),
            "dSharpe_H2": sharpe_stat(Ph2.to_numpy()) - sharpe_stat(Sh2.to_numpy()),
            "dlogG_H1": logG_stat(Ph1.to_numpy()) - logG_stat(Sh1.to_numpy()),
            "dlogG_H2": logG_stat(Ph2.to_numpy()) - logG_stat(Sh2.to_numpy()),
        })
        r["gate_logG"] = r["logG_100k"] > solar_only["logG_100k"]
        r["gate_calmar"] = r["calmar"] > solar_only["calmar"]
        r["gate_worst_month"] = r["worst_month"] > solar_only["worst_month"]
        r["gate_h1h2_same_sign"] = (r["dlogG_H1"] > 0) and (r["dlogG_H2"] > 0)
        r["gate_boot_p10"] = (r["p_dlogG_leq0"] < 0.10) and (r["p_dSharpe_leq0"] < 0.10)
        r["cell_pass"] = all(r[k] for k in ["gate_logG", "gate_calmar", "gate_worst_month",
                                            "gate_h1h2_same_sign", "gate_boot_p10"])
    grid_rows.append(r)
grid = pd.DataFrame(grid_rows)
grid.to_csv(os.path.join(OUT, "portfolio_grid.csv"), index=False)

# plateau check (>=3 adjacent passing cells among w>0 grid, per challenger)
plateau = {}
for chal in ["BMOM", "B1"]:
    sub = grid[(grid.challenger == chal) & (grid.risk_share_w > 0)].sort_values("risk_share_w")
    passes = sub["cell_pass"].fillna(False).astype(bool).to_list()
    best, cur = 0, 0
    for p in passes:
        cur = cur + 1 if p else 0
        best = max(best, cur)
    plateau[chal] = {"passes": passes, "max_adjacent_run": best, "plateau_met": best >= 3}

# ---------------- (3) diversification scorecard ----------------
def scorecard(name, C):
    wS, wC = S.resample("W").sum(), C.resample("W").sum()
    lose_d = S < 0
    lose_w = wS < 0
    worst20 = S.nsmallest(20).index
    top20S, top20C = set(S.nlargest(20).index), set(C.nlargest(20).index)
    ddS = _dd_series(np.cumsum(S.to_numpy()))
    ddC = _dd_series(np.cumsum(C.to_numpy()))
    return {
        "challenger": name,
        "rho_full": float(np.corrcoef(S, C)[0, 1]),
        "rho_solar_losing_days": float(np.corrcoef(S[lose_d], C[lose_d])[0, 1]),
        "n_solar_losing_days": int(lose_d.sum()),
        "rho_solar_losing_weeks": float(np.corrcoef(wS[lose_w], wC[lose_w])[0, 1]),
        "n_solar_losing_weeks": int(lose_w.sum()),
        "frac_solar_worst20_challenger_geq0": float((C.loc[worst20] >= 0).mean()),
        "n_worst20_active": int((C.loc[worst20] != 0).sum()),
        "dd_series_corr": float(np.corrcoef(ddS, ddC)[0, 1]),
        "top20_day_overlap_count": int(len(top20S & top20C)),
    }

score = pd.DataFrame([
    scorecard("BMOM", M),
    scorecard("B1", B),
    scorecard("BMOM+B1_equal_risk_sleeve", 0.5 * sM * M + 0.5 * sB * B),
])
score.to_csv(os.path.join(OUT, "diversification_scorecard.csv"), index=False)

# ---------------- (5) TRANSITION/HISTORICAL diagnostic ----------------
hcal = pd.DatetimeIndex(sorted(set(bmom_hist.index) | set(b1_hist.index)))
Mh = bmom_hist.reindex(hcal).fillna(0.0)
Bh = b1_hist.reindex(hcal).fillna(0.0)
hist_rows = []
for name, ser in [
    ("BMOM_hist_unscaled", Mh),
    ("B1_hist_unscaled", Bh),
    ("BMOM_hist_at_dev_scale", Mh * sM),
    ("B1_hist_at_dev_scale", Bh * sB),
    ("sleeve_2way_BMOM_w0.333", (1/3) * sM * Mh),
    ("sleeve_2way_B1_w0.333", (1/3) * sB * Bh),
    ("sleeve_3way_thirds_challenger_side", (1/3) * (sM * Mh) + (1/3) * (sB * Bh)),
]:
    r = {"series": name}
    r.update(metrics(ser))
    hist_rows.append(r)
hist = pd.DataFrame(hist_rows)
hist.to_csv(os.path.join(OUT, "historical_diagnostic.csv"), index=False)
hist_facts = {
    "hist_cal": f"{hcal[0].date()}..{hcal[-1].date()}", "n_hist_sessions": int(len(hcal)),
    "bmom_hist_active": int(len(bmom_hist)), "b1_hist_nights": int(len(b1_hist_rows)),
}

# ---------------- (6) improvement table ----------------
IMP_COLS = ["worst_month", "roll60_min", "tuw_frac", "longest_losing_day_streak",
            "longest_losing_week_streak", "longest_losing_month_streak",
            "max_dd", "longest_recovery_sessions", "worst_week", "es5_daily"]
imp = grid[["portfolio", "challenger", "risk_share_w"] + IMP_COLS].copy()
base = {c: solar_only[c] for c in IMP_COLS}
for c in IMP_COLS:
    imp[f"d_{c}"] = imp[c] - base[c]
imp.to_csv(os.path.join(OUT, "improvement_table.csv"), index=False)

# ---------------- (7) B-FADE appendix: correlation only ----------------
bf_rows = []
for h in [15, 30, 60]:
    d = bfade_rel.set_index("date")[f"net{h}"] * 5.0  # ticks -> $ ($5/tick NQ)
    d = d[(d.index >= DEV_START) & (d.index <= DEV_END)]
    F = d.reindex(cal).fillna(0.0)
    act = F != 0
    bf_rows.append({
        "horizon_min": h, "n_release_days": int(len(d)),
        "rho_full_calendar": float(np.corrcoef(S, F)[0, 1]),
        "rho_active_days_only": float(np.corrcoef(S[act], F[act])[0, 1]) if act.sum() > 2 else np.nan,
    })
bfade_corr = pd.DataFrame(bf_rows)

# ---------------- report ----------------
solar_m = standalone[(standalone.leg == "SOLAR") & (standalone.scaling == "unscaled")].iloc[0]

def fm(x, n=2):
    return "n/a" if pd.isna(x) else f"{x:,.{n}f}"

L = []
L.append("# SM05_BMOM_PORTFOLIO — B-MOM / B1 portfolio measurement vs SOLAR (dev window)\n")
L.append(f"Spec: `runs/SM05_BMOM_PORTFOLIO/spec.yaml` (frozen 2026-08-08). Type: MEASUREMENT — full grid reported, no selection.")
L.append(f"Window: union session calendar {facts['cal_start']} .. {facts['cal_end']} ({facts['n_union_sessions']} sessions), zero-filled.")
L.append(f"Seed {SEED}, block {BLOCK}, B={NBOOT}. Metrics: `src/analytics/sm_metrics.py` (ann 252, ddof 1, logG base $100k).\n")
L.append("## Legs and normalization (FACT)")
L.append(f"- SOLAR = E10 daily (`runs/SM01_SUBSTRATE/out/e10_daily_py.csv`), {facts['n_solar_sessions']} sessions <= 2026-05-31; dev daily sd = ${fm(facts['solar_dev_daily_sd'])}.")
L.append(f"- BMOM = W8-1 frozen rule daily net_c1_usd (`w8bmom_w14_daily.csv`), {facts['n_bmom_active']} active sessions; sd ${fm(facts['bmom_daily_sd'])}; vol-match scale x{fm(facts['scale_bmom_to_solar_vol'],4)}.")
L.append(f"- B1 = W9-1 nightly net at 2.0t (`w9b1_nightly.csv`, net2.0_usd = net2.0_t x $5), keyed by exit session; {facts['n_b1_nights']} dev nights -> {facts['n_b1_exit_sessions']} exit sessions ({facts['b1_dup_exit_sessions']} sessions with >1 night); sd ${fm(facts['b1_daily_sd'])}; vol-match scale x{fm(facts['scale_b1_to_solar_vol'],4)}.")
L.append(f"- Sessions in union calendar not in SOLAR ledger: {facts['sessions_only_bmom_or_b1_not_solar']}.")
L.append("- Every portfolio = (1-w)*SOLAR + w*(vol-matched challenger), then the whole portfolio rescaled to SOLAR dev vol before metrics (CONVENTIONS 6.7 risk-normalized growth).\n")
L.append("## (1) Standalone legs (see `standalone_metrics.csv`)")
L.append("| leg | scaling | net | logG_100k | sharpe | calmar | max_dd | worst_month | pos_day_frac |")
L.append("|---|---|---|---|---|---|---|---|---|")
for _, r in standalone.iterrows():
    L.append(f"| {r.leg} | {r.scaling} | {fm(r.net,0)} | {fm(r.logG_100k,4)} | {fm(r.sharpe,3)} | {fm(r.calmar,3)} | {fm(r.max_dd,0)} | {fm(r.worst_month,0)} | {fm(r.pos_day_frac,3)} |")
L.append("")
L.append("## (2) Full risk-share grid (`portfolio_grid.csv`) — FULL GRID, NO SELECTION")
L.append("| portfolio | w | logG_100k | sharpe | calmar | max_dd | worst_month | roll60_min | tuw | dSharpe | p(dSh<=0) | dlogG | p(dlogG<=0) | dlogG_H1 | dlogG_H2 | PASS |")
L.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
for _, r in grid.iterrows():
    if r.risk_share_w == 0:
        L.append(f"| {r.portfolio} (baseline=SOLAR) | 0 | {fm(r.logG_100k,4)} | {fm(r.sharpe,3)} | {fm(r.calmar,3)} | {fm(r.max_dd,0)} | {fm(r.worst_month,0)} | {fm(r.roll60_min,0)} | {fm(r.tuw_frac,3)} | — | — | — | — | — | — | — |")
    else:
        L.append(f"| {r.portfolio} | {r.risk_share_w} | {fm(r.logG_100k,4)} | {fm(r.sharpe,3)} | {fm(r.calmar,3)} | {fm(r.max_dd,0)} | {fm(r.worst_month,0)} | {fm(r.roll60_min,0)} | {fm(r.tuw_frac,3)} | {fm(r.dSharpe,3)} | {fm(r.p_dSharpe_leq0,4)} | {fm(r.dlogG,4)} | {fm(r.p_dlogG_leq0,4)} | {fm(r.dlogG_H1,4)} | {fm(r.dlogG_H2,4)} | {'PASS' if r.cell_pass else 'fail'} |")
L.append("")
L.append("## (3) Diversification scorecard (`diversification_scorecard.csv`)")
L.append("| challenger | rho_full | rho Solar-losing days | rho Solar-losing weeks | frac worst-20 Solar days challenger>=0 | dd-series corr | top-20-day overlap |")
L.append("|---|---|---|---|---|---|---|")
for _, r in score.iterrows():
    L.append(f"| {r.challenger} | {fm(r.rho_full,4)} | {fm(r.rho_solar_losing_days,4)} (n={r.n_solar_losing_days}) | {fm(r.rho_solar_losing_weeks,4)} (n={r.n_solar_losing_weeks}) | {fm(r.frac_solar_worst20_challenger_geq0,2)} ({r.n_worst20_active}/20 active) | {fm(r.dd_series_corr,4)} | {r.top20_day_overlap_count}/20 |")
L.append("")
L.append("## (4) Preregistered gates — mechanical application (FACT)")
L.append("Gate (spec): cell passes iff portfolio improves risk-normalized logG AND Calmar AND worst-month vs SOLAR-only, H1/H2 dlogG same (positive) sign, bootstrap P(dSharpe<=0)<0.10 AND P(dlogG<=0)<0.10. Plateau = >=3 adjacent passing cells.")
for chal, p in plateau.items():
    L.append(f"- {chal}: cell passes at w=[0.2,0.25,0.333,0.4,0.5] -> {p['passes']}; max adjacent run {p['max_adjacent_run']}; plateau {'MET' if p['plateau_met'] else 'NOT met'}.")
L.append(f"- Three-way thirds cell_pass = {bool(grid[grid.challenger=='3WAY_THIRDS'].cell_pass.iloc[0])}; 0.5/0.3/0.2 cell_pass = {bool(grid[grid.challenger=='3WAY_532'].cell_pass.iloc[0])} (single points, no plateau concept).")
L.append("")
L.append("## (6) Worst-month / rolling-60 / TUW / streak improvement (`improvement_table.csv`)")
L.append(f"SOLAR baseline: worst_month {fm(solar_only['worst_month'],0)}, roll60_min {fm(solar_only['roll60_min'],0)}, tuw {fm(solar_only['tuw_frac'],3)}, streaks d/w/m {solar_only['longest_losing_day_streak']}/{solar_only['longest_losing_week_streak']}/{solar_only['longest_losing_month_streak']}, max_dd {fm(solar_only['max_dd'],0)}.")
L.append("| portfolio | d worst_month | d roll60_min | d tuw | d day-streak | d week-streak | d month-streak | d max_dd |")
L.append("|---|---|---|---|---|---|---|---|")
for _, r in imp[imp.risk_share_w > 0].iterrows():
    L.append(f"| {r.portfolio} | {fm(r.d_worst_month,0)} | {fm(r.d_roll60_min,0)} | {fm(r.d_tuw_frac,3)} | {int(r.d_longest_losing_day_streak)} | {int(r.d_longest_losing_week_streak)} | {int(r.d_longest_losing_month_streak)} | {fm(r.d_max_dd,0)} |")
L.append("")
L.append("## (5) TRANSITION/HISTORICAL diagnostic — pre-2022 challenger side (DIAGNOSTIC ONLY)")
L.append(f"LIMITATION (binding): SOLAR has no pre-2022 ledger, so no pre-2022 portfolio can be formed. What is reported is the CHALLENGER SIDE of the 0.333 portfolios — the $ stream the challenger sleeve would have contributed at the dev-frozen vol-match scales — on the pre-2022 union calendar {hist_facts['hist_cal']} ({hist_facts['n_hist_sessions']} sessions; BMOM {hist_facts['bmom_hist_active']} active days, B1 {hist_facts['b1_hist_nights']} nights). Labels: TRANSITION/HISTORICAL. See `historical_diagnostic.csv`.")
L.append("| series | net | logG_100k | sharpe | calmar | max_dd | worst_month |")
L.append("|---|---|---|---|---|---|---|")
for _, r in hist.iterrows():
    L.append(f"| {r.series} | {fm(r.net,0)} | {fm(r.logG_100k,4)} | {fm(r.sharpe,3)} | {fm(r.calmar,3)} | {fm(r.max_dd,0)} | {fm(r.worst_month,0)} |")
L.append("")
L.append("## (7) B-FADE appendix — daily overlay correlation ONLY")
L.append("IN-SAMPLE-CHARACTERIZED (W8-2 honesty clause; W9-3 verdict UNCONFIRMED-POSSIBLY-RECENT, parked). NO portfolio arithmetic performed or permitted from this table.")
L.append("| exit horizon | n release days | rho vs SOLAR (full calendar, zero-fill) | rho (active days only) |")
L.append("|---|---|---|---|")
for _, r in bfade_corr.iterrows():
    L.append(f"| {int(r.horizon_min)} min | {int(r.n_release_days)} | {fm(r.rho_full_calendar,4)} | {fm(r.rho_active_days_only,4)} |")
L.append("")
L.append("## Files")
L.append("- portfolio_grid.csv, diversification_scorecard.csv (spec outputs)")
L.append("- standalone_metrics.csv, improvement_table.csv, historical_diagnostic.csv, facts.json (supporting)")

with open(os.path.join(OUT, "report.md"), "w", encoding="utf-8") as f:
    f.write("\n".join(L) + "\n")
with open(os.path.join(OUT, "facts.json"), "w", encoding="utf-8") as f:
    json.dump({"facts": facts, "hist_facts": hist_facts, "plateau": plateau,
               "solar_only": {k: (float(v) if isinstance(v, (int, float, np.floating)) else v)
                              for k, v in solar_only.items()}}, f, indent=2, default=str)

print(json.dumps(facts, indent=2))
print(json.dumps(hist_facts, indent=2))
print(json.dumps(plateau, indent=2, default=str))
print("SOLAR:", {k: round(float(v), 4) for k, v in solar_only.items() if isinstance(v, (int, float, np.floating))})
print(grid[["portfolio", "risk_share_w", "logG_100k", "sharpe", "calmar", "worst_month",
            "dSharpe", "p_dSharpe_leq0", "dlogG", "p_dlogG_leq0", "dlogG_H1", "dlogG_H2",
            "cell_pass"]].to_string(index=False))
print(score.to_string(index=False))
print(bfade_corr.to_string(index=False))
print("DONE")
