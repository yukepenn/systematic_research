"""G2_F1_TICK01_20260829 - NYSE TICK capitulation event study on NQ (MC-23, trial G00019).

SIGNAL_DIAGNOSTIC. No policy, no P&L, no trading-cost claim, no threshold search.
Frozen event: first RTH minute with ^TICK close <= -1000 within an arming cycle;
re-arm only after close >= -400; per-session reset (spec_resolutions.txt R1/R2).
Target: NQ forward 15-min simple return from the close of the event minute.
Gates: T1 mean>0 with session-clustered t>=2; T2 count-matched same-session control
(event mean > p95 of 1000 draw means); T3 session-block circular-shift null via
research_sdk.null_guard (sensitivity first; real above p95). 5/30/60 min are
REPORTED-ONLY diagnostics - no gate reads them.

Seal: every load passes research_sdk.seal_guard.assert_presealed. data_esnq untouched.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys

import numpy as np
import pandas as pd

ROOT = (r"D:\OneDrive - Washington University in St. Louis\TradingResearch"
        r"\systematic_research")
sys.path.insert(0, ROOT)
from research_sdk.seal_guard import assert_presealed  # noqa: E402
from research_sdk.null_guard import run_circular_null, verify_null_sensitivity  # noqa: E402

RUN = os.path.join(ROOT, "runs", "G2_F1_TICK01_20260829")
OUT = os.path.join(RUN, "out")
os.makedirs(OUT, exist_ok=True)

TRIG, REARM = -1000.0, -400.0          # frozen from practitioner convention - no search
H_TARGET = 15                          # THE target horizon (minutes)
H_DIAG = (5, 30, 60)                   # reported only
N_DRAWS_T2 = 1000                      # frozen in spec_resolutions.txt R7 (spec: >=300)
SEED_T2 = 20260829
MDE_K = 2.80

_log = open(os.path.join(OUT, "tick01_log.txt"), "w", encoding="utf-8")
_gate = open(os.path.join(OUT, "gate_table.txt"), "w", encoding="utf-8")


def P(*a):
    print(*a, flush=True)
    print(*a, file=_log)


def G(*a):
    """Print to BOTH the log and the formal gate table file."""
    P(*a)
    print(*a, file=_gate)


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# ------------------------------------------------------------------ data certification
def certify_and_load():
    P("=" * 100)
    P("=== DATA CERTIFICATION (manifest row counts + hashes, printed by program)")
    P("=" * 100)
    man = pd.read_csv(os.path.join(ROOT, "research", "data_internals", "MANIFEST.csv"))
    all_ok = True
    for _, r in man.iterrows():
        p = os.path.join(ROOT, "research", "data_internals", r["file"])
        d = pd.read_parquet(p)
        h = sha256(p)
        ok_rows = len(d) == int(r["bars"])
        ok_hash = h == r["sha256"]
        all_ok &= ok_rows and ok_hash
        P(f"    {r['symbol']:<6} rows {len(d):>7,} vs manifest {int(r['bars']):>7,} "
          f"[{'OK' if ok_rows else 'MISMATCH'}]   sha256 {'OK' if ok_hash else 'MISMATCH'}")
    if not all_ok:
        raise SystemExit("DEFECT: internals layer does not match its MANIFEST - refusing to run")
    P("    internals parquet layer CERTIFIED against MANIFEST.csv")

    nq_p = os.path.join(ROOT, "runs", "SM1M_SUBSTRATE", "out", "nq_1m_2022_2026.parquet")
    nq_h = sha256(nq_p)
    exp = "87aa53f007aa47b9ee10d0080317a3cde8d22b55aa368267fa9a4aed7435295d"
    P(f"    NQ substrate sha256 {'OK (matches GENESIS_REPRO_INCUMBENT provenance)' if nq_h == exp else 'MISMATCH'}")
    if nq_h != exp:
        raise SystemExit("DEFECT: NQ substrate hash mismatch vs recorded provenance")

    tick = pd.read_parquet(os.path.join(ROOT, "research", "data_internals", "TICK_1m.parquet"))
    nq = pd.read_parquet(nq_p)
    assert_presealed(tick, "time", "TICK01 tick load")
    assert_presealed(nq, "time", "TICK01 nq load")
    P(f"    seal_guard: TICK {len(tick):,} rows and NQ {len(nq):,} rows asserted pre-seal "
      f"(nothing >= 2026-08-01)")
    P("    data_esnq: NOT TOUCHED by this run (spec needs no tick-level data) - "
      "ALLOWLIST_DEV_44 enforcement vacuously satisfied")
    return tick, nq


# ------------------------------------------------------------------ grid construction
def build_grid(tick: pd.DataFrame, nq: pd.DataFrame):
    """One row per (session, RTH slot 09:31..15:59). Equal-length blocks -> positional
    alignment survives session-block rotation (spec_resolutions R8)."""
    tick = tick.drop_duplicates(subset="time").copy()
    tick["date"] = tick["time"].dt.normalize()
    tick["tod"] = tick["time"].dt.time

    slots = pd.timedelta_range("09:31:00", "15:59:00", freq="1min")
    slot_times = set((pd.Timestamp("2000-01-01") + slots).time)
    off_grid = ~tick["tod"].isin(slot_times)
    P(f"    TICK stamps outside the 09:31..15:59 grid: {int(off_grid.sum())} (reported, not used)")
    tick = tick[~off_grid]

    sessions = np.sort(tick["date"].unique())
    n_sess, n_slot = len(sessions), len(slots)
    idx = pd.MultiIndex.from_product([sessions, slots], names=["date", "slot"])
    stamps = idx.get_level_values("date") + idx.get_level_values("slot")

    tmap = pd.Series(tick["close"].to_numpy(), index=tick["time"])
    if not tmap.index.is_unique:
        raise SystemExit("DEFECT: duplicate TICK stamps after dedup")
    nq = nq.drop_duplicates(subset="time")
    qmap = pd.Series(nq["close"].to_numpy(), index=nq["time"])

    frame = pd.DataFrame({
        "session": np.repeat(sessions, n_slot),
        "stamp": stamps,
        "tick": tmap.reindex(stamps).to_numpy(),
        "nq_at": qmap.reindex(stamps).to_numpy(),
    })
    for h in sorted(set(H_DIAG) | {H_TARGET}):
        fwd = qmap.reindex(stamps + pd.Timedelta(minutes=h)).to_numpy()
        frame[f"fwd{h}"] = (fwd / frame["nq_at"].to_numpy() - 1.0) * 1e4  # bps
    # certify equal-length contiguous blocks
    assert len(frame) == n_sess * n_slot
    P(f"    grid: {n_sess:,} sessions x {n_slot} slots = {len(frame):,} rows; "
      f"tick present on {frame['tick'].notna().sum():,}, "
      f"NQ exact-stamp present on {frame['nq_at'].notna().sum():,}, "
      f"fwd{H_TARGET} computable on {frame[f'fwd{H_TARGET}'].notna().sum():,}")
    return frame, n_sess


# ------------------------------------------------------------------ event automaton
def detect_events(frame: pd.DataFrame, trig=TRIG, rearm=REARM, sign=-1) -> np.ndarray:
    """Vectorized hysteresis automaton, per contiguous session block, ARMED at each
    session start (R2). Returns boolean mask over frame rows. NaN tick = no-op."""
    x = frame["tick"].to_numpy()
    if sign < 0:
        a = x <= trig          # trigger candidates (NaN -> False)
        b = x >= rearm         # re-arm bars
    else:
        a = x >= trig
        b = x <= rearm
    codes = pd.factorize(frame["session"], sort=False)[0]
    s = pd.Series(np.where(a, 1.0, np.where(b, 0.0, np.nan)))
    prev = s.groupby(codes).ffill().groupby(codes).shift(1).to_numpy()
    # armed before t iff last decisive bar strictly before t was a re-arm (0) or none (NaN)
    return a & ~(prev == 1.0)


def cluster_t(x: np.ndarray, clusters: np.ndarray):
    """Liang-Zeger cluster-robust t for the mean, G/(G-1) small-sample factor (R6)."""
    n = len(x)
    xbar = float(np.mean(x))
    e = x - xbar
    sums = pd.Series(e).groupby(pd.Series(clusters)).sum().to_numpy()
    g = len(sums)
    se = np.sqrt(np.sum(sums ** 2) * (g / (g - 1))) / n
    return xbar, xbar / se, se, g


# ------------------------------------------------------------------ main
def main():
    tick, nq = certify_and_load()
    P("")
    P("=" * 100)
    P("=== GRID")
    P("=" * 100)
    frame, n_sess = build_grid(tick, nq)

    fwd_t = f"fwd{H_TARGET}"

    # ---------------- real events
    ev_mask = detect_events(frame)
    ev = frame[ev_mask].copy()
    ev_scored = ev[ev[fwd_t].notna() & ev["nq_at"].notna()]
    P("")
    P("=" * 100)
    P("=== EVENTS (frozen -1000 trigger / -400 re-arm, close-based, per-session reset)")
    P("=" * 100)
    P(f"    events detected            {len(ev):>7,}")
    P(f"    ... with exact NQ stamp + computable fwd{H_TARGET}: {len(ev_scored):,} "
      f"(excluded for missing stamps: {len(ev) - len(ev_scored)})")
    yr = ev["session"].dt.year
    for y, c in yr.value_counts().sort_index().items():
        P(f"      {y}: {c:>5,} events")
    years = n_sess / 252.0
    P(f"    events/year (n / (sessions/252)) = {len(ev) / years:,.1f}")
    P(f"    sessions with >=1 event: {ev['session'].nunique():,} of {n_sess:,}")

    ev_out = ev.copy()
    ev_out["scored"] = ev_out[fwd_t].notna() & ev_out["nq_at"].notna()
    cols = ["session", "stamp", "tick", "nq_at"] + [f"fwd{h}" for h in sorted(set(H_DIAG) | {H_TARGET})] + ["scored"]
    ev_out[cols].to_csv(os.path.join(OUT, "events.csv"), index=False)

    x = ev_scored[fwd_t].to_numpy()
    cl = ev_scored["session"].to_numpy()
    mean_bps, t_cl, se, g = cluster_t(x, cl)
    sd = float(np.std(x, ddof=1))
    mde = MDE_K * sd / np.sqrt(len(x))

    # ---------------- T2: count-matched same-session control
    P("")
    P("=" * 100)
    P(f"=== T2 CONTROL - count-matched random RTH minutes from the SAME sessions "
      f"({N_DRAWS_T2} draws, seed {SEED_T2})")
    P("=" * 100)
    universe = frame[frame["tick"].notna() & frame["nq_at"].notna() & frame[fwd_t].notna()]
    k_by_sess = ev_scored.groupby("session").size()
    uni_by_sess = {s: gdf[fwd_t].to_numpy() for s, gdf in universe.groupby("session")}
    rng = np.random.default_rng(SEED_T2)
    draw_means = np.empty(N_DRAWS_T2)
    for d in range(N_DRAWS_T2):
        tot, cnt = 0.0, 0
        for s, k in k_by_sess.items():
            u = uni_by_sess[s]
            pick = rng.choice(len(u), size=int(k), replace=False)
            tot += float(u[pick].sum())
            cnt += int(k)
        draw_means[d] = tot / cnt
    ctrl_p95 = float(np.percentile(draw_means, 95))
    ctrl_mean = float(np.mean(draw_means))
    P(f"    control universe: {len(universe):,} eligible minutes across "
      f"{len(uni_by_sess):,} sessions; per-draw n = {int(k_by_sess.sum()):,}")
    P(f"    control draw means: mean {ctrl_mean:+.3f} bps, p95 {ctrl_p95:+.3f} bps")

    # ---------------- T3: session-block circular-shift null (sensitivity FIRST)
    P("")
    P("=" * 100)
    P("=== T3 NULL - session-block circular shift of TICK against NQ (null_guard)")
    P("=" * 100)
    loader = lambda: frame[["session", "tick", fwd_t, "nq_at"]].copy()
    decide = lambda f: detect_events(f)
    def score(d, base):
        v = base[fwd_t].to_numpy()[np.asarray(d, dtype=bool)]
        v = v[~np.isnan(v)]
        return float(np.mean(v)) if len(v) else np.nan
    sens = verify_null_sensitivity(loader, decide, score, shifts=[1, 7, 313], unit="session")
    P(f"    null_guard sensitivity: real {sens['real_stat']:+.4f} bps, "
      f"spread across probe shifts {sens['spread']:.4f} bps -> NULL HAS TEETH")
    null = run_circular_null(loader, decide, score, n_shifts=n_sess - 1, unit="session")
    arr = np.asarray(null["null_stats"], dtype=float)
    n_nan = int(np.isnan(arr).sum())
    finite = arr[~np.isnan(arr)]
    null_p95 = float(np.percentile(finite, 95))
    P(f"    complete enumeration: {len(arr):,} rotations ({n_nan} zero-event draws), "
      f"real {null['real_stat']:+.4f} bps, null mean {np.mean(finite):+.4f}, "
      f"p95 {null_p95:+.4f}, percentile of real {null['percentile']:.4f}, "
      f"p_ge {null['p_ge']:.4f}")
    if abs(null["real_stat"] - mean_bps) > 1e-9:
        raise SystemExit("DEFECT: null-machinery real stat != T1 event mean")

    # ---------------- secondary (+1000, two-sided, NON-GATE)
    P("")
    P("=" * 100)
    P("=== SECONDARY (NON-GATE): symmetric +1000 event, two-sided report")
    P("=" * 100)
    pos_mask = detect_events(frame, trig=+1000.0, rearm=+400.0, sign=+1)
    pv = frame[pos_mask]
    pvs = pv[pv[fwd_t].notna() & pv["nq_at"].notna()]
    if len(pvs) >= 2 and pvs["session"].nunique() >= 2:
        pm, pt, _, pg = cluster_t(pvs[fwd_t].to_numpy(), pvs["session"].to_numpy())
        P(f"    +1000 events {len(pv):,} ({len(pvs):,} scored, {pg:,} sessions): "
          f"mean fwd{H_TARGET} {pm:+.3f} bps, clustered t {pt:+.2f} (two-sided, reported only)")
    else:
        pm, pt = float("nan"), float("nan")
        P(f"    +1000 events {len(pv):,} - too few to report a t")

    # ---------------- diagnostics (NON-GATE)
    P("")
    P("=" * 100)
    P("=== DIAGNOSTICS (NON-GATE; no gate reads these - no horizon selection)")
    P("=" * 100)
    horizon_prof = {}
    for h in H_DIAG:
        fh = f"fwd{h}"
        sub = ev[ev[fh].notna() & ev["nq_at"].notna()]
        hm, ht, _, _ = cluster_t(sub[fh].to_numpy(), sub["session"].to_numpy())
        horizon_prof[h] = (len(sub), hm, ht)
        P(f"    horizon {h:>3} min: n {len(sub):>6,}  mean {hm:+.3f} bps  clustered t {ht:+.2f}   [REPORTED ONLY]")

    lp = os.path.join(ROOT, "runs", "RR_W001_ACTION_VALUE_LEDGER", "out", "ledger_p1pct.csv")
    L = pd.read_csv(lp)
    S = L[L["in_scoring_population"] == 1].copy()
    S["ts"] = pd.to_datetime(S["decision_ts"])
    assert_presealed(S, "ts", "TICK01 p1 ledger load")
    ev_sess = set(ev["session"])
    p1_sess = set(S["ts"].dt.normalize())
    ev_in_p1 = ev["session"].isin(p1_sess).mean()
    ev_stamps = ev["stamp"].to_numpy()
    hits = 0
    for ts in S["ts"]:
        d = ts.to_datetime64() - ev_stamps
        if np.any((d >= np.timedelta64(0, "m")) & (d <= np.timedelta64(H_TARGET, "m"))):
            hits += 1
    P(f"    P1 overlap (descriptive only): {100 * ev_in_p1:.1f}% of events fall in sessions with >=1 "
      f"P1 scoring entry; {hits:,} of {len(S):,} P1 scoring entries have decision_ts within "
      f"[t, t+{H_TARGET}] of an event; event sessions {len(ev_sess):,}, P1 sessions {len(p1_sess):,}")

    # ---------------- gate table
    t1 = (mean_bps > 0) and (t_cl >= 2.0)
    t2 = mean_bps > ctrl_p95
    t3 = mean_bps > null_p95
    verdict = "INFORMATION-SUPPORTED" if (t1 and t2 and t3) else "NULL"

    G("")
    G("=" * 100)
    G("=== GATE TABLE - G2_F1_TICK01_20260829 (trial G00019) - printed by program")
    G("=" * 100)
    G(f"{'GATE':<6}{'SPEC':<58}{'OBSERVED':<44}{'PASS-FAIL'}")
    G(f"{'T1':<6}{'mean fwd15 > 0 AND session-clustered t >= 2.0':<58}"
      f"{f'mean {mean_bps:+.3f} bps, t {t_cl:+.2f} (n={len(x):,}, G={g:,})':<44}{'PASS' if t1 else 'FAIL'}")
    G(f"{'T2':<6}{'event mean > p95 of count-matched same-session draws':<58}"
      f"{f'event {mean_bps:+.3f} vs control p95 {ctrl_p95:+.3f} bps':<44}{'PASS' if t2 else 'FAIL'}")
    G(f"{'T3':<6}{'real above p95 of session-block circular-shift null':<58}"
      f"{f'real {mean_bps:+.3f} vs null p95 {null_p95:+.3f} bps':<44}{'PASS' if t3 else 'FAIL'}")
    G("")
    G(f"    MDE (2.80*sd/sqrt(n), ~80% power two-sided 5%): {mde:.3f} bps "
      f"= {mde / abs(mean_bps):.2f}x the observed |mean| (sd {sd:.2f} bps, n {len(x):,})")
    G(f"    [printed BEFORE the verdict per spec]")
    G("")
    G(f"    VERDICT: {verdict}"
      + ("" if verdict == "NULL" else " (a policy/economics run may now be preregistered - NOT run here)"))
    G(f"    secondary +1000 (non-gate): mean {pm:+.3f} bps, t {pt:+.2f}")
    G(f"    horizon profile 5/30/60 min: REPORTED ONLY above; no gate reads them")
    G(f"    prohibitions honored: no threshold search, no policy, no P&L, no cost claim, no sealed reads")

    # ---------------- ledger result (pending; NOT appended to SEARCH_LEDGER.jsonl)
    result = {
        "trial_id": "G00019",
        "metrics": {
            "n_events": int(len(ev)),
            "n_events_scored": int(len(x)),
            "events_per_year": round(len(ev) / years, 1),
            "mean_fwd15_bps": round(mean_bps, 4),
            "t_clustered": round(t_cl, 3),
            "n_cluster_sessions": int(g),
            "mde_bps": round(mde, 4),
            "control_p95_bps": round(ctrl_p95, 4),
            "control_mean_bps": round(ctrl_mean, 4),
            "control_draws": N_DRAWS_T2,
            "null_p95_bps": round(null_p95, 4),
            "null_rotations": int(len(arr)),
            "null_percentile_of_real": round(null["percentile"], 4),
            "null_p_ge": round(null["p_ge"], 4),
            "T1": "PASS" if t1 else "FAIL",
            "T2": "PASS" if t2 else "FAIL",
            "T3": "PASS" if t3 else "FAIL",
            "secondary_pos1000_mean_bps": None if np.isnan(pm) else round(pm, 4),
            "secondary_pos1000_t": None if np.isnan(pt) else round(pt, 3),
            "horizon_profile_bps_nongate": {str(h): {"n": int(v[0]), "mean_bps": round(v[1], 4), "t": round(v[2], 3)}
                                            for h, v in horizon_prof.items()},
        },
        "result": verdict,
        "note": ("MC-23 TICK capitulation event study, signal-only. Frozen -1000/-400 close-based "
                 "arming cycle, per-session reset; 15-min is THE target (5/30/60 diagnostics only). "
                 "T2 = 1000 count-matched same-session draws (W111b rule); T3 = complete-enumeration "
                 "session-block circular-shift null via null_guard (sensitivity verified first). "
                 "Internals layer certified vs MANIFEST; NQ substrate hash matches provenance; all "
                 "loads seal-guarded; data_esnq untouched. No policy/P&L claim attaches to this verdict."),
    }
    with open(os.path.join(OUT, "ledger_result_pending.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    P("")
    P(f"    wrote out/ledger_result_pending.json (result: {verdict})")
    _log.close()
    _gate.close()


if __name__ == "__main__":
    main()
