"""W17 C4 compliance audit — the PRE-REGISTERED success criterion of runs/W17_C4_COMPLIANCE/spec.yaml.

Success = ZERO holding intervals intersecting the per-session initial-margin window
          [session_close - 15 minutes, 18:00 ET product open)
across all dev sessions, for both Product B objects. Not "fewer". Exactly 0.

BROKER FACT (MEGA PROMPT V6 §7, NinjaTrader Brokerage Lifetime): intraday margin is
effective from the product open until 15 minutes prior to the session close; holiday early
closes do NOT extend it; intraday margin resumes at the 18:00 ET product open. So the window
is per-session, not a fixed clock:
    normal 17:00 close -> [16:45, 18:00)
    13:00 close        -> [12:45, 18:00)
    13:15 close        -> [13:00, 18:00)
    09:15 close        -> [09:00, 18:00)

Inputs are the strategies' own NT8 execution ledgers (fills), not trade lists: a trade list
structurally cannot distinguish "no order submitted" from "order submitted, unfilled", which
is the error this wave had to correct (V6 §18, reference case).

Usage:  python c4_audit.py
"""
import os, sys, datetime as dt
import pandas as pd
import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
OUT = os.path.join(ROOT, "runs", "W17_C4_COMPLIANCE", "out")
PB = os.path.join(ROOT, "runs", "PRODUCTB_ONECONTRACT_FINAL", "out")
NT8M = os.path.join(ROOT, "runs", "SMV2M_MASTER_BUILD", "out", "nt8")

DEV_END = pd.Timestamp("2026-05-29 17:00:00")
MARGIN_LEAD_MIN = 15          # broker: intraday margin ends 15 min before session close
PRODUCT_OPEN = dt.time(18, 0)  # broker: intraday margin resumes at the 18:00 ET product open
NORMAL_CLOSE = dt.time(17, 0)


def session_closes():
    """Map close-date -> actual session-close timestamp, from the committed MNQ 3-min export.

    fbos is NT8's first-bar-of-session flag; bars are stamped at bar END, so a normal Globex
    session's final 3-min bar is stamped 17:00.
    """
    b = pd.read_csv(os.path.join(PB, "mnq_3m_raw.csv"), comment="#",
                    parse_dates=["time"], usecols=["time", "fbos"])
    b["sess"] = b["fbos"].cumsum()
    closes = b.groupby("sess")["time"].max()
    return {t.date(): t for t in closes}


SESS_CLOSE = session_closes()


def margin_window(close_ts):
    lo = close_ts - pd.Timedelta(minutes=MARGIN_LEAD_MIN)
    hi = pd.Timestamp(dt.datetime.combine(close_ts.date(), PRODUCT_OPEN))
    return lo, hi


SIGN = {"Buy": +1, "BuyToCover": +1, "Sell": -1, "SellShort": -1}


def intervals_from_fills(path):
    """Flat-to-flat holding intervals from an execution ledger.

    Position is reconstructed from ORDER ACTIONS, not from the `target` column.
    This matters and was a real defect in the first version of this script: `target` is the
    strategy's last *decided* target, and it is NOT updated when the ENGINE closes a position
    on its own (an "Exit on session close" fill, e.g. NQ 2023-04-05 14:03 at a data-gap
    boundary). Using `target` therefore reports the position as still open across a genuinely
    flat stretch and manufactures a phantom breach. Verified against the independent pre-fix
    trade list, which shows the position flat 14:03 -> 20:33 on that date.
    """
    f = pd.read_csv(path, comment="#", parse_dates=["time"]).sort_values("n")
    out, open_at, pos = [], None, 0
    for t, act, q in zip(f.time, f.order_action, f.qty):
        s = SIGN.get(str(act).strip())
        if s is None:
            raise ValueError("unrecognised order_action %r in %s" % (act, path))
        prev = pos
        pos += s * int(q)
        if prev == 0 and pos != 0:
            open_at = t
        elif prev != 0 and pos == 0 and open_at is not None:
            out.append((open_at, t)); open_at = None
    if open_at is not None:
        out.append((open_at, f.time.iloc[-1]))
    return out, f


def intervals_from_trades(path):
    tr = pd.read_csv(path, parse_dates=["entry_time", "exit_time"])
    return list(zip(tr.entry_time, tr.exit_time)), tr


def audit(name, ivals):
    ivals = [(a, b) for a, b in ivals if b <= DEV_END]
    normal_hits, early_hits = [], []
    for a, b in ivals:
        d = a.date()
        while d <= b.date():
            ct = SESS_CLOSE.get(d)
            if ct is not None:
                lo, hi = margin_window(ct)
                if a < hi and b > lo:
                    (early_hits if ct.time() != NORMAL_CLOSE else normal_hits).append((a, b, ct))
            d += dt.timedelta(days=1)
    n = len(ivals)
    total = len(normal_hits) + len(early_hits)
    verdict = "PASS" if total == 0 else "FAIL"
    print(f"\n{name}")
    print(f"   holding intervals (dev window)                     : {n}")
    print(f"   breaches on NORMAL-close sessions  [16:45,18:00)   : {len(normal_hits)}")
    print(f"   breaches on EARLY-close sessions                   : {len(early_hits)}")
    print(f"   TOTAL C4 BREACHES                                  : {total}   -> {verdict}")
    if early_hits:
        dates = sorted({str(c.date()) for _, _, c in early_hits})
        print(f"     early-close breach dates ({len(dates)}): {', '.join(dates)}")
    if normal_hits:
        for a, b, c in normal_hits[:20]:
            print(f"     normal-session breach: held {a} -> {b} (session close {c})")
    return total, n


if __name__ == "__main__":
    print("=" * 78)
    print("W17 C4 COMPLIANCE AUDIT — pre-registered success criterion")
    print("=" * 78)
    print(f"dev sessions in the close map: {len(SESS_CLOSE)}   "
          f"early closes: {sum(1 for t in SESS_CLOSE.values() if t.time() != NORMAL_CLOSE)}")

    results = {}

    print("\n--- BEFORE (the objects this wave supersedes) ---")
    for nm, fn in (("BEST_ONE_NQ  (SolarWaveOneContractNQ_Final)", "nt_trades_nq.csv"),
                   ("BEST_ONE_MNQ (SolarWaveOneContractMNQ_Final)", "nt_trades_mnq.csv")):
        iv, _ = intervals_from_trades(os.path.join(PB, fn))
        results["before:" + nm] = audit(nm, iv)

    nm = "Product A    (SolarWaveSMMaster_v2)"
    iv, _ = intervals_from_fills(os.path.join(NT8M, "smm_v2_fills.csv"))
    results["before:" + nm] = audit(nm, iv)

    print("\n--- AFTER (this wave's rebuilds) ---")
    for nm, fn in (("BEST_ONE_NQ  (SolarWaveOneContractNQ_v2)", "nq_v2_fills.csv"),
                   ("BEST_ONE_MNQ (SolarWaveOneContractMNQ_v2)", "mnq_v2_fills.csv")):
        p = os.path.join(OUT, fn)
        if not os.path.exists(p):
            print(f"\n{nm}\n   LEDGER NOT PRESENT ({fn}) — backtest not yet run.")
            continue
        iv, f = intervals_from_fills(p)
        results["after:" + nm] = audit(nm, iv)
        print(f"   executions in ledger: {len(f)}")

    print("\n" + "=" * 78)
    fails = [k for k, (t, _) in results.items() if k.startswith("after:") and t > 0]
    if any(k.startswith("after:") for k in results):
        print("OVERALL: " + ("PASS — every rebuilt object has ZERO breaches"
                             if not fails else "FAIL — " + "; ".join(fails)))
