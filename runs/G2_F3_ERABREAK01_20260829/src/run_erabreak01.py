"""G2_F3_ERABREAK01_20260829 — trial G00024, card MC-54 leg 1.

Era break test at 2022-05: minute-of-session RV profile (RTH, per-session normalized)
and last-30-minute RV share, 2016-2019 vs 2023-2026-05-31, against a shared
circular-shift null of era labels (all N-1 whole-session rotations, >= 300).

All constants fixed in out/spec_resolutions.txt BEFORE computation. No parameter search.
"""
from __future__ import annotations

import hashlib
import io
import json
import os
import sys
from datetime import date

import numpy as np
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, ROOT)

from research_sdk.seal_guard import assert_presealed, truncate_presealed  # noqa: E402
from research_sdk.session_boundary import assert_not_locked_forward  # noqa: E402

RUN = os.path.join(ROOT, "runs", "G2_F3_ERABREAK01_20260829")
OUT = os.path.join(RUN, "out")

DEEP = os.path.join(ROOT, r"research\scalping_lab\substrate\minute\NQ\nq1m_2005_202605.parquet")
MODERN = os.path.join(ROOT, r"runs\SM1M_SUBSTRATE\out\nq_1m_2022_2026.parquet")
# expected SHA256 per runs\GENESIS_REPRO_INCUMBENT_20260828\out\run_provenance.txt
EXP_SHA = {
    DEEP: "dfd017eff0b031c2be89639fc4ad347d45053867edcdc2600002252b10b627cf",
    MODERN: "87aa53f007aa47b9ee10d0080317a3cde8d22b55aa368267fa9a4aed7435295d",
}

ERA_A = (date(2016, 1, 1), date(2019, 12, 31))     # pre-0DTE
ERA_B = (date(2023, 1, 1), date(2026, 5, 31))      # 0DTE era (2026-06+ burned-excluded)

MOD_OPEN = 9 * 60 + 30    # 570: 09:30 end-stamp, loaded ONLY as prior close for 09:31
MOD_LO = 9 * 60 + 31      # 571: first RTH bucket (covers 09:30-09:31)
MOD_HI = 16 * 60          # 960: last RTH bucket  (covers 15:59-16:00)
NB = MOD_HI - MOD_LO + 1  # 390 buckets
L30_LO = 15 * 60 + 31     # 931: last-30-min window end-stamps 15:31..16:00
MIN_VALID = 370           # session completeness (R5, fixed pre-compute)
MIN_SHIFTS = 300


def sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_era(path: str, first: date, last: date, ctx: str, parse_str: bool):
    """Load NQ 1-min close series through seal_guard, return per-session r^2 bucket matrix."""
    df = pd.read_parquet(path, columns=["time", "close"])
    if parse_str:
        df["time"] = pd.to_datetime(df["time"], format="%Y-%m-%d %H:%M:%S")
    df, n_dropped = truncate_presealed(df, "time", ctx)
    assert_presealed(df, "time", ctx + ":post-truncate")
    print(f"seal_guard PASS [{ctx}]: {n_dropped} sealed row(s) mechanically dropped, frame certified pre-seal")
    assert_not_locked_forward(last)
    t = df["time"]
    sess = t.dt.date.where(t.dt.hour < 18, (t + pd.Timedelta(days=1)).dt.date)
    df["session"] = sess
    df = df[(df["session"] >= first) & (df["session"] <= last)]
    mod = df["time"].dt.hour * 60 + df["time"].dt.minute
    df = df[(mod >= MOD_OPEN) & (mod <= MOD_HI)].copy()
    df = df.sort_values("time", kind="stable").reset_index(drop=True)
    dup = df.duplicated(subset=["time"]).sum()
    if dup:
        raise RuntimeError(f"DEFECT [{ctx}]: {dup} duplicate bar stamps")
    # 1-min log return: same session, gap exactly 60s (R3)
    lc = np.log(df["close"].to_numpy())
    r = np.diff(lc, prepend=np.nan)
    same = df["session"].to_numpy()
    same_prev = np.empty(len(df), dtype=bool)
    same_prev[0] = False
    same_prev[1:] = same[1:] == same[:-1]
    gap_s = df["time"].diff().dt.total_seconds().to_numpy()
    exact = gap_s == 60.0
    modv = (df["time"].dt.hour * 60 + df["time"].dt.minute).to_numpy()
    in_bucket = (modv >= MOD_LO) & (modv <= MOD_HI)
    keep = in_bucket & same_prev & exact
    n_gap_dropped = int((in_bucket & same_prev & ~exact).sum())
    n_first = int((in_bucket & ~same_prev).sum())
    sub = pd.DataFrame({"session": df["session"].to_numpy()[keep],
                        "mod": modv[keep],
                        "r2": r[keep] ** 2})
    mat = sub.pivot(index="session", columns="mod", values="r2")
    mat = mat.reindex(columns=range(MOD_LO, MOD_HI + 1))
    valid = mat.notna().sum(axis=1)
    tot = mat.sum(axis=1, skipna=True)
    keep_sess = (valid >= MIN_VALID) & (tot > 0)
    n_excl = int((~keep_sess).sum())
    mat = mat.loc[keep_sess]
    prof = mat.div(mat.sum(axis=1, skipna=True), axis=0)  # per-session normalization (R4)
    info = {
        "ctx": ctx, "n_sessions": len(prof), "n_excluded_incomplete": n_excl,
        "n_gap_dropped_returns": n_gap_dropped, "n_no_prior_close": n_first,
        "first_session": str(prof.index.min()), "last_session": str(prof.index.max()),
        "median_valid_buckets": float(valid[keep_sess].median()) if len(prof) else float("nan"),
    }
    return prof, info


def group_stats(sum_blk, cnt_blk, tot_sum, tot_cnt):
    """meanA, meanB per bucket for arrays shaped (K, NB); returns L1, |dShare|, S arrays."""
    cnt_b = tot_cnt - cnt_blk
    sum_b = tot_sum - sum_blk
    mA = np.where(cnt_blk > 0, sum_blk / np.maximum(cnt_blk, 1), 0.0)
    mB = np.where(cnt_b > 0, sum_b / np.maximum(cnt_b, 1), 0.0)
    l1 = np.abs(mA - mB).sum(axis=1)
    i30 = L30_LO - MOD_LO
    shA = mA[:, i30:].sum(axis=1) / mA.sum(axis=1)
    shB = mB[:, i30:].sum(axis=1) / mB.sum(axis=1)
    dsh = np.abs(shB - shA)
    return l1, dsh, l1 + dsh, (shA, shB)


def main():
    os.makedirs(OUT, exist_ok=True)
    buf = io.StringIO()

    def p(line=""):
        print(line)
        buf.write(line + "\n")

    p("G2_F3_ERABREAK01_20260829 — GATE TABLE (printed by program)")
    p(f"trial G00024 | card MC-54 leg 1 | python {sys.version.split()[0]} numpy {np.__version__} pandas {pd.__version__}")
    p("")
    p("[provenance] input hashes vs runs\\GENESIS_REPRO_INCUMBENT_20260828\\out\\run_provenance.txt")
    hash_ok = True
    for path in (DEEP, MODERN):
        h = sha256(path)
        ok = h == EXP_SHA[path]
        hash_ok &= ok
        p(f"  {'MATCH   ' if ok else 'MISMATCH'} {h}  {os.path.relpath(path, ROOT)}")
    p("[seal] every load below passes research_sdk.seal_guard (counts printed); window end <= LOCKED_FORWARD")
    p("[data_esnq enforcement] 0 reads — data_esnq tick stores NOT touched (NQ 1-min only per spec);")
    p("  ALLOWLIST_DEV_44 has no applicable access this run. Blind pools untouched. Spend $0.")
    p("")

    profA, infoA = load_era(DEEP, *ERA_A, ctx="eraA_deep_2016_2019", parse_str=True)
    profB, infoB = load_era(MODERN, *ERA_B, ctx="eraB_modern_2023_202605", parse_str=False)
    for info in (infoA, infoB):
        p(f"[load {info['ctx']}] sessions kept={info['n_sessions']} "
          f"(excluded incomplete/half-day={info['n_excluded_incomplete']}), "
          f"range {info['first_session']}..{info['last_session']}, "
          f"gap-dropped returns={info['n_gap_dropped_returns']}, "
          f"no-prior-close 09:31 losses={info['n_no_prior_close']}, "
          f"median valid buckets={info['median_valid_buckets']:.0f}/390")

    nA, nB = len(profA), len(profB)
    X = np.vstack([profA.to_numpy(), profB.to_numpy()])  # chronological within each block
    N = nA + nB
    V = np.nan_to_num(X, nan=0.0)
    C = (~np.isnan(X)).astype(np.float64)
    tot_sum, tot_cnt = V.sum(axis=0), C.sum(axis=0)
    PV = np.vstack([np.zeros((1, NB)), np.cumsum(np.vstack([V, V]), axis=0)])
    PC = np.vstack([np.zeros((1, NB)), np.cumsum(np.vstack([C, C]), axis=0)])
    ks = np.arange(N)  # k=0 real, k=1..N-1 null
    sum_blk = PV[ks + nA] - PV[ks]
    cnt_blk = PC[ks + nA] - PC[ks]
    l1, dsh, S, _ = group_stats(sum_blk, cnt_blk, tot_sum, tot_cnt)
    l1_real, dsh_real, S_real = l1[0], dsh[0], S[0]
    l1_null, dsh_null, S_null = l1[1:], dsh[1:], S[1:]
    n_shifts = N - 1

    # real-era shares & profiles for outputs
    _, _, _, (shA_r, shB_r) = group_stats(sum_blk[:1], cnt_blk[:1], tot_sum, tot_cnt)
    mA = np.where(cnt_blk[0] > 0, sum_blk[0] / np.maximum(cnt_blk[0], 1), 0.0)
    mB_cnt = tot_cnt - cnt_blk[0]
    mB = np.where(mB_cnt > 0, (tot_sum - sum_blk[0]) / np.maximum(mB_cnt, 1), 0.0)

    mins = np.arange(MOD_LO, MOD_HI + 1)
    pd.DataFrame({
        "minute_end_stamp": [f"{m // 60:02d}:{m % 60:02d}" for m in mins],
        "minute_of_day": mins,
        "profile_2016_2019": mA,
        "profile_2023_202605": mB,
        "abs_diff": np.abs(mA - mB),
        "n_sessions_A": cnt_blk[0].astype(int),
        "n_sessions_B": mB_cnt.astype(int),
    }).to_csv(os.path.join(OUT, "profiles.csv"), index=False)

    p95_S = float(np.percentile(S_null, 95))
    p95_l1 = float(np.percentile(l1_null, 95))
    p95_dsh = float(np.percentile(dsh_null, 95))
    p_S = (1 + int((S_null >= S_real).sum())) / (1 + n_shifts)
    p_l1 = (1 + int((l1_null >= l1_real).sum())) / (1 + n_shifts)
    p_dsh = (1 + int((dsh_null >= dsh_real).sum())) / (1 + n_shifts)

    p("")
    p("[MDE / event counts — printed BEFORE verdicts]")
    p(f"  n_sessions era A (2016-2019)        : {nA}")
    p(f"  n_sessions era B (2023-2026-05-31)  : {nB}")
    p(f"  n buckets per session (RTH)         : {NB}")
    p(f"  n circular whole-session shifts     : {n_shifts} (spec >= {MIN_SHIFTS}; ALL non-zero rotations, no RNG)")
    p(f"  null p95 S  (= minimal detectable S at this gate) : {p95_S:.6f}")
    p(f"  null p95 L1 (diagnostic)                          : {p95_l1:.6f}")
    p(f"  null p95 |dShare| (diagnostic)                    : {p95_dsh:.6f}")
    p(f"  null S max / median : {float(S_null.max()):.6f} / {float(np.median(S_null)):.6f}")
    p("")
    p(f"  era A last-30-min RV share : {float(shA_r[0]):.6f}")
    p(f"  era B last-30-min RV share : {float(shB_r[0]):.6f}")
    p(f"  share difference (B - A)   : {float(shB_r[0] - shA_r[0]):+.6f}")
    p(f"  profile L1 distance        : {l1_real:.6f}")
    p(f"  break statistic S = L1 + |dShare| : {S_real:.6f}")
    p("")

    g1 = hash_ok
    g2 = n_shifts >= MIN_SHIFTS
    brk = bool(S_real > p95_S)
    rows = [
        ("G1 DATA/PROVENANCE", "both era loads seal-clean; SHA256 == provenance record", f"hash_match={hash_ok}, seal certified", "PASS" if g1 else "FAIL"),
        ("G2 NULL FAMILY", f">= {MIN_SHIFTS} whole-session circular shifts, shared across family", f"n_shifts={n_shifts}, shared shift set", "PASS" if g2 else "FAIL"),
        ("G3 BREAK (p95)", "BREAK iff S_real > p95(null S)", f"S={S_real:.6f} vs p95={p95_S:.6f} (p={p_S:.4f})", "BREAK" if brk else "NO-BREAK"),
        ("G3a L1 (diag)", "non-binding component vs shared null", f"L1={l1_real:.6f} vs p95={p95_l1:.6f} (p={p_l1:.4f})", "above" if l1_real > p95_l1 else "below"),
        ("G3b |dShare| (diag)", "non-binding component vs shared null", f"|dSh|={dsh_real:.6f} vs p95={p95_dsh:.6f} (p={p_dsh:.4f})", "above" if dsh_real > p95_dsh else "below"),
    ]
    p("GATE                 | SPEC                                                       | OBSERVED                                             | PASS-FAIL")
    p("-" * 150)
    for g, s, o, v in rows:
        p(f"{g:<20} | {s:<58} | {o:<52} | {v}")
    p("")

    if not (g1 and g2):
        verdict, content = "DEFECT", "MEASUREMENT_INVALID"
        p("VERDICT: DEFECT — measurement gates failed; no content verdict issued.")
    else:
        verdict = "PASS"
        content = "BREAK" if brk else "NO_BREAK"
        p(f"CONTENT VERDICT: {content}  (trial verdict: PASS — measurement completed; content is the deliverable)")
        if brk:
            p("")
            p("BINDING DOCTRINE LINE (per spec verdict_semantics):")
            p("  BREAK at 2022-05 is REAL: pre-2022 intraday-vol statistics are INADMISSIBLE priors")
            p("  for modern (2023+) work. Every MC-38/52/55/56-class vol card must train/anchor on")
            p("  the modern era only. [evidence: DISCOVERY_CONSUMED (era B) / LEGACY_DIAGNOSTIC (era A)]")
        else:
            p("")
            p("DOCTRINE LINE: NO-BREAK — deep pre-2022 history is ADMISSIBLE as an intraday-vol prior.")
        p("")
        p("legs 2-4: NOT run (contingent riders; leg 4 folklore permanently banned on MDE failure per card — recorded).")

    with open(os.path.join(OUT, "gate_table.txt"), "w", encoding="utf-8") as f:
        f.write(buf.getvalue())

    ledger = {
        "trial_id": "G00024",
        "metrics": {
            "era_A": "2016-01-01..2019-12-31 (deep substrate)",
            "era_B": "2023-01-01..2026-05-31 (modern substrate)",
            "n_sessions_A": nA, "n_sessions_B": nB,
            "n_excluded_A": infoA["n_excluded_incomplete"], "n_excluded_B": infoB["n_excluded_incomplete"],
            "profile_L1": round(float(l1_real), 6),
            "share_last30_A": round(float(shA_r[0]), 6),
            "share_last30_B": round(float(shB_r[0]), 6),
            "share_diff_B_minus_A": round(float(shB_r[0] - shA_r[0]), 6),
            "break_stat_S": round(float(S_real), 6),
            "null_p95_S": round(p95_S, 6),
            "null_p95_L1": round(p95_l1, 6),
            "null_p95_dshare": round(p95_dsh, 6),
            "p_S": round(p_S, 4), "p_L1": round(p_l1, 4), "p_dshare": round(p_dsh, 4),
            "n_shifts": n_shifts,
            "content_verdict": content,
            "evidence_status": "DISCOVERY_CONSUMED",
        },
        "result": verdict,
        "note": ("MC-54 leg 1 era-admissibility measurement. Content verdict "
                 f"{content}: " +
                 ("pre-2022 intraday-vol statistics are INADMISSIBLE priors for modern work (binding doctrine line printed in gate_table.txt)."
                  if content == "BREAK" else
                  ("deep history admissible as intraday-vol prior." if content == "NO_BREAK" else "measurement invalid.")) +
                 " Resolutions in out/spec_resolutions.txt; profiles in out/profiles.csv. Legs 2-4 not run; leg-4 folklore ban recorded."),
    }
    with open(os.path.join(OUT, "ledger_result_pending.json"), "w", encoding="utf-8") as f:
        json.dump(ledger, f, indent=2)
    print("wrote out/gate_table.txt, out/profiles.csv, out/ledger_result_pending.json")


if __name__ == "__main__":
    main()
