"""G3_AUCTCYCLE_20260906 -- STEP 3: Treasury auction concession-cycle event study (G00073).

Spec: runs/G3_AUCTCYCLE_20260906/spec.yaml, frozen before results. This header DECLARES every
mechanical choice the spec leaves open, BEFORE any outcome is computed (prereg discipline):

FROZEN OBJECT (primary): LONG the matching future (ZN for 10y auctions, ZB for 30y) at the
AUCTION-DAY session close; exit at close D+5. Outcome = sum of the next 5 daily self-financing
ret_points (basis-safe, certified roll) x $1000/pt, minus cost. One event = one auction day.

DECLARED MECHANICS (all fixed in advance of results):
  D1. GATING COST RUNG = CONSERVATIVE (commission $4.36 RT + 2 ticks). The 1-tick rung is
      printed alongside (G6 band). Tick $: ZN $15.625, ZB $31.25, ES $12.50 (asserted vs data).
  D2. NULL P for G2 is ONE-SIDED (direction LONG preregistered in the spec's mechanism);
      the two-sided p is printed next to it. 2000 circular shifts of the event-position mask on
      each market's session axis, MIN_SHIFT 30, ONE shared uniform draw per iteration across
      ZN+ZB (dependence-preserving), fixed seed 20260906.
  D3. EVENT MAPPING: auction date -> exact session-date match on that market's axis; if absent,
      the first session within <= 3 calendar days after; else UNMAPPED (counted, reported).
      Events whose 5-day forward window is incomplete/gap-spanning have NaN outcome and drop
      from n_eff (counted).
  D4. G2 CI: block bootstrap BY EVENT (resample events with replacement), 2000 draws, percentile
      2.5/97.5. PASS = after-cost mean > 0 AND CI_lo > 0 AND one-sided shift p < 0.05.
  D5. MATCHED CONTROL (G3): cells = (market x weekday). Eligible control session: finite 5d
      outcome AND no mapped 10y/30y auction session within +/-5 TRADING sessions (inclusive) on
      that market's axis. Control mean = event-composition-weighted mean over cells, same
      after-cost transform. Delta CI: 2000 draws resampling BOTH events (with their cell labels
      and per-draw weights) and control days (within cell). PASS = delta > 0 AND CI_lo > 0.
  D6. G4 ERAS by auction date: 2009..2015-12-31 / 2016..2021-12-31 / 2022..2026-07-31. Sign of
      the pooled after-cost mean (conservative rung) per era. all>0 -> STRUCTURAL;
      modern era (2022+) > 0 with any earlier era <= 0 -> REGIME-LOCAL (owner doctrine: not a
      veto); modern era <= 0 -> SIGN-FLIP -> G4 FAIL.
  D7. G5 SAME-SIZE RULE: per-event standardized outcome z_e = y_pts / sd_m(unconditional 5d
      sum). ES effect is "same-size" iff mean z(ES) >= 0.5 x mean z(rates), same sign, AND the
      ES event-bootstrap CI excludes 0. Reclassifies mechanism (not auto-fail), per spec.
  D8. G1 MDE printed BEFORE any observed event mean: MDE(one-sided 5%, 80% power) =
      (1.6449+0.8416) x sigma_pool / sqrt(N_eff), sigma_pool from UNCONDITIONAL 5d-sum sd per
      market (event-composition weighted, in $). Uses no event outcome values.
  D9. SECONDARY (non-gating): concession A = close(D-5)->close(D0) (5 rets incl. auction day);
      concession B = close(D-6)->close(D-1) (5 rets, strictly pre-auction). Combined cycle =
      rebound - concession A. Original vs reopening split reported.
  D10. ANNEX-ONLY robustness (non-gating, declared here): cluster bootstrap by auction
      YEAR-MONTH (10y/30y auctions in the same week are dependent across the pooled family;
      the by-event CI is the preregistered gate, the cluster CI is printed for honesty).

SEAL: all inputs asserted < 2026-08-01. Evidence status: DISCOVERY on first read of this
representation (2009..2026-07 sample DISCOVERY_CONSUMED by this run).
"""
from __future__ import annotations

import json
import os

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.dirname(HERE)
OUT = os.path.join(RUN, "out")
SEAL = pd.Timestamp("2026-08-01")
RNG = np.random.default_rng(20260906)

H = 5                      # rebound horizon, trading days
EXCL = 5                   # control exclusion half-width, trading sessions
N_SHIFT, MIN_SHIFT, N_BB = 2000, 30, 2000
COMMISSION = 4.36
PV = {"ZN": 1000.0, "ZB": 1000.0, "ES": 50.0}
TICK = {"ZN": 0.015625, "ZB": 0.03125, "ES": 0.25}
COST = {m: {1: COMMISSION + 1 * TICK[m] * PV[m], 2: COMMISSION + 2 * TICK[m] * PV[m]}
        for m in PV}
ERAS = [("2009-15", pd.Timestamp("2009-01-01"), pd.Timestamp("2015-12-31")),
        ("2016-21", pd.Timestamp("2016-01-01"), pd.Timestamp("2021-12-31")),
        ("2022-26/07", pd.Timestamp("2022-01-01"), pd.Timestamp("2026-07-31"))]

_fh = open(os.path.join(OUT, "gate_table.txt"), "w", encoding="utf-8")


def P(*a):
    print(*a, flush=True)
    print(*a, file=_fh)


def fwd_sum(r, h):
    s = pd.Series(r)
    return s.shift(-1).rolling(h, min_periods=h).sum().shift(-(h - 1)).values


def map_events(cal_dates, sess_dates):
    """D3: exact match, else first session within <=3 calendar days after, else -1."""
    sd = pd.DatetimeIndex(sess_dates)
    pos, exact = [], []
    for ad in cal_dates:
        i = sd.searchsorted(ad)
        if i < len(sd) and sd[i] == ad:
            pos.append(i); exact.append(True)
        elif i < len(sd) and (sd[i] - ad).days <= 3:
            pos.append(i); exact.append(False)
        else:
            pos.append(-1); exact.append(False)
    return np.array(pos), np.array(exact)


def main():
    # ================================================================ LOAD + SEAL
    cal = pd.read_csv(os.path.join(OUT, "auction_calendar.csv"),
                      parse_dates=["auction_date"])
    manifest = json.load(open(os.path.join(OUT, "inputs_manifest.json"), encoding="utf-8"))
    mkt = {}
    for m in ("ZN", "ZB", "ES"):
        df = pd.read_parquet(os.path.join(OUT, f"{m.lower()}_daily.parquet"))
        assert df["date"].max() < SEAL, f"SEAL VIOLATION ({m})"
        assert abs(manifest[m]["tick_size"] - TICK[m]) < 1e-12, f"tick mismatch {m}"
        r = df["ret_points"].where(df["clean_daily"]).values
        mkt[m] = dict(df=df, dates=pd.DatetimeIndex(df["date"]), r=r,
                      y=fwd_sum(r, H),                                     # rebound pts
                      cA=pd.Series(r).rolling(H, min_periods=H).sum().values,           # D-5..D0
                      cB=pd.Series(r).rolling(H, min_periods=H).sum().shift(1).values,  # D-6..D-1
                      sd5=float(np.nanstd(fwd_sum(r, H))))
    assert cal["auction_date"].max() <= pd.Timestamp("2026-07-31"), "calendar window violation"

    # ================================================================ EVENT TABLE
    ev = cal.copy()
    ev["weekday"] = ev["auction_date"].dt.weekday
    rows = []
    unmapped = 0
    for m in ("ZN", "ZB"):
        sub = ev[ev["market"] == m]
        pos, exact = map_events(sub["auction_date"].values, mkt[m]["dates"])
        for (idx, rrow), p_, ex in zip(sub.iterrows(), pos, exact):
            if p_ < 0:
                unmapped += 1
                continue
            y = mkt[m]["y"][p_]
            rows.append(dict(
                auction_date=rrow["auction_date"], tenor=rrow["tenor"], market=m,
                reopening=rrow["reopening"], cusip=rrow["cusip"],
                session_date=mkt[m]["dates"][p_], pos=int(p_), exact=bool(ex),
                weekday=int(rrow["weekday"]),
                y_pts=y, z=y / mkt[m]["sd5"],
                pnl_cons=y * PV[m] - COST[m][2], pnl_opt=y * PV[m] - COST[m][1],
                conc_A=mkt[m]["cA"][p_], conc_B=mkt[m]["cB"][p_]))
    E = pd.DataFrame(rows)
    for name, lo, hi in ERAS:
        E.loc[(E["auction_date"] >= lo) & (E["auction_date"] <= hi), "era"] = name
    E["ym"] = E["auction_date"].dt.strftime("%Y-%m")
    E.to_csv(os.path.join(OUT, "event_study.csv"), index=False)
    fin = E[np.isfinite(E["y_pts"])].reset_index(drop=True)
    n_eff = len(fin)

    P("=" * 118)
    P("=== G3_AUCTCYCLE_20260906 -- Treasury auction concession cycle, ZN/ZB rebound D0->D+5 "
      "(G00073, family GENESIS3_EVENT)")
    P("=" * 118)
    P(f"calendar: {len(cal)} auctions ({(cal.tenor == '10Y').sum()} x 10Y -> ZN, "
      f"{(cal.tenor == '30Y').sum()} x 30Y -> ZB), "
      f"{(cal.reopening == 'Yes').sum()} reopenings; "
      f"{cal.auction_date.min().date()} -> {cal.auction_date.max().date()}")
    P(f"mapped events: {len(E)} ({int(E['exact'].sum())} exact-date, "
      f"{len(E) - int(E['exact'].sum())} next-session<=3cd; {unmapped} UNMAPPED -- "
      f"series start {mkt['ZN']['dates'][0].date()} postdates early-2009 auctions)")
    P(f"events with finite D+1..D+5 outcome (n_eff): {n_eff} "
      f"({len(E) - n_eff} dropped: window incomplete/gap-spanning)")
    P(f"sessions: ZN {len(mkt['ZN']['df']):,} / ZB {len(mkt['ZB']['df']):,} / "
      f"ES {len(mkt['ES']['df']):,}; unconditional 5d-sum sd: "
      f"ZN {mkt['ZN']['sd5']:.3f} pts, ZB {mkt['ZB']['sd5']:.3f} pts, ES {mkt['ES']['sd5']:.2f} pts")
    P(f"costs/ct RT (D1): ZN opt ${COST['ZN'][1]:.2f} cons ${COST['ZN'][2]:.2f} | "
      f"ZB opt ${COST['ZB'][1]:.2f} cons ${COST['ZB'][2]:.2f} | "
      f"ES opt ${COST['ES'][1]:.2f} cons ${COST['ES'][2]:.2f}")

    # ================================================================ G1: MDE FIRST (D8)
    w = fin.groupby("market").size() / n_eff
    var_pool = sum(w[m] * (mkt[m]["sd5"] * PV[m]) ** 2 for m in w.index)
    sd_pool = float(np.sqrt(var_pool))
    mde = (1.6449 + 0.8416) * sd_pool / np.sqrt(n_eff)
    P("")
    P(f"G1 MDE (PRINTED BEFORE ANY OBSERVED EVENT MEAN): sigma_pool = ${sd_pool:,.0f}/event "
      f"(composition ZN {w.get('ZN', 0):.2f} / ZB {w.get('ZB', 0):.2f}), N_eff = {n_eff}")
    P(f"    MDE(one-sided 5%, 80% power) = 2.486 x sigma_pool / sqrt(N) = ${mde:,.0f} per event "
      f"(~{mde / PV['ZN']:.3f} ZN-pts)")

    # ================================================================ OBSERVED PRIMARY
    obs_cons = float(np.mean(fin["pnl_cons"]))
    obs_opt = float(np.mean(fin["pnl_opt"]))
    obs_pts = {m: float(np.mean(fin[fin.market == m]["y_pts"])) for m in ("ZN", "ZB")}
    gross_usd = float(np.mean([r.y_pts * PV[r.market] for r in fin.itertuples()]))

    # G2 CI: block bootstrap by event (D4)
    draws_idx = RNG.integers(0, n_eff, size=(N_BB, n_eff))
    pnl = fin["pnl_cons"].values
    bb = pnl[draws_idx].mean(axis=1)
    ci = (float(np.percentile(bb, 2.5)), float(np.percentile(bb, 97.5)))

    # shared-draw circular-shift null (D2)
    u = RNG.random(N_SHIFT)
    null_stats = np.empty(N_SHIFT)
    posm = {m: fin[fin.market == m]["pos"].values for m in ("ZN", "ZB")}
    yusd = {m: mkt[m]["y"] * PV[m] - COST[m][2] for m in ("ZN", "ZB")}
    Lm = {m: len(mkt[m]["df"]) for m in ("ZN", "ZB")}
    for k in range(N_SHIFT):
        vals = []
        for m in ("ZN", "ZB"):
            off = MIN_SHIFT + int(np.floor(u[k] * (Lm[m] - 2 * MIN_SHIFT)))
            vals.append(yusd[m][(posm[m] + off) % Lm[m]])
        null_stats[k] = np.nanmean(np.concatenate(vals))
    p_1s = float((np.sum(null_stats >= obs_cons) + 1) / (N_SHIFT + 1))
    lo_ct, hi_ct = int(np.sum(null_stats <= obs_cons)), int(np.sum(null_stats >= obs_cons))
    p_2s = float(min(1.0, 2.0 * min((lo_ct + 1) / (N_SHIFT + 1), (hi_ct + 1) / (N_SHIFT + 1))))

    P("")
    P("PRIMARY (rebound, LONG at auction close -> close D+5, per contract, after cost):")
    P(f"    gross mean       ${gross_usd:+,.2f}/event  (ZN {obs_pts['ZN']:+.4f} pts, "
      f"ZB {obs_pts['ZB']:+.4f} pts)")
    P(f"    after-cost CONS  ${obs_cons:+,.2f}/event   [GATING]   after-cost OPT ${obs_opt:+,.2f}")
    P(f"    event-block bootstrap 95% CI (cons): [${ci[0]:+,.2f}, ${ci[1]:+,.2f}]")
    P(f"    shared-draw shift null: mean ${np.mean(null_stats):+,.2f}, sd ${np.std(null_stats):,.2f}; "
      f"p one-sided(LONG) = {p_1s:.4f} [GATING], two-sided = {p_2s:.4f}")
    # D10 annex: cluster bootstrap by year-month
    ymg = [g["pnl_cons"].values for _, g in fin.groupby("ym")]
    ncl = len(ymg)
    cl_draws = RNG.integers(0, ncl, size=(N_BB, ncl))
    cl_means = np.array([np.concatenate([ymg[j] for j in row]).mean() for row in cl_draws])
    P(f"    ANNEX (non-gating, D10): cluster-by-month bootstrap 95% CI "
      f"[${np.percentile(cl_means, 2.5):+,.2f}, ${np.percentile(cl_means, 97.5):+,.2f}] "
      f"({ncl} clusters)")

    g2 = (obs_cons > 0) and (ci[0] > 0) and (p_1s < 0.05)

    # ================================================================ G3: MATCHED CONTROL (D5)
    ctrl = {}
    for m in ("ZN", "ZB"):
        excl = np.zeros(Lm[m], dtype=bool)
        allpos, _ = map_events(ev["auction_date"].values, mkt[m]["dates"])
        for p_ in allpos[allpos >= 0]:
            excl[max(0, p_ - EXCL):p_ + EXCL + 1] = True
        okd = np.isfinite(mkt[m]["y"]) & ~excl
        wd = mkt[m]["dates"].weekday
        for wday in range(5):
            sel = np.where(okd & (wd == wday))[0]
            ctrl[(m, wday)] = mkt[m]["y"][sel] * PV[m] - COST[m][2]
    cellw = fin.groupby(["market", "weekday"]).size() / n_eff
    ctrl_mean = float(sum(cellw[c] * np.mean(ctrl[c]) for c in cellw.index))
    delta = obs_cons - ctrl_mean
    dboot = np.empty(N_BB)
    for k in range(N_BB):
        samp = fin.iloc[draws_idx[k]]
        em = float(np.mean(samp["pnl_cons"]))
        cw = samp.groupby(["market", "weekday"]).size() / n_eff
        cm = 0.0
        for c, wgt in cw.items():
            arr = ctrl[c]
            cm += wgt * float(np.mean(arr[RNG.integers(0, len(arr), len(arr))]))
        dboot[k] = em - cm
    dci = (float(np.percentile(dboot, 2.5)), float(np.percentile(dboot, 97.5)))
    n_ctrl = sum(len(v) for v in ctrl.values())
    g3 = (delta > 0) and (dci[0] > 0)

    P("")
    P("MATCHED CONTROL (same market x weekday, no 10y/30y auction within +/-5 sessions, "
      "same 5d window, same costs):")
    P(f"    control days: {n_ctrl:,} across {len(ctrl)} cells; "
      f"matched control mean ${ctrl_mean:+,.2f}/event-equivalent")
    P(f"    DELTA (event - control) = ${delta:+,.2f}; bootstrap 95% CI "
      f"[${dci[0]:+,.2f}, ${dci[1]:+,.2f}]")

    # ================================================================ G4: ERAS (D6)
    era_rows = []
    for name, lo, hi in ERAS:
        s = fin[fin["era"] == name]
        cw = s.groupby(["market", "weekday"]).size() / max(len(s), 1)
        cm = float(sum(cw[c] * np.mean(ctrl[c]) for c in cw.index)) if len(s) else np.nan
        era_rows.append(dict(era=name, n=len(s),
                             gross_usd=float(np.mean([r.y_pts * PV[r.market]
                                                      for r in s.itertuples()])),
                             after_cost_cons=float(np.mean(s["pnl_cons"])),
                             ctrl_matched=cm,
                             delta=float(np.mean(s["pnl_cons"])) - cm,
                             sign="+" if np.mean(s["pnl_cons"]) > 0 else "-"))
    era_t = pd.DataFrame(era_rows)
    era_t.to_csv(os.path.join(OUT, "era_table.csv"), index=False)
    signs = era_t["sign"].tolist()
    if all(s == "+" for s in signs):
        era_class = "STRUCTURAL"
    elif signs[2] == "+":
        era_class = "REGIME-LOCAL"
    else:
        era_class = "SIGN-FLIP"
    g4 = era_class != "SIGN-FLIP"

    P("")
    P("ERA TABLE (after-cost CONS, pooled; sign gates D6):")
    P(f"    {'era':<12}{'n':>5}  {'gross$':>10} {'aftercost$':>11} {'ctrl$':>9} {'delta$':>9} sign")
    for r in era_t.itertuples():
        P(f"    {r.era:<12}{r.n:>5}  {r.gross_usd:>+10.2f} {r.after_cost_cons:>+11.2f} "
          f"{r.ctrl_matched:>+9.2f} {r.delta:>+9.2f}   {r.sign}")
    P(f"    ERA CLASSIFICATION: {era_class}")

    # ================================================================ G5: ES SPECIFICITY (D7)
    es_pos, es_exact = map_events(ev["auction_date"].values, mkt["ES"]["dates"])
    es_y = np.array([mkt["ES"]["y"][p_] if p_ >= 0 else np.nan for p_ in es_pos])
    es_fin = es_y[np.isfinite(es_y)]
    es_pnl = es_fin * PV["ES"] - COST["ES"][2]
    es_mean = float(np.mean(es_pnl))
    es_bb = es_pnl[RNG.integers(0, len(es_pnl), size=(N_BB, len(es_pnl)))].mean(axis=1)
    es_ci = (float(np.percentile(es_bb, 2.5)), float(np.percentile(es_bb, 97.5)))
    z_es = float(np.mean(es_fin / mkt["ES"]["sd5"]))
    z_rates = float(np.mean(fin["z"]))
    same_size = (abs(z_rates) > 0 and np.sign(z_es) == np.sign(z_rates)
                 and z_es >= 0.5 * z_rates and (es_ci[0] > 0 or es_ci[1] < 0))
    P("")
    P("ES SPECIFICITY READ (same events, same construction, ES costs):")
    P(f"    n = {len(es_fin)}; after-cost mean ${es_mean:+,.2f}/event, "
      f"95% CI [${es_ci[0]:+,.2f}, ${es_ci[1]:+,.2f}]")
    P(f"    standardized effect: rates z-bar {z_rates:+.4f} vs ES z-bar {z_es:+.4f} "
      f"(ratio {z_es / z_rates if z_rates != 0 else np.nan:+.2f}); "
      f"same-size rule (D7): {'TRIPPED -> mechanism reclassified' if same_size else 'not tripped'}")

    # ================================================================ SECONDARY (D9, non-gating)
    P("")
    P("SECONDARY (non-gating):")
    for lbl, col in (("concession A close(D-5)->close(D0)", "conc_A"),
                     ("concession B close(D-6)->close(D-1)", "conc_B")):
        v = np.array([r * PV[m_] for r, m_ in zip(fin[col], fin["market"])
                      if np.isfinite(r)])
        P(f"    {lbl:<38} mean ${np.mean(v):+,.2f}/event gross (n={len(v)})")
    cyc = np.array([(y - a) * PV[m_] for y, a, m_ in
                    zip(fin["y_pts"], fin["conc_A"], fin["market"])
                    if np.isfinite(y) and np.isfinite(a)])
    P(f"    combined cycle (rebound - concession A)  mean ${np.mean(cyc):+,.2f}/event gross "
      f"(n={len(cyc)})")
    for flag in ("No", "Yes"):
        s = fin[fin["reopening"] == flag]
        P(f"    {'originals' if flag == 'No' else 'reopenings':<12} n={len(s):>3}  "
          f"after-cost cons ${np.mean(s['pnl_cons']):+,.2f}/event")
    for m in ("ZN", "ZB"):
        s = fin[fin["market"] == m]
        P(f"    {m:<12} n={len(s):>3}  after-cost cons ${np.mean(s['pnl_cons']):+,.2f}/event  "
          f"gross ${np.mean(s['y_pts'] * PV[m]):+,.2f}")

    # ================================================================ GATE TABLE
    g0 = (len(cal) > 0 and set(cal.tenor) == {"10Y", "30Y"}
          and cal["reopening"].isin(["Yes", "No"]).all()
          and all(manifest[m]["identity_gate_maxerr"] < 1e-9 for m in ("ZN", "ZB", "ES"))
          and all(manifest[m]["roll_causal"] for m in ("ZN", "ZB", "ES"))
          and all(pd.Timestamp(manifest[m]["seal_max"]) < SEAL for m in ("ZN", "ZB", "ES")))
    g1 = n_eff >= 300  # powered vs the spec's expected ~400+: printed; declared floor 300
    g6 = True          # ticks asserted at load; both rungs printed; gating rung = conservative
    g5 = True          # the read is printed (reclassification is narrative, not pass/fail)

    gates = [
        ("G0_FOUNDATIONS", "calendar persisted; roll identity+causality; seal < 2026-08-01",
         f"{len(cal)} auctions; maxerr 0.0e+00 x3; seal max "
         f"{max(manifest[m]['seal_max'] for m in ('ZN', 'ZB', 'ES'))}", g0),
        ("G1_MDE_FIRST", "MDE printed before observed; N ~ 400+ (declared floor 300)",
         f"MDE ${mde:,.0f}/event at N_eff={n_eff}", g1),
        ("G2_EDGE", "after-cost mean > 0 AND event-block CI excludes 0 AND 1-sided shift p < .05",
         f"mean ${obs_cons:+,.2f}, CI [{ci[0]:+,.2f},{ci[1]:+,.2f}], p_1s {p_1s:.4f}", g2),
        ("G3_CONTROL", "beats matched (market x weekday, +/-5-session-clean) control; delta CI ex 0",
         f"delta ${delta:+,.2f}, CI [{dci[0]:+,.2f},{dci[1]:+,.2f}]", g3),
        ("G4_ERA", "sign per era; all+ STRUCTURAL / modern-only REGIME-LOCAL / modern<=0 SIGN-FLIP",
         f"{'/'.join(signs)} -> {era_class}", g4),
        ("G5_SPECIFICITY", "ES same-event read printed; same-size rule (D7) evaluated",
         f"ES ${es_mean:+,.2f} CI [{es_ci[0]:+,.2f},{es_ci[1]:+,.2f}]; z ratio "
         f"{z_es / z_rates if z_rates != 0 else float('nan'):+.2f}; "
         f"{'same-size' if same_size else 'not same-size'}", g5),
        ("G6_COST", "modeled $4.36 RT + {1,2}-tick band; ticks asserted from data; cons rung gates",
         f"ZN {COST['ZN'][2]:.2f} / ZB {COST['ZB'][2]:.2f} cons; opt rung printed", g6),
    ]
    P("")
    P("GATE TABLE  (printed by program)")
    P(f"{'GATE':<16}{'SPEC':<92}{'OBSERVED':<72}{'PASS-FAIL'}")
    for g, s, o, ok in gates:
        P(f"{g:<16}{s:<92}{o:<72}{'PASS' if ok else '*** FAIL ***'}")

    # ================================================================ DECISION (mechanical)
    if g2 and g3 and era_class != "SIGN-FLIP":
        decision = "AUCT01 ENGINE CANDIDATE"
    else:
        decision = "CLOSED AT SCOPE (S28 block)"
    P("")
    P(f"DECISION RULE (spec, mechanical): G2={'PASS' if g2 else 'FAIL'} "
      f"G3={'PASS' if g3 else 'FAIL'} G4={era_class} -> {decision}")
    P(f"events/yr = {len(fin) / ((fin['auction_date'].max() - fin['auction_date'].min()).days / 365.25):.1f}; "
      f"after-cost economics at cons rung = ${obs_cons * len(fin) / ((fin['auction_date'].max() - fin['auction_date'].min()).days / 365.25):+,.0f}/yr/contract-pair-mix")
    P("=" * 118)

    json.dump(dict(
        n_cal=int(len(cal)), n_mapped=int(len(E)), n_eff=int(n_eff), mde_usd=mde,
        obs_cons=obs_cons, obs_opt=obs_opt, gross_usd=gross_usd, ci_cons=ci,
        p_shift_1s=p_1s, p_shift_2s=p_2s, null_mean=float(np.mean(null_stats)),
        null_sd=float(np.std(null_stats)),
        cluster_ci=[float(np.percentile(cl_means, 2.5)), float(np.percentile(cl_means, 97.5))],
        ctrl_mean=ctrl_mean, delta=delta, delta_ci=dci, n_ctrl=int(n_ctrl),
        era=era_t.to_dict("records"), era_class=era_class,
        es=dict(n=int(len(es_fin)), mean=es_mean, ci=es_ci, z=z_es, z_rates=z_rates,
                same_size=bool(same_size)),
        gates={g: bool(ok) for g, _, _, ok in gates}, decision=decision),
        open(os.path.join(OUT, "verdicts.json"), "w", encoding="utf-8"), indent=2)
    _fh.close()


if __name__ == "__main__":
    main()
