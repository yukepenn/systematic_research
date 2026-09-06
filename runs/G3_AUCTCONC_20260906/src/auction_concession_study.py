"""G3_AUCTCONC_20260906 -- the CONCESSION half of the auction cycle (G00080).

Spec: runs/G3_AUCTCONC_20260906/spec.yaml, committed a311e59 BEFORE results. This header
DECLARES every mechanical choice the spec leaves open, BEFORE any outcome is computed
(prereg discipline, mirroring G00073's D1-D10 where the spec says "same"):

FROZEN OBJECT: SHORT the matching future (ZN for 10y, ZB for 30y) at close(D-5); exit at
close(D0), the auction day. Events = the exact 414 mapped auctions in
runs/G3_AUCTCYCLE_20260906/out/event_study.csv AS-IS (sha printed). Series = the certified
causal-roll parquets in that run's out/, AS-IS (shas printed, manifest-checked). Outcome per
event = -conc_A x $1000/pt - cost, where conc_A = sum of ret_points over the 5 sessions
ending at the auction session (close(D-5)->close(D0), the SAME column G00073 wrote and whose
era split was deliberately never read; it is recomputed here from the parquets and asserted
identical, and additionally cross-checked as close[pos]-close[pos-5] on roll-free windows --
a different-way computation of what the number MEANS).

DECLARED MECHANICS (all fixed in advance of results):
  C1. GATING COST RUNG = CONSERVATIVE (commission $4.36 RT + 2 ticks): ZN $35.61, ZB $66.86
      per contract round trip, ASSERTED to the cent against the spec's G7 figures; 1-tick
      optimistic rung printed alongside. Tick $: ZN $15.625, ZB $31.25, ES $12.50 (asserted
      vs inputs_manifest tick sizes).
  C2. MIRROR DEBT (spec, provenance_honesty): the concession is 1 of exactly 2 preregistered
      halves -> EVERY null p is multiplied x2 (Bonferroni) before comparison to 0.05, and the
      G1 MDE alpha is halved (one-sided 2.5% -> multiplier z_.975+z_.80 = 2.8016). Bootstrap
      CIs stay at the mirror's 95% percentile convention (the spec applies the x2 debt to
      null p-values and the MDE alpha; it does not redefine the CI level).
  C3. NULL: 2000 circular shifts of the event-position mask, MIN_SHIFT 30, ONE shared
      uniform draw per iteration across ZN and ZB (dependence-preserving), fixed seed
      20260906 (G00073 D2 mirror). Direction preregistered = SHORT, so the raw p is
      one-sided P(null mean >= observed mean); the GATE compares 2 x p_1s to 0.05 (C2).
      The same shared draws evaluate BOTH renderings (pooled and portfolio).
      IN WORDS the null event is: "a random joint circular placement of the auction-day mask
      on the ZN/ZB session axes yields a mean after-cost concession-short at least as large
      as the observed one" -- computed over the same after-cost transform.
  C4. G2 CI: block bootstrap BY EVENT (resample events with replacement), 2000 draws,
      percentile 2.5/97.5. G2 clause = mean > 0 AND CI_lo > 0 AND 2 x p_1s < 0.05.
      Per spec G6, G2 GATES ON THE PORTFOLIO RENDERING; the pooled per-event figures are
      printed beside it (non-gating).
  C5. PORTFOLIO RENDERING (G6, deduplicated one-position-at-a-time): sort all 414 events by
      (entry_date, exit_date, market) where entry_date = session date at index pos-5 on the
      event's own market axis and exit_date = the mapped auction session date. Walk
      chronologically holding at most ONE contract: an event is TAKEN iff its outcome is
      finite AND pos >= 5 AND entry_date >= the standing exit_date (exiting and entering at
      the same close is allowed -- never two positions at once); otherwise it is SKIPPED
      with its reason recorded (BUSY / NO_OUTCOME). Selection uses DATES ONLY, no outcomes.
  C6. G3 CONTROL (G00073 D5 mirror, short side): eligible control session on market m =
      finite conc window AND no mapped 10y/30y auction (full 422-row calendar, both tenors,
      D3 mapping rule) within +/-5 TRADING sessions inclusive on that market's axis. Cells =
      (market x weekday of the window-END session). Control outcome = -cA x $1000 - cons
      cost. Control mean = event-composition-weighted over cells. Delta CI: 2000 draws
      resampling events (with per-draw cell weights) and control days within cells.
      G3 GATES ON THE POOLED PER-EVENT RENDERING (the direct mirror of G00073's G3 -- spec
      G6 reassigns only G2 to the portfolio); the portfolio-composition delta is printed as
      a declared non-gating annex. PASS = delta > 0 AND delta CI_lo > 0.
  C7. G4 ERAS by auction date AS-IS from the input CSV's era column (2009-15 / 2016-21 /
      2022-26/07, asserted against the date bounds). Sign of the POOLED after-cost cons
      short mean per era: all > 0 -> STRUCTURAL; modern (2022+) > 0 with any earlier era
      <= 0 -> REGIME-LOCAL (classification, not a veto); modern <= 0 -> MODERN-NEGATIVE ->
      G4 FAIL (spec: "the rebound's fate"). Portfolio per-era printed as annex.
  C8. G1 MDE printed BEFORE any observed event mean, for BOTH renderings (both Ns are
      known from dates alone): MDE = 2.8016 x sigma_pool / sqrt(N), sigma_pool from the
      UNCONDITIONAL backward-5-session-sum sd per market (in $, event-composition weighted).
      Uses no event outcome values. Declared power floor: pooled N_eff >= 300 (G00073
      mirror); the portfolio N carries no preregistered floor and is reported.
  C9. G5 ES read: the 414 event auction dates mapped to the ES axis (D3 rule); the SAME
      close(D-5)->close(D0) window; both the long-side gross drift (what ES does) and the
      after-cost SHORT rendering (what shorting alongside would cost) printed with
      event-bootstrap CIs and the standardized-size annex. Print-only gate.
  C10. G7 economics: events/yr for both renderings from the finite-event auction-date span;
      $/yr = mean x events/yr. Annex (declared, non-gating): per-market and
      originals/reopenings splits; cluster-by-month CI (G00073 D10 mirror).

SEAL: every parquet asserted max(date) < 2026-08-01; calendar asserted <= 2026-07-31.
Evidence status: DISCOVERY_CONSUMED (spec) -- the sample was consumed by G00073;
this is the second and last preregistered read of this family.
"""
from __future__ import annotations

import hashlib
import json
import os

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.dirname(HERE)
OUT = os.path.join(RUN, "out")
SRC_RUN = os.path.normpath(os.path.join(RUN, "..", "G3_AUCTCYCLE_20260906", "out"))
SEAL = pd.Timestamp("2026-08-01")
RNG = np.random.default_rng(20260906)

H = 5
EXCL = 5
N_SHIFT, MIN_SHIFT, N_BB = 2000, 30, 2000
COMMISSION = 4.36
PV = {"ZN": 1000.0, "ZB": 1000.0, "ES": 50.0}
TICK = {"ZN": 0.015625, "ZB": 0.03125, "ES": 0.25}
COST = {m: {1: COMMISSION + 1 * TICK[m] * PV[m], 2: COMMISSION + 2 * TICK[m] * PV[m]}
        for m in PV}
ERA_BOUNDS = {"2009-15": (pd.Timestamp("2009-01-01"), pd.Timestamp("2015-12-31")),
              "2016-21": (pd.Timestamp("2016-01-01"), pd.Timestamp("2021-12-31")),
              "2022-26/07": (pd.Timestamp("2022-01-01"), pd.Timestamp("2026-07-31"))}
ERA_ORDER = ["2009-15", "2016-21", "2022-26/07"]
MULT_MDE = 1.959964 + 0.841621          # C8: x2 debt on the alpha (one-sided 2.5%) + 80% power

_fh = open(os.path.join(OUT, "gate_table.txt"), "w", encoding="utf-8")


def P(*a):
    print(*a, flush=True)
    print(*a, file=_fh)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def map_events(cal_dates, sess_dates):
    """G00073 D3 mirror: exact match, else first session within <=3 calendar days after."""
    sd = pd.DatetimeIndex(sess_dates)
    pos = []
    for ad in cal_dates:
        i = sd.searchsorted(ad)
        if i < len(sd) and sd[i] == ad:
            pos.append(i)
        elif i < len(sd) and (sd[i] - ad).days <= 3:
            pos.append(i)
        else:
            pos.append(-1)
    return np.array(pos)


def main():
    # ================================================================ LOAD + SHA + SEAL
    files = {"event_study.csv": os.path.join(SRC_RUN, "event_study.csv"),
             "auction_calendar.csv": os.path.join(SRC_RUN, "auction_calendar.csv"),
             "zn_daily.parquet": os.path.join(SRC_RUN, "zn_daily.parquet"),
             "zb_daily.parquet": os.path.join(SRC_RUN, "zb_daily.parquet"),
             "es_daily.parquet": os.path.join(SRC_RUN, "es_daily.parquet")}
    shas = {k: sha256(v) for k, v in files.items()}
    manifest = json.load(open(os.path.join(SRC_RUN, "inputs_manifest.json"), encoding="utf-8"))
    for m in ("ZN", "ZB", "ES"):
        assert shas[f"{m.lower()}_daily.parquet"] == manifest[m]["parquet_sha256"], \
            f"parquet sha drifted vs certified manifest ({m})"

    E = pd.read_csv(files["event_study.csv"], parse_dates=["auction_date", "session_date"])
    cal = pd.read_csv(files["auction_calendar.csv"], parse_dates=["auction_date"])
    assert len(E) == 414, f"event table not 414 rows AS-IS: {len(E)}"
    assert len(cal) == 422, f"calendar not 422 rows AS-IS: {len(cal)}"
    assert bool(E["exact"].all()), "non-exact event mapping appeared; mirror broken"
    assert cal["auction_date"].max() <= pd.Timestamp("2026-07-31"), "calendar window violation"

    mkt = {}
    for m in ("ZN", "ZB", "ES"):
        df = pd.read_parquet(files[f"{m.lower()}_daily.parquet"])
        assert df["date"].max() < SEAL, f"SEAL VIOLATION ({m}): {df['date'].max()}"
        assert abs(manifest[m]["tick_size"] - TICK[m]) < 1e-12, f"tick mismatch {m}"
        r = df["ret_points"].where(df["clean_daily"]).values
        cA = pd.Series(r).rolling(H, min_periods=H).sum().values
        mkt[m] = dict(df=df, dates=pd.DatetimeIndex(df["date"]), r=r, cA=cA,
                      close=df["close"].values, rolled=df["rolled"].values,
                      sd5b=float(np.nanstd(cA)))
    assert abs(COST["ZN"][2] - 35.61) < 0.005 and abs(COST["ZB"][2] - 66.86) < 0.005, \
        "G7 cost rung drifted from spec figures"

    # integrity: recomputed cA == the CSV's conc_A (never era-read, but written by G00073)
    recomputed = np.array([mkt[r.market]["cA"][r.pos] for r in E.itertuples()])
    both = np.isfinite(recomputed) & np.isfinite(E["conc_A"].values)
    assert np.nanmax(np.abs(recomputed[both] - E["conc_A"].values[both])) < 1e-9, \
        "conc_A recompute mismatch vs AS-IS input"
    assert (np.isfinite(recomputed) == np.isfinite(E["conc_A"].values)).all()
    # different-way check of MEANING on roll-free clean windows: sum ret == close[p]-close[p-5]
    n_ck = n_ok = 0
    for r in E.itertuples():
        mm = mkt[r.market]
        p_ = r.pos
        if p_ >= 5 and np.isfinite(mm["cA"][p_]) and mm["rolled"][p_ - 4:p_ + 1].sum() == 0:
            n_ck += 1
            if abs(mm["cA"][p_] - (mm["close"][p_] - mm["close"][p_ - 5])) < 1e-9:
                n_ok += 1
    assert n_ck > 100 and n_ok == n_ck, f"close-diff meaning check failed: {n_ok}/{n_ck}"
    # session-date / weekday integrity
    for r in E.itertuples():
        assert mkt[r.market]["dates"][r.pos] == r.session_date, "pos/session_date drift"
    assert (pd.DatetimeIndex(E["session_date"]).weekday == E["weekday"].values).all()
    # era column AS-IS integrity vs declared bounds
    for r in E.itertuples():
        lo, hi = ERA_BOUNDS[r.era]
        assert lo <= r.auction_date <= hi, "era column inconsistent with bounds"

    # ================================================================ EVENT TABLE (short side)
    E["entry_pos"] = E["pos"] - H
    E["entry_date"] = pd.NaT
    ok_entry = E["entry_pos"] >= 0
    E.loc[ok_entry, "entry_date"] = [mkt[m]["dates"][p_] for m, p_ in
                                     zip(E.loc[ok_entry, "market"], E.loc[ok_entry, "entry_pos"])]
    E["short_pts"] = -E["conc_A"]
    E["pnl_short_cons"] = [(-a) * PV[m] - COST[m][2] if np.isfinite(a) else np.nan
                           for a, m in zip(E["conc_A"], E["market"])]
    E["pnl_short_opt"] = [(-a) * PV[m] - COST[m][1] if np.isfinite(a) else np.nan
                          for a, m in zip(E["conc_A"], E["market"])]
    fin = E[np.isfinite(E["pnl_short_cons"]) & (E["entry_pos"] >= 0)].reset_index(drop=True)
    n_eff = len(fin)

    P("=" * 118)
    P("=== G3_AUCTCONC_20260906 -- auction CONCESSION half: SHORT ZN/ZB close(D-5)->close(D0) "
      "(G00080, family GENESIS3_EVENT)")
    P("=" * 118)
    P("INPUT SHAS (AS-IS from runs/G3_AUCTCYCLE_20260906/out/):")
    for k, v in shas.items():
        P(f"    {k:<24} {v}")
    P(f"seal: ZN/ZB/ES max session "
      f"{max(str(mkt[m]['dates'].max().date()) for m in ('ZN', 'ZB', 'ES'))} < 2026-08-01 OK; "
      f"calendar max {cal['auction_date'].max().date()} <= 2026-07-31 OK")
    P(f"events: 414 AS-IS; finite concession-short outcome n_eff = {n_eff} "
      f"({414 - n_eff} dropped: window predates series start / masked session)")
    P(f"integrity: conc_A recompute max|err| < 1e-9 on {int(both.sum())} finite rows; "
      f"close-diff meaning check {n_ok}/{n_ck} roll-free windows exact; era bounds OK")
    P(f"costs/ct RT (C1): ZN opt ${COST['ZN'][1]:.2f} cons ${COST['ZN'][2]:.2f} | "
      f"ZB opt ${COST['ZB'][1]:.2f} cons ${COST['ZB'][2]:.2f} | "
      f"ES opt ${COST['ES'][1]:.2f} cons ${COST['ES'][2]:.2f}  (cons rung GATES, C1)")

    # ================================================================ G6: PORTFOLIO SELECTION
    # (C5 -- dates only, no outcomes)
    order = E.sort_values(["entry_date", "session_date", "market"],
                          na_position="last").reset_index(drop=True)
    taken_flags, reasons = [], []
    standing_exit = pd.Timestamp.min
    for r in order.itertuples():
        if not (np.isfinite(r.pnl_short_cons) and r.entry_pos >= 0):
            taken_flags.append(False); reasons.append("NO_OUTCOME")
        elif r.entry_date >= standing_exit:
            taken_flags.append(True); reasons.append("TAKEN")
            standing_exit = r.session_date
        else:
            taken_flags.append(False); reasons.append("BUSY")
    order["taken"] = taken_flags
    order["reason"] = reasons
    port = order[order["taken"]].reset_index(drop=True)
    n_take = len(port)
    order.to_csv(os.path.join(OUT, "portfolio_rendering.csv"), index=False)
    E.to_csv(os.path.join(OUT, "event_table.csv"), index=False)

    # overlap fractions (over events with a defined entry date)
    iv = order[order["entry_pos"] >= 0][["entry_date", "session_date", "market"]].values
    n_ov = n_ovx = 0
    for i in range(len(iv)):
        any_o = any_x = False
        for j in range(len(iv)):
            if i == j:
                continue
            if iv[i][0] <= iv[j][1] and iv[j][0] <= iv[i][1]:
                any_o = True
                if iv[i][2] != iv[j][2]:
                    any_x = True
        n_ov += any_o
        n_ovx += any_x
    frac_ov, frac_ovx = n_ov / len(iv), n_ovx / len(iv)
    P("")
    P("G6 OVERLAP HONESTY (C5): D-5..D0 windows across the two roots:")
    P(f"    overlap fraction (event overlaps ANY other event's window): "
      f"{frac_ov:.3f} ({n_ov}/{len(iv)}); cross-root only: {frac_ovx:.3f} ({n_ovx}/{len(iv)})")
    P(f"    deduplicated one-position-at-a-time portfolio: {n_take} taken / "
      f"{int((order['reason'] == 'BUSY').sum())} skipped-BUSY / "
      f"{int((order['reason'] == 'NO_OUTCOME').sum())} no-outcome  "
      f"(ZN {int((port['market'] == 'ZN').sum())}, ZB {int((port['market'] == 'ZB').sum())})")
    P("    the PORTFOLIO rendering carries the G2 gate (spec G6); pooled table printed beside")

    # ================================================================ G1: MDE FIRST (C8)
    w_pool = fin.groupby("market").size() / n_eff
    sd_pool = float(np.sqrt(sum(w_pool[m] * (mkt[m]["sd5b"] * PV[m]) ** 2 for m in w_pool.index)))
    mde_pool = MULT_MDE * sd_pool / np.sqrt(n_eff)
    w_take = port.groupby("market").size() / n_take
    sd_take = float(np.sqrt(sum(w_take[m] * (mkt[m]["sd5b"] * PV[m]) ** 2 for m in w_take.index)))
    mde_take = MULT_MDE * sd_take / np.sqrt(n_take)
    P("")
    P("G1 MDE (PRINTED BEFORE ANY OBSERVED EVENT MEAN; alpha one-sided 2.5% = 5%/2 mirror "
      "debt, 80% power; multiplier 2.802):")
    P(f"    POOLED     sigma_pool ${sd_pool:,.0f}/event "
      f"(ZN {w_pool.get('ZN', 0):.2f} / ZB {w_pool.get('ZB', 0):.2f}), N_eff {n_eff} "
      f"-> MDE ${mde_pool:,.0f}/event")
    P(f"    PORTFOLIO  sigma_pool ${sd_take:,.0f}/event "
      f"(ZN {w_take.get('ZN', 0):.2f} / ZB {w_take.get('ZB', 0):.2f}), N_taken {n_take} "
      f"-> MDE ${mde_take:,.0f}/event")
    g1 = n_eff >= 300

    # ================================================================ OBSERVED (both renderings)
    obs = {}
    for lbl, tab in (("POOLED", fin), ("PORTFOLIO", port)):
        pnl = tab["pnl_short_cons"].values
        idx = RNG.integers(0, len(tab), size=(N_BB, len(tab)))
        bb = pnl[idx].mean(axis=1)
        obs[lbl] = dict(
            tab=tab, n=len(tab), idx=idx,
            mean=float(np.mean(pnl)), mean_opt=float(np.mean(tab["pnl_short_opt"])),
            gross=float(np.mean(tab["short_pts"].values *
                                np.array([PV[m] for m in tab["market"]]))),
            ci=(float(np.percentile(bb, 2.5)), float(np.percentile(bb, 97.5))))

    # shared-draw circular-shift null (C3) -- same u draws evaluate both renderings
    u = RNG.random(N_SHIFT)
    Lm = {m: len(mkt[m]["df"]) for m in ("ZN", "ZB")}
    yshort = {m: -mkt[m]["cA"] * PV[m] - COST[m][2] for m in ("ZN", "ZB")}
    for lbl in ("POOLED", "PORTFOLIO"):
        tab = obs[lbl]["tab"]
        posm = {m: tab[tab["market"] == m]["pos"].values for m in ("ZN", "ZB")}
        ns = np.empty(N_SHIFT)
        for k in range(N_SHIFT):
            vals = []
            for m in ("ZN", "ZB"):
                off = MIN_SHIFT + int(np.floor(u[k] * (Lm[m] - 2 * MIN_SHIFT)))
                vals.append(yshort[m][(posm[m] + off) % Lm[m]])
            ns[k] = np.nanmean(np.concatenate(vals))
        p1 = float((np.sum(ns >= obs[lbl]["mean"]) + 1) / (N_SHIFT + 1))
        obs[lbl].update(null_mean=float(np.mean(ns)), null_sd=float(np.std(ns)),
                        p_1s=p1, p_gate=float(min(1.0, 2.0 * p1)))

    P("")
    P("OBSERVED (SHORT close(D-5)->close(D0), per contract, after cost, cons rung):")
    P("    null event IN WORDS (C3): P(random joint circular placement of the auction mask on "
      "the ZN/ZB axes gives a mean")
    P("    after-cost concession-short >= observed); GATE compares 2 x p_1s to 0.05 "
      "(mirror debt).")
    for lbl in ("POOLED", "PORTFOLIO"):
        o = obs[lbl]
        gate_tag = "[GATING, C4]" if lbl == "PORTFOLIO" else "[printed beside, non-gating]"
        P(f"    {lbl:<10} n={o['n']:>3}  gross ${o['gross']:+,.2f}  cons ${o['mean']:+,.2f}  "
          f"opt ${o['mean_opt']:+,.2f}  CI95 [${o['ci'][0]:+,.2f}, ${o['ci'][1]:+,.2f}]  "
          f"{gate_tag}")
        P(f"    {'':<10} null mean ${o['null_mean']:+,.2f} sd ${o['null_sd']:,.2f}; "
          f"p_1s {o['p_1s']:.4f} -> p x2 = {o['p_gate']:.4f}")
    op = obs["PORTFOLIO"]
    g2 = (op["mean"] > 0) and (op["ci"][0] > 0) and (op["p_gate"] < 0.05)

    # ================================================================ G3: MATCHED CONTROL (C6)
    ctrl = {}
    for m in ("ZN", "ZB"):
        excl = np.zeros(Lm[m], dtype=bool)
        allpos = map_events(cal["auction_date"].values, mkt[m]["dates"])
        for p_ in allpos[allpos >= 0]:
            excl[max(0, p_ - EXCL):p_ + EXCL + 1] = True
        okd = np.isfinite(mkt[m]["cA"]) & ~excl
        okd[:H] = False                       # entry close must exist on the axis (C5 mirror)
        wd = mkt[m]["dates"].weekday
        for wday in range(5):
            sel = np.where(okd & (wd == wday))[0]
            ctrl[(m, wday)] = -mkt[m]["cA"][sel] * PV[m] - COST[m][2]
    n_ctrl = sum(len(v) for v in ctrl.values())

    deltas = {}
    for lbl in ("POOLED", "PORTFOLIO"):
        tab, idx = obs[lbl]["tab"], obs[lbl]["idx"]
        cellw = tab.groupby(["market", "weekday"]).size() / len(tab)
        cmean = float(sum(cellw[c] * np.mean(ctrl[c]) for c in cellw.index))
        dl = obs[lbl]["mean"] - cmean
        db = np.empty(N_BB)
        for k in range(N_BB):
            samp = tab.iloc[idx[k]]
            em = float(np.mean(samp["pnl_short_cons"]))
            cw = samp.groupby(["market", "weekday"]).size() / len(tab)
            cm = 0.0
            for c, wgt in cw.items():
                arr = ctrl[c]
                cm += wgt * float(np.mean(arr[RNG.integers(0, len(arr), len(arr))]))
            db[k] = em - cm
        deltas[lbl] = dict(ctrl_mean=cmean, delta=dl,
                           ci=(float(np.percentile(db, 2.5)), float(np.percentile(db, 97.5))))
    dp = deltas["POOLED"]
    g3 = (dp["delta"] > 0) and (dp["ci"][0] > 0)

    P("")
    P("G3 MATCHED CONTROL (market x weekday of window-end, no auction within +/-5 sessions, "
      "same backward window, SHORT side, cons cost):")
    P(f"    control days: {n_ctrl:,} across {len(ctrl)} cells")
    P(f"    POOLED     ctrl ${dp['ctrl_mean']:+,.2f}  DELTA ${dp['delta']:+,.2f}  "
      f"CI95 [${dp['ci'][0]:+,.2f}, ${dp['ci'][1]:+,.2f}]   [GATING, C6]")
    dq = deltas["PORTFOLIO"]
    P(f"    PORTFOLIO  ctrl ${dq['ctrl_mean']:+,.2f}  DELTA ${dq['delta']:+,.2f}  "
      f"CI95 [${dq['ci'][0]:+,.2f}, ${dq['ci'][1]:+,.2f}]   [annex, non-gating]")

    # ================================================================ G4: ERAS (C7)
    era_rows = []
    for name in ERA_ORDER:
        s = fin[fin["era"] == name]
        sp = port[port["era"] == name]
        cw = s.groupby(["market", "weekday"]).size() / max(len(s), 1)
        cm = float(sum(cw[c] * np.mean(ctrl[c]) for c in cw.index)) if len(s) else np.nan
        mu = float(np.mean(s["pnl_short_cons"]))
        era_rows.append(dict(
            era=name, n=len(s),
            gross_usd=float(np.mean(s["short_pts"].values *
                                    np.array([PV[m] for m in s["market"]]))),
            after_cost_cons=mu, ctrl_matched=cm, delta=mu - cm,
            sign="+" if mu > 0 else "-",
            n_portfolio=len(sp),
            portfolio_after_cost=float(np.mean(sp["pnl_short_cons"])) if len(sp) else np.nan))
    era_t = pd.DataFrame(era_rows)
    era_t.to_csv(os.path.join(OUT, "era_table.csv"), index=False)
    signs = era_t["sign"].tolist()
    if all(s == "+" for s in signs):
        era_class = "STRUCTURAL"
    elif signs[2] == "+":
        era_class = "REGIME-LOCAL"
    else:
        era_class = "MODERN-NEGATIVE"
    g4 = era_class != "MODERN-NEGATIVE"

    P("")
    P("G4 ERA TABLE (pooled after-cost CONS short GATES the sign rule, C7; portfolio annex "
      "beside; FIRST EVER read of this split):")
    P(f"    {'era':<12}{'n':>5}  {'gross$':>10} {'aftercost$':>11} {'ctrl$':>9} {'delta$':>9} "
      f"sign  {'nPort':>6} {'port$':>10}")
    for r in era_t.itertuples():
        P(f"    {r.era:<12}{r.n:>5}  {r.gross_usd:>+10.2f} {r.after_cost_cons:>+11.2f} "
          f"{r.ctrl_matched:>+9.2f} {r.delta:>+9.2f}   {r.sign}   {r.n_portfolio:>6} "
          f"{r.portfolio_after_cost:>+10.2f}")
    P(f"    ERA CLASSIFICATION: {era_class}")

    # ================================================================ G5: ES SAME-WINDOW (C9)
    es_pos = map_events(E["auction_date"].values, mkt["ES"]["dates"])
    es_cA = np.array([mkt["ES"]["cA"][p_] if p_ >= H else np.nan for p_ in es_pos])
    es_fin = es_cA[np.isfinite(es_cA)]
    es_long_gross = es_fin * PV["ES"]
    es_short = -es_fin * PV["ES"] - COST["ES"][2]
    idx_es = RNG.integers(0, len(es_fin), size=(N_BB, len(es_fin)))
    ci_l = (float(np.percentile(es_long_gross[idx_es].mean(axis=1), 2.5)),
            float(np.percentile(es_long_gross[idx_es].mean(axis=1), 97.5)))
    ci_s = (float(np.percentile(es_short[idx_es].mean(axis=1), 2.5)),
            float(np.percentile(es_short[idx_es].mean(axis=1), 97.5)))
    sd5b_es = mkt["ES"]["sd5b"]
    z_es = float(np.mean(-es_fin / sd5b_es))
    z_rates = float(np.mean(np.array([s / mkt[m]["sd5b"] for s, m in
                                      zip(fin["short_pts"], fin["market"])])))
    P("")
    P("G5 ES SAME-WINDOW READ (C9; 414 auction dates on the ES axis, close(D-5)->close(D0)):")
    P(f"    n = {len(es_fin)}; ES LONG gross drift ${np.mean(es_long_gross):+,.2f}/event "
      f"CI95 [${ci_l[0]:+,.2f}, ${ci_l[1]:+,.2f}]")
    P(f"    ES SHORT after-cost           ${np.mean(es_short):+,.2f}/event "
      f"CI95 [${ci_s[0]:+,.2f}, ${ci_s[1]:+,.2f}]")
    P(f"    standardized SHORT-side effect: rates z-bar {z_rates:+.4f} vs ES z-bar {z_es:+.4f}"
      f" (ratio {z_es / z_rates if z_rates != 0 else float('nan'):+.2f})")
    g5 = True

    # ================================================================ G7: ECONOMICS (C10)
    yrs = (fin["auction_date"].max() - fin["auction_date"].min()).days / 365.25
    per_yr_pool, per_yr_take = n_eff / yrs, n_take / yrs
    ann_pool = obs["POOLED"]["mean"] * per_yr_pool
    ann_take = op["mean"] * per_yr_take
    P("")
    P("G7 ECONOMICS (cons rung):")
    P(f"    POOLED     {per_yr_pool:.1f} events/yr x ${obs['POOLED']['mean']:+,.2f} = "
      f"${ann_pool:+,.0f}/yr/contract (double-counts overlapping weeks)")
    P(f"    PORTFOLIO  {per_yr_take:.1f} trades/yr x ${op['mean']:+,.2f} = "
      f"${ann_take:+,.0f}/yr/contract (economically honest rendering)")
    # declared annexes (C10)
    ymg = [g["pnl_short_cons"].values for _, g in fin.groupby("ym")]
    cl_idx = RNG.integers(0, len(ymg), size=(N_BB, len(ymg)))
    cl_means = np.array([np.concatenate([ymg[j] for j in row]).mean() for row in cl_idx])
    P(f"    ANNEX cluster-by-month CI95 (pooled): [${np.percentile(cl_means, 2.5):+,.2f}, "
      f"${np.percentile(cl_means, 97.5):+,.2f}] ({len(ymg)} clusters)")
    for m in ("ZN", "ZB"):
        s = fin[fin["market"] == m]
        P(f"    ANNEX {m}: n={len(s)}  gross ${np.mean(s['short_pts']) * PV[m]:+,.2f}  "
          f"cons ${np.mean(s['pnl_short_cons']):+,.2f}")
    for flag, nm in (("No", "originals"), ("Yes", "reopenings")):
        s = fin[fin["reopening"] == flag]
        P(f"    ANNEX {nm}: n={len(s)}  cons ${np.mean(s['pnl_short_cons']):+,.2f}")
    g7 = True
    g6 = True   # overlap fraction + portfolio rendering + pooled table all printed/persisted
    g0_shas = True  # shas printed and matched the certified manifest (asserted above)

    # ================================================================ GATE TABLE
    gates = [
        ("G1_MDE_FIRST", "MDE printed before observed; x2 debt on alpha; pooled floor 300",
         f"pooled MDE ${mde_pool:,.0f} @N={n_eff}; portfolio MDE ${mde_take:,.0f} @N={n_take}",
         g1),
        ("G2_EDGE(PORT)", "PORTFOLIO after-cost cons mean>0 AND event-CI ex 0 AND 2xp_shift<.05",
         f"mean ${op['mean']:+,.2f}, CI [{op['ci'][0]:+,.2f},{op['ci'][1]:+,.2f}], "
         f"px2 {op['p_gate']:.4f}", g2),
        ("G3_CONTROL", "beats matched mkt x weekday non-auction control (short); delta CI ex 0",
         f"delta ${dp['delta']:+,.2f}, CI [{dp['ci'][0]:+,.2f},{dp['ci'][1]:+,.2f}]", g3),
        ("G4_ERA", "signs 2009-15/2016-21/2022-26; all+ STRUCT / modern-only RL / modern<=0 FAIL",
         f"{'/'.join(signs)} -> {era_class}", g4),
        ("G5_SPECIFICITY", "ES same-window read printed (short side fights equity beta?)",
         f"ES long gross ${np.mean(es_long_gross):+,.2f}; short cons ${np.mean(es_short):+,.2f} "
         f"CI [{ci_s[0]:+,.2f},{ci_s[1]:+,.2f}]", g5),
        ("G6_OVERLAP", "overlap fraction + dedup one-position portfolio printed; carries G2",
         f"overlap {frac_ov:.3f} (cross-root {frac_ovx:.3f}); {n_take} taken of {len(iv)}", g6),
        ("G7_COST", "ZN $35.61 / ZB $66.86 cons rung asserted; events/yr economics printed",
         f"rungs asserted; {per_yr_pool:.1f} ev/yr pooled, {per_yr_take:.1f} trades/yr port",
         g7),
    ]
    P("")
    P("GATE TABLE  (printed by program)")
    P(f"{'GATE':<16}{'SPEC':<80}{'OBSERVED':<78}{'PASS-FAIL'}")
    for g, s, o, ok in gates:
        P(f"{g:<16}{s:<80}{o:<78}{'PASS' if ok else '*** FAIL ***'}")

    # ================================================================ DECISION (mechanical)
    if g2 and g3 and g4:
        decision = "AUCTCONC01 ENGINE CANDIDATE"
    else:
        decision = ("CLOSED -- auction-cycle family FULLY closed (both halves) "
                    "-> FAILURE_MEMORY")
    P("")
    P(f"DECISION RULE (spec, mechanical): G2(portfolio)={'PASS' if g2 else 'FAIL'} "
      f"G3={'PASS' if g3 else 'FAIL'} G4={era_class} -> {decision}")
    P("=" * 118)

    json.dump(dict(
        input_shas=shas, n_events=414, n_eff=int(n_eff), n_taken=int(n_take),
        overlap_frac=frac_ov, overlap_frac_cross=frac_ovx,
        mde_pooled=mde_pool, mde_portfolio=mde_take,
        pooled=dict(mean=obs["POOLED"]["mean"], opt=obs["POOLED"]["mean_opt"],
                    gross=obs["POOLED"]["gross"], ci=obs["POOLED"]["ci"],
                    p_1s=obs["POOLED"]["p_1s"], p_gate=obs["POOLED"]["p_gate"],
                    null_mean=obs["POOLED"]["null_mean"], null_sd=obs["POOLED"]["null_sd"]),
        portfolio=dict(mean=op["mean"], opt=op["mean_opt"], gross=op["gross"], ci=op["ci"],
                       p_1s=op["p_1s"], p_gate=op["p_gate"],
                       null_mean=op["null_mean"], null_sd=op["null_sd"]),
        control=dict(n_ctrl=int(n_ctrl), pooled=dp, portfolio=dq),
        era=era_t.to_dict("records"), era_class=era_class,
        es=dict(n=int(len(es_fin)), long_gross=float(np.mean(es_long_gross)), ci_long=ci_l,
                short_cons=float(np.mean(es_short)), ci_short=ci_s,
                z_es=z_es, z_rates=z_rates),
        economics=dict(events_yr_pooled=per_yr_pool, trades_yr_portfolio=per_yr_take,
                       ann_pooled=ann_pool, ann_portfolio=ann_take),
        gates={g: bool(ok) for g, _, _, ok in gates}, decision=decision),
        open(os.path.join(OUT, "verdicts.json"), "w", encoding="utf-8"), indent=2)
    _fh.close()


if __name__ == "__main__":
    main()
