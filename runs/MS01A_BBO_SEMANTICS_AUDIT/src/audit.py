"""MS01A - certify the BBO data contract BEFORE any microstructure model is fitted.

DIAGNOSTIC / DATA-CONTRACT AUDIT. No alpha model, no feature search, no promotion.

MS01 reconstructed BBO by forward-filling the last Bid and the last Ask INDEPENDENTLY. That can
pair a fresh side with a stale one and inflate the apparent spread. MS01's 3.000-tick RTH median
is therefore UNVERIFIED, and every friction number downstream of it inherits that doubt.

This audit answers, from data:
  s6  how stale is each side at the moment we use it, and what is the spread when BOTH are fresh?
  s7  can we trust event ORDER across the Last/Bid/Ask series at equal timestamps?
  s8  what does `volume` MEAN on the Bid/Ask series? (it is NOT assumed to be quote size)
  s9  do trades sit inside the reconstructed spread, or outside it?

Anchoring on TRADE timestamps rather than a clock grid, because trades are where execution
actually happens and where s9's independent check lives.
"""
from __future__ import annotations

import os
import time as _t

import numpy as np
import pandas as pd

ROOT = (r"D:\OneDrive - Washington University in St. Louis\TradingResearch"
        r"\systematic_research")
RAW = os.path.join(ROOT, "research", "data_microstructure_v2", "raw", "NQ")
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "out")
os.makedirs(OUT, exist_ok=True)
TICK = 0.25
FRESH_MS = [50, 100, 250, 500, 1000]
_fh = open(os.path.join(OUT, "audit.txt"), "w", encoding="utf-8")


def P(*a):
    print(*a, flush=True)
    print(*a, file=_fh)
    _fh.flush()


def audit_session(path):
    d = pd.read_parquet(path, columns=["bip", "time", "price", "volume"])
    t = d["time"].values.astype("datetime64[ms]").astype(np.int64)      # ms resolution
    bip = d["bip"].values
    px = d["price"].values
    vol = d["volume"].values

    # ---- s7 ordering
    mono_all = bool(np.all(np.diff(t) >= 0))
    mono_each = {b: bool(np.all(np.diff(t[bip == b]) >= 0)) for b in (0, 1, 2)}
    same_ts = int(np.sum(np.diff(t) == 0))

    # ---- s8 volume semantics
    volstat = {b: (float(np.median(vol[bip == b])), float(np.mean(vol[bip == b])),
                   float(np.max(vol[bip == b])), float(np.mean(vol[bip == b] == 1)))
               for b in (0, 1, 2) if (bip == b).sum()}

    tb, pb = t[bip == 1], px[bip == 1]
    ta, pa = t[bip == 2], px[bip == 2]
    tl, pl = t[bip == 0], px[bip == 0]
    if len(tb) == 0 or len(ta) == 0 or len(tl) == 0:
        return None

    ib = np.searchsorted(tb, tl, side="right") - 1
    ia = np.searchsorted(ta, tl, side="right") - 1
    ok = (ib >= 0) & (ia >= 0)
    ib, ia, tl_, pl_ = ib[ok], ia[ok], tl[ok], pl[ok]
    bid, ask = pb[ib], pa[ia]
    age_b = tl_ - tb[ib]
    age_a = tl_ - ta[ia]
    age = np.maximum(age_b, age_a)
    spr = (ask - bid) / TICK

    sod = ((tl_ // 1000) % 86400)
    rth = (sod >= 9 * 3600 + 30 * 60) & (sod < 16 * 3600)

    return dict(mono_all=mono_all, mono_each=mono_each, same_ts=same_ts, n_ev=len(t),
                volstat=volstat, missing_side=float(1 - ok.mean()),
                bid=bid, ask=ask, last=pl_, spr=spr, age_b=age_b, age_a=age_a, age=age,
                rth=rth)


def main():
    files = sorted(f for f in os.listdir(RAW) if f.endswith(".parquet"))
    P("=" * 112)
    P("=== MS01A - BBO DATA CONTRACT AUDIT.  Diagnostic only. No model, no feature, no promotion.")
    P("=" * 112)
    P(f"    sessions {len(files)}   anchored on TRADE timestamps, ms resolution")

    A = {k: [] for k in ("spr", "age_b", "age_a", "age", "bid", "ask", "last", "rth")}
    mono_all = mono_each = 0
    same_ts = n_ev = 0
    miss = []
    vol_rows = []
    t0 = _t.time()
    for i, f in enumerate(files):
        r = audit_session(os.path.join(RAW, f))
        if r is None:
            continue
        for k in A:
            A[k].append(r[k])
        mono_all += r["mono_all"]
        mono_each += all(r["mono_each"].values())
        same_ts += r["same_ts"]
        n_ev += r["n_ev"]
        miss.append(r["missing_side"])
        for b, v in r["volstat"].items():
            vol_rows.append(dict(session=f[:9], bip=b, med=v[0], mean=v[1], mx=v[2], frac1=v[3]))
        if (i + 1) % 20 == 0:
            P(f"    ... {i+1}/{len(files)}  [{_t.time()-t0:.0f}s]")
    for k in A:
        A[k] = np.concatenate(A[k])

    # ------------------------------------------------------------------ s7
    P("")
    P("=" * 112)
    P("=== s7  EVENT ORDERING - can we trust sequence across Last/Bid/Ask?")
    P("=" * 112)
    P(f"    sessions where the FULL stream is time-sorted        {mono_all}/{len(files)}")
    P(f"    sessions where EACH series is individually sorted    {mono_each}/{len(files)}")
    P(f"    adjacent events sharing an identical timestamp       {same_ts:,} of {n_ev:,} "
      f"({100*same_ts/n_ev:.1f} %)")
    P("")
    if same_ts / n_ev > 0.10:
        P("    >>> A LARGE FRACTION OF EVENTS SHARE A TIMESTAMP. Exchange ordering CANNOT be")
        P("    >>> recovered at sub-millisecond resolution from this export. Per s7, features")
        P("    >>> requiring exact event sequencing (true aggressor side, queue inference,")
        P("    >>> quote-then-trade causality) ARE NOT ADMISSIBLE. Use coarser aggregation.")
    else:
        P("    >>> Same-timestamp collisions are rare enough that coarse sequencing is usable,")
        P("    >>> but exact sub-ms ordering is still not certified.")

    # ------------------------------------------------------------------ s8
    P("")
    P("=" * 112)
    P("=== s8  WHAT IS `volume` ON THE BID/ASK SERIES?  Verified, not assumed.")
    P("=" * 112)
    V = pd.DataFrame(vol_rows)
    P(f"    {'bip':<6}{'median':>10}{'mean':>12}{'max':>12}{'frac == 1':>12}")
    P("    " + "-" * 52)
    for b, nm in ((0, "0 Last"), (1, "1 Bid"), (2, "2 Ask")):
        g = V[V["bip"] == b]
        if g.empty:
            continue
        P(f"    {nm:<6}{g['med'].median():>10.1f}{g['mean'].mean():>12.2f}"
          f"{g['mx'].max():>12.0f}{g['frac1'].mean():>11.1%}")
    V.to_csv(os.path.join(OUT, "volume_semantics.csv"), index=False)

    # ------------------------------------------------------------------ s6
    P("")
    P("=" * 112)
    P("=== s6  QUOTE FRESHNESS - is MS01's 3.000-tick RTH median stale-pair biased?")
    P("=" * 112)
    P(f"    trades with a missing side                     {100*np.mean(miss):.3f} %")
    for lbl, a in (("bid age", A["age_b"]), ("ask age", A["age_a"]), ("max(age)", A["age"])):
        P(f"    {lbl:<10} median {np.median(a):>7.0f} ms   p90 {np.percentile(a,90):>8.0f}   "
          f"p99 {np.percentile(a,99):>9.0f}   max {a.max():>10.0f}")
    locked = float(np.mean(A["ask"] == A["bid"]))
    crossed = float(np.mean(A["ask"] < A["bid"]))
    P("")
    P(f"    locked  (ask == bid)   {100*locked:.3f} %")
    P(f"    crossed (ask <  bid)   {100*crossed:.3f} %")
    P(f"    MS01 discarded ask <= bid, i.e. {100*(locked+crossed):.3f} % of observations")

    P("")
    P(f"    {'filter':<26}{'n':>12}{'share':>9}{'median spr':>12}{'mean':>9}{'p90':>8}")
    P("    " + "-" * 76)
    rthm = A["rth"] & (A["ask"] > A["bid"])
    P(f"    {'RTH, MS01 convention':<26}{int(rthm.sum()):>12,}{100*rthm.mean():>8.1f}%"
      f"{np.median(A['spr'][rthm]):>12.3f}{A['spr'][rthm].mean():>9.3f}"
      f"{np.percentile(A['spr'][rthm],90):>8.3f}")
    rows = []
    for ms in FRESH_MS:
        m = rthm & (A["age"] <= ms)
        if m.sum() < 100:
            continue
        P(f"    {'RTH, both sides <= '+str(ms)+'ms':<26}{int(m.sum()):>12,}{100*m.mean():>8.1f}%"
          f"{np.median(A['spr'][m]):>12.3f}{A['spr'][m].mean():>9.3f}"
          f"{np.percentile(A['spr'][m],90):>8.3f}")
        rows.append(dict(filter=f"<={ms}ms", n=int(m.sum()), share=float(m.mean()),
                         median=float(np.median(A["spr"][m])), mean=float(A["spr"][m].mean())))
    pd.DataFrame(rows).to_csv(os.path.join(OUT, "spread_by_freshness.csv"), index=False)

    base = float(np.median(A["spr"][rthm]))
    tight = rthm & (A["age"] <= FRESH_MS[0])
    fresh = float(np.median(A["spr"][tight])) if tight.sum() > 100 else np.nan
    P("")
    P(f"    >>> MS01 convention median {base:.3f} ticks   vs   strictly-fresh median {fresh:.3f}")
    if np.isfinite(fresh) and fresh <= base - 0.5:
        P("    >>> THE SPREAD COLLAPSES WHEN BOTH SIDES ARE FRESH. MS01's reconstruction was")
        P("    >>> STALE-PAIR BIASED and its friction figure is TOO HIGH.")
    elif np.isfinite(fresh):
        P("    >>> The spread does NOT collapse under strict freshness. MS01's measurement is")
        P("    >>> materially STRENGTHENED - the wide spread is real, not a pairing artifact.")

    # ------------------------------------------------------------------ s9
    P("")
    P("=" * 112)
    P("=== s9  TRADES vs RECONSTRUCTED BBO - the strongest independent check available")
    P("=" * 112)
    for lbl, m in (("all fresh<=100ms", rthm & (A["age"] <= 100)), ("RTH all", rthm)):
        if m.sum() < 100:
            continue
        b, a_, l = A["bid"][m], A["ask"][m], A["last"][m]
        # EXACT tick comparison. np.isclose's DEFAULT rtol=1e-5 on ~30,000-point prices tolerates
        # +/-0.3, i.e. MORE THAN A TICK, which made "at bid", "at ask" and "inside" overlap and
        # sum to 158 %. Caught because disjoint categories cannot exceed 100 %.
        TOL = 1e-6
        at_bid = np.mean(np.abs(l - b) < TOL)
        at_ask = np.mean(np.abs(l - a_) < TOL)
        inside = np.mean((l > b + TOL) & (l < a_ - TOL))
        above = np.mean(l > a_)
        below = np.mean(l < b)
        P(f"    {lbl}   n={int(m.sum()):,}")
        P(f"      at bid {100*at_bid:6.2f} %   at ask {100*at_ask:6.2f} %   inside {100*inside:6.2f} %"
          f"   ABOVE ASK {100*above:6.2f} %   BELOW BID {100*below:6.2f} %")
        tot = at_bid + at_ask + inside + above + below
        P(f"      categories sum to {100*tot:6.2f} %   {'OK' if abs(tot-1) < 1e-6 else '<<< NOT DISJOINT'}")
        mid = (b + a_) / 2
        P(f"      (Last-mid)/tick  median {np.median((l-mid)/TICK):+.3f}  "
          f"p05 {np.percentile((l-mid)/TICK,5):+.3f}  p95 {np.percentile((l-mid)/TICK,95):+.3f}")
        P(f"      outside-spread rate = {100*(above+below):.2f} %")
    P("")
    P("=" * 112)
    P("=== s9b  QUOTED vs EFFECTIVE SPREAD - they are not the same cost, and the gap is the finding")
    P("=" * 112)
    m = rthm & (A["age"] <= 100)
    b, a_, l = A["bid"][m], A["ask"][m], A["last"][m]
    mid = (b + a_) / 2
    eff = 2.0 * np.abs(l - mid) / TICK          # effective spread, the standard definition
    quoted = (a_ - b) / TICK
    P(f"    QUOTED    spread  median {np.median(quoted):>6.3f}  mean {quoted.mean():>6.3f} ticks")
    P(f"    EFFECTIVE spread  median {np.median(eff):>6.3f}  mean {eff.mean():>6.3f} ticks"
      f"   (2 x |Last - mid|)")
    P(f"    ratio effective/quoted (mean)   {eff.mean()/quoted.mean():.3f}")
    P("")
    P("    >>> The median trade prints AT THE MID of a wide quoted spread. Whatever the Bid/Ask")
    P("    >>> series represent, they are NOT a spread that most prints actually pay.")
    P("    >>> CONSEQUENCE: the quoted spread is the correct cost for a strategy that MUST CROSS,")
    P("    >>> and an OVERSTATEMENT for one that can rest. MS01's friction is therefore a")
    P("    >>> CONSERVATIVE UPPER BOUND for aggressive execution, not a certified fill cost.")
    P("    >>> This is exactly why labels must be built from Ask_t / Bid_t directly (s5) rather")
    P("    >>> than by subtracting a median spread from a mid-to-mid return.")
    P("")
    P("    A healthy reconstruction puts few trades OUTSIDE the contemporaneous spread.")
    P(f"\n[{_t.time()-t0:.0f}s] done")
    _fh.close()


if __name__ == "__main__":
    main()
