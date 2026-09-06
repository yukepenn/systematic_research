"""G3_RATESCARRY_20260906 driver — outright rates carry-timing (ZN, ZB), the winning
G00074 control given its own honest, debt-priced trial.  Executes spec.yaml EXACTLY
(frozen before results; ledger G00081, family GENESIS3_RV).

FROZEN OBJECT (spec.yaml): per root i in {ZN, ZB}, weekly (ISO, causal):
position_t = sign(carry_i,t), carry as in CARRY_V1/G00074 verbatim
((P_near - P_deferred)/month_gap / lagged-63d sigma).  Always in, long or short.
Sized 1/sigma_i.  Both roots reported separately AND as an equal-vol pool (the pool
carries the headline).  Zero free parameters.

MACHINERY REUSE, not reimplementation: this driver IMPORTS carry_znzb.py and
run_znzb.py from runs/G3_ZNZB_SLOPE_20260906/src/ and asserts their sha256 against the
hashes recorded in G00074's out/znzb_verdict.json.  The per-root arms are built with
the EXACT three lines G00074 used for its outright controls; the arms' weekly nets are
asserted equal to G00074's out/outright_control.csv (RECON-B).  Any drift => INVALID-RUN.

SELECTION DEBT (provenance_honesty): the controls were observed positive BEFORE this
registration.  Priced by (a) null bar tightened to the 97.5th percentile, and
(b) MANDATORY victory over BOTH exposure-matched static arms (always-long, always-short).

GATES (spec.yaml, decision rule mechanical):
  G1   MDE printed BEFORE observed (~596 weeks realized coverage expected)
  G2   pool after-cost weekly mean > 0, block CI excludes 0, circular-shift null
       percentile >= 97.5 (debt-tightened bar)
  G2b  second null (13-wk block permutation); agreement judged TAIL-SIDE (both above
       or both below the bar), NOT raw percentile distance.  Split verdict = INVALID-RUN.
  G3   beats BOTH exposure-matched static arms: pool Sharpe > each arm's, AND alpha
       regression vs the static-long arm has CI excluding 0
  G4   era signs 2009-15 / 2016-21 / 2022-26; the 2022-26 cell DECIDES classification:
       negative modern = FAIL regardless of pooled total
  G5   MODELED $4.36 RT + {1,2}-tick band, weekly turnover printed
  G6   eval_battery weekly-vol lead; fixed-DD only as dollar descriptor; rho-to-P1
  decision: G2+G2b+G3+G4(modern not negative) PASS -> RATESCARRY01 ENGINE CANDIDATE;
            any fail -> closed at scope (completion note for the G00074 s28 block).
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from datetime import datetime, timezone

import numpy as np
import pandas as pd

sys.dont_write_bytecode = True          # never write __pycache__ into another run's src/

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(RUN))
OUT = os.path.join(RUN, "out")
os.makedirs(OUT, exist_ok=True)
ZNZB_SRC = os.path.join(ROOT, "runs", "G3_ZNZB_SLOPE_20260906", "src")
ZNZB_OUT = os.path.join(ROOT, "runs", "G3_ZNZB_SLOPE_20260906", "out")
sys.path.insert(0, os.path.join(ROOT, "research", "multi_market", "src"))
sys.path.insert(0, ZNZB_SRC)
sys.path.insert(0, ROOT)                # for research_sdk.eval_battery

import roll as R                                                        # noqa: E402
import run_znzb as RZ                                                   # noqa: E402
import carry_znzb as CZ                                                 # noqa: E402
from research_sdk.eval_battery import max_drawdown, cdar                # noqa: E402

# ---- FROZEN BY spec.yaml --------------------------------------------------
SEAL = pd.Timestamp("2026-08-01")
WIN_START = pd.Timestamp("2009-01-01")
PAIR = ("ZN", "ZB")
SECTOR = "rates"
PRIMARY_TICKS, STRESS_TICKS = 1.0, 2.0
ERAS = [("2009-15", pd.Timestamp("2009-01-01"), pd.Timestamp("2015-12-31")),
        ("2016-21", pd.Timestamp("2016-01-01"), pd.Timestamp("2021-12-31")),
        ("2022-26", pd.Timestamp("2022-01-01"), pd.Timestamp("2026-07-31"))]
G2_NULL_PCTL = 97.5                    # debt-tightened bar (spec: alpha halved)
BLOCK_WEEKS = 13                       # same as G00074 (asserted below)
N_BOOT = 2000                          # same as G00074 (asserted below)
N_PERM = 2000                          # 13-wk block-permutation null draws (recorded)
BOOT_SEED_MEAN = 20260916              # recorded
BOOT_SEED_ALPHA = 20260917             # recorded
PERM_SEED = 20260918                   # recorded
P1_DAILY_CSV = os.path.join(ROOT, "runs", "WE_W56_BREADTH", "out", "p1_daily.csv")
# G00074 machinery hashes (from runs/G3_ZNZB_SLOPE_20260906/out/znzb_verdict.json):
EXPECTED_HASHES = {
    "carry_znzb.py": "b443803f0c4b23a4d2a18f16601d50215e839f3c0ede1c236df7d2eb161d775a",
    "run_znzb.py": "fc61d3fe0535292374e471440908edfe187607f44aa86e11086431639620dee4",
    "ncd_day.py": "17603bdc722d30f386b013d35a33f8b2cb510d8b7ea6fdbc07f0274bf01baec9",
    "roll.py": "b88a5176f8ed1dbc3903e300f6238993099046437c4b921293c9ba1d2eda837f",
}
G2_EVENT_WORDS = (
    "the probability, under weekly signed position streams whose TIMING is destroyed by "
    "a circular shift (all offsets, both roots shifted TOGETHER, preserving each root's "
    "serial structure, the cross-root dependence, and the stream's composition/turnover) "
    "but evaluated against the SAME realized returns and the SAME cost machinery, of an "
    "after-cost weekly-mean pool P&L at least as large as observed")
G2B_SECOND_WAY = (
    "second computation of the SAME event by a different route: 13-week block "
    "PERMUTATION of the weekly position grid (both roots permuted together, preserving "
    "13-week local serial structure while destroying long-range timing), "
    f"{N_PERM} draws; agreement judged TAIL-SIDE against the {G2_NULL_PCTL} bar")
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


def hash_audit():
    """The imported machinery must be BYTE-IDENTICAL to what G00074 ran."""
    files = {
        "carry_znzb.py": os.path.join(ZNZB_SRC, "carry_znzb.py"),
        "run_znzb.py": os.path.join(ZNZB_SRC, "run_znzb.py"),
        "ncd_day.py": os.path.join(ROOT, "research", "multi_market", "src", "ncd_day.py"),
        "roll.py": os.path.join(ROOT, "research", "multi_market", "src", "roll.py"),
    }
    ok = True
    for k, p in files.items():
        h = sha256(p)
        good = h == EXPECTED_HASHES[k]
        ok = ok and good
        P(f"    {k:<16} {h[:16]}...  {'== G00074 recorded' if good else '*** DRIFT vs G00074 ***'}")
    return ok


def gate_table(rows, title):
    lines = []

    def L(s=""):
        lines.append(s)
        P(s)
    L("")
    L("=" * 118)
    L(f"=== {title}")
    L("=" * 118)
    L(f"    {'GATE':<46} {'SPEC':<44} {'OBSERVED':<56} VERDICT")
    for name, spec, obs, ok in rows:
        v = "PASS" if ok else "*** FAIL ***"
        if ok is None:
            v = "REPORT-ONLY"
        L(f"    {name:<46} {spec:<44} {obs:<56} {v}")
    return lines


def main():
    global _fh
    _fh = open(os.path.join(OUT, "ratescarry_console.txt"), "w", encoding="utf-8")
    P("=" * 118)
    P("=== G3_RATESCARRY_20260906 — outright rates carry-timing sign(own carry), ZN+ZB, equal-vol pool.")
    P("=== Window 2009-01-01 -> < 2026-08-01.  EVIDENCE STATUS: DISCOVERY_CONSUMED — the per-root arms were")
    P("=== OBSERVED as positive controls in G00074 BEFORE this registration; the debt is priced by the 97.5")
    P("=== null bar and the mandatory static-arm victory.  Costs MODELED; research sizing.")
    P(f"=== run at {datetime.now(timezone.utc).isoformat()}")
    P("=" * 118)

    P("")
    P("=== MACHINERY HASH AUDIT — imported modules vs G00074's recorded sha256")
    ok_hash = hash_audit()

    P("")
    P("=== s6/s7 UNIT TESTS (certified roll construction, reused not reinvented)")
    R.test_no_roll_telescopes()
    R.test_basis_invariance()
    R.test_roll_causality()
    ok_units = True                                # asserts inside would have raised

    assert CZ.DEV_START == WIN_START and CZ.DEV_END == SEAL, "window constants drifted"
    assert RZ.BLOCK_WEEKS == BLOCK_WEEKS and RZ.N_BOOT == N_BOOT, "G00074 constants drifted"

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
    with RZ._Uni(CZ, {SECTOR: list(PAIR)}):
        CZ._fh = _fh
        ok_causal = CZ.causality_probe(sub)
        CZ._fh = None

    # ---- decided-weeks frame (G00074's Wp — the shared weekly calendar/carry table)
    Wp, _out_rv, _u = RZ.pair_sim(CZ, sub, PRIMARY_TICKS)

    # ---- per-root arms: EXACTLY G00074's outright-control construction (verbatim lines)
    arm_daily, arm_units = {}, {}
    for r in PAIR:
        Wc = Wp.copy()
        Wc["w_rank"] = np.where(Wc["root"] == r, np.sign(Wc["carry"]), 0.0)
        Wc["w"] = Wc["w_rank"] / (Wc["n_live_sectors"] * Wc["n_sector"])
        _, oc, uc = RZ.pair_sim(CZ, sub, PRIMARY_TICKS, W=Wc)
        arm_daily[r], arm_units[r] = oc, uc

    # ---- THE FROZEN OBJECT: pool = sign(own carry) on BOTH roots, each 1/sigma_i
    Wpool = Wp.copy()
    Wpool["w_rank"] = np.sign(Wpool["carry"])
    Wpool["w"] = Wpool["w_rank"] / (Wpool["n_live_sectors"] * Wpool["n_sector"])
    _, out_p, UNITS_p = RZ.pair_sim(CZ, sub, PRIMARY_TICKS, W=Wpool)
    _, out_s, _ = RZ.pair_sim(CZ, sub, STRESS_TICKS, W=Wpool)

    # ---- exposure-matched STATIC ARMS: always-long / always-short, same sizing/calendar
    static_daily = {}
    for nm, sgn in (("LONG", 1.0), ("SHORT", -1.0)):
        Ws = Wp.copy()
        Ws["w_rank"] = sgn
        Ws["w"] = Ws["w_rank"] / (Ws["n_live_sectors"] * Ws["n_sector"])
        _, os_, us_ = RZ.pair_sim(CZ, sub, PRIMARY_TICKS, W=Ws)
        static_daily[nm] = os_

    # ---- sign-convention + exposure-match asserts
    n_zero_carry = int((Wpool["carry"] == 0).sum())
    assert (Wpool["w"] * 2 == Wpool["w_rank"]).all(), "pool weight convention broken"
    assert ((np.sign(Wpool["w"]) == np.sign(Wpool["carry"])) | (Wpool["carry"] == 0)).all(), \
        "sign(own carry) convention broken"
    P("")
    P(f"    decided weeks {Wp['week'].nunique()}   root-weeks {len(Wp)}   "
      f"exact-zero carries {n_zero_carry} (flat that root-week if any)")
    for r in PAIR:
        m = Wpool["root"] == r
        P(f"    {r}: long share of decided weeks {float((Wpool.loc[m, 'w_rank'] > 0).mean()):.1%}  "
          f"(the 'mostly-long through a bond bull' threat, quantified)")
    P("    exposure match: pool |w| = 1/2 per root-week = static arms' |w| "
      f"{'EXACT' if n_zero_carry == 0 else f'except {n_zero_carry} zero-carry rows'}")

    # ---- weekly aggregation (ISO weeks of the daily P&L calendar — G00074 verbatim)
    iso = out_p.index.isocalendar()
    wklab = pd.Series([f"{y}-W{w:02d}" for y, w in zip(iso.year, iso.week)],
                      index=out_p.index)
    wk_p = out_p.groupby(wklab.values).agg(gross=("gross", "sum"), cost=("cost", "sum"),
                                           net=("net", "sum"))
    wk_first = out_p.groupby(wklab.values).apply(lambda d: d.index.min())
    wk_s_net = out_s.groupby(wklab.values)["net"].sum()
    arm_wk = {r: arm_daily[r].groupby(wklab.values)["net"].sum()
              .reindex(wk_p.index).fillna(0.0) for r in PAIR}
    stat_wk = {nm: static_daily[nm].groupby(wklab.values)["net"].sum()
               .reindex(wk_p.index).fillna(0.0) for nm in static_daily}
    Nw = len(wk_p)
    y_w = wk_p["net"].to_numpy()
    sd_w = float(np.std(y_w, ddof=1))

    # ---- RECON-A: pool == sum of the two per-root arms (linearity of the machinery)
    recA = float(np.max(np.abs(y_w - (arm_wk["ZN"] + arm_wk["ZB"]).to_numpy())))
    ok_recA = recA < 1e-6
    P(f"    RECON-A pool == arm_ZN + arm_ZB:  max weekly |d| = ${recA:.2e}  "
      f"{'PASS' if ok_recA else '*** FAIL ***'}")

    # ---- RECON-B: arms == G00074's recorded outright controls (the provenance object)
    g74 = pd.read_csv(os.path.join(ZNZB_OUT, "outright_control.csv"), index_col="week")
    recB = max(float(np.max(np.abs(arm_wk["ZN"].reindex(g74.index).to_numpy()
                                   - g74["ctrl_zn_net"].to_numpy()))),
               float(np.max(np.abs(arm_wk["ZB"].reindex(g74.index).to_numpy()
                                   - g74["ctrl_zb_net"].to_numpy()))))
    ok_recB = (len(g74) == Nw) and recB < 1e-6
    P(f"    RECON-B arms == G00074 outright_control.csv:  {len(g74)} vs {Nw} weeks, "
      f"max |d| = ${recB:.2e}  {'PASS' if ok_recB else '*** FAIL ***'}")

    # =================================================================== G1 MDE FIRST
    P("")
    P("=" * 118)
    P("=== G1 — MDE, printed BEFORE any observed edge number  [DISCOVERY_CONSUMED]")
    P("=" * 118)
    se_mean = sd_w / np.sqrt(Nw)
    mde_mean = 2.80 * se_mean                       # 5% two-sided, 80% power
    se_S = np.sqrt(52.0 / Nw)
    P(f"    N = {Nw} ISO weeks   weekly-net sd = ${sd_w:,.0f}")
    P(f"    SE(weekly mean) = ${se_mean:,.0f}   MDE (5% two-sided, 80% power) = ${mde_mean:,.0f}/week")
    P(f"    SE(annualized Sharpe) ~ {se_S:.3f}   MDE Sharpe ~ {2.80 * se_S:.3f}")
    P("    NOTE the bar here is TIGHTER than powered-MDE convention: the shift-null must be cleared at the")
    P(f"    {G2_NULL_PCTL} percentile (selection debt), so a true edge near the MDE can still honestly FAIL.")

    # =================================================================== OBSERVED
    mean_w = float(np.mean(y_w))
    tot_net = float(wk_p["net"].sum())
    tot_gross = float(wk_p["gross"].sum())
    tot_cost = float(wk_p["cost"].sum())
    sharpe_w = float(mean_w / sd_w * np.sqrt(52)) if sd_w > 0 else 0.0
    mean_w_s = float(wk_s_net.mean())
    turno_w = float(UNITS_p.diff().abs().sum(1).groupby(wklab.values).sum().mean())

    P("")
    P("=" * 118)
    P("=== OBSERVED — frozen object, MODELED costs  [DISCOVERY_CONSUMED]")
    P("=" * 118)
    P(f"    POOL PRIMARY (1 tick): gross ${tot_gross:>12,.0f}   cost ${tot_cost:>10,.0f}   "
      f"net ${tot_net:>12,.0f}   weekly mean ${mean_w:>8,.2f}   ann Sharpe {sharpe_w:>7.3f}")
    P(f"    POOL STRESS  (2 tick): net ${float(wk_s_net.sum()):>12,.0f}   weekly mean ${mean_w_s:>8,.2f}")
    for r in PAIR:
        a = arm_wk[r]
        shp = float(a.mean() / a.std(ddof=1) * np.sqrt(52))
        P(f"    ARM {r}:  total net ${float(a.sum()):>12,.0f}   weekly mean ${float(a.mean()):>8,.2f}   "
          f"ann Sharpe {shp:>7.3f}")
    P(f"    turnover: mean weekly |dUnits| {turno_w:.4f}")

    # =================================================================== G2 — edge
    P("")
    P("=" * 118)
    P(f"=== G2 — pool after-cost weekly mean > 0, block CI excludes 0, shift-null >= {G2_NULL_PCTL} pctl")
    P("=" * 118)
    ok_g2a = mean_w > 0

    rng = np.random.default_rng(BOOT_SEED_MEAN)
    boots = np.array([y_w[RZ.block_boot_indices(Nw, rng)].mean() for _ in range(N_BOOT)])
    ci_lo, ci_hi = np.percentile(boots, [2.5, 97.5])
    ok_g2ci = ci_lo > 0
    P(f"    13-wk circular block bootstrap CI of the weekly mean ({N_BOOT} draws, seed {BOOT_SEED_MEAN}):")
    P(f"    weekly mean ${mean_w:,.2f}   95% CI [${ci_lo:,.2f}, ${ci_hi:,.2f}]")

    # circular-shift null: ALL offsets on the weekly signed position grid (pool)
    piv, _wk_days = RZ.weekly_grid(sub, Wpool)
    o_rec = RZ.sim_from_pivot(CZ, sub, piv, PRIMARY_TICKS)
    rec_diff = abs(float(o_rec["net"].sum()) - float(out_p["net"].sum()))
    P(f"    RECON-C pivot-reconstruction net vs direct: |d| = ${rec_diff:.6f}  "
      f"{'OK' if rec_diff < 1e-6 else '*** MISMATCH ***'}")
    ok_recC = rec_diff < 1e-6
    assert ok_recC, "pivot reconstruction drifted from direct simulate"

    Ngrid = len(piv)
    vals = piv.to_numpy()
    ks = list(range(1, Ngrid))                       # ALL offsets
    null_shift = np.empty(len(ks))
    for j, k in enumerate(ks):
        p2 = pd.DataFrame(np.roll(vals, k, axis=0), index=piv.index, columns=piv.columns)
        o2 = RZ.sim_from_pivot(CZ, sub, p2, PRIMARY_TICKS)
        null_shift[j] = float(o2["net"].sum()) / Nw
    pctl_shift = RZ.pctl_of(mean_w, null_shift)
    ok_g2null = pctl_shift >= G2_NULL_PCTL
    P(f"    EVENT IN WORDS: the null percentile is over {G2_EVENT_WORDS}.")
    P(f"    circular-shift null: {len(ks)} offsets on a {Ngrid}-week grid   "
      f"null weekly-mean mean ${null_shift.mean():,.2f} sd ${null_shift.std():,.2f}")
    P(f"    observed ${mean_w:,.2f} -> percentile {pctl_shift:.1f}  (debt-tightened bar {G2_NULL_PCTL})")
    ok_g2 = ok_g2a and ok_g2ci and ok_g2null

    # =================================================================== G2b — second null
    P("")
    P("=" * 118)
    P("=== G2b — second null computation; agreement judged TAIL-SIDE, never raw percentile distance")
    P("=" * 118)
    P(f"    {G2B_SECOND_WAY}.")
    n_blocks = int(np.ceil(Ngrid / BLOCK_WEEKS))
    blocks = [np.arange(i * BLOCK_WEEKS, min((i + 1) * BLOCK_WEEKS, Ngrid))
              for i in range(n_blocks)]
    rng_p = np.random.default_rng(PERM_SEED)
    null_perm = np.empty(N_PERM)
    for i in range(N_PERM):
        order = rng_p.permutation(n_blocks)
        idx = np.concatenate([blocks[b] for b in order])
        p3 = pd.DataFrame(vals[idx], index=piv.index, columns=piv.columns)
        o3 = RZ.sim_from_pivot(CZ, sub, p3, PRIMARY_TICKS)
        null_perm[i] = float(o3["net"].sum()) / Nw
    pctl_perm = RZ.pctl_of(mean_w, null_perm)
    side_shift = pctl_shift >= G2_NULL_PCTL
    side_perm = pctl_perm >= G2_NULL_PCTL
    ok_g2b = side_shift == side_perm
    P(f"    block-permutation null: {N_PERM} draws of {n_blocks} 13-wk blocks (seed {PERM_SEED})   "
      f"null weekly-mean mean ${null_perm.mean():,.2f} sd ${null_perm.std():,.2f}")
    P(f"    observed ${mean_w:,.2f} -> percentile {pctl_perm:.1f}")
    P(f"    TAIL-SIDE verdicts vs the {G2_NULL_PCTL} bar: shift={'ABOVE' if side_shift else 'BELOW'}  "
      f"perm={'ABOVE' if side_perm else 'BELOW'}  -> "
      f"{'AGREE' if ok_g2b else '*** SPLIT — INVALID-RUN ***'}")

    # =================================================================== G3 — static arms
    P("")
    P("=" * 118)
    P("=== G3 — MANDATORY victory over BOTH exposure-matched static arms (same sizing/costs/calendar)")
    P("=" * 118)
    stat_stats = {}
    for nm in ("LONG", "SHORT"):
        s = stat_wk[nm]
        shp = float(s.mean() / s.std(ddof=1) * np.sqrt(52)) if s.std(ddof=1) > 0 else 0.0
        stat_stats[nm] = (float(s.sum()), float(s.mean()), shp)
        P(f"    static {nm:<5} total net ${stat_stats[nm][0]:>12,.0f}   "
          f"weekly mean ${stat_stats[nm][1]:>8,.2f}   ann Sharpe {shp:>7.3f}")
    ok_g3_shL = sharpe_w > stat_stats["LONG"][2]
    ok_g3_shS = sharpe_w > stat_stats["SHORT"][2]

    xl = stat_wk["LONG"].to_numpy()
    X = np.column_stack([np.ones(Nw), xl])
    beta, *_ = np.linalg.lstsq(X, y_w, rcond=None)
    alpha = float(beta[0])
    resid = y_w - X @ beta
    r2 = 1.0 - resid.var() / np.var(y_w)
    rng_a = np.random.default_rng(BOOT_SEED_ALPHA)
    alphas = np.empty(N_BOOT)
    for i in range(N_BOOT):
        idx = RZ.block_boot_indices(Nw, rng_a)
        bb, *_ = np.linalg.lstsq(X[idx], y_w[idx], rcond=None)
        alphas[i] = bb[0]
    a_lo, a_hi = np.percentile(alphas, [2.5, 97.5])
    ok_g3_alpha = (a_lo > 0) or (a_hi < 0)          # spec literal: CI excludes 0
    ok_g3 = ok_g3_shL and ok_g3_shS and ok_g3_alpha
    P(f"    alpha regression pool ~ static-LONG: alpha ${alpha:,.2f}/wk   beta {beta[1]:+.3f}   R2 {r2:.3f}")
    P(f"    alpha 95% block-bootstrap CI [${a_lo:,.2f}, ${a_hi:,.2f}]   seed {BOOT_SEED_ALPHA}   "
      f"(spec clause: CI excludes 0; alpha sign {'+' if alpha > 0 else '-'})")
    P(f"    Sharpe: pool {sharpe_w:.3f} vs LONG {stat_stats['LONG'][2]:.3f} vs "
      f"SHORT {stat_stats['SHORT'][2]:.3f}")

    # =================================================================== G4 — eras
    P("")
    P("=" * 118)
    P("=== G4 — era signs; the 2022-26 cell DECIDES: negative modern = FAIL regardless of pooled total")
    P("=" * 118)
    era_rows = []
    for nm, a, b in ERAS:
        seg = out_p.loc[(out_p.index >= a) & (out_p.index <= b), "net"]
        cells = {"pool": float(seg.sum())}
        for r in PAIR:
            sr = arm_daily[r].loc[(arm_daily[r].index >= a) & (arm_daily[r].index <= b), "net"]
            cells[r] = float(sr.sum())
        for snm in ("LONG", "SHORT"):
            ss = static_daily[snm].loc[(static_daily[snm].index >= a)
                                       & (static_daily[snm].index <= b), "net"]
            cells[snm] = float(ss.sum())
        era_rows.append((nm, cells, len(seg)))
        P(f"    {nm}: pool ${cells['pool']:>11,.0f} ({'+' if cells['pool'] > 0 else '-'})   "
          f"ZN ${cells['ZN']:>10,.0f}   ZB ${cells['ZB']:>10,.0f}   "
          f"staticL ${cells['LONG']:>11,.0f}   staticS ${cells['SHORT']:>11,.0f}   ({len(seg)} days)")
    modern = era_rows[2][1]["pool"]
    ok_g4 = modern > 0
    P(f"    2022-26 pool cell: ${modern:,.0f} -> {'POSITIVE through the bond bear' if ok_g4 else 'NEGATIVE modern era — the bull in disguise'}")
    yr = out_p["net"].groupby(out_p.index.year).sum()
    P("    pool net by year: " + "  ".join(f"{y}:{v:+,.0f}" for y, v in yr.items()))

    # =================================================================== G5 — cost
    P("")
    P("=== G5 — MODELED cost band [$4.36 RT commission + {1,2}-tick spread per leg]  BASIS: modeled, not measured")
    stress_cost = float(out_s["cost"].sum())
    P(f"    PRIMARY drag: ${tot_cost:,.0f} total   weekly cost ${tot_cost / Nw:,.2f}   "
      f"= {100 * tot_cost / max(abs(tot_gross), 1e-9):.1f}% of |gross|")
    P(f"    STRESS  drag: ${stress_cost:,.0f} total   weekly cost ${stress_cost / Nw:,.2f}")
    P(f"    weekly turnover (|dUnits|): {turno_w:.4f}")

    # =================================================================== G6 — battery
    P("")
    P("=== G6 — eval_battery: WEEKLY-VOL LEAD; fixed-DD/CDaR as DOLLAR DESCRIPTORS only; rho-to-P1")
    mdd_wk = max_drawdown(y_w)
    cdar_wk = cdar(y_w, alpha=0.95)
    P(f"    LEAD  weekly-vol annualized Sharpe = {sharpe_w:.3f}  (mean ${mean_w:,.2f}/wk, sd ${sd_w:,.0f}/wk)")
    P(f"    path descriptors ONLY (no DD-normalized income is quoted; the eval_battery thinning-placebo")
    P(f"    guard is honored by never reading those bases as a denominator):")
    P(f"        weekly maxDD ${mdd_wk:,.0f}   weekly CDaR95 ${cdar_wk:,.0f}")
    p1 = pd.read_csv(P1_DAILY_CSV, index_col=0, parse_dates=True)["p1_usd"]
    cal = out_p.index[(out_p.index >= p1.index.min()) & (out_p.index <= p1.index.max())]
    p1_al = p1.reindex(cal).fillna(0.0)
    us_al = out_p["net"].reindex(cal).fillna(0.0)
    rho_d = float(np.corrcoef(p1_al.to_numpy(), us_al.to_numpy())[0, 1])
    p1_w = p1_al.groupby(p1_al.index.to_period("W")).sum()
    us_w = us_al.groupby(us_al.index.to_period("W")).sum()
    rho_w = float(np.corrcoef(p1_w.to_numpy(), us_w.to_numpy())[0, 1])
    P(f"    rho to P1 (SOURCE: runs/WE_W56_BREADTH/out/p1_daily.csv, zero-filled common calendar "
      f"{cal.min().date()}..{cal.max().date()}, {len(cal)} sessions):")
    P(f"        daily rho = {rho_d:+.4f}   weekly rho = {rho_w:+.4f}   (spec expectation: ~-0.05 class)")

    # =================================================================== GATE TABLE
    rows = [
        ("HASH  machinery == G00074 recorded", "4 files byte-identical", "see audit above",
         ok_hash),
        ("UT    s6/s7 unit tests", "telescope+basis+causality", "all pass", ok_units),
        ("SEAL  max session < 2026-08-01", "< 2026-08-01", f"{seal_max.date()}", ok_seal),
        ("CAUS  two-sided causality probe", "future<1e-12, past>1e-9", "see probe above",
         ok_causal),
        ("RECON-A pool == armZN + armZB", "max weekly |d| < 1e-6", f"${recA:.2e}", ok_recA),
        ("RECON-B arms == G00074 controls", "596 weeks, |d| < 1e-6",
         f"{len(g74)} wks, ${recB:.2e}", ok_recB),
        ("RECON-C pivot == direct simulate", "|d net| < 1e-6", f"${rec_diff:.2e}", ok_recC),
        ("G1    MDE printed before observed", "printed",
         f"MDE ${mde_mean:,.0f}/wk over {Nw} wks", True),
        ("G2a   pool after-cost weekly mean > 0", "> $0", f"${mean_w:,.2f}", ok_g2a),
        ("G2ci  95% block-boot CI excludes 0", "CI_lo > 0",
         f"[${ci_lo:,.2f}, ${ci_hi:,.2f}]", ok_g2ci),
        (f"G2n   circular-shift null at {G2_NULL_PCTL}", f">= {G2_NULL_PCTL} pctl (debt bar)",
         f"{pctl_shift:.1f}", ok_g2null),
        ("G2b   second-null TAIL-SIDE agreement", "both ABOVE or both BELOW the bar",
         f"shift {pctl_shift:.1f} / perm {pctl_perm:.1f}: "
         f"{'AGREE' if ok_g2b else 'SPLIT'}", ok_g2b),
        ("G3a   pool Sharpe > static-LONG", f"> {stat_stats['LONG'][2]:.3f}",
         f"{sharpe_w:.3f}", ok_g3_shL),
        ("G3b   pool Sharpe > static-SHORT", f"> {stat_stats['SHORT'][2]:.3f}",
         f"{sharpe_w:.3f}", ok_g3_shS),
        ("G3c   alpha vs static-LONG, CI excl. 0", "CI excludes 0",
         f"${alpha:,.2f}/wk, CI [${a_lo:,.2f}, ${a_hi:,.2f}]", ok_g3_alpha),
        ("G4    modern era (2022-26) not negative", "pool 2022-26 cell > 0",
         f"${modern:,.0f}", ok_g4),
        ("G5    cost band printed", "drag + turnover",
         f"1tk ${tot_cost / Nw:,.0f}/wk, 2tk ${stress_cost / Nw:,.0f}/wk", None),
        ("G6    battery + rho-to-P1 printed", "weekly-vol lead; DD as $ only",
         f"S {sharpe_w:.2f}; maxDD ${mdd_wk:,.0f}; rho_w {rho_w:+.3f}", None),
    ]
    tbl = gate_table(rows, "GATES — GATE / SPEC / OBSERVED / PASS-FAIL "
                           "[2009-01-01 -> 2026-07-31, DISCOVERY_CONSUMED, MODELED costs]")

    # ---- mechanical decision rule (spec.yaml):
    #      G2+G2b+G3+G4(modern not negative) PASS -> candidate; any fail -> closed;
    #      split second-null verdict or machinery defect -> INVALID-RUN.
    invalid = not (ok_hash and ok_units and ok_seal and ok_causal and ok_recA and ok_recB
                   and ok_recC and ok_roots) or not ok_g2b
    if invalid:
        verdict, ledger = ("INVALID-RUN (split null verdict)" if not ok_g2b
                           else "INVALID-RUN"), "DEFECT"
    elif ok_g2 and ok_g2b and ok_g3 and ok_g4:
        verdict, ledger = "RATESCARRY01 ENGINE CANDIDATE (Class-P assessment next)", "PASS"
    else:
        verdict, ledger = "CLOSED AT SCOPE (completion note for G00074 s28 block)", "FAIL"
    P("")
    P("=" * 118)
    P(f"=== PREREGISTERED BINARY VERDICT: {verdict}   (ledger G00081: {ledger})")
    P("=" * 118)

    # ---- outputs
    with open(os.path.join(OUT, "gate_table.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(tbl) + "\n")
        f.write(f"\nPREREGISTERED BINARY VERDICT: {verdict}   (ledger G00081: {ledger})\n")
    wk_out = wk_p.copy()
    wk_out.insert(0, "first_day", wk_first)
    wk_out["net_stress2tk"] = wk_s_net.reindex(wk_out.index)
    wk_out["arm_zn_net"] = arm_wk["ZN"]
    wk_out["arm_zb_net"] = arm_wk["ZB"]
    wk_out.index.name = "week"
    wk_out.to_csv(os.path.join(OUT, "weekly_pnl.csv"))
    sa = pd.DataFrame({"pool_net": wk_p["net"], "static_long_net": stat_wk["LONG"],
                       "static_short_net": stat_wk["SHORT"]})
    sa.index.name = "week"
    sa.to_csv(os.path.join(OUT, "static_arms.csv"))
    et = pd.DataFrame([dict(era=nm, pool_net=c["pool"], zn_net=c["ZN"], zb_net=c["ZB"],
                            static_long_net=c["LONG"], static_short_net=c["SHORT"],
                            days=nd) for nm, c, nd in era_rows])
    et.to_csv(os.path.join(OUT, "era_table.csv"), index=False)
    json.dump({
        "run_id": "G3_RATESCARRY_20260906", "ledger": "G00081",
        "verdict": verdict, "ledger_result": ledger,
        "gates": [{"gate": n, "spec": s, "observed": o,
                   "pass": (None if k is None else bool(k))} for n, s, o, k in rows],
        "headline": {"n_weeks": Nw, "weekly_mean": mean_w, "weekly_sd": sd_w,
                     "ann_sharpe_weekly": sharpe_w, "total_net": tot_net,
                     "total_gross": tot_gross, "total_cost": tot_cost,
                     "stress_total_net": float(wk_s_net.sum()),
                     "ci_lo": float(ci_lo), "ci_hi": float(ci_hi),
                     "mde_weekly_mean": float(mde_mean),
                     "null_shift_pctl": pctl_shift, "null_shift_n_offsets": len(ks),
                     "null_perm_pctl": pctl_perm, "null_perm_draws": N_PERM,
                     "arm_zn_total": float(arm_wk["ZN"].sum()),
                     "arm_zb_total": float(arm_wk["ZB"].sum()),
                     "arm_zn_sharpe": float(arm_wk["ZN"].mean() / arm_wk["ZN"].std(ddof=1)
                                            * np.sqrt(52)),
                     "arm_zb_sharpe": float(arm_wk["ZB"].mean() / arm_wk["ZB"].std(ddof=1)
                                            * np.sqrt(52)),
                     "static_long": stat_stats["LONG"], "static_short": stat_stats["SHORT"],
                     "alpha_weekly": alpha, "alpha_ci": [float(a_lo), float(a_hi)],
                     "beta_long": float(beta[1]), "r2": float(r2),
                     "eras": {nm: c for nm, c, _ in era_rows},
                     "long_share": {r: float((Wpool.loc[Wpool['root'] == r, 'w_rank'] > 0)
                                             .mean()) for r in PAIR},
                     "weekly_maxdd": mdd_wk, "weekly_cdar95": cdar_wk,
                     "rho_p1_daily": rho_d, "rho_p1_weekly": rho_w,
                     "turnover_weekly": turno_w},
        "seeds": {"boot_mean": BOOT_SEED_MEAN, "boot_alpha": BOOT_SEED_ALPHA,
                  "perm": PERM_SEED, "shift_null": "deterministic all-offsets"},
        "evidence_status": "DISCOVERY_CONSUMED (arms observed as G00074 controls before "
                           "registration; debt priced by 97.5 bar + static-arm victory; "
                           "2026-06/07 segment BURNED-window, no forward claim)",
        "machinery_hashes_verified": EXPECTED_HASHES,
        "utc": datetime.now(timezone.utc).isoformat(),
    }, open(os.path.join(OUT, "ratescarry_verdict.json"), "w", encoding="utf-8"), indent=2)
    P("    outputs: out/gate_table.txt, out/weekly_pnl.csv, out/static_arms.csv, "
      "out/era_table.csv, out/ratescarry_verdict.json, out/ratescarry_console.txt")
    _fh.close()
    return ledger


if __name__ == "__main__":
    main()
