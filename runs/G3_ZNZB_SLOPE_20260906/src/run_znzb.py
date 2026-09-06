"""G3_ZNZB_SLOPE_20260906 driver — preferred-habitat / term-premium carry expressed
duration-neutral on the ZN/ZB pair.  Executes spec.yaml EXACTLY (frozen before results).

FROZEN OBJECT (spec.yaml): weekly ISO rebalance, decision = last observation strictly
before the week's first trading day; carry_i = (P_near - P_deferred)/month_gap / sigma_i
for i in {ZN, ZB} — the CARRY_V1 construction VERBATIM (causal volume-crossover near
contract, 5-day pre-expiry buffer, sigma = lagged 63d sd of daily point change);
LONG the carry-richer root, SHORT the other, legs 1/sigma_i; no threshold, always in,
zero free parameters.

The construction module carry_znzb.py = carry_v1.py + exactly two mechanical changes
(contract load range 2009-2027; window constants 2009-01-01 / 2026-08-01).  Any other
diff => INVALID-RUN, asserted below (the CARRY_SIGC_CONFIRM diff-audit pattern).

GATES (spec.yaml, decision rule mechanical):
  G1  MDE printed BEFORE observed (~910 weeks)
  G2  after-cost weekly mean > 0, CI excludes 0, clears circular-shift null at 5%
  G3  reduce-to-outright control: positive alpha vs BOTH single-root carry-timing arms
  G4  era signs printed (2009-15 / 2016-21 / 2022-26) — classification, not veto
  G5  MODELED $4.36 RT + {1,2}-tick band on BOTH legs, weekly turnover, drag printed
  decision: G2+G3 PASS -> ZNZB_RV01 ENGINE CANDIDATE; either fails -> closed at scope.
"""
from __future__ import annotations

import difflib
import hashlib
import json
import os
import sys
from datetime import datetime, timezone

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(RUN))
OUT = os.path.join(RUN, "out")
os.makedirs(OUT, exist_ok=True)
CV_SRC = os.path.join(ROOT, "runs", "CARRY_V1_20260828", "src")
sys.path.insert(0, os.path.join(ROOT, "research", "multi_market", "src"))
sys.path.insert(0, HERE)

import ncd_day as N                                                     # noqa: E402
import roll as R                                                        # noqa: E402

# ---- FROZEN BY spec.yaml --------------------------------------------------
SEAL = pd.Timestamp("2026-08-01")
WIN_START = pd.Timestamp("2009-01-01")
PAIR = ("ZN", "ZB")
SECTOR = "rates"
PRIMARY_TICKS, STRESS_TICKS = 1.0, 2.0
ERAS = [("2009-15", pd.Timestamp("2009-01-01"), pd.Timestamp("2015-12-31")),
        ("2016-21", pd.Timestamp("2016-01-01"), pd.Timestamp("2021-12-31")),
        ("2022-26", pd.Timestamp("2022-01-01"), pd.Timestamp("2026-07-31"))]
BLOCK_WEEKS = 13                       # block bootstrap CIs (implementation, recorded)
N_BOOT = 2000                          # implementation choice, recorded
BOOT_SEED_MEAN = 20260906              # shared-draw seed, recorded for G3_BASISMOM
BOOT_SEED_ALPHA = 20260907             # recorded
BETA_ALT_LB = 252                      # 52-week alternative sigma for the stability audit
FRAGILITY_FLIP = 0.20
G2_NULL_PCTL = 95.0
EXPECTED_DIFF = {
    '-DEV_START, DEV_END = pd.Timestamp("2009-01-01"), pd.Timestamp("2019-01-01")',
    '+DEV_START, DEV_END = pd.Timestamp("2009-01-01"), pd.Timestamp("2026-08-01")',
    '-    for cid, r, m, y in N.contracts_for(root, 2009, 2019):',
    '+    for cid, r, m, y in N.contracts_for(root, 2009, 2027):',
}
G2_EVENT_WORDS = (
    "the probability, under weekly signed position streams whose TIMING is destroyed by "
    "a circular shift (all offsets, preserving each leg's serial structure, the pair's "
    "cross-leg dependence, and the stream's composition/turnover) but evaluated against "
    "the SAME realized returns and the SAME cost machinery, of an after-cost weekly-mean "
    "P&L at least as large as observed")
G2_SECOND_WAY = (
    "second computation of the same 'distinguishable from zero' event by a different "
    "route: 13-week circular block bootstrap CI of the weekly mean (2000 draws)")
# ---------------------------------------------------------------------------

_fh = None


def P(*a):
    print(*a, flush=True)
    if _fh is not None:
        print(*a, file=_fh)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def code_hashes():
    files = {
        "carry_znzb.py": os.path.join(HERE, "carry_znzb.py"),
        "run_znzb.py": os.path.join(HERE, "run_znzb.py"),
        "spec.yaml": os.path.join(RUN, "spec.yaml"),
        "carry_v1.py": os.path.join(CV_SRC, "carry_v1.py"),
        "ncd_day.py": os.path.join(ROOT, "research", "multi_market", "src", "ncd_day.py"),
        "roll.py": os.path.join(ROOT, "research", "multi_market", "src", "roll.py"),
    }
    return {k: sha256(v) for k, v in files.items()}


def diff_audit():
    """carry_znzb.py must differ from carry_v1.py by EXACTLY the two sanctioned
    mechanical changes.  Anything else => INVALID-RUN."""
    a = open(os.path.join(CV_SRC, "carry_v1.py"), encoding="utf-8").read().splitlines()
    b = open(os.path.join(HERE, "carry_znzb.py"), encoding="utf-8").read().splitlines()
    d = [l for l in difflib.unified_diff(a, b, lineterm="")
         if l.startswith(("+", "-")) and not l.startswith(("+++", "---"))]
    ok = set(d) == EXPECTED_DIFF and len(d) == 4
    P("    diff(carry_v1.py -> carry_znzb.py):")
    for l in d:
        P(f"        {l}")
    P(f"    diff audit: {'PASS - exactly the two sanctioned changes' if ok else '*** FAIL - INVALID-RUN ***'}")
    return ok


class _Uni:
    """Temporarily set the module's UNIVERSE (the sanctioned single-sector pair wrapper,
    identical to CARRY_SIGC_CONFIRM's)."""

    def __init__(self, mod, uni):
        self.mod, self.uni = mod, uni

    def __enter__(self):
        self.saved = self.mod.UNIVERSE
        self.mod.UNIVERSE = self.uni

    def __exit__(self, *a):
        self.mod.UNIVERSE = self.saved


def pair_sim(mod, sub, ticks, W=None):
    with _Uni(mod, {SECTOR: list(PAIR)}):
        if W is None:
            W = mod.weekly_weights(sub)
        out, gross, cost, UNITS, so = mod.simulate(sub, W, ticks)
    return W, out, UNITS


def weekly_grid(sub, W):
    """Full weekly weight pivot (CASH weeks = 0-row ffilled) on the pair's own calendar.
    FROZEN-MODULE SEMANTICS: simulate() ffills through weeks with no row; the grid must
    reproduce that exactly — the k=0 reconstruction is asserted before any use."""
    days = pd.DatetimeIndex(sorted(set().union(*[set(x.index) for x in sub.values()])))
    iso = days.isocalendar()
    wk = pd.Series([f"{y}-W{w:02d}" for y, w in zip(iso.year, iso.week)], index=days)
    first_day = wk.groupby(wk.values).apply(lambda s: s.index.min())
    fd = pd.DatetimeIndex(sorted(first_day.values))
    piv = W.pivot_table(index="effective_from", columns="root", values="w")
    piv = piv.reindex(index=fd, columns=list(PAIR)).ffill().fillna(0.0)
    return piv, wk


def sim_from_pivot(mod, sub, piv, ticks):
    long = piv.stack().rename("w").reset_index()
    long.columns = ["effective_from", "root", "w"]
    with _Uni(mod, {SECTOR: list(PAIR)}):
        out, *_ = mod.simulate(sub, long, ticks)
    return out


def pctl_of(obs, null):
    null = np.asarray(null, dtype=float)
    below = (null < obs - 1e-12).sum()
    ties = (np.abs(null - obs) <= 1e-12).sum()
    return float(100.0 * (below + 0.5 * ties) / len(null))


def block_boot_indices(n, rng):
    """Circular 13-week block bootstrap index draw of length n."""
    nb = int(np.ceil(n / BLOCK_WEEKS))
    starts = rng.integers(0, n, size=nb)
    idx = np.concatenate([(s + np.arange(BLOCK_WEEKS)) % n for s in starts])[:n]
    return idx


def gate_table(rows, title):
    lines = []

    def L(s=""):
        lines.append(s)
        P(s)
    L("")
    L("=" * 112)
    L(f"=== {title}")
    L("=" * 112)
    L(f"    {'GATE':<46} {'SPEC':<40} {'OBSERVED':<52} VERDICT")
    for name, spec, obs, ok in rows:
        v = "PASS" if ok else "*** FAIL ***"
        if ok is None:
            v = "REPORT-ONLY"
        L(f"    {name:<46} {spec:<40} {obs:<52} {v}")
    return lines


def main():
    global _fh
    _fh = open(os.path.join(OUT, "znzb_console.txt"), "w", encoding="utf-8")
    P("=" * 112)
    P("=== G3_ZNZB_SLOPE_20260906 — ZN/ZB duration-neutral slope-carry RV.  Window 2009-01-01 -> < 2026-08-01.")
    P(f"=== run at {datetime.now(timezone.utc).isoformat()}   [DISCOVERY; costs MODELED; research sizing]")
    P("=" * 112)

    ok_diff = diff_audit()

    P("")
    P("=== s6/s7 UNIT TESTS (certified roll construction, reused not reinvented)")
    R.test_no_roll_telescopes()
    R.test_basis_invariance()
    R.test_roll_causality()
    ok_units = True                                # asserts inside would have raised

    import carry_znzb as CZ
    assert CZ.DEV_START == WIN_START and CZ.DEV_END == SEAL, "window constants drifted"

    P("")
    P("=== building ZN/ZB panels (CARRY_V1 construction verbatim, structural truncation < 2026-08-01)")
    sub = {}
    for r in PAIR:
        x = CZ.build_root(r)
        if x is not None and len(x) > 200:
            sub[r] = x
            P(f"    {r:<4} paired days {len(x):>6}  {x.index.min().date()} -> {x.index.max().date()}  "
              f"median gap {x['gap'].median():.0f}mo  median |carry| {x['carry'].abs().median():.3f}")
    ok_roots = sorted(sub) == sorted(PAIR)
    seal_max = max(x.index.max() for x in sub.values()) if sub else pd.Timestamp("2262-01-01")
    ok_seal = ok_roots and seal_max < SEAL
    P(f"    seal assert: max session {seal_max.date()} < 2026-08-01  "
      f"{'PASS' if ok_seal else '*** FAIL ***'}")
    assert ok_seal, "SEAL VIOLATION or panel build failure"

    # ---- two-sided causality probe on the pair (frozen machinery)
    with _Uni(CZ, {SECTOR: list(PAIR)}):
        CZ._fh = _fh
        ok_causal = CZ.causality_probe(sub)
        CZ._fh = None

    # ---- frozen object: PRIMARY (1 tick) + STRESS (2 ticks), same weights
    Wp, out_p, UNITS_p = pair_sim(CZ, sub, PRIMARY_TICKS)
    _, out_s, _ = pair_sim(CZ, sub, STRESS_TICKS, W=Wp)

    # sanity: the carry-richer root is LONG (weekly_weights ranks ascending -> +1 = richer)
    chk = Wp.pivot_table(index="week", columns="root", values=["carry", "w_rank"])
    dcar = chk["carry"]["ZN"] - chk["carry"]["ZB"]
    richer_long = (np.sign(dcar) == np.sign(chk["w_rank"]["ZN"] - chk["w_rank"]["ZB"])) \
        | (dcar == 0)
    P(f"    sign convention check: carry-richer root LONG in {richer_long.mean():.1%} of "
      f"{len(chk)} decided weeks (must be 100%; exact ties counted as pass)")
    assert richer_long.all(), "sign convention broken"

    # ---- weekly aggregation (ISO weeks of the daily P&L calendar)
    iso = out_p.index.isocalendar()
    wklab = pd.Series([f"{y}-W{w:02d}" for y, w in zip(iso.year, iso.week)],
                      index=out_p.index)
    wk_p = out_p.groupby(wklab.values).agg(gross=("gross", "sum"), cost=("cost", "sum"),
                                           net=("net", "sum"))
    wk_first = out_p.groupby(wklab.values).apply(lambda d: d.index.min())
    wk_s_net = out_s.groupby(wklab.values)["net"].sum()
    Nw = len(wk_p)
    y_w = wk_p["net"].to_numpy()
    sd_w = float(np.std(y_w, ddof=1))

    # =================================================================== G1 MDE FIRST
    P("")
    P("=" * 112)
    P("=== G1 — MDE, printed BEFORE any observed edge number")
    P("=" * 112)
    se_mean = sd_w / np.sqrt(Nw)
    mde_mean = 2.80 * se_mean                       # 5% two-sided, 80% power
    se_S = np.sqrt(52.0 / Nw)
    P(f"    N = {Nw} ISO weeks   weekly-net sd = ${sd_w:,.0f}")
    P(f"    SE(weekly mean) = ${se_mean:,.0f}   MDE (5% two-sided, 80% power) = ${mde_mean:,.0f}/week")
    P(f"    SE(annualized Sharpe) ~ {se_S:.3f}   MDE Sharpe ~ {2.80 * se_S:.3f}")
    P("    -> only an edge of roughly P1-class weekly consistency is detectable; a small true"
      " edge most likely reads as FAIL and closes the object at scope.")

    # =================================================================== OBSERVED
    mean_w = float(np.mean(y_w))
    tot_net = float(wk_p["net"].sum())
    tot_gross = float(wk_p["gross"].sum())
    tot_cost = float(wk_p["cost"].sum())
    sharpe_w = float(mean_w / sd_w * np.sqrt(52)) if sd_w > 0 else 0.0
    mean_w_s = float(wk_s_net.mean())
    turno_d = float(UNITS_p.diff().abs().sum(1).mean())
    turno_w = float(UNITS_p.diff().abs().sum(1).groupby(wklab.values).sum().mean())
    drag_dollars = tot_cost
    drag_frac = tot_cost / max(abs(tot_gross), 1e-9)

    P("")
    P("=" * 112)
    P("=== OBSERVED — frozen object, MODELED costs [DISCOVERY]")
    P("=" * 112)
    P(f"    PRIMARY (1 tick):  gross ${tot_gross:>12,.0f}   cost ${tot_cost:>10,.0f}   "
      f"net ${tot_net:>12,.0f}   weekly mean ${mean_w:>8,.2f}   ann Sharpe {sharpe_w:>7.3f}")
    P(f"    STRESS  (2 tick):  net ${float(wk_s_net.sum()):>12,.0f}   weekly mean ${mean_w_s:>8,.2f}")
    P(f"    turnover: mean daily |dUnits| {turno_d:.4f}   mean weekly |dUnits| {turno_w:.4f}")

    # =================================================================== G2 — edge
    P("")
    P("=" * 112)
    P("=== G2 — after-cost weekly mean > 0, CI excludes 0, clears circular-shift null at 5%")
    P("=" * 112)
    ok_g2a = mean_w > 0

    # CI: 13-week circular block bootstrap (the spec's 'block bootstrap CIs')
    rng = np.random.default_rng(BOOT_SEED_MEAN)
    boots = np.array([y_w[block_boot_indices(Nw, rng)].mean() for _ in range(N_BOOT)])
    ci_lo, ci_hi = np.percentile(boots, [2.5, 97.5])
    ok_g2b = ci_lo > 0
    P(f"    {G2_SECOND_WAY}")
    P(f"    weekly mean ${mean_w:,.2f}   95% block-bootstrap CI [${ci_lo:,.2f}, ${ci_hi:,.2f}]  "
      f"seed {BOOT_SEED_MEAN} (recorded for shared draws)")

    # circular-shift null: ALL offsets on the weekly signed position grid
    piv, _wk_days = weekly_grid(sub, Wp)
    o_rec = sim_from_pivot(CZ, sub, piv, PRIMARY_TICKS)
    rec_diff = abs(float(o_rec["net"].sum()) - float(out_p["net"].sum()))
    P(f"    pivot-reconstruction net vs direct: |d| = ${rec_diff:.6f}  "
      f"{'OK' if rec_diff < 1e-6 else '*** MISMATCH ***'}")
    ok_recon = rec_diff < 1e-6
    assert ok_recon, "pivot reconstruction drifted from direct simulate"

    Ngrid = len(piv)
    vals = piv.to_numpy()
    ks = list(range(1, Ngrid))                       # ALL offsets, per spec
    null_means = np.empty(len(ks))
    for j, k in enumerate(ks):
        p2 = pd.DataFrame(np.roll(vals, k, axis=0), index=piv.index, columns=piv.columns)
        o2 = sim_from_pivot(CZ, sub, p2, PRIMARY_TICKS)
        null_means[j] = float(o2["net"].sum()) / Nw
    pctl = pctl_of(mean_w, null_means)
    ok_g2c = pctl >= G2_NULL_PCTL
    P(f"    EVENT IN WORDS: the null percentile is over {G2_EVENT_WORDS}.")
    P(f"    circular-shift null: {len(ks)} offsets on a {Ngrid}-week grid   "
      f"null weekly-mean mean ${null_means.mean():,.2f} sd ${null_means.std():,.2f}")
    P(f"    observed ${mean_w:,.2f} -> percentile {pctl:.1f}  (bar {G2_NULL_PCTL:.0f})")
    P("    shared-draw note: the shift null is DETERMINISTIC (all offsets) — inherently "
      "shared with G3_BASISMOM on overlapping windows; bootstrap seeds recorded above.")
    ok_g2 = ok_g2a and ok_g2b and ok_g2c

    # =================================================================== G3 — not outright
    P("")
    P("=" * 112)
    P("=== G3 — reduce-to-outright control: RV alpha vs BOTH single-root carry-timing arms")
    P("=" * 112)
    P("    controls: identical machinery — same weekly calendar/decision rule, position "
      "sign(own carry) [long when own carry positive, short when negative], legs 1/sigma, "
      "same 1-tick+commission cost model, same normalization.")
    ctrl_out = {}
    for r in PAIR:
        Wc = Wp.copy()
        Wc["w_rank"] = np.where(Wc["root"] == r, np.sign(Wc["carry"]), 0.0)
        Wc["w"] = Wc["w_rank"] / (Wc["n_live_sectors"] * Wc["n_sector"])
        _, oc, _ = pair_sim(CZ, sub, PRIMARY_TICKS, W=Wc)
        ctrl_out[r] = oc.groupby(wklab.values)["net"].sum().reindex(wk_p.index).fillna(0.0)
        P(f"    ctrl {r}: total net ${float(ctrl_out[r].sum()):>12,.0f}   "
          f"weekly mean ${float(ctrl_out[r].mean()):>8,.2f}   "
          f"ann Sharpe {float(ctrl_out[r].mean() / ctrl_out[r].std() * np.sqrt(52)):>7.3f}")

    X = np.column_stack([np.ones(Nw), ctrl_out["ZN"].to_numpy(), ctrl_out["ZB"].to_numpy()])
    beta, *_ = np.linalg.lstsq(X, y_w, rcond=None)
    resid = y_w - X @ beta
    r2 = 1.0 - resid.var() / np.var(y_w)
    alpha = float(beta[0])
    rng_a = np.random.default_rng(BOOT_SEED_ALPHA)
    alphas = np.empty(N_BOOT)
    for i in range(N_BOOT):
        idx = block_boot_indices(Nw, rng_a)
        bb, *_ = np.linalg.lstsq(X[idx], y_w[idx], rcond=None)
        alphas[i] = bb[0]
    a_lo, a_hi = np.percentile(alphas, [2.5, 97.5])
    ok_g3 = (alpha > 0) and (a_lo > 0)
    P(f"    OLS: alpha ${alpha:,.2f}/wk   beta_ZN {beta[1]:+.3f}   beta_ZB {beta[2]:+.3f}   R2 {r2:.3f}")
    P(f"    alpha 95% block-bootstrap CI [${a_lo:,.2f}, ${a_hi:,.2f}]   seed {BOOT_SEED_ALPHA}   "
      f"{'POSITIVE ALPHA' if ok_g3 else 'alpha not distinguishable from outright carry -> curve object NOT established'}")

    # =================================================================== beta stability audit
    P("")
    P("=== beta-stability audit (control, REPORT-ONLY): 52-week alternative sigma vs frozen 63d")
    alt_ord_flips, base_flips = [], None
    alt = {}
    for r in PAIR:
        s_alt = sub[r]["ret_points"].rolling(BETA_ALT_LB, min_periods=BETA_ALT_LB) \
            .std().shift(1)
        alt[r] = sub[r]["slope"] / s_alt
    dec = Wp.pivot_table(index="effective_from", columns="root", values="carry")
    ratio = []
    n_ok, n_flip = 0, 0
    for d0, row in dec.iterrows():
        av = {}
        for r in PAIR:
            px = alt[r].loc[alt[r].index < d0].dropna()
            if len(px) == 0 or (d0 - px.index.max()).days > 7:
                continue
            av[r] = float(px.iloc[-1])
        if len(av) == 2 and not (pd.isna(row["ZN"]) or pd.isna(row["ZB"])):
            n_ok += 1
            if np.sign(av["ZN"] - av["ZB"]) != np.sign(row["ZN"] - row["ZB"]):
                n_flip += 1
    sig_ratio = (sub["ZN"]["sigma"] / sub["ZB"]["sigma"].reindex(sub["ZN"].index)).dropna()
    flip_share = n_flip / max(n_ok, 1)
    wow = dec.dropna()
    wow_flip = float((np.sign(wow["ZN"] - wow["ZB"]).diff().abs() > 0).mean())
    fragile = flip_share > FRAGILITY_FLIP
    P(f"    hedge ratio sigma_ZN/sigma_ZB: min {sig_ratio.min():.3f}  median {sig_ratio.median():.3f}  "
      f"max {sig_ratio.max():.3f}")
    P(f"    carry-ordering agreement 63d-sigma vs 252d-sigma: {n_ok} comparable weeks, "
      f"{n_flip} flips = {flip_share:.1%}  "
      f"{'*** FRAGILITY FLAG (>20%) — ordering is sigma-driven ***' if fragile else '(below 20% flag)'}")
    P(f"    week-over-week ordering flip rate (choppiness): {wow_flip:.1%}")

    # =================================================================== G4 — eras
    P("")
    P("=== G4 — era signs (classification per owner doctrine, NOT a veto)")
    era_rows = []
    for nm, a, b in ERAS:
        seg = out_p.loc[(out_p.index >= a) & (out_p.index <= b), "net"]
        era_rows.append((nm, float(seg.sum()), len(seg)))
        P(f"    {nm}: net ${era_rows[-1][1]:>12,.0f}  ({era_rows[-1][2]} days)  "
          f"sign {'+' if era_rows[-1][1] > 0 else '-'}")
    yr = out_p["net"].groupby(out_p.index.year).sum()
    P("    net by year: " + "  ".join(f"{y}:{v:+,.0f}" for y, v in yr.items()))

    # =================================================================== G5 — cost
    P("")
    P("=== G5 — MODELED cost band [$4.36 RT commission + {1,2}-tick spread per leg]")
    P(f"    PRIMARY drag: ${drag_dollars:,.0f} total = {100 * drag_frac:.1f}% of |gross|   "
      f"weekly cost ${tot_cost / Nw:,.2f}")
    stress_cost = float(out_s['cost'].sum())
    P(f"    STRESS  drag: ${stress_cost:,.0f} total   weekly cost ${stress_cost / Nw:,.2f}")
    P(f"    weekly turnover (|dUnits|): {turno_w:.4f}   ZN tick $"
      f"{N.PV['ZN'] / 64:.2f}   ZB tick ${N.PV['ZB'] / 32:.2f}")
    P("    ZN/ZB are the deepest CME spread markets; the band above PROVES the claim rather "
      "than assuming it — the 2-tick arm is the fragility rung.")

    # =================================================================== GATE TABLE
    rows = [
        ("DIFF  module = carry_v1 + 2 changes", "exactly 2 sanctioned line-pairs",
         "see diff above", ok_diff),
        ("UT    s6/s7 unit tests", "telescope+basis+causality", "all pass", ok_units),
        ("SEAL  max session < 2026-08-01", "< 2026-08-01", f"{seal_max.date()}", ok_seal),
        ("CAUS  two-sided causality probe", "future<1e-12, past>1e-9", "see probe above",
         ok_causal),
        ("RECON pivot==direct simulate", "|d net| < 1e-6", f"${rec_diff:.2e}", ok_recon),
        ("G1    MDE printed before observed", "printed", f"MDE ${mde_mean:,.0f}/wk over {Nw} wks",
         True),
        ("G2a   after-cost weekly mean > 0", "> $0", f"${mean_w:,.2f}", ok_g2a),
        ("G2b   95% block-boot CI excludes 0", "CI_lo > 0",
         f"[${ci_lo:,.2f}, ${ci_hi:,.2f}]", ok_g2b),
        ("G2c   circular-shift null at 5%", f">= {G2_NULL_PCTL:.0f} pctl", f"{pctl:.1f}",
         ok_g2c),
        ("G3    positive alpha vs BOTH outrights", "alpha > 0 and CI_lo > 0",
         f"${alpha:,.2f}/wk, CI [${a_lo:,.2f}, ${a_hi:,.2f}]", ok_g3),
        ("G4    era signs printed", "3 eras",
         " ".join(f"{nm}:{'+' if v > 0 else '-'}" for nm, v, _ in era_rows), None),
        ("G5    cost band printed", "drag + turnover",
         f"1tk ${tot_cost / Nw:,.0f}/wk, 2tk ${stress_cost / Nw:,.0f}/wk", None),
        ("BETA  stability audit (flag only)", f"flip share <= {FRAGILITY_FLIP:.0%}",
         f"{flip_share:.1%} alt-sigma flips; wow {wow_flip:.1%}", None),
    ]
    tbl = gate_table(rows, "GATES — GATE / SPEC / OBSERVED / PASS-FAIL "
                           "[2009-01-01 -> 2026-07-31, DISCOVERY, MODELED costs]")

    # ---- mechanical decision rule (spec.yaml): G2+G3 PASS -> candidate; either fails -> closed
    invalid = not (ok_diff and ok_units and ok_seal and ok_causal and ok_recon and ok_roots)
    if invalid:
        verdict, ledger = "INVALID-RUN", "DEFECT"
    elif ok_g2 and ok_g3:
        verdict, ledger = "ZNZB_RV01 ENGINE CANDIDATE (Class-S/P; rho-to-P1 next)", "PASS"
    else:
        verdict, ledger = "CLOSED AT SCOPE (s28 block in REPORT.md)", "FAIL"
    P("")
    P("=" * 112)
    P(f"=== PREREGISTERED BINARY VERDICT: {verdict}   (ledger G00074: {ledger})")
    P("=" * 112)
    if ledger == "PASS":
        P("    rho-to-P1: no in-run P1 weekly P&L artifact exists in-repo (recorded by "
          "CARRY_SIGC_CONFIRM); computing it is the Class-S/P assessment step, not this run.")

    # ---- outputs
    with open(os.path.join(OUT, "gate_table.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(tbl) + "\n")
        f.write(f"\nPREREGISTERED BINARY VERDICT: {verdict}   (ledger G00074: {ledger})\n")
    wk_out = wk_p.copy()
    wk_out.insert(0, "first_day", wk_first)
    wk_out["net_stress2tk"] = wk_s_net.reindex(wk_out.index)
    wk_out.index.name = "week"
    wk_out.to_csv(os.path.join(OUT, "weekly_pnl.csv"))
    ctrl_df = pd.DataFrame({"rv_net": wk_p["net"], "ctrl_zn_net": ctrl_out["ZN"],
                            "ctrl_zb_net": ctrl_out["ZB"]})
    ctrl_df.index.name = "week"
    ctrl_df.to_csv(os.path.join(OUT, "outright_control.csv"))
    json.dump({
        "run_id": "G3_ZNZB_SLOPE_20260906", "verdict": verdict, "ledger_result": ledger,
        "gates": [{"gate": n, "spec": s, "observed": o,
                   "pass": (None if k is None else bool(k))} for n, s, o, k in rows],
        "headline": {"n_weeks": Nw, "weekly_mean": mean_w, "weekly_sd": sd_w,
                     "ann_sharpe_weekly": sharpe_w, "total_net": tot_net,
                     "total_gross": tot_gross, "total_cost": tot_cost,
                     "stress_total_net": float(wk_s_net.sum()),
                     "ci_lo": float(ci_lo), "ci_hi": float(ci_hi),
                     "null_pctl": pctl, "null_n_offsets": len(ks),
                     "alpha_weekly": alpha, "alpha_ci": [float(a_lo), float(a_hi)],
                     "beta_zn": float(beta[1]), "beta_zb": float(beta[2]), "r2": float(r2),
                     "ctrl_zn_total": float(ctrl_out["ZN"].sum()),
                     "ctrl_zb_total": float(ctrl_out["ZB"].sum()),
                     "flip_share_alt_sigma": flip_share, "wow_flip": wow_flip,
                     "eras": {nm: v for nm, v, _ in era_rows},
                     "mde_weekly_mean": float(mde_mean)},
        "seeds": {"boot_mean": BOOT_SEED_MEAN, "boot_alpha": BOOT_SEED_ALPHA,
                  "shift_null": "deterministic all-offsets"},
        "evidence_status": "DISCOVERY (2026-06/07 segment lies in the BURNED window; "
                           "sample includes it per frozen spec; no forward claim)",
        "code_hashes": code_hashes(),
        "utc": datetime.now(timezone.utc).isoformat(),
    }, open(os.path.join(OUT, "znzb_verdict.json"), "w", encoding="utf-8"), indent=2)
    P("    outputs: out/gate_table.txt, out/weekly_pnl.csv, out/outright_control.csv, "
      "out/znzb_verdict.json, out/znzb_console.txt")
    _fh.close()
    return ledger


if __name__ == "__main__":
    main()
