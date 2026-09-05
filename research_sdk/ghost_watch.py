"""ghost_watch.py -- REAL-TIME GHOST-POSITION ALARM.  Read-only.  Works with the CURRENTLY
DEPLOYED v1 classes -- no redeploy, no recompile, nothing touched on the live account.

WHY THIS EXISTS
    The owner trades MNQ by hand on the same account the strategy trades. That is a stated,
    standing fact, so "do not do that" is not an available answer. The ghost-position defect
    has already fired TWICE in three sessions:

      2026-09-01  owner flattened XM's short by hand -> XM's exit never reached the broker,
                  and XM's only live trade record was destroyed.
      2026-09-03  owner flattened P1's long by hand  -> P1's exit OPENED a naked short 6 MNQ,
                  held 51 minutes, closed by Tradovate AutoLiq.

    In BOTH cases the strategy could not see it and no alarm existed. HD-23 fixes this in
    source, but it is not deployed until the 2026-09-21 roll window. THIS SCRIPT COVERS THE
    GAP, today, from outside the strategy.

THE RULE IT ALARMS ON -- deliberately one-sided, to keep false positives at zero
    DANGER  <=>  the strategy claims a position the ACCOUNT CANNOT SUPPORT in that direction.

    strategy long 6, account long >= 6   -> OK. The owner may hold extra; that is theirs.
    strategy long 6, account long 4      -> DANGER: 2 of the strategy's contracts do not exist.
    strategy long 6, account FLAT        -> DANGER: this is exactly 2026-09-03 at 11:16.
    strategy FLAT,   account anything    -> OK, and SILENT. Owner positions are not the
                                            strategy's business and must never raise an alarm.

    ⚠️ WHAT THIS CANNOT SEE, stated next to what it can (CLAUDE.md section 4):
      * It cannot tell WHOSE contracts were removed. On a hand-traded account that is
        PROVABLY undecidable from the account alone. It does not try. It answers a strictly
        weaker and fully decidable question -- "can the account support what the strategy
        thinks it holds?" -- which is enough to catch every occurrence of this defect.
      * It reads the strategy's position from its own per-bar export, so it is only as fresh
        as the last written bar (<= 1 min while the writer is alive) and it is BLIND if that
        writer is dead. It reports the age and says so. Run `writer_watchdog.py` too.
      * A second strategy on the same account would make the account a three-way sum and this
        rule would false-positive. As of 2026-09-05 there is exactly one, and the script
        ABORTS rather than guess if it finds evidence of more.

WHAT TO DO WHEN IT FIRES  -- decide BEFORE the strategy's exit is due, not after
    A) restore the position by hand (buy/sell back what was removed), or
    B) DISABLE the strategy while it is in this state.
    Doing nothing means its exit fires against an account that cannot absorb it.
    🔴 Do NOT use NT8's Flatten button: it flattens the strategy's position too and latches
       RECONCILE-BREAK.

USAGE
    python -m research_sdk.ghost_watch                 one-shot; exit 0 = OK, 1 = DANGER
    python -m research_sdk.ghost_watch --watch 30      loop every 30 s until Ctrl-C
    python -m research_sdk.ghost_watch --json          machine-readable
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys
import time
from datetime import datetime, timedelta

try:
    from zoneinfo import ZoneInfo
    ET = ZoneInfo("America/New_York")
except Exception:                                                    # pragma: no cover
    ET = None

# ---- the deployed live configuration, 2026-09-05 (ListAllStrategies) --------------------
LIVE_ACCOUNT = "2047681"
EXEC_INSTRUMENT = "MNQU6"
MNQ_PER_NQ = 3
LIVE_EXPORT = r"C:\NT8_ForwardLogs\mnq\export\we_p1pct_p1pct.csv"
QTY_COL = 9                                   # `qty` = myQty, in NQ UNITS, per the header
NT8_LOG_DIR = os.path.join(os.path.expanduser("~"), "Documents", "NinjaTrader 8", "log")

# `Instrument='MNQU6' Account='2047681' Average price=X Quantity=N Market position=P Operation=O`
POS_RE = re.compile(
    r"^(?P<ts>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}):\d+\|[^|]*\|[^|]*\|"
    r"Instrument='(?P<inst>[^']+)' Account='(?P<acct>[^']+)' Average price=[\d.]+ "
    r"Quantity=(?P<qty>\d+) Market position=(?P<mp>\w+)")


def now_et():
    return datetime.now(ET) if ET else datetime.now()


def strategy_position():
    """(signed EXEC-instrument qty the strategy believes it holds, bar ts, age_min) or None."""
    if not os.path.exists(LIVE_EXPORT):
        return None
    with open(LIVE_EXPORT, "rb") as fh:                      # tail without loading 30+ MB
        fh.seek(0, os.SEEK_END)
        size = fh.tell()
        fh.seek(max(0, size - 8192))
        tail = fh.read().decode("utf-8", "replace").splitlines()
    for line in reversed(tail):
        p = line.split(",")
        if len(p) <= QTY_COL:
            continue
        try:
            ts = datetime.strptime(p[0], "%Y-%m-%d %H:%M:%S")
            nq_units = int(p[QTY_COL])
        except ValueError:
            continue
        if ET:
            ts = ts.replace(tzinfo=ET)
        age = (now_et() - ts).total_seconds() / 60.0
        return nq_units * MNQ_PER_NQ, ts, age
    return None


def account_position(days=3):
    """(signed account qty on EXEC_INSTRUMENT, ts) from NT8's OWN log, or None."""
    files = sorted(glob.glob(os.path.join(NT8_LOG_DIR, "log.*.txt")))[-(days * 4):]
    best = None
    for f in files:
        try:
            with open(f, "r", encoding="utf-8", errors="replace") as fh:
                for line in fh:
                    if "Instrument='" + EXEC_INSTRUMENT + "'" not in line:
                        continue
                    m = POS_RE.match(line)
                    if not m or m.group("acct") != LIVE_ACCOUNT:
                        continue
                    q = int(m.group("qty"))
                    mp = m.group("mp")
                    signed = q if mp == "Long" else (-q if mp == "Short" else 0)
                    ts = datetime.strptime(m.group("ts"), "%Y-%m-%d %H:%M:%S")
                    if ET:
                        ts = ts.replace(tzinfo=ET)
                    if best is None or ts >= best[1]:
                        best = (signed, ts)
        except OSError:
            continue
    return best


def other_strategy_orders(days=2):
    """Evidence of a SECOND strategy on this account. If found, the one-sided rule is unsafe."""
    files = sorted(glob.glob(os.path.join(NT8_LOG_DIR, "log.*.txt")))[-(days * 4):]
    names = set()
    for f in files:
        try:
            with open(f, "r", encoding="utf-8", errors="replace") as fh:
                for line in fh:
                    if "/" + LIVE_ACCOUNT + "'" not in line or "Name='" not in line:
                        continue
                    m = re.search(r"Name='([^']+)'", line)
                    if m and m.group(1):
                        names.add(m.group(1))
        except OSError:
            continue
    return names - {"L", "XL", "XLsess"}          # P1's own order names


def session_open(t=None):
    """CME index futures: Sun 18:00 ET -> Fri 17:00 ET, with a daily 17:00-18:00 break.

    Session awareness is not cosmetic. Without it this script reports BLIND every weekend,
    and an alarm that cries wolf gets muted -- which is precisely how the 2026-09-01 export
    outage survived five hours unnoticed.
    """
    t = t or now_et()
    wd, hm = t.weekday(), t.hour * 60 + t.minute        # Mon=0 .. Sun=6
    if wd == 5:                                          # Saturday: closed all day
        return False
    if wd == 6:                                          # Sunday: opens 18:00
        return hm >= 18 * 60
    if wd == 4 and hm >= 17 * 60:                        # Friday: closes 17:00
        return False
    return not (17 * 60 <= hm < 18 * 60)                 # daily maintenance break


def evaluate():
    sp = strategy_position()
    ap = account_position()
    foreign = other_strategy_orders()
    out = {"checked_et": now_et().strftime("%Y-%m-%d %H:%M:%S"), "verdict": "OK", "why": "",
           "session_open": session_open()}

    if foreign:
        out["verdict"] = "ABORT"
        out["why"] = ("a SECOND strategy appears to trade this account (order names "
                      + ", ".join(sorted(foreign)) + "). The account becomes a three-way sum "
                      "and this one-sided rule would false-positive. Refusing to guess.")
        return out
    if sp is None:
        out["verdict"] = "BLIND"
        out["why"] = "cannot read the strategy's export at " + LIVE_EXPORT
        return out
    if ap is None:
        out["verdict"] = "BLIND"
        out["why"] = "no " + EXEC_INSTRUMENT + " position line for " + LIVE_ACCOUNT + " in the NT8 log"
        return out

    mine, bar_ts, age = sp
    acct, acct_ts = ap
    out.update(strategy_claims=mine, account_holds=acct, bar_et=bar_ts.strftime("%H:%M:%S"),
               bar_age_min=round(age, 1), account_ts_et=acct_ts.strftime("%m-%d %H:%M:%S"))

    if age > 10:
        if not out["session_open"]:
            out["verdict"] = "IDLE"
            out["why"] = ("session is closed; a stale export is expected. Last known: strategy "
                          "%+d, account %+d." % (mine, acct))
            return out
        out["verdict"] = "BLIND"
        out["why"] = ("the strategy's export has not advanced for %.0f min WHILE THE SESSION IS "
                      "OPEN -- its position is UNKNOWN, not zero. Run writer_watchdog.py." % age)
        return out
    if mine == 0:
        out["why"] = ("strategy is FLAT. Any account position is the owner's and is not this "
                      "script's business.")
        return out
    supported = (acct >= mine) if mine > 0 else (acct <= mine)
    if supported:
        out["why"] = "the account can support what the strategy claims."
        return out

    short = mine - acct if mine > 0 else acct - mine
    out["verdict"] = "DANGER"
    out["shortfall"] = abs(short)
    out["why"] = (
        "THE ACCOUNT CANNOT SUPPORT THE STRATEGY'S POSITION. It claims %+d %s; the account "
        "holds %+d. %d contract(s) the strategy thinks it owns DO NOT EXIST. When its exit "
        "fires it will submit the full %d and OPEN an unowned position for the difference -- "
        "this is 2026-09-03 exactly." % (mine, EXEC_INSTRUMENT, acct, abs(short), abs(mine)))
    return out


def render(r):
    v = r["verdict"]
    bar = "=" * 96
    print(bar)
    print("GHOST WATCH  %s ET   account %s   %s   MnqPerNq=%d"
          % (r["checked_et"], LIVE_ACCOUNT, EXEC_INSTRUMENT, MNQ_PER_NQ))
    print(bar)
    if "strategy_claims" in r:
        print("  strategy claims : %+d   (bar %s ET, %s min old)"
              % (r["strategy_claims"], r["bar_et"], r["bar_age_min"]))
        print("  account holds   : %+d   (last change %s ET)"
              % (r["account_holds"], r["account_ts_et"]))
    print(bar)
    if v == "DANGER":
        print("*** DANGER ***  " + r["why"])
        print("")
        print("  DECIDE BEFORE THE STRATEGY'S EXIT IS DUE:")
        print("    A) restore the position by hand, or")
        print("    B) DISABLE the strategy while it is in this state.")
        print("  Doing nothing means its exit fires against an account that cannot absorb it.")
        print("  *** DO NOT use NT8's Flatten button -- it flattens the strategy's position")
        print("      too and latches RECONCILE-BREAK. ***")
    elif v in ("BLIND", "ABORT"):
        print("%s: %s" % (v, r["why"]))
        print("  A blind check is NOT a clean bill of health.")
    else:
        print("OK -- " + r["why"])
    print(bar)


def selftest():
    """REPLAY THE KNOWN INCIDENT. A guard that cannot be shown to catch the event it was
    written for is not trustworthy, so this replays 2026-09-03 minute by minute from the
    SAME two sources the live check uses and asserts the alarm fires in the right window."""
    print("=" * 96)
    print("SELFTEST -- replaying 2026-09-03 from the real export and the real NT8 log")
    print("=" * 96)

    rows = []
    with open(LIVE_EXPORT, "r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            if not line.startswith("2026-09-03 "):
                continue
            p = line.split(",")
            if len(p) > QTY_COL:
                try:
                    rows.append((datetime.strptime(p[0], "%Y-%m-%d %H:%M:%S"),
                                 int(p[QTY_COL]) * MNQ_PER_NQ))
                except ValueError:
                    pass
    # account position timeline for that day, from NT8's own log
    tl = []
    for f in sorted(glob.glob(os.path.join(NT8_LOG_DIR, "log.20260903*.txt"))):
        with open(f, "r", encoding="utf-8", errors="replace") as fh:
            for line in fh:
                if "Instrument='" + EXEC_INSTRUMENT + "'" not in line:
                    continue
                m = POS_RE.match(line)
                if m and m.group("acct") == LIVE_ACCOUNT:
                    q, mp = int(m.group("qty")), m.group("mp")
                    tl.append((datetime.strptime(m.group("ts"), "%Y-%m-%d %H:%M:%S"),
                               q if mp == "Long" else (-q if mp == "Short" else 0)))
    tl.sort()
    if not rows or not tl:
        print("  CANNOT RUN: export rows=%d, account rows=%d" % (len(rows), len(tl)))
        return 1

    def acct_at(t):
        v = 0
        for ts, q in tl:
            if ts <= t:
                v = q
            else:
                break
        return v

    fired = [(t, mine, acct_at(t)) for t, mine in rows
             if mine != 0 and not ((acct_at(t) >= mine) if mine > 0 else (acct_at(t) <= mine))]

    gates, ok = [], True
    g1 = bool(fired)
    gates.append(("G1", "the alarm fires at all on 2026-09-03", "yes",
                  "%d bars" % len(fired), g1))
    first = fired[0][0] if fired else None
    g2 = bool(first and datetime(2026, 9, 3, 11, 16) <= first <= datetime(2026, 9, 3, 11, 20))
    gates.append(("G2", "first fire is within 4 min of the 11:16:16 manual sell", "11:16-11:20",
                  first.strftime("%H:%M") if first else "never", g2))
    last = fired[-1][0] if fired else None
    g3 = bool(last and last >= datetime(2026, 9, 3, 15, 56))
    gates.append(("G3", "still firing at the 15:57 exit that opened the naked short", ">=15:56",
                  last.strftime("%H:%M") if last else "never", g3))
    pre = [t for t, _, _ in fired if t < datetime(2026, 9, 3, 11, 16)]
    g4 = not pre
    gates.append(("G4", "ZERO false positives before the manual sell", "0", str(len(pre)), g4))
    flat_bars = [(t, m) for t, m in rows if m == 0]
    g5 = len(flat_bars) > 0 and not [t for t, _, _ in fired if any(t == ft for ft, fm in flat_bars)]
    gates.append(("G5", "never fires while the strategy is FLAT (owner positions are theirs)",
                  "0", "0" if g5 else "some", g5))

    print("%-5s %-58s %12s %12s  %s" % ("GATE", "SPEC", "SPEC", "OBSERVED", "VERDICT"))
    print("-" * 96)
    for gid, d, sp_, obs, passed in gates:
        ok &= bool(passed)
        print("%-5s %-58s %12s %12s  %s" % (gid, d, sp_, obs, "PASS" if passed else "FAIL"))
    print("-" * 96)
    if fired:
        print("  window: %s -> %s ET, %d bars, shortfall %+d vs account %+d"
              % (fired[0][0].strftime("%H:%M"), fired[-1][0].strftime("%H:%M"), len(fired),
                 fired[0][1], fired[0][2]))
        print("  => the owner would have had 4h41m of warning before the 15:57 exit.")
    print("ALL PASS" if ok else "*** FAILED -- do not trust this alarm ***")
    print("=" * 96)
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description="real-time ghost-position alarm (read-only)")
    ap.add_argument("--watch", type=int, metavar="SEC", help="loop every SEC seconds")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--selftest", action="store_true",
                    help="replay the 2026-09-03 incident and assert the alarm catches it")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    while True:
        r = evaluate()
        print(json.dumps(r)) if a.json else render(r)
        if not a.watch:
            return 1 if r["verdict"] in ("DANGER", "ABORT") else 0
        try:
            time.sleep(max(5, a.watch))
        except KeyboardInterrupt:
            return 0


if __name__ == "__main__":
    sys.exit(main())
