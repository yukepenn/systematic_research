# G3_DUREXT_20260906 — bond-index duration-extension day (ledger G00086, family GENESIS3_EVENT)
# Frozen spec: runs/G3_DUREXT_20260906/spec.yaml (committed e1d10a0 before results).
# Inputs AS-IS from runs/G3_AUCTCYCLE_20260906/out/ (certified causal roll, identity-gated).
# PRIMARY: LONG ZB close(T-1)->close(T) on the LAST trading day T of each month.
# Concentration placebos: the T-2 day and the T+1 day (each vs all-days control);
# PRIMARY delta must exceed BOTH.
# Program prints MDE (G1) BEFORE any observed event mean is computed.

import hashlib
import json
import math
import os
import sys

import numpy as np
import pandas as pd

RUN = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research\runs\G3_DUREXT_20260906"
UP = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research\runs\G3_AUCTCYCLE_20260906\out"
OUT = os.path.join(RUN, "out")
os.makedirs(OUT, exist_ok=True)

SEAL = pd.Timestamp("2026-08-01")
COMMISSION_RT = 4.36               # NinjaTrader Lifetime, $/contract round trip (MODELED)
POINT_VALUE = 1000.0               # $ per point, ZB and ZN
TICK = {"ZB": 0.03125, "ZN": 0.015625}
N_SHIFTS = 2000
SEED_SHIFT = 20260906
SEED_BOOT = 20260907
N_BOOT = 10000

lines = []
def emit(s=""):
    print(s)
    lines.append(s)

def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

emit("=" * 118)
emit("=== G3_DUREXT_20260906 -- bond-index duration-extension day: LONG ZB close(T-1)->close(T) on month-end T (G00086)")
emit("=" * 118)

# ---------------------------------------------------------------- inputs AS-IS
manifest = json.load(open(os.path.join(UP, "inputs_manifest.json")))
series = {}
for sym in ("ZB", "ZN"):
    p = os.path.join(UP, f"{sym.lower()}_daily.parquet")
    sha = sha256(p)
    assert sha == manifest[sym]["parquet_sha256"], f"{sym} sha mismatch vs upstream manifest"
    df = pd.read_parquet(p).sort_values("date").reset_index(drop=True)
    assert df["date"].max() < SEAL, f"{sym} SEAL VIOLATION: max {df['date'].max()}"
    assert df["date"].is_unique
    # tick asserted from data: closes sit on the half-tick grid (NT8 records half ticks);
    # the COST band uses the DECLARED instrument tick from the manifest (conservative)
    assert TICK[sym] == manifest[sym]["tick_size"], f"{sym} declared tick mismatch vs manifest"
    half = TICK[sym] / 2
    grid = (df["close"] / half).round() * half
    assert np.allclose(grid, df["close"], atol=1e-12), f"{sym} half-tick-grid assert failed"
    on_full = int(np.isclose((df["close"] / TICK[sym]).round() * TICK[sym], df["close"], atol=1e-12).sum())
    series[sym] = df
    emit(f"input {sym}: {p}")
    emit(f"    sha256 {sha}  (== upstream manifest)  rows {len(df)}  span {df['date'].min().date()} -> {df['date'].max().date()}  seal assert PASS")
    emit(f"    declared tick {TICK[sym]} (manifest); data grid = half-tick ({half}): all {len(df)} closes on it, {on_full} on the full tick; COSTS use the declared (coarser) tick")

cost = {s: {"opt": COMMISSION_RT + 1 * TICK[s] * POINT_VALUE,
            "cons": COMMISSION_RT + 2 * TICK[s] * POINT_VALUE} for s in ("ZB", "ZN")}
emit(f"costs/ct RT (1-day hold, MODELED $4.36 RT + {{1,2}}-tick spread): "
     f"ZB opt ${cost['ZB']['opt']:.2f} cons ${cost['ZB']['cons']:.2f} | "
     f"ZN opt ${cost['ZN']['opt']:.2f} cons ${cost['ZN']['cons']:.2f}   [cons rung GATES]")

# ------------------------------------------------- event construction (frozen)
# last trading day T of each calendar month present in each series' own session calendar
def build_events(df):
    g = df.groupby([df["date"].dt.year, df["date"].dt.month])
    idx = g.apply(lambda x: x.index[-1]).values
    return np.sort(idx)

ev_idx = {s: build_events(series[s]) for s in ("ZB", "ZN")}
for s in ("ZB", "ZN"):
    d = series[s].loc[ev_idx[s], "date"]
    emit(f"events {s}: {len(ev_idx[s])} month-end sessions, {d.min().date()} -> {d.max().date()} "
         f"(months 2009-03 .. 2026-07; spec said ~210)")

# ---------------------------------------------------------------- G1: MDE FIRST
# printed BEFORE any observed event-day mean; sigma = unconditional daily $ sd
emit("")
emit("G1 MDE (PRINTED BEFORE ANY OBSERVED EVENT MEAN):")
NZB = len(ev_idx["ZB"])
sd_all = {s: float(series[s]["ret_points"].std(ddof=1)) * POINT_VALUE for s in ("ZB", "ZN")}
mde = {s: 2.486 * sd_all[s] / np.sqrt(len(ev_idx[s])) for s in ("ZB", "ZN")}
for s in ("ZB", "ZN"):
    emit(f"    {s}: unconditional daily sd ${sd_all[s]:,.0f}; N={len(ev_idx[s])}; "
         f"MDE(one-sided 5%, 80% power) = 2.486 x sd/sqrt(N) = ${mde[s]:,.0f}/event "
         f"({mde[s]/POINT_VALUE:.3f} pts)")

# ------------------------------------------------------------- observed cells
def cell(df, idx, offset):
    """returns (kept event positions, session dates, ret_points) for sessions idx+offset in range"""
    j = idx + offset
    keep = (j >= 0) & (j < len(df))
    j = j[keep]
    r = df.loc[j, "ret_points"].values
    d = df.loc[j, "date"].values
    fin = np.isfinite(r)
    return d[fin], r[fin], int((~keep).sum() + (~fin).sum())

obs = {}
for s in ("ZB", "ZN"):
    df = series[s]
    obs[s] = {}
    for name, off in (("T", 0), ("Tm2", -2), ("Tp1", +1)):
        d, r, dropped = cell(df, ev_idx[s], off)
        obs[s][name] = {"dates": d, "ret": r, "dropped": dropped}
    obs[s]["all_mean"] = float(df["ret_points"].mean())
    obs[s]["n_all"] = int(df["ret_points"].notna().sum())

emit("")
emit("PRIMARY (LONG ZB close(T-1)->close(T) on month-end T, per contract):")
zb = obs["ZB"]
gross_pts = float(zb["T"]["ret"].mean())
gross_d = gross_pts * POINT_VALUE
ac_cons = gross_d - cost["ZB"]["cons"]
ac_opt = gross_d - cost["ZB"]["opt"]
n_ev = len(zb["T"]["ret"])
emit(f"    n = {n_ev} (dropped {zb['T']['dropped']}); gross mean {gross_pts:+.4f} pts = ${gross_d:+,.2f}/event")
emit(f"    after-cost CONS ${ac_cons:+,.2f}/event   [GATING]   after-cost OPT ${ac_opt:+,.2f}/event")

# event-block bootstrap CI (resample events with replacement) on after-cost CONS mean
rng_b = np.random.default_rng(SEED_BOOT)
r_ev = zb["T"]["ret"] * POINT_VALUE - cost["ZB"]["cons"]
bm = np.array([rng_b.choice(r_ev, size=n_ev, replace=True).mean() for _ in range(N_BOOT)])
ci_lo, ci_hi = np.percentile(bm, [2.5, 97.5])
emit(f"    event-block bootstrap ({N_BOOT}, seed {SEED_BOOT}) 95% CI (cons): [${ci_lo:+,.2f}, ${ci_hi:+,.2f}]")

# shared-draw circular-shift null (2000 shifts, ONE shared draw for ZB and ZN)
rng_s = np.random.default_rng(SEED_SHIFT)
u = rng_s.random(N_SHIFTS)
null_means = {}
for s in ("ZB", "ZN"):
    df = series[s]
    r = df["ret_points"].values
    L = len(r)
    offs = 1 + (u * (L - 2)).astype(int)          # shared fractional draw -> per-series offset
    idx = ev_idx[s]
    nm = np.empty(N_SHIFTS)
    for k, o in enumerate(offs):
        nm[k] = np.nanmean(r[(idx + o) % L])
    null_means[s] = nm * POINT_VALUE
nm_zb = null_means["ZB"]
p_1s = (1 + int((nm_zb >= gross_d).sum())) / (1 + N_SHIFTS)
p_2s = (1 + int((np.abs(nm_zb - nm_zb.mean()) >= abs(gross_d - nm_zb.mean())).sum())) / (1 + N_SHIFTS)
z = (gross_d - nm_zb.mean()) / nm_zb.std(ddof=1)
emit(f"    shared-draw shift null (2000 shifts, seed {SEED_SHIFT}): null mean ${nm_zb.mean():+,.2f}, sd ${nm_zb.std(ddof=1):,.2f}")
emit(f"    p one-sided(LONG) = {p_1s:.4f} [GATING]; two-sided {p_2s:.4f}; z = {z:+.2f} (normal-approx p_1s = {1 - 0.5 * (1 + math.erf(z / np.sqrt(2))):.4f} cross-check)")
emit(f"    IN WORDS: p_1s is the probability, under {N_SHIFTS} dependence-preserving circular shifts of the")
emit(f"    month-end event flag over the {len(series['ZB'])}-session ZB sequence (one shared draw with ZN), that a")
emit(f"    randomly placed set of {NZB} pseudo-event days shows a mean 1-day ZB return >= the observed ${gross_d:+,.2f}.")

# --------------------------------------------------- concentration (G3) cells
emit("")
emit("CONCENTRATION (each cell vs the all-days control, gross $ -- cost identical across cells so deltas are cost-invariant):")
all_d = zb["all_mean"] * POINT_VALUE
deltas = {}
for name, label in (("T", "PRIMARY  T   (extension day)"), ("Tm2", "placebo  T-2"), ("Tp1", "placebo  T+1")):
    m = float(obs["ZB"][name]["ret"].mean()) * POINT_VALUE
    n = len(obs["ZB"][name]["ret"])
    deltas[name] = m - all_d
    emit(f"    {label:30s} n={n:4d}  mean ${m:+8.2f}  delta vs all-days(${all_d:+.2f}, n={zb['n_all']}) = ${deltas[name]:+8.2f}")
conc_ok = (deltas["T"] > deltas["Tm2"]) and (deltas["T"] > deltas["Tp1"])
emit(f"    concentration clause: delta_T > delta_T-2 ({deltas['T']:+.2f} > {deltas['Tm2']:+.2f}: {deltas['T'] > deltas['Tm2']}) "
     f"AND delta_T > delta_T+1 ({deltas['T']:+.2f} > {deltas['Tp1']:+.2f}: {deltas['T'] > deltas['Tp1']}) -> {conc_ok}")

# ---------------------------------------------------------------- G4 era table
emit("")
emit("ERA TABLE (ZB PRIMARY, after-cost CONS; sign gates; modern-negative = FAIL):")
era_def = [("2009-15", 2009, 2015), ("2016-21", 2016, 2021), ("2022-26/07", 2022, 2026)]
ev_dates = pd.to_datetime(zb["T"]["dates"])
ev_ret_d = zb["T"]["ret"] * POINT_VALUE
era_rows = []
era_sign = {}
for label, y0, y1 in era_def:
    m = (ev_dates.year >= y0) & (ev_dates.year <= y1)
    g = float(ev_ret_d[m].mean())
    ac = g - cost["ZB"]["cons"]
    era_sign[label] = "+" if ac > 0 else "-"
    era_rows.append((label, int(m.sum()), g, ac, era_sign[label]))
    emit(f"    {label:12s} n={int(m.sum()):4d}  gross ${g:+8.2f}  after-cost ${ac:+8.2f}  sign {era_sign[label]}")
signs = "/".join(era_sign[l] for l, _, _ in era_def)
modern_neg = era_sign["2022-26/07"] == "-"
if all(v == "+" for v in era_sign.values()):
    era_class = "STRUCTURAL"
elif modern_neg:
    era_class = "MODERN-NEGATIVE"
else:
    era_class = "REGIME-LOCAL (modern +, older mixed)"
emit(f"    ERA CLASSIFICATION: {signs} -> {era_class}")

# ------------------------------------------------------------------- ZN mirror
emit("")
emit("ZN MIRROR (reported, non-gating; same machinery):")
zn = obs["ZN"]
zn_gross = float(zn["T"]["ret"].mean()) * POINT_VALUE
zn_ac = zn_gross - cost["ZN"]["cons"]
zn_all = zn["all_mean"] * POINT_VALUE
zn_deltas = {k: float(zn[k]["ret"].mean()) * POINT_VALUE - zn_all for k in ("T", "Tm2", "Tp1")}
p_1s_zn = (1 + int((null_means["ZN"] >= zn_gross).sum())) / (1 + N_SHIFTS)
emit(f"    n = {len(zn['T']['ret'])}; gross ${zn_gross:+,.2f}; after-cost CONS ${zn_ac:+,.2f}; shared-draw p_1s {p_1s_zn:.4f}")
emit(f"    deltas vs all-days(${zn_all:+.2f}): T {zn_deltas['T']:+.2f} | T-2 {zn_deltas['Tm2']:+.2f} | T+1 {zn_deltas['Tp1']:+.2f} "
     f"-> concentration {(zn_deltas['T'] > zn_deltas['Tm2']) and (zn_deltas['T'] > zn_deltas['Tp1'])}")

# clean_daily audit (reported; spec froze no exclusion)
for s in ("ZB", "ZN"):
    df = series[s]
    for name in ("T", "Tm2", "Tp1"):
        dd = pd.to_datetime(obs[s][name]["dates"])
        bad = int((~df.set_index("date").loc[dd, "clean_daily"]).sum())
        if bad:
            emit(f"    NOTE {s} {name}: {bad} gap-spanning (clean_daily=False) day(s) included (spec froze no exclusion)")

# ------------------------------------------------------------------ gate table
emit("")
emit("GATE TABLE  (printed by program)")
g1 = ("PASS", f"MDE ${mde['ZB']:,.0f}/event at N={NZB} (printed first)")
g2_ok = (ac_cons > 0) and (ci_lo > 0) and (p_1s < 0.05)
g2 = ("PASS" if g2_ok else "*** FAIL ***",
      f"mean cons ${ac_cons:+,.2f}, CI [{ci_lo:+,.2f},{ci_hi:+,.2f}], p_1s {p_1s:.4f}")
g3 = ("PASS" if conc_ok else "*** FAIL ***",
      f"delta T {deltas['T']:+.2f} vs T-2 {deltas['Tm2']:+.2f} / T+1 {deltas['Tp1']:+.2f}")
g4_ok = not modern_neg
g4 = ("PASS" if g4_ok else "*** FAIL ***", f"{signs} -> {era_class}")
g5 = ("PASS", f"ticks asserted from data; ZB opt ${cost['ZB']['opt']:.2f} / cons ${cost['ZB']['cons']:.2f}; cons rung gates")
rows = [
    ("G1_MDE_FIRST", "MDE printed before observed (~210 events)", g1[1], g1[0]),
    ("G2_EDGE", "after-cost mean > 0 AND event-block CI excludes 0 AND 1-sided shift p < .05", g2[1], g2[0]),
    ("G3_CONCENTRATION", "PRIMARY delta-vs-control > EACH placebo-day delta (T-2 and T+1)", g3[1], g3[0]),
    ("G4_ERA", "3-era signs (after-cost cons); modern-negative = FAIL", g4[1], g4[0]),
    ("G5_COST", "1-day hold; modeled $4.36 RT + {1,2}-tick band; cons gates", g5[1], g5[0]),
]
emit(f"{'GATE':<18}{'SPEC':<78}{'OBSERVED':<72}PASS-FAIL")
for r in rows:
    emit(f"{r[0]:<18}{r[1]:<78}{r[2]:<72}{r[3]}")

decision = "DUREXT01 CANDIDATE (Class-P small calendar engine)" if (g2_ok and conc_ok and g4_ok) else \
    "CLOSED AT SCOPE (S28 block) -- closure completes the month-end/rates calendar family alongside G00077"
emit("")
emit(f"DECISION RULE (spec, mechanical): G2={'PASS' if g2_ok else 'FAIL'} G3={'PASS' if conc_ok else 'FAIL'} "
     f"G4={'PASS' if g4_ok else 'FAIL'} -> {decision}")
emit(f"events/yr = {n_ev / ((ev_dates.max() - ev_dates.min()).days / 365.25):.1f}; "
     f"after-cost economics at cons rung = ${ac_cons * 12:+,.0f}/yr/contract (12 events/yr)")
emit("evidence_status: DISCOVERY (first read of this representation); honest prior was ADVERSE-LEANING (G00077 banked control)")
emit("=" * 118)

# --------------------------------------------------------------------- outputs
with open(os.path.join(OUT, "gate_table.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(lines) + "\n")

# event_table.csv — one row per ZB event, ZN mirror joined by calendar month
zb_df = series["ZB"]
et = pd.DataFrame({
    "event_date": pd.to_datetime(zb["T"]["dates"]),
    "zb_ret_pts": zb["T"]["ret"],
})
et["zb_gross_usd"] = et["zb_ret_pts"] * POINT_VALUE
et["zb_aftercost_opt_usd"] = et["zb_gross_usd"] - cost["ZB"]["opt"]
et["zb_aftercost_cons_usd"] = et["zb_gross_usd"] - cost["ZB"]["cons"]
et["era"] = pd.cut(et["event_date"].dt.year, bins=[2008, 2015, 2021, 2026],
                   labels=["2009-15", "2016-21", "2022-26/07"])
zn_map = pd.DataFrame({
    "d": pd.to_datetime(obs["ZN"]["T"]["dates"]),
    "zn_ret_pts": obs["ZN"]["T"]["ret"],
})
zn_map["ym"] = zn_map["d"].dt.to_period("M")
et["ym"] = et["event_date"].dt.to_period("M")
et = et.merge(zn_map.rename(columns={"d": "zn_event_date"}), on="ym", how="left").drop(columns=["ym"])
et["zn_gross_usd"] = et["zn_ret_pts"] * POINT_VALUE
et["zn_aftercost_cons_usd"] = et["zn_gross_usd"] - cost["ZN"]["cons"]
clean_map = zb_df.set_index("date")["clean_daily"]
et["zb_clean_daily"] = clean_map.loc[et["event_date"]].values
et.to_csv(os.path.join(OUT, "event_table.csv"), index=False)

# placebo_days.csv — per instrument/cell rows
prows = []
for s in ("ZB", "ZN"):
    for name, off in (("Tm2", -2), ("Tp1", +1)):
        for d, r in zip(obs[s][name]["dates"], obs[s][name]["ret"]):
            prows.append({"instrument": s, "cell": name, "offset_sessions": off,
                          "session_date": pd.Timestamp(d).date(), "ret_pts": r,
                          "ret_usd": r * POINT_VALUE})
pd.DataFrame(prows).to_csv(os.path.join(OUT, "placebo_days.csv"), index=False)

print("\nWROTE out/gate_table.txt, out/event_table.csv, out/placebo_days.csv")
