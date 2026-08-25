"""R23: identify the suppression layer from the recovered 89-trade path.

The whole risk/gate behaviour of the era reduces to (a) the moments a reversal was DECLINED
and (b) the T1 signals that were then skipped while flat. This file characterises every one
of those decisions against the state the strategy could actually see.

No P&L objective: rules are scored only by whether they reproduce the recovered decisions.
"""
import csv
import json
import os
import sys

import numpy as np
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from solarwave import SolarWaveParams  # noqa: E402
import inverse_core as IC  # noqa: E402

OUT = os.path.join(ROOT, "runs", "OTR_R11_INVERSE", "out")


def main():
    df = pd.read_parquet(os.path.join(ROOT, "research", "scalping_lab", "substrate",
                                      "minute", "NQ", "nq1m_2005_202605.parquet"))
    df["time"] = pd.to_datetime(df["time"])
    seg = df[(df["time"] >= "2023-01-02 18:00") &
             (df["time"] <= "2023-01-18 17:00")].reset_index(drop=True)
    bb = IC.prepare(seg, SolarWaveParams())
    t, st, lb = bb["t"], bb["st"], bb["lb"]
    day_of = np.datetime_as_string(t.astype("datetime64[D]"))
    mod = ((t - t.astype("datetime64[D]")).astype("timedelta64[s]").astype(np.int64) // 60)
    P = sorted(json.load(open(os.path.join(OUT, "r22_global_path_11days.json"))),
               key=lambda x: x["ei"])
    entry_bar = {int(x["ei"]): x for x in P}

    # per-CALENDAR-DAY running state, since that is the unit the report uses
    day_net = {}
    for x in P:
        day_net[x["day"]] = day_net.get(x["day"], 0.0) + x["pnl"]
    days = sorted(day_net)
    prior_day_net = {d: (day_net[days[i - 1]] if i else 0.0) for i, d in enumerate(days)}
    # prior SESSION net, which is what a session-scoped strategy would actually carry
    sess_net = {}
    for x in P:
        s_idx = int(np.sum(bb["fb"][:int(x["xi"]) + 1])) - 1
        sess_net[s_idx] = sess_net.get(s_idx, 0.0) + x["pnl"]

    # CRITICAL distinction: the strategy's own state (session P&L, high-water, consecutive
    # losses, trade count) resets on the SESSION boundary (18:00 ET, NT8
    # Bars.IsFirstBarOfSession). Only the REPORT groups rows by calendar date. Resetting
    # strategy state on the calendar boundary would invent a rule the strategy cannot have.
    rows = []
    cum = hi = 0.0
    consec = {1: 0, -1: 0}
    ntr = 0
    pos = 0
    last_exit_bar = -10 ** 9
    last_pnl = last_mae = last_hold = 0.0
    n_losses = 0
    consec_any = 0
    last_cutoff = "2023-01-17"
    sess_open_bar = 0
    for i in range(bb["n"]):
        cur_day = day_of[i]
        if cur_day > last_cutoff:
            break                      # beyond the reported window: no labels exist
        if bb["fb"][i]:
            sess_open_bar = i
            last_pnl = last_mae = last_hold = 0.0
            n_losses = 0
            consec_any = 0
            cum = hi = 0.0
            consec = {1: 0, -1: 0}
            ntr = 0
        if i in entry_bar and pos == 0:
            pos = int(entry_bar[i]["d"])
        cl = [x for x in P if int(x["xi"]) == i]
        if cl and pos != 0:
            x = cl[0]
            cum += x["pnl"]; hi = max(hi, cum)
            consec[int(x["d"])] = consec[int(x["d"])] + 1 if x["pnl"] <= 0 else 0
            consec_any = consec_any + 1 if x["pnl"] <= 0 else 0
            n_losses += 1 if x["pnl"] <= 0 else 0
            last_pnl, last_mae = x["pnl"], x["mae"]
            last_hold = float(int(x["xi"]) - int(x["ei"]))
            ntr += 1; last_exit_bar = i; pos = 0
            if i in entry_bar and int(entry_bar[i]["ei"]) == i and entry_bar[i] is not x:
                pos = int(entry_bar[i]["d"])
        sig = int(st[i])
        if abs(sig) == 1 and i >= IC.BARS_REQUIRED and not bb["fb"][i] and not lb[i]:
            d = int(np.sign(sig))
            in_pos = pos != 0
            # a T1 opposite the open position is a REVERSAL decision; while flat it is an
            # ENTRY decision. Same gate, two surfaces.
            if in_pos and d == -pos:
                kind = "REVERSAL"
                took = any(int(x["ei"]) == i + 1 and int(x["d"]) == d for x in P)
            elif not in_pos:
                kind = "ENTRY"
                took = (i + 1) in entry_bar and int(entry_bar[i + 1]["d"]) == d
            else:
                continue
            rows.append(dict(day=cur_day, bar=i, time=str(t[i]), dir=d, kind=kind,
                             decision="TAKE" if took else "DECLINE",
                             sess_cum=round(cum, 2), sess_high=round(hi, 2),
                             drawdown_from_high=round(cum - hi, 2),
                             consec_same=consec[d], trades_done=ntr,
                             minute_of_day=int(mod[i]),
                             minutes_from_open=int((t[i] - t[sess_open_bar])
                                                   .astype("timedelta64[s]")
                                                   .astype(np.int64) // 60),
                             bars_since_exit=(i - last_exit_bar)
                             if last_exit_bar > -10 ** 8 else 9999,
                             prior_day_net=round(prior_day_net.get(cur_day, 0.0), 2),
                             prior_sess_net=round(sess_net.get(
                                 int(np.sum(bb["fb"][:i + 1])) - 2, 0.0), 2),
                             last_trade_pnl=round(last_pnl, 2),
                             last_trade_mae=round(last_mae, 2),
                             last_trade_hold=last_hold,
                             session_losses=n_losses,
                             consec_any=consec_any,
                             bars_since_prev_flip=int(i - int(
                                 np.max(np.flatnonzero(np.abs(st[:i]) == 1))))
                             if np.any(np.abs(st[:i]) == 1) else 9999))
    with open(os.path.join(OUT, "suppression_decisions.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)

    dec = [r for r in rows if r["decision"] == "DECLINE"]
    tak = [r for r in rows if r["decision"] == "TAKE"]
    print(f"decision points: {len(rows)}   TAKE {len(tak)}   DECLINE {len(dec)}")
    print(f"  by kind: " + str({k: (sum(1 for r in rows if r['kind'] == k and r['decision'] == 'TAKE'),
                                   sum(1 for r in rows if r['kind'] == k and r['decision'] == 'DECLINE'))
                                for k in ("REVERSAL", "ENTRY")}) + "  (TAKE, DECLINE)")
    print(f"\n=== every DECLINE, with the state the strategy could see ===")
    print(f"{'day':11} {'time':9} {'kind':9} {'dir':>3} {'sessCum':>9} {'sessHigh':>9} "
          f"{'ddFromHi':>9} {'consec':>6} {'nTr':>3} {'MoD':>5} {'bse':>5} {'priorDay':>10}")
    for r in dec:
        print(f"{r['day']:11} {r['time'][11:16]:9} {r['kind']:9} {r['dir']:>3} "
              f"{r['sess_cum']:>9.2f} {r['sess_high']:>9.2f} {r['drawdown_from_high']:>9.2f} "
              f"{r['consec_same']:>6} {r['trades_done']:>3} {r['minute_of_day']:>5} "
              f"{r['bars_since_exit']:>5} {r['prior_day_net']:>10.2f} "
              f"{r['prior_sess_net']:>10.2f}")

    print(f"\n=== single-feature separability (DECLINE vs TAKE) ===")
    for col in ("sess_cum", "sess_high", "drawdown_from_high", "consec_same",
                "trades_done", "minute_of_day", "minutes_from_open",
                "bars_since_exit", "prior_day_net", "prior_sess_net",
                "last_trade_pnl", "last_trade_mae", "last_trade_hold",
                "session_losses", "consec_any", "bars_since_prev_flip"):
        a = [r[col] for r in dec]; b = [r[col] for r in tak]
        sep = (min(a) > max(b)) or (max(a) < min(b))
        print(f"  {col:>20}: DECLINE [{min(a):>9.2f},{max(a):>9.2f}]  "
              f"TAKE [{min(b):>9.2f},{max(b):>9.2f}]  {'SEPARATES' if sep else 'overlaps'}")

    # two-feature threshold search, scored ONLY on decisions
    print(f"\n=== best 2-feature rules (scored on decisions only, no P&L) ===")
    feats = ["sess_cum", "sess_high", "drawdown_from_high", "consec_same",
             "trades_done", "minute_of_day", "minutes_from_open",
             "bars_since_exit", "prior_day_net", "prior_sess_net",
             "last_trade_pnl", "last_trade_mae", "last_trade_hold",
             "session_losses", "consec_any", "bars_since_prev_flip"]
    best = []
    for f1 in feats:
        v1 = sorted({r[f1] for r in rows})
        for f2 in feats:
            if f2 <= f1:
                continue
            v2 = sorted({r[f2] for r in rows})
            for a in v1:
                for b in v2:
                    for s1 in (1, -1):
                        for s2 in (1, -1):
                            err = 0
                            for r in rows:
                                blocked = (s1 * r[f1] >= s1 * a) and (s2 * r[f2] >= s2 * b)
                                if (r["decision"] == "DECLINE") != blocked:
                                    err += 1
                            if err <= 2:
                                best.append((err, f1, s1, a, f2, s2, b))
    best.sort()
    seen = set()
    for e in best[:20]:
        k = (e[1], e[4])
        if k in seen:
            continue
        seen.add(k)
        op1 = ">=" if e[2] > 0 else "<="
        op2 = ">=" if e[5] > 0 else "<="
        print(f"  err={e[0]}  DECLINE iff  {e[1]} {op1} {e[3]}  AND  {e[4]} {op2} {e[6]}")
    if not best:
        print("  none with <=1 error: the decisions are NOT explained by any 2-feature "
              "threshold rule over the observable state.")


def score_incumbent():
    """Score the incumbent D-gate against the recovered decisions, with SESSION-scoped
    state and prior-SESSION net -- the scoping the strategy itself must use."""
    import csv as _csv
    rows = list(_csv.DictReader(open(os.path.join(OUT, "suppression_decisions.csv"))))
    for r in rows:
        for k in ("sess_cum", "sess_high", "prior_sess_net", "prior_day_net"):
            r[k] = float(r[k])
        for k in ("consec_same", "trades_done", "minute_of_day", "minutes_from_open",
                  "bars_since_exit"):
            r[k] = int(r[k])

    def allows(r, X, X2, K, C, Cmin, cap, cd):
        if r["prior_sess_net"] <= -C and r["minutes_from_open"] <= Cmin:
            return False
        if r["trades_done"] >= cap:
            return False
        if r["bars_since_exit"] < cd:
            return False
        thr = X if r["minute_of_day"] >= 720 else X2
        if r["sess_high"] >= thr:
            if r["sess_cum"] < 0:
                return False
            if r["consec_same"] >= K:
                return False
        return True

    print("\n=== incumbent D-gate, session-scoped, vs the recovered decisions ===")
    inc = dict(X=1600.0, X2=2500.0, K=3, C=700.0, Cmin=360, cap=20, cd=3)
    e = sum(1 for r in rows if (r["decision"] == "TAKE") != allows(r, **inc))
    print(f"  incumbent {inc}: {len(rows)-e}/{len(rows)} correct")
    best = []
    for X in (400, 600, 800, 1000, 1200, 1400, 1600, 2000, 10**9):
        for K in (2, 3, 4, 10**6):
            for C in (100, 300, 500, 700, 10**9):
                for Cmin in (120, 240, 300, 360, 420, 600):
                    for cap in (10, 14, 20, 10**6):
                        for cd in (0, 2, 3, 5):
                            fp = fn = 0
                            for r in rows:
                                a = allows(r, X, X, K, C, Cmin, cap, cd)
                                if r["decision"] == "TAKE" and not a:
                                    fp += 1
                                elif r["decision"] == "DECLINE" and a:
                                    fn += 1
                                if fp + fn > 3:
                                    break
                            if fp + fn <= 3:
                                best.append((fp + fn, fp, fn, X, K, C, Cmin, cap, cd))
    best.sort()
    print(f"  sets with <=3 errors (X2 tied to X): {len(best)}")
    for b in best[:10]:
        print(f"    err={b[0]} (suppress {b[1]}, allow {b[2]})  X={b[3]} K={b[4]} "
              f"C={b[5]} Cmin={b[6]} cap={b[7]} cd={b[8]}")
    if best and best[0][0] == 0:
        print("  --> a ZERO-ERROR gate EXISTS under session scoping.")


if __name__ == "__main__":
    main()
    score_incumbent()
