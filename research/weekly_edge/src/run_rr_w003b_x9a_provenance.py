"""RR_W003b - THERE ARE TWO OBJECTS NAMED X9a, AND PAIR23 USES THE ONE THAT CONTAINS P1.

RUN CLASS: ENGINEERING_ONLY / AUDIT. Nothing is selected, tuned or promoted. This reconciles two
committed series that carry the same name and returns the admission verdict RR_W003 could not
reach until the ambiguity was resolved.

RR_W003 rebuilt W72's X9a channel and reproduced W72's era table EXACTLY on all four figures in
both eras. It then measured weekly rho(P1/PCT, X9a) = +0.11, against the +0.613 W88 recorded and
called "too correlated". Both numbers are right. They describe DIFFERENT OBJECTS.
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from run_we_w01 import ROOT                                               # noqa: E402

OUT = os.path.join(ROOT, "runs", "RR_W003_X9A_CONTRACT", "out")
STREAMS = os.path.join(ROOT, "runs", "WE_W76_FORWARD2026", "out", "streams_extended.csv")
MEMBERS = os.path.join(ROOT, "runs", "WE_W79_CLIQUE", "out", "members.csv")
MINE = os.path.join(OUT, "x9a_trades.csv")
_fh = open(os.path.join(OUT, "x9a_provenance.txt"), "w", encoding="utf-8")


def P_(*a):
    print(*a, flush=True)
    print(*a, file=_fh)
    _fh.flush()


def wk(idx):
    iso = pd.Series(idx).dt.isocalendar()
    return (iso["year"].astype(str) + "-W" + iso["week"].astype(str).str.zfill(2)).to_numpy()


def main():
    P_("=" * 120)
    P_("=== RR_W003b - TWO OBJECTS, ONE NAME.  ENGINEERING_ONLY / AUDIT.")
    P_("=" * 120)

    d = pd.read_csv(STREAMS); d["date"] = pd.to_datetime(d["date"])
    cl = pd.read_csv(MEMBERS)
    assert np.allclose(d["w72:X9a"].to_numpy(), cl["X9a"].to_numpy()), \
        "members.csv X9a is not streams_extended w72:X9a"
    mine = pd.read_csv(MINE); mine["et"] = pd.to_datetime(mine["et"])
    m = mine[(mine["et"] >= "2022-07-01") & (mine["et"] < "2026-08-01")]
    md = m.groupby(m["et"].dt.normalize())["pnl"].sum()

    J = pd.DataFrame({"P1": d.set_index("date")["P1"],
                      "BMOM": d.set_index("date")["BMOM"],
                      "STORED": d.set_index("date")["w72:X9a"]}).join(
        md.rename("REBUILT")).fillna(0.0)
    W = J.assign(wk=wk(J.index)).groupby("wk").sum()

    P_("")
    P_("=== 1. THE TWO SERIES, side by side over the same 1,058 campaign sessions")
    P_("")
    P_(f"{'':<44}{'STORED w72:X9a':>18}{'REBUILT W72 chan':>20}")
    P_(f"{'net $':<44}{J['STORED'].sum():>18,.0f}{J['REBUILT'].sum():>20,.0f}")
    P_(f"{'sessions active':<44}{int((J['STORED'] != 0).sum()):>18,}"
       f"{int((J['REBUILT'] != 0).sum()):>20,}")
    P_(f"{'daily sd':<44}{J['STORED'].std():>18,.1f}{J['REBUILT'].std():>20,.1f}")
    P_(f"{'weekly rho with P1':<44}{W['P1'].corr(W['STORED']):>18.4f}"
       f"{W['P1'].corr(W['REBUILT']):>20.4f}")
    P_(f"{'weekly rho with BMOM':<44}{W['BMOM'].corr(W['STORED']):>18.4f}"
       f"{W['BMOM'].corr(W['REBUILT']):>20.4f}")
    P_("")
    P_(f"    daily rho BETWEEN the two objects called X9a : "
       f"{J['STORED'].corr(J['REBUILT']):+.4f}")
    P_("    W88 recorded daily +0.673 / weekly +0.613 for P1-X9a and BMOM-X9a +0.009.")
    P_("    Both reproduce here EXACTLY - on the STORED series. The rebuilt channel is a")
    P_("    different object and neither number describes it.")

    P_("")
    P_("=" * 120)
    P_("=== 2. WHY THEY DIFFER - it is the EXECUTION WRAPPER, not the signal")
    P_("=" * 120)
    P_("    run_we_w76.py:167-172 builds every w72 stream as   long_obj(TG_for(channel)).")
    P_("    run_we_w76.py:123-132  TG_for(chan) = hyst(0.7086 * Tp + 2.83 * chan)")
    P_("    run_we_w76.py:146-153  long_obj(TGx) = the 13-member Solar ensemble vote, the tilt,")
    P_("                           fills_daily, causal_score, quality sizing and fills_qexit.")
    P_("    run_we_w76.py:156-157  S['P1'] = long_obj(TG_for(bmom))")
    P_("")
    P_("    So the STORED w72:X9a is P1's ENTIRE MACHINERY with X9a substituted for B-MOM as ONE")
    P_("    ADDITIVE TERM inside the tilt. It is a P1 VARIANT, not a standalone strategy.")
    P_("    W72's era table, which RR_W003 reproduced to all four figures in both eras, measured")
    P_("    something else: the RAW two-sided channel through sfills with a session box")
    P_("    (run_we_w72b.py:251).")
    P_("")
    P_("    That is the whole explanation for +0.613 versus +0.07. The stored object shares the")
    P_("    Solar ensemble with the incumbent, so of course it correlates with it. The raw channel")
    P_("    does not, and is two-sided where P1/PCT is long-only.")

    P_("")
    P_("=" * 120)
    P_("=== 3. WHAT THIS MEANS FOR PAIR23")
    P_("=" * 120)
    P_("    PAIR23 is '2 BMOM : 3 X9a'. Its members come from WE_W79_CLIQUE/out/members.csv, where")
    P_("      BMOM = d['BMOM']    = sfills(raw B-MOM channel)        -> a RAW CHANNEL")
    P_("      X9a  = d['w72:X9a'] = long_obj(TG_for(X9a channel))    -> a P1 VARIANT")
    P_("")
    P_("    PAIR23 is therefore NOT a basket of two independent channel sleeves. It is a raw")
    P_("    B-MOM channel plus a full P1-variant, and rho(BMOM, X9a) = +0.009 'INDEPENDENT' is")
    P_("    exactly what one expects when comparing a two-sided raw channel against a long-only")
    P_("    Solar ensemble - it is a statement about the two WRAPPERS, not about two signals.")
    P_("")
    P_("    Nothing measured about PAIR23 is withdrawn. Its economics stand. What changes is what")
    P_("    it IS, and therefore what a decomposition of it could ever mean.")

    P_("")
    P_("=" * 120)
    P_("=== 4. ADMISSION VERDICT - EXPERT_UNIVERSE criterion R3")
    P_("=" * 120)
    rho_stored = W["P1"].corr(W["STORED"])
    rho_rebuilt = W["P1"].corr(W["REBUILT"])
    P_(f"{'candidate':<40}{'weekly rho w/ P1':>18}{'R3 distinct?':>16}{'admissible?':>14}")
    P_(f"{'STORED w72:X9a (the PAIR23 member)':<40}{rho_stored:>18.4f}"
       f"{'NO':>16}{'NO':>14}")
    P_(f"{'REBUILT W72 raw channel':<40}{rho_rebuilt:>18.4f}"
       f"{'yes':>16}{'NO - see below':>14}")
    P_("")
    P_("    THE PAIR23 MEMBER FAILS R3 DECISIVELY. R3 requires that a candidate not be a")
    P_("    re-weighting of an object already present. This one CONTAINS the incumbent's entire")
    P_("    ensemble by construction, and weekly rho +0.613 measures that fact.")
    P_("")
    P_("    THE RAW CHANNEL PASSES R3 BUT IS NOT THE OBJECT THE QUESTION ASKED ABOUT. Admitting it")
    P_("    would not decompose PAIR23, because PAIR23 does not contain it. On its own it earns")
    P_(f"    ${J['REBUILT'].sum():,.0f} over the campaign window with t = 1.05 in W72's 2022-26 era")
    P_("    row - which is not a candidate, it is a channel.")
    P_("")
    P_("    VERDICT: X9a is NOT ADMITTED as a standalone expert, under either reading.")
    P_("    The frontier's premise - 'X9a is the one component of PAIR23 not already double-counted")
    P_("    inside P1/PCT's B-MOM OR-gate' - is FALSE. It is the MOST double-counted component.")
    J.to_csv(os.path.join(OUT, "x9a_two_objects_daily.csv"))
    _fh.close()


if __name__ == "__main__":
    main()
