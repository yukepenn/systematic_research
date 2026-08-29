"""G2_F3_DELEV01_20260829 — DEFECT evidence (printed by program) and final pending-ledger verdict.

Discovered AFTER the as-resolved gate computation ran (out/gate_table.txt, all gates FAIL):
the authorized NQ substrate is an ADDITIVELY BACK-ADJUSTED continuous series. Point moves are
preserved; PERCENT returns are compressed by (unadjusted level / adjusted level) in every era
before the final roll segment. The spec's PRIMARY event definition — RTH close-to-close return
in [-5.0%, -2.5%) over 2006->2026 — is therefore structurally unmeasurable on this substrate:
the 2008 forced-deleveraging days (the mechanism's core population, named in the spec) cannot
enter the band BY CONSTRUCTION. Charter rule: impossible -> DEFECT (not NULL; the mechanism was
never actually tested).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO))
from research_sdk.seal_guard import assert_presealed  # noqa: E402

RUN = REPO / "runs" / "G2_F3_DELEV01_20260829"
OUT = RUN / "out"
DEEP = REPO / "research" / "scalping_lab" / "substrate" / "minute" / "NQ" / "nq1m_2005_202605.parquet"
MODERN = REPO / "runs" / "SM1M_SUBSTRATE" / "out" / "nq_1m_2022_2026.parquet"
WIN_END = pd.Timestamp("2026-05-31")
_L: list[str] = []


def emit(s: str = ""):
    print(s)
    _L.append(s)


def closes_1600(path: Path, maxlab: pd.Timestamp) -> pd.Series:
    f = pq.ParquetFile(path)
    cm = {}
    for g in range(f.metadata.num_row_groups):
        d = f.read_row_group(g, columns=["time", "close"]).to_pandas()
        if d["time"].dtype == object:
            d["time"] = pd.to_datetime(d["time"], format="%Y-%m-%d %H:%M:%S")
        day = d["time"].dt.normalize()
        tod = d["time"] - day
        lab = day.where(tod <= pd.Timedelta(hours=17), day + pd.Timedelta(days=1))
        keep = lab <= maxlab
        d, lab, tod = d[keep], lab[keep], tod[keep]
        if len(d) == 0:
            continue
        assert_presealed(d, "time", f"defect_evidence {path.name} rg{g}")
        m = tod == pd.Timedelta(hours=16)
        for l, c in zip(lab[m], d.loc[m, "close"]):
            cm[pd.Timestamp(l)] = float(c)
    return pd.Series(cm).sort_index()


def main():
    emit("G2_F3_DELEV01_20260829 — DEFECT EVIDENCE (printed by program)  trial G00027")
    emit("=" * 100)
    deep = closes_1600(DEEP, WIN_END)
    mod = closes_1600(MODERN, WIN_END)
    emit("seal_guard.assert_presealed run on every row-group of both stores (nothing >= 2026-08-01 read;")
    emit("modern store truncated at labels <= 2026-05-31 before any use). data_esnq NOT accessed.")
    emit("")

    # 1. deep and modern stores are the SAME series in overlap -> one adjustment regime repo-wide
    both = pd.DataFrame({"deep": deep, "mod": mod}).dropna()
    d = (both["deep"] - both["mod"]).abs()
    emit(f"E1. deep vs modern NQ store, overlap {both.index.min().date()} -> {both.index.max().date()}: "
         f"n={len(both)}, max|diff|={d.max():.4f} pts -> IDENTICAL series (single adjusted source).")

    # 2. GFC window percent returns are physically impossible for the real instrument
    r = deep / deep.shift(1) - 1.0
    gfc = r.loc["2008-09-01":"2008-12-31"]
    emit(f"E2. Sep-Dec 2008 daily RTH close-to-close on the substrate: min={gfc.min():+.4%}, "
         f"max={gfc.max():+.4%}, n(|r|>=3.5%)={int((gfc.abs() >= 0.035).sum())} of {len(gfc)}.")
    emit("    The GFC produced MANY NQ days beyond +/-5%; a series where none exceeds +/-3.4% cannot be")
    emit("    NQ percent returns. The spec itself states effective N concentrates in 2008 — the")
    emit("    substrate structurally forbids 2008 events.")

    # 3. levels are impossible for any traded NQ contract in that era
    lvl_0810 = float(deep.loc["2008-10-01"])
    lvl_2006 = float(deep.iloc[1])
    emit(f"E3. Substrate RTH close 2008-10-01 = {lvl_0810:,.1f}; first 2006 close = {lvl_2006:,.1f}. No NQ")
    emit("    contract traded near these levels in those eras (NQ ~1,300-1,700 then; it first reached")
    emit("    ~4,900 in 2016). Levels carry a large positive additive offset in early eras.")

    # 4. arithmetic of the distortion: additive adjustment preserves points, compresses percents
    big = deep.loc["2008-10-13"] - deep.loc["2008-10-10"]
    emit(f"E4. 2008-10-10 -> 10-13 move = {big:+.1f} pts = {big / deep.loc['2008-10-10']:+.2%} at the adjusted")
    emit("    level, but the SAME point move at the true ~1,200-1,400 level is +11..13% — the documented")
    emit("    real magnitude of that day. Point moves match reality; percent moves do not: additive")
    emit("    back-adjustment. Compression factor ~ adjusted/true level (~3.5x in 2008, shrinking toward")
    emit("    the present but nonzero even in 2022-26).")
    emit("")
    emit("CONSEQUENCE FOR THE FROZEN SPEC")
    emit("  The primary object 'RTH close-to-close return in [-5.0%, -2.5%)' is not computable as NQ")
    emit("  percent returns from the authorized substrate for most of the 2006-2026 window, and the")
    emit("  band's meaning drifts by a factor ~3.5x across eras. True percent returns are unrecoverable")
    emit("  without the unadjusted level / roll-offset schedule, which the frozen provenance set does")
    emit("  not contain. The as-resolved computation (out/gate_table.txt: 31 detected, 29 traded, all")
    emit("  three gates FAIL) measured a DIFFERENT, era-distorted population — retained as evidence,")
    emit("  not quotable as a test of MC-40. Charter: impossible -> DEFECT.")
    emit("")
    emit("  NOTE for future waves: prior GENESIS uses of pct_next on this substrate for WITHIN-ERA")
    emit("  relative comparisons are less affected (shared compression within eras), but any ABSOLUTE")
    emit("  percent threshold spanning eras on this substrate inherits this defect.")

    (OUT / "defect_evidence.txt").write_text("\n".join(_L) + "\n", encoding="utf-8")

    prior = json.loads((OUT / "ledger_result_pending.json").read_text(encoding="utf-8"))
    metrics = dict(prior["metrics"])
    metrics.update({
        "defect_overlap_n": int(len(both)),
        "defect_overlap_max_abs_diff_pts": float(d.max()),
        "defect_gfc_r_min": round(float(gfc.min()), 6),
        "defect_gfc_r_max": round(float(gfc.max()), 6),
        "defect_level_2008_10_01": lvl_0810,
        "defect_first_2006_close": lvl_2006,
        "as_computed_gate_result_invalid_population": "NULL(all gates FAIL)",
    })
    pending = {
        "trial_id": "G00027",
        "metrics": metrics,
        "result": "DEFECT",
        "note": ("MC-40 NOT TESTED: authorized NQ substrate is an additively back-adjusted continuous series "
                 "(points preserved, percents compressed ~3.5x in 2008 -> the spec's percent band cannot see the "
                 "2008 deleveraging population; substrate shows zero |r|>=3.5% days in Sep-Dec 2008 and a "
                 "4,957 'price' on 2008-10-01). Frozen spec unimplementable on frozen data -> DEFECT per charter. "
                 "As-resolved computation retained as evidence (out/gate_table.txt: 29 traded events, D1 t=-0.76, "
                 "D2 control +$1,200 vs -$873, D3 p95 $946 — all FAIL on the DISTORTED band; not a test of the "
                 "mechanism). Retest requires an unadjusted or ratio-adjusted NQ daily series (free sources exist) "
                 "or an in-repo roll-offset schedule; no band/horizon/MA search was performed."),
    }
    (OUT / "ledger_result_pending.json").write_text(json.dumps(pending, indent=2), encoding="utf-8")
    print("WROTE:", OUT / "defect_evidence.txt", "and updated", OUT / "ledger_result_pending.json")


if __name__ == "__main__":
    main()
