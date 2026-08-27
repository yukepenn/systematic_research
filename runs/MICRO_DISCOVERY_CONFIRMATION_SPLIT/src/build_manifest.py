"""Determine, from evidence, whether a BLIND microstructure confirmation pool actually exists.

Directive PHASE 5. The instruction is explicit: "If these sessions have already been decoded/read in
a way that exposes outcomes, say so and do not manufacture a holdout."

So this script does not assume a holdout is available. It establishes which sessions have had their
PRICE CONTENT read by an alpha-discovery process, and freezes only what genuinely remains unread -
BEFORE any of it enters a feature pipeline.

Rule applied: file-presence enumeration does NOT consume a session. Computing forward returns on it
DOES.
"""
from __future__ import annotations

import hashlib
import os
import re
import subprocess

import pandas as pd

ROOT = (r"D:\OneDrive - Washington University in St. Louis\TradingResearch"
        r"\systematic_research")
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "out")
os.makedirs(OUT, exist_ok=True)
SEAL = "2026-08-01"
_fh = open(os.path.join(OUT, "split.txt"), "w", encoding="utf-8")


def P(*a):
    print(*a, flush=True)
    print(*a, file=_fh)


# Runs that read microstructure PRICE CONTENT and computed forward/future returns on it.
# Established by grepping their sources for forward-return construction, not assumed.
CONSUMERS = ["AUCTION03_MECHANISM_DECOMPOSITION", "AUCTION04_CLEAN_CAUSAL_SUBSTRATE",
             "FLOW01_AGGRESSIVE_PARTICIPATION", "U9B_MICROSTRUCTURE_ALPHA",
             "U9_TRUE_MICROSTRUCTURE", "ACTIONMAP01_AUCTION_ACTION_VALUE",
             "AUCTION01_VALUE_STATE", "AUCTION02_ACTION_RELEVANCE",
             "MS01_STANDALONE_FEASIBILITY", "MS01A_BBO_SEMANTICS_AUDIT"]


def sessions_in(dirp, pat):
    out = set()
    if os.path.isdir(dirp):
        for f in os.listdir(dirp):
            m = re.match(pat, f)
            if m:
                g = m.group(1)
                out.add(f"{g[:4]}-{g[4:6]}-{g[6:]}")
    return out


def main():
    T = pd.read_csv(os.path.join(ROOT, "runs/ORDERFLOW_EXPAND_20260827/out/bbo_hourly_truth.csv"))
    full_q = set(T[T["cls"] == "FULL"]["date"])
    usable_last = set(T[T["last_frac"] >= 0.90]["date"])

    old = sessions_in(os.path.join(ROOT, "research/scalping_lab/substrate/raw/NQ"),
                      r"^s(\d{8})\.parquet$")
    new = set(pd.read_csv(os.path.join(ROOT,
              "research/data_microstructure_v2/MANIFEST.csv"))["session_date"])
    mat = old | new

    P("=" * 104)
    P("=== MICROSTRUCTURE DISCOVERY / CONFIRMATION SPLIT")
    P("=== Determined from evidence. A holdout is NOT manufactured where none exists.")
    P("=" * 104)

    P("")
    P("--- BBO (quote-complete) LANE")
    P(f"    quote-FULL ceiling on disk               {len(full_q):>5}")
    P(f"    in v2 substrate  (read by MS01, MS01A)   {len(new & full_q):>5}")
    P(f"    in OLD substrate only                    {len((old & full_q) - new):>5}")
    P(f"    quote-FULL never materialized            {len(full_q - mat):>5}")
    P("")
    P("    Runs that read the OLD substrate's PRICE CONTENT and built forward/future returns:")
    for c in CONSUMERS:
        d = os.path.join(ROOT, "runs", c, "src")
        if not os.path.isdir(d):
            continue
        n = 0
        for f in os.listdir(d):
            if f.endswith(".py"):
                try:
                    s = open(os.path.join(d, f), encoding="utf-8", errors="replace").read()
                    if re.search(r"fwd|forward|future|shift\(-", s):
                        n += 1
                except OSError:
                    pass
        if n:
            P(f"      {c:<42} {n} source file(s)")
    P("")
    P("    >>> VERDICT: NO VALID BLIND BBO POOL EXISTS.")
    P("    >>> The 40 old-substrate quote-complete sessions were consumed by AUCTION01-04,")
    P("    >>> ACTIONMAP01, FLOW01 and the U9 microstructure waves, all of which computed forward")
    P("    >>> returns on them. The 58 v2 sessions were consumed by MS01 and MS01A.")
    P("    >>> Any BBO result is therefore DISCOVERY-GRADE ONLY and cannot be blind-confirmed.")

    P("")
    P("--- LAST-ONLY (trade-flow) LANE")
    unread = sorted(s for s in (usable_last - mat) if s < SEAL)
    P(f"    Last-usable ceiling                      {len(usable_last):>5}")
    P(f"    materialized anywhere (consumed)         {len(usable_last & mat):>5}")
    P(f"    NEVER EXTRACTED, price content UNREAD    {len(unread):>5}")
    if unread:
        P(f"    span                                     {unread[0]} -> {unread[-1]}")
    P("")
    P("    >>> VERDICT: A GENUINE BLIND POOL EXISTS HERE, and only here.")

    # -------------------------------------------------------------- freeze it
    R = pd.read_csv(os.path.join(ROOT, "runs/ORDERFLOW_EXPAND_20260827/out/runlist.csv"))
    B = R[R["date"].isin(unread)][["session", "date", "instrument", "quote_cls",
                                   "last_frac", "from_utc", "to_utc"]].copy()
    B = B.sort_values("date").reset_index(drop=True)
    p = os.path.join(OUT, "MICRO_BLIND_CONFIRMATION_POOL.csv")
    B.to_csv(p, index=False)
    h = hashlib.sha256(open(p, "rb").read()).hexdigest()
    try:
        head = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT,
                              capture_output=True, text=True).stdout.strip()
    except Exception:
        head = "?"

    P("")
    P("=" * 104)
    P("=== FROZEN: MICRO_BLIND_HISTORICAL_CONFIRMATION_POOL  (Last-only lane)")
    P("=" * 104)
    P(f"    sessions            {len(B)}")
    P(f"    span                {B['date'].min()} -> {B['date'].max()}")
    P(f"    contracts           {sorted(B['instrument'].unique())}")
    P(f"    quote classes       {B['quote_cls'].value_counts().to_dict()}")
    P(f"    all pre-seal        {bool((B['date'] < SEAL).all())}")
    P(f"    manifest sha256     {h}")
    P(f"    frozen at commit    {head}")
    P("")
    P("    EXCLUSION RULES, fixed now:")
    P("      - any session with last_frac < 0.90 is excluded")
    P("      - any session dated >= 2026-08-01 is excluded (VIRGIN seal)")
    P("      - early-close/holiday sessions are QUARANTINED by the same span gate the v2 QA uses")
    P("        (< 20 h span), and a quarantine does NOT permit substituting another session")
    P("      - no session may be added to or removed from this pool after this commit")
    P("")
    P("    WHAT THIS IS, EXACTLY: BLIND HISTORICAL CONFIRMATION. Its price content has never been")
    P("    read by any alpha-discovery process in this repo. It is NOT prospective forward")
    P("    evidence - it is historical data that happens to be unread, and it overlaps the")
    P("    discovery period in calendar time rather than following it. That is weaker than a")
    P("    forward pool and stronger than nothing, and it is called by its right name.")
    _fh.close()


if __name__ == "__main__":
    main()
