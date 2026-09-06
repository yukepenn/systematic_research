"""CARRY_SIGC_CONFIRM driver — two-phase, one-shot confirmation of the SI-vs-GC
relative-carry switch.  Executes DESIGN_FROZEN.md (sha 62d5a342...) EXACTLY.

PHASE A (dev window only, data < 2019-01-01 structurally): diff audit, s6/s7 unit
tests, R0a/R0b reproduction gates, R2 dev family table, null-machinery smoke on dev
data, MDE print.  Writes out/PHASE_A_PASS only if every Phase-A gate passes.

PHASE B (ONE-SHOT): refuses to start without PHASE_A_PASS; writes out/CONSUMED the
moment confirmation data is loaded; computes R1, G1-G8, dual nulls G4a/G4b, 9-pair
family, three cost arms, coverage clause, ANNEX (non-gating); prints the
GATE/SPEC/OBSERVED/PASS-FAIL table from the program; applies the binary decision rule.

The frozen construction lives in carry_confirm.py = carry_v1.py + exactly two
mechanical changes (contract load range 2017-2027; window constants 2018-01-02 /
2026-08-01).  Any other diff => INVALID-RUN, asserted below.
"""
from __future__ import annotations

import argparse
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
sys.path.insert(0, CV_SRC)
sys.path.insert(0, HERE)

import ncd_day as N                                                     # noqa: E402
import roll as R                                                        # noqa: E402

# ---- FROZEN BY DESIGN_FROZEN.md (sha 62d5a342...) -------------------------
SEAL = pd.Timestamp("2026-08-01")
W1_START, W1_END = pd.Timestamp("2019-01-02"), pd.Timestamp("2022-12-31")
W2_START, W2_END = pd.Timestamp("2023-01-02"), pd.Timestamp("2026-05-30")
HL_START, HL_END = W1_START, W2_END
ANNEX_START, ANNEX_END = pd.Timestamp("2026-06-01"), pd.Timestamp("2026-07-31")
G2_BAR = 0.45
G4A_PCTL = 95.0
G4_AGREE_PTS = 5.0
G5_RANK_MAX = 2
COVERAGE_REF = {"SI": 0.781, "GC": 0.734}          # CARRY00 measured fractions
COVERAGE_MIN_FRAC = 0.50                           # INVALID-RUN clause threshold
R0B_NET, R0B_NET_TOL = 286_211.0, 500.0
R0B_SHARPE, R0B_SHARPE_TOL = 0.932, 0.005
ABSENT_WEEKS_EXPECTED = {"2012-W49", "2013-W49"}
DEV_WEIGHT_ROWS = 3421
NULL_MIN_OFFSET = 26                               # k in [26, N-26], all offsets
BLOCK_WEEKS = 13
N_BLOCK_PERMS = 999                                # implementation choice, recorded
BLOCK_SEED = 20260906                              # implementation choice, recorded
PAIRS = [("equity_index", ("ES", "YM")), ("rates", ("ZN", "ZB")),
         ("metals", ("GC", "SI")), ("ags", ("ZC", "ZW")), ("ags", ("ZC", "ZM")),
         ("ags", ("ZC", "ZL")), ("ags", ("ZW", "ZM")), ("ags", ("ZW", "ZL")),
         ("ags", ("ZM", "ZL"))]
ALL_ROOTS = ["ES", "YM", "ZN", "ZB", "GC", "SI", "ZC", "ZW", "ZM", "ZL"]
FROZEN = ("GC", "SI")
EXPECTED_DIFF = {
    '-DEV_START, DEV_END = pd.Timestamp("2009-01-01"), pd.Timestamp("2019-01-01")',
    '+DEV_START, DEV_END = pd.Timestamp("2018-01-02"), pd.Timestamp("2026-08-01")',
    '-    for cid, r, m, y in N.contracts_for(root, 2009, 2019):',
    '+    for cid, r, m, y in N.contracts_for(root, 2017, 2027):',
}
G4A_EVENT_WORDS = ("the probability, under timing-destroyed signals that preserve "
                   "each series' serial structure and the family's cross-pair "
                   "dependence, of a HEADLINE net Sharpe at least as large as observed")
# ---------------------------------------------------------------------------

PASS_MARKER = os.path.join(OUT, "PHASE_A_PASS")
CONSUMED_MARKER = os.path.join(OUT, "CONSUMED")

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
        "carry_confirm.py": os.path.join(HERE, "carry_confirm.py"),
        "run_confirm.py": os.path.join(HERE, "run_confirm.py"),
        "spec.yaml": os.path.join(RUN, "spec.yaml"),
        "DESIGN_FROZEN.md": os.path.join(RUN, "DESIGN_FROZEN.md"),
        "carry_v1.py": os.path.join(CV_SRC, "carry_v1.py"),
        "ncd_day.py": os.path.join(ROOT, "research", "multi_market", "src", "ncd_day.py"),
        "roll.py": os.path.join(ROOT, "research", "multi_market", "src", "roll.py"),
    }
    return {k: sha256(v) for k, v in files.items()}


def diff_audit():
    """The confirmation module must differ from the dev module by EXACTLY the two
    sanctioned mechanical changes.  Anything else => INVALID-RUN."""
    a = open(os.path.join(CV_SRC, "carry_v1.py"), encoding="utf-8").read().splitlines()
    b = open(os.path.join(HERE, "carry_confirm.py"), encoding="utf-8").read().splitlines()
    d = [l for l in difflib.unified_diff(a, b, lineterm="")
         if l.startswith(("+", "-")) and not l.startswith(("+++", "---"))]
    ok = set(d) == EXPECTED_DIFF and len(d) == 4
    P("    diff(carry_v1.py -> carry_confirm.py):")
    for l in d:
        P(f"        {l}")
    P(f"    diff audit: {'PASS - exactly the two sanctioned changes' if ok else '*** FAIL - INVALID-RUN ***'}")
    return ok


class _Uni:
    """Temporarily set a module's UNIVERSE (the sanctioned single-sector wrapper)."""

    def __init__(self, mod, uni):
        self.mod, self.uni = mod, uni

    def __enter__(self):
        self.saved = self.mod.UNIVERSE
        self.mod.UNIVERSE = self.uni

    def __exit__(self, *a):
        self.mod.UNIVERSE = self.saved


def sharpe_of(net):
    sd = net.std()
    return float(net.mean() * 252 / (sd * np.sqrt(252))) if sd and sd > 0 else 0.0


def win(df, a, b):
    return df.loc[(df.index >= a) & (df.index <= b)]


def pair_sim(mod, panel10, sector, pair, ticks, W=None):
    sub = {r: panel10[r] for r in pair}
    with _Uni(mod, {sector: list(pair)}):
        if W is None:
            W = mod.weekly_weights(sub)
        out, gross, cost, UNITS, so = mod.simulate(sub, W, ticks)
    return W, out, UNITS


def ticks_for_arm(arm, pair):
    if arm == "PRIMARY":
        return 1.0
    if arm == "STRESS-A":
        return 2.0
    if arm == "STRESS-B":                      # SI 3 ticks, every other leg 1 tick
        return pd.Series({r: (3.0 if r == "SI" else 1.0) for r in pair})
    raise ValueError(arm)


# ------------------------------------------------------------------ null machinery
def weekly_grid(mod, sub, W, pair):
    """Full weekly weight pivot (CASH weeks = 0) on the pair's own calendar."""
    days = pd.DatetimeIndex(sorted(set().union(*[set(x.index) for x in sub.values()])))
    iso = days.isocalendar()
    wk = pd.Series([f"{y}-W{w:02d}" for y, w in zip(iso.year, iso.week)], index=days)
    first_day = wk.groupby(wk.values).apply(lambda s: s.index.min())
    fd = pd.DatetimeIndex(sorted(first_day.values))
    piv = W.pivot_table(index="effective_from", columns="root", values="w")
    # FROZEN-MODULE SEMANTICS: simulate() ffills through weeks with no row (a CASH
    # week PERSISTS the prior position). The grid must reproduce that exactly - the
    # k=0 reconstruction is asserted equal to the direct simulate before any use.
    piv = piv.reindex(index=fd, columns=list(pair)).ffill().fillna(0.0)
    return piv


def sim_from_pivot(mod, sub, sector, pair, piv, ticks):
    long = piv.stack().rename("w").reset_index()
    long.columns = ["effective_from", "root", "w"]
    with _Uni(mod, {sector: list(pair)}):
        out, *_ = mod.simulate(sub, long, ticks)
    return out


def null_distributions(mod, sub, sector, pair, piv, hl_slice):
    """G4a circular-shift null: all offsets k in [26, N-26] on the headline signal
    grid; P&L and costs recomputed per shift; returns (ks, sharpes, N)."""
    idx = piv.index
    starts = idx[idx <= HL_START]
    d0_start = starts.max() if len(starts) else idx.min()
    mask = (idx >= d0_start) & (idx <= HL_END)
    grid_pos = np.where(mask)[0]
    Nw = len(grid_pos)
    ks = list(range(NULL_MIN_OFFSET, Nw - NULL_MIN_OFFSET + 1))
    vals = piv.to_numpy()
    sh = []
    for k in ks:
        arr = vals.copy()
        arr[grid_pos] = np.roll(vals[grid_pos], k, axis=0)
        p2 = pd.DataFrame(arr, index=piv.index, columns=piv.columns)
        out = sim_from_pivot(mod, sub, sector, pair, p2, 1.0)
        sh.append(sharpe_of(win(out, *hl_slice)["net"]))
    return ks, np.array(sh), Nw, grid_pos


def block_perm_null(mod, sub, sector, pair, piv, grid_pos, hl_slice,
                    n_perms=N_BLOCK_PERMS, seed=BLOCK_SEED):
    """G4b: permute the headline signal grid in 13-week blocks, same P&L machinery."""
    vals = piv.to_numpy()
    g = vals[grid_pos]
    nb = int(np.ceil(len(g) / BLOCK_WEEKS))
    blocks = [g[i * BLOCK_WEEKS:(i + 1) * BLOCK_WEEKS] for i in range(nb)]
    rng = np.random.default_rng(seed)
    sh = []
    for _ in range(n_perms):
        order = rng.permutation(nb)
        perm = np.concatenate([blocks[j] for j in order], axis=0)
        arr = vals.copy()
        arr[grid_pos] = perm
        p2 = pd.DataFrame(arr, index=piv.index, columns=piv.columns)
        out = sim_from_pivot(mod, sub, sector, pair, p2, 1.0)
        sh.append(sharpe_of(win(out, *hl_slice)["net"]))
    return np.array(sh)


def pctl_of(obs, null):
    null = np.asarray(null, dtype=float)
    below = (null < obs - 1e-12).sum()
    ties = (np.abs(null - obs) <= 1e-12).sum()
    return float(100.0 * (below + 0.5 * ties) / len(null))


def gate_table(rows, title):
    P("")
    P("=" * 112)
    P(f"=== {title}")
    P("=" * 112)
    P(f"    {'GATE':<44} {'SPEC':<34} {'OBSERVED':<40} VERDICT")
    for name, spec, obs, ok in rows:
        v = "PASS" if ok else "*** FAIL ***"
        if ok is None:
            v = "REPORT-ONLY"
        P(f"    {name:<44} {spec:<34} {obs:<40} {v}")


# =============================================================== PHASE A
def phase_a():
    global _fh
    _fh = open(os.path.join(OUT, "phase_a.txt"), "w", encoding="utf-8")
    P("=" * 112)
    P("=== CARRY_SIGC_CONFIRM  PHASE A - dev-window reproduction.  NO data >= 2019-01-01 enters any frame.")
    P(f"=== run at {datetime.now(timezone.utc).isoformat()}")
    P("=" * 112)

    ok_diff = diff_audit()

    P("")
    P("=== s6/s7 UNIT TESTS")
    R.test_no_roll_telescopes()
    R.test_basis_invariance()
    R.test_roll_causality()
    ok_units = True                                 # asserts inside would have raised

    import carry_v1 as CV                           # dev module VERBATIM, never main()
    assert CV.DEV_END == pd.Timestamp("2019-01-01"), "dev module constant drifted"

    P("")
    P("=== building DEV panel (10 roots, dev module, structural truncation < 2019-01-01)")
    panel10 = {}
    for s, rs in CV.UNIVERSE.items():
        for r in rs:
            x = CV.build_root(r)
            if x is not None and len(x) > 200:
                panel10[r] = x
                P(f"    {r:<4} {s:<13} paired days {len(x):>6}  "
                  f"{x.index.min().date()} -> {x.index.max().date()}")
    assert max(x.index.max() for x in panel10.values()) < pd.Timestamp("2019-01-01")
    ok_roots = sorted(panel10) == sorted(ALL_ROOTS)

    # ---- R0a: construction identity vs the frozen dev artifact
    art = pd.read_csv(os.path.join(ROOT, "runs", "CARRY_V1_20260828", "out",
                                   "carry_v1_weights.csv"))
    W10 = CV.weekly_weights(panel10)
    m = art.merge(W10, on=["week", "root"], suffixes=("_a", "_b"), how="outer",
                  indicator=True)
    both = m["_merge"] == "both"
    dmax = max(float(np.nanmax(np.abs(m.loc[both, "w_rank_a"] - m.loc[both, "w_rank_b"]))),
               float(np.nanmax(np.abs(m.loc[both, "w_a"] - m.loc[both, "w_b"]))))
    ok_r0a = (len(art) == DEV_WEIGHT_ROWS and len(W10) == DEV_WEIGHT_ROWS
              and int(both.sum()) == DEV_WEIGHT_ROWS and dmax < 1e-9)
    obs_r0a = f"rows {len(W10)}/{len(art)}, matched {int(both.sum())}, max|dw| {dmax:.2e}"

    # ---- R0b: pair-wrapper identity + dev pair economics
    sub, Wp = ({r: panel10[r] for r in FROZEN}, None)
    Wp, outp, _ = pair_sim(CV, panel10, "metals", FROZEN, 1.0)
    art_m = art[art["root"].isin(FROZEN)]
    aw = set(art_m["week"])
    pw = set(Wp["week"])
    mm = art_m.merge(Wp, on=["week", "root"], suffixes=("_a", "_b"), how="inner")
    n_overlap = len(mm)
    n_match = int((np.abs(mm["w_rank_a"] - mm["w_rank_b"]) < 1e-9).sum())
    sign_contra = int((mm["w_rank_a"] * mm["w_rank_b"] < 0).sum())
    absent = aw.symmetric_difference(pw)
    net_p, sh_p = float(outp["net"].sum()), sharpe_of(outp["net"])
    ok_r0b = (n_match == n_overlap and n_overlap == 696 and sign_contra == 0
              and absent == ABSENT_WEEKS_EXPECTED
              and abs(net_p - R0B_NET) <= R0B_NET_TOL
              and abs(sh_p - R0B_SHARPE) <= R0B_SHARPE_TOL)
    obs_r0b = (f"w_rank {n_match}/{n_overlap}, sign-contra {sign_contra}, "
               f"absent {sorted(absent)}, net ${net_p:,.0f}, Sharpe {sh_p:.3f}")

    # ---- R2: dev family table (9 pairs, PRIMARY)
    P("")
    P("=== R2 - DEV family table (PRIMARY, dev window, research sizing)")
    P(f"    {'pair':<10} {'sector':<13} {'net':>14} {'Sharpe':>8}")
    fam = []
    for sec, pr in PAIRS:
        _, o, _ = pair_sim(CV, panel10, sec, pr, 1.0)
        fam.append((pr, sec, float(o["net"].sum()), sharpe_of(o["net"])))
        P(f"    {'/'.join(pr):<10} {sec:<13} ${fam[-1][2]:>13,.0f} {fam[-1][3]:>8.3f}")
    fam_sorted = sorted(fam, key=lambda t: -t[3])
    dev_rank = 1 + [i for i, t in enumerate(fam_sorted) if t[0] == FROZEN][0]
    ok_r2 = dev_rank == 1
    P(f"    frozen pair GC/SI dev rank by Sharpe: {dev_rank} of 9 (expected 1)")

    # ---- null-machinery SMOKE (dev window, engineering validation ONLY - no gate)
    P("")
    P("=== NULL-MACHINERY SMOKE (dev window, already-consumed data; validation only, NOT a gate)")
    piv = weekly_grid(CV, sub, Wp, FROZEN)
    with _Uni(CV, {"metals": list(FROZEN)}):
        pass
    o_rec = sim_from_pivot(CV, sub, "metals", FROZEN, piv, 1.0)
    rec_diff = abs(float(o_rec["net"].sum()) - net_p)
    P(f"    pivot-reconstruction net vs direct: |d| = ${rec_diff:.6f}  "
      f"{'OK' if rec_diff < 1e-6 else '*** MISMATCH ***'}")
    assert rec_diff < 1e-6, "pivot reconstruction drifted from direct simulate"
    dev_hl = (outp.index.min(), outp.index.max())
    idx = piv.index
    grid_pos = np.arange(len(idx))
    smoke_ok = True
    for k in (30, 60, 90):
        arr = piv.to_numpy().copy()
        arr[grid_pos] = np.roll(piv.to_numpy()[grid_pos], k, axis=0)
        p2 = pd.DataFrame(arr, index=piv.index, columns=piv.columns)
        o2 = sim_from_pivot(CV, sub, "metals", FROZEN, p2, 1.0)
        P(f"    smoke shift k={k}: Sharpe {sharpe_of(o2['net']):.3f} (dev observed {sh_p:.3f})")
    P("    smoke: block-perm x3")
    _ = block_perm_null(CV, sub, "metals", FROZEN, piv, grid_pos, dev_hl, n_perms=3,
                        seed=1)
    P("    null machinery exercised end-to-end on dev data: OK")

    # ---- MDE (committed in DESIGN_FROZEN.md s7, printed here)
    P("")
    P("=== MDE TABLE (committed in design s7)")
    P("    SE(annualized Sharpe) over 7.41y HEADLINE ~ 0.37 (H0) / 0.44 (at S~0.93)")
    P("    P(pass G2 | S=0.932) ~ 0.87 ; P(pass G2 | S=0) ~ 0.11 before other gates")
    P("    joint power ~ 0.65-0.70 if dev effect persists; ~0.3-0.45 at 40-50% decay")
    P("    false-pass ~ <=1-2% under H0 incl. family-rank clause")
    P("    smallest true Sharpe detectable at >=80% power ~ 0.8")
    P("    -> only a P1-class persistent effect passes; a halved edge most likely FAILS and closes")

    rows = [
        ("A-DIFF  module diff = 2 sanctioned changes", "exactly 2 lines changed",
         "see diff above", ok_diff),
        ("A-UT    s6/s7 unit tests", "all pass", "telescope+basis+causality pass", ok_units),
        ("A-ROOTS 10 dev roots built", "10 roots, >200 paired days",
         f"{len(panel10)} roots", ok_roots),
        ("R0a     construction identity", f"{DEV_WEIGHT_ROWS} rows match 100%",
         obs_r0a, ok_r0a),
        ("R0b     pair-wrapper identity + economics",
         f"696/696, absent={sorted(ABSENT_WEEKS_EXPECTED)}, ${R0B_NET:,.0f}+-{R0B_NET_TOL:.0f}, "
         f"{R0B_SHARPE}+-{R0B_SHARPE_TOL}", obs_r0b, ok_r0b),
        ("R2      dev family rank", "GC/SI rank 1 of 9", f"rank {dev_rank} of 9", ok_r2),
    ]
    gate_table(rows, "PHASE A GATES - GATE / SPEC / OBSERVED / PASS-FAIL")
    all_ok = all(bool(x[3]) for x in rows)
    P("")
    P(f"=== PHASE A: {'ALL GATES PASS -> Phase B may open the confirmation windows' if all_ok else 'FAILED -> ABORT, confirmation windows NOT opened'}")

    result = {"phase": "A", "all_pass": bool(all_ok),
              "gates": [{"gate": n, "spec": s, "observed": o, "pass": bool(k)}
                        for n, s, o, k in rows],
              "code_hashes": code_hashes(),
              "utc": datetime.now(timezone.utc).isoformat()}
    json.dump(result, open(os.path.join(OUT, "phase_a_result.json"), "w",
                           encoding="utf-8"), indent=2)
    if all_ok:
        with open(PASS_MARKER, "w", encoding="utf-8") as f:
            json.dump({"phase_a_pass": True, "code_hashes": result["code_hashes"],
                       "utc": result["utc"]}, f, indent=2)
        P(f"    PASS marker written: {PASS_MARKER}")
    _fh.close()
    return all_ok


# =============================================================== PHASE B
def phase_b():
    global _fh
    # ---- one-shot discipline
    if not os.path.exists(PASS_MARKER):
        print("PHASE_A_PASS missing - Phase B refuses to start.")
        sys.exit(2)
    marker = json.load(open(PASS_MARKER, encoding="utf-8"))
    hh = code_hashes()
    if marker["code_hashes"] != hh:
        print("code hash drift since Phase A - Phase B refuses to start.")
        sys.exit(2)
    if os.path.exists(CONSUMED_MARKER):
        print("CONSUMED marker exists - the confirmation windows are SPENT. Refusing.")
        sys.exit(2)

    _fh = open(os.path.join(OUT, "confirm.txt"), "w", encoding="utf-8")
    P("=" * 112)
    P("=== CARRY_SIGC_CONFIRM  PHASE B - ONE-SHOT confirmation.  Windows are spent by this execution.")
    P(f"=== run at {datetime.now(timezone.utc).isoformat()}")
    P("=" * 112)
    ok_diff = diff_audit()
    if not ok_diff:
        P("INVALID-RUN: module diff not sanctioned."); _fh.close(); sys.exit(3)

    import carry_confirm as CC
    assert CC.DEV_START == pd.Timestamp("2018-01-02"), "window constant wrong"
    assert CC.DEV_END == SEAL, "seal constant wrong"

    P("")
    P("=== building CONFIRMATION panel (10 roots, 2018-01-02 warmup, seal < 2026-08-01)")
    panel10 = {}
    for s, rs in CC.UNIVERSE.items():
        for r in rs:
            x = CC.build_root(r)
            if x is not None and len(x) > 200:
                panel10[r] = x
                P(f"    {r:<4} {s:<13} paired days {len(x):>6}  "
                  f"{x.index.min().date()} -> {x.index.max().date()}  "
                  f"median gap {x['gap'].median():.0f}mo")
    seal_max = max(x.index.max() for x in panel10.values())
    ok_seal = seal_max < SEAL
    assert ok_seal, "SEAL VIOLATION"
    P(f"    seal assert: max session {seal_max.date()} < 2026-08-01  PASS")
    ok_roots = sorted(panel10) == sorted(ALL_ROOTS)

    # confirmation data is loaded -> the windows are SPENT, mark now
    with open(CONSUMED_MARKER, "w", encoding="utf-8") as f:
        json.dump({"consumed": True, "utc": datetime.now(timezone.utc).isoformat(),
                   "code_hashes": hh}, f, indent=2)
    P(f"    CONSUMED marker written (windows spent): {CONSUMED_MARKER}")

    hl = (HL_START, HL_END)
    sub = {r: panel10[r] for r in FROZEN}

    # ---- R1 two-sided causality probe on the confirmation panel (frozen pair)
    with _Uni(CC, {"metals": list(FROZEN)}):
        CC._fh = _fh
        ok_r1 = CC.causality_probe(sub)
        CC._fh = None

    # ---- frozen pair, three cost arms
    Wp, out_p, UNITS_p = pair_sim(CC, panel10, "metals", FROZEN,
                                  ticks_for_arm("PRIMARY", FROZEN))
    _, out_sa, _ = pair_sim(CC, panel10, "metals", FROZEN,
                            ticks_for_arm("STRESS-A", FROZEN), W=Wp)
    _, out_sb, _ = pair_sim(CC, panel10, "metals", FROZEN,
                            ticks_for_arm("STRESS-B", FROZEN), W=Wp)

    hl_p, hl_sa, hl_sb = (win(o, *hl) for o in (out_p, out_sa, out_sb))
    w1_p, w2_p = win(out_p, W1_START, W1_END), win(out_p, W2_START, W2_END)
    net_hl, sh_hl = float(hl_p["net"].sum()), sharpe_of(hl_p["net"])
    net_w1, sh_w1 = float(w1_p["net"].sum()), sharpe_of(w1_p["net"])
    net_w2, sh_w2 = float(w2_p["net"].sum()), sharpe_of(w2_p["net"])
    net_sa, net_sb = float(hl_sa["net"].sum()), float(hl_sb["net"].sum())
    sh_sa, sh_sb = sharpe_of(hl_sa["net"]), sharpe_of(hl_sb["net"])
    drag_p = float(hl_p["cost"].sum() / max(hl_p["gross"].sum(), 1e-9))
    drag_sa = float(hl_sa["cost"].sum() / max(hl_sa["gross"].sum(), 1e-9))
    drag_sb = float(hl_sb["cost"].sum() / max(hl_sb["gross"].sum(), 1e-9))

    # ---- G8 static arms (matched unconditional controls, same calendar/sizing/costs)
    W_si = Wp.copy()
    W_si["w_rank"] = np.where(W_si["root"] == "SI", 1.0, -1.0)
    W_si["w"] = W_si["w_rank"] / (W_si["n_live_sectors"] * W_si["n_sector"])
    W_gc = Wp.copy()
    W_gc["w_rank"] = -W_si["w_rank"]
    W_gc["w"] = -W_si["w"]
    _, out_si, _ = pair_sim(CC, panel10, "metals", FROZEN, 1.0, W=W_si)
    _, out_gc, _ = pair_sim(CC, panel10, "metals", FROZEN, 1.0, W=W_gc)
    sh_static_si = sharpe_of(win(out_si, *hl)["net"])
    sh_static_gc = sharpe_of(win(out_gc, *hl)["net"])
    ok_g8 = (sh_hl > sh_static_si) and (sh_hl > sh_static_gc)

    # ---- family (9 pairs, 3 arms, per window) + G5
    P("")
    P("=== FAMILY TABLE - 9 same-sector pairs, identical wrapper, own calendars [PRE-FROZEN, MODELED costs]")
    fam_rows = []
    fam_store = {}
    for sec, pr in PAIRS:
        Wf, of_p, _ = pair_sim(CC, panel10, sec, pr, ticks_for_arm("PRIMARY", pr))
        _, of_a, _ = pair_sim(CC, panel10, sec, pr, ticks_for_arm("STRESS-A", pr), W=Wf)
        _, of_b, _ = pair_sim(CC, panel10, sec, pr, ticks_for_arm("STRESS-B", pr), W=Wf)
        h = win(of_p, *hl)
        row = dict(pair="/".join(pr), sector=sec,
                   hl_net_primary=float(h["net"].sum()),
                   hl_sharpe_primary=sharpe_of(h["net"]),
                   hl_drag_primary=float(h["cost"].sum() / max(h["gross"].sum(), 1e-9)),
                   w1_net_primary=float(win(of_p, W1_START, W1_END)["net"].sum()),
                   w1_sharpe_primary=sharpe_of(win(of_p, W1_START, W1_END)["net"]),
                   w2_net_primary=float(win(of_p, W2_START, W2_END)["net"].sum()),
                   w2_sharpe_primary=sharpe_of(win(of_p, W2_START, W2_END)["net"]),
                   hl_net_stressA=float(win(of_a, *hl)["net"].sum()),
                   hl_sharpe_stressA=sharpe_of(win(of_a, *hl)["net"]),
                   hl_net_stressB=float(win(of_b, *hl)["net"].sum()),
                   hl_sharpe_stressB=sharpe_of(win(of_b, *hl)["net"]))
        fam_rows.append(row)
        fam_store[pr] = (sec, Wf)
        P(f"    {row['pair']:<8} {sec:<13} HL net ${row['hl_net_primary']:>12,.0f}  "
          f"Sharpe {row['hl_sharpe_primary']:>7.3f}  W1 {row['w1_sharpe_primary']:>7.3f}  "
          f"W2 {row['w2_sharpe_primary']:>7.3f}  SA ${row['hl_net_stressA']:>12,.0f}  "
          f"SB ${row['hl_net_stressB']:>12,.0f}")
    fam_df = pd.DataFrame(fam_rows)
    fam_df["hl_rank_primary"] = fam_df["hl_sharpe_primary"].rank(ascending=False,
                                                                 method="min").astype(int)
    rank_frozen = int(fam_df.loc[fam_df["pair"] == "GC/SI", "hl_rank_primary"].iloc[0])
    ok_g5 = rank_frozen <= G5_RANK_MAX
    P("    note: STRESS-B is defined as 'SI 3 ticks / others 1 tick'; for pairs without SI it equals PRIMARY.")

    # ---- G4a dual nulls: circular shift, all offsets, shared set across pairs
    P("")
    P("=== G4a NULL - circular-shift (dependence-preserving), all offsets k in [26, N-26]")
    P(f"    EVENT IN WORDS: {G4A_EVENT_WORDS}.")
    piv_f = weekly_grid(CC, sub, Wp, FROZEN)
    o_rec = sim_from_pivot(CC, sub, "metals", FROZEN, piv_f, 1.0)
    rec_d = abs(sharpe_of(win(o_rec, *hl)["net"]) - sh_hl)
    assert rec_d < 1e-9, f"pivot reconstruction drifted: {rec_d}"
    ks_f, null_f, Nw_f, grid_pos_f = null_distributions(CC, sub, "metals", FROZEN,
                                                        piv_f, hl)
    pct_a = pctl_of(sh_hl, null_f)
    P(f"    frozen pair: N={Nw_f} headline weeks, {len(ks_f)} offsets, "
      f"null Sharpe mean {null_f.mean():+.3f} sd {null_f.std():.3f}, "
      f"observed {sh_hl:+.3f} -> percentile {pct_a:.1f}")
    fam_pctl = {}
    for sec, pr in PAIRS:
        if pr == FROZEN:
            fam_pctl["/".join(pr)] = pct_a
            continue
        sec_i, Wf = fam_store[pr]
        sub_i = {r: panel10[r] for r in pr}
        piv_i = weekly_grid(CC, sub_i, Wf, pr)
        ks_i, null_i, Nw_i, _ = null_distributions(CC, sub_i, sec_i, pr, piv_i, hl)
        obs_i = float(fam_df.loc[fam_df["pair"] == "/".join(pr),
                                 "hl_sharpe_primary"].iloc[0])
        fam_pctl["/".join(pr)] = pctl_of(obs_i, null_i)
        P(f"    {'/'.join(pr):<8} N={Nw_i} offsets={len(ks_i)} percentile "
          f"{fam_pctl['/'.join(pr)]:.1f} (same offset construction; shared set where N equal)")
    fam_df["hl_null_pctl_g4a"] = fam_df["pair"].map(fam_pctl)
    ok_g4a = pct_a >= G4A_PCTL

    # ---- G4b second computation: 13-week block permutation
    P("")
    P(f"=== G4b NULL - 13-week block permutation, {N_BLOCK_PERMS} draws, seed {BLOCK_SEED} (second computation of the same event)")
    null_b = block_perm_null(CC, sub, "metals", FROZEN, piv_f, grid_pos_f, hl)
    pct_b = pctl_of(sh_hl, null_b)
    agree = abs(pct_a - pct_b)
    P(f"    block-perm null mean {null_b.mean():+.3f} sd {null_b.std():.3f}, "
      f"observed {sh_hl:+.3f} -> percentile {pct_b:.1f}   |G4a-G4b| = {agree:.1f} pts")
    ok_g4b = agree <= G4_AGREE_PTS

    # ---- coverage INVALID-RUN clause
    P("")
    P("=== PAIRING-COVERAGE clause (INVALID-RUN if any window < 50% of CARRY00 fraction)")
    cached = N.cached_ids()
    cov_ok = True
    cov_report = {}
    for r in FROZEN:
        all_dates = set()
        for cid, _, m_, y_ in N.contracts_for(r, 2017, 2027):
            if cid not in cached:
                continue
            d = N.read_contract(cid)
            if d.empty:
                continue
            d = d[(d["date"] >= pd.Timestamp("2018-01-02")) & (d["date"] < SEAL)]
            all_dates.update(pd.DatetimeIndex(d["date"]))
        all_dates = pd.DatetimeIndex(sorted(all_dates))
        for wname, (a, b) in (("W1", (W1_START, W1_END)), ("W2", (W2_START, W2_END))):
            denom = int(((all_dates >= a) & (all_dates <= b)).sum())
            numer = int(((panel10[r].index >= a) & (panel10[r].index <= b)).sum())
            frac = numer / max(denom, 1)
            thr = COVERAGE_MIN_FRAC * COVERAGE_REF[r]
            okc = frac >= thr
            cov_ok &= okc
            cov_report[f"{r}_{wname}"] = frac
            P(f"    {r} {wname}: paired {numer}/{denom} = {frac:.3f}  "
              f"(threshold {thr:.3f}, CARRY00 ref {COVERAGE_REF[r]})  "
              f"{'OK' if okc else '*** INVALID-RUN TRIP ***'}")

    # ---- G7 diagnostics (REPORT-ONLY)
    P("")
    P("=== G7 DIAGNOSTICS (REPORT-ONLY, non-gating) [PRE-FROZEN, MODELED costs, research sizing]")
    yr = hl_p["net"].groupby(hl_p.index.year).sum()
    P("    net by year (PRIMARY):")
    for y in range(2019, 2027):
        if y in yr.index:
            tag = " (partial, Jan-May)" if y == 2026 else ""
            P(f"        {y}  ${yr[y]:>12,.0f}{tag}")
    pos_years = int((yr.reindex(range(2019, 2026)).fillna(0) > 0).sum())
    P(f"    positive complete years 2019-2025: {pos_years} of 7")
    turno = float(UNITS_p.diff().abs().sum(1).reindex(hl_p.index).mean())
    P(f"    turnover (mean daily |dUnits|, HEADLINE): {turno:.4f}")
    P(f"    cost/gross: PRIMARY {drag_p:.1%}  STRESS-A {drag_sa:.1%}  STRESS-B {drag_sb:.1%}")
    for r in FROZEN:
        for wname, (a, b) in (("W1", (W1_START, W1_END)), ("W2", (W2_START, W2_END))):
            g = panel10[r].loc[(panel10[r].index >= a) & (panel10[r].index <= b), "gap"]
            P(f"    realized gap {r} {wname}: median {g.median():.0f}mo "
              f"(dev median 2mo), mean {g.mean():.2f}mo")
    # long-SI state share and flips over headline weeks
    wsi = Wp[(Wp["root"] == "SI")].sort_values("effective_from")
    wsi_hl = wsi[(wsi["effective_from"] >= pd.Timestamp("2018-12-24"))
                 & (wsi["effective_from"] <= HL_END)]
    share_si = float((wsi_hl["w_rank"] > 0).mean())
    flips = int((np.sign(wsi_hl["w_rank"]).diff().abs() > 0).sum())
    P(f"    long-SI share of live headline weeks: {share_si:.1%} (dev 66.3%), "
      f"live weeks {len(wsi_hl)}, sign flips {flips} (dev 75)")
    # P&L split by state, with matched static controls on the same day masks
    pos_si = np.sign(UNITS_p["SI"].shift(1)).reindex(hl_p.index)
    for state, mask in (("long-SI", pos_si > 0), ("long-GC", pos_si < 0)):
        dsel = hl_p.loc[mask.fillna(False)]
        ctrl_si = win(out_si, *hl)["net"].loc[mask.fillna(False)]
        ctrl_gc = win(out_gc, *hl)["net"].loc[mask.fillna(False)]
        P(f"    {state} state: {len(dsel)} days, switch net ${dsel['net'].sum():>12,.0f} | "
          f"static-SI ctrl ${ctrl_si.sum():>12,.0f} | static-GC ctrl ${ctrl_gc.sum():>12,.0f}")
    P("    weekly P&L correlation vs P1/PCT: NOT-COMPUTED - no in-run P1 weekly P&L artifact "
      "exists in-repo; regenerating P1 is outside this run's frozen code surface (recorded).")

    # ---- ANNEX (non-gating, BURNED window)
    with open(os.path.join(OUT, "annex.txt"), "w", encoding="utf-8") as fa:
        fa.write("BURNED-WINDOW ANNEX 2026-06-01 -> 2026-07-31 [NON-GATING; the window is "
                 "globally BURNED; excluded from every gate]\n")
        for nm, o in (("PRIMARY", out_p), ("STRESS-A", out_sa), ("STRESS-B", out_sb)):
            ax = win(o, ANNEX_START, ANNEX_END)
            fa.write(f"  {nm:<9} days {len(ax):>3}  gross ${ax['gross'].sum():>10,.0f}  "
                     f"cost ${ax['cost'].sum():>8,.0f}  net ${ax['net'].sum():>10,.0f}\n")
        fa.write("Costs MODELED; research sizing; evidence status BURNED-ANNEX.\n")
    P("    ANNEX written to out/annex.txt (non-gating, not repeated here to keep the "
      "headline clean of burned-window numbers).")

    # ---- outputs
    daily = pd.DataFrame({"gross_primary": hl_p["gross"], "cost_primary": hl_p["cost"],
                          "net_primary": hl_p["net"], "net_stressA": hl_sa["net"],
                          "net_stressB": hl_sb["net"]})
    daily.to_csv(os.path.join(OUT, "sigc_daily_headline.csv"))
    fam_df.to_csv(os.path.join(OUT, "family_table.csv"), index=False)

    # ---- gate table
    ok_g1 = net_hl > 0
    ok_g2 = sh_hl >= G2_BAR
    ok_g3 = (net_w1 > 0) and (net_w2 > 0)
    ok_g6a = net_sa > 0
    ok_g6b = net_sb > 0
    rows = [
        ("R1   two-sided causality (confirm panel)", "future<1e-12, past>1e-9",
         "see probe above", ok_r1),
        ("SEAL max session < 2026-08-01", "< 2026-08-01", f"{seal_max.date()}", ok_seal),
        ("G1   HEADLINE PRIMARY net > 0", "> $0", f"${net_hl:,.0f}", ok_g1),
        ("G2   HEADLINE PRIMARY ann net Sharpe", ">= 0.45", f"{sh_hl:.3f}", ok_g2),
        ("G3   sign survival W1 AND W2", "net > 0 in each",
         f"W1 ${net_w1:,.0f} / W2 ${net_w2:,.0f}", ok_g3),
        ("G4a  circular-shift null percentile", ">= 95.0", f"{pct_a:.1f}", ok_g4a),
        ("G4b  block-perm agreement (5-pt clause)", f"|d| <= {G4_AGREE_PTS:.0f} pts",
         f"{pct_b:.1f} vs {pct_a:.1f}, |d|={agree:.1f}", ok_g4b),
        ("G5   family rank (selection pricing)", f"<= {G5_RANK_MAX} of 9",
         f"rank {rank_frozen} of 9", ok_g5),
        ("G6a  STRESS-A HEADLINE net > 0", "> $0", f"${net_sa:,.0f}", ok_g6a),
        ("G6b  STRESS-B HEADLINE net > 0", "> $0", f"${net_sb:,.0f}", ok_g6b),
        ("G8   switch beats BOTH static arms",
         "Sharpe > static-SI and > static-GC",
         f"{sh_hl:.3f} vs {sh_static_si:+.3f}/{sh_static_gc:+.3f}", ok_g8),
        ("COV  pairing coverage clause", ">= 50% of CARRY00 frac, all windows",
         "; ".join(f"{k} {v:.3f}" for k, v in cov_report.items()), cov_ok),
        ("G7   yearly diagnostic (REPORT-ONLY)", "reported",
         f"{pos_years}/7 positive years", None),
    ]
    gate_table(rows, "PHASE B GATES - GATE / SPEC / OBSERVED / PASS-FAIL "
                     "[HEADLINE 2019-01-02 -> 2026-05-30, PRE-FROZEN, MODELED costs]")

    # ---- binary decision rule (mechanical)
    invalid = (not ok_g4b) or (not cov_ok) or (not ok_diff) or (not ok_seal) \
        or (not ok_roots)
    blocking = [ok_r1, ok_g1, ok_g2, ok_g3, ok_g4a, ok_g5, ok_g6a, ok_g6b, ok_g8]
    if invalid:
        verdict = "INVALID-RUN"
        ledger = "DEFECT"
    elif all(blocking):
        verdict = "TRUE RV ENGINE CANDIDATE"
        ledger = "PASS"
    else:
        verdict = "ACCIDENTAL WINNER - PERMANENT CLOSURE"
        ledger = "FAIL"
    P("")
    P("=" * 112)
    P(f"=== PREREGISTERED BINARY VERDICT: {verdict}   (ledger G00070: {ledger})")
    P("=" * 112)

    json.dump({
        "run_id": "CARRY_SIGC_CONFIRM_20260906", "verdict": verdict,
        "ledger_result": ledger,
        "gates": [{"gate": n, "spec": s, "observed": o,
                   "pass": (None if k is None else bool(k))} for n, s, o, k in rows],
        "headline": {"net_primary": net_hl, "sharpe_primary": sh_hl,
                     "net_w1": net_w1, "sharpe_w1": sh_w1,
                     "net_w2": net_w2, "sharpe_w2": sh_w2,
                     "net_stressA": net_sa, "sharpe_stressA": sh_sa,
                     "net_stressB": net_sb, "sharpe_stressB": sh_sb,
                     "drag_primary": drag_p, "static_si_sharpe": sh_static_si,
                     "static_gc_sharpe": sh_static_gc,
                     "null_pctl_g4a": pct_a, "null_pctl_g4b": pct_b,
                     "family_rank": rank_frozen, "long_si_share": share_si,
                     "flips": flips, "positive_years_2019_2025": pos_years},
        "coverage": cov_report,
        "evidence_status": "PRE-FROZEN (spent by this execution); costs MODELED; research sizing",
        "utc": datetime.now(timezone.utc).isoformat(),
    }, open(os.path.join(OUT, "confirm_verdict.json"), "w", encoding="utf-8"), indent=2)
    P("    outputs: out/confirm.txt, out/confirm_verdict.json, out/family_table.csv, "
      "out/sigc_daily_headline.csv, out/annex.txt")
    _fh.close()
    return verdict


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", required=True, choices=["A", "B"])
    args = ap.parse_args()
    if args.phase == "A":
        ok = phase_a()
        sys.exit(0 if ok else 1)
    else:
        phase_b()
