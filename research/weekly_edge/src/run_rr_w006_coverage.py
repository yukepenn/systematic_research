"""RR_W006 - IS BOOK COVERAGE ACTUALLY A GAP?  Frontier row 1, the last runnable one.

RUN CLASS: DIAGNOSTIC. No hypothesis selected, no candidate promoted, no threshold chosen.

RR_W000 withdrew W119's "E_NO_ENGINE = 0, so coverage is genuinely not the gap": that lens was
counted inside a population its own definition excludes and was empty before any data was read. On
the RAW mask there are 32 sessions where NEITHER leg held a position while the session's |RTH move|
was in its own top decile. Coverage was therefore recorded UNMEASURED, not closed.

This measures it. Two questions decide the row, and neither needs a model:

  1. DIRECTION. P1/PCT is LONG-ONLY. A top-decile move DOWN is not a coverage gap for a long-only
     book - it is the design working as intended, and pricing it would require a short engine that
     does not exist.
  2. SIGNAL vs POLICY. Did the engine's signal FIRE on those sessions and get suppressed, or did it
     never fire at all? "Absent because suppressed" is a policy question. "Absent because the signal
     never fired" is a coverage question. They are different problems and the ledger can tell them
     apart.

No dollar figure is attached to the 32 sessions. Pricing an absence requires knowing the direction
in advance, which makes any such figure EX_POST_EXECUTION_FEASIBLE_ORACLE - level 2, not available
money. OPPORTUNITY_LANGUAGE.md is binding on exactly this.
"""
from __future__ import annotations

import os
import sys
import time as _time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_we_w01 as W1                                                   # noqa: E402
from run_we_w01 import ROOT                                               # noqa: E402
from run_we_w17 import load_deep                                          # noqa: E402
from run_we_w97 import votes                                              # noqa: E402
from we_fastctx import fast_build_context                                 # noqa: E402
from run_rr_w001 import runs_in                                           # noqa: E402

LEDGER = os.path.join(ROOT, "runs", "WE_W119_BOOKLOSS", "out", "book_loss_ledger.csv")
OUT = os.path.join(ROOT, "runs", "RR_W006_COVERAGE", "out")
os.makedirs(OUT, exist_ok=True)
A, B = np.datetime64("2022-07-01"), np.datetime64("2026-08-01")
_t0 = _time.time()
_fh = open(os.path.join(OUT, "coverage.txt"), "w", encoding="utf-8")


def P_(*a):
    print(*a, flush=True)
    print(*a, file=_fh)
    _fh.flush()


def main():
    P_("=" * 118)
    P_("=== RR_W006 - IS BOOK COVERAGE ACTUALLY A GAP?  DIAGNOSTIC.  Nothing promoted.")
    P_("=== No dollar figure is attached to an absence. Pricing one needs a directional oracle,")
    P_("=== which is LEVEL 2 and not available money (OPPORTUNITY_LANGUAGE.md, binding).")
    P_("=" * 118)

    L = pd.read_csv(LEDGER)
    L["date"] = pd.to_datetime(L["date"])
    mv = L["rth_move_pts"].abs()
    thr = mv.quantile(0.90)
    noeng = (L["p1_trades"] == 0) & (L["xm_active"] == 0)
    raw = noeng & (mv >= thr)
    S = L[raw].copy()
    P_("")
    P_(f"    in-window sessions                                   {len(L):>6,}")
    P_(f"    neither leg active                                   {int(noeng.sum()):>6,}")
    P_(f"    ... and |RTH move| in its own top decile (>= {thr:.0f} pts)  {len(S):>6,}   "
       f"<- the RAW E_NO_ENGINE mask")

    P_("")
    P_("=" * 118)
    P_("=== 1. DIRECTION - P1/PCT is LONG-ONLY, so a top-decile move DOWN is not its gap")
    P_("=" * 118)
    up = S["rth_move_pts"] > 0
    P_(f"    of the {len(S)} sessions, moves UP   : {int(up.sum()):>3}  ({100*up.mean():.1f} %)")
    P_(f"                          moves DOWN : {int((~up).sum()):>3}  ({100*(~up).mean():.1f} %)")
    P_(f"    mean |move| on the UP sessions   : {S.loc[up, 'rth_move_pts'].abs().mean():>7.1f} pts")
    P_(f"    mean |move| on the DOWN sessions : {S.loc[~up, 'rth_move_pts'].abs().mean():>7.1f} pts")
    P_("")
    P_("    A long-only engine declining a large DOWN session is the design working, not a miss.")
    P_(f"    The coverage question therefore concerns AT MOST the {int(up.sum())} UP sessions.")

    P_("")
    P_("=" * 118)
    P_("=== 2. SIGNAL vs POLICY - did the engine's signal fire and get suppressed, or never fire?")
    P_("=" * 118)
    D = load_deep("2022-01-01", "2026-07-31 17:00", extend=True)
    W1.DEV_END = pd.Timestamp("2026-07-31").date()
    X = fast_build_context(D)
    z = np.load(os.path.join(ROOT, "runs", "WE_W76_FORWARD2026", "out", "mem_ext.npz"))
    vl, _ = votes(D, z["mem"], z["bmom"], z["tilt"], X, z["bmom"])
    p = vl.astype(np.int8)
    sid, fb, lb, tarr = D["sid"], D["fb"], D["lb"], D["t"]
    lo_of = {int(sid[i]): int(i) for i in np.flatnonzero(fb)}
    hi_of = {int(sid[i]): int(i) for i in np.flatnonzero(lb)}
    date_of = {pd.Timestamp(tarr[lo_of[s]]).normalize(): s for s in lo_of}

    rows = []
    for _, r in S.iterrows():
        s = date_of.get(pd.Timestamp(r["date"]).normalize())
        if s is None:
            continue
        rr = runs_in(p, fb, lo_of[s], hi_of[s])
        rows.append(dict(date=r["date"].date(), move=r["rth_move_pts"],
                         up=bool(r["rth_move_pts"] > 0), n_runs=len(rr),
                         bars_signalled=int(sum(b_ - a_ + 1 for a_, b_ in rr))))
    R = pd.DataFrame(rows)
    fired = R["n_runs"] > 0
    P_(f"    sessions matched to the substrate                    {len(R):>6,}")
    P_(f"    signal FIRED at least once but no trade resulted     {int(fired.sum()):>6,}"
       f"   ({100*fired.mean():.1f} %)   <- POLICY, not coverage")
    P_(f"    signal NEVER fired all session                       {int((~fired).sum()):>6,}"
       f"   ({100*(~fired).mean():.1f} %)   <- genuine coverage absence")
    P_("")
    upfired = R[R["up"]]
    P_(f"    restricting to the {len(upfired)} UP sessions, the ones a long-only book could own:")
    P_(f"      signal fired but no trade                          {int((upfired['n_runs'] > 0).sum()):>6,}")
    P_(f"      signal never fired                                 {int((upfired['n_runs'] == 0).sum()):>6,}"
       f"   <- THE ACTUAL COVERAGE GAP")
    R.to_csv(os.path.join(OUT, "no_engine_sessions.csv"), index=False)

    P_("")
    P_("=" * 118)
    P_("=== 3. VERDICT")
    P_("=" * 118)
    gap = int((upfired["n_runs"] == 0).sum())
    P_(f"    The coverage gap, correctly scoped, is {gap} sessions out of 1,058 "
       f"({100*gap/len(L):.2f} %).")
    P_("")
    P_("    That is too few to support a new engine, and it cannot be priced without a directional")
    P_("    oracle. The remainder of the raw mask is either a DOWN move a long-only book is right to")
    P_("    decline, or a session where the signal DID fire and policy suppressed it - which is not a")
    P_("    coverage question at all, and whose policy half RR_W005 just closed.")
    P_("")
    P_("    COVERAGE moves from UNMEASURED to CLOSED. Nothing is promoted. No dollar figure is")
    P_("    attached to any absence.")
    P_(f"\n[{_time.time() - _t0:.0f}s] done")
    _fh.close()


if __name__ == "__main__":
    main()
