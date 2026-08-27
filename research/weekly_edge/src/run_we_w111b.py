"""WE_W111b - the control W108 owed and nobody ran, including me.

W108 reported as a discovery that all five of its fade mechanisms are POSITIVE on RANGE and MIXED
sessions and NEGATIVE on both TREND classes, and called that "the signs are exactly what the
mechanisms predict". W111 has just reproduced the same signature with five MORE mechanisms built
from a completely different information source.

Nine of nine is either a strong structural fact or a definitional identity, and there is a cheap
test that separates them. The W51 taxonomy defines TREND-UP as |close - open| >= 0.60 x range over
the WHOLE session and RANGE as |close - open| <= 0.25 x range. An UNCONDITIONAL fade of the morning
direction must therefore lose on a session that ran one way all day and win on one that did not,
with no mechanism involved at all.

So: run the unconditional fade. If it shows the same signature, the class split carries no
information about any of the nine mechanisms, and the W108 framing needs correcting.
"""
from __future__ import annotations

import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from run_we_w01 import ROOT                                              # noqa: E402
from we_lanes import LaneBench                                           # noqa: E402
from we_fades import MORN_A, MORN_B, DEC, EXIT, build_fades              # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W111_VOLDECAY", "out")
CLASSES = ("TREND-UP", "TREND-DOWN", "REVERSAL", "RANGE", "MIXED")


def main():
    out = open(os.path.join(OUT, "signature_control.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out); out.flush()

    L = LaneBench()
    MECH, ctx = build_fades(L)
    P_(f"    substrate {L.n:,} bars / {len(L.sess_in):,} in-window sessions")
    P_("")
    P_("=" * 118)
    P_("=== THE CONTROL: an UNCONDITIONAL fade of the morning direction, no mechanism, no filter.")
    P_("===   Decide 11:48, fill 11:49, hold to 15:44, size 1. Same geometry as W108 and W111.")
    P_("=" * 118)
    md = ctx["morn_dir"]
    arms = {
        "FADE morning dir (uncond.)": -md,
        "FOLLOW morning dir (uncond.)": md,
        "always LONG": np.ones(L.NS),
        "always SHORT": -np.ones(L.NS),
    }
    P_(f"{'arm':<30}{'N':>6}{'$/trade':>10}" + "".join(f"{k:>17}" for k in CLASSES))
    for lab, d_ in arms.items():
        des = np.nan_to_num(np.where(L.win, d_, 0)).astype(np.int8)
        pnl, take, cost, em = L.trade(des, DEC, EXIT)
        st = L.stats(pnl, take, cost, em)
        bc = L.by_class(pnl, take)
        P_(f"{lab:<30}{st['n']:>6}{st['per_trade']:>10,.0f}"
           + "".join(f"{bc[c][0]:>6} {bc[c][1]:>10,.0f}" for c in CLASSES))

    P_("")
    P_("=" * 118)
    P_("=== HOW MUCH OF THE MORNING DIRECTION IS ALREADY IN THE CLASS LABEL?")
    P_("=" * 118)
    o0 = L.at(MORN_A, use_open=True)
    cl = L.at(944)                       # 15:44, the last bar the fades hold to
    full = np.sign(cl - o0)
    g = L.win & np.isfinite(md) & np.isfinite(full) & (md != 0) & (full != 0)
    P_(f"    P(afternoon close on the same side of 09:31 as the 11:29 close) = "
       f"{float((md[g] == full[g]).mean()):.3f}   on {int(g.sum())} sessions")
    for c in CLASSES:
        m = g & (L.klass == c)
        if m.sum():
            P_(f"        within {c:<12} = {float((md[m] == full[m]).mean()):.3f}  "
               f"(n={int(m.sum())})")
    P_("")
    P_("    Reading. If the unconditional fade already shows the -TREND / +RANGE signature, then")
    P_("    every fade that trades against the morning direction MUST show it too, and the")
    P_("    signature is a property of the TAXONOMY, not evidence about any mechanism.")
    out.close()


if __name__ == "__main__":
    main()
