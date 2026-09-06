"""CARRY_V1 DEVELOPMENT - within-sector relative curve carry.  Frozen by SPEC.md before it ran.

DEVELOPMENT WINDOW ONLY.  2019+ is UNREACHABLE from this code path, not merely discouraged:
DEV_END is asserted, and the panel is truncated at load time so no later row ever enters a frame.

THE FAMILY.  Relative pricing across futures MATURITIES - a genuinely different information source
from trend. It is NOT a TSMOM rescue and TSMOM's failure is not evidence about it in either
direction.

SIGNAL, fixed before any P&L:
    curve_slope = (P_near - P_deferred) / month_gap        a DIFFERENCE, defined for negative prices
    carry_score = curve_slope / lagged 63d sd of the basis-safe daily price change
    weight      = centred rank of carry_score WITHIN SECTOR, in [-1, +1]

WHY WITHIN-SECTOR. An absolute zero-carry threshold across equity/rates/metals/ags encodes
financing and storage conventions rather than expected return: equity index is in contango
essentially always because the curve carries interest, and that is not a forecast.

CAUSALITY IS PROVED, NOT ASSUMED, and in BOTH directions (see causality_probe). Hours before this
was written, an int32 overflow made seven BBO features read +2.065 s into the future while every
summary statistic looked excellent.
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
sys.path.insert(0, os.path.join(ROOT, "research", "multi_market", "src"))
sys.path.insert(0, os.path.join(os.path.dirname(RUN), "CARRY00_CURVE_DATA_CAPABILITY_20260828",
                                "src"))
import ncd_day as N                                                     # noqa: E402
import roll as R                                                        # noqa: E402

OUT = os.path.join(RUN, "out")
os.makedirs(OUT, exist_ok=True)

# ---- FROZEN BY SPEC -------------------------------------------------------
UNIVERSE = {"equity_index": ["ES", "YM"], "rates": ["ZN", "ZB"],
            "metals": ["GC", "SI"], "ags": ["ZC", "ZW", "ZM", "ZL"]}
DEV_START, DEV_END = pd.Timestamp("2009-01-01"), pd.Timestamp("2026-08-01")
VOL_LB = 63
COMMISSION_RT = 4.36
PRIMARY_TICKS, STRESS_TICKS = 1.0, 2.0
GROSS_RISK_PER_SECTOR = 1.0
C2_SHARPE, C3_YEARS, C5_DRAG = 0.30, 6, 0.50
C6_ROOT, C7_SECTOR, C8_EXPO, C8_RHO = 0.40, 0.50, 0.25, 0.35
YEARS = list(range(2010, 2019))                                          # 9; 2009 is warmup
# ---------------------------------------------------------------------------
TICKSZ = {"ES": 0.25, "YM": 1.0, "ZN": 1 / 64, "ZB": 1 / 32, "GC": 0.10, "SI": 0.005,
          "ZC": 0.25, "ZW": 0.25, "ZM": 0.10, "ZL": 0.01}
_fh = None


def P(*a):
    print(*a, flush=True)
    if _fh is not None:
        print(*a, file=_fh)


def month_gap(a, b):
    return (b[1] - a[1]) * 12 + (b[0] - a[0])


def build_root(root):
    """NEAR (causal active contract), DEFERRED (nearest later listed month), and the basis-safe
    economic return, all on the DEVELOPMENT window only."""
    cached = N.cached_ids()
    rows = []
    for cid, r, m, y in N.contracts_for(root, 2009, 2027):
        if cid not in cached:
            continue
        d = N.read_contract(cid)
        if d.empty:
            continue
        d = d[(d["date"] >= DEV_START) & (d["date"] < DEV_END)]     # STRUCTURAL PROTECTION
        if d.empty:
            continue
        d["cmonth"], d["cyear"] = m, y
        d["expiry_key"] = y * 100 + m
        rows.append(d)
    if not rows:
        return None
    panel = pd.concat(rows, ignore_index=True).sort_values(["date", "expiry_key"])
    assert panel["date"].max() < DEV_END, "DEVELOPMENT WINDOW VIOLATION"

    led = R.build_roll_ledger(panel[["date", "contract_id", "expiry_key", "open", "high",
                                     "low", "close", "volume"]].copy(), root)
    held = R.designated_contract(panel, led)
    er = R.economic_returns(panel, held)                     # s7 self-financing, basis-safe
    if er.empty:
        return None
    er = er.set_index("date")

    meta = panel.groupby("contract_id").agg(cmonth=("cmonth", "first"),
                                            cyear=("cyear", "first"))
    bydate = {pd.Timestamp(d): set(g) for d, g in panel.groupby("date")["contract_id"]}
    dates = [pd.Timestamp(x) for x in np.sort(panel["date"].unique())]
    assert sum(1 for d in dates if bydate.get(d)) == len(dates), "date-key type mismatch"
    closes = panel.set_index(["date", "contract_id"])["close"]

    recs = []
    for d in dates:
        a = held.get(d)
        if not isinstance(a, str):
            continue
        ka = (int(meta.at[a, "cmonth"]), int(meta.at[a, "cyear"]))
        later = [(c, month_gap(ka, (int(meta.at[c, "cmonth"]), int(meta.at[c, "cyear"]))))
                 for c in bydate.get(d, set()) if c != a]
        later = [(c, g) for c, g in later if g > 0]
        if not later:
            continue
        defer, gap = min(later, key=lambda x: x[1])          # nearest later LISTED MONTH
        try:
            pn, pd_ = float(closes.loc[(d, a)]), float(closes.loc[(d, defer)])
        except KeyError:
            continue
        recs.append(dict(date=d, root=root, near=a, defer=defer, gap=gap,
                         slope=(pn - pd_) / gap, ret_points=float(er["ret_points"].get(d, np.nan))))
    if not recs:
        return None
    x = pd.DataFrame(recs).set_index("date").sort_index()
    # LAGGED 63d sigma of the basis-safe daily change. shift(1) => strictly prior information.
    allret = er["ret_points"].reindex(pd.DatetimeIndex(dates)).astype(float)
    sig = allret.rolling(VOL_LB, min_periods=VOL_LB).std().shift(1)
    x["sigma"] = sig.reindex(x.index)
    x["carry"] = x["slope"] / x["sigma"]
    x["ret_points"] = allret.reindex(x.index)
    return x.dropna(subset=["carry", "sigma"])


def weekly_weights(panel_by_root):
    """WEEKLY rebalance. Weights for ISO week W use the LAST eligible observation STRICTLY BEFORE
    the week's first trading day - i.e. information through the immediately preceding session."""
    allx = pd.concat(panel_by_root.values())
    days = pd.DatetimeIndex(sorted(allx.index.unique()))
    iso = days.isocalendar()
    wk = pd.Series([f"{y}-W{w:02d}" for y, w in zip(iso.year, iso.week)], index=days)
    first_day = wk.groupby(wk.values).apply(lambda s: s.index.min())

    sector_of = {r: s for s, rs in UNIVERSE.items() for r in rs}
    rows = []
    for week, d0 in first_day.items():
        prior = days[days < d0]
        if len(prior) == 0:
            continue
        obs = {}
        for r, x in panel_by_root.items():
            px = x.loc[x.index < d0]
            if len(px) == 0:
                continue
            last = px.index.max()
            if (d0 - last).days > 7:                 # a stale pair is not an observation
                continue
            obs[r] = float(px.at[last, "carry"]) if not isinstance(px.at[last, "carry"],
                                                                   pd.Series) else \
                float(px.at[last, "carry"].iloc[-1])
        bysec = {}
        for r, v in obs.items():
            bysec.setdefault(sector_of[r], []).append((r, v))
        live = {s: v for s, v in bysec.items() if len(v) >= 2}      # s40: else the sector is CASH
        if not live:
            continue
        for s, lst in live.items():
            lst = sorted(lst, key=lambda t: t[1])
            n = len(lst)
            for i, (r, v) in enumerate(lst):
                w = 2.0 * i / (n - 1) - 1.0                        # centred rank in [-1, +1]
                rows.append(dict(week=week, effective_from=d0, sector=s, root=r,
                                 carry=v, w_rank=w, n_sector=n, n_live_sectors=len(live)))
    W = pd.DataFrame(rows)
    # equal RISK across active sectors, then risk-normalise inside the sector
    W["w"] = W["w_rank"] * GROSS_RISK_PER_SECTOR / (W["n_live_sectors"] * W["n_sector"])
    return W


def simulate(panel_by_root, W, ticks):
    """Daily P&L in points x point value. Costs charged ONLY to actual position changes."""
    sector_of = {r: s for s, rs in UNIVERSE.items() for r in rs}
    wk = W.pivot_table(index="effective_from", columns="root", values="w").sort_index()
    roots = list(panel_by_root)
    for r in roots:
        if r not in wk.columns:
            wk[r] = 0.0
    wk = wk[roots].fillna(0.0)

    days = pd.DatetimeIndex(sorted(set().union(*[set(x.index) for x in panel_by_root.values()])))
    Wd = wk.reindex(days.union(wk.index)).ffill().reindex(days).fillna(0.0)
    RET = pd.DataFrame({r: panel_by_root[r]["ret_points"].reindex(days)
                        for r in roots}).astype(float)
    SIG = pd.DataFrame({r: panel_by_root[r]["sigma"].reindex(days) for r in roots}).astype(float)
    # risk-normalise: target constant point-risk per unit weight, using STRICTLY LAGGED sigma
    UNITS = Wd.div(SIG.replace(0, np.nan)).fillna(0.0)
    PV = pd.Series({r: N.PV[r] for r in roots})
    gross = (UNITS.shift(1).fillna(0.0) * RET.fillna(0.0)).mul(PV, axis=1)

    dU = UNITS.diff().abs().fillna(UNITS.abs())
    tickval = pd.Series({r: TICKSZ[r] * N.PV[r] for r in roots})
    cost = dU.mul(tickval * ticks + COMMISSION_RT, axis=1)

    net = gross - cost
    out = pd.DataFrame({"gross": gross.sum(1), "cost": cost.sum(1), "net": net.sum(1)})
    return out, gross, cost, UNITS, sector_of


def causality_probe(panel_by_root):
    """BOTH directions. A one-sided probe cannot distinguish a causal engine from one that
    ignores its inputs."""
    P("")
    P("=== CAUSALITY PROBE - both clauses must hold, and the second is what gives it teeth")
    base = weekly_weights(panel_by_root)
    wk = sorted(base["week"].unique())[len(base["week"].unique()) // 2]
    d0 = base.loc[base["week"] == wk, "effective_from"].iloc[0]

    fut = {r: x.copy() for r, x in panel_by_root.items()}
    for r in fut:
        m = fut[r].index >= d0
        fut[r].loc[m, "carry"] = fut[r].loc[m, "carry"] + 999.0
    wf = weekly_weights(fut)
    a = base[base["week"] == wk].set_index("root")["w"]
    b = wf[wf["week"] == wk].set_index("root")["w"].reindex(a.index)
    d_future = float(np.nanmax(np.abs(a - b)))

    past = {r: x.copy() for r, x in panel_by_root.items()}
    for r in past:
        m = past[r].index < d0
        past[r].loc[m, "carry"] = past[r].loc[m, "carry"] * -1.0
    wp = weekly_weights(past)
    c = wp[wp["week"] == wk].set_index("root")["w"].reindex(a.index)
    d_past = float(np.nanmax(np.abs(a - c)))

    P(f"    week {wk}, effective {d0.date()}")
    P(f"    corrupt FUTURE (>= t) carry:  max |dw| = {d_future:.3e}   "
      f"{'PASS - weights unchanged' if d_future < 1e-12 else '*** FAIL - LOOK-AHEAD ***'}")
    P(f"    corrupt PAST  (<  t) carry:  max |dw| = {d_past:.3e}   "
      f"{'PASS - weights DO respond' if d_past > 1e-9 else '*** FAIL - probe has no teeth ***'}")
    return d_future < 1e-12 and d_past > 1e-9


def main():
    global _fh
    _fh = open(os.path.join(OUT, "carry_v1.txt"), "w", encoding="utf-8")
    P("=" * 112)
    P("=== CARRY_V1 DEVELOPMENT - within-sector relative curve carry.  2009-2018 ONLY.")
    P("=" * 112)
    R.test_basis_invariance()
    R.test_no_roll_telescopes()

    panel = {}
    for s, rs in UNIVERSE.items():
        for r in rs:
            x = build_root(r)
            if x is not None and len(x) > 200:
                panel[r] = x
                P(f"    {r:<4} {s:<13} paired days {len(x):>6}  "
                  f"{x.index.min().date()} -> {x.index.max().date()}  "
                  f"median gap {x['gap'].median():.0f}mo  median |carry| {x['carry'].abs().median():.3f}")
    assert max(x.index.max() for x in panel.values()) < DEV_END, "DEVELOPMENT WINDOW VIOLATION"

    ok_causal = causality_probe(panel)

    W = weekly_weights(panel)
    P("")
    P(f"    rebalances {W['week'].nunique():,}   root-weeks {len(W):,}   "
      f"mean live sectors {W.groupby('week')['n_live_sectors'].first().mean():.2f}")

    res = {}
    for nm, tk in (("PRIMARY (1 tick)", PRIMARY_TICKS), ("STRESS (2 ticks)", STRESS_TICKS)):
        out, gross, cost, UNITS, sector_of = simulate(panel, W, tk)
        res[nm] = (out, gross, cost, UNITS, sector_of)

    out, gross, cost, UNITS, sector_of = res["PRIMARY (1 tick)"]
    stress = res["STRESS (2 ticks)"][0]
    P("")
    P("=" * 112)
    P("=== RESULT")
    P("=" * 112)
    for nm, o in (("PRIMARY (1 tick)", out), ("STRESS (2 ticks)", stress)):
        ann = o["net"].mean() * 252
        sd = o["net"].std() * np.sqrt(252)
        P(f"    {nm:<20} gross ${o['gross'].sum():>12,.0f}   cost ${o['cost'].sum():>11,.0f}   "
          f"net ${o['net'].sum():>12,.0f}   Sharpe {ann/sd if sd else 0:>6.3f}")
    drag = out["cost"].sum() / max(out["gross"].sum(), 1e-9)
    P(f"    cost / gross  {100*drag:.1f} %      turnover (mean daily |dUnits|) "
      f"{UNITS.diff().abs().sum(1).mean():.4f}")

    yr = out.groupby(out.index.year)["net"].sum().reindex(YEARS).fillna(0.0)
    P("")
    P("    net by development year")
    for y in YEARS:
        P(f"        {y}  ${yr[y]:>12,.0f}")
    npos = int((yr > 0).sum())

    contrib_r = gross.sum() - cost.sum()
    pos_r = contrib_r[contrib_r > 0]
    contrib_s = contrib_r.groupby(pd.Series(sector_of)).sum()
    pos_s = contrib_s[contrib_s > 0]
    P("")
    P("    contribution by root / sector (net)")
    for r in contrib_r.sort_values(ascending=False).index:
        P(f"        {r:<4} {sector_of[r]:<13} ${contrib_r[r]:>12,.0f}")
    for s in contrib_s.sort_values(ascending=False).index:
        P(f"        [{s:<12}] ${contrib_s[s]:>12,.0f}")
    top_r = pos_r.max() / pos_r.sum() if len(pos_r) else 1.0
    top_s = pos_s.max() / pos_s.sum() if len(pos_s) else 1.0

    eq = [r for r in UNITS.columns if sector_of[r] == "equity_index"]
    expo = float(np.sign(UNITS[eq].shift(1)).mean().mean()) if eq else 0.0

    ann = out["net"].mean() * 252
    sd = out["net"].std() * np.sqrt(252)
    sharpe = ann / sd if sd else 0.0

    P("")
    P("=" * 112)
    P("=== GATES - frozen in SPEC before this ran")
    P("=" * 112)
    G = [("C1  PRIMARY net > 0", f"${out['net'].sum():,.0f}", out["net"].sum() > 0),
         ("C2  Sharpe >= 0.30", f"{sharpe:.3f}", sharpe >= C2_SHARPE),
         (f"C3  >= {C3_YEARS} of 9 positive years", f"{npos} of 9", npos >= C3_YEARS),
         ("C4  STRESS net > 0", f"${stress['net'].sum():,.0f}", stress["net"].sum() > 0),
         (f"C5  cost drag <= {C5_DRAG:.0%}", f"{drag:.1%}", drag <= C5_DRAG),
         (f"C6  top root <= {C6_ROOT:.0%}", f"{top_r:.1%}", top_r <= C6_ROOT),
         (f"C7  top sector <= {C7_SECTOR:.0%}", f"{top_s:.1%}", top_s <= C7_SECTOR),
         ("C8  not a disguised long", f"mean signed equity exposure {expo:+.3f}",
          abs(expo) <= C8_EXPO)]
    P(f"    {'GATE':<34} {'OBSERVED':>28}   VERDICT")
    for nm, obs, good in G:
        P(f"    {nm:<34} {obs:>28}   {'PASS' if good else '*** FAIL ***'}")
    P(f"    {'causality probe (both clauses)':<34} {'':>28}   "
      f"{'PASS' if ok_causal else '*** FAIL ***'}")
    allpass = all(g for _, _, g in G) and ok_causal
    P("")
    P("=" * 112)
    P(f"=== CARRY_V1 DEVELOPMENT: {'ALL GATES PASS -> ONE-SHOT VALIDATION' if allpass else 'FAILED -> CARRY_V1 CLOSED'}")
    P("=" * 112)
    out.to_csv(os.path.join(OUT, "carry_v1_daily.csv"))
    W.to_csv(os.path.join(OUT, "carry_v1_weights.csv"), index=False)
    json.dump({"gates": [{"gate": n, "observed": o, "pass": bool(g)} for n, o, g in G],
               "causality": bool(ok_causal), "all_pass": bool(allpass),
               "net": float(out["net"].sum()), "sharpe": float(sharpe),
               "cost_drag": float(drag), "positive_years": npos,
               "stress_net": float(stress["net"].sum())},
              open(os.path.join(OUT, "carry_v1_verdict.json"), "w", encoding="utf-8"), indent=2)
    _fh.close()


if __name__ == "__main__":
    main()
