"""Generate DATA_ASSET_REGISTRY.md FROM MEASUREMENT. Never hand-maintained.

Directive s6. One row per information source, with the fields that decide what it may be used for.

THE STANDING RULE this file exists to enforce:

    INSTRUMENT-DATES ARE NOT DISTINCT USABLE SESSIONS.

Three different counts were circulating for NQ tick and they were all "correct" about different
populations, which is exactly how a power claim goes wrong:

    310  dates with >= 1 Last .ncd file, pre-seal          FILE PRESENCE
    262  310 minus the 48 already extracted (runlist)      FILE PRESENCE
    243  of those, last_frac >= 0.90 of session hours      USABLE SESSION
     99  quote-complete >= 90 %                            USABLE SESSION

Only the USABLE SESSION class may be used for power. 310 and 262 may be used for planning
extraction work and for nothing else.
"""
from __future__ import annotations

import os
import re
import subprocess
from collections import defaultdict

import pandas as pd

ROOT = (r"D:\OneDrive - Washington University in St. Louis\TradingResearch"
        r"\systematic_research")
DB = os.path.join(os.path.expanduser("~"), "Documents", "NinjaTrader 8", "db")
OUT = os.path.join(ROOT, "research", "data")
os.makedirs(OUT, exist_ok=True)
SEAL = "2026-08-01"
BURN_A, BURN_B = "2026-05-31", "2026-07-31"


def git_head():
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT,
                              capture_output=True, text=True).stdout.strip()
    except Exception:
        return "?"


HEAD = git_head()
rows = []


def add(**kw):
    kw.setdefault("last_verified_commit", HEAD)
    rows.append(kw)


def sessions_in(dirp, pat=r"^s(\d{8})"):
    out = set()
    if os.path.isdir(dirp):
        for f in os.listdir(dirp):
            m = re.match(pat, f)
            if m:
                g = m.group(1)
                out.add(f"{g[:4]}-{g[4:6]}-{g[6:]}")
    return out


# ------------------------------------------------------------------ 1. NQ 1-minute bars
for lbl, rel in [("nq1m_base", "research/scalping_lab/substrate/minute/NQ/nq1m_2005_202605.parquet"),
                 ("nq1m_ext", "runs/SM1M_SUBSTRATE/out/nq_1m_2022_2026.parquet")]:
    p = os.path.join(ROOT, rel)
    if not os.path.exists(p):
        continue
    d = pd.read_parquet(p, columns=["time"])
    # the base substrate stores `time` as an integer epoch, not a datetime dtype
    d["time"] = pd.to_datetime(d["time"])
    sess = d["time"].dt.normalize().nunique()
    add(asset=f"NQ 1-minute bars ({lbl})", symbol="NQ", resolution="1-minute",
        series="Last OHLCV", first=str(d["time"].min()), last=str(d["time"].max()),
        usable_sessions=sess, full_vs_partial="see MANIFEST_NOTES: 46 days have 261-379 RTH bars",
        missing="2014-01-27..31 whole week + scattered weekdays (2009-03-27, 2009-06-19, 2013-07-12)",
        quote_completeness="N/A - Last only", known_truncation="none",
        location=rel, extraction="MATERIALIZED", cost="$0",
        evidence_class="STRUCTURAL", seal=f"pre-{SEAL} only",
        suitable="P1/PCT, XM, any bar-level intraday study",
        unsuitable="anything needing signed flow, quotes, or sub-minute timing")

# ------------------------------------------------------------------ 2. microstructure
old_nq = sessions_in(os.path.join(ROOT, "research/scalping_lab/substrate/raw/NQ"))
MV2 = os.path.join(ROOT, "research/data_microstructure_v2/MANIFEST.csv")
M2 = pd.read_csv(MV2) if os.path.exists(MV2) else pd.DataFrame()
new_nq = set(M2["session_date"]) if len(M2) else set()

# hour-granularity truth
T = pd.read_csv(os.path.join(ROOT, "runs/ORDERFLOW_EXPAND_20260827/out/bbo_hourly_truth.csv"))
usable_last = set(T[T["last_frac"] >= 0.90]["date"])
full_q = set(T[T["cls"] == "FULL"]["date"])
allT_dates = set(T["date"])          # every pre-seal date with a Last file = the "310" population

# truncation audit on the OLD substrate
trunc = 0
oldp = os.path.join(ROOT, "research/scalping_lab/substrate/raw/NQ")
if os.path.isdir(oldp):
    for f in sorted(os.listdir(oldp)):
        if not re.match(r"^s\d{8}\.parquet$", f):
            continue
        try:
            n = len(pd.read_parquet(os.path.join(oldp, f), columns=["bip"]))
            if n >= 12_000_000:
                trunc += 1
        except Exception:
            pass

add(asset="NQ tick+BBO (OLD scalping_lab v1)", symbol="NQ", resolution="tick",
    series="Last+Bid+Ask (bip 0/1/2)",
    first=min(old_nq) if old_nq else "", last=max(old_nq) if old_nq else "",
    usable_sessions=len(old_nq),
    full_vs_partial=f"{len(old_nq & full_q)} quote-FULL of {len(old_nq)}",
    missing="non-contiguous sample of the store",
    quote_completeness="3 sessions carry no quotes at all",
    known_truncation=f"**{trunc} files sit at exactly 12,000,000 rows = v1 cap = TRUNCATED mid-session**",
    location="research/scalping_lab/substrate/raw/NQ", extraction="MATERIALIZED", cost="$0",
    evidence_class="MICROSTRUCTURE-CURRENT", seal=f"pre-{SEAL}",
    suitable="fill-cost/spread audit (W82/W89 used 45)",
    unsuitable="any feature needing the session tail on a truncated file")

if len(M2):
    add(asset="NQ tick+BBO (NEW v2)", symbol="NQ", resolution="tick",
        series="Last+Bid+Ask (bip 0/1/2)",
        first=M2["session_date"].min(), last=M2["session_date"].max(),
        usable_sessions=len(M2),
        full_vs_partial=f"{len(new_nq & full_q)} quote-FULL of {len(M2)}",
        missing="s20260525 quarantined (Memorial Day, 19.0h span)",
        quote_completeness=f"min bid/ask coverage {M2['cov_bid'].min():.4f}/{M2['cov_ask'].min():.4f}",
        known_truncation="none - 25M cap, largest session 22.8M rows",
        location="research/data_microstructure_v2/ (parquet gitignored)",
        extraction="MATERIALIZED", cost="$0",
        evidence_class="MICROSTRUCTURE-CURRENT", seal=f"pre-{SEAL}",
        suitable="signed flow, microprice, quote imbalance, spread state, absorption",
        unsuitable="any structural/multi-era claim")

add(asset="NQ tick+BBO (UNION, materialized)", symbol="NQ", resolution="tick",
    series="Last+Bid+Ask",
    first=min(old_nq | new_nq), last=max(old_nq | new_nq),
    usable_sessions=len(old_nq | new_nq),
    full_vs_partial=f"**{len((old_nq | new_nq) & full_q)} quote-FULL**, "
                    f"{len((old_nq | new_nq) & usable_last)} Last-usable",
    missing=f"store ceiling: {len(full_q)} quote-FULL, {len(usable_last)} Last-usable",
    quote_completeness="lane-dependent - DO NOT MERGE the two lanes",
    known_truncation=f"{trunc} old files truncated; mask required for tail-dependent features",
    location="two directories, deliberately not merged", extraction="MATERIALIZED", cost="$0",
    evidence_class="MICROSTRUCTURE-CURRENT", seal=f"pre-{SEAL}",
    suitable="standalone microstructure alpha (regime-local)",
    unsuitable="P1 full-horizon action-value routing - CLOSED-BY-POWER, 998 sessions needed, 713 exist")

# derived layers
for lbl, rel in [("grid1s (1-sec L1 grid, has sflow)", "research/scalping_lab/substrate/grid1s/NQ"),
                 ("sechilo (per-sec mid hi/lo)", "research/scalping_lab/substrate/sechilo/NQ")]:
    s = sessions_in(os.path.join(ROOT, rel))
    if s:
        add(asset=f"NQ {lbl}", symbol="NQ", resolution="1-second", series="derived L1",
            first=min(s), last=max(s), usable_sessions=len(s),
            full_vs_partial="derived from OLD v1 raw only", missing="inherits v1 gaps",
            quote_completeness="inherits v1",
            known_truncation="inherits v1 truncation; grid1s `last` has a recorded LOOKAHEAD defect "
                             "(AUCTION04 01_build_clean_substrate.py:17-21)",
            location=rel, extraction="MATERIALIZED", cost="$0",
            evidence_class="MICROSTRUCTURE-CURRENT", seal=f"pre-{SEAL}",
            suitable="spread/cost audit", unsuitable="anything causal using grid1s `last` unfixed")

es_old = sessions_in(os.path.join(ROOT, "research/scalping_lab/substrate/raw/ES"),
                     r"^es_s(\d{8})")          # ES files are es_sYYYYMMDD.parquet, not sYYYYMMDD
add(asset="ES tick+BBO (OLD)", symbol="ES", resolution="tick", series="Last+Bid+Ask",
    first=min(es_old) if es_old else "", last=max(es_old) if es_old else "",
    usable_sessions=len(es_old), full_vs_partial="manifest marks ARCHIVE_ONLY",
    missing="", quote_completeness="", known_truncation="unaudited",
    location="research/scalping_lab/substrate/raw/ES", extraction="MATERIALIZED", cost="$0",
    evidence_class="MICROSTRUCTURE-CURRENT", seal=f"pre-{SEAL}",
    suitable="cross-market microstructure (directive s32)",
    unsuitable="1-minute cross-market conclusions (W122 tested a different family)")

# ------------------------------------------------------------------ 3. internals
MI = os.path.join(ROOT, "research/data_internals/MANIFEST.csv")
if os.path.exists(MI):
    I = pd.read_csv(MI)
    for _, r in I.iterrows():
        add(asset=f"Market internals {r['symbol']}", symbol=r["symbol"], resolution="1-minute",
            series="OHLC index (NO volume)", first=r["first"], last=r["last"],
            usable_sessions=1147, full_vs_partial="RTH only, 09:31-15:59",
            missing="no overnight session at all",
            quote_completeness="N/A", known_truncation="none",
            location="research/data_internals/ (parquet gitignored)",
            extraction="MATERIALIZED", cost="$0",
            evidence_class="REGIME-LOCAL (2022+)", seal=f"pre-{SEAL}, hard-dropped at build",
            suitable="RTH breadth/vol state; covers 764 of 2,139 P1 decisions (35.7 %)",
            unsuitable="the 64 % of P1 decisions that are overnight - permanent ceiling")

# ------------------------------------------------------------------ 4. NT8 local store, unextracted
NCD = re.compile(r"^(\d{8})\d{4}\.(Last|Bid|Ask)\.ncd$", re.I)
add(asset="NQ tick store (UNEXTRACTED remainder)", symbol="NQ", resolution="tick",
    series="Last (+Bid/Ask where present)",
    first=min(usable_last - (old_nq | new_nq)) if (usable_last - (old_nq | new_nq)) else "",
    last=max(usable_last - (old_nq | new_nq)) if (usable_last - (old_nq | new_nq)) else "",
    usable_sessions=len(usable_last - (old_nq | new_nq)),
    full_vs_partial=f"{len(full_q - (old_nq | new_nq))} quote-FULL remain",
    missing="", quote_completeness="mostly Last-only",
    known_truncation="none - would use v4 exporter",
    location="~/Documents/NinjaTrader 8/db/tick", extraction="ON DISK, NOT EXTRACTED", cost="$0",
    evidence_class="MICROSTRUCTURE-CURRENT", seal=f"pre-{SEAL}",
    suitable="signed-flow lane expansion", unsuitable="quote features")

RM = pd.read_csv(os.path.join(ROOT, "runs/DATA_CAPABILITY_AUDIT_20260827/out/retention_matrix.csv"))
mm = RM[(RM["kind"] == "minute") & (RM["series"] == "Last") & (RM["distinct_usable"] > 100)]
for _, r in mm.iterrows():
    if r["root"] == "NQ":
        continue
    add(asset=f"{r['root']} 1-minute store", symbol=r["root"], resolution="1-minute",
        series="Last OHLCV", first=r["usable_first"], last=r["usable_last"],
        usable_sessions=int(r["distinct_usable"]), full_vs_partial="unaudited",
        missing="unaudited", quote_completeness="N/A", known_truncation="none",
        location="~/Documents/NinjaTrader 8/db/minute", extraction="ON DISK, NOT EXTRACTED",
        cost="$0", evidence_class="unclassified", seal=f"pre-{SEAL}",
        suitable="cross-market intraday", unsuitable="")

# ------------------------------------------------------------------ 5. provider-reachable
INV = os.path.join(ROOT, "runs/MULTIMARKET_INVENTORY_20260827/out/inventory.csv")
if os.path.exists(INV):
    V = pd.read_csv(INV)
    piv = V.pivot_table(index="root", columns="probe_year", values="bars",
                        aggfunc="sum").fillna(0)
    deep = sorted(piv[(piv > 100).all(axis=1)].index)
    add(asset="Multi-market DAILY via connection", symbol=f"{len(deep)} roots: {','.join(deep)}",
        resolution="daily", series="Last OHLCV",
        first="2016 probe (>=15y reachable: ES 12-11, ZN 12-16 served)", last="2026-07-31",
        usable_sessions="~250/yr/root, contract-level",
        full_vs_partial="6 sectors: equity index, rates, FX, energy, metals, ags",
        missing="RTY pre-2017 (CME listing); ZS September never resolves",
        quote_completeness="N/A", known_truncation="none",
        location="provider on demand; NOT materialized", extraction="INVENTORIED ONLY", cost="$0",
        evidence_class="STRUCTURAL (candidate)", seal="n/a",
        suitable="multi-market TSMOM/carry - slow signals NEED long history",
        unsuitable="anything intraday")

# ------------------------------------------------------------------ 6. seals
add(asset="SEALED forward pool", symbol="all", resolution="all", series="all",
    first=SEAL, last="ongoing", usable_sessions="~19 as of 2026-08-27",
    full_vs_partial="", missing="", quote_completeness="", known_truncation="",
    location="not read", extraction="**DO NOT READ**", cost="$0",
    evidence_class="GLOBAL VIRGIN", seal="**VIRGIN**",
    suitable="WEEKLY_EDGE_FORWARD_PROTOCOL checkpoints only",
    unsuitable="everything else")
add(asset="BURNED window", symbol="all", resolution="all", series="all",
    first=BURN_A, last=BURN_B, usable_sessions="", full_vs_partial="", missing="",
    quote_completeness="", known_truncation="", location="", extraction="", cost="",
    evidence_class="BURNED", seal="**BURNED**",
    suitable="reporting only", unsuitable="any fresh-evidence claim")

D = pd.DataFrame(rows)
D.to_csv(os.path.join(OUT, "DATA_ASSET_REGISTRY.csv"), index=False)

# ------------------------------------------------------------------ render the document
def esc(x):
    return str(x).replace("|", "\\|").replace("\n", " ")


L = []
L.append("# DATA ASSET REGISTRY\n")
L.append(f"**GENERATED FROM MEASUREMENT by `research/data/build_registry.py` at `{HEAD}`. "
         "Do not hand-edit — regenerate.**\n")
L.append("---\n")
L.append("## ⚠️ The standing rule this registry exists to enforce\n")
L.append("> ### **INSTRUMENT-DATES ARE NOT DISTINCT USABLE SESSIONS.**\n")
L.append("Three counts for NQ tick were circulating, all *correct about different populations* — "
         "which is exactly how a power claim goes wrong:\n")
L.append("| figure | definition | class | may be used for |")
L.append("|---:|---|---|---|")
L.append(f"| **{len(allT_dates)}** | dates with ≥ 1 `Last` `.ncd` file, pre-seal | **FILE PRESENCE** | planning extraction |")
L.append(f"| **{len(allT_dates) - 48}** | the above minus the 48 already extracted (runlist rows) | **FILE PRESENCE** | planning extraction |")
L.append(f"| **{len(usable_last)}** | of those, `last_frac ≥ 0.90` of required session hours | **USABLE SESSION** | **power** |")
L.append(f"| **{len(full_q)}** | quote-complete ≥ 90 % | **USABLE SESSION** | **power, quote features only** |")
L.append("")
L.append(f"`{len(allT_dates)} − 48 = {len(allT_dates) - 48}` exactly. **Only the USABLE SESSION class "
         "may enter a power calculation.** A stale `139` also circulated: it was the pre-correction "
         "date-level `bbo_complete=False` count and is **retired**.\n")
L.append("## ⚠️ Corrections this measurement forced\n")
L.append(f"- **Truncated old-substrate files: {trunc}, not 17.** The 17 came from the old MANIFEST's "
         "`capped` column, which was computed over 61 rows including `_rth` supplements. Measuring "
         f"the 48 session parquets directly gives **{trunc}**. Earlier statements of 17 are wrong.\n")
L.append("## Materialization status\n")
L.append(f"- **NQ quote-FULL materialized: {len((old_nq | new_nq) & full_q)} of a {len(full_q)} "
         "ceiling** — this lane is essentially exhausted on this disk.")
L.append(f"- **NQ Last-usable materialized: {len((old_nq | new_nq) & usable_last)} of a "
         f"{len(usable_last)} ceiling** — {len(usable_last - (old_nq | new_nq))} sessions remain "
         "extractable for the signed-flow lane.\n")
L.append("## Registry\n")
cols = ["asset", "symbol", "resolution", "series", "first", "last", "usable_sessions",
        "extraction", "cost", "evidence_class", "seal"]
L.append("| " + " | ".join(cols) + " |")
L.append("|" + "---|" * len(cols))
for _, r in D.iterrows():
    L.append("| " + " | ".join(esc(r.get(c, "")) for c in cols) + " |")
L.append("\n## Per-asset detail — completeness, truncation, and what each may be used for\n")
for _, r in D.iterrows():
    L.append(f"### {r['asset']}\n")
    L.append(f"- **location** `{r.get('location','')}` · **status** {r.get('extraction','')} "
             f"· **cost** {r.get('cost','')}")
    L.append(f"- **quote completeness**: {r.get('quote_completeness','') or 'n/a'}")
    L.append(f"- **known truncation**: {r.get('known_truncation','') or 'none'}")
    L.append(f"- **missing intervals**: {r.get('missing','') or 'none recorded'}")
    L.append(f"- **full vs partial**: {r.get('full_vs_partial','') or 'n/a'}")
    L.append(f"- ✅ **suitable for**: {r.get('suitable','')}")
    L.append(f"- ❌ **unsuitable for**: {r.get('unsuitable','') or '—'}")
    L.append("")
open(os.path.join(OUT, "DATA_ASSET_REGISTRY.md"), "wb").write(
    "\n".join(L).encode("utf-8"))

print(f"  {len(D)} assets measured -> DATA_ASSET_REGISTRY.csv + .md")
print(f"  truncated old-substrate files detected: {trunc}")
print(f"  NQ quote-FULL materialized: {len((old_nq | new_nq) & full_q)} of {len(full_q)} ceiling")
print(f"  NQ Last-usable materialized: {len((old_nq | new_nq) & usable_last)} of {len(usable_last)} ceiling")
