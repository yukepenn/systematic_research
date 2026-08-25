"""R14 (authorised by runs/OTR_R11_INVERSE/amendment_2.yaml):
re-adjudicate the incumbent D-gate against the unique-path INVARIANT LABELS.

No P&L objective appears anywhere in this file. A gate component is scored ONLY by whether
it reproduces the TAKE/SKIP labels implied by the uniquely-recovered daily trade paths.
"""
import csv
import itertools
import os
import sys

import numpy as np
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from solarwave import SolarWaveParams  # noqa: E402
import inverse_core as IC  # noqa: E402
from run_r11b_inverse import build_targets  # noqa: E402

OUT = os.path.join(ROOT, "runs", "OTR_R11_INVERSE", "out")
os.makedirs(OUT, exist_ok=True)
PV, BR, COMM = 20.0, 20, 4.18


def label_session(bb, s0, s1, path, bt_start=None):
    """Replay the unique path and emit one labelled row per T1 decision bar.

    A T1 signal bar is a DECISION POINT only when the strategy is FLAT at that bar's close
    (if it is in a position the signal is consumed by the reversal logic instead). At each
    decision point the label is TAKE if the path's next trade fills at bar+1, else SKIP.
    """
    st, ts, c, o, lb, fb, t = (bb[k] for k in ("st", "ts", "c", "o", "lb", "fb", "t"))
    trades = sorted(path, key=lambda x: x["ei"])
    entry_at = {int(x["ei"]): x for x in trades}
    mod = ((t - t.astype("datetime64[D]")).astype("timedelta64[s]").astype(np.int64) // 60)
    sess_open = t[s0]
    rows = []
    # replay
    pos, cum, hi = 0, 0.0, 0.0
    consec = {1: 0, -1: 0}
    ntr, last_exit = 0, -10 ** 9
    cur = None
    for i in range(s0, s1 + 1):
        # a trade that fills at bar i
        if i in entry_at and pos == 0:
            cur = entry_at[i]; pos = int(cur["d"])
        # realise a trade that exits at bar i
        if cur is not None and int(cur["xi"]) == i and pos != 0:
            pnl = float(cur["pnl"])
            cum += pnl; hi = max(hi, cum)
            consec[pos] = consec[pos] + 1 if pnl <= 0 else 0
            ntr += 1; last_exit = i; pos = 0; cur = None
            # a reversal fills at the same bar
            if i in entry_at and entry_at[i]["ei"] == i and entry_at[i] is not None:
                nx = entry_at[i]
                if int(nx["ei"]) == i and int(nx["d"]) != 0 and nx is not cur:
                    cur = nx; pos = int(nx["d"])
        sig = int(st[i])
        # NT8 BarsRequiredToTrade is counted from the FIRST BAR OF THE BACKTEST, not from
        # the start of our analysis segment. The trader's report begins with the 2023-01-03
        # session, so decisions in that session's first 20 bars are warm-up blocked by the
        # PLATFORM, not by any strategy gate. Mis-attributing them to a gate would invent
        # a rule that does not exist.
        warm = bt_start is not None and (i - bt_start) < BR
        if abs(sig) == 1 and pos == 0 and i >= BR and not fb[i] and not lb[i]:
            took = (i + 1) in entry_at and int(entry_at[i + 1]["d"]) == np.sign(sig)
            rows.append(dict(
                day=str(t[s1])[:10], bar=i, time=str(t[i]), dir=int(np.sign(sig)),
                label="TAKE" if took else "SKIP",
                sess_cum=round(cum, 2), sess_high=round(hi, 2),
                consec_same=consec[int(np.sign(sig))],
                trades_done=ntr, minute_of_day=int(mod[i]),
                minutes_from_open=int((t[i] - sess_open).astype("timedelta64[s]")
                                      .astype(np.int64) // 60),
                bars_since_exit=(i - last_exit) if last_exit > -10 ** 8 else 9999,
                warmup_blocked=bool(warm),
                bars_from_backtest_start=(i - bt_start) if bt_start is not None else -1))
    return rows


def gate_allows(r, prior_net, X, X2, K, C, cap, cd, use=("X", "K", "C", "cap", "cd")):
    if "C" in use and prior_net <= -C and r["minutes_from_open"] <= 360:
        return False
    if "cap" in use and r["trades_done"] >= cap:
        return False
    if "cd" in use and r["bars_since_exit"] < cd:
        return False
    if "X" in use:
        thr = X if r["minute_of_day"] >= 720 else X2
        if r["sess_high"] >= thr:
            if r["sess_cum"] < 0:
                return False
            if "K" in use and r["consec_same"] >= K:
                return False
    elif "K" in use:
        if r["consec_same"] >= K:
            return False
    return True


def main():
    tg = build_targets()
    df = pd.read_parquet(os.path.join(ROOT, "research", "scalping_lab", "substrate",
                                      "minute", "NQ", "nq1m_2005_202605.parquet"))
    df["time"] = pd.to_datetime(df["time"])
    seg = df[(df["time"] >= "2022-12-01") & (df["time"] <= "2023-01-18 17:00")].reset_index(drop=True)
    bb = IC.prepare(seg, SolarWaveParams())
    sd = {str(bb["t"][s1])[:10]: (s0, s1) for s0, s1 in IC.sessions(bb)}

    # the trader's backtest begins at the 2023-01-03 session open (evidenced by the
    # uniquely-recovered 1/3 path containing a trade entering 2023-01-02 21:39, and by the
    # report having no 1/2 row).
    bt_start = sd["2023-01-03"][0]
    rows, prior = [], {}
    prev_net = 0.0
    for day in sorted(tg):
        s0, s1 = sd[day]
        sols, stats = IC.enumerate_paths(bb, s0, s1, tg[day], frozenset({1}),
                                         comm_rt=COMM, node_budget=8_000_000,
                                         exit_strict=True)
        if len(sols) != 1:
            print(f"  {day}: {len(sols)} solutions -> NOT an invariant-label day, excluded")
            prev_net = tg[day].net
            continue
        prior[day] = prev_net
        rows += label_session(bb, s0, s1, sols[0], bt_start=bt_start)
        prev_net = tg[day].net
    for r in rows:
        r["prior_session_net"] = round(prior[r["day"]], 2)
    with open(os.path.join(OUT, "gate_labels.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    warm = [r for r in rows if r["warmup_blocked"]]
    if warm:
        print(f"\nPLATFORM WARM-UP (BarsRequiredToTrade=20 from backtest start), "
              f"excluded from gate fitting: {len(warm)}")
        for r in warm:
            print(f"   {r['day']} {r['time'][11:]} dir={r['dir']:+d} "
                  f"bar {r['bars_from_backtest_start']} of the backtest, label={r['label']}"
                  f"  {'CONSISTENT' if r['label']=='SKIP' else 'INCONSISTENT!'}")
    rows = [r for r in rows if not r["warmup_blocked"]]
    nT = sum(1 for r in rows if r["label"] == "TAKE")
    print(f"\ninvariant-label decision points: {len(rows)}  TAKE={nT}  SKIP={len(rows)-nT}"
          f"  over {len(prior)} days\n")
    print("=== the SKIPPED signals (what any gate must explain) ===")
    print(f"{'day':11} {'time':17} {'dir':>3} {'sessCum':>9} {'sessHigh':>9} "
          f"{'consec':>6} {'nTr':>3} {'MoD':>4} {'MfO':>4} {'barsSinceExit':>13} {'priorNet':>9}")
    for r in rows:
        if r["label"] == "SKIP":
            print(f"{r['day']:11} {r['time'][11:]:17} {r['dir']:>3} {r['sess_cum']:>9.2f} "
                  f"{r['sess_high']:>9.2f} {r['consec_same']:>6} {r['trades_done']:>3} "
                  f"{r['minute_of_day']:>4} {r['minutes_from_open']:>4} "
                  f"{r['bars_since_exit']:>13} {r['prior_session_net']:>9.2f}")

    # ---- leave-one-component-out on the incumbent constants -------------------
    INC = dict(X=1600.0, X2=2500.0, K=3, C=700.0, cap=20, cd=3)
    ALL = ("X", "K", "C", "cap", "cd")
    print("\n=== leave-one-component-out (incumbent constants, labels only) ===")
    print(f"{'components':<28} {'correct':>8} {'/':>1} {'total':>5}  {'FP(took->gate says no)':>24} {'FN':>4}")
    scores = []
    for drop in (None,) + ALL:
        use = tuple(x for x in ALL if x != drop)
        fp = fn = 0
        for r in rows:
            allowed = gate_allows(r, r["prior_session_net"], use=use, **INC)
            if r["label"] == "TAKE" and not allowed:
                fp += 1
            if r["label"] == "SKIP" and allowed:
                fn += 1
        name = "ALL" if drop is None else f"ALL minus {drop}"
        print(f"{name:<28} {len(rows)-fp-fn:>8} / {len(rows):>5}  {fp:>24} {fn:>4}")
        scores.append(dict(components="+".join(use), dropped=drop or "",
                           correct=len(rows) - fp - fn, total=len(rows),
                           false_suppress=fp, false_allow=fn))
    with open(os.path.join(OUT, "gate_component_scores.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(scores[0].keys())); w.writeheader(); w.writerows(scores)

    # ---- can ANY constant set explain every label? ---------------------------
    print("\n=== constant sweep (does any setting reproduce ALL invariant labels?) ===")
    best = []
    for X in (800, 1000, 1200, 1400, 1600, 1800, 2000, 2500, 10 ** 9):
        for X2 in (1600, 2000, 2500, 3000, 10 ** 9):
            for K in (2, 3, 4, 10 ** 6):
                for C in (300, 500, 700, 900, 10 ** 9):
                    for cap in (8, 10, 12, 16, 20, 10 ** 6):
                        for cd in (0, 1, 2, 3, 4, 5):
                            fp = fn = 0
                            for r in rows:
                                a = gate_allows(r, r["prior_session_net"], X, X2, K, C, cap, cd)
                                if r["label"] == "TAKE" and not a:
                                    fp += 1
                                elif r["label"] == "SKIP" and a:
                                    fn += 1
                                if fp + fn > 3:
                                    break
                            if fp + fn <= 3:
                                best.append((fp + fn, fp, fn, X, X2, K, C, cap, cd))
    best.sort()
    print(f"  sets with <=3 label errors: {len(best)}")
    for b in best[:15]:
        print(f"   err={b[0]} (suppress {b[1]}, allow {b[2]})  X={b[3]} X2={b[4]} K={b[5]} "
              f"C={b[6]} cap={b[7]} cd={b[8]}")
    if best and best[0][0] == 0:
        print("\n  A ZERO-ERROR constant set EXISTS.")
    else:
        print(f"\n  NO zero-error constant set in the swept space "
              f"(best = {best[0][0] if best else 'none'} errors). Per amendment_2 this is "
              f"reported as-is; no new ad-hoc gate term is added to force a fit.")


if __name__ == "__main__":
    main()
