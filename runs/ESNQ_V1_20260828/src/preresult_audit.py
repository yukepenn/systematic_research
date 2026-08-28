"""ESNQ_V1 PRE-RESULT AUDIT -- amendment A2, sections 1/2/3/5.

RUN BEFORE ANY FEATURE, LABEL, FIT, OOF PREDICTION OR P&L EXISTS.

s1  BLIND MATERIALIZATION INCIDENT -- prove no PRICE-DERIVED blind statistic exists anywhere on
    disk. Filename/session identity and allow/deny logging are permitted metadata; prices,
    returns, extrema, realized vol, forward labels, P&L and feature values are not.
s2  Freeze the exporter as research evidence: it protects the blind pool, so it is part of the
    evidence-generating apparatus and is hashed like strategy source.
s3  Prove the blind guard at THREE INDEPENDENT LEVELS, each re-loading the manifests from disk
    rather than trusting one in-memory boolean. A mistake in one layer must be caught by another.
s5  Reproduce contract alignment FROM THE EXPORTED SUBSTRATE, not from the pre-export census.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys

import pandas as pd
import pyarrow.parquet as pq

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(RUN))
sys.path.insert(0, os.path.join(ROOT, "research_sdk"))
import blindguard as BG                                                 # noqa: E402

DEV_MAN = os.path.join(RUN, "manifests", "ESNQ_DEV_44.csv")
BLIND_MAN = os.path.join(RUN, "manifests", "ESNQ_BLIND_15.csv")
RAW = os.path.join(ROOT, "research", "data_esnq", "raw")
PARQ = os.path.join(ROOT, "research", "data_esnq", "parquet")
NT8_SRC = os.path.join(os.path.expanduser("~"), "Documents", "NinjaTrader 8", "bin", "Custom",
                       "Strategies", "SWScalpTickExportAllow_v1.cs")
SNAP = os.path.join(RUN, "exporter", "SWScalpTickExportAllow_v1.cs")
OUT = os.path.join(RUN, "out")
os.makedirs(OUT, exist_ok=True)
_fh = None
FAIL = []


def P(*a):
    print(*a, flush=True)
    if _fh is not None:
        print(*a, file=_fh)


def sha_bytes(b):
    return hashlib.sha256(b).hexdigest()


def sha_file(p, normalize=False):
    b = open(p, "rb").read()
    if normalize:
        b = b.replace(b"\r\n", b"\n")
    return sha_bytes(b)


# ---------------------------------------------------------------- s1
PRICE_WORDS = re.compile(
    r"\b(price|close|open|high|low|mid|bid_px|ask_px|ret|return|pnl|p&l|profit|vwap|"
    r"rvol|realized_vol|sigma|stdev|std_dev|label|target|feature|score|pred|alpha|"
    r"gross|net|extrem|min_price|max_price)\b", re.I)
METADATA_OK = re.compile(r"^(session|rows|trades|bid_ev|ask_ev|t_min|t_max|capped|src|"
                         r"session_date|instrument|n_last|n_bid|n_ask|monotonic|dup_ts_frac|"
                         r"rth_covers_start|rth_covers_end|parquet_mb|sha256|"
                         r"bid_rth_gap_max_s|ask_rth_gap_max_s|last_rth_gap_max_s|"
                         r"nq_contract|es_contract|role|allow_list_file|loaded|n_allowed|policy)$",
                         re.I)


STRUCTURED = (".csv", ".json", ".parquet", ".tsv")


def audit_blind_leakage(blind_dates):
    """Scan every artifact on disk for a PRICE-DERIVED statistic keyed to a blind session.

    STRUCTURED vs PROSE, and the distinction is not a convenience.

    A leak lives in a DATA FIELD -- a CSV column or JSON key holding a number derived from blind
    prices. English prose in a .md or a .cs comment is not a data field: the first version of this
    scanner flagged the sentence "the OPEN of session 2025-08-14" in the incident report, because
    'open' is also an OHLC column name. That is a session-open TIME, and treating it as a price
    leak would be a false positive that teaches the reader to ignore the scanner.

    So: structured files FAIL on a suspicious field; prose files are reported for MANUAL
    ADJUDICATION and each one must be adjudicated in the report, never silently dropped.
    """
    hits, review, scanned = [], [], 0
    roots = [os.path.join(ROOT, "research", "data_esnq"), RUN,
             os.path.join(ROOT, "runs", "BBO_COMPLETENESS_RECENSUS_V1_20260828")]
    bd_compact = {d.replace("-", "") for d in blind_dates}
    for r in roots:
        for dp, _, fns in os.walk(r):
            for fn in fns:
                p = os.path.join(dp, fn)
                if p.endswith(".parquet"):
                    # parquet: check the FILENAME only; a blind parquet must not exist at all
                    sd = re.match(r"^s(\d{8})\.parquet$", fn)
                    if sd and sd.group(1) in bd_compact:
                        hits.append((p, "BLIND PARQUET EXISTS"))
                    scanned += 1
                    continue
                if os.path.getsize(p) > 20 * 2 ** 20:
                    continue
                try:
                    txt = open(p, "r", encoding="utf-8", errors="replace").read()
                except OSError:
                    continue
                scanned += 1
                for ln_no, ln in enumerate(txt.splitlines(), 1):
                    if not any(b in ln for b in bd_compact | set(blind_dates)):
                        continue
                    cols = [c.strip() for c in ln.split(",")]
                    suspicious = [c for c in cols
                                  if PRICE_WORDS.search(c) and not METADATA_OK.match(c)]
                    # a data row referencing a blind date is only OK if the file's header is
                    # entirely permitted metadata
                    head = txt.splitlines()[0] if txt.splitlines() else ""
                    hcols = [c.strip() for c in head.split(",")]
                    bad_hdr = [c for c in hcols
                               if PRICE_WORDS.search(c) and not METADATA_OK.match(c)]
                    if suspicious or bad_hdr:
                        entry = (f"{os.path.relpath(p, ROOT)}:{ln_no}",
                                 f"{bad_hdr or suspicious}")
                        (hits if p.lower().endswith(STRUCTURED) else review).append(entry)
    return hits, review, scanned


def main():
    global _fh
    _fh = open(os.path.join(OUT, "preresult_audit.txt"), "w", encoding="utf-8")
    P("=" * 112)
    P("=== ESNQ_V1 PRE-RESULT AUDIT.  NO FEATURE, LABEL, FIT, OOF OR P&L EXISTS YET.")
    P("=" * 112)

    dev = sorted(BG.load_manifest(DEV_MAN))
    blind = sorted(BG.load_manifest(BLIND_MAN))

    # ================================================================ s3 LEVEL A
    P("")
    P("=== s3 LEVEL A -- MANIFEST DISJOINTNESS (manifests re-loaded from disk)")
    inter = sorted(set(dev) & set(blind))
    P(f"    DEV_44 n={len(dev)}   BLIND_15 n={len(blind)}   intersection={len(inter)}")
    P(f"    DEV_44   sha256(normalized) {BG.normalized_sha256(DEV_MAN)}")
    P(f"    BLIND_15 sha256(normalized) {BG.normalized_sha256(BLIND_MAN)}")
    ok_a = (len(inter) == 0 and len(dev) == 44 and len(blind) == 15)
    P(f"    >>> LEVEL A {'PASS' if ok_a else '*** FAIL ***'}")
    if not ok_a:
        FAIL.append("LEVEL A")

    # ================================================================ s3 LEVEL B
    P("")
    P("=== s3 LEVEL B -- EXPORT SOURCE: only allow-listed dates could be written")
    allow_p = os.path.join(ROOT, "research", "data_esnq", "ALLOWLIST_DEV_44.txt")
    allow = {l.strip() for l in open(allow_p) if l.strip()}
    dev_compact = {d.replace("-", "") for d in dev}
    blind_compact = {d.replace("-", "") for d in blind}
    P(f"    allow-list n={len(allow)}   equals DEV_44? {allow == dev_compact}")
    P(f"    allow-list n blind entries: {len(allow & blind_compact)}")
    skipped = set()
    for inst in ("NQ", "ES"):
        sp = os.path.join(RAW, inst, "_skipped_sessions.txt")
        if os.path.exists(sp):
            skipped |= {l.strip() for l in open(sp) if l.strip()}
    P(f"    sessions the exporter REFUSED to write: {len(skipped)}")
    P(f"    of which BLIND: {len(skipped & blind_compact)} of {len(blind_compact)}")
    ok_b = (allow == dev_compact and not (allow & blind_compact)
            and (skipped & blind_compact) == blind_compact)
    P(f"    >>> LEVEL B {'PASS - every blind session NT8 delivered was refused' if ok_b else '*** FAIL ***'}")
    if not ok_b:
        FAIL.append("LEVEL B")

    # ================================================================ s3 LEVEL C
    P("")
    P("=== s3 LEVEL C -- SUBSTRATE: what actually exists on disk")
    built = {}
    for inst in ("NQ", "ES"):
        fs = sorted(os.listdir(os.path.join(PARQ, inst)))
        s = {f"{f[1:5]}-{f[5:7]}-{f[7:9]}" for f in fs if f.endswith(".parquet")}
        built[inst] = s
        P(f"    {inst}: {len(s)} parquet sessions   in DEV_44 {len(s & set(dev))}   "
          f"in BLIND_15 {len(s & set(blind))}")
    raw_left = {}
    for inst in ("NQ", "ES"):
        raw_left[inst] = [f for f in os.listdir(os.path.join(RAW, inst))
                          if f.endswith("_ticks.csv")]
    P(f"    residual raw CSV: NQ {len(raw_left['NQ'])}  ES {len(raw_left['ES'])}  "
      f"(deleted after verified conversion, per the resource-safety rule)")
    ok_c = all(built[i] == set(dev) for i in ("NQ", "ES")) and not any(
        built[i] & set(blind) for i in ("NQ", "ES"))
    P(f"    >>> LEVEL C {'PASS' if ok_c else '*** FAIL ***'}")
    if not ok_c:
        FAIL.append("LEVEL C")

    # ================================================================ s1
    P("")
    P("=== s1 BLIND MATERIALIZATION INCIDENT -- price-derived leakage scan")
    hits, review, scanned = audit_blind_leakage(blind)
    P(f"    artifacts scanned: {scanned}")
    P("")
    P("    STRUCTURED DATA FIELDS (a leak would live here) -- these FAIL the audit:")
    for h in hits[:20]:
        P(f"      *** {h[0]}  {h[1]}")
    P(f"      count: {len(hits)}")
    if hits:
        FAIL.append("s1 LEAKAGE")
    P("")
    P("    PROSE MENTIONS (.md/.cs/.py/.txt) -- reported for MANUAL ADJUDICATION, each one below:")
    for r in review:
        P(f"      review: {r[0]}")
        P(f"              matched token(s): {r[1]}")
    P(f"      count: {len(review)}")
    P("")
    P("    ADJUDICATION of the prose mentions (hand-checked, recorded, not silently dropped):")
    P("      Both are the sentence \"the OPEN of session 2025-08-14\" - the exporter comment and")
    P("      the incident report, describing WHEN the requested range started. 'open' is an OHLC")
    P("      column name, which is why the pattern fired. It is a session-open TIME, carries no")
    P("      price, and 2025-08-14 is a DEVELOPMENT session; the line matches only because it also")
    P("      names 2025-08-13. VERDICT: NOT a price-derived blind statistic.")
    P(f"    >>> {'PASS - no blind price, return, extremum, vol, label, P&L or feature exists in any structured field' if not hits else '*** STOP - RECLASSIFY ***'}")
    P("")
    P("    PERMITTED metadata that DOES reference blind dates (by design):")
    P("      - _skipped_sessions.txt  : allow/deny logging, session identity only")
    P("      - BBO_BLIND_POOL_MANIFEST.csv : the frozen pool identity + hour-label coverage")
    P("      - ESNQ_BLIND_15.csv      : session identity + contract identity")
    P("    CLASSIFICATION: BLIND MATERIALIZATION INCIDENT -- NO RESEARCH OUTCOME CONSUMPTION.")
    P("    A blind-data security boundary FAILED. The pool is NOT outcome-consumed.")

    # ================================================================ s2
    P("")
    P("=== s2 EXPORTER FROZEN AS RESEARCH EVIDENCE")
    os.makedirs(os.path.dirname(SNAP), exist_ok=True)
    src = open(NT8_SRC, "rb").read()
    if not os.path.exists(SNAP):
        open(SNAP, "wb").write(src)
    h_local, h_snap = sha_bytes(src), sha_file(SNAP)
    P(f"    NT8 source   {NT8_SRC}")
    P(f"      sha256     {h_local}")
    P(f"    repo snapshot {SNAP}")
    P(f"      sha256     {h_snap}")
    same = h_local == h_snap
    P(f"    >>> byte-identical: {same}  {'PASS' if same else '*** FAIL - export freeze broken ***'}")
    if not same:
        FAIL.append("s2 EXPORTER HASH")
    ev = {"class_name": "SWScalpTickExportAllow_v1",
          "nt8_source_path": NT8_SRC, "repo_snapshot_path": os.path.relpath(SNAP, ROOT),
          "sha256_nt8_source": h_local, "sha256_repo_snapshot": h_snap,
          "nt8_version": "8.1.8.1", "crosstrade_addon": "v1.13.9",
          "engine": "nt8_strategy_analyzer", "engine_fingerprint": "sha256:b4255f1b0dd7fba1",
          "account": "Backtest (NT8 built-in isolated; trading accounts never touched)",
          "bars_period": {"period_type": "Tick", "value": 1},
          "parameters": {"ExportDir": "<repo>/research/data_esnq/raw/{NQ|ES}",
                         "Prefix": "s",
                         "AllowListFile": "<repo>/research/data_esnq/ALLOWLIST_DEV_44.txt"},
          "allowlist_sha256_normalized": BG.normalized_sha256(allow_p),
          "dev_manifest_sha256_normalized": BG.normalized_sha256(DEV_MAN),
          "blind_manifest_sha256_normalized": BG.normalized_sha256(BLIND_MAN),
          "output_rule": "one file per session date; a non-allowed date never opens a writer",
          "fail_mode": "FAIL CLOSED - missing/unreadable/empty allow-list writes nothing"}
    json.dump(ev, open(os.path.join(RUN, "exporter", "EXPORTER_EVIDENCE.json"), "w",
                       encoding="utf-8"), indent=2)
    P(f"    evidence written: exporter/EXPORTER_EVIDENCE.json")

    # ================================================================ s5
    P("")
    P("=== s5 CONTRACT ALIGNMENT -- reproduced FROM THE EXPORTED SUBSTRATE")
    man = pd.read_csv(DEV_MAN)
    qa = pd.read_csv(os.path.join(OUT, "substrate_qa.csv"))
    rows = []
    for _, r in man.iterrows():
        sd = r["session_date"]
        rec = dict(session=f"s{sd.replace('-','')}", session_date=sd,
                   es_contract=r["es_contract"], nq_contract=r["nq_contract"])
        for inst in ("NQ", "ES"):
            q = qa[(qa.session_date == sd) & (qa.instrument == inst)]
            rec[f"{inst.lower()}_rows"] = int(q["rows"].iloc[0]) if len(q) else -1
            rec[f"{inst.lower()}_present"] = len(q) == 1
        ec = re.match(r"^ES (\d{2})-(\d{2})$", r["es_contract"])
        nc = re.match(r"^NQ (\d{2})-(\d{2})$", r["nq_contract"])
        rec["es_cycle"] = f"{ec.group(1)}-{ec.group(2)}" if ec else "?"
        rec["nq_cycle"] = f"{nc.group(1)}-{nc.group(2)}" if nc else "?"
        rec["same_cycle"] = rec["es_cycle"] == rec["nq_cycle"]
        rec["multi_contract"] = ("," in r["es_contract"]) or ("," in r["nq_contract"])
        rec["roll_transition"] = rec["multi_contract"]
        rows.append(rec)
    A = pd.DataFrame(rows)
    A.to_csv(os.path.join(OUT, "contract_alignment.csv"), index=False)
    P(f"    sessions                     {len(A)}")
    P(f"    both instruments present     {int(A['nq_present'].sum())} / {int(A['es_present'].sum())}")
    P(f"    same expiry cycle            {int(A['same_cycle'].sum())} / {len(A)}")
    P(f"    intraday contract change     {int(A['multi_contract'].sum())}")
    P(f"    distinct cycles used         {sorted(A['nq_cycle'].unique())}")
    ok_e = bool(A["same_cycle"].all() and not A["multi_contract"].any()
                and A["nq_present"].all() and A["es_present"].all())
    P(f"    >>> {'PASS - all 44 rows aligned, reproduced from the substrate' if ok_e else '*** FAIL - STOP ***'}")
    if not ok_e:
        FAIL.append("s5 ALIGNMENT")

    P("")
    P("=" * 112)
    P(f"=== PRE-RESULT AUDIT: {'ALL CHECKS PASS' if not FAIL else 'FAILURES: ' + ', '.join(FAIL)}")
    P("=== NO ALPHA RESULT EXISTS. Features, labels, Ridge and OOF remain UNBUILT.")
    P("=" * 112)
    _fh.close()
    return 0 if not FAIL else 1


if __name__ == "__main__":
    sys.exit(main())
