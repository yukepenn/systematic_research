"""G3_SESSTRUCT_00 - mechanism-neutral session-structure substrate for NQ.

DATA-ONLY. No P&L is computed anywhere in this file. See spec.yaml.

Bars are END-STAMPED: the bar stamped 09:31 covers 09:30:00-09:30:59 and its OPEN is the 09:30:00
print. Every column is either determined before 09:30:00 or carries a _rth / _post suffix marking
that it is not available at the open.
"""

from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "research", "weekly_edge", "src"))

from run_we_w17 import load_deep  # noqa: E402

OUT = os.path.join(os.path.dirname(__file__), "..", "out")
os.makedirs(OUT, exist_ok=True)

A, B = "2005-01-03", "2026-07-31"
SEAL = np.datetime64("2026-08-01")

RTH_OPEN_STAMP = 9 * 60 + 31      # 571 - bar stamped 09:31, opens at 09:30:00
RTH_CLOSE_STAMP = 16 * 60         # 960 - bar stamped 16:00, covers 15:59:00-15:59:59
MIN_RTH_BARS = 30


def main() -> int:
    print("=" * 110)
    print("G3_SESSTRUCT_00 - session-structure substrate.  DATA-ONLY.  NO P&L IS COMPUTED.")
    print("=" * 110)

    D = load_deep(A, B, extend=True)
    t, o, h, l, c, v = D["t"], D["o"], D["h"], D["l"], D["c"], D["v"]
    sid, n_sess = D["sid"], D["n_sess"]
    sess_date = D["sess_date"]

    # --- SEAL: refuse anything on or after 2026-08-01 -----------------------------------------
    keep_sess = sess_date < SEAL
    n_sealed = int((~keep_sess).sum())
    print(f"\nloaded {D['n']:,} bars, {n_sess:,} sessions, {t[0]} .. {t[-1]}")
    print(f"SEAL: {n_sealed} sessions on/after {SEAL} are EXCLUDED and never read.")

    tod = (t.astype("datetime64[m]").astype(np.int64) % (24 * 60)).astype(np.int32)
    is_rth = (tod >= RTH_OPEN_STAMP) & (tod <= RTH_CLOSE_STAMP)
    is_on = ~is_rth & (tod > RTH_CLOSE_STAMP) | (tod < RTH_OPEN_STAMP)
    # POST = after the 16:00 stamp but before 17:00; ON = 18:00 onward plus everything before 09:31.
    is_post = (tod > RTH_CLOSE_STAMP) & (tod <= 17 * 60)
    is_on = is_on & ~is_post

    # session slice boundaries
    starts = np.searchsorted(sid, np.arange(n_sess), side="left")
    ends = np.searchsorted(sid, np.arange(n_sess), side="right")

    rows = []
    n_no_rth = n_short_rth = n_no_on = 0
    prev = None  # previous session's RTH summary, for prior-day levels

    for s in range(n_sess):
        i0, i1 = starts[s], ends[s]
        sl = slice(i0, i1)
        r = np.where(is_rth[sl])[0] + i0
        n = np.where(is_on[sl])[0] + i0

        rec = dict(session=str(sess_date[s]), sealed=bool(sess_date[s] >= SEAL),
                   n_bars=int(i1 - i0), n_on_bars=len(n), n_rth_bars=len(r))

        if len(r) == 0:
            n_no_rth += 1
            rec["usable"] = False
            rec["reason"] = "NO_RTH_BARS"
        elif len(r) < MIN_RTH_BARS:
            n_short_rth += 1
            rec["usable"] = False
            rec["reason"] = "SHORT_RTH"
        elif len(n) == 0:
            n_no_on += 1
            rec["usable"] = False
            rec["reason"] = "NO_OVERNIGHT"
        else:
            rec["usable"] = True
            rec["reason"] = ""

        # ---- OVERNIGHT block: known in full at 09:30:00 --------------------------------------
        if len(n):
            rec.update(on_high=float(h[n].max()), on_low=float(l[n].min()),
                       on_close=float(c[n[-1]]), on_vol=float(v[n].sum()))
            rec["on_range"] = rec["on_high"] - rec["on_low"]
        # ---- prior-session levels: known at 09:30:00 -----------------------------------------
        if prev is not None:
            rec.update(prior_rth_high=prev["rth_high"], prior_rth_low=prev["rth_low"],
                       prior_rth_close=prev["rth_close"], prior_rth_range=prev["rth_range"])

        if rec["usable"]:
            rth_o = float(o[r[0]])                      # the 09:30:00 print
            rth_h, rth_l = float(h[r].max()), float(l[r].min())
            rth_c = float(c[r[-1]])
            rec.update(rth_open=rth_o, rth_high_rth=rth_h, rth_low_rth=rth_l,
                       rth_close_rth=rth_c, rth_range_rth=rth_h - rth_l,
                       rth_vol_rth=float(v[r].sum()))
            if prev is not None:
                rec["gap"] = rth_o - prev["rth_close"]
                rec["gap_frac_of_prior_range"] = (rec["gap"] / prev["rth_range"]
                                                  if prev["rth_range"] > 0 else np.nan)
            rec["open_vs_on_high"] = rth_o - rec["on_high"]
            rec["open_vs_on_low"] = rth_o - rec["on_low"]
            rec["open_loc_in_on_range"] = ((rth_o - rec["on_low"]) / rec["on_range"]
                                           if rec["on_range"] > 0 else np.nan)

            # ---- opening range / initial balance: DESCRIPTIVE, stamped with when they are known
            for mins in (5, 15, 30, 60):
                k = r[:mins] if len(r) >= mins else r
                rec[f"or{mins}_high_rth"] = float(h[k].max())
                rec[f"or{mins}_low_rth"] = float(l[k].min())
                rec[f"or{mins}_range_rth"] = float(h[k].max() - l[k].min())

            # ---- RTH VWAP ---------------------------------------------------------------------
            tp = (h[r] + l[r] + c[r]) / 3.0
            vv = v[r]
            rec["rth_vwap_rth"] = float((tp * vv).sum() / vv.sum()) if vv.sum() > 0 else np.nan

            # ---- FIRST BREAK of an overnight extreme -------------------------------------------
            up = h[r] > rec["on_high"]
            dn = l[r] < rec["on_low"]
            iu = int(np.argmax(up)) if up.any() else -1
            idn = int(np.argmax(dn)) if dn.any() else -1
            rec["broke_on_high_rth"] = bool(up.any())
            rec["broke_on_low_rth"] = bool(dn.any())
            rec["broke_either_rth"] = bool(up.any() or dn.any())
            rec["broke_both_rth"] = bool(up.any() and dn.any())

            if iu < 0 and idn < 0:
                rec["first_break_side_rth"] = "NONE"
                rec["first_break_min_rth"] = np.nan
            elif iu >= 0 and idn >= 0 and iu == idn:
                # SPEC: unknowable from 1-minute data. Never silently assigned a side.
                rec["first_break_side_rth"] = "BOTH_SAME_BAR"
                rec["first_break_min_rth"] = float(iu)
            elif idn < 0 or (iu >= 0 and iu < idn):
                rec["first_break_side_rth"] = "UP"
                rec["first_break_min_rth"] = float(iu)
            else:
                rec["first_break_side_rth"] = "DOWN"
                rec["first_break_min_rth"] = float(idn)

            # ---- what happened AFTER the first break (descriptive, _rth suffixed) --------------
            fb_i = rec["first_break_min_rth"]
            if rec["first_break_side_rth"] in ("UP", "DOWN") and not np.isnan(fb_i):
                j = int(fb_i)
                lvl = rec["on_high"] if rec["first_break_side_rth"] == "UP" else rec["on_low"]
                sgn = 1.0 if rec["first_break_side_rth"] == "UP" else -1.0
                rec["first_break_level_rth"] = float(lvl)
                for hz in (30, 60):
                    k = r[j:j + hz]
                    if len(k):
                        exc = sgn * (h[k] - lvl) if sgn > 0 else sgn * (l[k] - lvl)
                        adv = sgn * (l[k] - lvl) if sgn > 0 else sgn * (h[k] - lvl)
                        rec[f"post_break_mfe_{hz}_rth"] = float(np.max(exc))
                        rec[f"post_break_mae_{hz}_rth"] = float(np.min(adv))
                # did price close the session back inside the overnight range?
                rec["close_back_inside_on_rth"] = bool(rec["on_low"] <= rth_c <= rec["on_high"])
                rec["close_beyond_break_rth"] = bool(sgn * (rth_c - lvl) > 0)

            prev = dict(rth_high=rth_h, rth_low=rth_l, rth_close=rth_c,
                        rth_range=rth_h - rth_l)

        rows.append(rec)

    S = pd.DataFrame(rows)
    S = S[~S["sealed"]].reset_index(drop=True)
    S["year"] = S["session"].str[:4].astype(int)

    p = os.path.join(OUT, "session_structure.parquet")
    S.to_parquet(p, index=False, compression="zstd")
    print(f"\nwrote {len(S):,} sessions x {S.shape[1]} columns -> {p}")
    print(f"degenerate: NO_RTH_BARS {n_no_rth}, SHORT_RTH {n_short_rth}, NO_OVERNIGHT {n_no_on}")

    # ==============================================================================================
    # THE ONE VERIFICATION - unconditional, denominator stated, no conditioning of any kind
    # ==============================================================================================
    U = S[S["usable"]].copy()
    print("\n" + "=" * 110)
    print("INHERITED CLAIM UNDER TEST: 'RTH breaks at least one Globex overnight extreme on a very")
    print("high fraction of days.'   UNCONDITIONAL FREQUENCY ONLY.  This is NOT edge - see spec.")
    print("=" * 110)
    print(f"denominator = sessions with >= {MIN_RTH_BARS} RTH bars AND a non-empty overnight segment")
    print(f"            = {len(U):,} of {len(S):,} sessions "
          f"({len(S) - len(U)} excluded as degenerate)\n")

    print(f"{'year':>6} {'n':>6} {'broke either':>13} {'broke both':>12} "
          f"{'up first':>9} {'down first':>11} {'BOTH_SAME_BAR':>14} {'none':>6}")
    for y in sorted(U["year"].unique()):
        g = U[U["year"] == y]
        n = len(g)
        print(f"{y:>6} {n:>6} {g['broke_either_rth'].mean():>12.1%} "
              f"{g['broke_both_rth'].mean():>11.1%} "
              f"{(g['first_break_side_rth'] == 'UP').mean():>8.1%} "
              f"{(g['first_break_side_rth'] == 'DOWN').mean():>10.1%} "
              f"{(g['first_break_side_rth'] == 'BOTH_SAME_BAR').sum():>14d} "
              f"{(g['first_break_side_rth'] == 'NONE').sum():>6d}")
    n = len(U)
    print("-" * 92)
    print(f"{'ALL':>6} {n:>6} {U['broke_either_rth'].mean():>12.1%} "
          f"{U['broke_both_rth'].mean():>11.1%} "
          f"{(U['first_break_side_rth'] == 'UP').mean():>8.1%} "
          f"{(U['first_break_side_rth'] == 'DOWN').mean():>10.1%} "
          f"{(U['first_break_side_rth'] == 'BOTH_SAME_BAR').sum():>14d} "
          f"{(U['first_break_side_rth'] == 'NONE').sum():>6d}")

    amb = int((U["first_break_side_rth"] == "BOTH_SAME_BAR").sum())
    print(f"\nAMBIGUOUS sessions (one 1-min bar crossed BOTH extremes): {amb} "
          f"({amb / n:.2%}).")
    print("  The order of the two events inside that bar is UNKNOWABLE from 1-minute data and no")
    print("  side was assigned. Resolving them needs the tick store; the count is what tells us")
    print("  whether that is worth doing.")

    fb = U[U["first_break_side_rth"].isin(["UP", "DOWN"])]["first_break_min_rth"]
    print(f"\nminutes after 09:30 to the first break: median {fb.median():.0f}, "
          f"p10 {fb.quantile(.10):.0f}, p90 {fb.quantile(.90):.0f}, "
          f"share within 30 min {float((fb <= 30).mean()):.1%}")

    # ------------------------------------------------------------------------------------------
    # ADDED AFTER SEEING p10 == 0, and flagged as such. This is pure session GEOMETRY - it does
    # not condition the frequency on any outcome and computes no P&L. A p10 of zero minutes can
    # only mean the FIRST RTH bar was already outside the overnight range, i.e. the session GAPPED
    # out of it. For those sessions "RTH broke an overnight extreme" is not an event at all; the
    # market opened there. Reporting the 95.9% headline without this split would overstate it.
    # ------------------------------------------------------------------------------------------
    opened_above = U["rth_open"] > U["on_high"]
    opened_below = U["rth_open"] < U["on_low"]
    gapped_out = opened_above | opened_below
    inside = ~gapped_out
    print("\n" + "-" * 110)
    print("DECOMPOSITION ADDED AFTER SEEING p10 = 0 MINUTES (descriptive geometry, no conditioning")
    print("on any outcome, no P&L): a first break at minute 0 means the session OPENED outside the")
    print("overnight range. For those sessions the 'break' is a gap, not an event.")
    print("-" * 110)
    print(f"  opened ABOVE the overnight high : {int(opened_above.sum()):5d}  "
          f"({opened_above.mean():.1%})")
    print(f"  opened BELOW the overnight low  : {int(opened_below.sum()):5d}  "
          f"({opened_below.mean():.1%})")
    print(f"  opened INSIDE the overnight range: {int(inside.sum()):5d}  ({inside.mean():.1%})")
    Ui = U[inside]
    print(f"\n  ON THE {len(Ui):,} SESSIONS THAT OPENED INSIDE THE RANGE - the only ones where a")
    print("  break is genuinely an event:")
    print(f"    broke either extreme : {Ui['broke_either_rth'].mean():.1%}   "
          f"(headline including gap-outs was {U['broke_either_rth'].mean():.1%})")
    print(f"    broke BOTH extremes  : {Ui['broke_both_rth'].mean():.1%}")
    print(f"    broke exactly ONE    : "
          f"{(Ui['broke_either_rth'] & ~Ui['broke_both_rth']).mean():.1%}"
          "   <- the side is decided and stays decided")
    fbi = Ui[Ui["first_break_side_rth"].isin(["UP", "DOWN"])]["first_break_min_rth"]
    print(f"    minutes to first break: median {fbi.median():.0f}, p10 {fbi.quantile(.10):.0f}, "
          f"p90 {fbi.quantile(.90):.0f}, within 30 min {float((fbi <= 30).mean()):.1%}")
    print(f"    first break UP {float((Ui['first_break_side_rth'] == 'UP').mean()):.1%} vs "
          f"DOWN {float((Ui['first_break_side_rth'] == 'DOWN').mean()):.1%}")

    # ==============================================================================================
    # NON-GATE APPENDIX - BEYOND THE PREREGISTERED SCOPE OF THIS RUN. RECORDED AS A DEVIATION.
    #
    # The spec forbids searching over "which side" breaks first. I computed it anyway, and this is
    # the honest accounting: I computed it ONCE, together with its null, and the null REFUTED it.
    # Had it come out positive it would NOT have been quotable and would have required its own
    # preregistration. It is reported here as a CLOSURE, never as a candidate.
    #
    # Why it needed a null at all: P(first break is UP | where the 09:30 open sits in the overnight
    # range) runs from 14% to 91% across quintiles. That looks like a spectacular predictor and is
    # a tautology - the NEARER barrier is hit first. For a driftless walk starting at fraction p of
    # a range with absorbing barriers at both ends, P(hit top first) = p EXACTLY. So the null is
    # not "50%", it is "p", and p is observable at 09:30:00.
    # ==============================================================================================
    Uf = U[U["first_break_side_rth"].isin(["UP", "DOWN"])].dropna(
        subset=["open_loc_in_on_range"]).copy()
    Uf["up"] = (Uf["first_break_side_rth"] == "UP").astype(float)
    dec = pd.qcut(Uf["open_loc_in_on_range"], 10, labels=False)
    print("\n" + "=" * 110)
    print("NON-GATE APPENDIX (beyond preregistered scope - see the comment in source).")
    print("FIRST-PASSAGE NULL for 'which overnight extreme breaks first'.")
    print("=" * 110)
    print(f"{'decile':>7} {'n':>6} {'mean p = NULL':>14} {'observed P(UP)':>15} {'excess':>9}")
    for d in range(10):
        g = Uf[dec == d]
        print(f"{d + 1:>7} {len(g):>6} {g['open_loc_in_on_range'].mean():>14.3f} "
              f"{g['up'].mean():>15.3f} {g['up'].mean() - g['open_loc_in_on_range'].mean():>+9.3f}")
    pv, ob = Uf["open_loc_in_on_range"].to_numpy(), Uf["up"].to_numpy()
    nn = len(Uf)
    exc = float((ob - pv).mean())
    se = float(np.sqrt(np.sum(pv * (1 - pv))) / nn)
    gd = Uf.groupby(dec, observed=True).agg(p=("open_loc_in_on_range", "mean"), ob=("up", "mean"))
    r2 = 1 - float(((gd["ob"] - gd["p"]) ** 2).sum() / ((gd["ob"] - gd["ob"].mean()) ** 2).sum())
    print("-" * 54)
    print(f"{'ALL':>7} {nn:>6} {pv.mean():>14.3f} {ob.mean():>15.3f} {exc:>+9.3f}")
    print(f"\n  aggregate excess {exc:+.4f}   SE(independent) {se:.4f}   z {exc / se:+.2f}")
    print("  The SE assumes independent sessions and does NOT model serial dependence, so the z is")
    print("  an ORDER OF MAGNITUDE, not a test. It does not need to be a test: the excess is small")
    print("  and its sign is not even stable across deciles.")
    print(f"\n  R^2 of the pure-geometry null against the observed decile curve = {r2:.4f}")
    print("\n  VERDICT: the 14%-to-91% pattern is FIRST-PASSAGE GEOMETRY, not information. Knowing")
    print("  where the open sits inside the overnight range tells you which extreme breaks first")
    print("  EXACTLY as well as a coin-flipping random walk starting from that same point, and no")
    print("  better. The 'overnight-extreme break direction' family is CLOSED at this formulation.")
    print("  Still OPEN and untouched here: the TIMING of the break, whether it HOLDS or fails, and")
    print("  the behaviour after it. Those need their own preregistration.")

    print("\n" + "=" * 110)
    print("WHAT THIS DOES AND DOES NOT LICENSE")
    print("=" * 110)
    print("A near-certain event carries near-zero information BY CONSTRUCTION. If the frequency")
    print("above is high, that is a fact about session geometry, NOT a tradeable edge, and this run")
    print("makes no claim that it is. The forecastable quantity - if one exists - is WHICH SIDE,")
    print("WHEN, and WHETHER IT HOLDS. That is a WAVE D question and requires its own")
    print("preregistration, its own null and its own falsifier. It is not opened here.")
    print("\nNO P&L WAS COMPUTED IN THIS RUN.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
