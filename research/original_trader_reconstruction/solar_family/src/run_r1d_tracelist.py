"""R1.2d: trade-level trace of P6-family on Jan-2023 days, with signal context."""
import os
import sys

import numpy as np

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from otr_engine import load_ledger, run_wrapper, WrapperPolicy  # noqa: E402

full = load_ledger(os.path.join(ROOT, "research", "03_reverse_engineering", "ledgers", "t2_canonical_1m.csv"))
cut = np.searchsorted(full["time"], np.datetime64("2023-01-21T00:00:00"))
bars = {k: (v[:cut] if isinstance(v, np.ndarray) else v) for k, v in full.items()}
bars["n"] = int(cut)
bars["last_bar"] = bars["last_bar"].copy()
bars["last_bar"][-1] = True

pol = WrapperPolicy(comm_side=2.09, entry_types=(1, 3), reverse_on_flip=True)
r = run_wrapper(bars, pol)
st = bars["signal_trade"]
strend = bars["signal_trend"]

DAYS = {"2023-01-04": "tgt 14 (5W avg 771.82 / 9L avg -556.40) net -1148.52 LW 1865.82 LL -899.18",
        "2023-01-05": "tgt 6 (2W avg 1305.82 / 4L avg -660.43) net -30.08 LW 2310.82 LL -889.18",
        "2023-01-12": "tgt 16 (5W avg 940.82 / 11L avg -729.63) net -3321.88 LW 1535.82 LL -1204.18",
        "2023-01-16": "tgt 3 (2W avg 320.82 / 1L -34.18) net 607.46 LW 555.82 LL -34.18",
        "2023-01-17": "tgt 6 (3W avg 440.82 / 3L avg -579.18) net -415.08 LW 590.82 LL -1089.18",
        "2023-01-03": "tgt 12 (4W avg 1465.82 / 8L avg -770.43) net -300.16 LW 3050.82 LL -1179.18"}

for d, note in sorted(DAYS.items()):
    print(f"=== {d}  {note}")
    for t in r["trades"]:
        if str(t["exit_time"])[:10] != d:
            continue
        ei = t["entry_i"]
        sig = st[ei - 1] if ei > 0 else 0  # signal was on the bar BEFORE the fill
        print(f"  {'L' if t['dir']>0 else 'S'} entry {str(t['entry_time'])[11:16]} sig(prev)={sig:+d} "
              f"trend={strend[ei-1]:+d} exit {str(t['exit_time'])[11:16]} kind={t['exit_kind'][:12]:12s} "
              f"pnl {t['pnl']:9.2f} hold {t['hold_min']:6.1f}")
