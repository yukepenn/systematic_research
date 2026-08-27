"""RR_W001 addendum - is G3's failure an artifact of the normal approximation?

Spec: secondary_measurements ("power / MDE table per expert, with the session-clustered effective
N stated"). This does NOT re-run the gate. G3 failed and is recorded failed. This asks only
whether the FAILURE is robust, using a session block bootstrap that assumes no distributional form.

delta_action_value has sd $2,123.55 against a mean of $162.79 and p1/p99 of -$4,996/+$7,655, so the
normal-approximation MDE deserves an independent check rather than trust.
"""
from __future__ import annotations
import os
import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
OUT = os.path.join(ROOT, "runs", "RR_W001_ACTION_VALUE_LEDGER", "out")
fh = open(os.path.join(OUT, "rr_w001c.txt"), "w", encoding="utf-8")


def P_(*a):
    print(*a, flush=True); print(*a, file=fh); fh.flush()


BAR = 13.93
NB = 4000
rng = np.random.default_rng(1001)

L = pd.read_csv(os.path.join(OUT, "ledger_p1pct.csv"))
LW = L[L["in_window_session"]].reset_index(drop=True)
dav = LW["delta_action_value"].to_numpy()
sess = LW["session_id"].to_numpy()
usess = np.unique(sess)
by = {s: np.flatnonzero(sess == s) for s in usess}

P_("=" * 116)
P_("=== RR_W001c - SESSION BLOCK BOOTSTRAP CHECK ON G3.  The gate is NOT re-run; G3 failed and")
P_("=== stays failed. This asks only whether the failure survives dropping the normal assumption.")
P_("=" * 116)
P_(f"    n = {len(dav):,} decisions in {len(usess):,} session clusters")
P_(f"    mean ${dav.mean():,.2f}   sd ${dav.std(ddof=1):,.2f}   skew {pd.Series(dav).skew():.3f}   "
   f"kurtosis {pd.Series(dav).kurtosis():.1f}")
P_("")
P_("    A model sorts events; we ask how big a Q5-Q1 contrast must be to be distinguished from")
P_("    zero. Under RANDOM sorting the true contrast is 0, so the bootstrap distribution of the")
P_("    randomly-sorted contrast IS the null. Sessions are resampled whole, so intra-session")
P_("    dependence is preserved without estimating an ICC.")

stat = np.empty(NB)
for b in range(NB):
    pick = rng.choice(usess, size=len(usess), replace=True)
    idx = np.concatenate([by[s] for s in pick])
    v = dav[idx]
    perm = rng.permutation(len(v))
    k = len(v) // 5
    stat[b] = v[perm[:k]].mean() - v[perm[-k:]].mean()

se = float(stat.std(ddof=1))
mde_boot = 2.8016 * se
P_("")
P_(f"    bootstrap draws                                     {NB:,}")
P_(f"    SE of a randomly-sorted Q5-Q1 contrast             ${se:>10,.2f}")
P_(f"    bootstrap MDE for the CONTRAST (80 % power)        ${mde_boot:>10,.2f}")
P_(f"    normal-approximation MDE reported by the gate      ${564.63:>10,.2f}")
P_(f"    ratio bootstrap / normal                            {mde_boot / 564.63:>10.3f}x")
P_("")
P_(f"    smallest DETECTABLE per-decision policy gain (0.1x) ${0.1 * mde_boot:>10,.2f}")
P_(f"    materiality bar                                     ${BAR:>10,.2f}")
P_(f"    -> G3 under the bootstrap: "
   f"{'PASS' if 0.1 * mde_boot <= BAR else 'FAIL'}  ({0.1 * mde_boot / BAR:.2f}x the bar)")
P_("")
P_("    The ORACLE for comparison, so the ratio that actually matters is visible:")
orc = 604905.0 / len(dav)
P_(f"    f = 20 % ex-post abstention uplift                  ${orc:>10,.2f} per decision")
P_(f"    fraction of that oracle a router must CAPTURE before its gain is certifiable:")
P_(f"        normal approx  {100 * 56.46 / orc:>6.1f} %")
P_(f"        bootstrap      {100 * 0.1 * mde_boot / orc:>6.1f} %")
P_("")
P_("    OPPORTUNITY_LANGUAGE calibration of level-3 recovery in this repo: ~16 % (AFT, W112/W114)")
P_("    and ~20 % (RTH open, XM_CONFLICT, W104). Those are the only two data points that exist.")
fh.close()
