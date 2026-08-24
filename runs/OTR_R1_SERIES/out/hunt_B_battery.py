# hunt_B_battery.py — FAMILY B candidate battery, reproducible.
# Runs every Family-B gate tested in the hunt, scores vs r12f labels, prints master aggregates.
import numpy as np
import pandas as pd
import hunt_B_sim as H

def main():
    bars = H.get_bars(); ctx = H.make_ctx(bars); lab = H.load_labels()
    mod = ctx["mod"]; bso = ctx["bars_since_open"]; gapd = ctx["gap_days_sess"]
    sid = ctx["sid"]; dow = ctx["dow"]
    sess_len = ctx["slast"] - ctx["sopen"]      # per-session bar counts
    prevlen = ctx["prev_len_sess"]

    def seltime_w(i, d, p):
        # weekday-window fit: passes ALL hard labels, falsified by master aggregate
        if bso[i] == 0: return False
        w = dow[i]; m = mod[i]
        if w == 1 and d > 0 and 750 <= m <= 1019: return False   # Tue PM longs
        if w == 2 and m >= 1080: return False                    # Wed evening
        if w == 3 and 740 <= m <= 869: return False              # Thu midday
        return True

    gates = {
        "B0_none":       lambda i, d, p: True,
        "B1_firstbar":   lambda i, d, p: bso[i] > 0,
        "B2_open60":     lambda i, d, p: bso[i] >= 60,
        "B4_reopen_all": lambda i, d, p: gapd[sid[i]] < 2,
        "B5_sun_eve":    lambda i, d, p: not (gapd[sid[i]] >= 2 and mod[i] >= 1080),
        "B6_short_sess": lambda i, d, p: sess_len[sid[i]] >= 1370,
        "B7_aftershort": lambda i, d, p: prevlen[sid[i]] >= 1370,
        "SELTIME_W":     seltime_w,
    }
    for N in (60, 240, 360, 450):
        gates[f"B1+B3_{N}"] = (lambda N: lambda i, d, p:
                               (bso[i] > 0) and not (gapd[sid[i]] >= 2 and bso[i] < N))(N)

    for name, g in gates.items():
        tr = H.run_gated(bars, ctx, g)
        sc = H.score(bars, ctx, tr, lab)
        m = H.master(tr)
        print(f"== {name}: hard_ok={sc['hard_ok']} wrong_hard_skips={len(sc['wrong_hard_skips'])} "
              f"missed_hard_takes={len(sc['missed_hard_takes'])} soft_missed={len(sc['soft_missed'])} "
              f"| net={m['net']} trades={m['trades']} wr={m['wr']} pf={m['pf']} dd={m['dd']} hold={m['hold']}")
    print("TARGET:", H.TARGET)

if __name__ == "__main__":
    main()
