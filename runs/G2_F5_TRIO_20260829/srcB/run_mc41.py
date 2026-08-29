"""G2_F5_TRIO_20260829 sub-run B — MC-41 breadth divergence (trial G00030).

Frozen primary (spec.yaml B_MC41_breadth_divergence):
  delta = P(afternoon takes out the morning low | bottom-tercile 11:00 cumulative
  adjusted TICK) - matched unconditional P; internals minute 2022 -> 2026-05-31;
  circular-shift null (session unit) sharing the family draw; MDE + events/yr FIRST;
  if the powered MDE > 15pp the verdict is CLOSED-BY-POWER, printed as such.

All resolutions of spec ambiguities were frozen in outB/spec_resolutions.txt BEFORE
this program ran. Gate table is PRINTED BY THIS PROGRAM. No parameter search.
Substrate law: takeout computed on price LOWS in points level; no percent returns.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from datetime import time as dtime

import numpy as np
import pandas as pd

REPO = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, REPO)
from research_sdk.seal_guard import assert_presealed  # noqa: E402

OUTB = os.path.join(REPO, "runs", "G2_F5_TRIO_20260829", "outB")
TICK_PATH = os.path.join(REPO, "research", "data_internals", "TICK_1m.parquet")
TICK_MANIFEST_SHA = "72612a1e0f308b57862d6e0adfb5883ceee05dfc697c4cb980ea7b2c82b6d80f"
NQ_PATH = os.path.join(REPO, "runs", "SM1M_SUBSTRATE", "out", "nq_1m_2022_2026.parquet")
NQ_PROV_SHA = "87aa53f007aa47b9ee10d0080317a3cde8d22b55aa368267fa9a4aed7435295d"

END_DATE = pd.Timestamp("2026-05-31")          # R1 inclusive; Sunday -> last session 2026-05-29
MORN_LO, MORN_HI = dtime(9, 31), dtime(11, 0)   # R2 END-stamped
AFT_LO, AFT_HI = dtime(11, 1), dtime(16, 0)     # R2
WARMUP = 252                                    # R4
N_NULL = 10_000                                 # R8
SEED = 20260829                                 # R8 family draw
MDE_CEILING_PP = 15.0                           # spec: CLOSED-BY-POWER threshold
Z_POWER = 1.959963984540054 + 0.8416212335729143  # z_.975 + z_.80 = 2.8016 (R9)


def sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    lines: list[str] = []

    def emit(s: str = "") -> None:
        print(s)
        lines.append(s)

    emit("=" * 78)
    emit("G2_F5_TRIO_20260829 / sub-run B / MC-41 breadth divergence / trial G00030")
    emit("printed by program: runs/G2_F5_TRIO_20260829/srcB/run_mc41.py")
    emit("=" * 78)

    # ---- provenance + manifest gate ------------------------------------------------
    tick_sha, nq_sha = sha256(TICK_PATH), sha256(NQ_PATH)
    tick_sha_ok = tick_sha == TICK_MANIFEST_SHA
    nq_sha_ok = nq_sha == NQ_PROV_SHA
    emit(f"TICK_1m.parquet sha256 {tick_sha}  manifest-match={tick_sha_ok}")
    emit(f"nq_1m_2022_2026.parquet sha256 {nq_sha}  provenance-match={nq_sha_ok}")
    if not (tick_sha_ok and nq_sha_ok):
        raise SystemExit("MANIFEST/PROVENANCE HASH MISMATCH — aborting before any read")

    # ---- load through seal guard ---------------------------------------------------
    tick = pd.read_parquet(TICK_PATH, columns=["time", "close"])
    nq = pd.read_parquet(NQ_PATH, columns=["time", "low"])
    assert_presealed(tick, "time", "MC41 TICK full frame")
    assert_presealed(nq, "time", "MC41 NQ full frame")
    emit(f"seal_guard.assert_presealed PASS on both frames "
         f"(TICK {len(tick):,} rows, NQ {len(nq):,} rows)")

    tick = tick[tick["time"].dt.normalize() <= END_DATE].copy()
    nq = nq[nq["time"].dt.normalize() <= END_DATE].copy()
    tick["d"] = tick["time"].dt.date
    nq["d"] = nq["time"].dt.date
    tick["t"] = tick["time"].dt.time
    nq["t"] = nq["time"].dt.time

    # ---- per-session morning TICK cum + NQ takeout (R2/R3/R6/R7) -------------------
    tick_m = tick[(tick["t"] >= MORN_LO) & (tick["t"] <= MORN_HI)]
    g = tick_m.groupby("d")
    tick_sess = pd.DataFrame({
        "n_tick_morn": g["close"].count(),
        "cum11": g["close"].sum(),
        "has_1100": g["t"].agg(lambda s: MORN_HI in set(s)),
    })

    nq_rth = nq[(nq["t"] >= MORN_LO) & (nq["t"] <= AFT_HI)]
    gm = nq_rth[nq_rth["t"] <= MORN_HI].groupby("d")
    ga = nq_rth[nq_rth["t"] >= AFT_LO].groupby("d")
    nq_sess = pd.DataFrame({
        "n_nq_morn": gm["low"].count(),
        "morn_low": gm["low"].min(),
        "n_nq_aft": ga["low"].count(),
        "aft_low": ga["low"].min(),
        "last_rth": nq_rth.groupby("d")["t"].max(),
    })

    s = tick_sess.join(nq_sess, how="inner")
    n_joined = len(s)
    q = (
        (s["n_tick_morn"] >= 80) & s["has_1100"]
        & (s["n_nq_morn"] >= 80) & (s["n_nq_aft"] >= 200)
        & (s["last_rth"] >= dtime(15, 59))
    )
    n_dropped_quality = int((~q).sum())
    s = s[q].sort_index()
    s["takeout"] = (s["aft_low"] < s["morn_low"]).astype(int)  # POINTS-level lows (R7)

    # ---- causal terciles, trailing 252 full window (R4) ----------------------------
    cum = s["cum11"].to_numpy()
    n_all = len(s)
    bottom = np.full(n_all, np.nan)
    for i in range(WARMUP, n_all):
        thr = np.percentile(cum[i - WARMUP:i], 100.0 / 3.0)
        bottom[i] = 1.0 if cum[i] <= thr else 0.0
    s["bottom"] = bottom
    pop = s[~s["bottom"].isna()].copy()
    ind = pop["bottom"].to_numpy().astype(bool)
    out = pop["takeout"].to_numpy().astype(float)
    N = len(pop)
    n1 = int(ind.sum())

    p_uncond = out.mean()
    p_cond = out[ind].mean()
    delta_obs = p_cond - p_uncond

    # ---- circular-shift null, single family draw (R8) ------------------------------
    rng = np.random.default_rng(SEED)
    offsets = rng.integers(1, N, size=N_NULL)
    deltas = np.empty(N_NULL)
    for j, k in enumerate(offsets):
        deltas[j] = out[np.roll(ind, k)].mean() - p_uncond
    sigma_null = deltas.std(ddof=1)
    p_two = (1 + int((np.abs(deltas) >= abs(delta_obs)).sum())) / (N_NULL + 1)
    p_one = (1 + int((deltas >= delta_obs).sum())) / (N_NULL + 1)

    # ---- MDE + events/yr FIRST (R9/R11) --------------------------------------------
    mde_null_pp = Z_POWER * sigma_null * 100.0
    pbar = p_uncond
    mde_analytic_pp = Z_POWER * np.sqrt(pbar * (1 - pbar) * (1 / n1 + 1 / (N - n1))) * 100.0
    span_days = (pop.index[-1] - pop.index[0]).days if hasattr(pop.index[-1], "toordinal") else \
        (pd.Timestamp(pop.index[-1]) - pd.Timestamp(pop.index[0])).days
    years = span_days / 365.25
    events_yr = n1 / years

    emit()
    emit("---- POWER BLOCK (printed BEFORE verdicts, per spec) ----")
    emit(f"population: {n_joined} joined sessions; {n_dropped_quality} dropped by R6 quality; "
         f"{n_all} valid; {WARMUP} warm-up; {N} classified "
         f"({pop.index[0]} .. {pop.index[-1]}, {years:.2f} yr)")
    emit(f"events (bottom-tercile sessions): n1 = {n1}   EVENTS/YR = {events_yr:.1f}")
    emit(f"POWERED MDE (null-sd basis, alpha=.05 two-sided, power=.80): "
         f"{mde_null_pp:.2f} pp   [sigma_null = {sigma_null*100:.2f} pp]")
    emit(f"analytic two-proportion MDE (reference only): {mde_analytic_pp:.2f} pp")
    emit(f"CLOSED-BY-POWER threshold: MDE > {MDE_CEILING_PP:.0f} pp")
    closed_by_power = mde_null_pp > MDE_CEILING_PP

    emit()
    emit("---- OBSERVED (recorded after power block) ----")
    emit(f"P(takeout | bottom tercile) = {p_cond:.4f}   (n={n1})")
    emit(f"P(takeout) unconditional matched = {p_uncond:.4f}   (N={N})")
    emit(f"delta_obs = {delta_obs*100:+.2f} pp")
    emit(f"circular-shift null: N_NULL={N_NULL} seed={SEED}  p_two={p_two:.4f}  p_one(delta>0)={p_one:.4f}")

    # ---- verdict + gate table (printed by program) ---------------------------------
    if closed_by_power:
        verdict = "CLOSED-BY-POWER"
        primary = "NOT-EVALUABLE (population cannot power the contrast)"
    elif delta_obs > 0 and p_two < 0.05:
        verdict = "PASS"
        primary = "PASS"
    else:
        verdict = "FAIL (NULL)"
        primary = "FAIL"

    emit()
    emit("GATE TABLE (printed by program)")
    emit(f"{'GATE':<28}| {'SPEC':<40}| {'OBSERVED':<34}| PASS-FAIL")
    emit("-" * 118)
    rows = [
        ("G1 manifest/provenance", "sha256 match both substrates",
         f"TICK={tick_sha_ok} NQ={nq_sha_ok}", "PASS" if tick_sha_ok and nq_sha_ok else "FAIL"),
        ("G2 seal compliance", "no bar > 2026-07-31 17:00 ET read",
         "assert_presealed passed, window<=2026-05-31", "PASS"),
        ("G3 matched control", "unconditional P same wave/population",
         f"same {N}-session classified pop", "PASS"),
        ("G4 power", f"powered MDE <= {MDE_CEILING_PP:.0f} pp",
         f"MDE = {mde_null_pp:.2f} pp",
         "FAIL -> CLOSED-BY-POWER" if closed_by_power else "PASS"),
        ("G5 primary (frozen)", "delta > 0 AND p_two < 0.05 (R10)",
         f"delta={delta_obs*100:+.2f} pp, p_two={p_two:.4f}", primary),
    ]
    for gname, spec_c, obs_c, pf in rows:
        emit(f"{gname:<28}| {spec_c:<40}| {obs_c:<34}| {pf}")
    emit("-" * 118)
    emit(f"VERDICT (trial G00030 / MC-41): {verdict}")
    emit("evidence-status: DISCOVERY_CONSUMED (2022 -> 2026-05-31 internals population)")

    with open(os.path.join(OUTB, "B_gate_table.txt"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")

    frag = {
        "trial_id": "G00030",
        "mc_id": "MC-41",
        "run_id": "G2_F5_TRIO_20260829",
        "sub_run": "B_MC41_breadth_divergence",
        "date": "2026-08-29",
        "question": "does weak adjusted-TICK breadth by 11:00 condition afternoon downside on modern NQ?",
        "population": {"sessions_classified": N, "bottom_tercile_events": n1,
                       "span": [str(pop.index[0]), str(pop.index[-1])],
                       "events_per_year": round(events_yr, 1)},
        "power": {"mde_pp_null_basis": round(mde_null_pp, 2),
                  "mde_pp_analytic": round(mde_analytic_pp, 2),
                  "closed_by_power_threshold_pp": MDE_CEILING_PP,
                  "sigma_null_pp": round(sigma_null * 100, 2)},
        "observed": {"p_cond": round(p_cond, 4), "p_uncond": round(p_uncond, 4),
                     "delta_pp": round(delta_obs * 100, 2),
                     "p_two": round(p_two, 4), "p_one": round(p_one, 4),
                     "n_null": N_NULL, "seed": SEED},
        "verdict": verdict,
        "evidence_status": "DISCOVERY_CONSUMED",
        "promotion": "NONE",
        "spend_usd": 0,
        "live_enabled": False,
        "artifacts": ["runs/G2_F5_TRIO_20260829/outB/B_gate_table.txt",
                      "runs/G2_F5_TRIO_20260829/outB/spec_resolutions.txt",
                      "runs/G2_F5_TRIO_20260829/srcB/run_mc41.py"],
    }
    with open(os.path.join(OUTB, "ledger_result_pending.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(frag, f, indent=2)
    print("\nwrote outB/B_gate_table.txt and outB/ledger_result_pending.json")


if __name__ == "__main__":
    main()
