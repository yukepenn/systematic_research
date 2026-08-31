"""LIVE READINESS ACCEPTANCE SET — machine-verifiable, no MCP required.

Every assertion here was bought with a specific failure during 2026-08-30/31. The point of the file
is that "the book looks healthy" is NOT an acceptance criterion; these are.

WHY EACH CHECK EXISTS (do not delete one without reading its reason):

  R1  ROLL-PLAN IN THE FUTURE.  THE CHECK EVERYONE OMITS AND THE ONLY ONE THAT CATCHES A DEAD BOOK.
      ResolveRollDates runs ONCE on the first realtime bar and RollBlocked() is monotone, while
      GetNextRolloverDate is a ROOT-level lookup that cannot tell you already rolled.  Re-enabling
      inside the block window recomputes the SAME date and blocks new entries PERMANENTLY - while the
      strategy still reads Enabled / Realtime / bars advancing / warm-up GO / flat and passes every
      other item on this list.
  R2  WARM-UP GO + qual_entries.  A cold deploy loads ~4 sessions, so P1's 250-entry quality window
      never fills and it trades size-1 only for ~3 months.  The qty-2 bucket is ~43.5% of delivered
      net.  DaysToLoad=365 is the strategy, not hygiene.
  R3  NO ROLL-BLOCK / ENTRY-BLOCKED lines.
  R4  LEDGER RECONCILED at the historical->realtime transition (WARMUP-CARRY-FLAT).
  R5  INSTRUMENT GUARD ARMED.  HD05 defaults to "" = DISABLED and shipped that way for the entire
      first forward window.  An empty ExpectInstrument is a FAIL, not a default.
  R6  DECISION LEDGER ACTUALLY WRITING - verified BY READING THE FILE.
      ⚠️ NEVER use file length.  A directory-reported size of 0 on an open handle is a METADATA
      ARTIFACT: an unflushed 46,313,472-byte file reported 0 B for over an hour and I wrongly called
      it data loss.  Read the last row and check its timestamp.
  R7  SERIES CONTRACT-MONTH AGREEMENT for multi-series strategies.  A partial roll trades Dec NQ
      against Sept secondaries.
  R8  DaysToLoad present and >= the convergence floor (~330d; measured convergence is ~9 months for
      decision state and ~10.5 months for position SIZE, which is the binding horizon).

⚠️ TWO SOURCES THAT LIE, AND ARE THEREFORE NOT USED HERE:
  * the CrossTrade deployment REGISTRY - DisableStrategy does not clear it, so it reports stale rows
    (observed: 3 deployments when 2 strategies existed).  Count strategies with ListAllStrategies.
  * ListDeployedStrategies.live.performance - net_profit_currency is DaysToLoad warm-up SIMULATION
    presented inside a block labelled "live"; and on a 4-series strategy the scalar current_bar /
    instrumentName report a SECONDARY series.  Read currentBars[0] and instruments[].

Usage:  python live_readiness_check.py --tags p1pct,xm2
        python live_readiness_check.py --selftest
"""
from __future__ import annotations
import argparse, glob, os, re, sys
from datetime import datetime, date

NT8 = os.path.join(os.path.expanduser("~"), "Documents", "NinjaTrader 8")
LOGDIR = os.path.join(NT8, "log")
DEFAULT_WARMUP = r"C:\NT8_ForwardLogs\warmup"
DEFAULT_EXPORT = r"C:\NT8_ForwardLogs\export"
MIN_DAYS_TO_LOAD = 330          # measured convergence floor; do NOT lower without re-measuring

ROLL_RE = re.compile(r"\[HD (\S+) (\S+)\] ROLL-PLAN blockNewEntriesFrom=(\S+)")
CARRY_RE = re.compile(r"\[HD (\S+) (\S+)\] WARMUP-CARRY-(FLAT|NONFLAT)")
BLOCK_RE = re.compile(r"ROLL-BLOCK|ENTRY-BLOCKED")
HD05_RE = re.compile(r"\[HD (\S+) (\S+)\] HD05 primary OK .*want=(\S+ \S+)")


def _logs():
    fs = [f for f in glob.glob(os.path.join(LOGDIR, "log.*.txt")) if ".en." not in f]
    return sorted(fs)


def _log_lines():
    out = []
    for f in _logs():
        try:
            with open(f, "r", encoding="utf-8", errors="replace") as fh:
                out.extend(fh.read().splitlines())
        except OSError:
            pass
    return out


def last_roll_plan(lines, tag):
    """Newest ROLL-PLAN for a tag -> date, or None. Newest wins: a redeploy supersedes."""
    found = None
    for ln in lines:
        m = ROLL_RE.search(ln)
        if m and m.group(2) == tag:
            try:
                found = datetime.strptime(m.group(3), "%Y-%m-%d").date()
            except ValueError:
                found = None
    return found


def last_carry(lines, tag):
    found = None
    for ln in lines:
        m = CARRY_RE.search(ln)
        if m and m.group(2) == tag:
            found = m.group(3)
    return found


def last_hd05(lines, tag):
    found = None
    for ln in lines:
        m = HD05_RE.search(ln)
        if m and m.group(2) == tag:
            found = m.group(3)
    return found


def newest_warmup_cert(tag, warmup_dir):
    c = sorted(glob.glob(os.path.join(warmup_dir, f"warmup_{tag}_*.csv")))
    if not c:
        return None
    rows = open(c[-1], encoding="utf-8", errors="replace").read().splitlines()
    gates, env, verdict = {}, {}, None
    for r in rows[1:]:
        p = r.split(",")
        if len(p) >= 9 and p[3]:
            verdict = p[3]
            gates[p[4]] = (p[7], p[8])          # observed, pass
        elif len(p) >= 3 and p[0] == "env":
            env[p[1]] = p[2]
    return {"path": c[-1], "verdict": verdict, "gates": gates, "env": env}


def ledger_last_ts(export_dir, tag, prefix):
    """R6: READ the file. NEVER trust its length."""
    p = os.path.join(export_dir, f"we_{prefix}_{tag}.csv")
    if not os.path.exists(p):
        return None, 0
    last, n = None, 0
    with open(p, "r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            n += 1
            if line.strip():
                last = line
    if n <= 1 or not last:
        return None, n
    try:
        return datetime.strptime(last.split(",")[0], "%Y-%m-%d %H:%M:%S"), n
    except ValueError:
        return None, n


def check(tags, warmup_dir=DEFAULT_WARMUP, export_dir=DEFAULT_EXPORT,
          today=None, lines=None, prefixes=None):
    today = today or date.today()
    lines = _log_lines() if lines is None else lines
    prefixes = prefixes or {"p1pct": "p1pct", "xm2": "xm"}
    fails, notes = [], []

    for ln in lines:
        if BLOCK_RE.search(ln):
            fails.append(f"R3 blocking line present: {ln.strip()[:140]}")

    for tag in tags:
        rp = last_roll_plan(lines, tag)
        if rp is None:
            fails.append(f"R1 [{tag}] no ROLL-PLAN found - the strategy has not seen a realtime bar")
        elif rp <= today:
            fails.append(f"R1 [{tag}] 🔴 ROLL-PLAN blockNewEntriesFrom={rp} is NOT in the future "
                         f"(today {today}) - THE BOOK IS LATCHED DEAD while looking healthy")
        else:
            notes.append(f"R1 [{tag}] roll block {rp} ({(rp - today).days}d away) OK")

        cert = newest_warmup_cert(tag, warmup_dir)
        if cert is None:
            fails.append(f"R2 [{tag}] no warm-up certificate - WarmupCertDir unset or never written")
        else:
            if cert["verdict"] != "GO":
                fails.append(f"R2 [{tag}] warm-up verdict={cert['verdict']} (need GO)")
            for g, (obs, ok) in cert["gates"].items():
                if ok != "PASS":
                    fails.append(f"R2 [{tag}] gate {g} = {ok} (observed {obs})")
            q = cert["gates"].get("qual_entries")
            if q and int(q[0]) < 250:
                fails.append(f"R2 [{tag}] qual_entries {q[0]} < 250 - quality sizing NOT warm")
            dtl = cert["env"].get("DaysToLoad")
            if dtl is None or int(dtl) < MIN_DAYS_TO_LOAD:
                fails.append(f"R8 [{tag}] DaysToLoad={dtl} < {MIN_DAYS_TO_LOAD}")
            im = cert["env"].get("instrument_mismatch")
            if im is not None and im != "False":
                fails.append(f"R7 [{tag}] instrument_mismatch={im}")
            months = {k: v for k, v in cert["env"].items() if k.endswith("_expiry")}
            if len(set(months.values())) > 1:
                fails.append(f"R7 [{tag}] series expiries disagree: {months}")

        if last_carry(lines, tag) != "FLAT":
            fails.append(f"R4 [{tag}] ledger/position not reconciled FLAT at transition")

        if tag == "p1pct" and last_hd05(lines, tag) is None:
            fails.append(f"R5 [{tag}] instrument guard NOT armed (ExpectInstrument empty = disabled)")

        pre = prefixes.get(tag)
        if pre:
            ts, n = ledger_last_ts(export_dir, tag, pre)
            if ts is None:
                fails.append(f"R6 [{tag}] decision ledger unreadable/empty ({n} lines) - READ it, "
                             f"never trust file length")
            else:
                notes.append(f"R6 [{tag}] ledger {n:,} rows, last {ts}")

    return (len(fails) == 0), fails, notes


def selftest() -> int:
    """Every check must FIRE. A guard without teeth is not a guard."""
    ok = bad = 0

    def t(name, cond):
        nonlocal ok, bad
        if cond:
            ok += 1; print(f"  PASS {name}")
        else:
            bad += 1; print(f"  FAIL {name}")

    good = [
        "2026-08-31 10:31 [HD WeeklyEdgeP1PCT_v3 p1pct] ROLL-PLAN blockNewEntriesFrom=2026-09-08 leadDays=8",
        "2026-08-31 10:31 [HD WeeklyEdgeP1PCT_v3 p1pct] WARMUP-CARRY-FLAT ledger=0 strategyPosition=0",
        "2026-08-31 10:30 [HD WeeklyEdgeP1PCT_v3 p1pct] HD05 primary OK instrument=NQU6 expiry=2026-09-01 want=NQ 09-26",
    ]
    d = date(2026, 8, 31)
    t("roll plan in the future parses", last_roll_plan(good, "p1pct") == date(2026, 9, 8))
    t("carry FLAT parses", last_carry(good, "p1pct") == "FLAT")
    t("HD05 armed parses", last_hd05(good, "p1pct") == "NQ 09-26")

    # R1 must FIRE on a past block date - the latched-dead case
    late = [good[0].replace("2026-09-08", "2026-09-06"), good[1], good[2]]
    _, f, _ = check(["p1pct"], warmup_dir="__none__", export_dir="__none__",
                    today=date(2026, 9, 10), lines=late, prefixes={})
    t("R1 FIRES on a past roll-block date", any("LATCHED DEAD" in x for x in f))

    # R1 must NOT fire before the window
    _, f2, _ = check(["p1pct"], warmup_dir="__none__", export_dir="__none__",
                     today=d, lines=late, prefixes={})
    t("R1 quiet before the window", not any("LATCHED DEAD" in x for x in f2))

    # newest ROLL-PLAN wins (a redeploy supersedes an older line)
    two = [good[0].replace("2026-09-08", "2026-09-01"), good[0]]
    t("newest ROLL-PLAN supersedes", last_roll_plan(two, "p1pct") == date(2026, 9, 8))

    # R3 must fire on a block line
    _, f3, _ = check(["p1pct"], warmup_dir="__none__", export_dir="__none__", today=d,
                     lines=good + ["ROLL-BLOCK new entries refused from 2026-09-08"], prefixes={})
    t("R3 FIRES on ROLL-BLOCK", any(x.startswith("R3") for x in f3))

    # R4 must fire when the ledger did not reconcile flat
    nf = [good[0], good[1].replace("CARRY-FLAT", "CARRY-NONFLAT"), good[2]]
    _, f4, _ = check(["p1pct"], warmup_dir="__none__", export_dir="__none__", today=d,
                     lines=nf, prefixes={})
    t("R4 FIRES on CARRY-NONFLAT", any(x.startswith("R4") for x in f4))

    # R5 must fire when the instrument guard is disabled
    _, f5, _ = check(["p1pct"], warmup_dir="__none__", export_dir="__none__", today=d,
                     lines=good[:2], prefixes={})
    t("R5 FIRES when HD05 absent", any(x.startswith("R5") for x in f5))

    # R1 must fire when no realtime bar has been seen at all
    _, f6, _ = check(["p1pct"], warmup_dir="__none__", export_dir="__none__", today=d,
                     lines=[], prefixes={})
    t("R1 FIRES when no ROLL-PLAN exists", any("no ROLL-PLAN" in x for x in f6))

    print(f"\nselftest {ok}/{ok + bad}")
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--tags", default="p1pct,xm2")
    ap.add_argument("--warmup", default=DEFAULT_WARMUP)
    ap.add_argument("--export", default=DEFAULT_EXPORT)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(selftest())
    passed, fails, notes = check([t.strip() for t in a.tags.split(",") if t.strip()],
                                 warmup_dir=a.warmup, export_dir=a.export)
    for n in notes:
        print("  ok   " + n)
    for f in fails:
        print("  FAIL " + f)
    print("\nLIVE READINESS: " + ("PASS" if passed else f"FAIL ({len(fails)} findings)"))
    sys.exit(0 if passed else 1)
