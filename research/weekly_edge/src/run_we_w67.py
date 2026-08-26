"""WE_W67 - decode the combiner before touching it.

Six inherited magic numbers in a chain (10.0, 1.25, 0.9026, 13, 0.7086, 2.83) plus two
hysteresis levels, none ever examined. Scanning six constants is a six-dimensional parameter
search and W59 measured that selection loses here at every scale. But the chain is deterministic
and its domain is tiny, so the whole map can be ENUMERATED EXACTLY with no backtest and reduced
to the few quantities that actually decide anything. That is the W48 rule.

The prediction is written into the spec before this ran: the +-13 clamp should be dead code, the
effective entry threshold should be ~45 % of members net-long without tilt agreement and ~35 %
with it, and B-MOM agreement should collapse it to ~5 %. Phase 1 confirms or corrects that.
"""
from __future__ import annotations

import os
import sys
import time as _time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from run_we_w01 import ROOT, PV, round_away, sm14_1m                     # noqa: E402
from run_we_w19 import MEMBERS, QS                                       # noqa: E402
from run_we_w26 import fills_daily                                       # noqa: E402
from run_we_w35 import fills_qexit                                       # noqa: E402
from run_we_w37 import causal_score                                      # noqa: E402
from run_we_w39 import WIN                                               # noqa: E402
from run_we_w51 import session_frames, A, B                              # noqa: E402
from run_we_w51c import setup, dd_profile                                # noqa: E402
from run_we_w66 import WIDE                                              # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W67_COMBINER", "out")
os.makedirs(OUT, exist_ok=True)
W66OUT = os.path.join(ROOT, "runs", "WE_W66_INNER", "out")
BASE = [6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30]
DD_TARGET = 20245.0
ENTRY, EXIT = 3.0, 1.0
K_T, K_TILT, K_TP, CLAMP_TP = 10.0, 1.25, 0.9026, 13
W_TP, W_BMOM = 0.7086, 2.83


def combine(sum_next, nmem, agree, bmom, k_t=K_T, k_tilt=K_TILT, k_tp=K_TP,
            clamp_tp=CLAMP_TP, w_tp=W_TP, w_bmom=W_BMOM):
    T = max(-10, min(10, round_away(sum_next / float(nmem) * k_t)))
    mm = k_tilt if (agree and sum_next != 0) else 1.0
    Tp = max(-clamp_tp, min(clamp_tp, round_away(T * mm * k_tp)))
    return T, Tp, w_tp * Tp + w_bmom * bmom


def main():
    t0 = _time.time()
    out = open(os.path.join(OUT, "combiner.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out)

    # =====================================================================================
    # PHASE 1a/1b - EXACT ENUMERATION
    # =====================================================================================
    P_("=" * 118)
    P_("=== PHASE 1a: the full combiner map, enumerated exactly. No backtest, no fitting.")
    P_("=" * 118)
    rows = []
    for nmem in (13, 18):
        reach_T = set(); reach_Tp = set()
        for s in range(-nmem, nmem + 1):
            for agree in (False, True):
                for bm in (-1, 0, 1):
                    T, Tp, M = combine(s, nmem, agree, bm)
                    reach_T.add(T); reach_Tp.add(Tp)
                    rows.append(dict(nmem=nmem, sum=s, frac=s / nmem, agree=agree, bmom=bm,
                                     T=T, Tp=Tp, M=M, entry=abs(M) >= ENTRY,
                                     hold=abs(M) > EXIT))
        P_(f"   NMEM={nmem}: T reaches {min(reach_T)}..{max(reach_T)} (clamp is +-10 -> "
           f"{'REACHED' if max(abs(min(reach_T)), abs(max(reach_T))) >= 10 else 'DEAD CODE'})"
           f" | Tp reaches {min(reach_Tp)}..{max(reach_Tp)} (clamp is +-{CLAMP_TP} -> "
           f"{'REACHED' if max(abs(min(reach_Tp)), abs(max(reach_Tp))) >= CLAMP_TP else 'DEAD CODE'})")
    Mp = pd.DataFrame(rows)
    Mp.to_csv(os.path.join(OUT, "map.csv"), index=False)

    P_(f"\n{'='*118}\n=== PHASE 1b: six constants collapse to a table of thresholds")
    P_(f"{'='*118}")
    P_("The entry condition, expressed as the FRACTION OF MEMBERS NET-LONG required, per state.\n")
    P_(f"{'NMEM':<7}{'tilt agrees':<14}{'B-MOM':<9}{'min members net-long to ENTER':>32}"
       f"{'as a fraction':>16}{'to HOLD':>28}")
    tab = []
    for nmem in (13, 18):
        for agree in (False, True):
            for bm in (0, 1):
                q = Mp[(Mp.nmem == nmem) & (Mp.agree == agree) & (Mp.bmom == bm) & (Mp["sum"] > 0)]
                ent = q[q.entry]["sum"].min() if q.entry.any() else np.nan
                hld = q[q.hold]["sum"].min() if q.hold.any() else np.nan
                P_(f"{nmem:<7}{str(agree):<14}{bm:<9}"
                   f"{(f'{int(ent)} of {nmem}' if ent == ent else 'unreachable'):>32}"
                   f"{(f'{ent/nmem:.1%}' if ent == ent else '-'):>16}"
                   f"{(f'{int(hld)} of {nmem} ({hld/nmem:.1%})' if hld == hld else '-'):>28}")
                tab.append(dict(nmem=nmem, agree=agree, bmom=bm,
                                enter=float(ent) if ent == ent else np.nan,
                                enter_frac=float(ent / nmem) if ent == ent else np.nan,
                                hold=float(hld) if hld == hld else np.nan))
    pd.DataFrame(tab).to_csv(os.path.join(OUT, "thresholds.csv"), index=False)
    P_(f"\n   Read that table as the whole combiner. Everything else in the chain is scaling")
    P_(f"   that cancels out of the decision.")

    # =====================================================================================
    # PHASE 1c - EMPIRICAL STATE FREQUENCIES
    # =====================================================================================
    D, X, TG, st, en = setup()
    n, tarr, sid = D["n"], D["t"], D["sid"]
    f = os.path.join(W66OUT, f"mem460_clamp_{D['n']}.npz")
    if not os.path.exists(f):
        f = os.path.join(W66OUT, f"mem_460_{D['n']}.npz")
    z = np.load(f)
    mem, bmom, tilt = z["mem"], z["bmom"], z["tilt"]
    idx_of = {v: k for k, v in enumerate(WIDE)}
    cols = [idx_of[v] for v in BASE]
    s = mem[:, cols].sum(axis=1).astype(int)
    agree = (np.sign(s) == tilt) & (s != 0) & (tilt != 0)
    P_(f"\n{'='*118}\n=== PHASE 1c: how often is each state actually live? "
       f"({n:,} bars) [{_time.time()-t0:.0f}s]")
    P_(f"{'='*118}")
    P_(f"   tilt AGREES with the member consensus on {100*agree.mean():.1f} % of bars")
    P_(f"   B-MOM is non-zero on {100*float((bmom != 0).mean()):.1f} % of bars "
       f"(+1 on {100*float((bmom > 0).mean()):.1f} %, -1 on {100*float((bmom < 0).mean()):.1f} %)")
    P_(f"\n{'state':<34}{'bars':>12}{'share':>9}{'net-long members needed':>26}")
    st_rows = []
    for lab, m_ in (("tilt agrees + B-MOM long", agree & (bmom > 0)),
                    ("tilt agrees, no B-MOM", agree & (bmom == 0)),
                    ("no tilt agreement + B-MOM long", (~agree) & (bmom > 0)),
                    ("no tilt agreement, no B-MOM", (~agree) & (bmom == 0)),
                    ("B-MOM SHORT (any tilt)", bmom < 0)):
        ag = "agrees" in lab
        bm = 1 if "long" in lab else (-1 if "SHORT" in lab else 0)
        q = [r for r in tab if r["nmem"] == 13 and r["agree"] == ag and r["bmom"] == max(bm, 0)]
        need = q[0]["enter"] if q else np.nan
        P_(f"{lab:<34}{int(m_.sum()):>12,}{100*m_.mean():>8.1f}%"
           f"{(f'{int(need)} of 13' if need == need else '-'):>26}")
        st_rows.append(dict(state=lab, bars=int(m_.sum()), share=float(m_.mean())))
    pd.DataFrame(st_rows).to_csv(os.path.join(OUT, "states.csv"), index=False)

    # what state was each ACTUAL long entry in?
    tg = TG["all13"]
    ent_bar = np.zeros(n, bool)
    ent_bar[1:] = (tg[1:] > 0) & (tg[:-1] <= 0)
    P_(f"\n   Of the {int(ent_bar.sum()):,} bars where the all13 target turns LONG:")
    for lab, m_ in (("tilt agreed", agree), ("B-MOM was long", bmom > 0),
                    ("B-MOM was long AND tilt agreed", agree & (bmom > 0)),
                    ("NEITHER (pure member consensus)", (~agree) & (bmom <= 0))):
        P_(f"      {lab:<34}{100*float(m_[ent_bar].mean()):>7.1f} %")
    P_(f"\n   And the member consensus AT those entries: median "
       f"{np.median(s[ent_bar]):.0f} of 13 net-long "
       f"({np.median(s[ent_bar])/13:.0%}), 10th pct {np.percentile(s[ent_bar],10):.0f}, "
       f"90th pct {np.percentile(s[ent_bar],90):.0f}")
    P_(f"\n=== STATUS: phase 1 is measurement only. Phase 2 and 3 depend on what it found. ===")
    out.close()
    print(f"done [{_time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
