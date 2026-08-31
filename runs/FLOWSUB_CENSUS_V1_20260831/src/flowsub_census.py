"""FLOWSUB_CENSUS_V1 -- machine census of the NT8 local TICK store (the "flow substrate").

RUN CLASS: DATA-ONLY CENSUS.  No price, no return, no outcome, no P&L.
Reads FILE NAMES and FILE SIZES only.  Not one byte of any .ncd payload is decoded, so
the >=2026-08-01 seal, the 19-session blind BBO pool and the 141-session Last-only pool
are all untouched by construction.

WHAT IS BEING CHECKED (frozen before the numbers were produced):

  CLAIM UNDER TEST (runs/GENESIS_W1_FORENSICS_20260828/reports/b1_nt8_store_census.md:65):
      NQ tick store = 319 Last dates | 196 BBO (Bid n Ask) dates | 123 Last-only dates
  versus research/weekly_edge/DATA_CENSUS_20260826.md:45-57 which credits order flow with
  "48 sessions".

  Those two numbers are NOT the same object and the census must keep them apart:
     * a CALENDAR DATE with a tick file          (what B1 counted, no payload filter)
     * a MATERIALIZED SESSION parquet on disk    (what DATA_CENSUS counted)
     * a RECONSTRUCTIBLE SESSION                 (what actually matters)

DEFINITIONS FROZEN BEFORE COMPUTATION
-------------------------------------
1. FILE GRAMMAR.  db/tick/<INSTRUMENT>/yyyyMMddHH00.<Last|Bid|Ask>.ncd  (hourly buckets).

2. HOUR LABEL -> EXCHANGE TIME.  label L on stem date C covers ET hour (L-1) of date C;
   L=0 covers ET 23:00-23:59 of C-1.  VERIFIED THIS RUN by decoding the 28-byte header
   `firstTicks` field of pre-seal, already-consumed files only (see verify_label_map()).

3. PAYLOAD.  A .ncd file carries a 28-byte header (int32 version | f64 tickSize |
   f64 firstPrice | i64 firstTicks).  size <= 32 => EMPTY RESIDUE, counted as ABSENT.
   Threshold supplied by the orchestrator (CAPPROBE01) and re-verified here from the
   size histogram.

4. SESSION s(D) = ET D-1 18:00 -> D 17:00, i.e. 23 hour-slots:
       labels 19..23 on stem date D-1     (ET 18:00-22:59)
       label  00     on stem date D       (ET 23:00-23:59 of D-1)
       labels 01..17 on stem date D       (ET 00:00-16:59)
   Label 18 (ET 17:00-17:59) is the CME maintenance break and is expected empty.

5. RTH window = ET 09:30-16:00 -> hour labels 10..16.

6. ERA BUCKETS (research/operational/LOCKED_FORWARD.md + CLAUDE.md s5):
       PRE_BURN  < 2026-05-31
       BURNED    2026-05-31 .. 2026-07-31
       SEALED   >= 2026-08-01   (VIRGIN; metadata only, never a "usable" total)
"""
from __future__ import annotations

import datetime
import json
import os
import re
from collections import defaultdict

import numpy as np
import pandas as pd

DB = os.path.join(os.path.expanduser("~"), "Documents", "NinjaTrader 8", "db", "tick")
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(HERE, "out")
os.makedirs(OUT, exist_ok=True)

NCD = re.compile(r"^(\d{8})(\d{2})00\.(Last|Bid|Ask)\.ncd$", re.I)
EMPTY_MAX = 32                      # <= this many bytes = header-only residue
BURN0, BURN1, SEAL = "2026-05-31", "2026-07-31", "2026-08-01"
EVENING = [19, 20, 21, 22, 23]
DAYLAB = [0] + list(range(1, 18))   # 00 plus 01..17  -> 18 labels; +5 evening = 23
RTH = list(range(10, 17))           # ET 09..15  == 09:30-16:00 coverage
NET_EPOCH = datetime.datetime(1, 1, 1)

P = print
LINES = []


def say(s=""):
    LINES.append(s)
    P(s)


def era(iso: str) -> str:
    if iso >= SEAL:
        return "SEALED"
    if iso >= BURN0:
        return "BURNED"
    return "PRE_BURN"


# --------------------------------------------------------------------------- scan
def scan():
    rows = []
    for inst in sorted(os.listdir(DB)):
        d = os.path.join(DB, inst)
        if not os.path.isdir(d):
            continue
        root = inst.split()[0]
        with os.scandir(d) as it:
            for e in it:
                m = NCD.match(e.name)
                if not m:
                    continue
                ymd, hh, series = m.group(1), int(m.group(2)), m.group(3).capitalize()
                sz = e.stat().st_size
                rows.append((root, inst, f"{ymd[:4]}-{ymd[4:6]}-{ymd[6:8]}", hh,
                             series, sz, sz > EMPTY_MAX))
    return pd.DataFrame(rows, columns=["root", "inst", "stem_date", "label",
                                       "series", "bytes", "payload"])


# ------------------------------------------------------- label->ET map verification
def verify_label_map(F: pd.DataFrame):
    """Decode ONLY the i64 firstTicks field (offset 20:28) of a handful of PRE-BURN,
    ALREADY-CONSUMED files.  No price, no volume, no bar is read."""
    say("=" * 100)
    say("=== STEP 0  VERIFY THE HOUR-LABEL -> ET MAP FROM FILE HEADERS (timestamp field only)")
    say("=" * 100)
    cand = F[(F.root == "NQ") & (F.payload) & (F.stem_date < BURN0)]
    cand = cand.sort_values(["stem_date", "label"])
    probe = cand.groupby("label", as_index=False).head(1).head(24)
    ok = bad = 0
    detail = []
    for _, r in probe.iterrows():
        ymd = r.stem_date.replace("-", "")
        p = os.path.join(DB, r.inst, f"{ymd}{r.label:02d}00.{r.series}.ncd")
        b = np.fromfile(p, dtype=np.uint8, count=28)
        if b.size < 28:
            continue
        ts = int(b[20:28].view("<i8")[0])
        dt = NET_EPOCH + datetime.timedelta(microseconds=ts // 10)
        exp = (pd.Timestamp(r.stem_date) + pd.Timedelta(hours=int(r.label) - 1))
        hit = abs((pd.Timestamp(dt) - exp).total_seconds()) < 3600
        ok += hit
        bad += (not hit)
        detail.append((r.stem_date, r.label, r.series, str(dt), str(exp), hit))
    say(f"    probed {ok + bad} pre-burn headers   agree with 'ET hour = label - 1'  {ok}"
        f"   disagree {bad}")
    for d in detail[:6]:
        say(f"      {d[0]} L{d[1]:02d} {d[2]:<4} firstTs {d[3]:<26} expected-hour {d[4]}"
            f"  {'OK' if d[5] else 'MISMATCH'}")
    say(f"    >>> LABEL MAP {'VERIFIED' if bad == 0 else 'FAILED'}")
    say("")
    return bad == 0


# --------------------------------------------------------------------------- health
def health(F: pd.DataFrame):
    say("=" * 100)
    say("=== STEP 1  FILE HEALTH AND THE EMPTY-RESIDUE THRESHOLD")
    say("=" * 100)
    say(f"    tick files found                {len(F):>8,}")
    say(f"    total bytes                     {F.bytes.sum():>8,}")
    q = F.bytes.quantile([0, .01, .05, .25, .5, .75, 1]).astype(int)
    say(f"    byte quantiles  min {q[0]:,}  p1 {q[.01]:,}  p5 {q[.05]:,}  "
        f"p25 {q[.25]:,}  med {q[.5]:,}  p75 {q[.75]:,}  max {q[1]:,}")
    small = F[F.bytes <= 200].bytes.value_counts().sort_index()
    say(f"    files <= 200 B                  {int((F.bytes <= 200).sum()):>8,}"
        f"   (sizes: {dict(small.head(12))})")
    say(f"    files <= {EMPTY_MAX} B  = EMPTY RESIDUE   {int((~F.payload).sum()):>8,}")
    br = F[~F.payload].label.value_counts().sort_index()
    say(f"    empty-residue by hour label     {dict(br)}")
    say(f"    zero-byte files                 {int((F.bytes == 0).sum()):>8,}")
    say("")


# --------------------------------------------------------------------------- census
def date_level(F: pd.DataFrame, root: str, payload_only: bool):
    G = F[(F.root == root)]
    if payload_only:
        G = G[G.payload]
    have = defaultdict(set)
    for s, grp in G.groupby("series"):
        for d in grp.stem_date.unique():
            have[s].add(d)
    last, bid, ask = have["Last"], have["Bid"], have["Ask"]
    bbo = bid & ask
    return last, bbo, (last - bbo)


def sessions(F: pd.DataFrame, root: str):
    """Per SESSION s(D): hour-label coverage for Last / Bid / Ask, payload-filtered."""
    G = F[(F.root == root) & (F.payload)]
    have = defaultdict(set)                                  # (date, series)->labels
    bytes_ = defaultdict(int)
    for r in G.itertuples():
        have[(r.stem_date, r.series)].add(r.label)
        bytes_[(r.stem_date, r.series)] += r.bytes
    alldates = sorted({d for d, _ in have})
    rows = []
    for iso in alldates:
        prev = str((pd.Timestamp(iso) - pd.Timedelta(days=1)).date())
        rec = {"session": "s" + iso.replace("-", ""), "date": iso, "era": era(iso)}
        for s in ("Last", "Bid", "Ask"):
            ev, dy = have.get((prev, s), set()), have.get((iso, s), set())
            got = len([h for h in EVENING if h in ev]) + len([h for h in DAYLAB if h in dy])
            rth = len([h for h in RTH if h in dy])
            rec[s.lower() + "_h"] = got
            rec[s.lower() + "_frac"] = round(got / 23, 3)
            rec[s.lower() + "_rth"] = rth
            rec[s.lower() + "_mb"] = round(
                (bytes_.get((prev, s), 0) + bytes_.get((iso, s), 0)) / 1e6, 2)
        rec["quote_frac"] = min(rec["bid_frac"], rec["ask_frac"])
        rec["quote_rth"] = min(rec["bid_rth"], rec["ask_rth"])
        rec["trade_bearing"] = rec["last_h"] > 0
        rec["last_usable"] = rec["last_frac"] >= 0.90
        rec["bbo_any"] = rec["quote_frac"] > 0
        rec["bbo_rth_complete"] = rec["quote_rth"] == len(RTH)
        rec["bbo_full"] = rec["quote_frac"] >= 0.90
        rows.append(rec)
    return pd.DataFrame(rows)


def main():
    F = scan()
    F.to_csv(os.path.join(OUT, "tick_file_inventory.csv"), index=False)
    verify_label_map(F)
    health(F)

    say("=" * 100)
    say("=== STEP 2  REPRODUCE B1's CALENDAR-DATE COUNT, THEN APPLY THE PAYLOAD FILTER")
    say("=" * 100)
    say(f"    {'root':<5} {'filter':<14} {'Last dates':>10} {'BBO dates':>10} "
        f"{'Last-only':>10}")
    b1 = {}
    for root in ("NQ", "MNQ", "ES"):
        for po, tag in ((False, "names only"), (True, "payload > 32B")):
            L, B, LO = date_level(F, root, po)
            say(f"    {root:<5} {tag:<14} {len(L):>10} {len(B):>10} {len(LO):>10}")
            if root == "NQ":
                b1[tag] = (len(L), len(B), len(LO))
    say("")
    say(f"    B1 RECORDED CLAIM for NQ:  319 Last / 196 BBO / 123 Last-only")
    say(f"    reproduced (names only) :  {b1['names only'][0]} / {b1['names only'][1]}"
        f" / {b1['names only'][2]}")
    say(f"    with payload filter     :  {b1['payload > 32B'][0]} / "
        f"{b1['payload > 32B'][1]} / {b1['payload > 32B'][2]}")
    say("")

    say("=" * 100)
    say("=== STEP 3  THE OBJECT THAT MATTERS: SESSIONS, NOT CALENDAR DATES")
    say("=" * 100)
    allS = {}
    for root in ("NQ", "MNQ", "ES"):
        S = sessions(F, root)
        S.to_csv(os.path.join(OUT, f"sessions_{root}.csv"), index=False)
        allS[root] = S
        T = S[S.trade_bearing]
        say(f"  --- {root} ---   trade-bearing sessions {len(T)}"
            f"   span {T.date.min()} .. {T.date.max()}")
        for e in ("PRE_BURN", "BURNED", "SEALED"):
            E = T[T.era == e]
            if not len(E):
                continue
            say(f"      {e:<9} n={len(E):>4}"
                f"   last_usable(>=0.90) {int(E.last_usable.sum()):>4}"
                f"   bbo_any {int(E.bbo_any.sum()):>4}"
                f"   bbo_RTH_complete {int(E.bbo_rth_complete.sum()):>4}"
                f"   bbo_full(>=0.90) {int(E.bbo_full.sum()):>4}"
                f"   Last-only {int((~E.bbo_any).sum()):>4}")
        say("")

    # ------------------------------------------------ materialization cross-check
    say("=" * 100)
    say("=== STEP 4  WHAT IS ALREADY MATERIALIZED AS PARQUET (the DATA_CENSUS '48')")
    say("=" * 100)
    repo = os.path.dirname(os.path.dirname(HERE))
    mats = {
        "scalping_lab raw/NQ": os.path.join(repo, "research", "scalping_lab", "substrate",
                                            "raw", "NQ"),
        "scalping_lab grid1s/NQ": os.path.join(repo, "research", "scalping_lab", "substrate",
                                               "grid1s", "NQ"),
        "v2 raw/NQ": os.path.join(repo, "research", "data_microstructure_v2", "raw", "NQ"),
        "scalping_lab raw/ES": os.path.join(repo, "research", "scalping_lab", "substrate",
                                            "raw", "ES"),
    }
    sets = {}
    for k, p in mats.items():
        if not os.path.isdir(p):
            say(f"    {k:<26} MISSING")
            continue
        ss = {f[:9] for f in os.listdir(p) if f.startswith("s") and f.endswith(".parquet")}
        sets[k] = ss
        mb = sum(os.path.getsize(os.path.join(p, f)) for f in os.listdir(p)) / 1e6
        say(f"    {k:<26} {len(ss):>4} sessions  {mb:>9.1f} MB")
    nq_mat = sets.get("scalping_lab raw/NQ", set()) | sets.get("v2 raw/NQ", set())
    say(f"    NQ materialized in EITHER substrate            {len(nq_mat)}")
    S = allS["NQ"]
    T = S[S.trade_bearing]
    reach = set(T.session)
    say(f"    NQ trade-bearing sessions reachable from db/tick   {len(reach)}")
    say(f"    materialized but NOT reachable (orphan)            "
        f"{len(nq_mat - reach)}  {sorted(nq_mat - reach)[:8]}")
    say(f"    reachable but NOT materialized                     {len(reach - nq_mat)}")
    pre = set(T[T.era == 'PRE_BURN'].session)
    say(f"      of which PRE_BURN                                {len(pre - nq_mat)}")
    say(f"      of which PRE_BURN and bbo_RTH_complete           "
        f"{len(set(T[(T.era=='PRE_BURN') & T.bbo_rth_complete].session) - nq_mat)}")
    say(f"      of which PRE_BURN and Last-only, last>=0.90      "
        f"{len(set(T[(T.era=='PRE_BURN') & (~T.bbo_any) & T.last_usable].session) - nq_mat)}")
    say("")

    with open(os.path.join(OUT, "census.txt"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(LINES) + "\n")
    summary = {r: {"sessions": int(allS[r].trade_bearing.sum())} for r in allS}
    with open(os.path.join(OUT, "summary.json"), "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=1)


if __name__ == "__main__":
    main()
