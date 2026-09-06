# G3_CLOSEHOUR_20260906  (ledger G00085, family GENESIS3_EVENT)
# Close-hour hedging-flow momentum, vol-gated. Frozen object per spec.yaml.
# Program-printed gate table; ALL cells reported; mechanical clauses only.
import io
import os
import sys
import numpy as np
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
RUN = os.path.join(ROOT, "runs", "G3_CLOSEHOUR_20260906")
OUT = os.path.join(RUN, "out")
os.makedirs(OUT, exist_ok=True)

SEAL = pd.Timestamp("2026-08-01")
SEED = 20260906
B_BOOT = 2000
BLOCK_L = 10

# Cost model. BASIS = MODELED ALL_IN (Lifetime commission $4.36/ctRT + spread band).
# Spec G5 names the {1,2}-tick band with ES $12.50/tick; family convention (G00072,
# same wave/family) reads the band as ticks PER SIDE and adds the commission -> ALL_IN.
COMM = 4.36
MKT = {
    # tick_pts, tick_usd, pt_usd
    "ES":  dict(tick_pts=0.25, tick_usd=12.50, pt_usd=50.0,
                path=os.path.join(ROOT, "runs", "SM1M_ES_SUBSTRATE", "out", "es_1m_2022_2026.parquet")),
    "RTY": dict(tick_pts=0.10, tick_usd=5.00, pt_usd=50.0,
                path=os.path.join(ROOT, "runs", "SM1M_RTY_SUBSTRATE", "out", "rty_1m_2022_2026.parquet")),
    "YM":  dict(tick_pts=1.00, tick_usd=5.00, pt_usd=5.0,
                path=os.path.join(ROOT, "runs", "SM1M_YM_SUBSTRATE", "out", "ym_1m_2022_2026.parquet")),
}
for m, d in MKT.items():
    d["cost_primary_usd"] = 2 * d["tick_usd"] + COMM          # 1 tick/side RT
    d["cost_stress_usd"] = 4 * d["tick_usd"] + COMM           # 2 ticks/side RT
    d["cost_primary_pts"] = d["cost_primary_usd"] / d["pt_usd"]
    d["cost_stress_pts"] = d["cost_stress_usd"] / d["pt_usd"]

buf = io.StringIO()
def P(s=""):
    print(s)
    buf.write(s + "\n")

HR = "=" * 100
P(HR)
P("G3_CLOSEHOUR_20260906  (ledger G00085, family GENESIS3_EVENT)")
P("Close-hour hedging-flow momentum, vol-gated -- frozen object: s = sign(close(15:00)-close(09:30));")
P("hold s from close(15:00) to close(16:00) cash close; 1 RT/day max.  EVIDENCE STATUS: DISCOVERY")
P("(substrates DISCOVERY_CONSUMED for other objects).  POINTS basis on back-adjusted 1-min substrates.")
P("Vol gate (PRIMARY arm), frozen mechanical reading of 'trailing-20-session daily range top half,")
P("causal': at session t, the most recently COMPLETED full session's range R(t-1) must lie in the top")
P("half of the trailing-20 completed-session window {R(t-20)..R(t-1)}, i.e. R(t-1) >= median of the 20.")
P("Full session = reaches the 16:00 cash-close stamp; range = full-session high-low (18:00->17:00 ET).")
P("Everything the gate reads is complete before the 15:00 decision bar: CAUSAL.")
P(f"cost arms (BASIS=MODELED ALL_IN = comm ${COMM:.2f} + spread, per ctRT): PRIMARY 1tk/side; STRESS 2tk/side")
for m, d in MKT.items():
    P(f"  {m:3s}: tick {d['tick_pts']} pt = ${d['tick_usd']:.2f}; ${d['pt_usd']:.0f}/pt; "
      f"PRIMARY ${d['cost_primary_usd']:.2f} RT = {d['cost_primary_pts']:.4f} pt; "
      f"STRESS ${d['cost_stress_usd']:.2f} RT = {d['cost_stress_pts']:.4f} pt")
P("")

# ---------------------------------------------------------------- load + session build
def build(m):
    d = MKT[m]
    df = pd.read_parquet(d["path"], columns=["time", "high", "low", "close"])
    tmax = df["time"].max()
    assert tmax < SEAL, f"SEAL VIOLATION {m}: max time {tmax}"
    mins = df["time"].dt.hour * 60 + df["time"].dt.minute
    sess = df["time"].dt.normalize() + pd.to_timedelta((mins > 17 * 60).astype(int), unit="D")
    df = df.assign(sess=sess, mins=mins)
    g = df.groupby("sess")
    agg = g.agg(high=("high", "max"), low=("low", "min"), nbars=("close", "size"))
    stamps = df[df["mins"].isin([9 * 60 + 30, 15 * 60, 16 * 60])]
    piv = stamps.pivot_table(index="sess", columns="mins", values="close", aggfunc="last")
    piv.columns = [f"c{c}" for c in piv.columns]
    agg = agg.join(piv)
    agg = agg[agg["nbars"] >= 30]
    assert agg.index.max() < SEAL, f"SEAL VIOLATION {m}: session {agg.index.max()}"
    # full sessions = reach the cash close (16:00 stamp); these define the range window
    full = agg[agg["c960"].notna()].copy()
    full["range"] = full["high"] - full["low"]
    r = full["range"].to_numpy()
    n = len(full)
    gate = np.full(n, np.nan)
    for i in range(20, n):
        w = r[i - 20:i]
        gate[i] = 1.0 if r[i - 1] >= np.median(w) else 0.0
    full["gate"] = gate
    elig = full[(full["gate"].notna()) & full["c570"].notna() & full["c900"].notna() & full["c960"].notna()].copy()
    elig["s"] = np.sign(elig["c900"] - elig["c570"])
    elig["r"] = elig["c960"] - elig["c900"]
    return agg, full, elig

data = {}
P("substrates (seal assert: all bars < 2026-08-01):")
for m in MKT:
    agg, full, elig = build(m)
    data[m] = dict(full=full, elig=elig)
    nz = int((elig["s"] == 0).sum())
    P(f"  {m:3s}: sessions(nbars>=30)={len(agg)}; full(16:00 stamp)={len(full)}; "
      f"eligible(gate defined + 09:30/15:00/16:00 stamps)={len(elig)} "
      f"({elig.index.min().date()} .. {elig.index.max().date()}); gated={int(elig['gate'].sum())}; s==0 days={nz}")
P("")

# ---------------------------------------------------------------- cells
CELLS = []  # (market, arm)
for m in MKT:
    for arm in ("gated", "ungated"):
        CELLS.append((m, arm))

def cell_series(m, arm, cost_key="cost_primary_pts"):
    """Per-eligible-session net pnl (points); traded mask."""
    e = data[m]["elig"]
    c = MKT[m][cost_key]
    live = (e["gate"] == 1.0) if arm == "gated" else pd.Series(True, index=e.index)
    traded = live & (e["s"] != 0)
    pnl = np.where(traded, e["s"] * e["r"] - c, 0.0)
    gross = np.where(traded, e["s"] * e["r"], 0.0)
    return pd.DataFrame({"net": pnl, "gross": gross, "traded": traded}, index=e.index)

rng = np.random.default_rng(SEED)

def block_boot_means(x, B=B_BOOT, L=BLOCK_L, rng=rng):
    """Circular moving-block bootstrap means of a 1-d chronological series."""
    n = len(x)
    nb = int(np.ceil(n / L))
    starts = rng.integers(0, n, size=(B, nb))
    idx = (starts[:, :, None] + np.arange(L)[None, None, :]) % n
    sample = x[idx.reshape(B, -1)[:, :n]]
    return sample.mean(axis=1)

# --- G1: MDE FIRST (printed before any observed mean) --------------------------------
P("[G1] MDE FIRST (session-block bootstrap SE over TRADED sessions; L=10, B=2000, seed 20260906)")
P("     printed before any observed mean.  MDE_sig = 1.96*SE; MDE_80 = 2.8016*SE (5% two-sided, 80% power)")
mde_rows = {}
for m, arm in CELLS:
    cs = cell_series(m, arm)
    x = cs.loc[cs["traded"], "net"].to_numpy()
    bm = block_boot_means(x)
    se = bm.std(ddof=1)
    sd = x.std(ddof=1)
    mde_rows[(m, arm)] = dict(n=len(x), sd=sd, se=se, mde_sig=1.96 * se, mde80=2.8016 * se)
    d = MKT[m]
    P(f"     {m:3s} {arm:7s}: n={len(x):5d}  SD={sd:8.4f} pt  SE_bb={se:7.4f} pt  "
      f"MDE_sig={1.96*se:7.4f} pt (${1.96*se*d['pt_usd']:7.2f})  MDE_80={2.8016*se:7.4f} pt (${2.8016*se*d['pt_usd']:7.2f})")
P("")

# --- family correlation / K_eff ------------------------------------------------------
fam = pd.DataFrame({f"{m}_{a}": cell_series(m, a)["net"] for m, a in CELLS})
cors = []
cols = fam.columns.tolist()
for i in range(len(cols)):
    for j in range(i + 1, len(cols)):
        pair = fam[[cols[i], cols[j]]].dropna()
        cors.append(pair[cols[i]].corr(pair[cols[j]]))
rho_bar = float(np.mean(cors))
K = 6
k_eff_raw = K / (1 + (K - 1) * rho_bar)
K_eff = float(min(K, max(1.0, k_eff_raw)))
alpha_corr = 0.05 / K_eff
P(f"[family] 6 cells; mean pairwise corr of daily net PnL rho_bar = {rho_bar:+.4f} over 15 pairs")
P(f"         K_eff = 6/(1+5*rho_bar) = {k_eff_raw:.3f} -> clamped to [1,6] = {K_eff:.3f}")
P(f"         K_eff-corrected one-sided alpha = 0.05/K_eff = {alpha_corr:.4f}  (right-tail pct threshold {100*alpha_corr:.2f}%)")
P("")

# --- observed cell table -------------------------------------------------------------
P("[cells] ALL 6 cells (PRIMARY = 1tk/side ALL_IN; per TRADED session; HEADLINE = gated-ES '<<')")
P("     market arm       n     gross_pt   net_pt    net_$/ses  total_net_$   CI95_net_pt(block)")
cell_stats = {}
csv_rows = []
for m, arm in CELLS:
    cs = cell_series(m, arm)
    x = cs.loc[cs["traded"], "net"].to_numpy()
    gx = cs.loc[cs["traded"], "gross"].to_numpy()
    bm = block_boot_means(x)
    lo, hi = np.percentile(bm, [2.5, 97.5])
    d = MKT[m]
    st = dict(n=len(x), gross=gx.mean(), net=x.mean(), net_usd=x.mean() * d["pt_usd"],
              total_usd=x.sum() * d["pt_usd"], ci_lo=lo, ci_hi=hi)
    cell_stats[(m, arm)] = st
    tag = "  <<" if (m, arm) == ("ES", "gated") else ""
    P(f"     {m:3s}   {arm:7s} {st['n']:5d}   {st['gross']:8.4f} {st['net']:8.4f}   {st['net_usd']:9.2f}  {st['total_usd']:11.2f}   [{lo:8.4f},{hi:8.4f}]{tag}")
    csv_rows.append(dict(market=m, arm=arm, n=st["n"], gross_mean_pt=st["gross"], net_mean_pt=st["net"],
                         net_mean_usd=st["net_usd"], total_net_usd=st["total_usd"],
                         ci95_lo_pt=lo, ci95_hi_pt=hi,
                         sd_pt=mde_rows[(m, arm)]["sd"], se_bb_pt=mde_rows[(m, arm)]["se"],
                         mde_sig_pt=mde_rows[(m, arm)]["mde_sig"], mde80_pt=mde_rows[(m, arm)]["mde80"]))
P("")

# --- shift null (shared draw across family) -----------------------------------------
elig_T = {m: len(data[m]["elig"]) for m in MKT}
Tmin = min(elig_T.values())
Ks = np.arange(1, Tmin)  # full enumeration of shared circular offsets
P(f"[null] circular-shift null: signal series rolled k sessions against fixed (return, gate);")
P(f"       SHARED offset k across all 6 cells per draw (dependence preserved); k = 1..{Tmin-1} FULLY ENUMERATED")
null_pct = {}
for m, arm in CELLS:
    e = data[m]["elig"]
    c = MKT[m]["cost_primary_pts"]
    s = e["s"].to_numpy()
    r = e["r"].to_numpy()
    live = (e["gate"].to_numpy() == 1.0) if arm == "gated" else np.ones(len(e), bool)
    obs = float(np.sum(np.where(live & (s != 0), s * r - c, 0.0)))
    T = len(s)
    nulls = np.empty(len(Ks))
    for ii, k in enumerate(Ks):
        ss = np.roll(s, k)
        nulls[ii] = np.sum(np.where(live & (ss != 0), ss * r - c, 0.0))
    pct = 100.0 * (1 + np.sum(nulls >= obs)) / (1 + len(Ks))
    null_pct[(m, arm)] = dict(obs_total=obs, pct=pct, null_mean=nulls.mean(), null_p95=np.percentile(nulls, 95))
    P(f"       {m:3s} {arm:7s}: obs total {obs:10.2f} pt; right-tail pct = {pct:6.2f}%  (null mean {nulls.mean():8.2f}, 95th {np.percentile(nulls,95):8.2f})")
P(f"       K_eff-corrected clearance bar (headline cell): pct <= {100*alpha_corr:.2f}%")
P("")

# --- G2 headline ---------------------------------------------------------------------
hs = cell_stats[("ES", "gated")]
hp = null_pct[("ES", "gated")]
g2_mean = hs["net"] > 0
g2_ci = hs["ci_lo"] > 0
g2_null = hp["pct"] <= 100 * alpha_corr
G2 = g2_mean and g2_ci and g2_null
P("[G2] HEADLINE gated-ES, PRIMARY after-cost:")
P(f"     mean net = {hs['net']:+.4f} pt = {hs['net_usd']:+.2f} $/session-traded (gross {hs['gross']:+.4f} pt); n={hs['n']}")
P(f"     clause 1 mean>0: {'PASS' if g2_mean else 'FAIL'};  clause 2 CI95 [{hs['ci_lo']:+.4f},{hs['ci_hi']:+.4f}] excludes 0 from above: {'PASS' if g2_ci else 'FAIL'}")
P(f"     clause 3 shift-null pct {hp['pct']:.2f}% <= {100*alpha_corr:.2f}%: {'PASS' if g2_null else 'FAIL'}")
P(f"     vs MDE_80 {mde_rows[('ES','gated')]['mde80']:.4f} pt: observed |mean| {abs(hs['net']):.4f} pt "
  f"{'>=' if abs(hs['net']) >= mde_rows[('ES','gated')]['mde80'] else '<'} MDE_80 (informational)")
P("")

# --- G3 coherence --------------------------------------------------------------------
P("[G3] coherence (classification, not veto for RTY/YM):")
sup = 0
for m in MKT:
    gn = cell_stats[(m, "gated")]["net"]
    un = cell_stats[(m, "ungated")]["net"]
    same = np.sign(gn) == np.sign(cell_stats[("ES", "gated")]["net"])
    if m != "ES" and gn > 0:
        sup += 1
    P(f"     {m:3s}: gated net {gn:+.4f} pt vs ungated net {un:+.4f} pt; gated-ungated = {gn-un:+.4f} pt; "
      f"gated sign {'+' if gn>0 else '-' if gn<0 else '0'}{' (same as ES-gated)' if same else ''}")
G3 = cell_stats[("ES", "gated")]["net"] >= cell_stats[("ES", "ungated")]["net"]
P(f"     RTY/YM gated-cell positive support: {sup}/2")
P(f"     clause (ES): gated >= ungated per-traded-session net: {'PASS' if G3 else 'FAIL'}")
P("")

# --- G4 chronology -------------------------------------------------------------------
P("[G4] chronology halves (gated-ES, PRIMARY after-cost)")
era_rows = []
era_means = {}
for m, arm in CELLS:
    cs = cell_series(m, arm)
    t = cs.loc[cs["traded"], "net"]
    e1 = t[t.index <= "2023-12-31"]
    e2 = t[t.index >= "2024-01-01"]
    era_means[(m, arm)] = (e1.mean(), e2.mean())
    era_rows.append(dict(market=m, arm=arm, era="2022-23", n=len(e1), net_mean_pt=e1.mean(),
                         net_mean_usd=e1.mean() * MKT[m]["pt_usd"]))
    era_rows.append(dict(market=m, arm=arm, era="2024-26", n=len(e2), net_mean_pt=e2.mean(),
                         net_mean_usd=e2.mean() * MKT[m]["pt_usd"]))
e1m, e2m = era_means[("ES", "gated")]
for m, arm in CELLS:
    a, b = era_means[(m, arm)]
    P(f"     {m:3s} {arm:7s}: 2022-23 net {a:+.4f} pt | 2024-26 net {b:+.4f} pt")
G4 = not (e1m < 0 and e2m < 0)
P(f"     clause (gated-ES): both-halves-negative = FAIL -> 2022-23 {e1m:+.4f}, 2024-26 {e2m:+.4f}: {'PASS' if G4 else 'FAIL'}")
P("")

# --- G5 cost -------------------------------------------------------------------------
css = cell_series("ES", "gated", "cost_stress_pts")
xs = css.loc[css["traded"], "net"].to_numpy()
stress_mean = xs.mean()
P("[G5] cost (1 RT/day by construction -- one decision bar, one exit bar, verified: max 1 trade/session)")
P(f"     gated-ES PRIMARY (1tk/side, ${MKT['ES']['cost_primary_usd']:.2f} RT): net {hs['net']:+.4f} pt = {hs['net_usd']:+.2f} $/ses")
P(f"     gated-ES STRESS  (2tk/side, ${MKT['ES']['cost_stress_usd']:.2f} RT): net {stress_mean:+.4f} pt = {stress_mean*50:+.2f} $/ses")
G5 = stress_mean > 0
P(f"     clause: after-cost mean > 0 at STRESS rung: {'PASS' if G5 else 'FAIL'}")
P("")

# --- G6 battery ----------------------------------------------------------------------
P("[G6] eval battery -- WEEKLY-VOL LEAD (gated-ES net PRIMARY $; DISCOVERY)")
ces = cell_series("ES", "gated")
daily_usd = ces["net"] * MKT["ES"]["pt_usd"]
wk = daily_usd.resample("W-FRI").sum()
yrs = (daily_usd.index.max() - daily_usd.index.min()).days / 365.25
sharpe_w = wk.mean() / wk.std(ddof=1) * np.sqrt(52) if wk.std(ddof=1) > 0 else np.nan
cum = wk.cumsum()
dd = (cum.cummax() - cum).to_numpy()
maxdd = dd.max()
cdar95 = dd[dd >= np.percentile(dd, 95)].mean()
P(f"     weekly grid: {len(wk)} calendar weeks ({yrs:.2f} yr), zeros where no trade")
P(f"     LEAD  weekly-vol annualized Sharpe = {sharpe_w:.2f}  (mean ${wk.mean():.1f}/wk, sd ${wk.std(ddof=1):.1f}/wk)")
P(f"     native: total net ${daily_usd.sum():,.0f} over {yrs:.2f} yr = ${daily_usd.sum()/yrs:,.0f}/yr on "
  f"{hs['n']/yrs:.1f} trades/yr (${hs['net_usd']:.2f}/trade)")
P(f"     path descriptives ONLY: weekly maxDD ${maxdd:,.0f}, CDaR95 ${cdar95:,.0f}")
P("     NO fixed-DD- or CDaR-normalized income figure is quoted in this run (thinning-placebo guard honored).")
P("")
# rho to P1
p1 = pd.read_csv(os.path.join(ROOT, "runs", "WE_W56_BREADTH", "out", "p1_daily.csv"),
                 index_col=0, parse_dates=True)["p1_usd"]
lo_d = max(daily_usd.index.min(), p1.index.min())
hi_d = min(daily_usd.index.max(), p1.index.max())
grid = daily_usd.index[(daily_usd.index >= lo_d) & (daily_usd.index <= hi_d)]
cand = daily_usd.reindex(grid).fillna(0.0)
p1g = p1.reindex(grid).fillna(0.0)
rho_d = cand.corr(p1g)
cw = cand.resample("W-FRI").sum()
pw = p1g.resample("W-FRI").sum()
rho_w = cw.corr(pw)
both = grid[(ces.reindex(grid)["traded"].fillna(False)) & grid.isin(p1.index)]
rho_both = daily_usd.reindex(both).corr(p1.reindex(both))
P(f"     rho to P1 (SOURCE: runs/WE_W56_BREADTH/out/p1_daily.csv -- P1 daily PnL reproduced from file;")
P(f"       zero-filled common calendar {lo_d.date()}..{hi_d.date()}, {len(grid)} sessions; both-traded n={len(both)}):")
P(f"       daily rho = {rho_d:+.4f}   weekly rho = {rho_w:+.4f}   both-traded-days rho = {rho_both:+.4f}")
P(f"       (15:00-16:00 sits INSIDE P1's live exposure window -- the stacking question, answered by these numbers)")
G6 = True  # procedural: printed
P("")

# --- G1 procedural -------------------------------------------------------------------
G1 = True  # MDE printed per cell before observed means

# ---------------------------------------------------------------- final table
P(HR)
P(f"{'GATE':<18s}{'SPEC':<72s}{'PASS/FAIL':>10s}")
P("-" * 100)
def row(g, spec, obs, ok):
    P(f"{g:<18s}{spec:<72s}{'PASS' if ok else 'FAIL':>10s}")
    P(f"{'':18s}OBSERVED: {obs}")
row("G1_MDE_first", "MDE printed per cell (~590 gated ES sessions) BEFORE observed means",
    f"6/6 cells printed; gated-ES n={mde_rows[('ES','gated')]['n']}, MDE_80={mde_rows[('ES','gated')]['mde80']:.4f} pt", G1)
row("G2_edge", "gated-ES net mean>0 AND block CI95 excl 0 AND K_eff-corrected shift null",
    f"mean {hs['net']:+.4f} pt; CI [{hs['ci_lo']:+.4f},{hs['ci_hi']:+.4f}]; pct {hp['pct']:.2f}% vs bar {100*alpha_corr:.2f}%", G2)
row("G3_coherence", "RTY/YM support printed (classification); ES gated >= ungated",
    f"support {sup}/2; ES gated {cell_stats[('ES','gated')]['net']:+.4f} vs ungated {cell_stats[('ES','ungated')]['net']:+.4f} pt", G3)
row("G4_chronology", "2022-23 vs 2024-26 halves; both-wrong-sign = FAIL (gated-ES)",
    f"2022-23 {e1m:+.4f} pt; 2024-26 {e2m:+.4f} pt", G4)
row("G5_cost", "1 RT/day; {1,2}-tick band; net>0 at 2tk/side STRESS",
    f"PRIMARY {hs['net']:+.4f} pt; STRESS {stress_mean:+.4f} pt", G5)
row("G6_battery", "weekly-vol lead; rho-to-P1 printed; no unguarded DD figure",
    f"Sharpe_wk {sharpe_w:.2f}; rho_d {rho_d:+.3f} rho_w {rho_w:+.3f}; guard honored", G6)
P("-" * 100)
P(f"blocking set G2+G4: G2:{'PASS' if G2 else 'FAIL'}  G4:{'PASS' if G4 else 'FAIL'}")
decision = "CLOSEHOUR01 CANDIDATE (Class-P/S assessment; rho-to-P1 decides stacking)" if (G2 and G4) else "CLOSED AT SCOPE (spec section 28)"
P(f"DECISION (mechanical): {decision}")
P("EVIDENCE STATUS: DISCOVERY (substrates DISCOVERY_CONSUMED for other objects).")
P(HR)

# ---------------------------------------------------------------- artifacts
pd.DataFrame(csv_rows).to_csv(os.path.join(OUT, "cells.csv"), index=False)
pd.DataFrame(era_rows).to_csv(os.path.join(OUT, "era_table.csv"), index=False)
with open(os.path.join(OUT, "gate_table.txt"), "w", encoding="utf-8") as f:
    f.write(buf.getvalue())
print("\nWROTE out/gate_table.txt, out/cells.csv, out/era_table.csv")
