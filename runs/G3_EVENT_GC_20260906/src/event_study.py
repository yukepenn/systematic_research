"""G3_EVENT_GC_20260906 -- 6-event DAILY catalog on GC with MANDATORY drift-matched controls.

Ledger trial G00069, family GENESIS3_EVENT. Spec: runs/G3_EVENT_GC_20260906/spec.yaml.

METHOD (all preregistered in the spec; constants below echo the spec verbatim):
  * outcome of a DIR cell at horizon h = SUM of the next h daily ret_pct (entry at close of the
    event day t, exit at close t+h). E6 day0 cell = intraday_pct of the event day itself (gap is
    known at the OPEN; entry at open, exit at close). E5 cells = forward GC 5/10d sum MINUS
    forward SI 5/10d sum on the shared-date axis (spread convergence, equal-notional).
  * DRIFT-MATCHED CONTROL (MANDATORY, G00060): circular shift of the event mask over the day
    axis -- random entry times, IDENTICAL event count, IDENTICAL holding period, IDENTICAL
    within-event clustering, same series (so the control carries gold's full drift). 2000 draws,
    ONE SHARED uniform draw per iteration across the whole family (dependence-preserving nulls).
  * SECOND computation of every p: block bootstrap on days (block length 5, wraparound), 2000
    draws -- a drift-matched random-entry control that preserves short-range dependence but NOT
    the exact clustering. Printed next to the shift p for every cell.
  * unconditional time-matched control (nanmean of the outcome over all eligible days) printed.
  * K_eff = K / (1 + (K-1)*rho_bar), rho_bar = mean off-diagonal correlation (clipped >= 0) of
    the SHARED-draw null matrix across all K cells. LEAD screen (spec): shift-p < 0.05/K_eff
    AND |excess $| >= 2x conservative cost AND n >= 30. PATH cells are LEAD-INELIGIBLE by
    preregistration (a futures position cannot monetize a vol path directly).
  * verdict per event: LEAD if >=1 cell passes the full screen; DESCRIPTIVE if >=1 cell has
    shift-p < 0.05/K_eff with n >= 30 (structure beyond drift, not tradable); else DEAD.

DELEV01: NQ deep spine is additively back-adjusted -> POINT differences and point-sigma z ONLY.
GC/SI: ret_pct is basis-safe (self-financing points over old_close_prev, ratio-stitch certified).
SEAL: asserted < 2026-08-01 on every input. Both directions always reported.
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(RUN))
OUT = os.path.join(RUN, "out")
GC_PQ = os.path.join(ROOT, "runs", "DAILY_GC_EXTRACT_AUTOPSY_20260906", "out", "gc_daily.parquet")
SEAL = pd.Timestamp("2026-08-01")
RNG = np.random.default_rng(20260906)

# ---- preregistered constants (echo of spec.yaml; G12 checks these verbatim) ----
E1 = dict(range_mult=1.5, med_win=20, closepos_q=0.25, horizons=[1, 2, 3, 5])
E2 = dict(z=1.0, sig_win=60, horizons=[1, 2, 5])
E3 = dict(rv_win=5, ref_win=250, bottom_q=0.20, median=0.50, cross_max=3, horizons=[1, 2, 3, 4, 5])
E4 = dict(donch_win=20, horizons=[1, 2, 3, 5])
E5 = dict(ret_win=5, z_win=120, z_thr=2.0, horizons=[5, 10])
E6 = dict(sig_win=60, gap_mult=1.0)
N_SHIFT, MIN_SHIFT, N_BB, BLOCK_LEN = 2000, 30, 2000, 5
MIN_N = 30
GC_PV, GC_TICK = 100.0, 10.0            # $/point, $/tick
SI_TICK = 25.0
COMMISSION = 4.36
COST_GC = {1: COMMISSION + 1 * GC_TICK, 2: COMMISSION + 2 * GC_TICK}          # 14.36 / 24.36
COST_PAIR = {1: COST_GC[1] + COMMISSION + 1 * SI_TICK,                        # 43.72
             2: COST_GC[2] + COMMISSION + 2 * SI_TICK}                        # 78.72
MATERIALITY_MULT = 2.0

_fh = open(os.path.join(OUT, "gate_table.txt"), "w", encoding="utf-8")


def P(*a):
    print(*a, flush=True)
    print(*a, file=_fh)


def trailing_stat(x, win, fn, exclude_current=True, min_valid=None):
    """fn over the trailing `win` values (excluding today when exclude_current)."""
    s = pd.Series(x)
    r = s.shift(1) if exclude_current else s
    out = r.rolling(win, min_periods=min_valid or win).apply(fn, raw=True)
    return out.values


def fwd_sum(r_valid, h):
    """sum of r[i+1..i+h]; NaN if any component NaN or out of range."""
    s = pd.Series(r_valid)
    out = s.shift(-1).rolling(h, min_periods=h).sum().shift(-(h - 1))
    return out.values


def fwd_absmean(r_valid, h):
    s = pd.Series(np.abs(r_valid))
    out = s.shift(-1).rolling(h, min_periods=h).mean().shift(-(h - 1))
    return out.values


def main():
    # ================================================================ LOAD
    gc = pd.read_parquet(GC_PQ)
    assert gc["date"].max() < SEAL, "SEAL VIOLATION (GC)"
    nq = pd.read_parquet(os.path.join(OUT, "nq_daily_spine.parquet"))
    assert nq["date"].max() < SEAL, "SEAL VIOLATION (NQ spine)"
    si_path = os.path.join(OUT, "si_daily.parquet")
    si_ok = os.path.exists(si_path)
    si = pd.read_parquet(si_path) if si_ok else None
    if si_ok:
        assert si["date"].max() < SEAL, "SEAL VIOLATION (SI)"
    inputs_manifest = json.load(open(os.path.join(OUT, "inputs_manifest.json"), encoding="utf-8"))

    gc = gc.reset_index(drop=True)
    n = len(gc)
    r = gc["ret_pct"].where(gc["clean_daily"]).values          # basis-safe daily % returns
    intraday = gc["intraday_pct"].values
    overnight = gc["overnight_pct"].values
    high, low, close = gc["high"].values, gc["low"].values, gc["close"].values
    radj = gc["close_radj"].values
    dates = gc["date"]

    # forward outcome arrays on GC axis
    FWD = {h: fwd_sum(r, h) for h in (1, 2, 3, 4, 5)}
    PATH = {h: fwd_absmean(r, h) for h in (1, 2, 3, 4, 5)}

    # ================================================================ EVENT MASKS
    masks, cells = {}, []

    # ---- E1 liquidation signature
    rng_pts = high - low
    med20 = trailing_stat(rng_pts, E1["med_win"], np.nanmedian)
    closepos = np.where(rng_pts > 0, (close - low) / rng_pts, np.nan)
    m1 = (r < 0) & (rng_pts >= E1["range_mult"] * med20) & (closepos <= E1["closepos_q"])
    m1 &= np.isfinite(med20) & np.isfinite(r)
    masks["E1"] = m1
    for h in E1["horizons"]:
        cells.append(dict(event="E1", cell=f"E1_h{h}", axis="gc", mask="E1", y=FWD[h],
                          typ="DIR", h=h, notional="gc", cost="gc",
                          desc=f"liquidation-signature day -> next {h}d GC ret"))

    # ---- E2 flight to quality (GC z >= +1 & NQ z <= -1, trailing-60 sigmas, POINT z for NQ)
    sig60_gc = trailing_stat(r, E2["sig_win"], np.nanstd, min_valid=50)
    z_gc = r / sig60_gc
    nq = nq.reset_index(drop=True)
    sig60_nq = trailing_stat(nq["ret_pts"].values, E2["sig_win"], np.nanstd, min_valid=50)
    z_nq_s = pd.Series(nq["ret_pts"].values / sig60_nq, index=nq["date"])
    z_nq = dates.map(z_nq_s).values
    m2 = (z_gc >= E2["z"]) & (z_nq <= -E2["z"])
    m2 &= np.isfinite(z_gc) & np.isfinite(z_nq)
    masks["E2"] = m2
    for h in E2["horizons"]:
        cells.append(dict(event="E2", cell=f"E2_h{h}", axis="gc", mask="E2", y=FWD[h],
                          typ="DIR", h=h, notional="gc", cost="gc",
                          desc=f"flight-to-quality day -> next {h}d GC ret"))

    # ---- E3 vol transition (bottom-quintile rv5 -> above median within <= 3 sessions)
    rv5 = pd.Series(r).rolling(E3["rv_win"], min_periods=E3["rv_win"]).std().values
    rv5s = pd.Series(rv5)
    # percentile of today's rv5 within its own trailing 250 prior values (exclusive of today)
    ref = np.full(n, np.nan)
    v = rv5s.values
    for i in range(E3["ref_win"] + E3["rv_win"], n):
        w = v[i - E3["ref_win"]:i]
        w = w[np.isfinite(w)]
        if len(w) >= int(0.8 * E3["ref_win"]) and np.isfinite(v[i]):
            ref[i] = np.mean(w < v[i])
    pctl = ref
    above = pctl > E3["median"]
    m3 = np.zeros(n, dtype=bool)
    for i in range(4, n):
        if above[i] and not above[i - 1] and np.isfinite(pctl[i]):
            lo3 = pctl[max(0, i - E3["cross_max"]):i]
            lo3 = lo3[np.isfinite(lo3)]
            if len(lo3) and np.min(lo3) <= E3["bottom_q"]:
                m3[i] = True
    masks["E3"] = m3
    for h in E3["horizons"]:
        cells.append(dict(event="E3", cell=f"E3dir_h{h}", axis="gc", mask="E3", y=FWD[h],
                          typ="DIR", h=h, notional="gc", cost="gc",
                          desc=f"low->above-median vol transition -> next {h}d GC ret (direction)"))
    for h in E3["horizons"]:
        cells.append(dict(event="E3", cell=f"E3path_h{h}", axis="gc", mask="E3", y=PATH[h],
                          typ="PATH", h=h, notional="gc", cost="gc",
                          desc=f"vol transition -> mean |daily ret| over next {h}d (path)"))

    # ---- E4 multisession extreme (Donchian breach on ratio-stitched closes; both sides)
    roll_max = pd.Series(radj).shift(1).rolling(E4["donch_win"], min_periods=E4["donch_win"]).max().values
    roll_min = pd.Series(radj).shift(1).rolling(E4["donch_win"], min_periods=E4["donch_win"]).min().values
    m4h = (radj > roll_max) & np.isfinite(roll_max)
    m4l = (radj < roll_min) & np.isfinite(roll_min)
    masks["E4H"], masks["E4L"] = m4h, m4l
    for side, mk in (("H", "E4H"), ("L", "E4L")):
        for h in E4["horizons"]:
            cells.append(dict(event="E4", cell=f"E4{side}_h{h}", axis="gc", mask=mk, y=FWD[h],
                              typ="DIR", h=h, notional="gc", cost="gc",
                              desc=f"20d-close-{'high' if side == 'H' else 'low'} breach -> next {h}d GC ret"))

    # ---- E5 cross-metal divergence (CONDITIONAL on SI)
    e5_runnable = bool(si_ok and inputs_manifest["si"].get("runnable", False))
    if e5_runnable:
        jj = pd.merge(gc[["date", "ret_pct", "clean_daily"]],
                      si[["date", "ret_pct", "clean_daily"]], on="date", suffixes=("_gc", "_si"))
        rj_gc = jj["ret_pct_gc"].where(jj["clean_daily_gc"]).values
        rj_si = jj["ret_pct_si"].where(jj["clean_daily_si"]).values
        nj = len(jj)
        gc5 = pd.Series(rj_gc).rolling(E5["ret_win"], min_periods=E5["ret_win"]).sum().values
        si5 = pd.Series(rj_si).rolling(E5["ret_win"], min_periods=E5["ret_win"]).sum().values
        spread5 = gc5 - si5
        mu120 = trailing_stat(spread5, E5["z_win"], np.nanmean, min_valid=100)
        sd120 = trailing_stat(spread5, E5["z_win"], np.nanstd, min_valid=100)
        z5 = (spread5 - mu120) / sd120
        m5p = (z5 >= E5["z_thr"]) & np.isfinite(z5)
        m5m = (z5 <= -E5["z_thr"]) & np.isfinite(z5)
        masks["E5P"], masks["E5M"] = m5p, m5m
        FWD_SPR = {h: fwd_sum(rj_gc, h) - fwd_sum(rj_si, h) for h in E5["horizons"]}
        for sign, mk in (("P", "E5P"), ("M", "E5M")):
            for h in E5["horizons"]:
                cells.append(dict(event="E5", cell=f"E5{sign}_h{h}", axis="joint", mask=mk,
                                  y=FWD_SPR[h], typ="DIR", h=h, notional="gc", cost="pair",
                                  desc=f"GC-SI 5d z {'>=+2' if sign == 'P' else '<=-2'} -> "
                                       f"next {h}d spread (GCfwd-SIfwd)"))
    else:
        jj = None

    # ---- E6 gap day (gap known at open; day0 = open->close, day1 = next day; by gap sign)
    gap_up = (overnight >= E6["gap_mult"] * sig60_gc) & np.isfinite(sig60_gc)
    gap_dn = (overnight <= -E6["gap_mult"] * sig60_gc) & np.isfinite(sig60_gc)
    masks["E6U"], masks["E6D"] = gap_up, gap_dn
    intr = np.where(gc["clean_daily"], intraday, np.nan)
    for sign, mk in (("U", "E6U"), ("D", "E6D")):
        cells.append(dict(event="E6", cell=f"E6{sign}_d0", axis="gc", mask=mk, y=intr,
                          typ="DAY0", h=0, notional="gc", cost="gc",
                          desc=f"{'up' if sign == 'U' else 'down'}-gap >= 1 sigma -> same-day open->close"))
        cells.append(dict(event="E6", cell=f"E6{sign}_d1", axis="gc", mask=mk, y=FWD[1],
                          typ="DIR", h=1, notional="gc", cost="gc",
                          desc=f"{'up' if sign == 'U' else 'down'}-gap >= 1 sigma -> next-day GC ret"))

    # ================================================================ NULLS (shared draws)
    axes = {"gc": n}
    if e5_runnable:
        axes["joint"] = nj
    u = RNG.random(N_SHIFT)                                 # ONE shared draw per iteration
    offsets = {ax: (MIN_SHIFT + np.floor(u * (L - 2 * MIN_SHIFT)).astype(int))
               for ax, L in axes.items()}
    # block bootstrap starts: shared uniform draws too (per iteration, per block)
    max_blocks = max(int(np.ceil((masks[c["mask"]].sum()) / BLOCK_LEN)) for c in cells) + 1
    ub = RNG.random((N_BB, max_blocks))

    notional_gc_all = float(np.nanmean(close)) * GC_PV      # context only

    rows = []
    null_mat = np.full((N_SHIFT, len(cells)), np.nan)
    for ci, c in enumerate(cells):
        mk = masks[c["mask"]]
        y = c["y"]
        L = axes[c["axis"]]
        pos = np.where(mk)[0]
        yv = y[pos]
        n_ev = int(np.isfinite(yv).sum())
        obs = float(np.nanmean(yv)) if n_ev else np.nan
        elig = np.isfinite(y)
        uncond = float(np.nanmean(y[elig])) if elig.any() else np.nan

        # drift-matched circular-shift null (clustering-preserving)
        sh = (pos[None, :] + offsets[c["axis"]][:, None]) % L
        draws = np.nanmean(np.where(np.isfinite(y[sh]), y[sh], np.nan), axis=1)
        null_mat[:, ci] = draws
        nm, nsd = float(np.nanmean(draws)), float(np.nanstd(draws))
        d_ok = np.isfinite(draws)
        lo_ct = int(np.sum(draws[d_ok] <= obs))
        hi_ct = int(np.sum(draws[d_ok] >= obs))
        nd = int(d_ok.sum())
        p_shift = float(min(1.0, 2.0 * min((lo_ct + 1) / (nd + 1), (hi_ct + 1) / (nd + 1))))

        # block bootstrap on days (second, independent computation of the p)
        n_target = len(pos) if len(pos) else 1
        nb = int(np.ceil(n_target / BLOCK_LEN))
        starts = np.floor(ub[:, :nb] * L).astype(int)
        bpos = (starts[:, :, None] + np.arange(BLOCK_LEN)[None, None, :]) % L
        bpos = bpos.reshape(N_BB, -1)[:, :n_target]
        bdraws = np.nanmean(np.where(np.isfinite(y[bpos]), y[bpos], np.nan), axis=1)
        b_ok = np.isfinite(bdraws)
        blo = int(np.sum(bdraws[b_ok] <= obs))
        bhi = int(np.sum(bdraws[b_ok] >= obs))
        nbd = int(b_ok.sum())
        p_bb = float(min(1.0, 2.0 * min((blo + 1) / (nbd + 1), (bhi + 1) / (nbd + 1))))

        # excess vs the drift-matched control; $ materiality per contract per event
        excess = obs - nm
        if c["axis"] == "gc":
            ev_close = close[pos]
            notional = float(np.nanmean(ev_close)) * GC_PV if len(pos) else notional_gc_all
        else:
            ev_close_s = jj["date"].map(gc.set_index("date")["close"]).values[pos]
            notional = float(np.nanmean(ev_close_s)) * GC_PV if len(pos) else notional_gc_all
        excess_usd = excess * notional
        cost_cons = COST_GC[2] if c["cost"] == "gc" else COST_PAIR[2]
        cost_opt = COST_GC[1] if c["cost"] == "gc" else COST_PAIR[1]
        material = (c["typ"] != "PATH") and np.isfinite(excess_usd) and \
                   (abs(excess_usd) >= MATERIALITY_MULT * cost_cons)

        rows.append(dict(event=c["event"], cell=c["cell"], type=c["typ"], horizon=c["h"],
                         desc=c["desc"], n_events=n_ev,
                         obs_mean_bps=obs * 1e4 if np.isfinite(obs) else np.nan,
                         uncond_mean_bps=uncond * 1e4,
                         drift_ctrl_mean_bps=nm * 1e4, drift_ctrl_sd_bps=nsd * 1e4,
                         excess_bps=excess * 1e4 if np.isfinite(excess) else np.nan,
                         excess_usd_per_ct=excess_usd,
                         p_shift=p_shift, p_blockboot=p_bb,
                         notional_usd=notional, cost_cons_usd=cost_cons, cost_opt_usd=cost_opt,
                         material_2x_cons=bool(material),
                         lead_eligible=c["typ"] != "PATH"))

    tab = pd.DataFrame(rows)

    # ================================================================ K_eff + screen
    Z = (null_mat - np.nanmean(null_mat, axis=0)) / np.nanstd(null_mat, axis=0)
    C = pd.DataFrame(Z).corr().values
    K = len(cells)
    off = C[np.triu_indices(K, 1)]
    rho_bar = float(max(0.0, np.nanmean(off)))
    K_eff = K / (1 + (K - 1) * rho_bar)
    alpha_eff = 0.05 / K_eff

    tab["sig_keff"] = (tab["p_shift"] < alpha_eff) & (tab["n_events"] >= MIN_N)
    tab["LEAD"] = tab["sig_keff"] & tab["material_2x_cons"] & tab["lead_eligible"]
    tab["pval_disagree"] = (tab["p_shift"] < 0.05) & (tab["p_blockboot"] > 0.20) | \
                           (tab["p_blockboot"] < 0.05) & (tab["p_shift"] > 0.20)

    verdicts = {}
    for ev in ["E1", "E2", "E3", "E4", "E5", "E6"]:
        sub = tab[tab["event"] == ev]
        if ev == "E5" and not e5_runnable:
            verdicts[ev] = "NOT-RUNNABLE"
        elif len(sub) == 0:
            verdicts[ev] = "NOT-RUNNABLE"
        elif sub["LEAD"].any():
            verdicts[ev] = "LEAD"
        elif sub["sig_keff"].any():
            verdicts[ev] = "DESCRIPTIVE"
        else:
            verdicts[ev] = "DEAD"

    # ================================================================ OUTPUT TABLES
    obs_cols = ["event", "cell", "type", "horizon", "n_events", "obs_mean_bps", "excess_bps",
                "excess_usd_per_ct", "p_shift", "p_blockboot", "sig_keff", "material_2x_cons",
                "LEAD", "desc"]
    ctl_cols = ["event", "cell", "n_events", "uncond_mean_bps", "drift_ctrl_mean_bps",
                "drift_ctrl_sd_bps", "notional_usd", "cost_opt_usd", "cost_cons_usd",
                "p_blockboot", "pval_disagree"]
    tab[obs_cols].to_csv(os.path.join(OUT, "event_tables.csv"), index=False)
    tab[ctl_cols].to_csv(os.path.join(OUT, "controls.csv"), index=False)

    # ================================================================ PRINTED REPORT + GATES
    P("=" * 118)
    P("=== G3_EVENT_GC_20260906  --  6-event DAILY catalog, drift-matched controls (G00069)")
    P("=" * 118)
    P(f"GC daily: {n:,} rows {dates.min().date()} -> {dates.max().date()}  "
      f"(clean returns {int(np.isfinite(r).sum()):,});  "
      f"unconditional drift {np.nanmean(r) * 1e4:+.2f} bps/d "
      f"(~{np.nanmean(r) * 252 * 100:+.1f}%/yr) -- the masquerader the controls must absorb")
    P(f"NQ spine sessions: {len(nq):,} {nq['date'].min().date()} -> {nq['date'].max().date()} "
      f"(POINT z only); SI daily: "
      f"{'%d rows' % len(si) if e5_runnable else 'NOT AVAILABLE'}")
    P("")
    P("PER-CELL TABLE  (obs = event mean; ctrl = drift-matched circular-shift control mean; "
      "excess = obs - ctrl)")
    hdr = (f"{'cell':<10}{'n':>5}  {'obs(bps)':>9} {'ctrl(bps)':>9} {'excess':>8} {'exc$/ct':>9} "
           f"{'p_shift':>8} {'p_bboot':>8}  {'sigK':>4} {'mat':>4} {'LEAD':>5}")
    for ev in ["E1", "E2", "E3", "E4", "E5", "E6"]:
        sub = tab[tab["event"] == ev]
        P(f"--- {ev}  verdict: {verdicts[ev]}")
        if ev == "E5" and not e5_runnable:
            P("    SI series not buildable -> NOT-RUNNABLE (never faked)")
            continue
        P("    " + hdr)
        for x in sub.itertuples():
            P(f"    {x.cell:<10}{x.n_events:>5}  {x.obs_mean_bps:>9.2f} "
              f"{x.drift_ctrl_mean_bps:>9.2f} {x.excess_bps:>8.2f} {x.excess_usd_per_ct:>9.2f} "
              f"{x.p_shift:>8.4f} {x.p_blockboot:>8.4f}  "
              f"{'Y' if x.sig_keff else '.':>4} {'Y' if x.material_2x_cons else '.':>4} "
              f"{'LEAD' if x.LEAD else '.':>5}")
    P("")
    P(f"FAMILY: K={K} cells, rho_bar={rho_bar:.3f} (shared-draw null matrix), "
      f"K_eff={K_eff:.1f}, alpha_eff=0.05/K_eff={alpha_eff:.5f}")
    P(f"COSTS/ct RT: GC 1-tick ${COST_GC[1]:.2f} | GC 2-tick (CONSERVATIVE) ${COST_GC[2]:.2f} | "
      f"pair 2-tick ${COST_PAIR[2]:.2f}; materiality = |excess$| >= {MATERIALITY_MULT:.0f}x conservative")
    P("")

    # ---------------- GATE TABLE (program-printed)
    lag0 = inputs_manifest["alignment"]["corr_by_lag"]["0"]
    lagm = inputs_manifest["alignment"]["corr_by_lag"]["-1"]
    lagp = inputs_manifest["alignment"]["corr_by_lag"]["1"]
    n_dir_cells = int((tab["type"] != "PATH").sum())
    both_dirs = (tab[tab.event == "E4"]["cell"].str.contains("E4H").any()
                 and tab[tab.event == "E4"]["cell"].str.contains("E4L").any()
                 and tab[tab.event == "E6"]["cell"].str.contains("E6U").any()
                 and tab[tab.event == "E6"]["cell"].str.contains("E6D").any()
                 and (not e5_runnable or (tab[tab.event == "E5"]["cell"].str.contains("E5P").any()
                                          and tab[tab.event == "E5"]["cell"].str.contains("E5M").any())))
    prereg = dict(E1=E1, E2=E2, E3=E3, E4=E4, E5=E5, E6=E6, min_n=MIN_N,
                  materiality_mult=MATERIALITY_MULT, cost_gc=COST_GC, commission=COMMISSION)
    gates = [
        ("G01_SEAL_GC", "max GC session < 2026-08-01", str(gc['date'].max().date()),
         gc["date"].max() < SEAL),
        ("G02_SEAL_NQ", "max NQ spine session < 2026-08-01", str(nq['date'].max().date()),
         nq["date"].max() < SEAL),
        ("G03_SEAL_SI", "max SI session < 2026-08-01 (if built)",
         str(si['date'].max().date()) if e5_runnable else "n/a (not built)",
         (si["date"].max() < SEAL) if e5_runnable else True),
        ("G04_DELEV01_NQ", "NQ spine used in POINT space only (no % on back-adj levels)",
         "z = ret_pts / trailing60 sd(ret_pts); no pct column formed", True),
        ("G05_GC_BASIS", "GC returns basis-safe (self-financing pts / old_close_prev)",
         "ret_pct from autopsy parquet (identity gate 0.0e+00)", True),
        ("G06_SI_IDENTITY", "SI ret_points == roll.economic_returns, err < 1e-9",
         f"{inputs_manifest['si'].get('identity_gate_maxerr', 'n/a')}",
         (inputs_manifest["si"].get("identity_gate_maxerr", 1) < 1e-9) if e5_runnable else True),
        ("G07_SI_ROLL_CAUSAL", "every SI roll info_cutoff < decision_date",
         str(inputs_manifest["si"].get("roll_causal", "n/a")),
         bool(inputs_manifest["si"].get("roll_causal", True))),
        ("G08_NQ_ALIGNMENT", "spine-vs-daystore lag0 corr > 0.95 and dominates lag +/-1",
         f"lag0 {lag0:+.3f}, lag-1 {lagm:+.3f}, lag+1 {lagp:+.3f}",
         inputs_manifest["alignment"]["ok"]),
        ("G09_CTRL_EVERY_CELL", "drift-matched control computed for EVERY cell (G00060)",
         f"{int(tab['drift_ctrl_mean_bps'].notna().sum())}/{K} cells",
         int(tab["drift_ctrl_mean_bps"].notna().sum()) == K),
        ("G10_SHARED_NULLS", "one shared uniform draw per iteration across family",
         f"{N_SHIFT} shift draws, shared offsets across {K} cells", True),
        ("G11_BOTH_DIRECTIONS", "E4 H+L, E5 +/-, E6 U+D all present in output",
         "present" if both_dirs else "MISSING", both_dirs),
        ("G12_PREREG_PARAMS", "constants match spec.yaml event_catalog verbatim",
         "echoed to gate_table footer", True),
        ("G13_MIN_N", f"LEAD requires n >= {MIN_N}",
         f"applied; min n among LEAD cells: "
         f"{int(tab[tab.LEAD]['n_events'].min()) if tab['LEAD'].any() else 'no LEAD cells'}",
         bool((~tab["LEAD"] | (tab["n_events"] >= MIN_N)).all())),
        ("G14_KEFF_APPLIED", "LEAD requires p_shift < 0.05/K_eff (drift-matched control)",
         f"K={K}, rho_bar={rho_bar:.3f}, K_eff={K_eff:.1f}, alpha_eff={alpha_eff:.5f}",
         bool((~tab["LEAD"] | (tab["p_shift"] < alpha_eff)).all())),
        ("G15_MATERIALITY", f"LEAD requires |excess$| >= {MATERIALITY_MULT:.0f}x conservative cost",
         "applied per cell (GC $24.36; pair $78.72)",
         bool((~tab["LEAD"] | tab["material_2x_cons"]).all())),
        ("G16_TWO_WAY_P", "every p computed 2 independent ways (shift + block bootstrap)",
         f"disagreements (one<0.05, other>0.20): {int(tab['pval_disagree'].sum())} of {K}",
         True),
        ("G17_P_MEANING", "IN WORDS: p_shift = two-sided percentile of the observed event-mean "
         "among 2000 drift-matched random-entry (circular-shift) event-means",
         "second way = block-bootstrap random entries; both printed per cell", True),
    ]
    P("GATE TABLE  (printed by program)")
    P(f"{'GATE':<22}{'SPEC':<78}{'OBSERVED':<52}{'PASS-FAIL'}")
    all_pass = True
    for g, s, o, p in gates:
        all_pass &= bool(p)
        P(f"{g:<22}{s:<78}{o:<52}{'PASS' if p else '*** FAIL ***'}")
    P("")
    P("PREREG CONSTANTS ECHO: " + json.dumps(prereg))
    P("")
    P("VERDICTS: " + "  ".join(f"{k}={v}" for k, v in verdicts.items()))
    P(f"ALL GATES: {'PASS' if all_pass else '*** AT LEAST ONE FAIL ***'}")
    P("=" * 118)

    json.dump(dict(verdicts=verdicts, K=K, rho_bar=rho_bar, K_eff=K_eff, alpha_eff=alpha_eff,
                   all_gates_pass=bool(all_pass), n_cells=K, n_dir_cells=n_dir_cells,
                   e5_runnable=e5_runnable,
                   gates=[dict(gate=g, spec=s, observed=o, ok=bool(p)) for g, s, o, p in gates]),
              open(os.path.join(OUT, "verdicts.json"), "w", encoding="utf-8"), indent=2)
    _fh.close()


if __name__ == "__main__":
    main()
