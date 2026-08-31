"""G3_TAILPROBE_00 - DISCOVERY MODE A. EVERYTHING HERE IS `DISCOVERY_CONTAMINATED`.

Directive section 16 creates two modes and this run is explicitly MODE A: bounded exploration whose
ONLY purpose is to decide whether a LOCKED challenge is worth writing. No promotion can originate
here. No P&L number produced here is quotable as a result.

THE QUESTION (directive section 40)
-----------------------------------
NOT "which P1 trades should we delete" - exposure-reducing rules are 10 for 10 in the wrong
direction in this repo, and T2_P1SIZE01 already failed TWO alternative size maps built from the
SAME five quality features. Reparameterising that feature set again is prohibited before compute.

The only non-repetitive question left is: at decision time, is there NEW INFORMATION - information
P1's decision stack does not currently use at all - that marks the states with a larger right tail?

WHAT COUNTS AS NEW HERE
-----------------------
Session geometry from G3_SESSTRUCT_00: overnight range, overnight extremes, the gap, where the open
sits in the overnight range, prior-session levels. P1's 13-member vote stack, its range throttle,
its delta gate and its five quality features use NONE of these.

THE CAUSALITY CONSTRAINT THAT SHAPES THE WHOLE RUN
--------------------------------------------------
P1 trades around the clock and W79 measured that it takes ~59% of its net OVERNIGHT. The overnight
range is NOT COMPLETE until 09:30. So for a trade entered at 02:00, `on_high`/`on_low`/`gap` DO NOT
EXIST YET and using them would be a look-ahead of hours, not of one bar.

Therefore trades are SPLIT BY ENTRY TIME and the feature sets differ:
    entry before 09:30  ->  only prior-session features are admissible
    entry at/after 09:30 ->  overnight + gap + open-location features become admissible
Any run that pooled these would be measuring a leak, not an edge.

HOW THE SCAN IS PRICED
----------------------
Testing K features and reporting the best one is a scan. The null here is a MAX-STATISTIC
permutation null: the feature-to-session assignment is shuffled with CIRCULAR SHIFTS of the session
index (preserving serial dependence), the best |statistic| across ALL K features is recorded on each
draw, and the observed best is compared to that distribution. This prices the search, not a single
feature. A per-feature p-value is never reported alone.
"""

from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, ROOT)

OUT = os.path.join(os.path.dirname(__file__), "..", "out")
os.makedirs(OUT, exist_ok=True)

SESS = os.path.join(ROOT, "runs", "G3_SESSTRUCT_00_20260831", "out", "session_structure.parquet")
TRD = os.path.join(ROOT, "runs", "G2_AUG_INCUMBENT_READ_20260830", "out", "p1_trades_full.csv")

N_PERM = 2000
RNG = np.random.default_rng(20260831)

# Features known at 09:30:00. Split into those that need the overnight segment complete and those
# that do not. The distinction is the causality constraint above, not a preference.
PRIOR_ONLY = ["prior_rth_range", "prior_rth_close", "prior_rth_high", "prior_rth_low"]
NEEDS_0930 = ["on_range", "gap", "gap_frac_of_prior_range", "open_loc_in_on_range",
              "open_vs_on_high", "open_vs_on_low", "on_vol"]


def session_of(ts: pd.Timestamp) -> pd.Timestamp:
    """18:00 ET -> 17:00 ET session. A bar stamped after 18:00 belongs to the NEXT calendar day's
    session, matching load_deep's sess_date (session end date)."""
    d = ts.normalize()
    return d + pd.Timedelta(days=1) if ts.hour >= 18 else d


def main() -> int:
    print("=" * 108)
    print("G3_TAILPROBE_00 - DISCOVERY MODE A.  EVERYTHING BELOW IS DISCOVERY_CONTAMINATED.")
    print("No promotion may originate here. No number here is quotable as a result.")
    print("=" * 108)

    S = pd.read_parquet(SESS)
    S = S[S["usable"]].copy()
    S["sess"] = pd.to_datetime(S["session"])

    T = pd.read_csv(TRD)
    T["et"] = pd.to_datetime(T["et"])
    T["sess"] = T["et"].apply(session_of)
    T["ppc"] = T["pnl"] / T["qty"]           # per-contract: the size-invariant quantity
    T["tod"] = T["et"].dt.hour * 60 + T["et"].dt.minute

    n0 = len(T)
    T = T.merge(S, on="sess", how="inner")
    print(f"\nP1 trades {n0}, joined to a usable session: {len(T)} "
          f"({len(T)/n0:.1%}); unmatched {n0-len(T)} (holidays / degenerate sessions)")

    pre = T[T["tod"] < 9 * 60 + 30].copy()
    post = T[T["tod"] >= 9 * 60 + 30].copy()
    print(f"\nCAUSALITY SPLIT - the overnight range is not complete until 09:30:")
    print(f"  entered BEFORE 09:30 : {len(pre):5d} trades  "
          f"net/ctr ${pre.ppc.sum():>12,.0f}   ONLY prior-session features admissible")
    print(f"  entered AT/AFTER 09:30: {len(post):5d} trades  "
          f"net/ctr ${post.ppc.sum():>12,.0f}   overnight features become admissible")
    print("  Pooling these would measure a look-ahead of HOURS, not of one bar. They are not pooled.")

    results = []
    for label, df, feats in (("PRE_0930", pre, PRIOR_ONLY),
                             ("POST_0930", post, PRIOR_ONLY + NEEDS_0930)):
        if len(df) < 200:
            print(f"\n[{label}] only {len(df)} trades - skipped")
            continue
        y = df["ppc"].to_numpy(float)
        thr = np.quantile(y, 0.90)
        tail = (y >= thr).astype(float)           # the RIGHT TAIL, which is what carries P1
        sess_idx = pd.factorize(df["sess"])[0]    # for circular shifts that respect sessions

        print("\n" + "=" * 108)
        print(f"[{label}]  n={len(df)}  right tail = top decile of per-contract P&L "
              f"(threshold ${thr:,.0f}/ctr)")
        print(f"  the tail carries ${y[y >= thr].sum():,.0f} of ${y.sum():,.0f} total per-contract")
        print("=" * 108)
        print(f"{'feature':<28}{'n':>7}{'spearman':>10}{'tailQ1':>9}{'tailQ5':>9}{'Q5-Q1':>9}"
              f"{'|stat|':>9}")

        stats = {}
        for f in feats:
            if f not in df.columns:
                continue
            x = df[f].to_numpy(float)
            ok = np.isfinite(x) & np.isfinite(y)
            if ok.sum() < 200:
                continue
            xr = pd.Series(x[ok]).rank().to_numpy()
            yr = pd.Series(y[ok]).rank().to_numpy()
            sp = float(np.corrcoef(xr, yr)[0, 1])
            q = pd.qcut(pd.Series(x[ok]), 5, labels=False, duplicates="drop")
            t_ok = tail[ok]
            tq1 = float(t_ok[q == 0].mean()) if (q == 0).any() else np.nan
            tq5 = float(t_ok[q == q.max()].mean()) if (q == q.max()).any() else np.nan
            stat = abs(tq5 - tq1)
            stats[f] = dict(sp=sp, tq1=tq1, tq5=tq5, stat=stat, n=int(ok.sum()))
            print(f"{f:<28}{ok.sum():>7}{sp:>+10.4f}{tq1:>9.3f}{tq5:>9.3f}"
                  f"{tq5 - tq1:>+9.3f}{stat:>9.4f}")

        if not stats:
            continue
        best_f = max(stats, key=lambda k: stats[k]["stat"])
        best = stats[best_f]["stat"]

        # ---- MAX-STATISTIC CIRCULAR-SHIFT NULL: prices the scan, preserves dependence ----------
        uniq = np.unique(sess_idx)
        null = np.empty(N_PERM)
        feat_mat = {f: df[f].to_numpy(float) for f in stats}
        for b in range(N_PERM):
            shift = int(RNG.integers(1, len(uniq)))
            # map each session to a shifted session, then carry that session's FEATURES to it
            new_of = {s: uniq[(i + shift) % len(uniq)] for i, s in enumerate(uniq)}
            src = np.array([new_of[s] for s in sess_idx])
            # build a lookup from session -> row index (first row of that session)
            first = {}
            for i, s in enumerate(sess_idx):
                first.setdefault(s, i)
            take = np.array([first[s] for s in src])
            bmax = 0.0
            for f in stats:
                xs = feat_mat[f][take]
                ok = np.isfinite(xs)
                if ok.sum() < 200:
                    continue
                q = pd.qcut(pd.Series(xs[ok]), 5, labels=False, duplicates="drop")
                t_ok = tail[ok]
                if not (q == 0).any() or not (q == q.max()).any():
                    continue
                bmax = max(bmax, abs(float(t_ok[q == q.max()].mean())
                                     - float(t_ok[q == 0].mean())))
            null[b] = bmax

        p = float((null >= best).mean())
        print(f"\n  best feature: {best_f}  |Q5-Q1 tail-rate gap| = {best:.4f}")
        print(f"  MAX-STATISTIC circular-shift null over {len(stats)} features, {N_PERM} draws:")
        print(f"    null p50 {np.percentile(null,50):.4f}   p95 {np.percentile(null,95):.4f}   "
              f"p99 {np.percentile(null,99):.4f}")
        print(f"    p(best >= observed) = {p:.4f}   "
              f"-> {'SURVIVES the scan-priced null' if p < 0.05 else 'DOES NOT SURVIVE'}")
        results.append(dict(split=label, n=len(df), best_feature=best_f, best_stat=best,
                            p_maxstat=p, n_features=len(stats),
                            null_p95=float(np.percentile(null, 95))))

    # ==============================================================================================
    # STAGE 2 - THE NULL THAT ACTUALLY MATTERS: IS THIS INFORMATION, OR IS IT VOLATILITY SCALING?
    #
    # Every surviving feature above (on_range, gap, gap_frac, open_loc, open_vs_on_low) SCALES WITH
    # VOLATILITY. The right tail was defined on the POOLED per-contract P&L distribution. On a
    # high-volatility day EVERY trade has a larger |P&L|, so high-volatility days are mechanically
    # over-represented in a pooled top decile - with or without any information.
    #
    # That is the same failure mode as the first-passage tautology in G3_SESSTRUCT_00: a real,
    # monotone, highly significant relationship that a mechanism produces for free. The
    # circular-shift null CANNOT catch it, because the association it tests for genuinely exists.
    #
    # The discriminating test: rescale each trade's P&L by the session's OWN volatility, so the
    # tail is defined WITHIN volatility state rather than across it. If the features still mark the
    # tail, that is information. If they do not, it was scaling all along.
    # ==============================================================================================
    print("\n" + "=" * 108)
    print("STAGE 2 - VOLATILITY-NORMALISED TAIL. Is this information, or is it scaling?")
    print("=" * 108)
    stage2 = []
    for label, df, feats in (("POST_0930", post, PRIOR_ONLY + NEEDS_0930),):
        if len(df) < 200:
            continue
        vol = df["on_range"].to_numpy(float)
        ok0 = np.isfinite(vol) & (vol > 0)
        d2 = df[ok0].copy()
        yn = d2["ppc"].to_numpy(float) / vol[ok0]      # P&L per contract PER POINT of overnight range
        thr = np.quantile(yn, 0.90)
        tail = (yn >= thr).astype(float)
        print(f"  target = per-contract P&L / on_range  (n={len(d2)}, tail threshold {thr:.3f})")
        print(f"\n{'feature':<28}{'n':>7}{'spearman':>10}{'tailQ1':>9}{'tailQ5':>9}{'Q5-Q1':>9}")
        s2 = {}
        for f in feats:
            if f not in d2.columns:
                continue
            x = d2[f].to_numpy(float)
            ok = np.isfinite(x)
            if ok.sum() < 200:
                continue
            sp = float(np.corrcoef(pd.Series(x[ok]).rank(), pd.Series(yn[ok]).rank())[0, 1])
            q = pd.qcut(pd.Series(x[ok]), 5, labels=False, duplicates="drop")
            t_ok = tail[ok]
            tq1 = float(t_ok[q == 0].mean())
            tq5 = float(t_ok[q == q.max()].mean())
            s2[f] = abs(tq5 - tq1)
            print(f"{f:<28}{ok.sum():>7}{sp:>+10.4f}{tq1:>9.3f}{tq5:>9.3f}{tq5-tq1:>+9.3f}")
        bf = max(s2, key=lambda k: s2[k])
        best2 = s2[bf]

        # ------------------------------------------------------------------------------------
        # STAGE 2 NEEDS ITS OWN NULL. Comparing a volatility-NORMALISED statistic against the
        # RAW target's null threshold is invalid - different target, different distribution,
        # different null. Recomputing the max-statistic circular-shift null on THIS target.
        # ------------------------------------------------------------------------------------
        s_idx = pd.factorize(d2["sess"])[0]
        uniq2 = np.unique(s_idx)
        first2 = {}
        for i, s in enumerate(s_idx):
            first2.setdefault(s, i)
        fm2 = {f: d2[f].to_numpy(float) for f in s2}
        null2 = np.empty(N_PERM)
        for b in range(N_PERM):
            shift = int(RNG.integers(1, len(uniq2)))
            new_of = {s: uniq2[(i + shift) % len(uniq2)] for i, s in enumerate(uniq2)}
            take = np.array([first2[new_of[s]] for s in s_idx])
            bmax = 0.0
            for f in s2:
                xs = fm2[f][take]
                ok = np.isfinite(xs)
                if ok.sum() < 200:
                    continue
                q = pd.qcut(pd.Series(xs[ok]), 5, labels=False, duplicates="drop")
                t_ok = tail[ok]
                if not (q == 0).any() or not (q == q.max()).any():
                    continue
                bmax = max(bmax, abs(float(t_ok[q == q.max()].mean())
                                     - float(t_ok[q == 0].mean())))
            null2[b] = bmax
        p2 = float((null2 >= best2).mean())

        print(f"\n  best after volatility normalisation: {bf} = {best2:.4f}")
        print(f"  (best BEFORE normalisation was open_vs_on_low = 0.1170)")
        print(f"  MAX-STATISTIC circular-shift null ON THE NORMALISED TARGET, {N_PERM} draws:")
        print(f"    null p50 {np.percentile(null2,50):.4f}   p95 {np.percentile(null2,95):.4f}"
              f"   p99 {np.percentile(null2,99):.4f}")
        print(f"    p(best >= observed) = {p2:.4f}")
        stage2.append(dict(best=bf, stat=best2, p=p2))

        # The survival threshold is the NORMALISED null's own p95, not an arbitrary constant.
        p95_2 = float(np.percentile(null2, 95))
        print(f"\n  WHAT NORMALISATION DID TO EACH FEATURE (survival bar = normalised null p95 ="
              f" {p95_2:.4f}):")
        for f, raw in (("gap", 0.1102), ("gap_frac_of_prior_range", 0.0925),
                       ("open_loc_in_on_range", 0.0912), ("open_vs_on_high", 0.0123),
                       ("on_range", 0.0994), ("open_vs_on_low", 0.1170), ("on_vol", 0.0310),
                       ("prior_rth_range", 0.0304)):
            if f in s2:
                print(f"    {f:<26} raw {raw:.4f} -> normalised {s2[f]:.4f}   "
                      f"{'SURVIVES' if s2[f] > p95_2 else 'DEAD - was volatility scaling'}")
        if p2 < 0.05:
            print("\n  => A SCALE-FREE EFFECT SURVIVES. on_range and open_vs_on_low were volatility")
            print("     SCALING and are dead. What remains is the GAP / OPEN-LOCATION family, which")
            print("     is directional and scale-free by construction. That licenses a LOCKED Mode B")
            print("     challenge - and nothing else.")
        else:
            print("\n  => NOTHING survives once the scan is priced on the correct target. The Stage 1")
            print("     result was volatility scaling: P1's per-contract P&L is larger on more")
            print("     volatile sessions, which is arithmetic, not information.")

    print("\n" + "=" * 108)
    print("VERDICT - what this DISCOVERY probe licenses")
    print("=" * 108)
    pd.DataFrame(results).to_csv(os.path.join(OUT, "tailprobe_results.csv"), index=False)
    any_surv = any(r["p_maxstat"] < 0.05 for r in results)
    for r in results:
        print(f"  [{r['split']:<9}] best={r['best_feature']:<26} stat={r['best_stat']:.4f}  "
              f"scan-priced p={r['p_maxstat']:.4f}  over {r['n_features']} features")
    if any_surv:
        print("\n  At least one split survives its scan-priced null. That licenses EXACTLY ONE")
        print("  thing: writing a LOCKED (Mode B) challenge with the mechanism, sign, horizon and")
        print("  falsifier frozen BEFORE any economics. It does NOT license a size rule, a filter,")
        print("  a P&L figure, or a candidate. The effect size here is a TAIL-RATE GAP, not money.")
    else:
        print("\n  NOTHING survives the scan-priced null. Session geometry does NOT mark P1's right")
        print("  tail. This closes the 'new information for P1 sizing from session structure'")
        print("  direction at this formulation and SAVES a locked wave that would have failed.")
        print("  That is the intended use of Mode A.")
    print("\n  EVERY NUMBER IN THIS RUN IS DISCOVERY_CONTAMINATED. NO PROMOTION ORIGINATES HERE.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
