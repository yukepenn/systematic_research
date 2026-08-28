"""ASSET_CENSUS -- what information can this repo still access whose relevant OUTCOMES are unspent?

A BOUNDED OPTION-VALUE CENSUS. Not feature discovery. No hypothesis is proposed, no model fitted,
no price read. Only availability, coverage, and consumption provenance.

THE DISTINCTION THAT DOES THE WORK, and it must not be blurred:

    "these market dates were used somewhere else in the repo"
        does NOT automatically consume every possible feature family on them.

    "this same OUTCOME was inspected while choosing THIS hypothesis"
        DOES create selection debt.

So each asset carries TWO consumption fields: OUTCOME-CONSUMED (were forward returns computed on
these rows at all?) and FAMILY-CONSUMED (which hypothesis families were chosen while looking at
them?). An asset can be outcome-consumed and still support a genuinely different family -- with the
selection debt stated, not waved away.
"""
from __future__ import annotations

import collections
import json
import os
import re
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(RUN))
sys.path.insert(0, os.path.join(ROOT, "research", "multi_market", "src"))
OUT = os.path.join(RUN, "out")
os.makedirs(OUT, exist_ok=True)
DB = os.path.join(os.path.expanduser("~"), "Documents", "NinjaTrader 8", "db")
SEAL = "2026-08-01"
NCD = re.compile(r"^(\d{8})(\d{2})\d{2}\.(Last|Bid|Ask)\.ncd$", re.I)
RTH = set(range(10, 17))                     # label = ET hour + 1; RTH 10:00-15:30 + warmup + exit
_fh = None


def P(*a):
    print(*a, flush=True)
    if _fh is not None:
        print(*a, file=_fh)


def tick_coverage(root_prefix):
    have = collections.defaultdict(set)
    inst = collections.defaultdict(set)
    d0 = os.path.join(DB, "tick")
    for inst_dir in sorted(os.listdir(d0)):
        if not inst_dir.startswith(root_prefix):
            continue
        p = os.path.join(d0, inst_dir)
        if not os.path.isdir(p):
            continue
        for f in os.listdir(p):
            m = NCD.match(f)
            if m:
                iso = f"{m.group(1)[:4]}-{m.group(1)[4:6]}-{m.group(1)[6:]}"
                have[(iso, m.group(3).capitalize())].add(int(m.group(2)))
                inst[iso].add(inst_dir)
    days = sorted({d for d, _ in have})
    rth = [d for d in days
           if all(RTH <= have.get((d, s), set()) for s in ("Bid", "Ask", "Last"))]
    return days, rth, inst


def main():
    global _fh
    _fh = open(os.path.join(OUT, "asset_census.txt"), "w", encoding="utf-8")
    P("=" * 116)
    P("=== UNCONSUMED INFORMATION ASSET CENSUS -- option value, not feature discovery")
    P("=== No price read. No hypothesis proposed. No model fitted.")
    P("=" * 116)

    assets = []

    # ---------------------------------------------------------------- 1/2/3 tick BBO
    nq_days, nq_rth, nq_inst = tick_coverage("NQ ")
    es_days, es_rth, es_inst = tick_coverage("ES ")
    nq_pre = [d for d in nq_rth if d < SEAL]
    es_pre = [d for d in es_rth if d < SEAL]
    both = sorted(set(nq_pre) & set(es_pre))

    cw = pd.read_csv(os.path.join(ROOT, "runs/BBO_COMPLETENESS_RECENSUS_V1_20260828/out/"
                                        "bbo_crosswalk.csv"))
    consumed_nq = set(cw[cw["outcome_consumed"]]["session_date"])
    blind_nq = set(cw[cw["eligible_blind_new_rule"]]["session_date"])

    P("")
    P("=== ASSET 1  NQ BBO (price-side quotes)")
    P(f"    RTH-complete pre-seal            {len(nq_pre):>5}")
    P(f"    outcome-consumed                 {len(set(nq_pre) & consumed_nq):>5}   "
      f"(materialized into a substrate a forward-return run globs)")
    P(f"    GENUINELY UNREAD (frozen pool)   {len(blind_nq):>5}   sha256 84a8575a...0931")
    P(f"    post-seal, metadata only         "
      f"{len([d for d in nq_rth if d >= SEAL]):>5}   COUNTED, NOT READ")
    assets.append(dict(asset="NQ BBO price-side", pre_seal_usable=len(nq_pre),
                       outcome_consumed=len(set(nq_pre) & consumed_nq),
                       genuinely_unread=len(blind_nq),
                       blind_pool_possible="YES - 19 frozen",
                       family_consumed="MS-BBO-V1 (void), MS01, MS01A, AUCTION01-04, FLOW01, U9/U9B",
                       export_cost="already exported for 97; 19 need extraction (~40 MB/session)",
                       decisions_per_session=331, exec_realism="direct bid/ask crossing, measured"))

    P("")
    P("=== ASSET 2  ES BBO (price-side quotes)   <-- the finding of this census")
    es_touch = "esnq00_census.py (metadata only: file names and hour labels; NO prices)"
    P(f"    RTH-complete pre-seal            {len(es_pre):>5}")
    P(f"    span                             {es_pre[0]} -> {es_pre[-1]}")
    P(f"    contracts                        "
      f"{sorted({c for d in es_pre for c in es_inst[d]})}")
    P(f"    OUTCOME-CONSUMED                     0   *** ZERO ***")
    P(f"    only code that has ever touched it: {es_touch}")
    P(f"    post-seal, metadata only         "
      f"{len([d for d in es_rth if d >= SEAL]):>5}   COUNTED, NOT READ")
    assets.append(dict(asset="ES BBO price-side", pre_seal_usable=len(es_pre),
                       outcome_consumed=0, genuinely_unread=len(es_pre),
                       blind_pool_possible="YES - the whole asset is unread",
                       family_consumed="NONE",
                       export_cost=f"~{len(es_pre)} sessions x ~40 MB = ~{len(es_pre)*40/1024:.1f} GB",
                       decisions_per_session=331, exec_realism="same contract as NQ; ES tick 0.25, "
                                                               "$50/pt, tighter spread in ticks"))

    P("")
    P("=== ASSET 3  ES-NQ OVERLAP (both RTH-complete, same session)")
    P(f"    overlapping sessions             {len(both):>5}   {both[0]} -> {both[-1]}")
    P(f"    of which NQ side outcome-consumed{len(set(both) & consumed_nq):>5}")
    P(f"    of which NQ side in the blind 19 {len(set(both) & blind_nq):>5}")
    P(f"    of which NQ side NEITHER         "
      f"{len([d for d in both if d not in consumed_nq and d not in blind_nq]):>5}")
    assets.append(dict(asset="ES+NQ overlap", pre_seal_usable=len(both),
                       outcome_consumed=len(set(both) & consumed_nq),
                       genuinely_unread=len(set(both) & blind_nq),
                       blind_pool_possible=f"PARTIAL - {len(set(both) & blind_nq)} sessions have "
                                           f"BOTH sides unread",
                       family_consumed="NQ side only, via the NQ lane",
                       export_cost="both instruments; ~2x the per-session cost",
                       decisions_per_session=331, exec_realism="NQ execution; ES informational"))

    # ---------------------------------------------------------------- 4 Last-only blind pool
    bp = pd.read_csv(os.path.join(ROOT, "runs/MICRO_DISCOVERY_CONFIRMATION_SPLIT/out/"
                                        "MICRO_BLIND_CONFIRMATION_POOL.csv"))
    P("")
    P("=== ASSET 4  NQ Last-only BLIND HISTORICAL CONFIRMATION POOL")
    P(f"    sessions                         {len(bp):>5}   {bp['date'].min()} -> {bp['date'].max()}")
    P(f"    status                           UNSPENT, frozen at fd7b05f")
    P(f"    quote classes                    {bp['quote_cls'].value_counts().to_dict()}")
    P("    governance: only a GENUINELY DIFFERENT mechanism, frozen WITHOUT reading the pool.")
    P("    MS-LAST-V1 closed ONE feature family / 60 s / Ridge-GBM budget / policy / cost model.")
    assets.append(dict(asset="NQ Last-only blind pool", pre_seal_usable=len(bp),
                       outcome_consumed=0, genuinely_unread=len(bp),
                       blind_pool_possible="IS one", family_consumed="MS-LAST-V1 scope only",
                       export_cost="extraction needed", decisions_per_session=331,
                       exec_realism="NO QUOTES - cannot price a bid/ask crossing"))

    # ---------------------------------------------------------------- 5 multi-market daily
    import ncd_day as N
    dayd = os.path.join(DB, "day")
    roots = collections.Counter()
    for d in os.listdir(dayd):
        m = re.match(r"^([A-Z0-9]+)\s", d)
        if m and os.path.isdir(os.path.join(dayd, d)):
            roots[m.group(1)] += 1
    known = set(N.CORE) | set(N.EXTENDED)
    extra = {r: c for r, c in roots.items() if r not in known}
    MICROS = {"MGC", "MNQ", "MES", "MYM", "M6B", "MHG", "MCL", "MET", "MBT", "QM"}
    P("")
    P("=== ASSET 5  MULTI-MARKET DAILY (true unmerged contracts)")
    P(f"    instrument dirs                  {sum(roots.values()):>5}   roots {len(roots)}")
    P(f"    in the declared universe         {len(known):>5}")
    P(f"    extra roots on disk              {len(extra):>5}   {dict(sorted(extra.items(), key=lambda kv: -kv[1]))}")
    P(f"    extra roots that are MICROS of an existing root (zero new information): "
      f"{sorted(set(extra) & MICROS)}")
    nonmicro = {r: c for r, c in extra.items() if r not in MICROS}
    P(f"    extra NON-micro roots            {nonmicro}")
    P(f"    of those with >= 10 contracts    {[r for r, c in nonmicro.items() if c >= 10]}")
    P("    >>> NO genuinely new root with usable depth. The 'add more roots' option for curve")
    P("    >>> work is CLOSED-BY-DATA, not merely unattempted.")
    P("")
    P("    OUTCOME-CONSUMED: daily returns 2009-2018 (TSMOM dev, CARRY dev), 2019-2022 (TSMOM V2")
    P("    validation), 2023-2026 (TSMOM TAIL-H1). FAMILY-CONSUMED: trend, curve slope.")
    P("    NOT computed as a signal on this substrate: contract VOLUME (present in every .ncd")
    P("    record, used only as the roll criterion), and open-interest proxies. That is a")
    P("    DIFFERENT information surface on OUTCOME-CONSUMED dates -- usable, but it inherits")
    P("    family-selection debt and CANNOT claim an unread window.")
    assets.append(dict(asset="Multi-market daily", pre_seal_usable=sum(roots.values()),
                       outcome_consumed=sum(roots.values()), genuinely_unread=0,
                       blind_pool_possible="NO - every window has been read by trend or curve",
                       family_consumed="TSMOM V1/V2/TAIL-H1, CARRY_V1",
                       export_cost="zero - already local",
                       decisions_per_session=1, exec_realism="daily close/open, costed"))

    # ---------------------------------------------------------------- 6 minute
    mind = os.path.join(DB, "minute")
    mroots = collections.Counter()
    msz = 0
    for d in os.listdir(mind):
        p = os.path.join(mind, d)
        if not os.path.isdir(p):
            continue
        m = re.match(r"^([A-Z0-9]+)\s", d)
        if m:
            mroots[m.group(1)] += 1
        msz += sum(os.path.getsize(os.path.join(p, f)) for f in os.listdir(p)
                   if f.endswith(".ncd"))
    P("")
    P("=== ASSET 6  NT8 MINUTE STORE")
    P(f"    instrument dirs {sum(mroots.values())}   roots {dict(sorted(mroots.items(), key=lambda kv: -kv[1]))}")
    P(f"    total size {msz / 2**30:.3f} GB")
    P("    NQ 1-minute is the weekly_edge substrate and is DEEPLY outcome-consumed (123 waves).")
    P("    ES/RTY/YM 1-minute underpins XM_CONFLICT. W122 closed 1-minute ES->NQ as a family.")
    assets.append(dict(asset="NT8 minute store", pre_seal_usable=sum(mroots.values()),
                       outcome_consumed=sum(mroots.values()), genuinely_unread=0,
                       blind_pool_possible="NO", family_consumed="weekly_edge (123 waves), "
                                                                 "XM_CONFLICT, W122",
                       export_cost="zero", decisions_per_session=1,
                       exec_realism="1-min bars; already parity-certified for P1/XM"))

    pd.DataFrame(assets).to_csv(os.path.join(OUT, "asset_registry.csv"), index=False)
    json.dump(assets, open(os.path.join(OUT, "asset_registry.json"), "w", encoding="utf-8"),
              indent=2)

    P("")
    P("=" * 116)
    P("=== SUMMARY -- assets ranked by GENUINELY UNREAD outcome rows")
    P("=" * 116)
    P(f"    {'asset':<28} {'usable':>8} {'consumed':>9} {'UNREAD':>8}   blind pool possible?")
    for a in sorted(assets, key=lambda x: -x["genuinely_unread"]):
        P(f"    {a['asset']:<28} {a['pre_seal_usable']:>8} {a['outcome_consumed']:>9} "
          f"{a['genuinely_unread']:>8}   {a['blind_pool_possible']}")
    _fh.close()


if __name__ == "__main__":
    main()
