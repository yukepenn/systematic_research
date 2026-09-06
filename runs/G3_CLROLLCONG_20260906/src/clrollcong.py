"""G3_CLROLLCONG_20260906 (G00094) — GSCI/commodity-index roll congestion (the Goldman roll).

FROZEN OBJECT (spec.yaml, committed before results): CL primary (GC/SI reported where pairable):
per month, the F1-F2 calendar-spread return over the GSCI roll window (business days 5-9 of the
month), per-contract day store, POINTS. Congestion trade = LONG-back/SHORT-front through the
window. Conditional split: trailing-20-day vol tercile of the outright, top vs rest, with the
matched unconditional control.

FROZEN-INTERPRETATION NOTES — recorded HERE, before any result was computed:

I1. PAIR DEFINITION. For calendar month M: F1 = the nearest contract in the root's declared
    liquid cycle with delivery month >= M+1 (for CL this is delivery M+1 — exactly the GSCI CL
    roll: in month M the index rolls delivery M+1 -> M+2); F2 = the next cycle contract after F1.
    CL cycle = all 12 months. GC cycle = [2,4,6,8,12] (October excluded: not an index/liquid
    month, and the store's GC 10-* directories are empty). SI cycle = [3,5,7,9,12].
I2. WINDOW. Business days of month M realized on F1's OWN trading calendar (its store dates
    inside M; self-correcting for holidays). Entry = close of bd4, exit = close of bd9 (holding
    the change into bd5..bd9, 5 daily spread changes). S = F2 - F1 (back minus front);
    R = S(bd9) - S(bd4) in POINTS; R > 0 = congestion-trade profit.
I3. VALIDITY. A month is primary-usable iff F1 has >= 9 trading dates inside M and F2 has closes
    on ALL SIX dates bd4..bd9. Partial windows are censused, never pooled. No exclusions of any
    kind are frozen; defective data is disclosed, not dropped.
I4. G2 NULL. Circular shift of the window-flag vector against the concatenated daily spread-
    change series (all valid within-month ΔS days of the root, date-ordered; flag=1 on the five
    into-bd5..bd9 change days). Statistic T = 5 * mean(ΔS | flag) (per-window-equivalent gross
    drift). All shifts k = 1..N-1; p_1s = (1 + #{T_k >= T_0}) / (1 + (N-1)). One shared shift
    across all months per draw preserves dependence. The p is computed on GROSS T: the cost is
    the same constant per 5-day window, so ranks (and p) are identical after cost.
    IN WORDS, THE EVENT THE p IS OVER: "the probability that a randomly circularly-shifted
    placement of the 5-day window over the same daily spread-change series produces a pooled
    drift at least as large as the observed bd5-9 placement." Second, different computation of
    the same event: normal tail from the placebo distribution's own mean/sd (z), printed beside.
I5. G2 GATE = (pooled AFTER-COST-CONS mean > 0) AND (shift p_1s < 0.05). CL only gates.
I6. G4 VOL. vol(M) = stdev(ddof=1) of ln(F1 close ratios) over the trailing 20 F1 closes ending
    at bd4 (>= 17 closes required, else the month is excluded from the conditional split only —
    census printed). Terciles = full-sample [1/3, 2/3] quantiles over CL usable months with
    valid vol (in-sample conditioning, DISCOVERY). TOP = vol >= upper cut ("impaired-arb");
    REST = the rest. G4 GATE = (TOP after-cost-cons mean > 0) AND (bootstrap 95% CI of
    delta = TOP - REST excludes 0 from above). Matched unconditional control (ALL months, same
    construction) printed in the same table.
I7. G3 ERAS (frozen): 2009-01..2014-12 / 2015-01..2020-12 / 2021-01..2026-07 by calendar month.
    REPORT gate: PASS = every cell printed (including empty cells printed as empty). The decay
    read is descriptive. Supplementary NON-GATING decay reads: (a) CL usable months split into
    three equal-n chronological thirds; (b) GC/SI era tables — because the CL store is
    systematically truncated post-2016 (measured below), these carry the era-3 read.
I8. G5 COST. MODELED, SPREAD_ONLY, {1,2}-tick band per leg per RT, 2 legs x 1 RT per month-trade.
    CL: $10/tick -> base $20 = 0.02 pt, cons $40 = 0.04 pt. GC: $10/tick -> 0.2/0.4 pt.
    SI: $25/tick -> 0.01/0.02 pt. Gates use the CONS rung. COMMISSION_ONLY info, non-gating:
    2 x $4.36 = $8.72/month-trade. Tick headers asserted == declared on every loaded contract.
I9. SEAL. Every row with date >= 2026-08-01 is dropped at load; the program asserts the max
    surviving date < 2026-08-01. Candidate months end at 2026-07.
I10. RNG seed 20260906; 10,000 bootstrap draws (percentile CIs); month = the block unit.
I11. IDENTITY GATES. Per-contract path only (ncd_day.read_contract; the unmerged store);
    sha256 of ncd_day.py printed; endpoint R asserted == sum of the 5 daily ΔS (telescoping);
    merged-path contamination screen (F1/F2 identical volume on >= 3 window dates -> flagged,
    non-gating) and absurd-spread screen (|S(bd4)| > 10 pt CL / > 50 pt GC/SI -> flagged).
I12. DECISION RULE (mechanical, from spec): G2 FAIL and G4 FAIL -> CLOSED-AS-COMPETED-AWAY
    (permanent). G4 PASS alone -> narrow impaired-arb lead (Class-P at best, next-stage
    falsifier required). G2 PASS -> not closed; recorded as-is.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys

import numpy as np
import pandas as pd

SRC_DIR = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research\research\multi_market\src"
RUN_DIR = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research\runs\G3_CLROLLCONG_20260906"
OUT = os.path.join(RUN_DIR, "out")
sys.path.insert(0, SRC_DIR)
import ncd_day  # noqa: E402

SEAL = pd.Timestamp("2026-08-01")
M_FIRST, M_LAST = pd.Period("2009-01", "M"), pd.Period("2026-07", "M")
ERAS = [("2009-14", pd.Period("2009-01", "M"), pd.Period("2014-12", "M")),
        ("2015-20", pd.Period("2015-01", "M"), pd.Period("2020-12", "M")),
        ("2021-26", pd.Period("2021-01", "M"), pd.Period("2026-07", "M"))]
ROOTS = {
    "CL": dict(cycle=list(range(1, 13)), tick=0.01, pv=1000.0),
    "GC": dict(cycle=[2, 4, 6, 8, 12], tick=0.10, pv=100.0),
    "SI": dict(cycle=[3, 5, 7, 9, 12], tick=0.005, pv=5000.0),
}
COMMISSION_RT = 4.36
N_BOOT = 10000
RNG = np.random.default_rng(20260906)

_cache: dict[str, pd.DataFrame] = {}
_tick_asserts: dict[str, int] = {}


def load(cid: str, root: str) -> pd.DataFrame:
    if cid in _cache:
        return _cache[cid]
    d = ncd_day.read_contract(cid)
    if not d.empty:
        d = d[d["date"] < SEAL].reset_index(drop=True)
        if not d.empty:
            tk = float(d["tick_size"].iloc[0])
            assert abs(tk - ROOTS[root]["tick"]) < 1e-12, f"tick mismatch {cid}: {tk}"
            _tick_asserts[root] = _tick_asserts.get(root, 0) + 1
            assert d["date"].max() < SEAL, f"SEAL VIOLATION {cid}"
    _cache[cid] = d
    return d


def pair_for(root: str, per: pd.Period):
    cyc = ROOTS[root]["cycle"]
    cands = []
    for y in (per.year, per.year + 1):
        for m in cyc:
            p = pd.Period(f"{y}-{m:02d}", "M")
            if p >= per + 1:
                cands.append(p)
    cands = sorted(set(cands))
    f1, f2 = cands[0], cands[1]
    return (ncd_day.contract_id(root, f1.month, f1.year),
            ncd_day.contract_id(root, f2.month, f2.year))


def closes(d: pd.DataFrame) -> pd.Series:
    if d.empty:
        return pd.Series(dtype=float)
    return pd.Series(d["close"].values, index=pd.DatetimeIndex(d["date"]).normalize())


def vols_series(d: pd.DataFrame) -> pd.Series:
    if d.empty:
        return pd.Series(dtype=float)
    return pd.Series(d["volume"].values, index=pd.DatetimeIndex(d["date"]).normalize())


def boot_ci(x: np.ndarray, n=N_BOOT):
    if len(x) == 0:
        return (np.nan, np.nan)
    idx = RNG.integers(0, len(x), size=(n, len(x)))
    means = x[idx].mean(axis=1)
    return tuple(np.percentile(means, [2.5, 97.5]))


def fmt(v, w=10, p=5):
    return ("%" + str(w) + "." + str(p) + "f") % v if np.isfinite(v) else " " * (w - 3) + "nan"


def main():
    print("=" * 100)
    print("G3_CLROLLCONG_20260906 (G00094) — Goldman-roll congestion, CL primary, GC/SI secondary")
    print("=" * 100)
    with open(os.path.join(SRC_DIR, "ncd_day.py"), "rb") as f:
        print(f"transport ncd_day.py sha256 = {hashlib.sha256(f.read()).hexdigest()}")
    print(f"seal: all rows >= {SEAL.date()} dropped at load; candidate months {M_FIRST}..{M_LAST}")
    print(__doc__.split("FROZEN-INTERPRETATION NOTES")[0].strip())
    print("(full frozen-interpretation notes I1-I12 in src/clrollcong.py header)")

    # ---------------- build panel ----------------
    months = pd.period_range(M_FIRST, M_LAST, freq="M")
    rows = []
    daily = {r: [] for r in ROOTS}   # per root: (date, dS, flag) for shift null
    max_seen = pd.Timestamp("1900-01-01")
    for root in ROOTS:
        prev_f1 = None
        for per in months:
            f1c, f2c = pair_for(root, per)
            d1, d2 = load(f1c, root), load(f2c, root)
            is_roll = (prev_f1 is not None and f1c != prev_f1)
            prev_f1 = f1c
            rec = dict(root=root, month=str(per), f1=f1c, f2=f2c, is_roll_month=is_roll,
                       status="", n_bd=0, t0="", t1="", R_gross=np.nan, R_net_base=np.nan,
                       R_net_cons=np.nan, vol20=np.nan, n_vol_closes=0, contam_flag=False,
                       abs_spread_flag=False)
            if d1.empty:
                rec["status"] = "NO_F1_DATA"; rows.append(rec); continue
            if d2.empty:
                rec["status"] = "NO_F2_DATA"; rows.append(rec); continue
            c1, c2 = closes(d1), closes(d2)
            v1, v2 = vols_series(d1), vols_series(d2)
            max_seen = max(max_seen, c1.index.max(), c2.index.max())
            bd = [t for t in c1.index if t.year == per.year and t.month == per.month]
            rec["n_bd"] = len(bd)
            if len(bd) < 9:
                rec["status"] = "F1_SHORT_MONTH"; rows.append(rec); continue
            win = bd[3:9]                       # bd4..bd9 inclusive (6 closes)
            rec["t0"], rec["t1"] = str(win[0].date()), str(win[-1].date())
            missing = [t for t in win if t not in c2.index]
            # daily ΔS series for the shift null (independent of primary completeness)
            for j in range(1, len(bd)):
                t, p_ = bd[j], bd[j - 1]
                if t in c2.index and p_ in c2.index:
                    dS = (c2[t] - c1[t]) - (c2[p_] - c1[p_])
                    daily[root].append((t, dS, 1 if 4 <= j <= 8 else 0))
            if missing:
                rec["status"] = f"F2_WINDOW_GAP_{len(missing)}of6"; rows.append(rec); continue
            S = [(c2[t] - c1[t]) for t in win]
            R = S[-1] - S[0]
            dsum = sum(S[j] - S[j - 1] for j in range(1, 6))
            assert abs(R - dsum) < 1e-9, f"telescoping violated {root} {per}"
            tick, pv = ROOTS[root]["tick"], ROOTS[root]["pv"]
            cost_base, cost_cons = 2 * tick, 4 * tick     # points: {1,2} ticks x 2 legs
            rec.update(status="OK", R_gross=R, R_net_base=R - cost_base,
                       R_net_cons=R - cost_cons)
            # vol20 on F1 outright, trailing 20 closes ending at bd4
            hist = c1[c1.index <= win[0]].tail(20)
            rec["n_vol_closes"] = len(hist)
            if len(hist) >= 17:
                lr = np.diff(np.log(hist.values))
                rec["vol20"] = float(np.std(lr, ddof=1))
            # identity screens
            same_vol = sum(1 for t in win if t in v2.index and v1[t] == v2[t])
            rec["contam_flag"] = same_vol >= 3
            rec["abs_spread_flag"] = abs(S[0]) > (10 if root == "CL" else 50)
            rows.append(rec)
    panel = pd.DataFrame(rows)
    assert max_seen < SEAL, "SEAL VIOLATION in assembled panel"
    print(f"\nseal assert PASS: max loaded/used date {max_seen.date()} < {SEAL.date()}")
    print("tick-header asserts PASS on every loaded contract: " +
          ", ".join(f"{r}={_tick_asserts.get(r,0)} contracts @ {ROOTS[r]['tick']}" for r in ROOTS))

    era_of = {}
    for lab, a, b in ERAS:
        for per in pd.period_range(a, min(b, M_LAST), freq="M"):
            era_of[str(per)] = lab
    panel["era"] = panel["month"].map(era_of)
    panel.to_csv(os.path.join(OUT, "monthly_panel.csv"), index=False)

    # ---------------- pairing coverage (census, honest) ----------------
    print("\n" + "-" * 100)
    print("PAIRING COVERAGE (census of all candidate months; the store's systematic gaps, itemized)")
    print("-" * 100)
    for root in ROOTS:
        sub = panel[panel.root == root]
        print(f"\n{root}: census {len(sub)} months; status counts: " +
              str(sub["status"].str.replace(r"_\din6$", "", regex=False).value_counts().to_dict()))
        ok = sub[sub.status == "OK"]
        print(f"  usable-for-primary {len(ok)}; per frozen era: " +
              str(ok["era"].value_counts().reindex([e[0] for e in ERAS], fill_value=0).to_dict()))
        if len(ok):
            print(f"  usable span {ok['month'].min()} .. {ok['month'].max()}")
    cl = panel[(panel.root == "CL")]
    cl_ok = cl[cl.status == "OK"].copy()
    gap = cl[cl.status.str.startswith("F2_WINDOW_GAP")]
    print("\nCL gap anatomy (the TSYROLL-style systematic store truncation, measured):")
    print(f"  months lost to F2_WINDOW_GAP: {len(gap)}; first lost month {gap['month'].min() if len(gap) else '-'};"
          f" every CL contract with delivery >= 2016-02 carries only ~its final month of rows,")
    print("  so the F2 leg (delivery M+2) is born ~day 16-18 of month M and can never overlap bd5-9.")
    print("  This is DATA ABSENCE in the store, not market absence; itemized in monthly_panel.csv.")

    # ---------------- G1 MDE first ----------------
    print("\n" + "-" * 100)
    print("G1 — MDE FIRST (printed before any observed pooled mean)")
    print("-" * 100)
    R = cl_ok["R_gross"].values.astype(float)
    Rn = cl_ok["R_net_cons"].values.astype(float)
    N = len(R)
    sd = float(np.std(R, ddof=1))
    mde = 2.4865 * sd / np.sqrt(N)   # z(0.95)+z(0.80)
    pv = ROOTS["CL"]["pv"]
    print(f"CL usable months N = {N} (census {len(cl)}; shortfall itemized above, honest)")
    print(f"monthly window-return sd = {sd:.5f} pt  (cost-invariant)")
    print(f"MDE (one-sided 5%, 80% power) = 2.4865*sd/sqrt(N) = {mde:.5f} pt = ${mde*pv:,.0f}/month-trade")

    # ---------------- observed + G2 ----------------
    print("\n" + "-" * 100)
    print("G2 — POOLED AFTER-COST MEAN vs CIRCULAR-SHIFT NULL (CL, gating)")
    print("-" * 100)
    g_mean, n_mean = float(np.mean(R)), float(np.mean(Rn))
    ci = boot_ci(Rn)
    dl = pd.DataFrame(daily["CL"], columns=["date", "dS", "flag"]).sort_values("date")
    ds, fl = dl["dS"].values.astype(float), dl["flag"].values.astype(int)
    nD, nW = len(ds), int(fl.sum())
    T0 = 5.0 * float(ds[fl == 1].mean())
    Tk = np.empty(nD - 1)
    for k in range(1, nD):
        Tk[k - 1] = 5.0 * ds[np.roll(fl, k) == 1].mean()
    p_shift = (1 + int((Tk >= T0).sum())) / (1 + len(Tk))
    z = (T0 - Tk.mean()) / Tk.std(ddof=1)
    from math import erf, sqrt
    p_norm = 0.5 * (1 - erf(z / sqrt(2)))
    print(f"pooled GROSS mean       = {g_mean:+.5f} pt = ${g_mean*pv:+,.2f}/month-trade  (share>0 {100*np.mean(R>0):.1f}%)")
    print(f"pooled NET-CONS mean    = {n_mean:+.5f} pt = ${n_mean*pv:+,.2f}/month-trade  (share>0 {100*np.mean(Rn>0):.1f}%)")
    print(f"month-bootstrap 95% CI (net-cons) = [{ci[0]:+.5f}, {ci[1]:+.5f}] pt  (cross-check, non-gating)")
    print(f"flagged-day construction T0 = {T0:+.5f} pt vs per-month pooled gross {g_mean:+.5f} pt "
          f"(same event two ways; T0 uses all {nW} valid window days incl. partial months)")
    print(f"shift null: {len(Tk)} circular shifts over {nD} valid daily ΔS obs; "
          f"placebo mean {Tk.mean():+.5f}, sd {Tk.std(ddof=1):.5f} pt")
    print("EVENT IN WORDS: p = probability that a circularly-shifted placement of the 5-day window")
    print("  over the same daily spread-change series yields pooled drift >= the observed bd5-9 one.")
    print(f"p_1s(shift rank) = {p_shift:.4f}   |   second computation, normal tail of placebo dist: "
          f"z = {z:+.3f}, p = {p_norm:.4f}")
    g2a, g2b = n_mean > 0, p_shift < 0.05
    g2 = g2a and g2b
    print(f"G2 clause A (net-cons mean > 0): {'PASS' if g2a else 'FAIL'}   "
          f"clause B (p_shift < 0.05): {'PASS' if g2b else 'FAIL'}   ==> G2 {'PASS' if g2 else 'FAIL'}")

    # ---------------- G3 era thirds ----------------
    print("\n" + "-" * 100)
    print("G3 — ERA THIRDS (frozen 2009-14 / 2015-20 / 2021-26) — THE DECAY READ")
    print("-" * 100)
    era_rows = []

    def era_line(tag, root, sub_ok):
        r_ = sub_ok["R_gross"].values.astype(float)
        rn_ = sub_ok["R_net_cons"].values.astype(float)
        lo, hi = boot_ci(rn_)
        line = dict(table=tag, root=root, cell=sub_ok.name if hasattr(sub_ok, "name") else "",
                    n=len(r_), gross_mean_pt=np.mean(r_) if len(r_) else np.nan,
                    net_cons_mean_pt=np.mean(rn_) if len(r_) else np.nan,
                    ci_lo=lo, ci_hi=hi, share_pos_gross=np.mean(r_ > 0) if len(r_) else np.nan)
        return line

    hdr = f"{'root':<5}{'era':<10}{'n':>4} {'gross_pt':>10} {'netcons_pt':>11} {'ci_lo':>10} {'ci_hi':>10} {'sh>0':>6}"
    print(hdr)
    for root in ROOTS:
        ok = panel[(panel.root == root) & (panel.status == "OK")]
        for lab, _, _ in ERAS:
            sub = ok[ok.era == lab]
            li = era_line("frozen_era", root, sub); li["cell"] = lab
            era_rows.append(li)
            if len(sub) == 0:
                print(f"{root:<5}{lab:<10}{0:>4} {'EMPTY (store-limited)':>54}")
            else:
                print(f"{root:<5}{lab:<10}{len(sub):>4} {fmt(li['gross_mean_pt'])} {fmt(li['net_cons_mean_pt'],11)}"
                      f" {fmt(li['ci_lo'])} {fmt(li['ci_hi'])} {100*li['share_pos_gross']:>5.1f}%")
    print("\nSUPPLEMENTARY (non-gating) — CL usable months in three equal-n chronological thirds")
    cl_ok = cl_ok.sort_values("month").reset_index(drop=True)
    cuts = np.array_split(np.arange(len(cl_ok)), 3)
    for i, idx in enumerate(cuts):
        sub = cl_ok.iloc[idx]
        li = era_line("cl_supp_third", "CL", sub)
        li["cell"] = f"T{i+1}:{sub['month'].iloc[0]}..{sub['month'].iloc[-1]}"
        era_rows.append(li)
        print(f"{'CL':<5}{li['cell']:<22}{len(sub):>4} {fmt(li['gross_mean_pt'])} {fmt(li['net_cons_mean_pt'],11)}"
              f" {fmt(li['ci_lo'])} {fmt(li['ci_hi'])} {100*li['share_pos_gross']:>5.1f}%")
    print("\nSUPPLEMENTARY (non-gating) — GC/SI actual-roll months only (F1 changed vs prior month)")
    for root in ("GC", "SI"):
        ok = panel[(panel.root == root) & (panel.status == "OK") & (panel.is_roll_month)]
        for lab, _, _ in ERAS:
            sub = ok[ok.era == lab]
            li = era_line("rollmonth_era", root, sub); li["cell"] = lab + "/rollmo"
            era_rows.append(li)
            if len(sub):
                print(f"{root:<5}{li['cell']:<10}{len(sub):>4} {fmt(li['gross_mean_pt'])} "
                      f"{fmt(li['net_cons_mean_pt'],11)} {fmt(li['ci_lo'])} {fmt(li['ci_hi'])} "
                      f"{100*li['share_pos_gross']:>5.1f}%")
            else:
                print(f"{root:<5}{li['cell']:<10}{0:>4} {'EMPTY':>20}")
    pd.DataFrame(era_rows).to_csv(os.path.join(OUT, "era_thirds.csv"), index=False)
    g3 = True   # REPORT gate: all cells printed above, empties printed as empty
    print("\nG3 (report gate, all cells printed incl. empties): PASS-AS-PRINTED")

    # ---------------- G4 impaired-arb conditional ----------------
    print("\n" + "-" * 100)
    print("G4 — TOP-VOL-TERCILE (IMPAIRED-ARB) vs REST, with matched unconditional control (CL)")
    print("-" * 100)
    v_ok = cl_ok[np.isfinite(cl_ok["vol20"])].copy()
    n_novol = len(cl_ok) - len(v_ok)
    q1, q2 = np.quantile(v_ok["vol20"].values, [1 / 3, 2 / 3])
    top = v_ok[v_ok["vol20"] >= q2]
    rest = v_ok[v_ok["vol20"] < q2]
    print(f"months with valid vol20: {len(v_ok)} of {len(cl_ok)} usable ({n_novol} excluded, <17 trailing closes)")
    print(f"tercile cuts (full-sample, in-sample conditioning, DISCOVERY): q33={q1:.5f} q67={q2:.5f} (daily log-ret sd)")
    rows4 = []
    for nm, sub in (("TOP (impaired-arb)", top), ("REST", rest), ("ALL (uncond control)", v_ok),
                    ("ALL usable (pooled)", cl_ok)):
        rn_ = sub["R_net_cons"].values.astype(float)
        r_ = sub["R_gross"].values.astype(float)
        lo, hi = boot_ci(rn_)
        rows4.append((nm, len(sub), np.mean(r_), np.mean(rn_), lo, hi, np.mean(rn_ > 0)))
        print(f"  {nm:<22} n={len(sub):>3}  gross {np.mean(r_):+.5f}  net-cons {np.mean(rn_):+.5f} pt"
              f"  CI[{lo:+.5f},{hi:+.5f}]  share>0(net) {100*np.mean(rn_>0):.1f}%")
    a1, a2 = top["R_net_cons"].values.astype(float), rest["R_net_cons"].values.astype(float)
    i1 = RNG.integers(0, len(a1), size=(N_BOOT, len(a1)))
    i2 = RNG.integers(0, len(a2), size=(N_BOOT, len(a2)))
    deltas = a1[i1].mean(axis=1) - a2[i2].mean(axis=1)
    dlo, dhi = np.percentile(deltas, [2.5, 97.5])
    delta = a1.mean() - a2.mean()
    print(f"  delta (TOP - REST) net-cons = {delta:+.5f} pt, bootstrap 95% CI [{dlo:+.5f}, {dhi:+.5f}]")
    g4a, g4b = a1.mean() > 0, dlo > 0
    g4 = g4a and g4b
    print(f"G4 clause A (TOP net-cons mean > 0): {'PASS' if g4a else 'FAIL'}   "
          f"clause B (delta CI_lo > 0): {'PASS' if g4b else 'FAIL'}   ==> G4 {'PASS' if g4 else 'FAIL'}")
    print("NOTE: with the CL store truncated post-2016-01, this cell can only speak for 2009-15;")
    print("      the 2020 negative-price episode (the canonical impaired-arb month) is NOT in the CL panel.")

    # ---------------- G5 cost ----------------
    print("\n" + "-" * 100)
    print("G5 — COST MODEL (MODELED, SPREAD_ONLY, {1,2}-tick band per leg; CONS rung gates)")
    print("-" * 100)
    for root in ROOTS:
        t_, p_ = ROOTS[root]["tick"], ROOTS[root]["pv"]
        print(f"  {root}: tick {t_} pt (${t_*p_:.2f}); base 2x1 tick = {2*t_:.3f} pt = ${2*t_*p_:.2f}; "
              f"cons 2x2 ticks = {4*t_:.3f} pt = ${4*t_*p_:.2f} per month-trade (2 legs x 1 RT)")
    print(f"  COMMISSION_ONLY info, non-gating: 2 x ${COMMISSION_RT} = ${2*COMMISSION_RT}/month-trade")
    print("  tick headers asserted == declared on every loaded contract (see assert line above)")
    g5 = True
    print("G5: PASS (printed; cons rung gates G2/G3/G4 net figures; EVIDENCE=MODELED)")

    # ---------------- identity screens / anomalies ----------------
    print("\n" + "-" * 100)
    print("IDENTITY SCREENS (non-gating, disclosed)")
    print("-" * 100)
    for root in ROOTS:
        ok = panel[(panel.root == root) & (panel.status == "OK")]
        cf = ok[ok.contam_flag]
        af = ok[ok.abs_spread_flag]
        print(f"  {root}: merged-path contamination flags (F1==F2 volume >=3 window days): "
              f"{len(cf)} {list(cf['month']) if len(cf) else ''}")
        print(f"      absurd-spread flags (|S(bd4)| > {'10' if root=='CL' else '50'} pt): "
              f"{len(af)} {list(af['month']) if len(af) else ''}")

    # ---------------- gate table + decision ----------------
    print("\n" + "=" * 100)
    print("GATE / SPEC / OBSERVED / PASS-FAIL (program-printed)")
    print("=" * 100)
    tbl = [
        ("G1_MDE_first", "MDE printed before observed; honest N",
         f"N={N} (census {len(cl)}), MDE={mde:.4f} pt (${mde*pv:,.0f})", "PASS"),
        ("G2_pooled", "net-cons mean>0 AND shift p<0.05",
         f"net-cons {n_mean:+.4f} pt, p_shift {p_shift:.4f}", "PASS" if g2 else "FAIL"),
        ("G3_era_thirds", "2009-14/2015-20/2021-26 printed",
         "printed; CL era3 EMPTY (store-limited), GC/SI carry era3", "PASS" if g3 else "FAIL"),
        ("G4_impaired_arb", "TOP net-cons>0 AND delta CI_lo>0",
         f"TOP {a1.mean():+.4f} pt, delta {delta:+.4f} CI[{dlo:+.4f},{dhi:+.4f}]",
         "PASS" if g4 else "FAIL"),
        ("G5_cost", "{1,2}-tick band, cons gates, ticks asserted",
         "printed; asserts PASS", "PASS" if g5 else "FAIL"),
    ]
    print(f"{'GATE':<18}{'SPEC':<42}{'OBSERVED':<58}{'VERDICT'}")
    for g, s, o, v in tbl:
        print(f"{g:<18}{s:<42}{o:<58}{v}")
    if (not g2) and (not g4):
        decision = "CLOSED-AS-COMPETED-AWAY"
        note = "permanent; the expected and bankable outcome (spec decision rule: G2+G4 both fail)"
    elif g4 and not g2:
        decision = "NARROW-IMPAIRED-ARB-LEAD"
        note = "Class-P at best; next-stage falsifier required (spec decision rule: G4 alone passing)"
    else:
        decision = "NOT-CLOSED-G2-PASS"
        note = "unexpected under the card's own prior; record as-is, next-stage falsifier required"
    print(f"\nDECISION (mechanical): {decision} — {note}")
    print("EVIDENCE STATUS of every number above: DISCOVERY (first read of this representation; consumed).")

    verdicts = dict(
        run_id="G3_CLROLLCONG_20260906", ledger="G00094", family="GENESIS3_RV",
        decision=decision,
        gates=dict(G1="PASS", G2="PASS" if g2 else "FAIL", G3="PASS" if g3 else "FAIL",
                   G4="PASS" if g4 else "FAIL", G5="PASS" if g5 else "FAIL"),
        cl=dict(N=N, census=len(cl), sd_pt=sd, mde_pt=mde, gross_mean_pt=g_mean,
                net_cons_mean_pt=n_mean, net_cons_ci=list(ci), p_shift=p_shift,
                z_placebo=float(z), p_norm=float(p_norm), n_shifts=int(len(Tk)),
                T0_flagged=T0, usable_span=[str(cl_ok['month'].min()), str(cl_ok['month'].max())]),
        g4=dict(n_top=len(a1), n_rest=len(a2), top_net_cons=float(a1.mean()),
                rest_net_cons=float(a2.mean()), delta=float(delta), delta_ci=[float(dlo), float(dhi)],
                q67_cut=float(q2)),
        seal=dict(max_date_used=str(max_seen.date()), seal="2026-08-01", asserted=True),
    )
    with open(os.path.join(OUT, "verdicts.json"), "w", encoding="utf-8") as f:
        json.dump(verdicts, f, indent=2)
    print("\nwrote out/monthly_panel.csv, out/era_thirds.csv, out/verdicts.json")


if __name__ == "__main__":
    main()
