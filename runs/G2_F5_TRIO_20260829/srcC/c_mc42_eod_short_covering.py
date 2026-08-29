"""C_MC42_eod_short_covering — GENESIS II Formal Wave 5, trial G00031.

Frozen primary (runs/G2_F5_TRIO_20260829/spec.yaml, sub-run C): down-day
(09:30 open -> 15:30 close point return < 0) continuation coefficient
beta(15:30->16:00 return on 09:30->15:30 return), POINTS only (substrate law),
2023-26/05 with 20-session circular block-bootstrap 95% CI vs the 2006-15 point
estimate. Adopt-exit-rule clause fires ONLY if the CI excludes the 2006-15 point
AND the sign flips. Ambiguity resolutions: outC/spec_resolutions.txt (R1-R10).

Gate table is PRINTED BY THIS PROGRAM; event counts and MDE precede verdicts.
Single stochastic device: numpy default_rng(20260829), one shared draw.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from datetime import date

import numpy as np
import pandas as pd

REPO = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, REPO)
from research_sdk.seal_guard import assert_presealed  # noqa: E402

OUT = os.path.join(REPO, "runs", "G2_F5_TRIO_20260829", "outC")

DEEP = os.path.join(REPO, "research", "scalping_lab", "substrate", "minute", "NQ", "nq1m_2005_202605.parquet")
MODERN = os.path.join(REPO, "runs", "SM1M_SUBSTRATE", "out", "nq_1m_2022_2026.parquet")
EXPECTED_SHA = {
    DEEP: "dfd017eff0b031c2be89639fc4ad347d45053867edcdc2600002252b10b627cf",
    MODERN: "87aa53f007aa47b9ee10d0080317a3cde8d22b55aa368267fa9a4aed7435295d",
}

SEED = 20260829
BLOCK = 20
REPS = 2000
MIN_DOWN_PER_REP = 10

ERA_OLD = (date(2006, 1, 1), date(2015, 12, 31))
ERA_NEW = (date(2023, 1, 1), date(2026, 5, 31))


def sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 22), b""):
            h.update(chunk)
    return h.hexdigest()


def load_sessions(path: str, era: tuple[date, date], label: str) -> pd.DataFrame:
    """Return per-session frame: session_date, r_day, r_eod (POINTS). Strict anchors (R4)."""
    df = pd.read_parquet(path, columns=["time", "open", "close"])
    if df["time"].dtype == object:
        df["time"] = pd.to_datetime(df["time"], format="%Y-%m-%d %H:%M:%S")
        assert not df["time"].isna().any(), f"{label}: unparsed timestamps"
    assert_presealed(df, "time", f"C_MC42 load {label}")  # seal guard on the RAW load (R10)

    t = df["time"]
    hm = t.dt.hour * 100 + t.dt.minute
    rth = df[(hm >= 931) & (hm <= 1600)].copy()
    rth["session_date"] = rth["time"].dt.date  # RTH stamps: calendar date == session date (R4)
    rth = rth[(rth["session_date"] >= era[0]) & (rth["session_date"] <= era[1])]
    rth["hm"] = rth["time"].dt.hour * 100 + rth["time"].dt.minute

    piv_open = rth[rth["hm"] == 931].set_index("session_date")["open"]
    piv_1530 = rth[rth["hm"] == 1530].set_index("session_date")["close"]
    piv_1600 = rth[rth["hm"] == 1600].set_index("session_date")["close"]
    for name, s in [("0931", piv_open), ("1530", piv_1530), ("1600", piv_1600)]:
        assert s.index.is_unique, f"{label}: duplicate {name} anchor bars"

    all_dates = sorted(set(rth["session_date"]))
    ses = pd.DataFrame(index=pd.Index(all_dates, name="session_date"))
    ses["o0930"] = piv_open
    ses["c1530"] = piv_1530
    ses["c1600"] = piv_1600
    n_total = len(ses)
    ses = ses.dropna()
    n_excl = n_total - len(ses)
    ses = ses.sort_index()
    ses["r_day"] = ses["c1530"] - ses["o0930"]  # POINTS (R2)
    ses["r_eod"] = ses["c1600"] - ses["c1530"]  # POINTS (R2)
    ses.attrs["n_excl_anchor"] = n_excl
    ses.attrs["n_total_dates"] = n_total
    return ses


def ols_beta(x: np.ndarray, y: np.ndarray) -> tuple[float, float]:
    """OLS slope (with intercept) and conventional SE."""
    n = len(x)
    xm, ym = x.mean(), y.mean()
    sxx = float(((x - xm) ** 2).sum())
    b = float(((x - xm) * (y - ym)).sum()) / sxx
    a = ym - b * xm
    resid = y - a - b * x
    se = float(np.sqrt((resid @ resid) / (n - 2) / sxx))
    return b, se


def main() -> None:
    lines: list[str] = []

    def p(s: str = "") -> None:
        print(s)
        lines.append(s)

    p("C_MC42_eod_short_covering — gate table (PRINTED BY PROGRAM)  trial G00031")
    p(f"run: G2_F5_TRIO_20260829 sub-run C   seed={SEED}  block={BLOCK} sessions  reps={REPS}")
    p("substrate law: all returns in POINTS on the back-adjusted substrate")
    p("")

    # -- provenance verification -----------------------------------------------------
    for path in (DEEP, MODERN):
        h = sha256(path)
        ok = h == EXPECTED_SHA[path]
        p(f"input {os.path.relpath(path, REPO)}")
        p(f"  sha256 {h}  {'MATCHES' if ok else 'MISMATCH vs'} GENESIS_REPRO_INCUMBENT_20260828 provenance")
        assert ok, "substrate hash mismatch — refusing to run"
    p("")

    old = load_sessions(DEEP, ERA_OLD, "deep 2006-15")
    new = load_sessions(MODERN, ERA_NEW, "modern 2023-26/05")

    down_old = old[old["r_day"] < 0.0]
    down_new = new[new["r_day"] < 0.0]

    # -- event counts FIRST (rule 7) -------------------------------------------------
    p("EVENT COUNTS (before any verdict)")
    for label, ses, dn in (("2006-15 (deep)", old, down_old), ("2023-26/05 (modern)", new, down_new)):
        p(f"  {label:22s} anchor-complete sessions={len(ses):5d}  "
          f"excluded(missing anchors)={ses.attrs['n_excl_anchor']:4d} of {ses.attrs['n_total_dates']:5d}  "
          f"down-days={len(dn):4d} ({100.0 * len(dn) / len(ses):.1f}%)")
    yrs_new = (pd.Timestamp(ERA_NEW[1]) - pd.Timestamp(ERA_NEW[0])).days / 365.25
    p(f"  down-day events/yr (2023-26/05): {len(down_new) / yrs_new:.1f}")
    p("")

    # -- point estimates -------------------------------------------------------------
    b_old, se_old = ols_beta(down_old["r_day"].to_numpy(), down_old["r_eod"].to_numpy())
    b_new, se_new = ols_beta(down_new["r_day"].to_numpy(), down_new["r_eod"].to_numpy())

    # -- circular block bootstrap over ALL modern sessions, beta among down-days (R5) --
    rng = np.random.default_rng(SEED)  # the sub-run's single shared draw
    x_all = new["r_day"].to_numpy()
    y_all = new["r_eod"].to_numpy()
    n = len(x_all)
    n_blocks = int(np.ceil(n / BLOCK))
    betas = np.empty(REPS)
    dropped = 0
    kept = 0
    for _ in range(REPS):
        starts = rng.integers(0, n, size=n_blocks)
        idx = (starts[:, None] + np.arange(BLOCK)[None, :]).ravel()[:n] % n
        xb, yb = x_all[idx], y_all[idx]
        m = xb < 0.0
        if m.sum() < MIN_DOWN_PER_REP or np.var(xb[m]) == 0.0:
            dropped += 1
            continue
        betas[kept] = ols_beta(xb[m], yb[m])[0]
        kept += 1
    betas = betas[:kept]
    ci_lo, ci_hi = np.percentile(betas, [2.5, 97.5])
    se_boot = float(betas.std(ddof=1))

    # -- MDE before verdicts (rule 7 / R7) -------------------------------------------
    mde = 2.80 * se_boot
    p("MDE (before any verdict)")
    p(f"  bootstrap SE(beta_2023-26/05) = {se_boot:.5f}   (reps kept {kept}/{REPS}, dropped {dropped})")
    p(f"  MDE |beta_new - beta_old| @ two-sided alpha=0.05, power=0.80: {mde:.5f}")
    p(f"  observed |beta_new - beta_old| = {abs(b_new - b_old):.5f}  "
      f"({'>= MDE: contrast powered' if abs(b_new - b_old) >= mde else '< MDE: contrast under-powered at this effect size'})")
    p("")

    p("PRIMARY (frozen)")
    p(f"  beta 2006-15    (OLS, down-days) = {b_old:+.5f}   conventional SE {se_old:.5f}   N={len(down_old)}")
    p(f"  beta 2023-26/05 (OLS, down-days) = {b_new:+.5f}   conventional SE {se_new:.5f}   N={len(down_new)}")
    p(f"  2023-26/05 95% block-bootstrap CI (circular, {BLOCK}-session blocks, {kept} reps): "
      f"[{ci_lo:+.5f}, {ci_hi:+.5f}]")
    p("")

    # -- clause evaluation (verbatim, R8) --------------------------------------------
    excludes = (b_old < ci_lo) or (b_old > ci_hi)
    sign_flip = (np.sign(b_new) != np.sign(b_old)) and np.sign(b_new) != 0 and np.sign(b_old) != 0
    fires = excludes and sign_flip

    p("ADOPT-EXIT-RULE CLAUSE (frozen text: 'ONLY if the 2023-26 CI excludes the 2006-15")
    p("point estimate AND the sign flips (else banked, no rule)') — evaluation verbatim:")
    p(f"  (A) CI excludes 2006-15 point:  {b_old:+.5f} in [{ci_lo:+.5f}, {ci_hi:+.5f}] ? "
      f"{'NO -> A holds' if excludes else 'YES -> A fails'}   A={'PASS' if excludes else 'FAIL'}")
    p(f"  (B) sign flips:  sign(beta_new)={np.sign(b_new):+.0f}  sign(beta_old)={np.sign(b_old):+.0f}   "
      f"B={'PASS' if sign_flip else 'FAIL'}")
    p(f"  CLAUSE = A AND B = {'FIRES -> adopt exit rule' if fires else 'DOES NOT FIRE -> banked, no rule'}")
    p("")

    # -- gate table ------------------------------------------------------------------
    p(f"{'GATE':32s}| {'SPEC':44s}| {'OBSERVED':34s}| VERDICT")
    p("-" * 124)
    rows = [
        ("substrate hashes", "match GENESIS_REPRO provenance", "both match", "PASS"),
        ("seal (>=2026-08-01 virgin)", "assert_presealed on both raw loads", "no sealed rows", "PASS"),
        ("units", "POINTS only (substrate law)", "points throughout", "PASS"),
        ("bootstrap reps", f">= 2000, {BLOCK}-session blocks", f"{kept} kept / {dropped} dropped", "PASS" if kept >= 2000 else "FAIL"),
        ("clause A: CI excludes old beta", f"{b_old:+.5f} outside CI", f"CI [{ci_lo:+.5f}, {ci_hi:+.5f}]", "PASS" if excludes else "FAIL"),
        ("clause B: sign flip", "sign(beta_new) != sign(beta_old)", f"{np.sign(b_new):+.0f} vs {np.sign(b_old):+.0f}", "PASS" if sign_flip else "FAIL"),
        ("ADOPT-EXIT-RULE", "fires ONLY if A AND B", "A AND B = " + ("True" if fires else "False"), "FIRES" if fires else "NO RULE (banked)"),
    ]
    for g, s, o, v in rows:
        p(f"{g:32s}| {s:44s}| {o:34s}| {v}")
    p("")
    verdict = "ADOPT_CLAUSE_FIRES" if fires else "BANKED_NO_RULE"
    p(f"VERDICT: {verdict}")

    with open(os.path.join(OUT, "C_gate_table.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    frag = {
        "trial_id": "G00031",
        "mc_id": "MC-42",
        "run_id": "G2_F5_TRIO_20260829",
        "sub_run": "C_MC42_eod_short_covering",
        "date": "2026-08-29",
        "question": "did down-day 15:30->16:00 continuation flip sign in the 0DTE era?",
        "verdict": verdict,
        "evidence_status": "DISCOVERY_CONSUMED",
        "primary": {
            "beta_2006_15": round(b_old, 6),
            "beta_2006_15_ols_se": round(se_old, 6),
            "n_down_2006_15": int(len(down_old)),
            "beta_2023_2605": round(b_new, 6),
            "beta_2023_2605_ols_se": round(se_new, 6),
            "n_down_2023_2605": int(len(down_new)),
            "ci95_block_bootstrap_2023_2605": [round(ci_lo, 6), round(ci_hi, 6)],
            "bootstrap": {"seed": SEED, "block_sessions": BLOCK, "reps_kept": int(kept), "reps_dropped": int(dropped)},
            "mde_beta_contrast_80pct_power": round(mde, 6),
            "units": "points",
        },
        "clause": {"A_ci_excludes_old_point": bool(excludes), "B_sign_flip": bool(sign_flip), "fires": bool(fires)},
        "seal": "assert_presealed on both raw loads; max data session 2026-05-31 era cut",
        "spend_usd": 0,
        "live_enabled": False,
        "artifacts": ["outC/C_gate_table.txt", "outC/spec_resolutions.txt", "outC/ledger_result_pending.json"],
    }
    with open(os.path.join(OUT, "ledger_result_pending.json"), "w", encoding="utf-8") as f:
        json.dump(frag, f, indent=2)
    print("\nwrote outC/C_gate_table.txt and outC/ledger_result_pending.json")


if __name__ == "__main__":
    main()
