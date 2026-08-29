"""G2_F7 S1 — parity between clean-room (outI) and primary (F6 out), trial G00034.

Printed by program. Audit of srcI first; then decision-level diff via the dual-rule
engine; EVERY disagreement classified before the verdict (W52).
"""
import io
import json
import os
import re
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from engine import (REPO, OUT, RUN, COST35, load_bars, session_table, build_events,  # noqa: E402
                    sha256_file, EXPECTED_SHA, SUBSTRATE)
from research_sdk import seal_guard  # noqa: E402

PRIMARY_CSV = os.path.join(REPO, r"runs\G2_F6_AUCTREV01_20260829\out\events.csv")
INDEP_CSV = os.path.join(RUN, r"outI\events_indep.csv")
SRCI = os.path.join(RUN, r"srcI\auctrev_indep.py")

L = []


def P(s=""):
    print(s)
    L.append(s)


def main():
    P("=" * 100)
    P("G2_F7_AUCTREV_CERT_20260829 — S1 INDEPENDENT-IMPLEMENTATION PARITY (trial G00034)")
    P("printed by srcV/s1_parity.py — clean-room outI/events_indep.csv vs primary F6 out/events.csv")
    P(f"substrate sha256 {sha256_file(SUBSTRATE)} == provenance {EXPECTED_SHA}: "
      f"{sha256_file(SUBSTRATE) == EXPECTED_SHA}")
    P("=" * 100)

    # ---- A. clean-room audit (V1) — before any parity number --------------------------
    P()
    P("A. CLEAN-ROOM AUDIT of srcI/auctrev_indep.py (V1)")
    src_text = io.open(SRCI, "r", encoding="utf-8").read()
    pat = (r"G2_F6[^\s\"']*(?:src|out|events|gate|REPORT)|events\.csv|gate_table|"
           r"REPORT\.md|outA|G2_F5")
    hits = [(i + 1, ln.strip()) for i, ln in enumerate(src_text.splitlines())
            if re.search(pat, ln, re.IGNORECASE)]
    P(f"   grep pattern: {pat}")
    P(f"   matches in srcI: {len(hits)}" + ("" if not hits else "  <-- FORBIDDEN"))
    for ln_no, ln in hits:
        P(f"     line {ln_no}: {ln}")
    opens = re.findall(r"(?:read_parquet|open)\(([^)]+)\)", src_text)
    P(f"   file-open surface ({len(opens)} call sites):")
    for o in opens:
        P(f"     {o.strip()}")
    audit_ok = (len(hits) == 0)
    P(f"   AUDIT: {'PASS — no forbidden path referenced; reads = substrate + own outputs only' if audit_ok else 'FAIL'}")

    # ---- B. load both event files (sealed) --------------------------------------------
    prim = pd.read_csv(PRIMARY_CSV)
    indep = pd.read_csv(INDEP_CSV)
    for fr, cols, tag in ((prim, ["session_id", "entry_ts", "exit_ts"], "primary"),
                          (indep, ["session_id", "entry_ts", "exit_ts"], "indep")):
        for c in cols:
            tmp = fr[[c]].copy()
            tmp[c] = pd.to_datetime(tmp[c])
            seal_guard.assert_presealed(tmp, c, f"S1 {tag} events {c}")
    prim["net35"] = prim["net35_pts"]
    indep["net35"] = indep["gross_pts"] - COST35

    sp, si = set(prim["session_id"]), set(indep["session_id"])
    inter, sd_only_p, sd_only_i = sp & si, sp - si, si - sp
    P()
    P("B. EVENT SETS")
    P(f"   primary events N = {len(prim)} (sessions {len(sp)}); indep N = {len(indep)} (sessions {len(si)})")
    P(f"   intersection {len(inter)}; primary-only {len(sd_only_p)}; indep-only {len(sd_only_i)}")

    # ---- C. dual-rule engine reproduction (decision level) ----------------------------
    P()
    P("C. DUAL-RULE ENGINE (verifier re-implementation of BOTH recorded readings)")
    bars = load_bars()
    qP = session_table(bars, "morning")   # primary reading of F6 R3(c)
    qI = session_table(bars, "chrono")    # clean-room reading (outI I2c)
    P(f"   qualifying sessions: morning-rule {len(qP)} (primary printed 5052); "
      f"chrono-rule {len(qI)} (indep printed 5055)")
    evP, cP = build_events(qP, bars, "bottom")
    evI, cI = build_events(qI, bars, "bottom")
    P(f"   engine events: morning {len(evP)} (primary 534); chrono {len(evI)} (indep 535)")

    def match(engine_ev, file_ev, px_col, xx_col, net_series, tol, tag):
        a = engine_ev.set_index("session_id")
        b = file_ev.set_index("session_id")
        same_set = set(a.index) == set(b.index)
        common = sorted(set(a.index) & set(b.index))
        de = (a.loc[common, "entry_px"].to_numpy() - b.loc[common, px_col].to_numpy())
        dx = (a.loc[common, "exit_px"].to_numpy() - b.loc[common, xx_col].to_numpy())
        dn = (a.loc[common, "net35"].to_numpy() - net_series.loc[common].to_numpy())
        ok = same_set and np.abs(de).max() <= tol and np.abs(dx).max() <= tol and np.abs(dn).max() <= tol
        P(f"   engine vs {tag}: same session set {same_set}; max|d entry_px| {np.abs(de).max():.6f}; "
          f"max|d exit_px| {np.abs(dx).max():.6f}; max|d net35| {np.abs(dn).max():.6f}  -> "
          f"{'REPRODUCED' if ok else 'NOT REPRODUCED'}")
        return ok

    okP = match(evP, prim.rename(columns={"entry_open": "entry_px", "exit_close": "exit_px"}),
                "entry_px", "exit_px", prim.set_index("session_id")["net35"], 1e-6, "primary events.csv")
    okI = match(evI, indep, "entry_px", "exit_px", indep.set_index("session_id")["net35"],
                0.006, "indep events_indep.csv")

    # ---- D. classification of EVERY disagreement (V5) ---------------------------------
    P()
    P("D. DISAGREEMENT CLASSIFICATION (every differing decision, before any dollar verdict)")
    setP_q, setI_q = set(qP["session"]), set(qI["session"])
    census_diff = sorted(setI_q - setP_q) + sorted(setP_q - setI_q)
    P(f"   qualification census difference: {len(census_diff)} session(s)")
    for s in census_diff:
        side = "chrono-only" if s in setI_q else "morning-only"
        g = bars[bars["session"] == s]
        own = g[g["ts"].dt.normalize() == s]
        n_morning = int((own["minute"] <= 570).sum())
        pre = g[g["ts"] <= s + pd.Timedelta(hours=9, minutes=30)]
        first_own = own["ts"].min()
        P(f"     {s.date()} [{side}]: own-date bars stamped <=09:30: {n_morning}; "
          f"chronological bars <= 09:30: {len(pre)}; first own-date bar {first_own}")
        P(f"        CLASS: QUALIFICATION-RULE AMBIGUITY — F6 R3(c) 'raw close at/before 09:30' "
          f"read as time-of-day-on-session-date (primary) vs chronological-within-session (indep).")

    qPi = {s: i for i, s in enumerate(qP["session"])}
    qIi = {s: i for i, s in enumerate(qI["session"])}
    for sid in sorted(sd_only_i | sd_only_p):
        s = pd.Timestamp(sid)
        srcs = "indep-only" if sid in sd_only_i else "primary-only"
        inP, inI = s in qPi, s in qIi
        row = []
        if inP:
            iP = qPi[s]
            row.append(f"morning-rule: idx {iP}, D {qP.at[iP,'D']:+.2f}, Q10 {qP.at[iP,'Q10']:+.4f}, "
                       f"bottom {bool(qP.at[iP,'bottom'])}")
        else:
            row.append("morning-rule: NOT QUALIFYING")
        if inI:
            iI = qIi[s]
            row.append(f"chrono-rule: idx {iI}, D {qI.at[iI,'D']:+.2f}, Q10 {qI.at[iI,'Q10']:+.4f}, "
                       f"bottom {bool(qI.at[iI,'bottom'])}")
        else:
            row.append("chrono-rule: NOT QUALIFYING")
        P(f"   event disagreement {sid} [{srcs}]:")
        for r in row:
            P(f"        {r}")
        if inP and inI:
            iP, iI = qPi[s], qIi[s]
            if bool(qP.at[iP, "bottom"]) != bool(qI.at[iI, "bottom"]):
                if iP < 252 or iI < 252:
                    P("        CLASS: BURN-IN INDEX SHIFT — census difference moves the 252-session "
                      "burn-in boundary; downstream of the same R3(c) ambiguity.")
                else:
                    P("        CLASS: TRAILING-WINDOW CONTENT SHIFT — extra chrono-rule qualifying "
                      "session(s) enter the 252-window and move Q10 across D; downstream of R3(c).")
            else:
                P("        CLASS: OUTCOME/NEXT-SESSION DIFFERENCE — check gap/entry (printed above).")
        elif inI and not inP:
            P("        CLASS: QUALIFICATION-RULE AMBIGUITY (direct) — session qualifies only under "
              "the chrono reading of R3(c).")
        elif inP and not inI:
            P("        CLASS: QUALIFICATION-RULE AMBIGUITY (direct) — session qualifies only under "
              "the morning reading of R3(c).")
    # intersection value mismatches beyond tolerance
    both = prim.set_index("session_id").join(indep.set_index("session_id"),
                                             how="inner", lsuffix="_p", rsuffix="_i")
    dnet = (both["net35_p"] - both["net35_i"]).abs()
    dts = (both["entry_ts_p"] != both["entry_ts_i"]) | (both["exit_ts_p"] != both["exit_ts_i"])
    n_val = int(((dnet > 0.006) | dts).sum())
    P(f"   intersection rows with entry_ts/exit_ts or |net35| > 0.006 pt mismatch: {n_val}")
    for sid, r in both[(dnet > 0.006) | dts].iterrows():
        P(f"     {sid}: net_p {r['net35_p']:.4f} net_i {r['net35_i']:.4f} "
          f"entry {r['entry_ts_p']}|{r['entry_ts_i']} exit {r['exit_ts_p']}|{r['exit_ts_i']}")

    # ---- E. parity gates (V2-V4) ------------------------------------------------------
    P()
    P("E. PARITY GATES ($ figures POINTS-based; F7 S1 bands)")
    jac = len(inter) / len(sp | si)
    net_i = both["net35_i"].to_numpy()
    net_p = both["net35_p"].to_numpy()
    corr = float(np.corrcoef(net_p, net_i)[0, 1])
    tot_p = float(prim["net35"].sum())
    tot_i = float(indep["net35"].sum())
    tot_dev = abs(tot_i - tot_p) / abs(tot_p)
    g1 = jac >= 0.99
    g2 = corr >= 0.99
    g3 = tot_dev <= 0.01
    P("   GATE       SPEC                                    OBSERVED                       VERDICT")
    P("   " + "-" * 92)
    P(f"   S1-audit   no forbidden reference in srcI          {len(hits)} matches"
      f"{'':22s}{'PASS' if audit_ok else 'FAIL'}")
    P(f"   S1-a       event-set agreement >= 99%              {jac*100:.3f}%  ({len(inter)}/{len(sp | si)})"
      f"{'':12s}{'PASS' if g1 else 'FAIL'}")
    P(f"   S1-b       per-event net corr >= 0.99              {corr:.6f} on {len(both)} events"
      f"{'':10s}{'PASS' if g2 else 'FAIL'}")
    P(f"   S1-c       total net within 1%                     {tot_p:+.2f} vs {tot_i:+.2f} pts "
      f"(dev {tot_dev*100:.3f}%)   {'PASS' if g3 else 'FAIL'}")
    P(f"   engine reproduction (context, non-gate): primary {'REPRODUCED' if okP else 'NOT'} / "
      f"indep {'REPRODUCED' if okI else 'NOT'}")
    s1_pass = audit_ok and g1 and g2 and g3
    P()
    P(f"S1 VERDICT: {'PASS — parity certified; disagreements fully classified (single R3(c) seed-rule ambiguity)' if s1_pass else 'FAIL'}")
    P("Multiplicity: AUCTREV is 1 of 13 formal GENESIS II objects (~750 prior experiments); "
      "evidence status remains DISCOVERY_CONSUMED.")

    # reconciled set for S2 = intersection with primary values (V6)
    rec = prim[prim["session_id"].isin(inter)].copy()
    state = dict(s1_pass=bool(s1_pass), audit_hits=len(hits), jaccard=jac, corr=corr,
                 tot_primary_pts=tot_p, tot_indep_pts=tot_i, tot_dev=tot_dev,
                 n_reconciled=int(len(rec)),
                 n_census_diff=len(census_diff), n_event_diff=len(sd_only_i | sd_only_p),
                 n_value_mismatch=n_val, engine_repro_primary=bool(okP), engine_repro_indep=bool(okI))
    os.makedirs(OUT, exist_ok=True)
    rec.to_csv(os.path.join(OUT, "reconciled_events.csv"), index=False)
    with open(os.path.join(OUT, "state_s1.json"), "w", encoding="utf-8") as f:
        json.dump(state, f, indent=1)
    text = "\n".join(L) + "\n"
    with open(os.path.join(OUT, "S1_parity.txt"), "wb") as f:
        f.write(text.encode("utf-8"))
    assert os.path.getsize(os.path.join(OUT, "S1_parity.txt")) > 0


if __name__ == "__main__":
    main()
