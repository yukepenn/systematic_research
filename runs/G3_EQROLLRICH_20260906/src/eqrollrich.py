"""G3_EQROLLRICH_20260906 -- Equity roll-cycle financing richness (Hazelkorn-Moskowitz-Vasudevan
JF 2023) on ES (primary) + NQ (mechanism mirror). Ledger G00088, family GENESIS3_RV.

Spec: runs/G3_EQROLLRICH_20260906/spec.yaml (committed before results). DISCOVERY.
Per-contract dailies read directly from the NT8 day store via the certified reader
research/multi_market/src/ncd_day.py (per-contract, NON-continuous work -- no roll splice is
built and no cross-contract return is ever booked; the object is a same-date calendar spread).

================================ FROZEN CONVENTIONS (D1-D14) =====================================
Written and fixed BEFORE any result was computed. Spec ambiguities are resolved here, not after.

D1  FN ANCHOR (the spec requires this documented by the program and fixed before results).
    ES/NQ quarterly futures cash-settle to the SOQ on the THIRD FRIDAY of Mar/Jun/Sep/Dec
    (= expiry E). Equity index futures have NO first-notice mechanism (cash-settled); the event
    anchor the spec calls "FN" is the CME QUARTERLY EQUITY ROLL DATE convention:
        FN := E - 8 calendar days  (the THURSDAY of the week preceding expiration week),
    the CME-documented peak of the equity quarterly roll ("roll week": the majority of open
    interest transfers on the Thursday/Friday eight days before expiration; CME Equity Quarterly
    Roll analytics anchor on that Thursday). Assert FN is a Thursday. FN maps to the LAST front-
    contract session with date <= FN (holiday-safe); the mapped session is slot 0.
D2  RICHNESS ORIENTATION. R_t := back_close_t - front_close_t, in POINTS, same date, same root.
    Futures-implied financing over [T1,T2]: F_back/F_front ~ 1 + (r_implied - div)(T2-T1), so a
    RICHER implied financing = LARGER back-minus-front = dR_t > 0 ("richening").
    DIVIDEND CONFOUND BOUND (spec): the LEVEL of R embeds expected dividends between the two
    expiries -> NO level claims anywhere. Only within-cycle day-to-day CHANGES dR_t = R_t -
    R_{t-1} of a FIXED contract pair are used; the dividend level differences out and only
    (slow) dividend-expectation revisions remain as residual confound. Stated, not removable.
D3  EVENT TIME = TRADING SESSIONS on the FRONT contract's session grid (the liquid leg defines
    the calendar; repo convention, cf. AUCTCYCLE's trading-session windows). Slot 0 = FN session;
    slot -k = k-th front session before it. R is computed on slots -13..-1; daily changes
    dR(s) = R(s) - R(s-1) live on slots -12..-1 (12 changes).
    EARLY window = slots [-12,-6] (7 changes); LATE window = slots [-5,-1] (5 changes). FN itself
    (slot 0) is in neither window (spec windows end at FN-1).
    CYCLE SHAPE STATISTIC (PRIMARY, frozen in spec) := mean(dR over EARLY) - mean(dR over LATE),
    points/day. Richen-then-cheapen -> positive.
D4  PAIR FIXED PER CYCLE: front = the quarterly contract expiring that cycle month; back = the
    next quarterly contract. Never re-designated inside the window. Contract identity = the full
    NT8 id ("ES 09-13"), never the display symbol.
D5  COVERAGE RULE (availability rule; the store probe showed back-month bars often BEGIN only
    ~5-7 sessions before expiry in later years -- a data-availability fact, recorded not patched).
    A change dR(s) is VALID iff back closes (>0) exist on the slot-s and slot-(s-1) session dates.
    A cycle is INCLUDED iff >=5 of 7 EARLY changes valid AND >=4 of 5 LATE changes valid AND the
    front grid reaches slot -13. Exclusions printed with reasons. Spec anticipated ~68 cycles;
    the availability-driven sample will be smaller and is printed (G0c).
D6  DATA HYGIENE: closes used as-is (settlement-based day store); rows with close<=0 dropped; NO
    winsorization/trimming (top-|dR| outliers printed as diagnostics). Zero-volume back rows are
    settle-only prints: retained, prevalence printed (they are committee/algorithm settles, a
    stated limitation). STALENESS DIAGNOSTIC (non-gating, declared now): fraction of used changes
    with back close exactly unchanged while |front change| >= 1 tick; plus the front-drift mirror
    (corr of cycle shape stat with the same stat computed on FRONT closes alone) -- if the spread
    shape were a stale-back artifact it would mirror -(front drift shape).
D7  G2 NULL (cycle-level permutation, dependence-preserving): within each included cycle take the
    vector of its VALID changes in slot order and the fixed early/late label vector of the same
    slots; a draw applies an INDEPENDENT uniform circular rotation of the value vector against
    the fixed labels in each cycle (cycles are non-overlapping calendar quarters ~ independent
    units; rotation preserves within-cycle ordering/autocorrelation). Draw statistic = cross-
    cycle mean of the rotated shape stat. 20,000 draws, seed 20260906.
    p_perm (one-sided, preregistered direction) = (1 + #{draw >= observed}) / (1 + 20000).
D8  G1 MDE FIRST: one-sided 5%, 80% power: MDE = (1.6449+0.8416) * sd(cycle stats)/sqrt(N),
    printed BEFORE the observed mean, with the spec-mandated words "POWER IS THIN".
D9  G3 MECHANISM GATE: Pearson corr of MATCHED daily changes (same cycle, same slot, both roots'
    change valid) pooled over cycles INCLUDED FOR BOTH roots, slots -12..-1. Gate: corr > 0
    (spec wording; magnitude printed with n and a naive 95% CI). Annex (printed, non-gating):
    Spearman; cycle-level corr of the two roots' shape stats; pooled corr over ALL matched slots
    regardless of inclusion.
D10 G4 ERA (post-2016 stability MANDATED): eras by expiry year 2009-15 / 2016-21 / 2022-26/07
    (repo convention). G4 PASS iff the ES era-mean shape stat > 0 in BOTH 2016-21 AND 2022-26/07
    with n >= 5 cycles in each; an era too thin to demonstrate stability cannot pass it.
D11 G5 COST (diagnostic only -- spec: licenses a signal-lead, not a trade; never gates the
    decision): printed with BASIS and EVIDENCE tags per research/operational/COST_MODEL.md.
D12 SEAL: every read hard-filtered to date < 2026-08-01 and asserted (>= 2026-08-01 is VIRGIN).
    Only cycles whose full window sits before the seal can be included (guaranteed by D5 since
    sealed sessions are absent). Expiries considered: 2009-03 .. 2026-06 (70 candidate cycles).
D13 G6 P-MEANING (campaign doctrine, added to the spec's five gates; the decision rule is
    UNCHANGED = G2+G3+G4): one gate states IN WORDS what event the headline probability is over,
    and a SECOND computation of the same event runs a different way (cycle-level sign-flip null,
    20,000 draws, same seed, + one-sample t). PASS iff both are computed and qualitatively agree
    ((p_perm<0.05) == (p_signflip<0.05)); disagreement is recorded as FAIL and flagged.
D14 DECISION RULE (mechanical, frozen in spec): G2 AND G3 AND G4 PASS -> EQROLLRICH01 signal-lead
    (CONDITIONER lead; separate predictive falsifier would follow). ELSE closed at scope (S28).
    NQ's own shape stat is an annex and NEVER rescues or vetoes the ES primary.
==================================================================================================
Writes ONLY inside runs/G3_EQROLLRICH_20260906/.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(RUN))
sys.path.insert(0, os.path.join(ROOT, "research", "multi_market", "src"))
import ncd_day as N  # noqa: E402

OUT = os.path.join(RUN, "out")
os.makedirs(OUT, exist_ok=True)
SEAL = pd.Timestamp("2026-08-01")
SEED = 20260906
NDRAWS = 20000
EXPIRIES = [(y, m) for y in range(2009, 2027) for m in (3, 6, 9, 12)
            if (y, m) <= (2026, 6)]                      # 2009-03 .. 2026-06 = 70 candidates
EARLY = list(range(-12, -5))                             # slots -12..-6  (7 changes)
LATE = list(range(-5, 0))                                # slots -5..-1   (5 changes)
Z95_1S, Z80 = 1.6449, 0.8416

_fh = open(os.path.join(OUT, "gate_table.txt"), "w", encoding="utf-8")
_lg = open(os.path.join(OUT, "run_log.txt"), "w", encoding="utf-8")


def P(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    print(s, file=_fh)
    print(s, file=_lg)


def third_friday(y: int, m: int) -> dt.date:
    d = dt.date(y, m, 15)
    while d.weekday() != 4:
        d += dt.timedelta(days=1)
    return d


_CACHE: dict[str, pd.DataFrame] = {}


def contract(cid: str) -> pd.DataFrame:
    """Per-contract daily rows, seal-filtered, close>0 only. Never merged across contracts."""
    if cid not in _CACHE:
        x = N.read_contract(cid)
        if len(x):
            x = x[(x["date"] < SEAL) & (x["close"] > 0)].reset_index(drop=True)
            assert len(x) == 0 or x["date"].max() < SEAL, "SEAL VIOLATION"
        _CACHE[cid] = x
    return _CACHE[cid]


def build_cycles(root: str):
    """Per-cycle event-time spread paths. Returns (cycle_rows, path_rows, excl_rows)."""
    cycles, paths, excl = [], [], []
    for (y, m) in EXPIRIES:
        cyc = f"{y}-{m:02d}"
        exp = third_friday(y, m)
        fn_cal = exp - dt.timedelta(days=8)
        assert fn_cal.weekday() == 3, f"FN {fn_cal} is not a Thursday"
        fid = N.contract_id(root, m, y)
        bm, by = (m + 3, y) if m < 12 else (3, y + 1)
        bid = N.contract_id(root, bm, by)
        f, b = contract(fid), contract(bid)
        if len(f) == 0:
            excl.append(dict(root=root, cycle=cyc, reason="NO_FRONT_DATA"))
            continue
        fdates = f["date"].sort_values().reset_index(drop=True)
        grid = fdates[fdates <= pd.Timestamp(fn_cal)]
        if len(grid) == 0:
            excl.append(dict(root=root, cycle=cyc, reason="NO_FRONT_SESSION_<=FN"))
            continue
        fn_sess = grid.iloc[-1]
        pre = fdates[fdates < fn_sess].tolist()
        if len(pre) < 13:
            excl.append(dict(root=root, cycle=cyc,
                             reason=f"FRONT_GRID_SHORT({len(pre)}<13)"))
            continue
        slots = {s: pre[len(pre) + s] for s in range(-13, 0)}     # slot -1 = last pre-FN session
        fc = f.set_index("date")["close"]
        bc = b.set_index("date")["close"] if len(b) else pd.Series(dtype=float)
        bv = b.set_index("date")["volume"] if len(b) else pd.Series(dtype=float)
        R, FC, BV = {}, {}, {}
        for s in range(-13, 0):
            d0 = slots[s]
            FC[s] = float(fc.get(d0, np.nan))
            back = float(bc.get(d0, np.nan))
            R[s] = back - FC[s] if np.isfinite(back) and np.isfinite(FC[s]) else np.nan
            BV[s] = float(bv.get(d0, np.nan))
        dR = {s: (R[s] - R[s - 1]) for s in range(-12, 0)}
        dF = {s: (FC[s] - FC[s - 1]) for s in range(-12, 0)}
        n_early = sum(np.isfinite(dR[s]) for s in EARLY)
        n_late = sum(np.isfinite(dR[s]) for s in LATE)
        included = (n_early >= 5) and (n_late >= 4)
        if not included:
            excl.append(dict(root=root, cycle=cyc,
                             reason=f"BACK_COVERAGE(early {n_early}/7, late {n_late}/5)"))
        shape = np.nan
        front_shape = np.nan
        if included:
            e = [dR[s] for s in EARLY if np.isfinite(dR[s])]
            l = [dR[s] for s in LATE if np.isfinite(dR[s])]
            shape = float(np.mean(e) - np.mean(l))
            ef = [dF[s] for s in EARLY if np.isfinite(dR[s])]
            lf = [dF[s] for s in LATE if np.isfinite(dR[s])]
            front_shape = float(np.mean(ef) - np.mean(lf))
        cycles.append(dict(root=root, cycle=cyc, year=y, expiry=str(exp), fn_cal=str(fn_cal),
                           fn_session=str(pd.Timestamp(fn_sess).date()), front=fid, back=bid,
                           n_early=n_early, n_late=n_late, included=included,
                           shape_pts=shape, front_shape_pts=front_shape))
        for s in range(-13, 0):
            paths.append(dict(root=root, cycle=cyc, slot=s,
                              date=str(pd.Timestamp(slots[s]).date()),
                              front=fid, back=bid, front_close=FC[s],
                              back_volume=BV[s], R_pts=R[s],
                              dR_pts=dR.get(s, np.nan),
                              in_early=s in EARLY, in_late=s in LATE,
                              valid_change=bool(np.isfinite(dR.get(s, np.nan))),
                              included_cycle=included))
    return pd.DataFrame(cycles), pd.DataFrame(paths), pd.DataFrame(excl)


def rotation_stats(dr_by_cycle):
    """For each cycle: array of the shape stat under every circular rotation of its valid
    changes against the fixed early/late labels. Element 0 = observed."""
    per_cycle = []
    for vals, labels in dr_by_cycle:
        L = len(vals)
        stats = np.empty(L)
        for k in range(L):
            v = np.roll(vals, k)
            stats[k] = v[labels].mean() - v[~labels].mean()
        per_cycle.append(stats)
    return per_cycle


def main():
    P("=" * 118)
    P("=== G3_EQROLLRICH_20260906 -- equity roll-cycle financing richness (HMV JF 2023) on ES + NQ"
      "   (G00088, GENESIS3_RV)")
    P("=" * 118)
    P("")
    P("FROZEN CONVENTIONS D1-D14 (full text in src/eqrollrich.py header, written before results):")
    P("  D1 FN ANCHOR = CME quarterly equity roll convention: FN := expiry(3rd Friday) - 8 calendar")
    P("     days = the THURSDAY preceding expiration week (peak of the CME-documented roll week);")
    P("     asserted Thursday; mapped to last front session <= FN. Equity futures are cash-settled")
    P("     (no true first notice); 'FN' is this roll-date anchor. FIXED BEFORE RESULTS.")
    P("  D2 R = back - front close (points), same date; dR>0 = financing RICHENING. CHANGES only;")
    P("     dividend LEVEL differences out (no level claims; dividend-expectation revisions remain).")
    P("  D3 event time = front-contract trading sessions; EARLY=[FN-12,FN-6] (7 changes),")
    P("     LATE=[FN-5,FN-1] (5 changes); shape = mean(dR early) - mean(dR late), points/day.")
    P("  D5 include cycle iff early>=5/7 and late>=4/5 valid changes and front grid >=13 pre-FN.")
    P("  D7 G2 null = per-cycle independent circular rotation of valid changes vs fixed labels,")
    P(f"     {NDRAWS} draws, seed {SEED}, one-sided.")
    P("  D10 G4 = ES era-mean shape > 0 in BOTH 2016-21 and 2022-26/07 (n>=5 each).")
    P("  D13 G6 P-meaning gate added per campaign doctrine; decision rule unchanged (G2+G3+G4).")
    P("")

    # ---------------------------------------------------------------- build
    es_cyc, es_paths, es_excl = build_cycles("ES")
    nq_cyc, nq_paths, nq_excl = build_cycles("NQ")
    all_paths = pd.concat([es_paths, nq_paths], ignore_index=True)
    all_paths.to_csv(os.path.join(OUT, "cycle_paths.csv"), index=False)
    all_cyc = pd.concat([es_cyc, nq_cyc], ignore_index=True)
    all_cyc.to_csv(os.path.join(OUT, "cycle_stats.csv"), index=False)
    pd.concat([es_excl, nq_excl], ignore_index=True).to_csv(
        os.path.join(OUT, "exclusions.csv"), index=False)

    max_read = max(x["date"].max() for x in _CACHE.values() if len(x))
    P("--- DATA / SEAL")
    P(f"    per-contract day store via certified ncd_day.py; contracts touched: "
      f"{sum(1 for x in _CACHE.values() if len(x))} with data / {len(_CACHE)} requested")
    P(f"    SEAL: every read filtered < {SEAL.date()}; max session retained = "
      f"{max_read.date()}  assert PASS")
    ticks = {r: set(x['tick_size'].iloc[0] for c, x in _CACHE.items()
                    if len(x) and c.startswith(r + ' ')) for r in ('ES', 'NQ')}
    P(f"    tick sizes: ES {sorted(ticks['ES'])}  NQ {sorted(ticks['NQ'])}")
    P("")

    P("--- G0c COVERAGE (rule D5 declared before results; store back-month availability is the binding fact)")
    for root, cyc, exc in (("ES", es_cyc, es_excl), ("NQ", nq_cyc, nq_excl)):
        inc = cyc[cyc.included]
        P(f"    {root}: {len(EXPIRIES)} candidate cycles (spec anticipated ~68) -> INCLUDED "
          f"{len(inc)}   excluded {len(EXPIRIES) - len(inc)}")
        if len(inc):
            P(f"        included span {inc.cycle.min()} .. {inc.cycle.max()};  full 12/12 valid: "
            f"{int(((inc.n_early == 7) & (inc.n_late == 5)).sum())} of {len(inc)}")
        reasons = exc.reason.str.replace(r"\(.*", "", regex=True).value_counts()
        # partial-coverage rows sit in cyc with included=False, not in exc? no: excl carries them
        P(f"        exclusion reasons: " + ", ".join(f"{k} x{v}" for k, v in reasons.items()))
    P("")

    es_in = es_cyc[es_cyc.included].reset_index(drop=True)
    nq_in = nq_cyc[nq_cyc.included].reset_index(drop=True)
    Nc = len(es_in)
    sd = float(es_in.shape_pts.std(ddof=1))

    # ---------------------------------------------------------------- G1 MDE FIRST
    mde = (Z95_1S + Z80) * sd / np.sqrt(Nc)
    P("--- G1: MDE FIRST (one-sided 5%, 80% power) -- printed before the observed statistic")
    P(f"    N = {Nc} included ES cycles (spec anticipated ~68 -- store back-month availability cut")
    P(f"    it to {Nc}); sd(cycle shape) = {sd:.4f} pts/day")
    P(f"    MDE = 2.4865 * sd/sqrt(N) = {mde:.4f} pts/day  (= ${mde * 50:.2f}/day on ES $50/pt)")
    P("    POWER IS THIN: ~%d cycles resolve only a shape of >= %.3f pts/day; a true richness"
      % (Nc, mde))
    P("    shape smaller than that is NOT detectable here. Said plainly, per spec G1.")
    P("")

    # ---------------------------------------------------------------- observed primary
    obs = float(es_in.shape_pts.mean())
    e_mean = float(np.nanmean([r for r in es_paths[es_paths.included_cycle
                                                   & es_paths.in_early].dR_pts]))
    l_mean = float(np.nanmean([r for r in es_paths[es_paths.included_cycle
                                                   & es_paths.in_late].dR_pts]))
    P("--- OBSERVED PRIMARY (ES)")
    P(f"    pooled mean dR EARLY [FN-12,FN-6] = {e_mean:+.4f} pts/day   "
      f"pooled mean dR LATE [FN-5,FN-1] = {l_mean:+.4f} pts/day")
    P(f"    OBSERVED SHAPE STAT (mean over {Nc} cycles of early-minus-late) = {obs:+.4f} pts/day"
      f"   (= ${obs * 50:+.2f}/day)")
    P(f"    cycle-level: median {float(es_in.shape_pts.median()):+.4f}   "
      f"share>0 {float((es_in.shape_pts > 0).mean()):.1%}")
    P("")

    # ---------------------------------------------------------------- G2 permutation
    rng = np.random.default_rng(SEED)
    dr_by_cycle = []
    for cyc in es_in.cycle:
        sub = es_paths[(es_paths.root == "ES") & (es_paths.cycle == cyc)
                       & es_paths.valid_change & (es_paths.slot >= -12)]
        sub = sub.sort_values("slot")
        dr_by_cycle.append((sub.dR_pts.values.astype(float), sub.in_early.values.astype(bool)))
    per_cycle = rotation_stats(dr_by_cycle)
    obs_check = float(np.mean([s[0] for s in per_cycle]))
    assert abs(obs_check - obs) < 1e-9, "rotation-0 must reproduce the observed stat"
    draws = np.empty(NDRAWS)
    offs = [rng.integers(0, len(s), NDRAWS) for s in per_cycle]
    M = np.stack([s[o] for s, o in zip(per_cycle, offs)])
    draws = M.mean(axis=0)
    p_perm = (1 + int((draws >= obs).sum())) / (1 + NDRAWS)
    P("--- G2: SHAPE (cycle-level rotation permutation, D7)")
    P(f"    null mean {draws.mean():+.5f}  sd {draws.std(ddof=1):.5f}  draws {NDRAWS}  seed {SEED}")
    P(f"    p_perm (one-sided, P[draw >= obs]) = {p_perm:.4f}")
    P(f"    G2 requires shape > 0 AND p < 0.05:  shape {obs:+.4f}  p {p_perm:.4f}")
    P("")

    # ---------------------------------------------------------------- G3 comovement
    def matched_pairs(cycles_both):
        a = es_paths[(es_paths.cycle.isin(cycles_both)) & es_paths.valid_change
                     & (es_paths.slot >= -12)][["cycle", "slot", "dR_pts"]]
        b = nq_paths[(nq_paths.cycle.isin(cycles_both)) & nq_paths.valid_change
                     & (nq_paths.slot >= -12)][["cycle", "slot", "dR_pts"]]
        m = a.merge(b, on=["cycle", "slot"], suffixes=("_es", "_nq"))
        return m

    co = sorted(set(es_in.cycle) & set(nq_in.cycle))
    m = matched_pairs(co)
    r = float(np.corrcoef(m.dR_pts_es, m.dR_pts_nq)[0, 1]) if len(m) > 2 else np.nan
    zr = np.arctanh(r) if np.isfinite(r) else np.nan
    se = 1 / np.sqrt(len(m) - 3) if len(m) > 3 else np.nan
    lo, hi = np.tanh(zr - 1.96 * se), np.tanh(zr + 1.96 * se)
    rs = float(pd.Series(m.dR_pts_es).corr(pd.Series(m.dR_pts_nq), method="spearman"))
    cyc_shape = es_in[["cycle", "shape_pts"]].merge(
        nq_in[["cycle", "shape_pts"]], on="cycle", suffixes=("_es", "_nq"))
    r_cyc = float(cyc_shape.shape_pts_es.corr(cyc_shape.shape_pts_nq)) if len(cyc_shape) > 2 else np.nan
    m_all = matched_pairs(sorted(set(es_cyc.cycle) & set(nq_cyc.cycle)))
    r_all = float(np.corrcoef(m_all.dR_pts_es, m_all.dR_pts_nq)[0, 1]) if len(m_all) > 2 else np.nan
    P("--- G3: MECHANISM GATE -- ES/NQ within-cycle richness-change comovement (D9)")
    P(f"    co-included cycles = {len(co)} ({co[0]}..{co[-1] if co else '-'});  matched (cycle,slot) "
      f"daily-change pairs n = {len(m)}")
    P(f"    Pearson corr = {r:+.4f}   naive 95% CI [{lo:+.4f}, {hi:+.4f}]   Spearman {rs:+.4f}")
    P(f"    annex: cycle-level shape-stat corr (n={len(cyc_shape)}) = {r_cyc:+.4f};  all matched "
      f"slots regardless of inclusion (n={len(m_all)}) = {r_all:+.4f}")
    P(f"    G3 requires corr > 0:  {r:+.4f}")
    P("")

    # ---------------------------------------------------------------- G4 eras
    def era_of(yy):
        return "2009-15" if yy <= 2015 else ("2016-21" if yy <= 2021 else "2022-26/07")
    es_in2 = es_in.copy()
    es_in2["era"] = es_in2.year.map(era_of)
    P("--- G4: ERA STABILITY (post-2016 MANDATED, D10)")
    era_rows = {}
    for era in ("2009-15", "2016-21", "2022-26/07"):
        s = es_in2[es_in2.era == era].shape_pts
        era_rows[era] = (len(s), float(s.mean()) if len(s) else np.nan)
        P(f"    {era:<10} n={len(s):>3}  mean shape {float(s.mean()) if len(s) else float('nan'):+.4f} "
          f"pts/day  sign {'+' if len(s) and s.mean() > 0 else '-'}")
    g4 = all(era_rows[e][0] >= 5 and era_rows[e][1] > 0 for e in ("2016-21", "2022-26/07"))
    P(f"    G4 requires BOTH post-2016 era means > 0 with n>=5:  "
      f"2016-21 {era_rows['2016-21'][1]:+.4f} (n={era_rows['2016-21'][0]})  "
      f"2022-26/07 {era_rows['2022-26/07'][1]:+.4f} (n={era_rows['2022-26/07'][0]})")
    P("")

    # ---------------------------------------------------------------- G5 cost note
    P("--- G5: COST NOTE (DIAGNOSTIC ONLY -- spec: a shape finding licenses a SIGNAL-LEAD, not a")
    P("    trade; nothing here gates the decision)")
    P("    exploiting richness directly = ES calendar spread, 2 legs:")
    P("      COMMISSION_ONLY  $8.72/spread RT  (2 x $4.36 Lifetime template; EVIDENCE: installed)")
    P("      SPREAD_ONLY      MODELED: ES calendar tick 0.05 pt = $2.50; roll-period calendar mkt")
    P("                       typically 1 tick wide -> 2 crossings ~ $5.00  (NO calendar-spread")
    P("                       quote data in this repo -- MODELED, not measured)")
    P("      ALL_IN           MODELED ~ $13.72/spread RT  (NQ analog ~ $10.72: tick $1.00)")
    P(f"    scale: observed |shape| {abs(obs):.3f} pts/day over a 7-day window ~ "
      f"{abs(obs) * 7 * 50:.0f} $/cycle gross on ES -- quoted for scale only, NOT a P&L claim")
    P("")

    # ---------------------------------------------------------------- G6 P-meaning
    rng2 = np.random.default_rng(SEED)
    signs = rng2.choice([-1.0, 1.0], size=(NDRAWS, Nc))
    flip = (signs * es_in.shape_pts.values).mean(axis=1)
    p_flip = (1 + int((flip >= obs).sum())) / (1 + NDRAWS)
    t = obs / (sd / np.sqrt(Nc))
    P("--- G6: P-MEANING (D13; doctrine gate -- decision rule unchanged)")
    P("    IN WORDS: p_perm answers 'if the TIMING of daily calendar-spread changes within each")
    P("    cycle were exchangeable (no richen-then-cheapen placement around the roll date), how")
    P("    often would per-cycle random rotations produce a cross-cycle mean early-minus-late")
    P("    shape at least as positive as observed?' It is a statement about WITHIN-CYCLE TIMING,")
    P("    not about the sign or size of financing itself.")
    P(f"    SECOND WAY (different event construction, same hypothesis): cycle-level sign-flip null")
    P(f"    p_flip = {p_flip:.4f} ({NDRAWS} draws); one-sample t = {t:+.2f} (N={Nc})")
    agree = (p_perm < 0.05) == (p_flip < 0.05)
    P(f"    qualitative agreement ((p_perm<.05)==(p_flip<.05)): {agree}")
    P("")

    # ---------------------------------------------------------------- diagnostics (D6)
    used = es_paths[es_paths.included_cycle & (es_paths.slot >= -13)]
    v0 = float((used.back_volume == 0).mean())
    ch = es_paths[es_paths.included_cycle & es_paths.valid_change & (es_paths.slot >= -12)].copy()
    # back change = dR + front change is not directly stored; recompute back stale flag
    ch["dF"] = np.nan
    fr = es_paths[es_paths.included_cycle].set_index(["cycle", "slot"]).front_close
    for i, row in ch.iterrows():
        prev = fr.get((row.cycle, row.slot - 1), np.nan)
        ch.at[i, "dF"] = row.front_close - prev
    dback = ch.dR_pts + ch.dF
    stale = float(((np.abs(dback) < 1e-9) & (np.abs(ch.dF) >= 0.25)).mean())
    fs_corr = float(es_in.shape_pts.corr(es_in.front_shape_pts))
    top = ch.reindex(ch.dR_pts.abs().sort_values(ascending=False).index).head(5)
    P("--- DIAGNOSTICS (declared D6, non-gating)")
    P(f"    back-leg zero-volume share of used slots (ES, included cycles): {v0:.1%} "
      f"(settle-only prints, retained)")
    P(f"    staleness: share of used changes with back EXACTLY unchanged while |dFront| >= 1 tick:"
      f" {stale:.1%}")
    P(f"    front-drift mirror: corr(cycle shape, front-only shape) = {fs_corr:+.3f} "
      f"(strongly negative would suggest stale-back artifact)")
    P(f"    mean front-only shape = {float(es_in.front_shape_pts.mean()):+.4f} pts/day")
    P("    top-5 |dR| (no trimming): " + "; ".join(
        f"{r_.cycle} s{int(r_.slot)} {r_.dR_pts:+.2f}" for r_ in top.itertuples()))
    nq_obs = float(nq_in.shape_pts.mean()) if len(nq_in) else np.nan
    P(f"    NQ annex (never rescues/vetoes): N={len(nq_in)} included cycles, mean shape "
      f"{nq_obs:+.4f} pts/day, share>0 {float((nq_in.shape_pts > 0).mean()) if len(nq_in) else float('nan'):.1%}")
    P("")

    # ---------------------------------------------------------------- gate table
    g1 = True                                   # MDE printed first, thin power said plainly
    g2 = (obs > 0) and (p_perm < 0.05)
    g3 = np.isfinite(r) and (r > 0)
    g5 = True                                   # diagnostic printed
    g0a = bool(max_read < SEAL)
    g0b = True                                  # D1 documented in header before results
    g0c = True                                  # rule declared; counts printed
    g6 = bool(agree)

    P("GATE TABLE  (printed by program)")
    hdr = f"{'GATE':<16} {'SPEC':<78} {'OBSERVED':<66} PASS-FAIL"
    P(hdr)
    def row(g, spec, obsv, ok):
        P(f"{g:<16} {spec:<78} {obsv:<66} {'PASS' if ok else '*** FAIL ***'}")
    row("G0a_SEAL", "all reads < 2026-08-01 (VIRGIN untouched)",
        f"max session read {max_read.date()}", g0a)
    row("G0b_FN_ANCHOR", "FN convention documented by program, fixed before results (spec)",
        "D1: FN = 3rd-Friday expiry - 8cd (Thu of roll week, CME convention); asserted Thu", g0b)
    row("G0c_COVERAGE", "availability rule declared pre-results; exclusions printed",
        f"ES {Nc}/70 cycles included, NQ {len(nq_in)}/70 (back-month store gaps recorded)", g0c)
    row("G1_MDE_first", "MDE printed before observed; ~68 cycles; POWER IS THIN said plainly",
        f"MDE {mde:.4f} pts/day at N={Nc} (printed first); thin-power statement printed", g1)
    row("G2_shape", "shape stat > 0 AND cycle-level permutation p < 0.05",
        f"shape {obs:+.4f} pts/day; p_perm {p_perm:.4f} ({NDRAWS} draws, seed {SEED})", g2)
    row("G3_comovement", "MECHANISM: ES/NQ within-cycle richness changes co-move, corr > 0",
        f"pooled matched corr {r:+.4f} (n={len(m)} pairs, {len(co)} co-included cycles)", g3)
    row("G4_era", "post-2016 stability mandated: both post-2016 era means > 0, n>=5",
        f"2016-21 {era_rows['2016-21'][1]:+.4f} (n={era_rows['2016-21'][0]}); "
        f"2022-26/07 {era_rows['2022-26/07'][1]:+.4f} (n={era_rows['2022-26/07'][0]})", g4)
    row("G5_cost", "diagnostic only; cost note printed (licenses signal-lead, not a trade)",
        "COMMISSION_ONLY $8.72; SPREAD_ONLY MODELED $5.00; ALL_IN MODELED ~$13.72/spr RT", g5)
    row("G6_P_MEANING", "p stated in words + second computation of same event, qual. agreement",
        f"p_perm {p_perm:.4f} vs sign-flip {p_flip:.4f}, t {t:+.2f}; agree={agree}", g6)
    P("")
    decision = ("EQROLLRICH01 SIGNAL-LEAD (conditioner lead; separate predictive falsifier next)"
                if (g2 and g3 and g4) else "CLOSED AT SCOPE (S28 block)")
    P(f"DECISION RULE (spec, mechanical): G2={'PASS' if g2 else 'FAIL'}  "
      f"G3={'PASS' if g3 else 'FAIL'}  G4={'PASS' if g4 else 'FAIL'}  ->  {decision}")
    P("NQ annex NEVER rescues/vetoes (D14). evidence_status: DISCOVERY (first read of this "
      "representation).")
    P("=" * 118)

    json.dump(dict(
        n_candidates=len(EXPIRIES), n_es=Nc, n_nq=int(len(nq_in)),
        sd_cycle=sd, mde_pts=mde, obs_shape_pts=obs,
        pooled_early=e_mean, pooled_late=l_mean,
        p_perm=p_perm, p_flip=p_flip, t=t,
        g3_corr=r, g3_n=int(len(m)), g3_ci=[float(lo), float(hi)],
        g3_spearman=rs, g3_cycle_corr=r_cyc, g3_all_corr=r_all,
        era={e: dict(n=era_rows[e][0], mean=era_rows[e][1]) for e in era_rows},
        nq_shape=nq_obs, front_mirror_corr=fs_corr, stale_share=stale, back_vol0_share=v0,
        gates=dict(G0a_SEAL=g0a, G0b_FN_ANCHOR=g0b, G0c_COVERAGE=g0c, G1_MDE_first=g1,
                   G2_shape=bool(g2), G3_comovement=bool(g3), G4_era=bool(g4),
                   G5_cost=g5, G6_P_MEANING=g6),
        decision=decision),
        open(os.path.join(OUT, "verdicts.json"), "w", encoding="utf-8"), indent=2, default=str)
    P("")
    P("WROTE out/gate_table.txt, out/cycle_paths.csv, out/cycle_stats.csv, out/exclusions.csv, "
      "out/verdicts.json")
    _fh.close()
    _lg.close()


if __name__ == "__main__":
    main()
