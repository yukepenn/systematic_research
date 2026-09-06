"""G2_F14_MC58_REBOUND_20260906 — MC-58 breadth-washout REBOUND, long side (modern leg).

Preregistered spec: runs/G2_F14_MC58_REBOUND_20260906/spec.yaml (committed before results).
Ledger trial G00055. The ERA leg is NOT in this run (data-gated).

State construction is the G00030 (MC-41 / trial G00030) construction VERBATIM:
  bottom-tercile (trailing-252 causal) 11:00 cumulative adjusted-TICK sessions whose
  afternoon 1-min low TAKES OUT the morning 1-min low (POINTS), 2023-01 -> 2026-05-31.
Statistic (NEW to MC-58): LONG 1 NQ at the OPEN of the first 1-min bar AFTER the first
  afternoon takeout bar; exit at the 15:59-stamped close; NO stop; $40/RT ALL_IN.

Gates (ALL printed by this program):
  G0  seal            : max session <= 2026-05-31 hard assert; POINTS basis asserted.
  G1  MDE-first       : B1 mean-MDE AND B2 increment-MDE printed BEFORE any return table.
  B1  economics       : event-clustered t >= 2.0 on mean net > 0.
  B2i PRIMARY discrim. : beats identical trigger on NON-bottom-tercile takeout sessions.
  B2ii random         : beats p95 of >=10,000 count-matched random-session longs at
                        resampled takeout times.
  B3  circular-shift  : null on the state series, family-shared draw, effective-K.
  timing-teeth        : +5/+15/+30-min delayed entries; +30 must lose >=40% of mean net;
                        a FLAT curve falsifies the flush-anchored mechanism.
  concentration       : CLASSIFICATION-only (carries the F9 incumbent-236.8% note).

Outcome taxonomy (preregistered):
  B2(i) control >= candidate OR increment ~= 0  -> CLOSED-AS-GENERIC-MR (permanent)
  positive but under increment-MDE              -> CLOSED-BY-POWER (labeled as such)
  B1 + B2(i) + B2(ii) + B3 pass AND delay decays -> SURVIVES

Prohibitions honoured: no tercile/delay/exit search; no stops; no reclaim gating; no era
pooling; entry is EVENT-TIME (bar after takeout), never state-time 11:01 full-window.
POINTS-based P&L (substrate law). Seed 20260906 (family draw).
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

RUN = os.path.join(REPO, "runs", "G2_F14_MC58_REBOUND_20260906")
OUT = os.path.join(RUN, "out")
TICK_PATH = os.path.join(REPO, "research", "data_internals", "TICK_1m.parquet")
TICK_MANIFEST_SHA = "72612a1e0f308b57862d6e0adfb5883ceee05dfc697c4cb980ea7b2c82b6d80f"
NQ_PATH = os.path.join(REPO, "runs", "SM1M_SUBSTRATE", "out", "nq_1m_2022_2026.parquet")
NQ_PROV_SHA = "87aa53f007aa47b9ee10d0080317a3cde8d22b55aa368267fa9a4aed7435295d"

END_DATE = pd.Timestamp("2026-05-31")            # G00030 R1 inclusive endpoint
HARD_DROP_CUT = pd.Timestamp("2026-06-01")        # task: never materialize >= 2026-06-01
MORN_LO, MORN_HI = dtime(9, 31), dtime(11, 0)     # END-stamped (G00030 R2)
AFT_LO, AFT_HI = dtime(11, 1), dtime(16, 0)       # G00030 R2 afternoon window
EXIT_T = dtime(15, 59)                            # 15:59-stamped close
WARMUP = 252                                      # G00030 R4
N_NULL = 10_000                                   # B3 circular-shift draws
N_RANDOM = 10_000                                 # B2(ii) count-matched random draws
SEED = 20260906                                   # family draw (this run)
POINT_USD = 20.0                                  # NQ point multiplier
COST_ALLIN = 40.0                                 # $/RT ALL_IN (p90-spread regime)
COST_NG_2501 = 25.01                              # printed NON-gate
COST_NG_3300 = 33.00                              # printed NON-gate
DELAYS = [0, 5, 15, 30]                           # timing-teeth (minutes)
DELAY_BAND_FRAC = 0.40                            # +30 must lose >= 40% of mean net
Z_POWER = 1.959963984540054 + 0.8416212335729143  # z_.975 + z_.80 = 2.8016
INCUMBENT_F9_NOTE = "the incumbent fails this bar at 236.8% (F9)"


def sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _mins(t: dtime) -> int:
    return t.hour * 60 + t.minute


def main() -> None:
    lines: list[str] = []

    def emit(s: str = "") -> None:
        print(s)
        lines.append(s)

    emit("=" * 96)
    emit("G2_F14_MC58_REBOUND_20260906 / MC-58 breadth-washout REBOUND (long) / trial G00055")
    emit("printed by program: runs/G2_F14_MC58_REBOUND_20260906/src/run_mc58.py")
    emit("=" * 96)

    # ---- G1a manifest / provenance gate (abort before any read on mismatch) --------
    tick_sha, nq_sha = sha256(TICK_PATH), sha256(NQ_PATH)
    tick_ok, nq_ok = tick_sha == TICK_MANIFEST_SHA, nq_sha == NQ_PROV_SHA
    emit(f"TICK_1m.parquet sha256 {tick_sha}  manifest-match={tick_ok}")
    emit(f"nq_1m_2022_2026.parquet sha256 {nq_sha}  provenance-match={nq_ok}")
    if not (tick_ok and nq_ok):
        raise SystemExit("MANIFEST/PROVENANCE HASH MISMATCH — aborting before any read")

    # ---- load with pushdown hard-drop (never materialize >= 2026-06-01) ------------
    tick = pd.read_parquet(TICK_PATH, columns=["time", "close"],
                           filters=[("time", "<", HARD_DROP_CUT)])
    nq = pd.read_parquet(NQ_PATH, columns=["time", "open", "low", "close"],
                         filters=[("time", "<", HARD_DROP_CUT)])
    # verbatim G00030 endpoint filter (redundant after pushdown, kept for identity)
    tick = tick[tick["time"].dt.normalize() <= END_DATE].copy()
    nq = nq[nq["time"].dt.normalize() <= END_DATE].copy()
    assert_presealed(tick, "time", "MC58 TICK frame (post hard-drop)")
    assert_presealed(nq, "time", "MC58 NQ frame (post hard-drop)")
    emit(f"seal_guard.assert_presealed PASS on both frames "
         f"(TICK {len(tick):,} rows, NQ {len(nq):,} rows; pushdown-dropped >= 2026-06-01)")

    for df in (tick, nq):
        df["d"] = df["time"].dt.date
        df["t"] = df["time"].dt.time

    # ---- G0 seal: hard assert max session <= 2026-05-31 ----------------------------
    max_tick_d = max(tick["d"]); max_nq_d = max(nq["d"])
    seal_ok = (max_tick_d <= END_DATE.date()) and (max_nq_d <= END_DATE.date())
    if not seal_ok:
        raise SystemExit("G0 SEAL VIOLATION: a session > 2026-05-31 survived the hard-drop")
    emit(f"G0 seal: max TICK session={max_tick_d}, max NQ session={max_nq_d} (both <= 2026-05-31) PASS")
    emit("G0 basis: takeout & P&L computed on POINTS (price levels). DELEV01 not implicated —")
    emit("          within-session additive offsets cancel in (aft_low<morn_low) and in "
         "(exit-entry).")

    # ---- state construction (G00030 verbatim) --------------------------------------
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
    s["takeout"] = (s["aft_low"] < s["morn_low"]).astype(int)  # POINTS-level lows

    cum = s["cum11"].to_numpy()
    n_all = len(s)
    bottom = np.full(n_all, np.nan)
    thr_bot_arr = np.full(n_all, np.nan)
    for i in range(WARMUP, n_all):
        thr = np.percentile(cum[i - WARMUP:i], 100.0 / 3.0)
        thr_bot_arr[i] = thr
        bottom[i] = 1.0 if cum[i] <= thr else 0.0
    s["bottom"] = bottom
    s["thr_bot"] = thr_bot_arr
    pop = s[~s["bottom"].isna()].copy()
    N = len(pop)

    # ---- per-session afternoon bar arrays (for event-time trade construction) ------
    aft = nq_rth[nq_rth["t"] >= AFT_LO].copy().sort_values("time")
    aft_by_d: dict = {}
    for d, sub in aft.groupby("d"):
        tt = sub["t"].to_numpy()
        aft_by_d[d] = {
            "t": tt,
            "tmin": np.array([_mins(x) for x in tt], dtype=int),
            "low": sub["low"].to_numpy(dtype=float),
            "open": sub["open"].to_numpy(dtype=float),
            "close": sub["close"].to_numpy(dtype=float),
        }
    morn_low = pop["morn_low"].to_dict()
    exit_min = _mins(EXIT_T)

    def _exit_close(rec) -> float:
        idx = np.where(rec["tmin"] == exit_min)[0]
        return float(rec["close"][idx[0]]) if len(idx) else float("nan")

    def trade(d, delay_min: int = 0):
        """LONG at open of first bar AFTER first afternoon takeout (POINTS), + optional
        delay in minutes relative to that base entry; exit at 15:59 close. Returns None
        if unenterable at/before the 15:59 exit bar."""
        rec = aft_by_d.get(d)
        if rec is None:
            return None
        lows, opens, tmin = rec["low"], rec["open"], rec["tmin"]
        ml = morn_low[d]
        breach = lows < ml
        if not breach.any():
            return None
        to_idx = int(np.argmax(breach))          # first afternoon takeout bar
        to_min = int(tmin[to_idx])
        if to_idx + 1 >= len(lows):
            return None
        base_entry_min = int(tmin[to_idx + 1])    # bar AFTER takeout
        if delay_min == 0:
            ei = to_idx + 1
        else:
            cand = np.where(tmin >= base_entry_min + delay_min)[0]
            if len(cand) == 0:
                return None
            ei = int(cand[0])
        entry_min = int(tmin[ei])
        if entry_min > exit_min:                   # cannot enter at/before the 15:59 exit
            return None
        exit_close = _exit_close(rec)
        if not np.isfinite(exit_close):
            return None
        entry_open = float(opens[ei])
        gross_pts = exit_close - entry_open
        net = gross_pts * POINT_USD - COST_ALLIN
        return {
            "to_min": to_min, "entry_min": entry_min, "entry_open": entry_open,
            "exit_close": exit_close, "gross_pts": gross_pts, "net": net,
        }

    cand_idx = list(pop[(pop["bottom"] == 1) & (pop["takeout"] == 1)].index)
    ctrl_idx = list(pop[(pop["bottom"] == 0) & (pop["takeout"] == 1)].index)
    n_bottom = int((pop["bottom"] == 1).sum())
    n_notbreach = n_bottom - len(cand_idx)

    # candidate base trades (delay 0)
    cand_rows, cand_net, cand_unenter = [], [], 0
    for d in cand_idx:
        r = trade(d, 0)
        if r is None:
            cand_unenter += 1
        else:
            cand_rows.append((d, r)); cand_net.append(r["net"])
    cand_net = np.array(cand_net, dtype=float)
    n_cand = len(cand_net)

    # control base trades (delay 0) — identical trigger, non-bottom takeout sessions
    ctrl_net, ctrl_unenter = [], 0
    ctrl_entry_mins = []
    for d in ctrl_idx:
        r = trade(d, 0)
        if r is None:
            ctrl_unenter += 1
        else:
            ctrl_net.append(r["net"]); ctrl_entry_mins.append(r["entry_min"])
    ctrl_net = np.array(ctrl_net, dtype=float)
    n_ctrl = len(ctrl_net)

    mean_cand = cand_net.mean()
    sd_cand = cand_net.std(ddof=1)
    t_cand = mean_cand / (sd_cand / np.sqrt(n_cand))
    mean_ctrl = ctrl_net.mean()
    sd_ctrl = ctrl_net.std(ddof=1)
    increment = mean_cand - mean_ctrl

    cand_entry_mins = np.array([r["entry_min"] for _, r in cand_rows], dtype=int)
    cand_to_mins = np.array([r["to_min"] for _, r in cand_rows], dtype=int)

    # ---- family draw: B3 circular-shift offsets FIRST, then B2(ii) random draws ----
    rng = np.random.default_rng(SEED)
    offsets = rng.integers(1, N, size=N_NULL)

    # B3: circular-shift the bottom-state indicator over ordered classified sessions;
    # candidate-null mean = mean net over sessions where rolled_bottom==1 AND takeout==1.
    net_by_d = {d: r["net"] for d, r in cand_rows}
    for d in ctrl_idx:
        r = trade(d, 0)
        if r is not None:
            net_by_d[d] = r["net"]                # takeout sessions carry a tradeable net
    pop_order = list(pop.index)
    bottom_vec = pop["bottom"].to_numpy().astype(bool)
    takeout_vec = pop["takeout"].to_numpy().astype(bool)
    net_vec = np.array([net_by_d.get(d, np.nan) for d in pop_order], dtype=float)
    tradeable = takeout_vec & np.isfinite(net_vec)   # sessions with a valid long trade
    null_means = np.empty(N_NULL)
    for j, k in enumerate(offsets):
        sel = np.roll(bottom_vec, k) & tradeable
        null_means[j] = net_vec[sel].mean() if sel.any() else np.nan
    null_means = null_means[np.isfinite(null_means)]
    p95_b3 = np.percentile(null_means, 95.0)
    p_one_b3 = (1 + int((null_means >= mean_cand).sum())) / (len(null_means) + 1)

    # effective-K (CLAUDE.md 4): lag-1 autocorr of the ordered candidate net series
    cn = cand_net - cand_net.mean()
    rho1 = float(np.dot(cn[:-1], cn[1:]) / np.dot(cn, cn)) if len(cn) > 2 else 0.0
    K_eff = n_cand / (1 + (n_cand - 1) * max(rho1, 0.0))

    # B2(ii): count-matched random-session longs at RESAMPLED takeout times.
    # Precompute net matrix M[pool_session, unique_takeout_minute]: enter at first bar
    # STRICTLY AFTER the (resampled) takeout minute, exit 15:59 close, POINTS, $40 RT.
    pool_ds = pop_order                              # all classified sessions
    uniq_to = np.unique(cand_to_mins)
    to_col = {m: c for c, m in enumerate(uniq_to)}
    M = np.full((len(pool_ds), len(uniq_to)), np.nan)
    for ri, d in enumerate(pool_ds):
        rec = aft_by_d.get(d)
        if rec is None:
            continue
        exit_close = _exit_close(rec)
        if not np.isfinite(exit_close):
            continue
        tmin, opens = rec["tmin"], rec["open"]
        for m in uniq_to:
            pos = np.searchsorted(tmin, m, side="right")  # first bar with time > m
            if pos < len(tmin) and tmin[pos] <= exit_min:
                M[ri, to_col[m]] = (exit_close - opens[pos]) * POINT_USD - COST_ALLIN
    # column index for each observed candidate takeout minute (the resample source)
    cand_to_colidx = np.array([to_col[m] for m in cand_to_mins], dtype=int)
    n_pool = len(pool_ds)
    rnd_means = np.empty(N_RANDOM)
    for j in range(N_RANDOM):
        rows = rng.integers(0, n_pool, size=n_cand)
        cols = cand_to_colidx[rng.integers(0, n_cand, size=n_cand)]  # resampled to-times
        vals = M[rows, cols]
        m = vals[np.isfinite(vals)]
        rnd_means[j] = m.mean() if len(m) else np.nan
    rnd_means = rnd_means[np.isfinite(rnd_means)]
    p95_b2ii = np.percentile(rnd_means, 95.0)
    p_one_b2ii = (1 + int((rnd_means >= mean_cand).sum())) / (len(rnd_means) + 1)

    # ---- delay curve (timing-teeth) on the COMMON enterable subset -----------------
    delay_rows = {dl: [] for dl in DELAYS}
    common_mask = []
    per_delay_all = {dl: [] for dl in DELAYS}
    for d, _ in cand_rows:
        rr = {dl: trade(d, dl) for dl in DELAYS}
        ok_all = all(v is not None for v in rr.values())
        common_mask.append(ok_all)
        for dl in DELAYS:
            if rr[dl] is not None:
                per_delay_all[dl].append(rr[dl]["net"])
            if ok_all:
                delay_rows[dl].append(rr[dl]["net"])
    n_common = int(sum(common_mask))
    delay_stat = {}
    for dl in DELAYS:
        arr = np.array(delay_rows[dl], dtype=float)
        m = arr.mean()
        t = m / (arr.std(ddof=1) / np.sqrt(len(arr))) if len(arr) > 1 else float("nan")
        delay_stat[dl] = {"n": len(arr), "mean": m, "t": t,
                          "n_avail": len(per_delay_all[dl]),
                          "mean_avail": float(np.mean(per_delay_all[dl]))}
    base_mean = delay_stat[0]["mean"]
    mean_30 = delay_stat[30]["mean"]
    # decay band: +30 must lose >= 40% of mean net (only meaningful for a positive base)
    if base_mean > 0:
        loss_frac_30 = (base_mean - mean_30) / base_mean
        band_ok = loss_frac_30 >= DELAY_BAND_FRAC
        curve_decays = band_ok and (mean_30 < base_mean)
    else:
        loss_frac_30 = float("nan")
        band_ok = False
        curve_decays = False   # a non-positive base cannot exhibit a flush-decay to defend

    # ---- MDEs -----------------------------------------------------------------------
    mde_b1_usd = Z_POWER * sd_cand / np.sqrt(n_cand)                      # B1 mean-MDE
    mde_b1_eff = Z_POWER * sd_cand / np.sqrt(K_eff)                        # effective-K adj
    mde_incr_usd = Z_POWER * np.sqrt(sd_cand**2 / n_cand + sd_ctrl**2 / n_ctrl)  # B2 incr-MDE

    span_days = (pd.Timestamp(pop.index[-1]) - pd.Timestamp(pop.index[0])).days
    years = span_days / 365.25
    events_yr = n_cand / years

    # ============================ PRINT: POWER / MDE BARRIER =========================
    emit()
    emit("#" * 96)
    emit("G1 BARRIER — POWER BLOCK (n, events/yr, pre/post-breach decomp, MDEs) BEFORE any")
    emit("            return table. NOTHING about observed means is printed above this line.")
    emit("#" * 96)
    emit(f"population: {n_joined} joined sessions; {n_dropped_quality} dropped by quality; "
         f"{n_all} valid; {WARMUP} warm-up; {N} classified "
         f"({pop.index[0]} .. {pop.index[-1]}, {years:.2f} yr)")
    emit(f"pre/post-breach decomposition of bottom-tercile (n={n_bottom}): "
         f"BREACHED/took-out morning low = {len(cand_idx)} (candidate events); "
         f"NOT-breached = {n_notbreach}")
    emit(f"candidate tradeable events: n_cand = {n_cand} "
         f"(unenterable-at/before-15:59 dropped = {cand_unenter})   EVENTS/YR = {events_yr:.1f}")
    emit(f"control (non-bottom takeout) tradeable: n_ctrl = {n_ctrl} "
         f"(spec ~258; unenterable dropped = {ctrl_unenter})")
    emit(f"B1 mean-MDE  (Z*sd/sqrt(n), a=.05 two-sided, power=.80): ${mde_b1_usd:.2f}/event  "
         f"[sd=${sd_cand:.2f}, n={n_cand}]")
    emit(f"   effective-K note: rho1(net)={rho1:+.4f} -> K_eff={K_eff:.1f}; "
         f"effective-K mean-MDE = ${mde_b1_eff:.2f}/event")
    emit(f"B2 increment-MDE (two-sample cand vs control): ${mde_incr_usd:.2f}/event  "
         f"[sd_ctrl=${sd_ctrl:.2f}, n_ctrl={n_ctrl}]")
    emit("(cost basis: ALL_IN $40/RT — p90-spread regime, EXEC01-derived stressed floor)")

    # ============================ PRINT: RETURN TABLE ===============================
    def row(name: str, v: np.ndarray) -> str:
        m = v.mean()
        t = m / (v.std(ddof=1) / np.sqrt(len(v)))
        return (f"{name:<52}| {len(v):>5} | {m:>+10.2f} | {t:>+7.2f} | "
                f"{v.sum():>+12.0f} | {(v > 0).mean() * 100:>6.1f}%")

    emit()
    emit("---- RETURN TABLE (net $/event; POINTS gross x $20/pt; ALL_IN $40/RT) ----")
    emit(f"{'LEG':<52}| {'n':>5} | {'mean/ev':>10} | {'t':>7} | {'total $':>12} | winrate")
    emit("-" * 104)
    emit(row("CANDIDATE rebound-long bottom-tercile takeout", cand_net))
    emit(row("CONTROL rebound-long NON-tercile takeout (B2i)", ctrl_net))
    emit("-" * 104)
    emit(f"candidate gross: {(mean_cand + COST_ALLIN) / POINT_USD:+.2f} pts/event; "
         f"increment (cand - control) = ${increment:+.2f}/event")
    # non-gate cost sensitivity (printed, never a gate)
    ng2501 = ((cand_net + COST_ALLIN) - COST_NG_2501)
    ng3300 = ((cand_net + COST_ALLIN) - COST_NG_3300)
    emit(f"NON-gate cost sensitivity: mean net @ $25.01={ng2501.mean():+.2f}, "
         f"@ $33.00={ng3300.mean():+.2f}, @ $40.00(gate)={mean_cand:+.2f}")

    # ============================ PRINT: B2 DUAL CONTROLS ===========================
    b1_pass = (mean_cand > 0) and (t_cand >= 2.0)
    b2i_control_ge = mean_ctrl >= mean_cand
    b2i_incr_zero = abs(increment) < 1e-9
    b2i_pass = (increment > 0) and (not b2i_control_ge)
    b2ii_pass = mean_cand > p95_b2ii
    b3_pass = mean_cand > p95_b3

    emit()
    emit("---- B2(i) PRIMARY DISCRIMINATOR (identical trigger, non-tercile takeout) ----")
    emit(f"  candidate mean net    = ${mean_cand:+.2f}/event (n={n_cand})")
    emit(f"  control  mean net     = ${mean_ctrl:+.2f}/event (n={n_ctrl})")
    emit(f"  increment (cand-ctrl) = ${increment:+.2f}/event   increment-MDE = ${mde_incr_usd:.2f}")
    emit(f"  entry time-of-day (min-of-day) median: cand={np.median(cand_entry_mins):.0f} "
         f"({int(np.median(cand_entry_mins))//60:02d}:{int(np.median(cand_entry_mins))%60:02d}), "
         f"ctrl={np.median(ctrl_entry_mins):.0f} "
         f"({int(np.median(ctrl_entry_mins))//60:02d}:{int(np.median(ctrl_entry_mins))%60:02d})")
    emit(f"  -> control>=candidate: {b2i_control_ge}    increment~=0: {b2i_incr_zero}")

    emit()
    emit(f"---- B2(ii) count-matched random-session longs @ resampled takeout times "
         f"(N={len(rnd_means)}) ----")
    emit(f"  observed cand mean=${mean_cand:+.2f}  vs  p95(random)=${p95_b2ii:+.2f}  "
         f"p50=${np.percentile(rnd_means,50):+.2f}  p_one={p_one_b2ii:.4f}  -> "
         f"{'BEATEN' if b2ii_pass else 'NOT BEATEN'}")

    emit()
    emit(f"---- B3 circular-shift null on STATE series (N={len(null_means)}, seed={SEED}, "
         f"family-shared offsets) ----")
    emit(f"  observed cand mean=${mean_cand:+.2f}  vs  p95(null)=${p95_b3:+.2f}  "
         f"p_one={p_one_b3:.4f}  K_eff={K_eff:.1f}  -> {'BEATEN' if b3_pass else 'NOT BEATEN'}")

    # ============================ PRINT: TIMING-TEETH ===============================
    emit()
    emit(f"---- TIMING-TEETH delay curve (common enterable subset n={n_common}) ----")
    emit(f"  {'delay':>6} | {'n':>4} | {'mean/ev':>10} | {'t':>7} | {'mean(all avail)':>15}")
    for dl in DELAYS:
        st = delay_stat[dl]
        emit(f"  +{dl:>4}m | {st['n']:>4} | {st['mean']:>+10.2f} | {st['t']:>+7.2f} | "
             f"{st['mean_avail']:>+15.2f} (n={st['n_avail']})")
    emit(f"  band: +30m must lose >= {DELAY_BAND_FRAC*100:.0f}% of mean net. "
         f"base=${base_mean:+.2f}, +30=${mean_30:+.2f}, loss_frac={loss_frac_30 if np.isfinite(loss_frac_30) else float('nan'):.3f}")
    if base_mean <= 0:
        emit("  NOTE: base mean net is NOT positive -> there is no positive flush-edge for a "
             "delay to erode; the decay band is VACUOUS and the mechanism is not defended here.")
    emit(f"  curve_decays_per_band = {curve_decays}")

    # ============================ PRINT: CONCENTRATION ==============================
    tot_abs = np.abs(cand_net).sum()
    top1_share = np.abs(cand_net).max() / tot_abs if tot_abs > 0 else float("nan")
    order = np.argsort(-np.abs(cand_net))
    top5_share = np.abs(cand_net)[order[:5]].sum() / tot_abs if tot_abs > 0 else float("nan")
    emit()
    emit("---- CONCENTRATION (CLASSIFICATION ONLY — never a kill-gate) ----")
    emit(f"  top-1 |event| share of sum|net| = {top1_share*100:.1f}% ; "
         f"top-5 share = {top5_share*100:.1f}%")
    emit(f"  carried classification note: {INCUMBENT_F9_NOTE}")

    # ============================ VERDICT (taxonomy) ================================
    if b2i_control_ge or b2i_incr_zero:
        verdict = "CLOSED-AS-GENERIC-MR"
        verdict_note = ("B2(i) control >= candidate (or increment ~= 0): the rebound-long "
                        "collapses onto SWEEP01 + W118 generic post-cross MR. PERMANENT.")
    elif b1_pass and b2i_pass and b2ii_pass and b3_pass and curve_decays:
        verdict = "SURVIVES"
        verdict_note = ("B1 + B2(i) + B2(ii) + B3 pass, identified, delay curve decays per "
                        "band. Licenses robustness + gated era leg ONLY, never promotion.")
    elif (increment > 0) and (increment < mde_incr_usd):
        verdict = "CLOSED-BY-POWER"
        verdict_note = ("increment positive but under the printed increment-MDE at this exact "
                        "scope — a WEAKER closure, NOT 'closed for good'.")
    else:
        verdict = "CLOSED-AS-GENERIC-MR"
        verdict_note = ("B2(i) not passed and increment not a powered positive: closes onto "
                        "generic post-cross MR at this scope.")

    survives_info_gate = bool(b1_pass and b2i_pass and b2ii_pass and b3_pass and curve_decays)

    # ============================ GATE TABLE (printed by program) ===================
    emit()
    emit("GATE TABLE (printed by program)")
    emit(f"{'GATE':<26}| {'SPEC':<44}| {'MDE / OBSERVED':<44}| PASS-FAIL")
    emit("-" * 128)
    rows = [
        ("G0 seal/points", "max session <= 2026-05-31; POINTS basis",
         f"maxTICK={max_tick_d} maxNQ={max_nq_d}; POINTS", "PASS" if seal_ok else "FAIL"),
        ("G1a manifest/prov", "sha256 match both substrates",
         f"TICK={tick_ok} NQ={nq_ok}", "PASS" if tick_ok and nq_ok else "FAIL"),
        ("G1b MDE-first barrier", "B1 mean-MDE AND B2 incr-MDE before returns",
         f"B1-MDE ${mde_b1_usd:.0f}; incr-MDE ${mde_incr_usd:.0f} (printed first)", "PASS"),
        ("B1 economics", "mean net > 0 AND event-clustered t >= 2.0",
         f"mean=${mean_cand:+.2f}, t={t_cand:+.2f}", "PASS" if b1_pass else "FAIL"),
        ("B2(i) PRIMARY", "beats identical trigger, non-tercile takeout",
         f"incr=${increment:+.2f} (cand {mean_cand:+.0f} vs ctrl {mean_ctrl:+.0f})",
         "PASS" if b2i_pass else "FAIL"),
        ("B2(ii) random", ">p95 of >=10k count-matched random longs",
         f"obs ${mean_cand:+.2f} vs p95 ${p95_b2ii:+.2f}", "PASS" if b2ii_pass else "FAIL"),
        ("B3 circular-shift", "obs > p95 state-series shift null (K_eff)",
         f"obs ${mean_cand:+.2f} vs p95 ${p95_b3:+.2f}, K_eff={K_eff:.0f}",
         "PASS" if b3_pass else "FAIL"),
        ("timing-teeth", "+30m loses >=40%; FLAT curve falsifies",
         f"base ${base_mean:+.0f} -> +30 ${mean_30:+.0f}; decays={curve_decays}",
         "PASS" if curve_decays else "FAIL/NA"),
        ("concentration", "CLASSIFICATION ONLY (not a kill-gate)",
         f"top1 {top1_share*100:.0f}%; F9 note carried", "INFO"),
    ]
    for gname, spec_c, obs_c, pf in rows:
        emit(f"{gname:<26}| {spec_c:<44}| {obs_c:<44}| {pf}")
    emit("-" * 128)
    emit(f"VERDICT (trial G00055 / MC-58): {verdict}")
    emit(f"  {verdict_note}")
    emit(f"survives_info_gate = {survives_info_gate}")
    emit("REGIME-LOCAL: 2023-01 -> 2026-05-31 internals population only; ERA leg NOT in this run.")
    emit("evidence-status: DISCOVERY_CONSUMED")

    # ---- write gate_table.txt -------------------------------------------------------
    with open(os.path.join(OUT, "gate_table.txt"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")

    # ---- event_table.csv ------------------------------------------------------------
    ev = pd.DataFrame({
        "date": [d for d, _ in cand_rows],
        "cum11": [pop.loc[d, "cum11"] for d, _ in cand_rows],
        "tercile_boundary": [pop.loc[d, "thr_bot"] for d, _ in cand_rows],
        "morn_low": [pop.loc[d, "morn_low"] for d, _ in cand_rows],
        "aft_low": [pop.loc[d, "aft_low"] for d, _ in cand_rows],
        "takeout_min": [r["to_min"] for _, r in cand_rows],
        "entry_min": [r["entry_min"] for _, r in cand_rows],
        "entry_open": [r["entry_open"] for _, r in cand_rows],
        "exit_close_1559": [r["exit_close"] for _, r in cand_rows],
        "gross_pts": [r["gross_pts"] for _, r in cand_rows],
        "net_usd_allin40": [r["net"] for _, r in cand_rows],
    })
    ev.to_csv(os.path.join(OUT, "event_table.csv"), index=False, float_format="%.4f")

    # ---- delay_curve.csv ------------------------------------------------------------
    dc = pd.DataFrame({
        "delay_min": DELAYS,
        "n_common": [delay_stat[dl]["n"] for dl in DELAYS],
        "mean_net_common": [delay_stat[dl]["mean"] for dl in DELAYS],
        "t_common": [delay_stat[dl]["t"] for dl in DELAYS],
        "n_avail": [delay_stat[dl]["n_avail"] for dl in DELAYS],
        "mean_net_avail": [delay_stat[dl]["mean_avail"] for dl in DELAYS],
    })
    dc.to_csv(os.path.join(OUT, "delay_curve.csv"), index=False, float_format="%.4f")

    # ---- ledger fragment (pending; coordinator records serially) --------------------
    frag = {
        "trial_id": "G00055",
        "mc_id": "MC-58 (breadth-washout rebound, long, modern leg)",
        "run_id": "G2_F14_MC58_REBOUND_20260906",
        "date": "2026-09-06",
        "question": "does the +9.62pp G00030 washout state monetize as a REBOUND long "
                    "(vs the same trigger off non-tercile takeouts)?",
        "population": {"sessions_classified": N, "bottom_tercile": n_bottom,
                       "candidate_events": n_cand, "control_events": n_ctrl,
                       "span": [str(pop.index[0]), str(pop.index[-1])],
                       "events_per_year": round(events_yr, 1)},
        "power": {"b1_mean_mde_usd": round(mde_b1_usd, 2),
                  "b1_mean_mde_effK_usd": round(mde_b1_eff, 2),
                  "b2_increment_mde_usd": round(mde_incr_usd, 2),
                  "K_eff": round(K_eff, 1), "rho1": round(rho1, 4)},
        "observed": {
            "cand_mean_net_usd_allin40": round(float(mean_cand), 2),
            "cand_t": round(float(t_cand), 3),
            "ctrl_mean_net_usd": round(float(mean_ctrl), 2),
            "increment_usd": round(float(increment), 2),
            "b2ii_p95_random_usd": round(float(p95_b2ii), 2),
            "b2ii_p_one": round(float(p_one_b2ii), 4),
            "b3_p95_null_usd": round(float(p95_b3), 2),
            "b3_p_one": round(float(p_one_b3), 4),
            "delay_base_usd": round(float(base_mean), 2),
            "delay_plus30_usd": round(float(mean_30), 2),
            "curve_decays_per_band": bool(curve_decays),
            "top1_concentration_share": round(float(top1_share), 4),
            "n_null": len(null_means), "n_random": len(rnd_means), "seed": SEED,
        },
        "gates": {"B1": "PASS" if b1_pass else "FAIL",
                  "B2i": "PASS" if b2i_pass else "FAIL",
                  "B2ii": "PASS" if b2ii_pass else "FAIL",
                  "B3": "PASS" if b3_pass else "FAIL",
                  "timing_teeth": "PASS" if curve_decays else "FAIL/NA"},
        "verdict": verdict,
        "survives_info_gate": survives_info_gate,
        "regime_scope": "REGIME-LOCAL 2023-01 -> 2026-05-31; era leg NOT in run",
        "evidence_status": "DISCOVERY_CONSUMED",
        "promotion": "NONE",
        "spend_usd": 0,
        "live_enabled": False,
        "artifacts": ["runs/G2_F14_MC58_REBOUND_20260906/out/gate_table.txt",
                      "runs/G2_F14_MC58_REBOUND_20260906/out/event_table.csv",
                      "runs/G2_F14_MC58_REBOUND_20260906/out/delay_curve.csv",
                      "runs/G2_F14_MC58_REBOUND_20260906/src/run_mc58.py"],
    }
    with open(os.path.join(OUT, "ledger_result_pending.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(frag, f, indent=2)
    print("\nwrote out/gate_table.txt, out/event_table.csv, out/delay_curve.csv, "
          "out/ledger_result_pending.json")


if __name__ == "__main__":
    main()
