"""FWD_BOOTSTRAP V2 - repair the estimator so that MONTE-CARLO NOISE and BLOCK-LENGTH
SENSITIVITY are separately identified, and so that "primary L=6" and "sensitivity L=6" are the
SAME NUMBER rather than two independent draws presented as one estimator.

--------------------------------------------------------------------------------------------
THE DEFECT IN V1, established by SOURCE-PROVENANCE GATE (locate artifact -> locate code ->
locate convention -> reproduce -> only then test alternatives), NOT by nearest-number matching:

    V1 primary:      rng = default_rng(SEED)   created ONCE, then consumed sequentially by
                     CPA -> CPB -> CPC. By CPC the stream has already been advanced.
    V1 sensitivity:  r2 = default_rng(SEED)    created FRESH inside every (checkpoint, L) cell.

    Reproduced exactly:   CPA  primary -14,532.45  sensitivity -14,532.45   diff     0.00
                          CPB  primary -12,777.46  sensitivity -12,880.56   diff   103.10
                          CPC  primary  -2,436.60  sensitivity  -1,605.09   diff  -831.51

    CPA agrees to the CENT because it is drawn first, while the primary stream is still fresh.
    That coincidence is what disguised the defect.

CONSEQUENCE, and it is the part that actually matters: at CPC two INDEPENDENT 40,000-replicate
estimates of the SAME quantity differ by $832, while V1's reported BLOCK-LENGTH SPREAD at CPC
was $568. V1's dependence-sensitivity table was, at that checkpoint, reporting MONTE-CARLO
NOISE. A sensitivity analysis whose signal is smaller than its own measurement error cannot
support the conclusion drawn from it.

--------------------------------------------------------------------------------------------
PREREGISTERED BEFORE ANY V2 NUMBER WAS COMPUTED:

  * TOLERANCE. The Monte-Carlo standard error of EVERY reported percentile, at EVERY
    checkpoint, must be <= $250. That is ~1.2 % of the $20,245 fixed-drawdown risk budget and
    far below the smallest gap between adjacent bands. Declared here, ahead of measurement, so
    that B cannot be chosen to make a threshold land somewhere convenient.

  * SEEDING. Deterministic child seeds keyed by (checkpoint, block_length[, batch]). The
    primary L=6 estimate and the sensitivity L=6 estimate therefore resolve to the SAME stream
    and must agree BIT-FOR-BIT. Asserted programmatically below; the script aborts otherwise.

  * TWO-STAGE B. Pilot at B0 = 40,000 with R = 40 independent batches to MEASURE the MC error,
    then set B_final from the measured error and the declared tolerance. B is chosen by a rule
    fixed in advance, not by inspecting where a band lands.

  * UNCHANGED FROM V1, deliberately: the weekly series, the frozen scaling k, the primary block
    length L = round(n^(1/3)), the sensitivity grid {3, 6, 12}, and the checkpoint definitions.
    This run repairs an ESTIMATOR. It does not touch the frozen strategy or re-choose a
    convention, and no sealed data is read.
"""
from __future__ import annotations

import os

import numpy as np
import pandas as pd

ROOT = (r"D:\OneDrive - Washington University in St. Louis\TradingResearch"
        r"\systematic_research")
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "out")
os.makedirs(OUT, exist_ok=True)

TARGET_DD = 20245.0
SEED = 20260827
MC_SE_TOLERANCE = 250.0        # dollars. DECLARED BEFORE MEASUREMENT.
B_PILOT = 40_000               # V1's replicate count, kept as the pilot
R_BATCH = 40                   # independent batches used to MEASURE the MC error
B_CAP = 2_000_000              # compute guard
CHUNK = 50_000                 # draw chunk size; fixed so large B stays deterministic
CHECKPOINTS = {"A": 60, "B": 126, "C": 252}
CP_ORD = {"A": 1, "B": 2, "C": 3}
SENS_L = (3, 6, 12)
PCTS = (1, 5, 25)

_fh = open(os.path.join(OUT, "bootstrap_v2.txt"), "w", encoding="utf-8")


def P(*a):
    print(*a, flush=True)
    print(*a, file=_fh)


def max_dd(cum):
    return float(np.max(np.maximum.accumulate(cum) - cum))


# ---------------------------------------------------------------------------- the estimator
def cum_draws(xt, n, w, L, B, seed_key):
    """Circular block bootstrap. ONE deterministic stream per seed_key, chunked so that large B
    stays inside memory WITHOUT changing the numbers: chunk boundaries are fixed by CHUNK."""
    rng = np.random.default_rng(seed_key)
    off = np.arange(L)[None, None, :]
    out = np.empty(B, dtype=np.float64)
    done = 0
    while done < B:
        m = min(CHUNK, B - done)
        nb = int(np.ceil(w / L))
        st = rng.integers(0, n, size=(m, nb))
        ix = (st[:, :, None] + off).reshape(m, -1)[:, :w]
        out[done:done + m] = xt[ix].sum(axis=1)
        done += m
    return out


def key(cp, L, batch=None):
    """Deterministic child seed. (checkpoint, block_length) alone for a REPORTED estimate;
    a fourth element for the pilot batches, so the two never collide."""
    return [SEED, CP_ORD[cp], L] if batch is None else [SEED, CP_ORD[cp], L, batch]


def main():
    d = pd.read_csv(os.path.join(ROOT, "runs/WE_W110_XMDIVERSE/out/weekly.csv"))
    d = d.rename(columns={d.columns[0]: "week"})
    x = d["p1"].values.astype(float)
    n = len(x)
    dd = max_dd(np.cumsum(x))
    k = TARGET_DD / dd
    xs = x * k
    xt = np.concatenate([xs, xs])
    L_PRIMARY = max(2, int(round(n ** (1 / 3))))

    P("=" * 104)
    P("=== FWD_BOOTSTRAP V2 - separating MONTE-CARLO NOISE from BLOCK-LENGTH SENSITIVITY")
    P("=== Repairs an ESTIMATOR. Frozen strategy untouched. No sealed data read.")
    P("=" * 104)
    P(f"    weekly observations         {n}   {d['week'].iloc[0]} -> {d['week'].iloc[-1]}  (ISO weeks)")
    P(f"    raw weekly mean             ${x.mean():>10,.2f}   <- canonical $1,394")
    P(f"    weekly maxDD (ISO-week)     ${dd:>10,.2f}   <- canonical $22,931, matches to $0.33")
    P(f"    FROZEN scaling k            {k:>10.6f}")
    P(f"    scaled weekly mean          ${xs.mean():>10,.2f}   <- canonical $1,230")
    P(f"    primary block length L      {L_PRIMARY:>10}   (= round(n^(1/3)), preregistered in V1)")
    P(f"    declared MC-SE tolerance    ${MC_SE_TOLERANCE:>10,.0f}   DECLARED BEFORE MEASUREMENT")

    # ------------------------------------------------------------------ 1. reproduce V1's bug
    P("")
    P("=" * 104)
    P("=== 1. THE V1 DEFECT, REPRODUCED FROM V1's OWN CODE PATH")
    P("=" * 104)
    P("    V1 primary used ONE rng consumed sequentially A->B->C; V1 sensitivity reset the seed")
    P("    in every cell. Re-running both literally:")
    v1rng = np.random.default_rng(SEED)
    P(f"\n    {'CP':<4}{'V1 primary L=6':>18}{'V1 sens L=6':>16}{'difference':>14}")
    P("    " + "-" * 52)
    for cp, sess in CHECKPOINTS.items():
        w = sess // 5
        nb = int(np.ceil(w / L_PRIMARY))
        st = v1rng.integers(0, n, size=(B_PILOT, nb))
        ix = (st[:, :, None] + np.arange(L_PRIMARY)[None, None, :]).reshape(B_PILOT, -1)[:, :w]
        a = float(np.percentile(xt[ix].sum(axis=1), 1))
        r2 = np.random.default_rng(SEED)
        nb2 = int(np.ceil(w / 6))
        st2 = r2.integers(0, n, size=(B_PILOT, nb2))
        ix2 = (st2[:, :, None] + np.arange(6)[None, None, :]).reshape(B_PILOT, -1)[:, :w]
        b = float(np.percentile(xt[ix2].sum(axis=1), 1))
        P(f"    {cp:<4}{a:>18,.2f}{b:>16,.2f}{a-b:>14,.2f}")
    P("\n    CPA agrees to the CENT - it is drawn FIRST, while the primary stream is fresh.")
    P("    That coincidence is exactly what disguised the defect at CPB and CPC.")

    # ------------------------------------------------------- 2. MEASURE the Monte-Carlo error
    P("")
    P("=" * 104)
    P("=== 2. HOW BIG IS MONTE-CARLO NOISE? - measured, not assumed")
    P(f"=== {R_BATCH} INDEPENDENT batches of B = {B_PILOT:,}, per (checkpoint, block length).")
    P("=" * 104)
    P(f"    {'CP':<4}{'L':>4}{'mean p01':>14}{'MC sd of p01':>15}{'MC sd p05':>13}"
      f"{'MC sd p25':>13}{'B needed':>12}")
    P("    " + "-" * 75)
    pilot, need = {}, {}
    for cp, sess in CHECKPOINTS.items():
        w = sess // 5
        for L in SENS_L:
            est = np.array([[np.percentile(cum_draws(xt, n, w, L, B_PILOT, key(cp, L, b)), q)
                             for q in PCTS] for b in range(R_BATCH)])
            se = est.std(axis=0, ddof=1)
            pilot[(cp, L)] = (est.mean(axis=0), se)
            # SE ~ 1/sqrt(B): B_needed = B_pilot * (worst SE / tolerance)^2
            bneed = int(np.ceil(B_PILOT * (se.max() / MC_SE_TOLERANCE) ** 2))
            need[(cp, L)] = bneed
            P(f"    {cp:<4}{L:>4}{est.mean(axis=0)[0]:>14,.0f}{se[0]:>15,.0f}{se[1]:>13,.0f}"
              f"{se[2]:>13,.0f}{bneed:>12,}")
    B_FINAL = min(B_CAP, max(need.values()))
    B_FINAL = int(np.ceil(B_FINAL / CHUNK) * CHUNK)
    P("")
    P(f"    >>> V1 reported single-batch numbers at B = {B_PILOT:,}. The MC sd of p01 there reaches")
    P(f"        ${max(v[1][0] for v in pilot.values()):,.0f} - LARGER than several of the")
    P("        block-length 'spreads' V1 attributed to dependence.")
    P(f"    >>> B_FINAL = {B_FINAL:,} by the preregistered rule (worst SE, tolerance "
      f"${MC_SE_TOLERANCE:,.0f}, cap {B_CAP:,}).")

    # -------------------------------------------------- 3. final bands, ONE estimator per cell
    P("")
    P("=" * 104)
    P("=== 3. CHECKPOINT BANDS at B_FINAL - empirical (primary) vs Gaussian (diagnostic)")
    P("=" * 104)
    mu, sd = xs.mean(), xs.std(ddof=1)
    from math import erf, sqrt
    rows, primary_cum = [], {}
    P(f"    {'CP':<4}{'wk':>4}{'expected':>11}   {'source':<10}{'p01 INVALID':>14}"
      f"{'p05 WATCH':>13}{'p25 HEALTHY':>14}{'P(cum<0)':>11}")
    P("    " + "-" * 92)
    for cp, sess in CHECKPOINTS.items():
        w = sess // 5
        cum = cum_draws(xt, n, w, L_PRIMARY, B_FINAL, key(cp, L_PRIMARY))
        primary_cum[cp] = cum
        e = [float(np.percentile(cum, q)) for q in PCTS]
        pneg = float((cum < 0).mean())
        g_mu, g_sd = mu * w, sd * np.sqrt(w)
        g = [g_mu + z * g_sd for z in (-2.3263, -1.6449, -0.6745)]
        pneg_g = 0.5 * (1 + erf((0 - g_mu) / (g_sd * sqrt(2))))
        P(f"    {cp:<4}{w:>4}{g_mu:>11,.0f}   {'EMPIRICAL':<10}{e[0]:>14,.0f}{e[1]:>13,.0f}"
          f"{e[2]:>14,.0f}{100*pneg:>10.1f}%")
        P(f"    {'':<4}{'':>4}{'':>11}   {'gaussian':<10}{g[0]:>14,.0f}{g[1]:>13,.0f}"
          f"{g[2]:>14,.0f}{100*pneg_g:>10.1f}%")
        P(f"    {'':<4}{'':>4}{'':>11}   {'DELTA':<10}{e[0]-g[0]:>14,.0f}{e[1]-g[1]:>13,.0f}"
          f"{e[2]-g[2]:>14,.0f}{100*(pneg-pneg_g):>+10.1f}%")
        rows.append(dict(checkpoint=cp, sessions=sess, weeks=w, block_length=L_PRIMARY,
                         B=B_FINAL, expected=round(g_mu, 2),
                         emp_p01=round(e[0], 2), emp_p05=round(e[1], 2), emp_p25=round(e[2], 2),
                         emp_p_neg=round(pneg, 5),
                         mc_se_p01=round(pilot[(cp, L_PRIMARY)][1][0] *
                                         np.sqrt(B_PILOT / B_FINAL), 2),
                         gauss_p01=round(g[0], 2), gauss_p05=round(g[1], 2),
                         gauss_p25=round(g[2], 2), gauss_p_neg=round(pneg_g, 5)))
    pd.DataFrame(rows).to_csv(os.path.join(OUT, "checkpoint_bands_v2.csv"), index=False)

    # --------------------------------- 4. block sensitivity, NET of the noise it is drawn from
    P("")
    P("=" * 104)
    P("=== 4. BLOCK-LENGTH SENSITIVITY - and whether it EXCEEDS its own measurement error")
    P("=== The V1 table could not answer this because it never measured its own MC error.")
    P("=" * 104)
    P(f"    {'CP':<4}" + "".join(f"{'L='+str(L):>13}" for L in SENS_L)
      + f"{'spread':>11}{'MC sd':>9}{'spread/MCsd':>13}   verdict")
    P("    " + "-" * 90)
    srows = []
    for cp, sess in CHECKPOINTS.items():
        w = sess // 5
        vals, ses = [], []
        for L in SENS_L:
            c = (primary_cum[cp] if L == L_PRIMARY
                 else cum_draws(xt, n, w, L, B_FINAL, key(cp, L)))
            vals.append(float(np.percentile(c, 1)))
            ses.append(pilot[(cp, L)][1][0] * np.sqrt(B_PILOT / B_FINAL))
        spread = max(vals) - min(vals)
        mcsd = float(np.mean(ses))
        ratio = spread / mcsd if mcsd > 0 else np.inf
        # a spread of two independent estimates has sd ~ sqrt(2)*MC sd; require 3x that
        real = spread > 3 * np.sqrt(2) * mcsd
        P(f"    {cp:<4}" + "".join(f"{v:>13,.0f}" for v in vals)
          + f"{spread:>11,.0f}{mcsd:>9,.0f}{ratio:>13.1f}   "
          + ("REAL dependence effect" if real else "WITHIN measurement noise"))
        srows.append(dict(checkpoint=cp, weeks=w, **{f"p01_L{L}": round(v, 2)
                                                    for L, v in zip(SENS_L, vals)},
                          spread=round(spread, 2), mc_sd=round(mcsd, 2),
                          spread_over_mcsd=round(ratio, 3), real_effect=bool(real)))
    pd.DataFrame(srows).to_csv(os.path.join(OUT, "block_sensitivity_v2.csv"), index=False)

    # ------------------------------- 4b. is the resampling space even big enough to resample?
    P("")
    P("=" * 104)
    P("=== 4b. SUPPORT SIZE - a circular block bootstrap with nb blocks over n starts has n^nb")
    P("===     distinct paths. Where that is small, the 'distribution' is a FINITE SET OF ATOMS")
    P("===     and a percentile of it is QUANTIZED, not merely noisy. More replicates cannot help.")
    P("=" * 104)
    P(f"    {'CP':<4}{'wk':>4}{'L':>4}{'blocks':>8}{'distinct paths':>18}{'B_FINAL':>10}   note")
    P("    " + "-" * 78)
    for cp, sess in CHECKPOINTS.items():
        w = sess // 5
        for L in SENS_L:
            nb = int(np.ceil(w / L))
            sup = float(n) ** nb
            note = ("DEGENERATE - enumerable, see below" if sup <= B_FINAL
                    else ("thin - each path drawn many times" if sup < 10 * B_FINAL else "ample"))
            P(f"    {cp:<4}{w:>4}{L:>4}{nb:>8}{sup:>18,.0f}{B_FINAL:>10,}   {note}")
    P("")
    P("    Where the support is enumerable the EXACT percentile is computable with ZERO Monte-Carlo")
    P("    error, so it is reported exactly rather than sampled:")
    for cp, sess in CHECKPOINTS.items():
        w = sess // 5
        for L in SENS_L:
            nb = int(np.ceil(w / L))
            if float(n) ** nb > B_FINAL:
                continue
            # Enumerate ALL n^nb paths. Blocks 0..nb-2 are full length L; the LAST block is
            # truncated to whatever is left, exactly as the sampler does. A first version of
            # this enumerated a SINGLE block and was only correct when nb == 1 - it reported
            # a 6-week sum as if it were CPA's 12-week path.
            tail = w - (nb - 1) * L
            full = np.array([xt[s:s + L].sum() for s in range(n)])          # full-length block
            part = np.array([xt[s:s + tail].sum() for s in range(n)])       # truncated last one
            tot = part.copy()
            for _ in range(nb - 1):
                tot = (full[:, None] + tot[None, :]).ravel()
            assert tot.size == n ** nb, f"enumeration size {tot.size} != {n}^{nb}"
            ex = float(np.percentile(tot, 1))
            samp = float(np.percentile(cum_draws(xt, n, w, L, B_FINAL, key(cp, L)), 1))
            P(f"      {cp} L={L}: EXACT p01 ${ex:>11,.2f}   sampled ${samp:>11,.2f}   "
              f"error ${samp-ex:>9,.2f}   ({n**nb:,} atoms)")
    P("")
    P("    >>> This is why CPA/L=12 showed a $961 MC sd on p05 in section 2 while its p25 sd was")
    P("    >>> only $48: the tail percentile is hopping between ADJACENT ATOMS of a 213-point")
    P("    >>> discrete distribution. That is a property of the DESIGN, not of the data, and it")
    P("    >>> means L=12 at a 12-week checkpoint is not a bootstrap at all - it is an enumeration")
    P("    >>> of the 213 twelve-week windows in the record. It is reported, not silently kept.")

    # ------------------------------------------------- 5. THE ASSERTION THE DIRECTIVE DEMANDS
    P("")
    P("=" * 104)
    P("=== 5. BLOCKING ASSERTION - primary L=6 and sensitivity L=6 must be ONE estimator")
    P("=" * 104)
    ok = True
    for cp, sess in CHECKPOINTS.items():
        w = sess // 5
        a = float(np.percentile(primary_cum[cp], 1))
        b = float(np.percentile(cum_draws(xt, n, w, L_PRIMARY, B_FINAL,
                                          key(cp, L_PRIMARY)), 1))
        same = (a == b)
        ok &= same
        P(f"    {cp:<4} primary ${a:>12,.4f}   sensitivity ${b:>12,.4f}   "
          f"{'IDENTICAL' if same else '*** MISMATCH ***'}")
    assert ok, "primary and sensitivity L=6 disagree - the V1 defect has NOT been repaired"
    P("\n    ASSERTION PASSES. Both paths resolve to the deterministic child seed")
    P("    [SEED, checkpoint_ordinal, block_length], so they are the SAME draw by construction")
    P("    rather than by luck of ordering. This assert now guards the design permanently.")
    _fh.close()


if __name__ == "__main__":
    main()
