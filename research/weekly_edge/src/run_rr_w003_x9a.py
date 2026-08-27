"""RR_W003 - X9a DECISION-EVENT CONTRACT.  Frontier row 1.

RUN CLASS: ENGINEERING_ONLY. No hypothesis is selected, no parameter is chosen, no candidate is
promoted, no alpha budget is consumed. This asks whether X9a HAS a reproducible decision-event
contract and a coherent counterfactual, so it can be judged on its own rather than only inside the
PAIR23 basket - EXPERT_UNIVERSE section 3 deferred exactly this and said it must not be folded into
a measurement wave.

Everything economic below is REPRODUCED from committed evidence, never newly selected:
  W72  X9a era table   pre-2022  3,948 trades  +$28.6/trade  t 1.83  PF 1.105
                       2022-26     950 trades +$123.0/trade  t 1.05  PF 1.095
  W88  weekly rho      P1 - X9a  +0.613 "too correlated"   BMOM - X9a  +0.009 "INDEPENDENT"

The withdrawn 92 % PAIR23 claim is NOT reinterpreted here (directive section 35).
"""
from __future__ import annotations

import os
import sys
import time as _time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_we_w01 as W1                                                   # noqa: E402
from run_we_w01 import ROOT                                               # noqa: E402
from run_we_w17 import load_deep                                          # noqa: E402
from run_we_w38 import sfills                                             # noqa: E402
from we_channels import build_channels                                    # noqa: E402

OUT = os.path.join(ROOT, "runs", "RR_W003_X9A_CONTRACT", "out")
os.makedirs(OUT, exist_ok=True)
LEDGER = os.path.join(ROOT, "runs", "RR_W001_ACTION_VALUE_LEDGER", "out", "ledger_p1pct.csv")
SPLIT = pd.Timestamp("2022-01-01")
A, B = np.datetime64("2022-07-01"), np.datetime64("2026-08-01")
W72_TARGET = {"2006-2021": (3948, 28.6, 1.83, 1.105), "2022-2026": (950, 123.0, 1.05, 1.095)}
_t0 = _time.time()
_fh = open(os.path.join(OUT, "x9a_contract.txt"), "w", encoding="utf-8")


def P_(*a):
    print(*a, flush=True)
    print(*a, file=_fh)
    _fh.flush()


def el():
    return f"[{_time.time() - _t0:6.0f}s]"


def main():
    P_("=" * 122)
    P_("=== RR_W003 - X9a DECISION-EVENT CONTRACT.  ENGINEERING_ONLY.")
    P_("=== Nothing is selected, tuned or promoted. Economics are REPRODUCED, never newly chosen.")
    P_("=" * 122)

    # ================================================================= reproduction gate
    DD = load_deep("2006-01-05", "2026-05-29 17:00")
    W1.DEV_END = pd.Timestamp("2026-07-31").date()
    flat_d = DD["t"] >= DD["sess_end"][DD["sid"]] - np.timedelta64(21 * 60, "s")
    CH = build_channels(DD, which=["X9a_disp_sessanchor"])
    x9 = CH["X9a_disp_sessanchor"]
    P_(f"{el()} deep substrate {DD['n']:,} bars / {DD['n_sess']:,} sessions; channel rebuilt")

    trl = sfills(DD, np.where(flat_d, 0, x9).astype(np.int8), halt=1300.0, target=1000.0)
    df = pd.DataFrame(dict(et=pd.to_datetime([x["et"] for x in trl]),
                           xt=pd.to_datetime([x["xt"] for x in trl]),
                           d=[x["d"] for x in trl], pnl=[x["pnl"] for x in trl]))
    P_("")
    P_("=" * 122)
    P_("=== 1. REPRODUCTION GATE - is this the SAME object W72 measured?  BLOCKING.")
    P_("=" * 122)
    P_(f"{'era':<12}{'trades':>9}{'W72':>9}{'$/trade':>10}{'W72':>10}{'t':>7}{'W72':>7}"
       f"{'PF':>7}{'W72':>7}{'':>10}")
    allok = True
    for lab, m in (("2006-2021", df["et"] < SPLIT), ("2022-2026", df["et"] >= SPLIT)):
        q = df[m]
        se = q["pnl"].std(ddof=1) / np.sqrt(len(q))
        gw = q.loc[q["pnl"] > 0, "pnl"].sum(); gl = -q.loc[q["pnl"] < 0, "pnl"].sum()
        n0, p0, t0_, f0 = W72_TARGET[lab]
        t_ = q["pnl"].mean() / se
        pf = gw / gl
        ok = (abs(len(q) - n0) <= max(2, 0.01 * n0)) and (abs(q["pnl"].mean() - p0) < 1.0)
        allok &= ok
        P_(f"{lab:<12}{len(q):>9,}{n0:>9,}{q['pnl'].mean():>10.1f}{p0:>10.1f}"
           f"{t_:>7.2f}{t0_:>7.2f}{pf:>7.3f}{f0:>7.3f}{('  OK' if ok else '  MISMATCH'):>10}")
    P_("")
    if not allok:
        P_("    GATE FAILED - this is not the object W72 measured. No contract is issued.")
        _fh.close(); sys.exit(1)
    P_("    GATE PASSED - the channel and its economics reproduce. The object is the same one.")

    # ================================================================= the contract
    P_("")
    P_("=" * 122)
    P_("=== 2. THE DECISION-EVENT CONTRACT")
    P_("=" * 122)
    n = DD["n"]
    fb = DD["fb"]
    runs = []
    i = 0
    while i < n:
        if x9[i] == 0:
            i += 1; continue
        j = i
        while j + 1 < n and x9[j + 1] == x9[i] and not fb[j + 1]:
            j += 1
        runs.append((i, j))
        i = j + 1
    L = np.array([b_ - a_ + 1 for a_, b_ in runs])
    inwin = (df["et"] >= pd.Timestamp("2022-07-01")) & (df["et"] < pd.Timestamp("2026-08-01"))
    P_(f"    signal array          latched int8, one value per bar, exactly like P1/PCT's")
    P_(f"    contiguous same-sign session-bounded runs   {len(runs):>10,}")
    P_(f"    run length bars       mean {L.mean():>6.1f}   median {np.median(L):>5.0f}   "
       f"max {L.max():,}")
    P_(f"    trades produced                             {len(df):>10,}")
    P_(f"    runs that never become a trade (box latched){len(runs) - len(df):>10,}")
    P_(f"    trades in the campaign-#7 window            {int(inwin.sum()):>10,}")
    P_(f"    direction balance     long {100*float((df['d']>0).mean()):.1f} %   "
       f"short {100*float((df['d']<0).mean()):.1f} %   <- TWO-SIDED, unlike P1/PCT")
    P_("")
    P_("    | field | value |")
    P_("    | expert_id            | X9A_DISP_SESSANCHOR |")
    P_("    | family_id            | DISPLACEMENT_CHANNEL |")
    P_("    | eligibility          | the latched channel changes to a new non-zero value |")
    P_("    | decision timestamp   | the OPEN of bar i |")
    P_("    | information cutoff   | close of bar i-1 (sfills reads dir_arr[i-1], as gfills does) |")
    P_("    | allowed actions      | ACCEPT / ABSTAIN |")
    P_("    | exits                | FROZEN: session box halt -1300 / target +1000, flat 21 min before session end |")
    P_("    | path dependent       | YES - same session-box latch as P1/PCT |")
    P_("    | counterfactual       | WELL DEFINED - suppress the contiguous run, replay the frozen policy |")

    # ================================================================= admission
    P_("")
    P_("=" * 122)
    P_("=== 3. ADMISSION - the five EXPERT_UNIVERSE criteria")
    P_("=" * 122)
    LP = pd.read_csv(LEDGER)
    LP = LP[LP["in_window_session"]]
    p1w = pd.Series(LP["baseline_trade_net"].to_numpy(),
                    index=pd.to_datetime(LP["session_date"])).resample("W").sum()
    x9w = pd.Series(df.loc[inwin, "pnl"].to_numpy(),
                    index=df.loc[inwin, "et"]).resample("W").sum()
    J = pd.concat([p1w.rename("p1"), x9w.rename("x9")], axis=1).fillna(0.0)
    rho_w = float(J["p1"].corr(J["x9"]))
    P_(f"    weekly rho(P1/PCT, X9a) on the campaign window, {len(J)} weeks : {rho_w:+.4f}")
    P_(f"    W88 recorded +0.613 and called it TOO CORRELATED; XM_CONFLICT sits at +0.081")
    P_("")
    crit = [
        ("R1", "deterministic, frozen rule", True,
         "build_channels is committed code; no parameter is chosen here"),
        ("R2", "reproducible opportunity timestamps", True,
         f"{len(runs):,} runs -> {len(df):,} trades, and the W72 era table reproduces"),
        ("R3", "meaningful economic DISTINCTNESS from the incumbent", rho_w < 0.30,
         f"weekly rho with P1/PCT = {rho_w:+.4f}"),
        ("R4", "enough observations for its proposed role", int(inwin.sum()) >= 300,
         f"{int(inwin.sum()):,} in-window trades"),
        ("R5", "a coherent counterfactual", True,
         "latched channel + session box = the RR_W001 replay applies unchanged"),
    ]
    P_(f"{'':<5}{'criterion':<50}{'verdict':>10}   evidence")
    for cid, desc, ok, ev in crit:
        P_(f"{cid:<5}{desc:<50}{('PASS' if ok else 'FAIL'):>10}   {ev}")
    P_("")
    npass = sum(1 for c in crit if c[2])
    P_(f"    {npass} of 5 criteria pass.")
    pd.DataFrame([dict(criterion=c[0], requirement=c[1], verdict="PASS" if c[2] else "FAIL",
                       evidence=c[3]) for c in crit]).to_csv(
        os.path.join(OUT, "admission.csv"), index=False)
    df.to_csv(os.path.join(OUT, "x9a_trades.csv"), index=False)
    J.to_csv(os.path.join(OUT, "weekly_p1_x9a.csv"))
    P_(f"\n{el()} done")
    _fh.close()


if __name__ == "__main__":
    main()
