"""VOLUME00 -- volume SEMANTICS and CAPABILITY.  No return, no P&L, no signal, no model.

Executes runs/VOLUME00_20260828/SPEC.md exactly.  Every threshold below was committed in that
SPEC before this file produced a number.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(RUN))
MM = os.path.join(ROOT, "research", "multi_market", "src")
sys.path.insert(0, MM)
sys.path.insert(0, os.path.join(ROOT, "research_sdk"))
import ncd_day as N                                                          # noqa: E402
import roll as R                                                             # noqa: E402
from contract_truth import load_root                                         # noqa: E402

OUT = os.path.join(RUN, "out")
os.makedirs(OUT, exist_ok=True)
DB = os.path.join(os.path.expanduser("~"), "Documents", "NinjaTrader 8", "db")
DB_DAY, DB_MIN = os.path.join(DB, "day"), os.path.join(DB, "minute")
SEAL = pd.Timestamp("2026-08-01")

# ---- FROZEN IN THE SPEC, BEFORE ANY MEASUREMENT -----------------------------------------
V1_EXACT_MIN, V1_RELTOL = 0.95, 0.005
V2_MAX_DUP_SHARE, V2_MIN_SHARED_VOL = 0.005, 1000
V3_MAX_MEDIAN_RATIO = 0.25
V5_MAX_MEDIAN_COLLAPSE = 0.50
MIN_ALIGNED_DAYS = 200
SAMPLE_PER_ROOT, SAMPLE_MAX_DAYS = 3, 400
J_THRESHOLD, J_JUMP_UNITS = 0.10, 1.0
EMBARGO_LADDER, EMBARGO_RATIO = (0, 1, 3, 5), 1.5
Z_EXTREME = 2.0
LOOKBACK = 63
G1_MIN_ROOTS, G2_MIN_SECTORS, G3_MIN_YEARS = 12, 4, 8
G4_MIN_ROOT_DAYS, G5_MIN_COVERAGE = 1500, 0.80
Y0, Y1 = 2009, 2027

_fh = None


def P(*a):
    print(*a, flush=True)
    print(*a, file=_fh)


def sha256_file(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


# ============================================================ MINUTE READER (structural only)
MIN_CANDIDATES = [
    ("HDR28_REC48", 28, np.dtype([("ts", "<i8"), ("o", "<f8"), ("h", "<f8"), ("l", "<f8"),
                                  ("c", "<f8"), ("v", "<i8")])),
    ("HDR16_REC48", 16, np.dtype([("ts", "<i8"), ("o", "<f8"), ("h", "<f8"), ("l", "<f8"),
                                  ("c", "<f8"), ("v", "<i8")])),
    ("HDR28_REC40", 28, np.dtype([("ts", "<i8"), ("o", "<f4"), ("h", "<f4"), ("l", "<f4"),
                                  ("c", "<f4"), ("v", "<i8")])),
]
NET_EPOCH = np.datetime64("0001-01-01T00:00:00", "us")


def _try_layout(raw, hdr, rec, file_date):
    """Structural acceptance ONLY -- never compared to the daily store."""
    if raw.size <= hdr or (raw.size - hdr) % rec.itemsize:
        return None
    n = (raw.size - hdr) // rec.itemsize
    if n < 5:
        return None
    a = raw[hdr:hdr + n * rec.itemsize].view(rec)
    ts = a["ts"].astype("int64")
    if not np.all(np.diff(ts) > 0):
        return None
    t = (NET_EPOCH + (ts // 10).astype("timedelta64[us]")).astype("datetime64[ns]")
    t = pd.DatetimeIndex(t)
    # every stamp must land inside the named session's plausible window: [D-1 17:00, D+1 00:00)
    lo, hi = file_date - pd.Timedelta(hours=7), file_date + pd.Timedelta(days=1)
    if not ((t >= lo) & (t < hi)).all():
        return None
    o, h, l, c = (a[k].astype(float) for k in "ohlc")
    if not (np.all(h >= np.maximum(o, c) - 1e-6) and np.all(l <= np.minimum(o, c) + 1e-6)):
        return None
    if not np.all(a["v"] >= 0):
        return None
    if not np.all(o > 0):
        return None
    return pd.DataFrame({"t": t, "volume": a["v"].astype("int64")})


def detect_minute_layout(sample_files):
    votes = {}
    for path, fdate in sample_files:
        raw = np.fromfile(path, dtype=np.uint8)
        for name, hdr, rec in MIN_CANDIDATES:
            if _try_layout(raw, hdr, rec, fdate) is not None:
                votes[name] = votes.get(name, 0) + 1
    if not votes:
        return None
    return max(votes.items(), key=lambda kv: kv[1])


def read_minute(path, fdate, layout_name):
    hdr, rec = next((h, r) for n, h, r in MIN_CANDIDATES if n == layout_name)
    return _try_layout(np.fromfile(path, dtype=np.uint8), hdr, rec, fdate)


# ============================================================ MAIN
def main():
    global _fh
    _fh = open(os.path.join(OUT, "volume00.txt"), "w", encoding="utf-8")
    res = {}

    P("=" * 112)
    P("=== VOLUME00 -- DATA SEMANTICS + CAPABILITY.  NO RETURN, NO P&L, NO SIGNAL, NO MODEL.")
    P("=" * 112)
    P(f"    HEAD                {subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,capture_output=True,text=True).stdout.strip()}")
    P(f"    universe            {len(N.CORE)} CORE roots, {len(set(N.SECTOR[r] for r in N.CORE))} sectors")
    P(f"    hard seal cap       every row date < {SEAL.date()}")

    # ---------------------------------------------------------------- STAGE 0  provenance
    P("")
    P("--- STAGE 0  PROVENANCE OF THE VOLUME FIELD (producing artifact -> producing code)")
    rdr = os.path.join(MM, "ncd_day.py")
    blob = subprocess.run(["git", "hash-object", rdr], cwd=ROOT, capture_output=True,
                          text=True).stdout.strip()
    prov = dict(store=DB_DAY, file_pattern="<FULL CONTRACT ID>/<YYYY>.Last.ncd",
                header_bytes=N.HDR, record_dtype=str(N.REC),
                volume_field="int64 at byte offset 40 of each 48-byte record",
                reader="research/multi_market/src/ncd_day.py::read_ncd_day",
                reader_git_blob=blob, reader_sha256=sha256_file(rdr))
    for k, v in prov.items():
        P(f"    {k:<20} {v}")
    res["provenance"] = prov

    # ---------------------------------------------------------------- STAGE 1  panels
    P("")
    P("--- STAGE 1  CONTRACT PANELS  (true unmerged db/day store; AddDataSeries is barred)")
    cache = os.path.join(OUT, "panel.parquet")
    if os.path.exists(cache):
        panel = pd.read_parquet(cache)
        P(f"    loaded cached panel  {len(panel):,} contract-days")
    else:
        parts = []
        for r in N.CORE:
            d = load_root(r, Y0, Y1)
            if len(d):
                d = d[["date", "contract_id", "root", "expiry_key", "open", "high", "low",
                       "close", "volume"]].copy()
                parts.append(d)
                P(f"    {r:<4} contracts {d['contract_id'].nunique():>4}  rows {len(d):>7,}")
        panel = pd.concat(parts, ignore_index=True)
        panel.to_parquet(cache, index=False)
    panel = panel[panel["date"] < SEAL].reset_index(drop=True)
    assert panel["date"].max() < SEAL, "SEAL VIOLATION"
    panel["sector"] = panel["root"].map(N.SECTOR)
    P(f"    panel after seal cap {len(panel):,} contract-days  "
      f"{panel['contract_id'].nunique():,} contracts  {panel['date'].min().date()} -> {panel['date'].max().date()}")

    # ---------------------------------------------------------------- STAGE 2  V4
    P("")
    P("--- STAGE 2  V4  FIELD SEMANTICS")
    v = panel["volume"]
    v4 = dict(dtype=str(v.dtype), negative=int((v < 0).sum()), zero=int((v == 0).sum()),
              nan=int(v.isna().sum()),
              integral=bool(np.all(np.asarray(v.values, dtype=np.float64) ==
                                   np.floor(np.asarray(v.values, dtype=np.float64)))),
              total_rows=int(len(v)), max=int(v.max()), median=float(v.median()))
    v4["PASS"] = bool(v4["negative"] == 0 and v4["nan"] == 0 and v4["integral"]
                      and str(v.dtype).startswith("int"))
    for k, val in v4.items():
        P(f"    {k:<20} {val}")
    P(f"    zero-volume share    {v4['zero']/v4['total_rows']:.4%}  "
      f"(counted MISSING for volume purposes, per SPEC 6)")
    res["V4"] = v4

    # ---------------------------------------------------------------- STAGE 3  V2 / V3
    P("")
    P("--- STAGE 3  V2 DUPLICATION  /  V3 FRONT-vs-DEFERRED   (direct tests of the merged copy)")
    ledgers, held_map = {}, {}
    for r in N.CORE:
        d = panel[panel["root"] == r]
        led = R.build_roll_ledger(d, r)
        ledgers[r] = led
        held_map[r] = R.designated_contract(d, led)

    dup_rows, v3_rows, v2_examples = [], [], []
    for r in N.CORE:
        d = panel[panel["root"] == r]
        piv = d.pivot_table(index="date", columns="contract_id", values="volume")
        ekey = d.groupby("contract_id")["expiry_key"].first()
        piv = piv[sorted(piv.columns, key=lambda c: ekey[c])]
        held = held_map[r]
        nlive_all, ndup, nrat, rats = 0, 0, 0, []
        for dt, row in piv.iterrows():
            live = row.dropna()
            if len(live) < 2:
                continue
            nlive_all += 1
            big = live[live >= V2_MIN_SHARED_VOL]
            if len(big) >= 2 and big.duplicated().any():
                ndup += 1
                if len(v2_examples) < 8:
                    dv = big[big.duplicated(keep=False)]
                    v2_examples.append((r, str(dt.date()), dict(dv.astype("int64"))))
            hc = held.get(dt)
            if isinstance(hc, str) and hc in live.index:
                after = [c for c in piv.columns if ekey[c] > ekey[hc] and c in live.index]
                if after:
                    nxt = after[0]
                    if live[hc] > 0:
                        rats.append(float(live[nxt]) / float(live[hc]))
                        nrat += 1
        dup_rows.append(dict(root=r, sector=N.SECTOR[r], multi_contract_days=nlive_all,
                             dup_days=ndup,
                             dup_share=(ndup / nlive_all) if nlive_all else np.nan))
        v3_rows.append(dict(root=r, sector=N.SECTOR[r], n=nrat,
                            median_ratio=float(np.median(rats)) if rats else np.nan,
                            p90_ratio=float(np.percentile(rats, 90)) if rats else np.nan,
                            share_exactly_one=float(np.mean(np.abs(np.array(rats) - 1.0) < 1e-12))
                            if rats else np.nan))
    dup = pd.DataFrame(dup_rows)
    v3t = pd.DataFrame(v3_rows)
    tot_days, tot_dup = int(dup["multi_contract_days"].sum()), int(dup["dup_days"].sum())
    v2_share = tot_dup / tot_days if tot_days else np.nan
    all_rats_med = float(np.nanmedian(v3t["median_ratio"]))
    v3_pool_one = float(np.nansum(v3t["share_exactly_one"] * v3t["n"]) / max(v3t["n"].sum(), 1))
    P(f"    V2  root-days with >=2 live contracts        {tot_days:,}")
    P(f"    V2  days with an identical-volume pair >={V2_MIN_SHARED_VOL}  {tot_dup:,}   "
      f"share {v2_share:.4%}   gate <= {V2_MAX_DUP_SHARE:.2%}   "
      f"{'PASS' if v2_share <= V2_MAX_DUP_SHARE else '*** FAIL ***'}")
    if v2_examples:
        P("        examples:")
        for r, dt, dv in v2_examples:
            P(f"          {r} {dt}  {dv}")
    P(f"    V3  median  vol(next live) / vol(designated), pooled over roots   {all_rats_med:.4f}")
    P(f"    V3  share of those ratios EXACTLY 1.000 (the merged-copy signature) {v3_pool_one:.6%}")
    P(f"        gate median < {V3_MAX_MEDIAN_RATIO}   "
      f"{'PASS' if all_rats_med < V3_MAX_MEDIAN_RATIO else '*** FAIL ***'}")
    P("")
    P("    per root:")
    P(f"      {'root':<5}{'sector':<14}{'multi-days':>11}{'dup':>7}{'dup share':>11}"
      f"{'V3 median':>11}{'V3 p90':>9}{'=1.000':>9}")
    for _, a in dup.merge(v3t[["root", "median_ratio", "p90_ratio", "share_exactly_one"]],
                          on="root").iterrows():
        P(f"      {a['root']:<5}{a['sector']:<14}{a['multi_contract_days']:>11,}{a['dup_days']:>7,}"
          f"{a['dup_share']:>11.4%}{a['median_ratio']:>11.4f}{a['p90_ratio']:>9.3f}"
          f"{a['share_exactly_one']:>9.4%}")
    dup.merge(v3t, on=["root", "sector"]).to_csv(os.path.join(OUT, "volume_semantics.csv"),
                                                 index=False)
    res["V2"] = dict(multi_contract_days=tot_days, dup_days=tot_dup, share=v2_share,
                     gate=V2_MAX_DUP_SHARE, PASS=bool(v2_share <= V2_MAX_DUP_SHARE))
    res["V3"] = dict(pooled_median_ratio=all_rats_med, share_exactly_one=v3_pool_one,
                     gate=V3_MAX_MEDIAN_RATIO, PASS=bool(all_rats_med < V3_MAX_MEDIAN_RATIO))

    # ---------------------------------------------------------------- STAGE 4  V5
    P("")
    P("--- STAGE 4  V5  DOES VOLUME COLLAPSE INTO EXPIRY?  (a merged copy would not)")
    coll = []
    for cid, g in panel.groupby("contract_id"):
        g = g.sort_values("date")
        if len(g) < LOOKBACK + 5:
            continue
        tail = float(np.median(g["volume"].values[-5:]))
        base = float(np.median(g["volume"].values[-(LOOKBACK + 5):-5]))
        if base <= 0:
            continue
        coll.append(dict(contract_id=cid, root=g["root"].iloc[0], ratio=tail / base))
    ct = pd.DataFrame(coll)
    v5med = float(ct["ratio"].median())
    P(f"    contracts measured                        {len(ct):,}")
    P(f"    median  last-5-day vol / own 63d median   {v5med:.4f}   "
      f"gate < {V5_MAX_MEDIAN_COLLAPSE}   {'PASS' if v5med < V5_MAX_MEDIAN_COLLAPSE else '*** FAIL ***'}")
    P(f"    share of contracts with ratio > 0.90 (no collapse at all)  "
      f"{float((ct['ratio']>0.90).mean()):.2%}")
    byroot = ct.groupby("root")["ratio"].median().sort_values()
    P("    per-root median collapse ratio: " +
      "  ".join(f"{r} {v:.3f}" for r, v in byroot.items()))
    res["V5"] = dict(contracts=int(len(ct)), median_ratio=v5med, gate=V5_MAX_MEDIAN_COLLAPSE,
                     PASS=bool(v5med < V5_MAX_MEDIAN_COLLAPSE),
                     share_no_collapse=float((ct["ratio"] > 0.90).mean()))

    # ---------------------------------------------------------------- STAGE 5  V1
    P("")
    P("--- STAGE 5  V1  CROSS-SOURCE  db/day daily volume  vs  SUM of db/minute session volume")
    P("    GetBars is DISQUALIFIED as reference: it is the writer that produced the store under")
    P("    test, and calling it would mutate the evidence while certifying it.")
    day_ids = set(os.listdir(DB_DAY)) if os.path.isdir(DB_DAY) else set()
    legal = set()
    for r in N.CORE:
        for cid, _, m, y in N.contracts_for(r, Y0, Y1):
            legal.add(cid)
    mins = sorted(n for n in os.listdir(DB_MIN)
                  if os.path.isdir(os.path.join(DB_MIN, n)) and n in legal and n in day_ids)
    ekey_all = panel.groupby("contract_id")["expiry_key"].first().to_dict()
    byroot_ids = {}
    for cid in mins:
        rt = cid.split()[0]
        byroot_ids.setdefault(rt, []).append(cid)
    sample = []
    for rt in sorted(byroot_ids):
        lst = sorted(byroot_ids[rt], key=lambda c: ekey_all.get(c, 0))
        n = len(lst)
        for i in sorted({0, n // 2, n - 1}):
            sample.append(lst[i])
    P(f"    minute-store CORE contracts present in BOTH stores  {len(mins)}   "
      f"roots {sorted(byroot_ids)}")
    P(f"    deterministic sample (first/middle/last per root)    {len(sample)} contracts")

    files = []
    for cid in sample:
        dd = os.path.join(DB_MIN, cid)
        fs = sorted(f for f in os.listdir(dd) if re.match(r"^\d{8}\.Last\.ncd$", f))
        for f in fs[:SAMPLE_MAX_DAYS]:
            files.append((cid, os.path.join(dd, f), pd.Timestamp(f[:8])))
    P(f"    candidate minute session files                      {len(files):,}")

    layout = detect_minute_layout([(p, d) for _, p, d in files[:40]])
    if layout is None:
        P("    *** MINUTE LAYOUT NOT RESOLVED -- reference UNAVAILABLE (SPEC 3.7) ***")
        res["V1"] = dict(status="REFERENCE UNAVAILABLE", reason="no structural layout accepted")
    else:
        lname, nvote = layout
        P(f"    minute record layout accepted structurally: {lname}  ({nvote}/40 probe files)")
        recs = []
        for cid, p, fdate in files:
            m = read_minute(p, fdate, lname)
            if m is None or len(m) == 0:
                continue
            recs.append(dict(contract_id=cid, file_date=fdate, minute_vol=int(m["volume"].sum()),
                             bars=len(m), t0=m["t"].iloc[0], t1=m["t"].iloc[-1]))
        mv = pd.DataFrame(recs)
        P(f"    minute sessions parsed                              {len(mv):,}")
        dayv = panel.set_index(["contract_id", "date"])["volume"]
        best = None
        for aname, shift in (("A0", 0), ("A1:+1", 1), ("A1:-1", -1)):
            key = list(zip(mv["contract_id"], mv["file_date"] + pd.Timedelta(days=shift)))
            dv = pd.Series([dayv.get(k, np.nan) for k in key], index=mv.index)
            ok = dv.notna()
            if ok.sum() == 0:
                P(f"    alignment {aname:<6} matched 0 contract-days")
                continue
            a, b = mv.loc[ok, "minute_vol"].values.astype(float), dv[ok].values.astype(float)
            exact = float(np.mean(a == b))
            rel = np.abs(a - b) / np.maximum(b, 1.0)
            within = float(np.mean(rel <= V1_RELTOL))
            P(f"    alignment {aname:<6} matched {int(ok.sum()):>6,} contract-days   "
              f"exact {exact:>7.2%}   within {V1_RELTOL:.1%} {within:>7.2%}   "
              f"median rel err {float(np.median(rel)):.4%}")
            cand = dict(alignment=aname, matched=int(ok.sum()), exact=exact, within=within,
                        median_rel_err=float(np.median(rel)))
            if best is None or exact > best["exact"]:
                best = cand
        if best is None or best["matched"] < MIN_ALIGNED_DAYS:
            P(f"    *** fewer than {MIN_ALIGNED_DAYS} aligned contract-days -- "
              f"reference UNAVAILABLE (SPEC 3.7) ***")
            res["V1"] = dict(status="REFERENCE UNAVAILABLE",
                             reason="insufficient aligned contract-days", best=best)
        else:
            ok = best["exact"] >= V1_EXACT_MIN or best["within"] >= V1_EXACT_MIN
            P(f"    >>> adopted alignment {best['alignment']}   "
              f"{'PASS' if ok else '*** FAIL -- SOURCES DISAGREE ***'}")
            res["V1"] = dict(status="MEASURED", layout=lname, **best, PASS=bool(ok))

    # ---------------------------------------------------------------- STAGE 6  causal roll
    P("")
    P("--- STAGE 6  CAUSAL ACTIVE-CONTRACT CONTRACT  (recovered, not reinvented)")
    P("    The roll for day t compares CURRENT vs NEXT eligible contract using volume at t-1 ONLY.")
    P("    Stated plainly because it is true: ACTIVE_CONTRACT(t) is decided from t-1 volume.")
    P("    The pre-expiry override uses contract mechanics only -- no price, no volume.")
    R.test_no_roll_telescopes(verbose=False)
    R.test_basis_invariance(verbose=False)
    R.test_roll_causality(verbose=False)
    P("    roll.py unit tests: no-roll telescoping PASS | basis invariance PASS | "
      "causality (teeth + no leak) PASS")
    led_all = pd.concat([ledgers[r] for r in N.CORE], ignore_index=True)
    b = led_all.dropna(subset=["info_cutoff"])
    causal_ok = bool((pd.to_datetime(b["info_cutoff"]) < pd.to_datetime(b["decision_date"])).all())
    P(f"    real ledger: {len(led_all):,} rows  "
      f"({int((led_all.reason=='VOLUME_CROSSOVER').sum())} volume, "
      f"{int((led_all.reason=='PRE_EXPIRY_OVERRIDE').sum())} pre-expiry, "
      f"{int((led_all.reason=='INITIALISE').sum())} init)")
    P(f"    ASSERTION every info_cutoff STRICTLY < its decision_date on all {len(b):,} "
      f"volume rolls: {'PASS' if causal_ok else '*** FAIL ***'}")
    assert causal_ok, "CAUSAL ROLL DEFECT"
    res["causal_roll"] = dict(rows=int(len(led_all)),
                              volume_rolls=int((led_all.reason == "VOLUME_CROSSOVER").sum()),
                              pre_expiry_rolls=int((led_all.reason == "PRE_EXPIRY_OVERRIDE").sum()),
                              PASS=causal_ok)

    # ---------------------------------------------------------------- STAGE 7  entanglement
    P("")
    P("--- STAGE 7  ROLL-ENTANGLEMENT AUDIT   (no return, no P&L anywhere in this stage)")

    def lv(x):
        return np.log1p(np.asarray(x, dtype=float))

    def roll_mad_scale(series):
        """1.4826 * MAD over the PRIOR `LOOKBACK` observations, strictly lagged."""
        s = pd.Series(series)
        med = s.rolling(LOOKBACK).median().shift(1)
        mad = s.rolling(LOOKBACK).apply(lambda w: np.median(np.abs(w - np.median(w))),
                                        raw=True).shift(1)
        return med, 1.4826 * mad

    jump_rows = []
    for r in N.CORE:
        d = panel[panel["root"] == r]
        piv = d.pivot_table(index="date", columns="contract_id", values="volume")
        held = held_map[r]
        des = pd.Series([piv.at[dt, c] if (isinstance(c, str) and c in piv.columns
                                           and dt in piv.index) else np.nan
                         for dt, c in held.items()], index=held.index)
        _, sc = roll_mad_scale(lv(des.values))
        sc = pd.Series(sc.values, index=held.index)
        root_scale = float(np.nanmedian(sc.values))
        led = ledgers[r]
        for _, row in led.iterrows():
            if not isinstance(row["old_contract"], str):
                continue
            dt = row["effective_date"]
            oc, nc = row["old_contract"], row["new_contract"]
            if dt not in piv.index or oc not in piv.columns or nc not in piv.columns:
                continue
            vo, vn = piv.at[dt, oc], piv.at[dt, nc]
            if pd.isna(vo) or pd.isna(vn):
                continue
            jump = float(np.log1p(vn) - np.log1p(vo))
            s = sc.get(dt, np.nan)
            if not np.isfinite(s) or s <= 0:
                s = root_scale
            jump_rows.append(dict(root=r, sector=N.SECTOR[r], date=dt, reason=row["reason"],
                                  old=oc, new=nc, jump_lv=jump, scale=s,
                                  jump_units=jump / s if s and np.isfinite(s) else np.nan))
    jt = pd.DataFrame(jump_rows)
    jt.to_csv(os.path.join(OUT, "roll_entanglement.csv"), index=False)
    big = jt["jump_units"].abs() > J_JUMP_UNITS
    J = float(big.mean())
    P(f"    causal rolls with BOTH contracts quoted on the switch date  {len(jt):,}")
    P(f"    same-day contract-switch log-volume jump  LV(new,d) - LV(old,d):")
    P(f"        median {jt['jump_lv'].median():+.3f}   mean {jt['jump_lv'].mean():+.3f}   "
      f"p05 {jt['jump_lv'].quantile(.05):+.3f}   p95 {jt['jump_lv'].quantile(.95):+.3f}")
    P(f"    in units of the root's own trailing 1.4826*MAD63 of LV:")
    P(f"        |jump| > {J_JUMP_UNITS}  on  {int(big.sum()):,} of {len(jt):,}   J = {J:.4f}   "
      f"threshold {J_THRESHOLD}")
    for rs, g in jt.groupby("reason"):
        P(f"        {rs:<22} n {len(g):>5,}  median jump {g['jump_lv'].median():+7.3f}  "
          f"|jump|>1 unit {float((g['jump_units'].abs()>J_JUMP_UNITS).mean()):.2%}")
    REPRESENTATION = "DESIGNATED_CONTRACT" if J <= J_THRESHOLD else "ROOT_TOTAL"
    P("")
    P(f"    >>> REPRESENTATION DECISION RULE (frozen in SPEC 3.6, resolved on roll mechanics only)")
    P(f"    >>> J = {J:.4f}  {'<=' if J <= J_THRESHOLD else '>'} {J_THRESHOLD}  ->  "
      f"ADOPTED REPRESENTATION = {REPRESENTATION}")
    if REPRESENTATION == "ROOT_TOTAL":
        P("    >>> root-total volume is the SUM over all live contracts of the root on date d.")
        P("    >>> It is INVARIANT to which contract is designated, so it cannot jump at a roll.")
        P("    >>> It is only meaningful BECAUSE V2/V3 certify the per-contract fields are not")
        P("    >>> duplicated copies -- under a merged copy the sum would be n x the front.")
    res["roll_entanglement"] = dict(rolls_measured=int(len(jt)), J=J, threshold=J_THRESHOLD,
                                    representation=REPRESENTATION,
                                    median_jump_lv=float(jt["jump_lv"].median()))

    # ---- build the adopted volume series per root
    P("")
    P(f"--- STAGE 7b  ZVOL under {REPRESENTATION}, and the ROLL EMBARGO ladder")
    er = pd.read_parquet(os.path.join(ROOT, "research", "multi_market", "out",
                                      "economic_returns.parquet"))
    er = er[er["date"] < SEAL]
    vol_rows = []
    for r in N.CORE:
        d = panel[panel["root"] == r]
        piv = d.pivot_table(index="date", columns="contract_id", values="volume")
        if REPRESENTATION == "ROOT_TOTAL":
            s = piv.sum(axis=1, min_count=1)
        else:
            held = held_map[r]
            s = pd.Series([piv.at[dt, c] if (isinstance(c, str) and c in piv.columns
                                             and dt in piv.index) else np.nan
                           for dt, c in held.items()], index=held.index)
        s = s[s.index < SEAL]
        rolldates = set(pd.to_datetime(ledgers[r]["effective_date"]).tolist())
        idx = list(s.index)
        pos_of = {dt: i for i, dt in enumerate(idx)}
        rpos = sorted(pos_of[dt] for dt in rolldates if dt in pos_of)
        dist = np.full(len(idx), 10 ** 6, dtype=np.int64)
        for rp in rpos:
            lo, hi = max(0, rp - 12), min(len(idx), rp + 13)
            for i in range(lo, hi):
                dist[i] = min(dist[i], abs(i - rp))
        vol_rows.append(pd.DataFrame(dict(root=r, sector=N.SECTOR[r], date=idx,
                                          vol=s.values, roll_dist=dist)))
    vt = pd.concat(vol_rows, ignore_index=True)
    vt["vol_usable"] = vt["vol"].notna() & (vt["vol"] > 0)
    vt["LV"] = np.where(vt["vol_usable"], np.log1p(vt["vol"].fillna(0)), np.nan)

    zs = []
    for r, g in vt.groupby("root"):
        g = g.sort_values("date").copy()
        x = g["LV"]
        med = x.rolling(LOOKBACK, min_periods=LOOKBACK).median().shift(1)
        mad = x.rolling(LOOKBACK, min_periods=LOOKBACK).apply(
            lambda w: np.median(np.abs(w - np.median(w))), raw=True).shift(1)
        g["ZVOL"] = (x - med) / np.maximum(1.4826 * mad, 1e-6)
        zs.append(g)
    vt = pd.concat(zs, ignore_index=True)
    ex = vt["ZVOL"].abs() > Z_EXTREME
    P(f"    observations with a defined ZVOL          {int(vt['ZVOL'].notna().sum()):,}")
    P(f"    unconditional |ZVOL| > {Z_EXTREME} rate            "
      f"{float(ex[vt['ZVOL'].notna()].mean()):.4%}")
    ratios = {}
    for e in (1, 3, 5):
        near = vt["roll_dist"] <= e
        m = vt["ZVOL"].notna()
        a = float(ex[m & near].mean()) if int((m & near).sum()) else np.nan
        bb = float(ex[m & ~near].mean()) if int((m & ~near).sum()) else np.nan
        ratios[e] = a / bb if bb else np.nan
        P(f"    radius +-{e}: near-roll rate {a:.4%}  (n {int((m&near).sum()):,})   "
          f"far rate {bb:.4%}   ratio {ratios[e]:.3f}   gate <= {EMBARGO_RATIO}")
    E = 0 if ratios[1] <= EMBARGO_RATIO else (1 if ratios[3] <= EMBARGO_RATIO
                                              else (3 if ratios[5] <= EMBARGO_RATIO else 5))
    P(f"    >>> ROLL EMBARGO ladder -> E = {E} sessions each side "
      f"(feature hygiene only; positions still roll and still pay real turnover)")
    res["embargo"] = dict(unconditional_extreme_rate=float(ex[vt["ZVOL"].notna()].mean()),
                          ratios={str(k): (None if not np.isfinite(v) else float(v))
                                  for k, v in ratios.items()}, E=int(E))

    # ---------------------------------------------------------------- STAGE 8  capability
    P("")
    P("--- STAGE 8  CAPABILITY GATES")
    pe = er[["root", "date", "eligible"]].copy()
    mg = vt.merge(pe, on=["root", "date"], how="left")
    mg["eligible"] = mg["eligible"].fillna(False)
    if E > 0:
        mg["vol_usable"] = mg["vol_usable"] & (mg["roll_dist"] > E)
    mg["admit"] = mg["eligible"] & mg["vol_usable"]
    cov = []
    for r, g in mg.groupby("root"):
        pdays = int(g["eligible"].sum())
        vdays = int(g["admit"].sum())
        cov.append(dict(root=r, sector=N.SECTOR[r], price_eligible_days=pdays,
                        volume_eligible_days=vdays,
                        coverage=(vdays / pdays) if pdays else np.nan,
                        zero_vol_days=int((g["vol"] == 0).sum()),
                        first=str(g.loc[g["admit"], "date"].min())[:10] if vdays else "-",
                        last=str(g.loc[g["admit"], "date"].max())[:10] if vdays else "-"))
    cv = pd.DataFrame(cov)
    cv["G4"] = cv["volume_eligible_days"] >= G4_MIN_ROOT_DAYS
    cv["G5"] = cv["coverage"] >= G5_MIN_COVERAGE
    cv["ADMITTED"] = cv["G4"] & cv["G5"]
    cv.to_csv(os.path.join(OUT, "coverage.csv"), index=False)
    P(f"      {'root':<5}{'sector':<14}{'price days':>11}{'vol days':>10}{'coverage':>10}"
      f"{'zero-vol':>10}  {'first':<11}{'last':<11} admit")
    for _, a in cv.iterrows():
        P(f"      {a['root']:<5}{a['sector']:<14}{a['price_eligible_days']:>11,}"
          f"{a['volume_eligible_days']:>10,}{a['coverage']:>10.2%}{a['zero_vol_days']:>10,}  "
          f"{a['first']:<11}{a['last']:<11} {'YES' if a['ADMITTED'] else 'NO'}")
    adm = cv[cv["ADMITTED"]]
    admitted_roots, admitted_sectors = list(adm["root"]), sorted(set(adm["sector"]))
    yrs = sorted(set(mg.loc[mg["admit"] & mg["root"].isin(admitted_roots), "date"].dt.year))
    G = {"G1 eligible non-micro roots >= 12": (len(admitted_roots), len(admitted_roots) >= G1_MIN_ROOTS),
         "G2 distinct sectors >= 4": (len(admitted_sectors), len(admitted_sectors) >= G2_MIN_SECTORS),
         "G3 usable calendar years >= 8": (len(yrs), len(yrs) >= G3_MIN_YEARS),
         "G4 >= 1500 eligible root-days per admitted root":
             (int(adm["volume_eligible_days"].min()) if len(adm) else 0, bool(adm["G4"].all()) and len(adm) > 0),
         "G5 >= 80% coverage vs price days":
             (f"{adm['coverage'].min():.2%}" if len(adm) else "-", bool(adm["G5"].all()) and len(adm) > 0),
         "G6 no unresolved volume-semantics defect": ("see V1-V5", None),
         "G7 no causal-roll defect": ("asserted", causal_ok)}
    v_pass = [res["V2"]["PASS"], res["V3"]["PASS"], res["V4"]["PASS"], res["V5"]["PASS"]]
    v1s = res["V1"].get("status")
    v1_blocking_fail = (v1s == "MEASURED" and not res["V1"].get("PASS"))
    G["G6 no unresolved volume-semantics defect"] = (
        f"V1 {v1s}, V2/V3/V4/V5 {'all PASS' if all(v_pass) else 'FAIL'}",
        bool(all(v_pass)) and not v1_blocking_fail)
    P("")
    P(f"    {'GATE':<52}{'OBSERVED':>22}   VERDICT")
    for k, (o, ok) in G.items():
        P(f"    {k:<52}{str(o):>22}   {'PASS' if ok else '*** FAIL ***'}")
    res["capability"] = {k: dict(observed=str(o), passed=bool(ok)) for k, (o, ok) in G.items()}
    res["admitted_roots"] = admitted_roots
    res["admitted_sectors"] = admitted_sectors
    res["years"] = [int(y) for y in yrs]

    # ---------------------------------------------------------------- STAGE 9  verdict
    P("")
    P("=" * 112)
    struct_ok = all(v_pass) and causal_ok
    if not struct_ok or v1_blocking_fail:
        verdict = "VOLUME SEMANTICS NOT CERTIFIED"
    elif not all(ok for _, ok in G.values()):
        verdict = "CLOSED-BY-DATA"
    elif v1s == "MEASURED":
        verdict = "DATA-CAPABLE / CROSS-SOURCE VERIFIED"
    else:
        verdict = "DATA-CAPABLE / CONTRACT-SPECIFIC BY STRUCTURE, NOT CROSS-SOURCE VERIFIED"
    P(f"=== VOLUME00 VERDICT: {verdict}")
    P("=" * 112)
    P(f"    adopted representation   {REPRESENTATION}")
    P(f"    roll embargo E           {E}")
    P(f"    admitted roots           {len(admitted_roots)}  {admitted_roots}")
    P(f"    admitted sectors         {len(admitted_sectors)}  {admitted_sectors}")
    P(f"    usable calendar years    {len(yrs)}  {yrs[0]}-{yrs[-1]}" if yrs else "")
    P("    NO RETURN, NO P&L, NO SIGNAL, NO MODEL WAS COMPUTED IN THIS RUN.")
    res["verdict"] = verdict
    res["representation"] = REPRESENTATION
    res["E"] = int(E)
    json.dump(res, open(os.path.join(OUT, "volume00.json"), "w", encoding="utf-8"),
              indent=2, default=str)
    # the adopted volume substrate, for VOLUME_LIQUIDITY_V1 (no returns joined here)
    mg[["root", "sector", "date", "vol", "roll_dist", "vol_usable", "eligible", "admit",
        "LV", "ZVOL"]].to_parquet(os.path.join(OUT, "volume_substrate.parquet"), index=False)
    _fh.close()


if __name__ == "__main__":
    main()
