"""BBO_COMPLETENESS_RECENSUS_V1 -- reconcile 99 vs 123.  DATA-ONLY.  Frozen by SPEC.md.

NO PRICES READ. NO OUTCOMES READ. NO MODEL. Only file names, hour labels and substrate membership.

The forbidden move, stated so the code can be checked against it: subtracting 99 from 116 and
calling the remainder a blind pool. The two counts use DIFFERENT DEFINITIONS -- OLD is full-session
(23 hour labels, 18:00 D-1 -> 17:00 D ET), NEW is an RTH window (8 labels on D). This script applies
BOTH to one enumerated universe and reports where and WHY they disagree.

SOURCE-PROVENANCE GATE: 'consumed' requires naming the chain
    session -> materialized into substrate S -> consumer run globs S -> computes forward returns
File enumeration does not consume. Timestamp-only capability inspection does not consume.
"""
from __future__ import annotations

import hashlib
import os
import re
import subprocess
import sys
from collections import defaultdict

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(RUN))
sys.path.insert(0, os.path.join(ROOT, "research_sdk"))

OUT = os.path.join(RUN, "out")
os.makedirs(OUT, exist_ok=True)
DB = os.path.join(os.path.expanduser("~"), "Documents", "NinjaTrader 8", "db", "tick")
SEAL = "2026-08-01"
NCD = re.compile(r"^(\d{8})(\d{2})\d{2}\.(Last|Bid|Ask)\.ncd$", re.I)

# ---- OLD criterion, transcribed from ORDERFLOW_EXPAND/src/bbo_hourly_truth.py ----------------
EVENING = [19, 20, 21, 22, 23]          # on D-1
DAY = [0] + list(range(1, 18))          # label 00 on D plus 01..17 on D
OLD_NEED = len(EVENING) + len(DAY)      # 23
# ---- NEW criterion ---------------------------------------------------------------------------
RTH_AS_RUN = set(range(9, 17))          # esnq00_census.py, as executed
RTH_CORRECTED = set(range(10, 17))      # label = ET hour + 1; RTH 10:00-15:30 + warmup + exit
# ---- provenance ------------------------------------------------------------------------------
SUB_OLD = os.path.join(ROOT, "research/scalping_lab/substrate/raw/NQ")
SUB_V2 = os.path.join(ROOT, "research/data_microstructure_v2/raw/NQ")
CONSUMERS_OLD = "AUCTION01-04 / ACTIONMAP01 / FLOW01 / U9 / U9B (forward returns on OLD substrate)"
CONSUMERS_V2 = "MS01 / MS01A / MSBBO_V1 / MSBBO_DEPLOYMENT_FREEZE (forward returns on v2)"
_fh = None


def P(*a):
    print(*a, flush=True)
    if _fh is not None:
        print(*a, file=_fh)


def scan_tick_store():
    """(iso date, series) -> set of hour labels, for every NQ contract dir. Metadata only."""
    have = defaultdict(set)
    contracts = defaultdict(set)
    for inst in sorted(os.listdir(DB)):
        if not inst.startswith("NQ "):
            continue
        d = os.path.join(DB, inst)
        if not os.path.isdir(d):
            continue
        with os.scandir(d) as it:
            for e in it:
                m = NCD.match(e.name)
                if not m:
                    continue
                ymd, hh, series = m.group(1), int(m.group(2)), m.group(3).capitalize()
                iso = f"{ymd[:4]}-{ymd[4:6]}-{ymd[6:8]}"
                have[(iso, series)].add(hh)
                contracts[iso].add(inst)
    return have, contracts


def materialized(path, pat=r"^s(\d{8})\.parquet$"):
    out = set()
    if os.path.isdir(path):
        for f in os.listdir(path):
            m = re.match(pat, f)
            if m:
                g = m.group(1)
                out.add(f"{g[:4]}-{g[4:6]}-{g[6:]}")
    return out


def main():
    global _fh
    _fh = open(os.path.join(OUT, "recensus.txt"), "w", encoding="utf-8")
    P("=" * 116)
    P("=== BBO_COMPLETENESS_RECENSUS_V1 -- 99 vs 123.  DATA-ONLY: no price, no outcome, no model.")
    P("=" * 116)

    have, contracts = scan_tick_store()
    old_sub, v2_sub = materialized(SUB_OLD), materialized(SUB_V2)
    P(f"    OLD substrate  {SUB_OLD.split('systematic_research')[-1]}   {len(old_sub)} sessions")
    P(f"    v2  substrate  {SUB_V2.split('systematic_research')[-1]}   {len(v2_sub)} sessions")

    dates = sorted({d for d, _ in have})
    rows = []
    for iso in dates:
        prev = str((pd.Timestamp(iso) - pd.Timedelta(days=1)).date())
        rec = {"session_date": iso, "contract": ",".join(sorted(contracts[iso])),
               "file_presence": True, "sealed": iso >= SEAL}
        # ---- OLD: 23 required session-hour labels per side
        fr = {}
        for series in ("Last", "Bid", "Ask"):
            ev, dy = have.get((prev, series), set()), have.get((iso, series), set())
            got = len([h for h in EVENING if h in ev]) + len([h for h in DAY if h in dy])
            fr[series] = round(got / OLD_NEED, 3)
        rec["bid_coverage"] = fr["Bid"]
        rec["ask_coverage"] = fr["Ask"]
        rec["last_coverage"] = fr["Last"]
        qf = min(fr["Bid"], fr["Ask"])
        rec["old_quote_frac"] = qf
        rec["old_quote_class"] = "NONE" if qf <= 0.05 else ("PARTIAL" if qf <= 0.90 else "FULL")
        # ---- NEW: RTH labels on D only, both windows
        lab = {s: have.get((iso, s), set()) for s in ("Last", "Bid", "Ask")}
        rec["new_rth_complete_9_16"] = all(RTH_AS_RUN <= lab[s] for s in lab)
        rec["new_rth_complete_10_16"] = all(RTH_CORRECTED <= lab[s] for s in lab)
        rec["rth_span_labels"] = len(RTH_CORRECTED & lab["Bid"] & lab["Ask"] & lab["Last"])
        # ---- provenance
        rec["previously_exported_v2"] = iso in v2_sub
        rec["previously_exported_old"] = iso in old_sub
        if rec["previously_exported_v2"] and rec["previously_exported_old"]:
            run, prov = "BOTH", f"{CONSUMERS_V2}; {CONSUMERS_OLD}"
        elif rec["previously_exported_v2"]:
            run, prov = "v2 consumers", CONSUMERS_V2
        elif rec["previously_exported_old"]:
            run, prov = "OLD consumers", CONSUMERS_OLD
        else:
            run, prov = "", "NOT MATERIALIZED -- no run has read this session's prices"
        rec["outcome_consumed_by_run"] = run
        rec["consumption_provenance"] = prov
        consumed = bool(run)
        rec["outcome_consumed"] = consumed
        # ---- blind eligibility under each rule
        rec["eligible_blind_old_rule"] = bool(
            (not rec["sealed"]) and rec["old_quote_class"] == "FULL" and not consumed)
        rec["eligible_blind_new_rule"] = bool(
            (not rec["sealed"]) and rec["new_rth_complete_10_16"] and not consumed)
        # ---- why the two criteria disagree
        o, n = rec["old_quote_class"] == "FULL", rec["new_rth_complete_10_16"]
        if o == n:
            why = ""
        elif n and not o:
            why = (f"RTH labels 10-16 complete but full-session coverage only "
                   f"{qf:.3f} -- overnight/evening leg missing")
        else:
            why = "full-session FULL but an RTH label is absent (unexpected; inspect)"
        rec["reason_for_disagreement"] = why
        rows.append(rec)

    D = pd.DataFrame(rows).sort_values("session_date").reset_index(drop=True)
    pre = D[~D["sealed"]].copy()
    D.to_csv(os.path.join(OUT, "bbo_crosswalk.csv"), index=False)

    # ---------------------------------------------------------------- reproduce the OLD number
    P("")
    P("=" * 116)
    P("=== STEP 1  REPRODUCE THE OLD CLASSIFIER  (source-provenance gate: reproduce before compare)")
    P("=" * 116)
    ref = pd.read_csv(os.path.join(ROOT,
                      "runs/ORDERFLOW_EXPAND_20260827/out/bbo_hourly_truth.csv"))
    mine = pre[["session_date", "old_quote_class"]].rename(columns={"session_date": "date"})
    j = ref[["date", "cls"]].merge(mine, on="date", how="outer", indicator=True)
    agree = int((j["cls"] == j["old_quote_class"]).sum())
    P(f"    stored bbo_hourly_truth.csv rows {len(ref)}   recomputed pre-seal rows {len(pre)}")
    P(f"    class agreement on common dates: {agree} / {int((j['_merge'] == 'both').sum())}")
    for c in ("FULL", "PARTIAL", "NONE"):
        P(f"      {c:<8} stored {int((ref['cls'] == c).sum()):>4}   "
          f"recomputed {int((pre['old_quote_class'] == c).sum()):>4}")
    ok_repro = agree == int((j["_merge"] == "both").sum()) and len(ref) == len(pre)
    P(f"    >>> {'REPRODUCED EXACTLY' if ok_repro else '*** DOES NOT REPRODUCE - stop ***'}")

    # ---------------------------------------------------------------- the crosswalk
    P("")
    P("=" * 116)
    P("=== STEP 2  THE CROSSWALK  (pre-seal universe only)")
    P("=" * 116)
    P(f"    pre-seal dates with any NQ tick file           {len(pre):>5}")
    P(f"    OLD quote-FULL (23 session-hour labels)        {int((pre['old_quote_class']=='FULL').sum()):>5}")
    P(f"    NEW RTH-complete, labels 9-16 (as run)         {int(pre['new_rth_complete_9_16'].sum()):>5}")
    P(f"    NEW RTH-complete, labels 10-16 (corrected)     {int(pre['new_rth_complete_10_16'].sum()):>5}")
    P(f"    materialized in v2                             {int(pre['previously_exported_v2'].sum()):>5}")
    P(f"    materialized in OLD substrate                  {int(pre['previously_exported_old'].sum()):>5}")
    P(f"    materialized in EITHER  = OUTCOME-CONSUMED     {int(pre['outcome_consumed'].sum()):>5}")
    P("")
    ct = pd.crosstab(pre["old_quote_class"], pre["new_rth_complete_10_16"])
    P("    OLD class  x  NEW RTH-complete(10-16)")
    P("      " + ct.to_string().replace("\n", "\n      "))

    P("")
    P("=== STEP 3  THE SIX STATES, KEPT SEPARATE")
    for lbl, m in (("file exists", pd.Series(True, index=pre.index)),
                   ("RTH-complete (new, 10-16)", pre["new_rth_complete_10_16"]),
                   ("quote-FULL (old, 23h)", pre["old_quote_class"] == "FULL"),
                   ("materialized", pre["outcome_consumed"]),
                   ("RTH-complete AND materialized", pre["new_rth_complete_10_16"] & pre["outcome_consumed"]),
                   ("RTH-complete AND NOT materialized", pre["new_rth_complete_10_16"] & ~pre["outcome_consumed"]),
                   ("quote-FULL AND NOT materialized", (pre["old_quote_class"] == "FULL") & ~pre["outcome_consumed"])):
        P(f"    {lbl:<38} {int(m.sum()):>5}")

    # ---------------------------------------------------------------- verdict
    blind_old = pre[pre["eligible_blind_old_rule"]]
    blind_new = pre[pre["eligible_blind_new_rule"]]
    P("")
    P("=" * 116)
    P("=== STEP 4  VERDICT")
    P("=" * 116)
    P(f"    genuinely unread AND quote-FULL under the OLD rule   {len(blind_old):>5}")
    P(f"    genuinely unread AND RTH-complete under the NEW rule {len(blind_new):>5}")
    if len(blind_new):
        P(f"    span {blind_new['session_date'].min()} -> {blind_new['session_date'].max()}")
        P(f"    contracts {sorted({c for s in blind_new['contract'] for c in s.split(',')})}")

    verdict = "A" if len(blind_new) == 0 else "B"
    P("")
    if verdict == "A":
        P("    >>> VERDICT A: NO historical blind BBO pool exists.")
        P("    >>> The 99-vs-123 gap is entirely a DEFINITION difference plus post-split caching.")
    else:
        P(f"    >>> VERDICT B: a genuine pre-seal blind BBO pool exists -- {len(blind_new)} sessions.")
        P("    >>> FREEZING AND HASHING NOW. Its returns are NOT inspected and it is NOT spent.")
        cols = ["session_date", "contract", "old_quote_class", "old_quote_frac",
                "new_rth_complete_9_16", "new_rth_complete_10_16",
                "bid_coverage", "ask_coverage", "last_coverage"]
        p = os.path.join(OUT, "BBO_BLIND_POOL_MANIFEST.csv")
        blind_new[cols].to_csv(p, index=False)
        h = hashlib.sha256(open(p, "rb").read()).hexdigest()
        head = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT,
                              capture_output=True, text=True).stdout.strip()
        P(f"    >>> manifest sha256 {h}")
        P(f"    >>> frozen at commit {head}")
        with open(os.path.join(OUT, "BBO_BLIND_POOL_MANIFEST.sha256"), "w",
                  encoding="utf-8") as fh:
            fh.write(f"{h}  BBO_BLIND_POOL_MANIFEST.csv\n")

    # sealed inventory, METADATA ONLY
    sealed = D[D["sealed"]]
    P("")
    P(f"    sealed (>= {SEAL}) dates inventoried by metadata only: {len(sealed)}  "
      f"-- no price or outcome read; all blind-eligibility flags False by construction")
    P(f"    sealed dates that would be RTH-complete: "
      f"{int(sealed['new_rth_complete_10_16'].sum())}  (counted, NOT read)")
    _fh.close()
    return verdict


if __name__ == "__main__":
    main()
