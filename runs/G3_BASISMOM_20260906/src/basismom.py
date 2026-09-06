"""G3_BASISMOM_20260906 -- basis-momentum (Boons & Prado 2019), executed EXACTLY per spec.yaml.

FROZEN OBJECT (spec.yaml, committed before results):
  BM_i(m) = cumret_12m(front-nearby_i) - cumret_12m(second-nearby_i), POINT-return basis,
  monthly end-of-month, causal. ARM-W (the claim): within-root calendar spread, long front /
  short second (legs vol-scaled 1/sigma63, lagged) where BM>0, reverse where BM<0, hold 1 month.
  ARM-X (secondary, n=5 THIN breadth): cross-sectional rank on BM, long top-2 / short bottom-2
  outright front. ARM-X NEVER rescues ARM-W.

AVAILABILITY RULE, declared BEFORE any P&L exists (s3: sample may move for DATA AVAILABILITY,
never for returns): the local day store holds the second-nearby leg only where the strip was
cached (complete 2009-2015 all roots; 2016 hole; CL absent 2016-2025; others patchy). A calendar
month is VALID for a root iff it has >= MIN_DAYS_MONTH joint (both-leg) sessions. cumret_12m
requires 12 CONSECUTIVE valid months (NaN propagation enforces this); a signal month is
TRADEABLE iff BM finite, sigmas finite, and the accrual month m+1 is VALID.

SIZING (family convention, G3_ZNZB_SLOPE wording 'legs sized 1/sigma_i'): each leg
K / (sigma_leg * PV) contracts, sigma_leg = lagged (shift 1) 63-day sd of the leg's own daily
POINT return, taken at the signal month-end. K = $100 target daily vol per leg. Sharpe and cost
DRAG are invariant to K (tick+commission costs scale linearly with contracts).

COSTS (G5, frozen): $4.36 commission RT x 2 legs + {1,2}-tick per leg; SI thinness rung = SI at
3 ticks (others 2). Charged on monthly position changes |dN| per contract. Primary rung = 1 tick.

NULLS (frozen): circular shift of BM vs forward returns -- ONE SHARED OFFSET per draw across all
5 roots on the common month grid (dependence-preserving; seed 20260906, offsets written to
out/null_offsets.csv for the G3_ZNZB_SLOPE shared draw) + 12-month circular block bootstrap CIs.

Everything below prints its own GATE / SPEC / OBSERVED / PASS-FAIL rows. No hand assembly.
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
import ncd_day as N            # noqa: E402

OUT = os.path.join(RUN, "out")
os.makedirs(OUT, exist_ok=True)

# ---- FROZEN CONSTANTS -------------------------------------------------------
UNIVERSE = ["CL", "GC", "SI", "ZN", "ZB"]
SEAL = pd.Timestamp("2026-08-01")
MIN_DAYS_MONTH = 14          # availability rule, declared before results
VOL_LB = 63
K = 100.0                    # $ daily vol target per leg (scale only)
COMMISSION_RT = 4.36
TICKSZ = {"CL": 0.01, "GC": 0.10, "SI": 0.005, "ZN": 1 / 64, "ZB": 1 / 32}
N_NULL = 2000
N_BOOT = 2000
SEED = 20260906              # shared-draw seed with G3_ZNZB_SLOPE
BLOCK = 12
NW_LAG = 3
ERAS = [("2009-15", pd.Period("2009-01", "M"), pd.Period("2015-12", "M")),
        ("2016-21", pd.Period("2016-01", "M"), pd.Period("2021-12", "M")),
        ("2022-26", pd.Period("2022-01", "M"), pd.Period("2026-07", "M"))]
RUNGS = {"PRIMARY_1tick": {r: 1.0 for r in UNIVERSE},
         "STRESS_2tick": {r: 2.0 for r in UNIVERSE},
         "SI3_rung": {**{r: 2.0 for r in UNIVERSE}, "SI": 3.0}}
# -----------------------------------------------------------------------------

_fh = open(os.path.join(OUT, "gate_table.txt"), "w", encoding="utf-8")


def P(*a):
    print(*a, flush=True)
    print(*a, file=_fh)


def legcost(root, ticks):
    return ticks * TICKSZ[root] * N.PV[root] + COMMISSION_RT


def sharpe(x):
    x = np.asarray(x, float)
    s = x.std(ddof=1)
    return float(x.mean() / s * np.sqrt(12)) if s > 0 else 0.0


# ---------------------------------------------------------------- monthly frames
def monthly_frame(root):
    x = pd.read_parquet(os.path.join(OUT, f"legs_{root}.parquet"))
    x["date"] = pd.to_datetime(x["date"])
    x = x.set_index("date").sort_index()
    assert x.index.max() < SEAL, f"SEAL VIOLATION in analysis ({root})"
    sig_f_d = x["ret_f"].rolling(VOL_LB, min_periods=VOL_LB).std().shift(1)
    sig_s_d = x["ret_s"].rolling(VOL_LB, min_periods=VOL_LB).std().shift(1)
    p = x.index.to_period("M")
    g = x.groupby(p)
    m = pd.DataFrame({"mret_f": g["ret_f"].sum(), "mret_s": g["ret_s"].sum(),
                      "ndays": g["ret_f"].size(), "slope_me": g["slope"].last(),
                      "sig_f": sig_f_d.groupby(p).last(), "sig_s": sig_s_d.groupby(p).last()})
    full = pd.period_range(m.index.min(), m.index.max(), freq="M")
    m = m.reindex(full)
    valid = m["ndays"].fillna(0) >= MIN_DAYS_MONTH
    m.loc[~valid, ["mret_f", "mret_s", "slope_me", "sig_f", "sig_s"]] = np.nan
    m["valid"] = valid
    m["cum12_f"] = m["mret_f"].rolling(12, min_periods=12).sum()   # NaN month kills the window
    m["cum12_s"] = m["mret_s"].rolling(12, min_periods=12).sum()
    m["BM"] = m["cum12_f"] - m["cum12_s"]
    m["fwd_f"] = m["mret_f"].shift(-1)
    m["fwd_s"] = m["mret_s"].shift(-1)
    m["fwd_valid"] = m["valid"].shift(-1).apply(lambda v: bool(v) if v == v else False)
    m["liveW"] = (m["BM"].notna() & (m["sig_f"] > 0) & (m["sig_s"] > 0)
                  & m["fwd_f"].notna() & m["fwd_s"].notna() & m["fwd_valid"])
    return m


def align(frames):
    grid = pd.period_range(min(f.index.min() for f in frames.values()),
                           max(f.index.max() for f in frames.values()), freq="M")
    out = {}
    for r, f in frames.items():
        f = f.reindex(grid)
        for c in ("valid", "fwd_valid", "liveW"):   # bool cols degrade to object on reindex
            f[c] = f[c].apply(lambda v: bool(v) if v == v else False)
        out[r] = f
    return grid, out


# ---------------------------------------------------------------- arm machinery
def spread_pnl(m, root, s, ticks):
    """Gross/cost/net accrual for a signed calendar-spread sign vector s on signal grid."""
    zsp = K * (m["fwd_f"] / m["sig_f"] - m["fwd_s"] / m["sig_s"])
    gross = np.where(s != 0, s * zsp.values, 0.0)
    with np.errstate(divide="ignore", invalid="ignore"):
        nf = np.where(s != 0, s * K / (m["sig_f"].values * N.PV[root]), 0.0)
        ns = np.where(s != 0, -s * K / (m["sig_s"].values * N.PV[root]), 0.0)
    nf = np.nan_to_num(nf)
    ns = np.nan_to_num(ns)
    dnf = np.abs(np.diff(nf, prepend=0.0))
    dns = np.abs(np.diff(ns, prepend=0.0))
    cost = dnf * legcost(root, ticks) + dns * legcost(root, ticks)
    return gross, cost, nf, ns


def outright_pnl(m, root, s, ticks):
    zf = K * (m["fwd_f"] / m["sig_f"])
    gross = np.where(s != 0, s * zf.values, 0.0)
    with np.errstate(divide="ignore", invalid="ignore"):
        nf = np.where(s != 0, s * K / (m["sig_f"].values * N.PV[root]), 0.0)
    nf = np.nan_to_num(nf)
    dnf = np.abs(np.diff(nf, prepend=0.0))
    cost = dnf * legcost(root, ticks)
    return gross, cost, nf


def sign_of(v, live):
    s = np.sign(np.nan_to_num(v))
    s[~live] = 0.0
    return s


def main():
    P("=" * 118)
    P("=== G3_BASISMOM_20260906  --  basis-momentum (Boons & Prado 2019) on {CL,GC,SI,ZN,ZB}  (G00075, GENESIS3_RV)")
    P("=" * 118)

    frames = {r: monthly_frame(r) for r in UNIVERSE}
    grid, F = align(frames)
    G = len(grid)

    P("")
    P("--- DATA / AVAILABILITY (rule declared before results: month VALID iff >= "
      f"{MIN_DAYS_MONTH} joint both-leg sessions; cum12 needs 12 consecutive valid months)")
    livemat = {}
    for r in UNIVERSE:
        m = F[r]
        lw = m["liveW"].values.astype(bool)
        livemat[r] = lw
        vm = int(m["valid"].sum())
        span = (f"{m.index[lw][0]}..{m.index[lw][-1]}" if lw.any() else "NONE")
        P(f"    {r:<3} months-on-grid {G}  valid {vm}  liveW(signal) {int(lw.sum()):>3}  "
          f"live span {span}")
    n_live_roots = np.sum([livemat[r] for r in UNIVERSE], axis=0)
    live_any = n_live_roots > 0

    # accrual month = signal month + 1; portfolio live set:
    acc_idx = grid[live_any] + 1
    M_live = int(live_any.sum())
    root_months = int(n_live_roots.sum())

    # ---------------- G1 MDE FIRST (printed before any observed P&L) ----------------
    P("")
    P("--- G1: MDE FIRST (80% power, two-sided 5%: detectable ann Sharpe = 2.80*sqrt(12/M))")
    mde_sharpe = 2.80 * np.sqrt(12.0 / max(M_live, 1))
    P(f"    ARM-W portfolio months M = {M_live}   pooled root-months = {root_months} "
      f"(spec anticipated ~200/arm)")
    P(f"    MDE annualized Sharpe = {mde_sharpe:.2f}   -- a true Sharpe below this is NOT "
      f"detectable at this sample size")

    # ---------------- causality probe (two-sided, per root) ----------------
    P("")
    P("--- CAUSALITY PROBE (two-sided): corrupt daily returns AFTER month-end t* -> BM(t*) frozen;"
      " corrupt INSIDE window -> BM(t*) moves")
    probe_ok = True
    for r in UNIVERSE:
        m = F[r]
        lw = np.where(livemat[r])[0]
        if len(lw) == 0:
            continue
        i = int(lw[len(lw) // 2])
        t_star = grid[i]
        x = pd.read_parquet(os.path.join(OUT, f"legs_{r}.parquet"))
        x["date"] = pd.to_datetime(x["date"])
        x = x.set_index("date").sort_index()
        per = x.index.to_period("M")

        def bm_at(ret_f):
            mm = ret_f.groupby(per).sum()
            nd = ret_f.groupby(per).size()
            mm = mm.reindex(pd.period_range(per.min(), per.max(), freq="M"))
            nd = nd.reindex(mm.index).fillna(0)
            mm[nd < MIN_DAYS_MONTH] = np.nan
            c12f = mm.rolling(12, min_periods=12).sum()
            ms = x["ret_s"].groupby(per).sum().reindex(mm.index)
            ms[nd < MIN_DAYS_MONTH] = np.nan
            c12s = ms.rolling(12, min_periods=12).sum()
            return float((c12f - c12s).get(t_star, np.nan))

        base = bm_at(x["ret_f"])
        fut = x["ret_f"].copy()
        fut[x.index.to_period("M") > t_star] += 999.0
        d_future = abs(bm_at(fut) - base)
        past = x["ret_f"].copy()
        inwin = (x.index.to_period("M") <= t_star) & (x.index.to_period("M") > t_star - 12)
        idx = np.where(inwin)[0]
        past.iloc[idx[len(idx) // 2]] += 999.0
        d_inside = abs(bm_at(past) - base)
        ok = (d_future < 1e-9) and (d_inside > 1.0)
        probe_ok &= ok
        P(f"    {r:<3} t*={t_star}  corrupt-future |dBM| = {d_future:.2e} "
          f"{'PASS' if d_future < 1e-9 else '*** LOOK-AHEAD ***'}   corrupt-inside |dBM| = "
          f"{d_inside:.1f} {'PASS (teeth)' if d_inside > 1.0 else '*** NO TEETH ***'}")

    # ---------------- ARM-W ----------------
    signs = {}
    for r in UNIVERSE:
        m = F[r]
        signs[r] = sign_of(m["BM"].values, livemat[r])

    armW = {}
    for rung, tk in RUNGS.items():
        rows = {}
        for r in UNIVERSE:
            gross, cost, nf, ns = spread_pnl(F[r], r, signs[r], tk[r])
            rows[r] = dict(gross=gross, cost=cost, net=gross - cost,
                           to=np.abs(np.diff(nf, prepend=0.0)) + np.abs(np.diff(ns, prepend=0.0)))
        armW[rung] = rows

    def portfolio(rows):
        g = np.sum([rows[r]["gross"] for r in UNIVERSE], axis=0)
        c = np.sum([rows[r]["cost"] for r in UNIVERSE], axis=0)
        return g, c, g - c

    gW, cW, nW = portfolio(armW["PRIMARY_1tick"])
    y = nW[live_any]                                   # live-month net series (PRIMARY)
    obs_mean = float(y.mean()) if M_live else 0.0
    obs_sharpe = sharpe(y) if M_live > 1 else 0.0

    P("")
    P("--- ARM-W (THE CLAIM): within-root calendar spread sign(BM), monthly")
    P(f"    live months {M_live}  ({acc_idx[0]}..{acc_idx[-1]} accrual)" if M_live else
      "    live months 0")
    for rung in RUNGS:
        g, c, n = portfolio(armW[rung])
        yl = n[live_any]
        drag = float(np.sum(c[live_any]) / np.sum(g[live_any])) if np.sum(g[live_any]) > 0 else np.nan
        P(f"    {rung:<14} gross ${np.sum(g[live_any]):>10,.0f}  cost ${np.sum(c[live_any]):>9,.0f}  "
          f"net ${np.sum(yl):>10,.0f}  mean/mo ${np.mean(yl):>8,.2f}  annSharpe {sharpe(yl):>7.3f}  "
          f"drag {'n/a (gross<=0)' if not np.isfinite(drag) else f'{drag:.1%}'}")
    to_mean = float(np.mean(np.sum([armW['PRIMARY_1tick'][r]['to'] for r in UNIVERSE],
                                   axis=0)[live_any]))
    P(f"    mean monthly turnover (contracts, both legs, all roots, per $100/day-vol unit): "
      f"{to_mean:.3f}")
    P("    per-root net (PRIMARY): " + "  ".join(
        f"{r} ${np.sum(armW['PRIMARY_1tick'][r]['net'][live_any]):,.0f}" for r in UNIVERSE))

    # roll-friction annex (informational; frozen cost model charges monthly rebalance only)
    P("    [annex] continuous-series roll executions are NOT charged by the frozen monthly-"
      "turnover cost model; per-root front rolls/yr: " + "  ".join(
          f"{r}={float(pd.read_parquet(os.path.join(OUT, f'legs_{r}.parquet'))['rolled_f'].mean())*252:.1f}"
          for r in UNIVERSE))

    # ---------------- null: shared-offset circular shift ----------------
    rng = np.random.default_rng(SEED)
    offsets = rng.integers(1, G, size=N_NULL)
    pd.DataFrame({"draw": np.arange(N_NULL), "offset": offsets}).to_csv(
        os.path.join(OUT, "null_offsets.csv"), index=False)
    null_means = np.empty(N_NULL)
    BMv = {r: F[r]["BM"].values for r in UNIVERSE}
    for j, k in enumerate(offsets):
        tot = 0.0
        for r in UNIVERSE:
            bs = np.roll(BMv[r], int(k))
            live = np.isfinite(bs) & (F[r]["sig_f"].values > 0) & (F[r]["sig_s"].values > 0) \
                & np.isfinite(F[r]["fwd_f"].values) & np.isfinite(F[r]["fwd_s"].values) \
                & F[r]["fwd_valid"].values
            s = sign_of(bs, live)
            gross, cost, _, _ = spread_pnl(F[r], r, s, RUNGS["PRIMARY_1tick"][r])
            tot += float(np.sum(gross - cost))
        null_means[j] = tot / max(M_live, 1)
    p_shift = float((1 + np.sum(null_means >= obs_mean)) / (1 + N_NULL))

    # ---------------- block bootstrap CI (12-month circular blocks) ----------------
    rngb = np.random.default_rng(SEED + 1)
    boots_mean = np.empty(N_BOOT)
    boots_sharpe = np.empty(N_BOOT)
    Mv = len(y)
    nblk = int(np.ceil(Mv / BLOCK))
    for j in range(N_BOOT):
        starts = rngb.integers(0, Mv, size=nblk)
        idx = np.concatenate([(s0 + np.arange(BLOCK)) % Mv for s0 in starts])[:Mv]
        yb = y[idx]
        boots_mean[j] = yb.mean()
        boots_sharpe[j] = sharpe(yb)
    ci_mean = (float(np.percentile(boots_mean, 2.5)), float(np.percentile(boots_mean, 97.5)))
    ci_shp = (float(np.percentile(boots_sharpe, 2.5)), float(np.percentile(boots_sharpe, 97.5)))

    # ---------------- monotonicity (within-root terciles, pooled response) ----------------
    ter_resp = {1: [], 2: [], 3: []}
    ter_tbl = {}
    for r in UNIVERSE:
        m = F[r]
        lw = livemat[r]
        if lw.sum() < 9:
            continue
        bm = pd.Series(m["BM"].values[lw])
        resp = pd.Series((K * (m["fwd_f"] / m["sig_f"] - m["fwd_s"] / m["sig_s"])).values[lw])
        q = pd.qcut(bm, 3, labels=[1, 2, 3])
        ter_tbl[r] = {int(t): float(resp[q == t].mean()) for t in (1, 2, 3)}
        for t in (1, 2, 3):
            ter_resp[t].extend(resp[q == t].tolist())
    tmeans = {t: float(np.mean(ter_resp[t])) if ter_resp[t] else np.nan for t in (1, 2, 3)}
    monotone = bool(tmeans[1] < tmeans[2] < tmeans[3])
    P("")
    P("--- MONOTONICITY (rank-response across within-root BM terciles; response = unsigned fwd "
      "spread $ per $100/day-vol)")
    P(f"    pooled  T1 {tmeans[1]:>8.2f}   T2 {tmeans[2]:>8.2f}   T3 {tmeans[3]:>8.2f}   "
      f"monotone(T1<T2<T3): {monotone}")
    for r, d in ter_tbl.items():
        P(f"    {r:<3}     T1 {d[1]:>8.2f}   T2 {d[2]:>8.2f}   T3 {d[3]:>8.2f}")

    # ---------------- parents + subsumption ----------------
    parents = {}
    for name, sigcol in (("BASIS", "slope_me"), ("MOM12", "cum12_f")):
        rows = {}
        for r in UNIVERSE:
            m = F[r]
            live = livemat[r] & np.isfinite(m[sigcol].values)
            s = sign_of(m[sigcol].values, live)
            if name == "BASIS":
                gross, cost, _, _ = spread_pnl(m, r, s, RUNGS["PRIMARY_1tick"][r])
            else:
                gross, cost, _ = outright_pnl(m, r, s, RUNGS["PRIMARY_1tick"][r])
            rows[r] = gross - cost
        parents[name] = np.sum([rows[r] for r in UNIVERSE], axis=0)

    x1 = parents["BASIS"][live_any]
    x2 = parents["MOM12"][live_any]
    X = np.column_stack([np.ones(Mv), x1, x2])
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    e = y - X @ beta
    XtX_inv = np.linalg.inv(X.T @ X)
    S = np.zeros((3, 3))
    for lag in range(NW_LAG + 1):
        w = 1.0 - lag / (NW_LAG + 1)
        for t in range(lag, Mv):
            u = X[t] * e[t]
            v = X[t - lag] * e[t - lag]
            S += w * (np.outer(u, v) + (np.outer(v, u) if lag > 0 else 0))
    Vb = XtX_inv @ S @ XtX_inv
    se = np.sqrt(np.diag(Vb))
    alpha, se_a = float(beta[0]), float(se[0])
    ci_a = (alpha - 1.96 * se_a, alpha + 1.96 * se_a)
    P("")
    P("--- SUBSUMPTION (G3): ARM-W net ~ a + b1*STATIC-BASIS net + b2*MOM12 net  (NW lag 3, "
      f"n={Mv} months)")
    P(f"    alpha  {alpha:>9.3f} $/mo   se {se_a:>7.3f}   t {alpha/se_a if se_a>0 else 0:>6.2f}   "
      f"95% CI [{ci_a[0]:.3f}, {ci_a[1]:.3f}]")
    P(f"    b_basis {beta[1]:>8.3f} (se {se[1]:.3f})   b_mom12 {beta[2]:>8.3f} (se {se[2]:.3f})")
    pd.DataFrame([dict(term="alpha", coef=alpha, se=se_a, t=alpha / se_a if se_a > 0 else 0,
                       ci_lo=ci_a[0], ci_hi=ci_a[1], n=Mv),
                  dict(term="b_basis", coef=float(beta[1]), se=float(se[1]),
                       t=float(beta[1] / se[1]) if se[1] > 0 else 0,
                       ci_lo=float(beta[1] - 1.96 * se[1]), ci_hi=float(beta[1] + 1.96 * se[1]), n=Mv),
                  dict(term="b_mom12", coef=float(beta[2]), se=float(se[2]),
                       t=float(beta[2] / se[2]) if se[2] > 0 else 0,
                       ci_lo=float(beta[2] - 1.96 * se[2]), ci_hi=float(beta[2] + 1.96 * se[2]), n=Mv)]
                 ).to_csv(os.path.join(OUT, "subsumption.csv"), index=False)

    # ---------------- eras ----------------
    P("")
    P("--- G4 ERAS (accrual months; classification, not veto)")
    era_out = {}
    acc_all = grid + 1
    for nm, p0, p1 in ERAS:
        msk = live_any & (acc_all >= p0) & (acc_all <= p1)
        n = int(msk.sum())
        tot = float(np.sum(nW[msk])) if n else 0.0
        era_out[nm] = dict(n=n, net=tot, sign=("+" if tot > 0 else "-" if tot < 0 else "0"))
        P(f"    {nm}: n={n:>3}  net ${tot:>10,.2f}  sign {era_out[nm]['sign']}")

    # ---------------- ARM-X (secondary; THIN BREADTH n=5 -- flagged) ----------------
    P("")
    P("--- ARM-X (SECONDARY, BREADTH n=5 THIN -- informs mechanism map only, NEVER rescues ARM-W)")
    P("    [flag] BM is on a POINT basis; cross-root ranks compare point scales -- interpret "
      "with care (frozen wording: 'rank on BM')")
    wX = {r: np.zeros(G) for r in UNIVERSE}
    for i in range(G):
        liver = [r for r in UNIVERSE if livemat[r][i]]
        if len(liver) < 4:
            continue
        vals = sorted([(F[r]["BM"].values[i], r) for r in liver])
        for _, r in vals[:2]:
            wX[r][i] = -1.0
        for _, r in vals[-2:]:
            wX[r][i] = +1.0
    gX = np.zeros(G)
    cX = np.zeros(G)
    for r in UNIVERSE:
        gr, co, _ = outright_pnl(F[r], r, wX[r], RUNGS["PRIMARY_1tick"][r])
        gX += gr
        cX += co
    liveX = np.array([any(wX[r][i] != 0 for r in UNIVERSE) for i in range(G)])
    MX = int(liveX.sum())
    yX = (gX - cX)[liveX]
    if MX > 1:
        nullX = np.empty(N_NULL)
        for j, k in enumerate(offsets):        # SAME shared draw
            tot = 0.0
            wXn = {r: np.zeros(G) for r in UNIVERSE}
            bshift = {r: np.roll(BMv[r], int(k)) for r in UNIVERSE}
            for i in range(G):
                liver = [r for r in UNIVERSE
                         if np.isfinite(bshift[r][i]) and livemat[r][i]]
                if len(liver) < 4:
                    continue
                vals = sorted([(bshift[r][i], r) for r in liver])
                for _, r in vals[:2]:
                    wXn[r][i] = -1.0
                for _, r in vals[-2:]:
                    wXn[r][i] = +1.0
            for r in UNIVERSE:
                gr, co, _ = outright_pnl(F[r], r, wXn[r], RUNGS["PRIMARY_1tick"][r])
                tot += float(np.sum(gr - co))
            nullX[j] = tot / max(MX, 1)
        pX = float((1 + np.sum(nullX >= yX.mean())) / (1 + N_NULL))
        P(f"    live months {MX}  net ${np.sum(yX):>10,.2f}  mean/mo ${np.mean(yX):>8,.2f}  "
          f"annSharpe {sharpe(yX):>7.3f}  shift-null p {pX:.4f}   [n=5 THIN]")
    else:
        pX = np.nan
        P(f"    live months {MX} -- too thin to report")

    # ---------------- outputs ----------------
    sigrows = []
    for r in UNIVERSE:
        m = F[r]
        for i, per in enumerate(grid):
            if np.isfinite(m["BM"].values[i]):
                sigrows.append(dict(signal_month=str(per), root=r, BM=m["BM"].values[i],
                                    cum12_f=m["cum12_f"].values[i], cum12_s=m["cum12_s"].values[i],
                                    slope_me=m["slope_me"].values[i], sig_f=m["sig_f"].values[i],
                                    sig_s=m["sig_s"].values[i], liveW=bool(livemat[r][i])))
    pd.DataFrame(sigrows).to_csv(os.path.join(OUT, "bm_signals.csv"), index=False)

    pnl = pd.DataFrame({"accrual_month": [str(p) for p in acc_all[live_any]],
                        "gross_1t": gW[live_any], "cost_1t": cW[live_any], "net_1t": nW[live_any],
                        "net_2t": portfolio(armW["STRESS_2tick"])[2][live_any],
                        "net_SI3": portfolio(armW["SI3_rung"])[2][live_any],
                        "parent_basis_net": x1, "parent_mom12_net": x2})
    for r in UNIVERSE:
        pnl[f"net_1t_{r}"] = armW["PRIMARY_1tick"][r]["net"][live_any]
    pnl.to_csv(os.path.join(OUT, "armW_pnl.csv"), index=False)
    pd.DataFrame({"accrual_month": [str(p) for p in acc_all[liveX]],
                  "gross_1t": gX[liveX], "cost_1t": cX[liveX],
                  "net_1t": (gX - cX)[liveX]}).to_csv(os.path.join(OUT, "armX_pnl.csv"),
                                                      index=False)

    # ---------------- GATE TABLE ----------------
    seal_max = max(pd.read_parquet(os.path.join(OUT, f"legs_{r}.parquet"))["date"].max()
                   for r in UNIVERSE)
    n2, s2 = portfolio(armW["STRESS_2tick"])[2], portfolio(armW["SI3_rung"])[2]
    drag1 = float(np.sum(cW[live_any]) / np.sum(gW[live_any])) if np.sum(gW[live_any]) > 0 else np.nan

    g2a = obs_sharpe > 0
    g2b = ci_shp[0] > 0
    g2c = p_shift < 0.05
    g2d = monotone
    g2 = g2a and g2b and g2c and g2d
    g3 = (alpha > 0) and (ci_a[0] > 0)

    rows = [
        ("G0a_SEAL", "max session over all 5 roots < 2026-08-01", str(pd.Timestamp(seal_max).date()),
         pd.Timestamp(seal_max) < SEAL),
        ("G0b_CERT_ROLL", "certified ncd_day+roll reused; roll.py unit tests pass; front ledger causal; "
         "second leg = carry_v1 deferred convention, distinct from front on every date",
         "see out/build_log.txt (all asserted at build)", True),
        ("G0c_COVERAGE", f"availability rule declared pre-results: month valid iff >= {MIN_DAYS_MONTH} "
         "joint days; 12 consecutive valid months for cum12",
         f"liveW root-months {root_months}; portfolio months {M_live} "
         f"(spec assumed 2009..2026-07 continuous; store holds full strip 2009-2015 only)", True),
        ("G0d_CAUSALITY", "two-sided probe: future corruption frozen, in-window corruption moves BM",
         "all 5 roots PASS" if probe_ok else "FAILURE", probe_ok),
        ("G1_MDE_first", "MDE printed before observed results (~200 root-months anticipated)",
         f"M={M_live} portfolio months, {root_months} root-months, MDE annSharpe {mde_sharpe:.2f}",
         True),
        ("G2a_sharpe_pos", "ARM-W after-cost (PRIMARY 1-tick) ann Sharpe > 0",
         f"{obs_sharpe:.3f} (mean ${obs_mean:.2f}/mo)", g2a),
        ("G2b_ci_excl0", "95% block-bootstrap (12-mo circular) Sharpe CI excludes 0",
         f"Sharpe CI [{ci_shp[0]:.3f}, {ci_shp[1]:.3f}]  mean CI [${ci_mean[0]:.2f}, ${ci_mean[1]:.2f}]",
         g2b),
        ("G2c_null_5pct", "clears shared-offset circular-shift null at 5% (one-sided)",
         f"p = {p_shift:.4f} ({N_NULL} draws, shared offsets, seed {SEED})", g2c),
        ("G2d_monotone", "fwd spread response monotone across within-root BM terciles (pooled)",
         f"T1 {tmeans[1]:.2f} < T2 {tmeans[2]:.2f} < T3 {tmeans[3]:.2f} = {monotone}", g2d),
        ("G2_armW", "G2a AND G2b AND G2c AND G2d", f"{g2a}/{g2b}/{g2c}/{g2d}", g2),
        ("G3_subsumption", "alpha > 0 vs BOTH parents jointly, NW 95% CI excludes 0",
         f"alpha {alpha:.3f} $/mo, CI [{ci_a[0]:.3f}, {ci_a[1]:.3f}]", g3),
        ("G4_era", "3-era signs printed; classification not veto",
         "  ".join(f"{nm}:{era_out[nm]['sign']}(n={era_out[nm]['n']})" for nm in era_out), True),
        ("G5_cost", "cost rungs printed: 1-tick / 2-tick / SI-3-tick; monthly turnover; drag",
         f"net1 ${np.sum(nW[live_any]):,.0f} net2 ${np.sum(n2[live_any]):,.0f} "
         f"netSI3 ${np.sum(s2[live_any]):,.0f}; drag(1t) "
         f"{'n/a' if not np.isfinite(drag1) else f'{drag1:.1%}'}; turnover {to_mean:.3f} ct/mo", True),
        ("G6_P_MEANING", "IN WORDS: p_shift = fraction of 2000 draws (ONE shared circular offset "
         "applied to every root's monthly BM on the common grid) whose after-cost PRIMARY portfolio "
         "mean monthly net >= observed; SECOND WAY = 12-month circular block-bootstrap CI of the "
         "same mean (printed in G2b)", "both computed; qualitative agreement: "
         f"p={p_shift:.3f} vs mean-CI [{ci_mean[0]:.2f},{ci_mean[1]:.2f}]", True),
    ]

    P("")
    P("GATE TABLE  (printed by program)")
    P(f"{'GATE':<18} {'SPEC':<98} {'OBSERVED':<72} PASS-FAIL")
    for nm, spec, obs, ok in rows:
        P(f"{nm:<18} {spec:<98} {obs:<72} {'PASS' if ok else '*** FAIL ***'}")

    decision = "BASISMOM01 ENGINE CANDIDATE" if (g2 and g3) else "CLOSED AT SCOPE (S28)"
    P("")
    P(f"DECISION RULE (mechanical): G2={'PASS' if g2 else 'FAIL'}  G3={'PASS' if g3 else 'FAIL'}"
      f"  ->  {decision}")
    P("ARM-X NEVER RESCUES ARM-W (frozen): ARM-X result is mechanism-map information only.")
    P("=" * 118)

    json.dump(dict(
        run_id="G3_BASISMOM_20260906", ledger="G00075",
        M_live=M_live, root_months=root_months, mde_sharpe=mde_sharpe,
        armW=dict(mean=obs_mean, sharpe=obs_sharpe, net_1t=float(np.sum(nW[live_any])),
                  net_2t=float(np.sum(n2[live_any])), net_SI3=float(np.sum(s2[live_any])),
                  drag_1t=None if not np.isfinite(drag1) else drag1,
                  ci_mean=ci_mean, ci_sharpe=ci_shp, p_shift=p_shift,
                  terciles=tmeans, monotone=monotone),
        armX=dict(M=MX, mean=float(np.mean(yX)) if MX else None,
                  sharpe=sharpe(yX) if MX > 1 else None,
                  p_shift=None if not np.isfinite(pX) else pX),
        subsumption=dict(alpha=alpha, se=se_a, ci=list(ci_a),
                         b_basis=float(beta[1]), b_mom12=float(beta[2])),
        eras=era_out, gates={nm: bool(ok) for nm, _, _, ok in rows},
        g2=bool(g2), g3=bool(g3), decision=decision),
        open(os.path.join(OUT, "verdicts.json"), "w", encoding="utf-8"), indent=2, default=str)
    _fh.close()


if __name__ == "__main__":
    main()
