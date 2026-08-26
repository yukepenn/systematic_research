"""WE_W57 - does B-MOM track a REGIME or a CALENDAR?

W56 measured that P1 + B-MOM at w=0.30 pays +43 % more per week at a slightly better drawdown
distribution. The arithmetic is sound; the ingredient is not established. B-MOM earns t = 2.66
on 1,122 sessions (2022-2026, its own development sample) and t = 0.27 on 4,077 sessions
(2006-2021). Charter Amendment 1 section 2(b) admits a recency-concentrated edge only if it
tracks a MEASURABLE CAUSAL REGIME VARIABLE that was also present earlier.

The power is in the 4,077 pre-2022 sessions that already exist, not in a 40-session forward
peek. Nothing is re-implemented: this re-buckets B-MOM's own saved daily ledger.
"""
from __future__ import annotations

import os
import sys
import time as _time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from run_we_w01 import ROOT                                              # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W57_BMOMREGIME", "out")
os.makedirs(OUT, exist_ok=True)
BMOM_H = os.path.join(ROOT, "research", "scalping_lab", "artifacts", "w10_bmom_hist",
                      "w10bmom_daily.csv")
BMOM_D = os.path.join(ROOT, "research", "scalping_lab", "artifacts", "w8_bmom",
                      "w8bmom_w14_daily.csv")
PARQ = os.path.join(ROOT, "research", "scalping_lab", "substrate", "minute", "NQ",
                    "nq1m_2005_202605.parquet")
NQ = 5                    # quintiles
RANKWIN = 500             # trailing sessions used for the causal rank
SPLIT = pd.Timestamp("2022-01-01")


def main():
    t0 = _time.time()
    out = open(os.path.join(OUT, "regime.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out)

    # ---------------- PHASE 0: B1 ------------------------------------------------------
    bm = pd.concat([pd.read_csv(BMOM_H), pd.read_csv(BMOM_D)], ignore_index=True)
    bm["sess"] = pd.to_datetime(bm["sess"])
    bm = bm.sort_values("sess").reset_index(drop=True)
    dev = bm[bm["sess"] >= SPLIT]
    ok = (len(bm) == 5199) and abs(dev["net_c1_usd"].sum() - 319123.12) < 1.0
    P_(f"=== PHASE 0 B1: {len(bm):,} sessions (expect 5,199), dev-era net "
       f"${dev['net_c1_usd'].sum():,.2f} (expect $319,123.12) -> "
       f"{'PASS' if ok else 'FAIL - VOID'}")
    if not ok:
        out.close(); return

    # ---------------- PHASE 1: causal regime variables ----------------------------------
    P_(f"\n   building daily regime variables from the 1-minute substrate "
       f"[{_time.time()-t0:.0f}s]")
    df = pd.read_parquet(PARQ, columns=["time", "open", "high", "low", "close", "volume"])
    df["time"] = pd.to_datetime(df["time"])
    mod = (df["time"].dt.hour * 60 + df["time"].dt.minute).values
    rth = df[(mod > 570) & (mod <= 960)].copy()          # 09:31..16:00 ET bars
    rth["d"] = rth["time"].dt.normalize()
    g = rth.groupby("d")
    day = pd.DataFrame({
        "o": g["open"].first(), "h": g["high"].max(), "l": g["low"].min(),
        "c": g["close"].last(), "v": g["volume"].sum(), "nbar": g["close"].count(),
    })
    day = day[day["nbar"] >= 200]                        # full RTH sessions only

    # intraday variance ratio: Var(30-min returns) / (30 * Var(1-min returns)), per day
    vr = {}
    for d, q in rth.groupby("d"):
        c = q["close"].values
        if len(c) < 200:
            continue
        r = np.diff(c)
        k = 30
        m = (len(r) // k) * k
        if m < 5 * k:
            continue
        r30 = r[:m].reshape(-1, k).sum(axis=1)
        v1 = r.var(ddof=1)
        vr[d] = float(r30.var(ddof=1) / (k * v1)) if v1 > 0 else np.nan
    day["vr"] = pd.Series(vr)
    day["tr"] = day["h"] - day["l"]
    day["gap"] = (day["o"] - day["c"].shift(1)).abs()
    P_(f"   {len(day):,} RTH sessions {day.index.min().date()} -> {day.index.max().date()} "
       f"[{_time.time()-t0:.0f}s]")

    def trail(s, w, minp=60):
        return s.rolling(w, min_periods=minp).mean().shift(1)     # lagged = causal
    REG = pd.DataFrame(index=day.index)
    REG["R1_range_pts"] = trail(day["tr"], 60)
    REG["R1b_range_pct"] = trail(day["tr"] / day["c"], 60)
    REG["R2_price"] = day["c"].shift(1)
    REG["R3_varratio"] = trail(day["vr"], 60)
    REG["R4_gap_share"] = trail(day["gap"] / day["tr"].replace(0, np.nan), 60)
    REG["R5_volume"] = trail(day["v"], 60) / trail(day["v"], 500, 250)

    M = bm.set_index("sess").join(REG, how="inner")
    M["era"] = np.where(M.index >= SPLIT, "2022-2026", "2006-2021")
    P_(f"   joined: {len(M):,} B-MOM sessions carry regime variables "
       f"({int((M['era'] == '2006-2021').sum()):,} pre-2022, "
       f"{int((M['era'] == '2022-2026').sum()):,} post)")

    # ---------------- PHASE 2: THE DECISIVE TEST ----------------------------------------
    P_(f"\n{'='*110}\n=== PHASE 2: B-MOM by causal regime quintile, SEPARATELY BY ERA")
    P_(f"{'='*110}")
    P_("REGIME if the top quintile is positive with a meaningful t PRE-2022 as well.")
    P_("DATE if only the post-2022 rows earn. Quintile boundaries are CAUSAL trailing ranks")
    P_(f"against the prior {RANKWIN} sessions, never a full-sample quantile.\n")

    def crank(v):
        r = np.full(len(v), np.nan)
        for j in range(RANKWIN, len(v)):
            h = v[max(0, j - RANKWIN):j]
            h = h[np.isfinite(h)]
            if len(h) >= 100 and np.isfinite(v[j]):
                r[j] = float((h < v[j]).mean())
        return r
    pnl = M["net_c1_usd"].values
    rows = []
    for var in REG.columns:
        rk = crank(M[var].values)
        M["_rk"] = rk
        P_(f"--- {var} ---")
        P_(f"{'quintile':<10}" + "".join(f"{e:>34}" for e in ("2006-2021", "2022-2026"))
           + f"{'top-Q share pre/post':>24}")
        P_(f"{'':<10}" + "".join(f"{'n':>8}{'net $':>12}{'mean$':>7}{'t':>7}"
                                 for _ in range(2)))
        for b in range(NQ):
            hi = ((b + 1) / NQ) if b < NQ - 1 else 1.0001
            m = np.isfinite(rk) & (rk >= b / NQ) & (rk < hi)
            line = f"Q{b+1:<9}"
            rec = dict(var=var, q=b + 1)
            for e in ("2006-2021", "2022-2026"):
                mm = m & (M["era"].values == e)
                if mm.sum() < 20:
                    line += f"{int(mm.sum()):>8}{'-':>12}{'-':>7}{'-':>7}"
                    continue
                p = pnl[mm]
                se = p.std(ddof=1) / np.sqrt(len(p))
                t = p.mean() / se if se > 0 else 0.0
                line += f"{len(p):>8}{p.sum():>12,.0f}{p.mean():>7,.0f}{t:>7.2f}"
                rec[f"n_{e}"] = int(len(p)); rec[f"net_{e}"] = float(p.sum())
                rec[f"mean_{e}"] = float(p.mean()); rec[f"t_{e}"] = float(t)
            if b == NQ - 1:
                pre = float((m & (M["era"].values == "2006-2021")).sum())
                pos = float((m & (M["era"].values == "2022-2026")).sum())
                npre = float((M["era"].values == "2006-2021").sum())
                npos = float((M["era"].values == "2022-2026").sum())
                line += f"{100*pre/npre:>11.1f}%{100*pos/npos:>11.1f}%"
            P_(line)
            rows.append(rec)
        P_("")
    Q = pd.DataFrame(rows)
    Q.to_csv(os.path.join(OUT, "quintiles.csv"), index=False)

    # ---------------- THE VERDICT -------------------------------------------------------
    P_(f"{'='*110}\n=== VERDICT (preregistered: REGIME requires the top quintile positive "
       f"PRE-2022)")
    P_(f"{'='*110}")
    top = Q[Q["q"] == NQ]
    P_(f"{'variable':<18}{'pre-2022 n':>12}{'pre-2022 mean$':>16}{'pre-2022 t':>12}"
       f"{'post n':>9}{'post mean$':>12}{'post t':>9}{'verdict':>12}")
    qualifies = []
    for _, r in top.iterrows():
        pn = r.get("n_2006-2021", 0)
        pm = r.get("mean_2006-2021", np.nan)
        pt = r.get("t_2006-2021", np.nan)
        on_ = r.get("n_2022-2026", 0)
        om = r.get("mean_2022-2026", np.nan)
        ot = r.get("t_2022-2026", np.nan)
        # amendment_1: the spec's MECHANICAL COHERENCE requirement, which the first version of
        # this code did not implement. (a) the edge must be there pre-2022 AND (b) it must be
        # in the SAME regime state post-2022, or the variable does not locate the modern edge.
        good = bool(np.isfinite(pt) and pt >= 1.65 and np.isfinite(pm) and pm > 0
                    and np.isfinite(ot) and ot >= 1.65 and np.isfinite(om) and om > 0)
        if good:
            qualifies.append(r["var"])
        P_(f"{r['var']:<18}{int(pn) if pn == pn else 0:>12}"
           f"{pm if pm == pm else 0:>16,.0f}{pt if pt == pt else 0:>12.2f}"
           f"{int(on_) if on_ == on_ else 0:>9}{om if om == om else 0:>12,.0f}"
           f"{ot if ot == ot else 0:>9.2f}"
           f"{('REGIME' if good else 'date'):>12}")
    P_("")
    if qualifies:
        P_(f"   QUALIFYING VARIABLES: {', '.join(qualifies)}")
        P_(f"   -> B-MOM's edge is present pre-2022 in the same regime state. Amendment 1")
        P_(f"      section 2(b) is satisfied for these variables and phase 3 is authorised.")
    else:
        P_(f"   NO VARIABLE QUALIFIES. In every candidate regime's top quintile, B-MOM's")
        P_(f"   pre-2022 record fails to reach t = 1.65 with a positive mean.")
        P_(f"   -> RECORDED: B-MOM is a 4-year in-sample result, not a regime-conditioned edge.")
        P_(f"      W56's falsifier fires: this repo holds no engine that diversifies P1 on")
        P_(f"      present evidence, model concentration is the binding constraint on the")
        P_(f"      owner's objective, and the next move is to BUILD or BUY genuinely different")
        P_(f"      information rather than to recombine what already exists.")

    # ---------------- multiplicity, per amendment_1 --------------------------------------
    P_(f"\n=== MULTIPLICITY on this wave's own 60-cell scan (amendment_1) ===")
    cells = []
    for var in REG.columns:
        rk = crank(M[var].values)
        for b in range(NQ):
            hi = ((b + 1) / NQ) if b < NQ - 1 else 1.0001
            m = np.isfinite(rk) & (rk >= b / NQ) & (rk < hi)
            for e in ("2006-2021", "2022-2026"):
                mm = m & (M["era"].values == e)
                if mm.sum() >= 20:
                    cells.append((mm, e))

    def count_hits(p):
        c = 0
        for mm, _ in cells:
            v = p[mm]
            se = v.std(ddof=1) / np.sqrt(len(v))
            if se > 0 and v.mean() / se >= 1.65:
                c += 1
        return c
    obs = count_hits(pnl)
    rng_ = np.random.default_rng(20260857)
    era_arr = M["era"].values
    perm_counts = []
    for _ in range(500):
        p = pnl.copy()
        for e in ("2006-2021", "2022-2026"):          # permute WITHIN era
            idx = np.flatnonzero(era_arr == e)
            p[idx] = rng_.permutation(p[idx])
        perm_counts.append(count_hits(p))
    perm_counts = np.array(perm_counts)
    P_(f"   {len(cells)} cells with n >= 20. Observed cells at t >= 1.65: {obs}")
    P_(f"   permuted within era: {perm_counts.mean():.1f} on average "
       f"(5th-95th pct {np.percentile(perm_counts,5):.0f}-{np.percentile(perm_counts,95):.0f}), "
       f"p(as many by chance) = {float((perm_counts >= obs).mean()):.3f}")
    P_(f"   -> the quintile structure is "
       + ("MORE than chance produces" if float((perm_counts >= obs).mean()) < 0.05
          else "NOT distinguishable from chance"))

    # ---------------- context: what actually changed between the eras -------------------
    P_(f"\n=== CONTEXT: did these variables actually move between the eras? ===")
    P_(f"{'variable':<18}{'2006-2021 median':>20}{'2022-2026 median':>20}{'ratio':>10}")
    for var in REG.columns:
        a = M.loc[M["era"] == "2006-2021", var].median()
        b_ = M.loc[M["era"] == "2022-2026", var].median()
        P_(f"{var:<18}{a:>20,.4f}{b_:>20,.4f}{(b_/a if a else np.nan):>10.2f}")
    P_(f"\n   B-MOM's friction is 2.872 ticks = $14.36 per round turn at 1 NQ, FIXED in ticks.")
    P_(f"   As a share of the median daily RTH range it was "
       f"{100*14.36/(20*M.loc[M['era']=='2006-2021','R1_range_pts'].median()):.2f} % pre-2022 "
       f"and {100*14.36/(20*M.loc[M['era']=='2022-2026','R1_range_pts'].median()):.2f} % after.")
    P_(f"\n=== STATUS: diagnostic, nothing adopted. ===")
    out.close()
    print(f"done [{_time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
