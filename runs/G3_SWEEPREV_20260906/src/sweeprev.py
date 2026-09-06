# G3_SWEEPREV_20260906  (ledger G00092, family GENESIS3_EVENT)
# Post-sweep liquidity-provision reversal (Nagel-2012 family) with the generic-MR discriminator.
# Frozen object per spec.yaml. Program-printed gate table; ALL cells reported; POINTS basis.
# NQ EXCLUDED from the universe (flagged, per spec: NQ is the momentum outlier).
#
# FROZEN MECHANICAL READINGS (stated here, before any result is computed):
#  R1.  Substrates: runs/SM1M_{ES,RTY,YM,ZB,CL}_SUBSTRATE/out/*.parquet, POINTS, bars
#       END-stamped ET (bar stamped 09:31 opens 09:30). Session = trade date: bars with
#       end-stamp minute-of-day > 17*60 belong to the NEXT day (family convention). Seal:
#       assert max time < 2026-08-01 per substrate before anything else.
#  R2.  1-min return r_t = close_t - close_{t-1} WITHIN session only (first bar of a session
#       has no r). Returns after intra-session missing minutes telescope into the next bar.
#  R3.  Trailing-30-min window at bar t = bars with end-stamp in [t-30min, t) (closed-left,
#       time-based). The 17:00->18:01 maintenance gap is > 30 min, so a single global
#       time-based rolling never crosses sessions (asserted: min inter-session gap > 30 min).
#       Trailing stats: trail_high = max(high); trail_low = min(low); trail_medrange =
#       median(high-low); trail_sd = std(r, ddof=1); trail_cnt = count(bars).
#  R4.  ELIGIBLE-BAR universe (IDENTICAL for all three objects — "same events universe
#       conventions"): (a) session first stamp <= t-30min (full trailing window inside the
#       session); (b) trail_cnt >= 20 of 30 (missing-minute tolerance, frozen); (c) trail_sd
#       defined and > 0; (d) r_t defined; (e) session last stamp >= t+30min (full exit
#       horizon inside the session).
#  R5.  SWEEP event (spec literal): eligible AND (high_t > trail_high OR low_t < trail_low)
#       AND (high_t - low_t) >= 2.0 * trail_medrange. Direction = FADE: up-sweep (high
#       breach) -> dir -1 (short); down-sweep (low breach) -> dir +1 (long); both-side
#       breach -> dir = -sign(r_t), dropped if r_t == 0 (count printed).
#  R6.  k-SIGMA MR CONTROL (the discriminator's comparator, spec literal "fade any 1-min
#       move >= the same z threshold regardless of breach/range"): eligible AND
#       |r_t| >= 2.0 * trail_sd. dir = -sign(r_t). "The same z" is frozen as z = 2.0, the
#       same multiplier the sweep definition applies to its range condition; sigma = trail_sd
#       (same trailing-30-min window). Same exit, same conventions.
#  R7.  VOL-MATCHED NON-SWEEP PLACEBO (spec literal): CONTROL condition AND NO 30-min-extreme
#       breach on either side (high_t <= trail_high AND low_t >= trail_low). dir = -sign(r_t).
#  R8.  Entry = close of the event bar (decision at bar close). Exit = close of the LAST bar
#       with end-stamp <= t+30min in the same session (exists by R4e; missing-minute exits
#       telescope backward). PnL_pts = dir * (exit_close - entry_close); USD = pts * PT_USD.
#  R9.  Non-overlap suppression, per market per object, greedy in time order: accept an event
#       iff its entry stamp >= previous accepted entry stamp + 30min (one position at a time;
#       an entry exactly at the prior exit stamp is allowed). Applied BEFORE the macro split
#       (one trade stream per market per object).
#  R10. Macro split on the ENTRY end-stamp (ET): MACRO iff minute-of-day in [08:25,08:50] or
#       [13:55,14:20] (inclusive); EX-MACRO = complement. GATING cells = pooled ex-macro.
#  R11. Costs (BASIS = MODELED ALL_IN, family convention: comm $4.36/ctRT Lifetime + spread
#       ticks PER SIDE): rungs {1,2} ticks/side; the 2-tick/side rung GATES (spec G7: 30-min
#       horizon is cost-hostile — conservative gates).
#         ES  tick 0.25 pt=$12.50, $50/pt:   1tk/s $29.36, 2tk/s $54.36
#         RTY tick 0.10 pt=$5.00,  $50/pt:   1tk/s $14.36, 2tk/s $24.36
#         YM  tick 1.00 pt=$5.00,  $5/pt:    1tk/s $14.36, 2tk/s $24.36
#         ZB  tick 1/32 pt=$31.25, $1000/pt: 1tk/s $66.86, 2tk/s $129.36
#         CL  tick 0.01 pt=$10.00, $1000/pt: 1tk/s $24.36, 2tk/s $44.36
#       G5 additionally uses the SPEC-NAMED G00062 bar for ZB: the G00062 cost model's 2-tick
#       rung $66.86/RT = 2.1395 ticks — clause: ZB ex-macro sweep per-event GROSS mean (ticks)
#       >= 2.1395, else the ZB cell is recorded COST-DEAD. (G5 does not block the decision
#       rule, which is G2+G3+G4+G6 by spec.)
#  R12. G2 (three clauses, ALL required): on the pooled (5-market) ex-macro sweep cell,
#       (a) after-cost per-event mean at the GATING rung > 0 (USD/contract);
#       (b) circular session-block bootstrap CI95 (L=10, B=2000, seed 20260906) of that
#           after-cost mean excludes 0;
#       (c) OPERATIVE shared-draw circular null p < 0.05, computed on the GROSS pooled mean:
#           whole-session circular shift of the event overlay — every event keeps its clock
#           slot and its direction, its session index shifts by the SAME k for all events and
#           all markets (shared draw; k applied modulo each market's own session count),
#           k = 1..S_union-1 FULLY ENUMERATED; entry/exit prices read from a per-session
#           minute-slot close grid forward-filled within session (identity-checked at k=0);
#           pseudo-events landing before a session's first bar are dropped from that
#           replicate; two-sided p = (1 + #{|mean_k| >= |mean_obs|}) / S_union.
#           SECOND COMPUTATION (printed, non-gating): whole-session sign-flip null, one
#           eps_s in {-1,+1} per union session SHARED across all markets and all three
#           objects' family, B = 10,000. K_eff over the 5 markets printed: rho_bar = mean
#           pairwise corr of per-session ex-macro sweep gross USD sums (pairwise-common
#           sessions, 0 where a session has no events), K_eff = 5/(1+4*rho_bar), clamped [1,5].
#  R13. G3 THE DISCRIMINATOR: delta = pooled ex-macro per-event GROSS mean (USD), SWEEP minus
#       CONTROL. JOINT circular session-block bootstrap (same session draws applied to both
#       objects, L=10, B=2000) CI95 of delta. PASS iff delta_obs > 0 AND CI excludes 0
#       (lo > 0). ("Beat" = strictly better; a CI excluding 0 from below is a FAIL.)
#  R14. G4: pooled ex-macro per-event GROSS mean, PLACEBO < SWEEP (point estimates; the
#       spec's word "shows LESS"); joint block-bootstrap CI of that delta printed as context.
#       G6: sign(pooled ex-macro GROSS mean, era1) == sign(era2); era1 = session date
#       <= 2023-12-31 ("2022-23"; ZB starts 2022-12-27 — disclosed), era2 >= 2024-01-01.
#       Decision rule (spec verbatim): G2+G3+G4+G6 PASS -> SWEEPREV01 candidate. Else closed
#       at scope (S28).
#
# POINTS ONLY: no percent column is formed anywhere in this program.

import io
import os
import hashlib
import math
import numpy as np
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
RUN = os.path.join(ROOT, "runs", "G3_SWEEPREV_20260906")
OUT = os.path.join(RUN, "out")
os.makedirs(OUT, exist_ok=True)

SEAL = pd.Timestamp("2026-08-01")
SEED = 20260906
B_BOOT = 2000
BLOCK_L = 10
B_FLIP = 10_000
K_RANGE = 2.0        # spec: range >= 2x trailing median range
K_SIG = 2.0          # frozen reading of "the same z" (R6)
W_TRAIL = 30         # minutes
HOLD = 30            # minutes
MIN_TRAIL = 20       # bars (R4b)
COMM = 4.36
ERA_SPLIT = pd.Timestamp("2024-01-01")

MKTS = ["ES", "RTY", "YM", "ZB", "CL"]
SUB = {
    "ES":  ("SM1M_ES_SUBSTRATE",  "es_1m_2022_2026.parquet"),
    "RTY": ("SM1M_RTY_SUBSTRATE", "rty_1m_2022_2026.parquet"),
    "YM":  ("SM1M_YM_SUBSTRATE",  "ym_1m_2022_2026.parquet"),
    "ZB":  ("SM1M_ZB_SUBSTRATE",  "zb_1m_2023_2026.parquet"),
    "CL":  ("SM1M_CL_SUBSTRATE",  "cl_1m_2022_2026.parquet"),
}
TICK_PT = {"ES": 0.25, "RTY": 0.10, "YM": 1.0, "ZB": 1.0 / 32.0, "CL": 0.01}
TICK_USD = {"ES": 12.50, "RTY": 5.00, "YM": 5.00, "ZB": 31.25, "CL": 10.00}
PT_USD = {"ES": 50.0, "RTY": 50.0, "YM": 5.0, "ZB": 1000.0, "CL": 1000.0}
COST1 = {m: 2 * TICK_USD[m] + COMM for m in MKTS}   # 1 tick/side RT
COST2 = {m: 4 * TICK_USD[m] + COMM for m in MKTS}   # 2 ticks/side RT  << GATES
ZB_G00062_RUNG_USD = 66.86                          # G00062 model 2-tick rung (per RT)
ZB_G00062_RUNG_TICKS = ZB_G00062_RUNG_USD / TICK_USD["ZB"]

buf = io.StringIO()
def P(s=""):
    print(s)
    buf.write(s + "\n")

HR = "=" * 100
P(HR)
P("G3_SWEEPREV_20260906  (ledger G00092, family GENESIS3_EVENT)   EVIDENCE STATUS: DISCOVERY")
P("Post-sweep liquidity-provision reversal on ES/RTY/YM/ZB/CL 1-min (NQ EXCLUDED — flagged outlier),")
P("with THE DISCRIMINATOR: sweep-fade must beat the plain k-sigma MR control (delta CI excl. 0) or die.")
P("POINTS basis. Frozen mechanical readings R1-R14 in src header. Seed 20260906.")
P(f"cost model (BASIS=MODELED ALL_IN, comm ${COMM:.2f}/ctRT + spread ticks PER SIDE; 2tk/side rung GATES):")
for m in MKTS:
    P(f"   {m:3s} tick {TICK_PT[m]:.5f} pt = ${TICK_USD[m]:5.2f}, ${PT_USD[m]:6.0f}/pt:  "
      f"1tk/side ${COST1[m]:6.2f}/RT   2tk/side ${COST2[m]:7.2f}/RT (GATING)")
P(f"   ZB G5 spec-named bar: G00062 model 2-tick rung ${ZB_G00062_RUNG_USD:.2f}/RT = {ZB_G00062_RUNG_TICKS:.4f} ticks/event (GROSS bar)")
P("")

# ------------------------------------------------------------- load + seal + universe
P("[G0] substrates, seal, session convention (end-stamp > 17:00 ET -> next trade date), eligible universe")
data = {}
for m in MKTS:
    path = os.path.join(ROOT, "runs", SUB[m][0], "out", SUB[m][1])
    sha = hashlib.sha256(open(path, "rb").read()).hexdigest()
    df = pd.read_parquet(path)
    assert df["time"].is_monotonic_increasing and not df["time"].duplicated().any()
    tmax = df["time"].max()
    assert tmax < SEAL, f"SEAL VIOLATION {m}: max time {tmax}"
    assert int((df["time"] >= SEAL).sum()) == 0
    mins = (df["time"].dt.hour * 60 + df["time"].dt.minute).to_numpy()
    sess = (df["time"].dt.normalize() + pd.to_timedelta((mins > 17 * 60).astype(int), unit="D"))
    df = df.assign(mins=mins, sess=sess.to_numpy())
    # prove the global time-rolling never crosses sessions
    tt = df["time"].to_numpy()
    sb = df["sess"].to_numpy()
    cross = np.flatnonzero(sb[1:] != sb[:-1])
    min_gap = (tt[cross + 1] - tt[cross]).min() / np.timedelta64(1, "m")
    assert min_gap > W_TRAIL, f"{m}: inter-session gap {min_gap} <= {W_TRAIL}min"
    df["r"] = df.groupby("sess")["close"].diff()
    df["rng"] = df["high"] - df["low"]
    ti = df.set_index("time")
    roll = ti.rolling(f"{W_TRAIL}min", closed="left")
    df["trail_high"] = roll["high"].max().to_numpy()
    df["trail_low"] = roll["low"].min().to_numpy()
    df["trail_medrange"] = roll["rng"].median().to_numpy()
    df["trail_sd"] = ti["r"].rolling(f"{W_TRAIL}min", closed="left", min_periods=MIN_TRAIL).std(ddof=1).to_numpy()
    df["trail_cnt"] = roll["close"].count().to_numpy()
    g = df.groupby("sess")["time"]
    first = g.transform("min")
    last = g.transform("max")
    d30 = pd.Timedelta(minutes=W_TRAIL)
    h30 = pd.Timedelta(minutes=HOLD)
    elig = (
        (first <= df["time"] - d30)
        & (df["trail_cnt"] >= MIN_TRAIL)
        & df["trail_sd"].notna() & (df["trail_sd"] > 0)
        & df["r"].notna()
        & (last >= df["time"] + h30)
    )
    df["elig"] = elig.to_numpy()
    # exit price: last bar with stamp <= t+30min, same session (merge_asof per session-safe:
    # global asof is safe because t+30min never crosses the >30min session gap given R4e)
    ex = pd.merge_asof(
        pd.DataFrame({"target": df["time"] + h30}),
        df[["time", "close", "sess"]].rename(columns={"time": "xt", "close": "exit_close", "sess": "xsess"}),
        left_on="target", right_on="xt", direction="backward",
    )
    df["exit_close"] = ex["exit_close"].to_numpy()
    df["exit_sess"] = ex["xsess"].to_numpy()
    ok = ~df["elig"] | (df["exit_sess"] == df["sess"])
    assert bool(ok.all()), f"{m}: exit crossed session for an eligible bar"
    n_sess = df["sess"].nunique()
    data[m] = df
    P(f"   {m:3s} {os.path.relpath(path, ROOT)}")
    P(f"       sha256 {sha}")
    P(f"       bars {len(df):,}; span {df['time'].min()} .. {tmax}; bars >= 2026-08-01: 0  SEAL OK")
    P(f"       sessions {n_sess:,}; eligible bars {int(df['elig'].sum()):,} "
      f"({100.0 * df['elig'].mean():.1f}% of bars); min inter-session gap {min_gap:.0f} min")
P("")

# ------------------------------------------------------------- event construction
MACRO1 = (8 * 60 + 25, 8 * 60 + 50)
MACRO2 = (13 * 60 + 55, 14 * 60 + 20)

def is_macro(mins):
    return ((mins >= MACRO1[0]) & (mins <= MACRO1[1])) | ((mins >= MACRO2[0]) & (mins <= MACRO2[1]))

def suppress(times):
    """Greedy non-overlap (R9): accept iff t >= prev_accepted + HOLD min. Returns bool mask."""
    keep = np.zeros(len(times), dtype=bool)
    lock = None
    h = np.timedelta64(HOLD, "m")
    for i, t in enumerate(times):
        if lock is None or t >= lock:
            keep[i] = True
            lock = t + h
    return keep

events = {}   # (market, obj) -> DataFrame of accepted events
raw_counts = {}
both_drop = {}
for m in MKTS:
    df = data[m]
    e = df["elig"].to_numpy()
    hi_breach = df["high"].to_numpy() > df["trail_high"].to_numpy()
    lo_breach = df["low"].to_numpy() < df["trail_low"].to_numpy()
    big_range = df["rng"].to_numpy() >= K_RANGE * df["trail_medrange"].to_numpy()
    r = df["r"].to_numpy()
    sweep_raw = e & (hi_breach | lo_breach) & big_range
    both = sweep_raw & hi_breach & lo_breach
    dir_sweep = np.where(hi_breach & ~lo_breach, -1.0, np.where(lo_breach & ~hi_breach, 1.0, -np.sign(r)))
    drop_both_zero = sweep_raw & both & (r == 0)
    sweep_raw = sweep_raw & ~drop_both_zero
    ctrl_raw = e & (np.abs(r) >= K_SIG * df["trail_sd"].to_numpy())
    dir_ctrl = -np.sign(r)
    plac_raw = ctrl_raw & ~hi_breach & ~lo_breach
    raw_counts[m] = dict(sweep=int(sweep_raw.sum()), control=int(ctrl_raw.sum()),
                         placebo=int(plac_raw.sum()),
                         overlap_sweep_ctrl=int((sweep_raw & ctrl_raw).sum()),
                         both_breach=int((sweep_raw & both).sum()))
    both_drop[m] = int(drop_both_zero.sum())
    for obj, mask, dvec in [("SWEEP", sweep_raw, dir_sweep), ("CONTROL", ctrl_raw, dir_ctrl),
                            ("PLACEBO", plac_raw, dir_ctrl)]:
        sub = df.loc[mask, ["time", "mins", "sess", "close", "exit_close"]].copy()
        sub["dir"] = dvec[mask]
        keep = suppress(sub["time"].to_numpy())
        sub = sub.loc[keep]
        sub["pnl_pts"] = sub["dir"] * (sub["exit_close"] - sub["close"])
        sub["pnl_usd"] = sub["pnl_pts"] * PT_USD[m]
        sub["macro"] = is_macro(sub["mins"].to_numpy())
        sub["market"] = m
        events[(m, obj)] = sub.reset_index(drop=True)

P("[events] raw event bars -> after non-overlap suppression (R9); macro split (R10) on entry stamp")
P(f"   {'mkt':4s}{'obj':9s}{'raw':>8s}{'kept':>8s}{'exmacro':>9s}{'macro':>7s}   notes")
for m in MKTS:
    for obj in ["SWEEP", "CONTROL", "PLACEBO"]:
        ev = events[(m, obj)]
        note = ""
        if obj == "SWEEP":
            note = (f"both-side-breach kept {raw_counts[m]['both_breach']}, r==0 dropped {both_drop[m]}; "
                    f"sweep∩ctrl raw {raw_counts[m]['overlap_sweep_ctrl']}")
        P(f"   {m:4s}{obj:9s}{raw_counts[m][obj.lower()]:>8,}{len(ev):>8,}"
          f"{int((~ev['macro']).sum()):>9,}{int(ev['macro'].sum()):>7,}   {note}")
P("")

# ------------------------------------------------------------- session panels
def sess_panel(ev_list, col="pnl_usd"):
    """union-session sums and counts for a list of event frames (already filtered)."""
    allv = pd.concat(ev_list, ignore_index=True)
    g = allv.groupby("sess")[col]
    return g.sum(), g.size()

union_sessions = sorted(set().union(*[set(data[m]["sess"].unique()) for m in MKTS]))
union_sessions = pd.Index(union_sessions)
S_union = len(union_sessions)
sess_pos = {s: i for i, s in enumerate(union_sessions)}

def vec_on_union(sums, cnts):
    v = np.zeros(S_union); n = np.zeros(S_union)
    idx = [sess_pos[s] for s in sums.index]
    v[idx] = sums.to_numpy(); n[idx] = cnts.to_numpy()
    return v, n

rng = np.random.default_rng(SEED)
NB = math.ceil(S_union / BLOCK_L)
starts = rng.integers(0, S_union, size=(B_BOOT, NB))
IDX = (starts[:, :, None] + np.arange(BLOCK_L)[None, None, :]).reshape(B_BOOT, NB * BLOCK_L)[:, :S_union] % S_union

def boot_mean(v, n, idx=IDX):
    tv = v[idx].sum(axis=1); tn = n[idx].sum(axis=1)
    with np.errstate(invalid="ignore", divide="ignore"):
        mm = tv / tn
    return mm[np.isfinite(mm)]

def boot_ci(v, n):
    mm = boot_mean(v, n)
    return np.percentile(mm, 2.5), np.percentile(mm, 97.5)

# per-market bootstrap uses its own session axis
mkt_idx = {}
for m in MKTS:
    sm = sorted(data[m]["sess"].unique())
    Sp = len(sm)
    nb = math.ceil(Sp / BLOCK_L)
    st = rng.integers(0, Sp, size=(B_BOOT, nb))
    mkt_idx[m] = ((st[:, :, None] + np.arange(BLOCK_L)[None, None, :]).reshape(B_BOOT, nb * BLOCK_L)[:, :Sp] % Sp,
                  {s: i for i, s in enumerate(sm)}, Sp)

def mkt_vec(ev, col, m):
    _, pos, Sp = mkt_idx[m]
    v = np.zeros(Sp); n = np.zeros(Sp)
    g = ev.groupby("sess")[col]
    idx = [pos[s] for s in g.sum().index]
    v[idx] = g.sum().to_numpy(); n[idx] = g.size().to_numpy()
    return v, n

# ------------------------------------------------------------- G1: MDE FIRST
P("[G1] MDE FIRST (printed before any observed mean). Ex-macro cells, per-event USD/contract.")
P("     SE = sd_s(session sums)*sqrt(n_sess)/n_events (session-cluster); MDE_sig=1.96*SE; MDE_80=2.8016*SE.")
P(f"     {'cell':16s}{'n_ev':>7s}{'n_sess':>8s}{'SE($/ev)':>10s}{'MDE_sig':>9s}{'MDE_80':>9s}{'cost1($)':>10s}{'cost2($)':>10s}")
for m in MKTS:
    ev = events[(m, "SWEEP")]
    ex = ev[~ev["macro"]]
    ss = ex.groupby("sess")["pnl_usd"].sum()
    se = ss.std(ddof=1) * math.sqrt(len(ss)) / len(ex) if len(ex) > 1 else float("nan")
    P(f"     {m + ' SWEEP exm':16s}{len(ex):>7,}{len(ss):>8,}{se:>10.2f}{1.96 * se:>9.2f}{2.8016 * se:>9.2f}"
      f"{COST1[m]:>10.2f}{COST2[m]:>10.2f}")
pool_ex = pd.concat([events[(m, "SWEEP")].query("~macro") for m in MKTS], ignore_index=True)
ssp = pool_ex.groupby("sess")["pnl_usd"].sum()
se_p = ssp.std(ddof=1) * math.sqrt(len(ssp)) / len(pool_ex)
P(f"     {'POOLED SWEEP exm':16s}{len(pool_ex):>7,}{len(ssp):>8,}{se_p:>10.2f}{1.96 * se_p:>9.2f}{2.8016 * se_p:>9.2f}"
  f"{'':>10s}{'':>10s}")
P("")

# ------------------------------------------------------------- observed cells (ALL reported)
P("[cells] per-event means (USD/contract, GROSS and NET at both rungs); CI95 = circular session-block")
P("        bootstrap (L=10, B=2000) of the GROSS mean, per market on its own session axis; era split R14.")
rows = []
P(f"   {'mkt':4s}{'obj':9s}{'cell':8s}{'era':9s}{'n_ev':>7s}{'n_ss':>6s}{'mean_pts':>10s}{'gross$':>9s}"
  f"{'net1$':>9s}{'net2$':>9s}{'ci_lo$':>9s}{'ci_hi$':>9s}")
for m in MKTS:
    for obj in ["SWEEP", "CONTROL", "PLACEBO"]:
        ev = events[(m, obj)]
        for cell, cmask in [("EXMACRO", ~ev["macro"]), ("MACRO", ev["macro"])]:
            sub0 = ev[cmask]
            for era, emask in [("ALL", pd.Series(True, index=sub0.index)),
                               ("2022-23", sub0["sess"] < ERA_SPLIT),
                               ("2024-26", sub0["sess"] >= ERA_SPLIT)]:
                sub = sub0[emask]
                n = len(sub)
                if n == 0:
                    rows.append(dict(market=m, obj=obj, cell=cell, era=era, n_events=0, n_sessions=0,
                                     mean_pts=np.nan, mean_usd_gross=np.nan, mean_usd_net_1tk=np.nan,
                                     mean_usd_net_2tk=np.nan, ci_lo_usd=np.nan, ci_hi_usd=np.nan))
                    P(f"   {m:4s}{obj:9s}{cell:8s}{era:9s}{0:>7,}{0:>6,}{'-':>10s}{'-':>9s}{'-':>9s}{'-':>9s}{'-':>9s}{'-':>9s}")
                    continue
                gp = sub["pnl_pts"].mean(); gu = sub["pnl_usd"].mean()
                n1 = gu - COST1[m]; n2 = gu - COST2[m]
                nss = sub["sess"].nunique()
                if era == "ALL":
                    v, cn = mkt_vec(sub, "pnl_usd", m)
                    mm = v[mkt_idx[m][0]].sum(axis=1) / np.maximum(cn[mkt_idx[m][0]].sum(axis=1), 1)
                    lo, hi = np.percentile(mm, 2.5), np.percentile(mm, 97.5)
                else:
                    lo = hi = np.nan
                rows.append(dict(market=m, obj=obj, cell=cell, era=era, n_events=n, n_sessions=nss,
                                 mean_pts=gp, mean_usd_gross=gu, mean_usd_net_1tk=n1, mean_usd_net_2tk=n2,
                                 ci_lo_usd=lo, ci_hi_usd=hi))
                ci = f"{lo:>9.2f}{hi:>9.2f}" if era == "ALL" else f"{'-':>9s}{'-':>9s}"
                P(f"   {m:4s}{obj:9s}{cell:8s}{era:9s}{n:>7,}{nss:>6,}{gp:>10.4f}{gu:>9.2f}{n1:>9.2f}{n2:>9.2f}{ci}")
cells_df = pd.DataFrame(rows)
cells_df.to_csv(os.path.join(OUT, "cells.csv"), index=False)

# pooled cells
P("   --- pooled (5 markets, USD/contract) ---")
pooled = {}
for obj in ["SWEEP", "CONTROL", "PLACEBO"]:
    for cell in ["EXMACRO", "MACRO"]:
        for era in ["ALL", "2022-23", "2024-26"]:
            evs = []
            for m in MKTS:
                ev = events[(m, obj)]
                sub = ev[~ev["macro"]] if cell == "EXMACRO" else ev[ev["macro"]]
                if era == "2022-23":
                    sub = sub[sub["sess"] < ERA_SPLIT]
                elif era == "2024-26":
                    sub = sub[sub["sess"] >= ERA_SPLIT]
                evs.append(sub)
            allv = pd.concat(evs, ignore_index=True)
            pooled[(obj, cell, era)] = allv
            if len(allv):
                gu = allv["pnl_usd"].mean()
                net2 = (allv["pnl_usd"] - allv["market"].map(COST2)).mean()
                net1 = (allv["pnl_usd"] - allv["market"].map(COST1)).mean()
                if era == "ALL":
                    v, cn = vec_on_union(*sess_panel(evs))
                    lo, hi = boot_ci(v, cn)
                    ci = f"{lo:>9.2f}{hi:>9.2f}"
                else:
                    ci = f"{'-':>9s}{'-':>9s}"
                P(f"   {'POOL':4s}{obj:9s}{cell:8s}{era:9s}{len(allv):>7,}{allv['sess'].nunique():>6,}"
                  f"{'':>10s}{gu:>9.2f}{net1:>9.2f}{net2:>9.2f}{ci}")
P("")

# ------------------------------------------------------------- G2
P("[G2] pooled ex-macro SWEEP cell (GATING cell), USD/contract at the 2tk/side rung")
sw = pooled[("SWEEP", "EXMACRO", "ALL")]
net2_ser = sw["pnl_usd"] - sw["market"].map(COST2)
net2_mean = net2_ser.mean()
gross_mean = sw["pnl_usd"].mean()
sw_net = sw.assign(net=net2_ser)
g = sw_net.groupby("sess")["net"]
vN = np.zeros(S_union); nN = np.zeros(S_union)
idx = [sess_pos[s] for s in g.sum().index]
vN[idx] = g.sum().to_numpy(); nN[idx] = g.size().to_numpy()
lo_net, hi_net = boot_ci(vN, nN)
vG, nG = vec_on_union(*sess_panel([events[(m, "SWEEP")].query("~macro") for m in MKTS]))
lo_g, hi_g = boot_ci(vG, nG)
P(f"     after-cost mean (2tk/side): {net2_mean:+.2f} $/event   (gross {gross_mean:+.2f}; 1tk/side {(sw['pnl_usd'] - sw['market'].map(COST1)).mean():+.2f})")
P(f"     session-block CI95 of the after-cost mean: [{lo_net:+.2f}, {hi_net:+.2f}]   (gross CI [{lo_g:+.2f}, {hi_g:+.2f}])")

# K_eff over 5 markets
mat = np.zeros((S_union, len(MKTS)))
present = np.zeros((S_union, len(MKTS)), dtype=bool)
for j, m in enumerate(MKTS):
    ev = events[(m, "SWEEP")].query("~macro")
    s = ev.groupby("sess")["pnl_usd"].sum()
    ii = [sess_pos[x] for x in s.index]
    mat[ii, j] = s.to_numpy()
    msess = set(data[m]["sess"].unique())
    present[:, j] = [x in msess for x in union_sessions]
cors = []
for a in range(5):
    for b in range(a + 1, 5):
        common = present[:, a] & present[:, b]
        xa, xb = mat[common, a], mat[common, b]
        if xa.std() > 0 and xb.std() > 0:
            cors.append(np.corrcoef(xa, xb)[0, 1])
rho_bar = float(np.mean(cors))
K_eff = float(np.clip(5.0 / (1.0 + 4.0 * rho_bar), 1.0, 5.0))
P(f"     K_eff over 5 markets: rho_bar = {rho_bar:+.4f} (10 pairs, session gross-sum corr) -> "
  f"K_eff = 5/(1+4*rho_bar) = {K_eff:.3f} (printed per spec; the pooled test is ONE test at alpha 0.05)")

# operative circular-shift null (R12c)
P("     OPERATIVE shared-draw CIRCULAR null (whole-session shift of the event overlay, k=1..S_union-1,")
P(f"     S_union={S_union}; entry/exit via per-session minute-slot ffilled close grids; identity-checked at k=0):")
null_sum = np.zeros(S_union)
null_cnt = np.zeros(S_union)
for m in MKTS:
    df = data[m]
    sm = sorted(df["sess"].unique())
    pos = {s: i for i, s in enumerate(sm)}
    Sp = len(sm)
    slot = ((df["mins"].to_numpy() - (18 * 60 + 1)) % 1440)
    W = 1380  # slots 0 (18:01) .. 1379 (17:00 last bar); no 17:01-17:59 or 18:00 stamps exist (verified)
    Gd = np.full((Sp, W), np.nan)
    si = df["sess"].map(pos).to_numpy()
    Gd[si, slot] = df["close"].to_numpy()
    Gd = pd.DataFrame(Gd).ffill(axis=1).to_numpy()
    ev = events[(m, "SWEEP")].query("~macro")
    e_slot = ((ev["mins"].to_numpy() - (18 * 60 + 1)) % 1440).astype(int)
    x_slot = e_slot + HOLD
    assert x_slot.max() < W
    s_i = ev["sess"].map(pos).to_numpy()
    d_i = ev["dir"].to_numpy()
    # identity at k=0
    p0 = d_i * (Gd[s_i, x_slot] - Gd[s_i, e_slot]) * PT_USD[m]
    assert np.allclose(p0, ev["pnl_usd"].to_numpy(), atol=1e-6), f"{m}: grid identity failed"
    kvec = np.arange(S_union)
    rows_k = (s_i[None, :] + kvec[:, None]) % Sp
    pnl_k = d_i[None, :] * (Gd[rows_k, x_slot[None, :]] - Gd[rows_k, e_slot[None, :]]) * PT_USD[m]
    null_sum += np.nansum(pnl_k, axis=1)
    null_cnt += np.sum(~np.isnan(pnl_k), axis=1)
    del Gd, rows_k, pnl_k
mean_k = null_sum / null_cnt
obs_shift = mean_k[0]
assert abs(obs_shift - gross_mean) < 1e-6
nulls = mean_k[1:]
p_shift = (1 + int(np.sum(np.abs(nulls) >= abs(obs_shift)))) / S_union
P(f"       obs gross mean {obs_shift:+.2f} $/ev; null mean {nulls.mean():+.2f}, sd {nulls.std(ddof=1):.2f}; "
  f"two-sided p = {p_shift:.4f}")
P("       in words: the probability, under the null that the sweep-overlay (clock slots + fade directions)")
P("       carries no session-specific information, of a pooled gross per-event mean at least this large in")
P("       magnitude when the whole overlay is circularly shifted by k sessions (shared k, all markets).")
# second computation: sign-flip
eps = rng.choice([-1.0, 1.0], size=(B_FLIP, S_union))
flip_means = (eps @ vG) / nG.sum()
p_flip = (1 + int(np.sum(np.abs(flip_means) >= abs(gross_mean)))) / (B_FLIP + 1)
P(f"       SECOND COMPUTATION (sign-flip, one shared eps per session, B={B_FLIP:,}): p = {p_flip:.4f}")
G2a = net2_mean > 0
G2b = (lo_net > 0) or (hi_net < 0)
G2c = p_shift < 0.05
G2 = G2a and G2b and G2c
P(f"     G2a after-cost mean>0: {G2a}   G2b CI excl 0: {G2b}   G2c circular p<0.05: {G2c}   => G2 {'PASS' if G2 else 'FAIL'}")
P("")

# ------------------------------------------------------------- G3 discriminator
P("[G3] THE DISCRIMINATOR: pooled ex-macro GROSS per-event mean, SWEEP minus k-sigma CONTROL;")
P("     joint circular session-block bootstrap CI95 (same draws both objects).")
ct = pooled[("CONTROL", "EXMACRO", "ALL")]
ctrl_mean = ct["pnl_usd"].mean()
vC, nC = vec_on_union(*sess_panel([events[(m, "CONTROL")].query("~macro") for m in MKTS]))
tvG = vG[IDX].sum(axis=1); tnG = nG[IDX].sum(axis=1)
tvC = vC[IDX].sum(axis=1); tnC = nC[IDX].sum(axis=1)
with np.errstate(invalid="ignore", divide="ignore"):
    deltas = tvG / np.maximum(tnG, 1) - tvC / np.maximum(tnC, 1)
delta_obs = gross_mean - ctrl_mean
d_lo, d_hi = np.percentile(deltas, 2.5), np.percentile(deltas, 97.5)
disc_rows = []
P(f"     {'mkt':6s}{'n_sweep':>8s}{'n_ctrl':>8s}{'sweep$':>9s}{'ctrl$':>9s}{'delta$':>9s}{'ci_lo':>9s}{'ci_hi':>9s}")
for m in MKTS:
    evs = events[(m, "SWEEP")].query("~macro"); evc = events[(m, "CONTROL")].query("~macro")
    vs, ns = mkt_vec(evs, "pnl_usd", m); vc, nc = mkt_vec(evc, "pnl_usd", m)
    I = mkt_idx[m][0]
    with np.errstate(invalid="ignore", divide="ignore"):
        dd = vs[I].sum(axis=1) / np.maximum(ns[I].sum(axis=1), 1) - vc[I].sum(axis=1) / np.maximum(nc[I].sum(axis=1), 1)
    dobs = evs["pnl_usd"].mean() - evc["pnl_usd"].mean()
    lo, hi = np.percentile(dd, 2.5), np.percentile(dd, 97.5)
    disc_rows.append(dict(market=m, n_sweep=len(evs), n_control=len(evc),
                          mean_sweep_usd=evs["pnl_usd"].mean(), mean_control_usd=evc["pnl_usd"].mean(),
                          delta_usd=dobs, ci_lo=lo, ci_hi=hi))
    P(f"     {m:6s}{len(evs):>8,}{len(evc):>8,}{evs['pnl_usd'].mean():>9.2f}{evc['pnl_usd'].mean():>9.2f}"
      f"{dobs:>9.2f}{lo:>9.2f}{hi:>9.2f}")
disc_rows.append(dict(market="POOLED", n_sweep=len(sw), n_control=len(ct),
                      mean_sweep_usd=gross_mean, mean_control_usd=ctrl_mean,
                      delta_usd=delta_obs, ci_lo=d_lo, ci_hi=d_hi))
P(f"     {'POOLED':6s}{len(sw):>8,}{len(ct):>8,}{gross_mean:>9.2f}{ctrl_mean:>9.2f}{delta_obs:>9.2f}{d_lo:>9.2f}{d_hi:>9.2f}")
pd.DataFrame(disc_rows).to_csv(os.path.join(OUT, "discriminator.csv"), index=False)
G3 = (delta_obs > 0) and (d_lo > 0)
P(f"     G3 clause: delta_obs > 0 AND CI lo > 0  =>  G3 {'PASS' if G3 else 'FAIL'}"
  + ("" if G3 else "  (sweep does NOT beat the generic k-sigma MR control)"))
P("")

# ------------------------------------------------------------- G4 placebo
P("[G4] vol-matched non-sweep placebo vs sweep, pooled ex-macro GROSS per-event mean")
pl = pooled[("PLACEBO", "EXMACRO", "ALL")]
plac_mean = pl["pnl_usd"].mean()
vP, nP = vec_on_union(*sess_panel([events[(m, "PLACEBO")].query("~macro") for m in MKTS]))
tvP = vP[IDX].sum(axis=1); tnP = nP[IDX].sum(axis=1)
with np.errstate(invalid="ignore", divide="ignore"):
    dP = tvG / np.maximum(tnG, 1) - tvP / np.maximum(tnP, 1)
P(f"     sweep {gross_mean:+.2f} $/ev (n={len(sw):,})  placebo {plac_mean:+.2f} $/ev (n={len(pl):,})  "
  f"delta {gross_mean - plac_mean:+.2f}  CI95 [{np.percentile(dP, 2.5):+.2f}, {np.percentile(dP, 97.5):+.2f}] (context)")
G4 = plac_mean < gross_mean
P(f"     G4 clause (spec 'shows LESS', point estimates): placebo < sweep  =>  G4 {'PASS' if G4 else 'FAIL'}")
P("")

# ------------------------------------------------------------- G5 ZB cost bar
P("[G5] ZB leg vs the spec-named G00062 cost-fragility bar (per-event GROSS >= breakeven ticks at the 2-tick rung)")
zb = events[("ZB", "SWEEP")].query("~macro")
zb_ticks = (zb["pnl_pts"] / TICK_PT["ZB"]).mean()
P(f"     ZB ex-macro sweep per-event gross: {zb_ticks:+.4f} ticks (n={len(zb):,})  "
  f"vs bar {ZB_G00062_RUNG_TICKS:.4f} ticks (${ZB_G00062_RUNG_USD:.2f}/RT G00062 model)")
P(f"     (family 2tk/side rung for scale: ${COST2['ZB']:.2f}/RT = {COST2['ZB'] / TICK_USD['ZB']:.3f} ticks)")
G5 = zb_ticks >= ZB_G00062_RUNG_TICKS
P(f"     G5 {'PASS' if G5 else 'FAIL'}" + ("" if G5 else "  -> the ZB cell is recorded COST-DEAD (non-blocking for the decision rule)"))
P("")

# ------------------------------------------------------------- G6 chronology
P("[G6] chronology: sign consistency of the pooled ex-macro GROSS mean, 2022-23 vs 2024-26")
e1 = pooled[("SWEEP", "EXMACRO", "2022-23")]; e2 = pooled[("SWEEP", "EXMACRO", "2024-26")]
m1, m2 = e1["pnl_usd"].mean(), e2["pnl_usd"].mean()
P(f"     era1 2022-23: {m1:+.2f} $/ev (n={len(e1):,})   era2 2024-26: {m2:+.2f} $/ev (n={len(e2):,})   (ZB era1 starts 2022-12-27)")
G6 = np.sign(m1) == np.sign(m2)
P(f"     G6 clause: sign(era1) == sign(era2)  =>  G6 {'PASS' if G6 else 'FAIL'}")
P("")

# ------------------------------------------------------------- G7 cost band
P("[G7] {1,2}-tick/side per-market band, pooled + per-market after-cost means (ex-macro sweep cell)")
P(f"     {'mkt':6s}{'gross$':>9s}{'net@1tk/s':>11s}{'net@2tk/s':>11s}")
for m in MKTS:
    ev = events[(m, "SWEEP")].query("~macro")
    gu = ev["pnl_usd"].mean()
    P(f"     {m:6s}{gu:>9.2f}{gu - COST1[m]:>11.2f}{gu - COST2[m]:>11.2f}")
P(f"     {'POOLED':6s}{gross_mean:>9.2f}{(sw['pnl_usd'] - sw['market'].map(COST1)).mean():>11.2f}{net2_mean:>11.2f}")
G7 = True
P("     G7: band printed for every market; the CONSERVATIVE 2tk/side rung gates G2 (30-min horizon is cost-hostile).  APPLIED")
P("")

# ------------------------------------------------------------- gate table + decision
P(HR)
P("GATE TABLE (program-printed)")
P(f"{'GATE':6s}| {'SPEC':78s}| OBSERVED | PASS-FAIL")
def gate_row(name, spec_txt, obs, ok):
    P(f"{name:6s}| {spec_txt:78s}| {obs:8s} | {'PASS' if ok else 'FAIL'}")
gate_row("G1", "MDE printed per market BEFORE any observed mean", "printed", True)
gate_row("G2", "pooled ex-macro after-cost mean>0 AND session-block CI excl 0 AND circular p<.05",
         f"{net2_mean:+.2f}$/p={p_shift:.3f}", G2)
gate_row("G3", "DISCRIMINATOR: sweep minus k-sigma control delta CI excludes 0 (delta>0)",
         f"{delta_obs:+.2f}$", G3)
gate_row("G4", "vol-matched non-sweep placebo shows LESS than the sweep cells",
         f"{plac_mean:+.2f}<{gross_mean:+.2f}" if G4 else f"{plac_mean:+.2f}!<{gross_mean:+.2f}", G4)
gate_row("G5", "ZB per-event gross >= G00062 breakeven ticks at the 2-tick rung (else COST-DEAD)",
         f"{zb_ticks:+.2f}tk", G5)
gate_row("G6", "2022-23 vs 2024-26 sign consistency, pooled ex-macro gross mean",
         f"{m1:+.1f}/{m2:+.1f}", G6)
gate_row("G7", "{1,2}-tick/side per-market band printed; conservative 2tk/side rung gates", "applied", G7)
P("")
decision = "SWEEPREV01 CANDIDATE" if (G2 and G3 and G4 and G6) else "CLOSED AT SCOPE (S28)"
P(f"DECISION RULE (spec verbatim, mechanical): G2+G3+G4+G6 {'ALL PASS' if (G2 and G3 and G4 and G6) else 'NOT all PASS'} -> {decision}")
if not (G2 and G3 and G4 and G6):
    P("   -> and with it the last open intraday-MR representation on the non-NQ complex closes.")
P(HR)

with open(os.path.join(OUT, "gate_table.txt"), "w", encoding="utf-8") as f:
    f.write(buf.getvalue())
print("\nwrote out/gate_table.txt, out/cells.csv, out/discriminator.csv")
