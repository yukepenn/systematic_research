"""WE_W04 ATOMS (spec preregistered): atomic ablation of the product stack on 1-min NQ.

Every atom runs through the product's own pipeline (sm14_1m) with parameter overrides whose
defaults leave prior behavior unchanged. bmom off everywhere to isolate the Solar path.
"""
from __future__ import annotations

import os
import sys
import time as _time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from run_we_w01 import (ROOT, STRESS_RT, load, week_table, summarize, sm14_1m)  # noqa: E402
from run_we_w03 import fills                                                    # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W04_ATOMS", "out")
os.makedirs(OUT, exist_ok=True)


def main():
    t0 = _time.time()
    D = load()
    print(f"bars {D['n']:,} [{_time.time()-t0:.0f}s]", flush=True)

    members = {}

    def add(nm, **kw):
        tg = sm14_1m(D, 460, with_bmom=False, return_targets=True, **kw)
        members[nm] = week_table(fills(D, tg), D, lambda x: x["xt"])
        print(f"{nm} [{_time.time()-t0:.0f}s]", flush=True)

    for k in (6, 10, 14, 18, 22, 26, 30):
        add(f"MEM{k}", volmults=[k])
    add("BASE")
    add("NOHYST", exit_level=3.0)
    add("NOTILT", tilt_on=False)
    add("NOBLOCK", blocks_on=False)
    add("NOHYST_NOTILT", exit_level=3.0, tilt_on=False)

    rows = []
    for nm, per_s in members.items():
        rec = {"member": nm}
        for which in ("dev", "hold"):
            r = summarize(per_s, D, which)
            if r is None:
                continue
            stress = np.array(r["_net"]) - STRESS_RT * np.array(r["_ntr"])
            rec.update({f"{which}_mean": round(r["mean"]), f"{which}_pos": round(r["pos"], 1),
                        f"{which}_worst": round(r["worst"]),
                        f"{which}_sharpe": round(r["sharpe"], 3),
                        f"{which}_tpw": round(r["tpw"], 1),
                        f"{which}_ptrade": round(r["per_trade"], 1),
                        f"{which}_total": round(r["total"]),
                        f"{which}_stress_mean": round(float(stress.mean()))})
        rows.append(rec)
    sm = pd.DataFrame(rows)
    sm.to_csv(os.path.join(OUT, "summary.csv"), index=False)
    cols = ["member", "dev_mean", "dev_pos", "dev_worst", "dev_sharpe", "dev_tpw",
            "dev_ptrade", "dev_stress_mean", "hold_mean", "hold_pos", "hold_sharpe"]
    print("\n" + sm[cols].to_string(index=False))
    base = sm[sm["member"] == "BASE"].iloc[0]
    print("\nmarginal deltas vs BASE (dev_sharpe / dev_ptrade / dev_worst):")
    for nm in ("NOHYST", "NOTILT", "NOBLOCK", "NOHYST_NOTILT"):
        r = sm[sm["member"] == nm].iloc[0]
        print(f"  {nm:<16} {r['dev_sharpe']-base['dev_sharpe']:+.3f}  "
              f"{r['dev_ptrade']-base['dev_ptrade']:+.1f}  "
              f"{r['dev_worst']-base['dev_worst']:+,.0f}")
    print(f"\ndone [{_time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
