"""WE_W52 parity: the NinjaScript implementation against the Python object, COMPONENT BY COMPONENT.

The strategy exports a per-bar ledger (nMem, nThr, dL, ratio, voteOK, size, score, qty). This
compares each column against the Python object over the same bars, so a disagreement is
localised to the component that produced it instead of showing up only as a P&L difference.

Warm-up is handled honestly: NinjaTrader starts cold on 2026-01-02 while the Python object
carries years of state, so the comparison window starts 2026-04-01, by which point NT8 has
more than the 50 sessions the HTF tilt needs, more than the 14 RTH days B-MOM needs, and more
than the 60 sessions the range throttle's median needs. The QUALITY SIZE is reported separately
and NOT counted in the verdict, because its trailing-250-ENTRY window is still cold at that
point by construction and cannot agree.
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_we_w01 as W1                                                  # noqa: E402
from run_we_w01 import ROOT                                             # noqa: E402
from run_we_w17 import load_deep                                        # noqa: E402
from run_we_w19 import MEMBERS, QS                                      # noqa: E402
from run_we_w38 import targets                                          # noqa: E402
from we_quality import build_context                                    # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W52_NINJASCRIPT", "out")
WARM = pd.Timestamp("2026-04-01")


def main():
    nt = pd.read_csv(os.path.join(OUT, "we_p1_w52a.csv"))
    nt["pyts"] = pd.to_datetime(nt["pyts"])
    nt = nt.sort_values("pyts").reset_index(drop=True)
    out = open(os.path.join(OUT, "parity.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out)

    P_("=== WE_W52 NinjaScript parity: WeeklyEdgeP1_v1 vs the Python P1 object ===")
    P_(f"   NT8 ledger {len(nt):,} bars, {nt['pyts'].min()} -> {nt['pyts'].max()}")

    D = load_deep("2022-01-01", "2026-07-31 17:00")
    W1.DEV_END = pd.Timestamp("2026-07-31").date()
    n, tarr = D["n"], D["t"]
    X = build_context(D)
    TG = targets(D)

    nMem = np.zeros(n, np.int16)
    for mem in MEMBERS:
        nMem += (TG[mem] > 0).astype(np.int16)
    nThr = np.zeros(n, np.int16)
    for q in QS:
        ok = np.ones(n, bool) if q is None else ((X["norm"] <= 0) | (X["ratio"] >= q))
        nThr += ok.astype(np.int16)
    dL = X["dL"].astype(np.int16)
    voteOK = ((nMem.astype(int) * nThr.astype(int) * (1 + dL.astype(int))) >= 16).astype(np.int8)
    ratio = np.where(X["norm"] > 0, X["ratio"], 1.0)

    py = pd.DataFrame(dict(pyts=pd.to_datetime(tarr), nMem=nMem, nThr=nThr,
                           dL=dL, ratio=ratio, voteOK=voteOK))
    m = py.merge(nt, on="pyts", how="inner", suffixes=("_py", "_nt"))
    P_(f"   matched on timestamp: {len(m):,} bars "
       f"({100*len(m)/max(len(nt),1):.1f} % of the NT8 ledger)")
    if len(m) < 1000:
        P_("   TOO FEW MATCHED BARS - the timestamp convention is wrong, run VOID")
        out.close(); return

    w = m[m["pyts"] >= WARM].reset_index(drop=True)
    P_(f"   warm window {WARM.date()} onward: {len(w):,} bars\n")

    P_(f"{'component':<28}{'agree %':>10}{'disagreeing bars':>19}{'verdict':>14}")
    res = {}
    for col in ("nMem", "nThr", "dL", "voteOK"):
        a, b = w[col + "_py"].values, w[col + "_nt"].values
        eq = (a == b)
        res[col] = 100.0 * eq.mean()
        P_(f"{col:<28}{res[col]:>10.3f}{int((~eq).sum()):>19}"
           f"{('PASS' if res[col] >= 99 else ('close' if res[col] >= 90 else 'FAIL')):>14}")
    rd = np.abs(w["ratio_py"].values - w["ratio_nt"].values)
    P_(f"{'ratio (max abs diff)':<28}{rd.max():>10.6f}{int((rd > 1e-4).sum()):>19}"
       f"{('PASS' if rd.max() < 1e-4 else 'check'):>14}")

    P_(f"\n   quality SIZE (reported, NOT in the verdict - its trailing-250-entry window is")
    P_(f"   still cold on this backtest by construction):")
    ent = w[(w["voteOK_nt"] == 1) & (w["qty"] == 0)]
    P_(f"      NT8 entries in the warm window: {len(ent)} | size-2 share "
       f"{100*(ent['size'] == 2).mean() if len(ent) else 0:.1f} % | scored "
       f"{100*(ent['score'] > 0).mean() if len(ent) else 0:.1f} %")

    bad = w[w["voteOK_py"] != w["voteOK_nt"]]
    if len(bad):
        P_(f"\n   first 10 voteOK disagreements:")
        P_(f"{'timestamp':<22}{'nMem py/nt':>12}{'nThr py/nt':>12}{'dL py/nt':>10}"
           f"{'ratio py/nt':>22}")
        for _, r in bad.head(10).iterrows():
            P_(f"{str(r['pyts']):<22}{int(r['nMem_py'])}/{int(r['nMem_nt']):<10}"
               f"{int(r['nThr_py'])}/{int(r['nThr_nt']):<10}"
               f"{int(r['dL_py'])}/{int(r['dL_nt']):<8}"
               f"{r['ratio_py']:.4f}/{r['ratio_nt']:.4f}")
        # which component explains the disagreement
        for col in ("nMem", "nThr", "dL"):
            share = 100.0 * (bad[col + "_py"] != bad[col + "_nt"]).mean()
            P_(f"   {col} also disagrees on {share:.1f} % of the voteOK disagreements")

    P_(f"\n=== VERDICT (thresholds preregistered in spec.yaml) ===")
    v = res["voteOK"]
    P_(f"   decision-series agreement {v:.3f} % -> "
       + ("IMPLEMENTATION VALIDATED" if v >= 99 else
          ("localised disagreement, report before proceeding" if v >= 90 else
           "NOT VALIDATED - the C# is not the object")))
    pd.DataFrame([dict(component=k, agree_pct=round(x, 4)) for k, x in res.items()]).to_csv(
        os.path.join(OUT, "parity_components.csv"), index=False)
    out.close()


if __name__ == "__main__":
    main()
