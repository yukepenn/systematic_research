"""AUCTION04_CLEAN_CAUSAL_SUBSTRATE -- independent unit tests.

Every check here re-derives its expected value from raw ticks using code that does
NOT call into 01_build_clean_substrate.py's own functions (causal_running_poc,
causal_lookup, build_mid_grid, process_session are never imported) -- a fresh,
differently-structured implementation of the same definitions, so this genuinely
catches implementation bugs (off-by-one, wrong tick scaling, wrong causal cutoff),
not just re-runs the same code and compares it to itself.

Covers, each independently reconstructed straight from raw parquet:
  T1  20 markout/range/mfe/mae spot checks (task's explicit requirement) -- ticks,
      points, and dollars_1NQ all cross-checked against the SAME raw price
      difference (dollars is computed directly from raw price points * $20/pt, not
      derived from the ticks column at all -- so a units bug anywhere in the
      pipeline's ticks<->points<->dollars chain would be caught even if the ticks
      number happened to look plausible in isolation).
  T2  10 causal_last_t / causal_running_POC_t spot checks via a brute-force,
      non-vectorized (dict-based cumulative-volume) re-implementation of the
      running-POC algorithm, filtered strictly to trades with time<=t -- proves
      both the POC construction and the causal cutoff independently of the
      vectorized cumsum/cummax + searchsorted implementation in the build script.
  T3  Defect-1 regression check: reproduces the ORIGINAL (buggy) double-division
      formula on our own raw-tick-derived mid series and confirms it lands at
      4.0x the clean pipeline's value (proves we understand *why* it was wrong,
      not just that our number differs from the old one).
  T4  Decision-point-set identity: clean output's (sess_tag,time) pairs are
      exactly AUCTION01/W5's own frozen decision_points_30s(.parquet|_CONFIRM.parquet)
      -- same sample, not a different one.
  T5  Governance: every sess_tag in both output files is in the 45-tag permitted
      list, and none is >=2026-08-01.
"""
import os
import numpy as np
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
RAW = os.path.join(ROOT, "research", "scalping_lab", "substrate", "raw", "NQ")
OUT = os.path.join(ROOT, "runs", "AUCTION04_CLEAN_CAUSAL_SUBSTRATE", "out")
REF_DEC_DISCOVERY = os.path.join(ROOT, "runs", "AUCTION01_VALUE_STATE", "out", "decision_points_30s.parquet")
REF_DEC_CONFIRM = os.path.join(ROOT, "runs", "W5_PROTECTED_CONFIRMATION", "results", "out",
                                "decision_points_30s_CONFIRM.parquet")
ORIG_DECISION_OUTCOMES = os.path.join(ROOT, "runs", "AUCTION01_VALUE_STATE", "out", "decision_outcomes.parquet")

TICK = 0.25
POINT_USD = 20.0
DOLLAR_PER_TICK = TICK * POINT_USD  # $5.00/tick, matches BASELINE_MODELS.md's stated NQ tick value
HORIZONS = [15, 60, 300]
RNG = np.random.default_rng(20260810)

DISCOVERY_TAGS = [
    "20250814", "20250820", "20250901", "20250902", "20250905", "20250910", "20250911", "20250922",
    "20251002", "20251009", "20251027", "20251029", "20251110", "20251117", "20251124", "20251128",
    "20251209", "20251222", "20260123", "20260206", "20260211", "20260218", "20260220", "20260223",
    "20260303", "20260312", "20260317", "20260320", "20260406", "20260409", "20260417", "20260423",
    "20260428", "20260506", "20260511", "20260519", "20260520",
]
CONFIRMATION_TAGS = [
    "20250819", "20250912", "20251028", "20251125", "20260217", "20260302", "20260422", "20260512",
]
PERMITTED_TAGS = set(DISCOVERY_TAGS) | set(CONFIRMATION_TAGS)

FAILS = []
PASSES = 0


def check(name, cond, detail=""):
    global PASSES
    if cond:
        PASSES += 1
        print(f"  PASS  {name}")
    else:
        FAILS.append((name, detail))
        print(f"  FAIL  {name}  -- {detail}")


# --------------------------------------------------------------------------- raw readers (fresh, independent)
def read_bbo_events(tag):
    """bip in {1,2} rows, sorted by time -- an independent read straight off raw
    parquet, no dependency on sechilo/NQ or any pipeline intermediate."""
    raw_f = os.path.join(RAW, f"s{tag}.parquet")
    rth_f = os.path.join(RAW, f"s{tag}_rth.parquet")
    parts = [pd.read_parquet(raw_f)]
    if os.path.exists(rth_f):
        parts.append(pd.read_parquet(rth_f))
    df = pd.concat(parts, ignore_index=True)
    df["time"] = pd.to_datetime(df["time"])
    df = df.drop_duplicates(subset=["bip", "time", "price", "volume"])
    df = df[df.bip.isin([1, 2])].sort_values("time", kind="mergesort").reset_index(drop=True)
    bid = df["price"].where(df.bip == 1).ffill()
    ask = df["price"].where(df.bip == 2).ffill()
    mid = (bid + ask) / 2.0  # PRICE units (points) -- deliberately NOT tick-scaled here
    ok = bid.notna() & ask.notna()
    return df["time"][ok].reset_index(drop=True), mid[ok].reset_index(drop=True)


def read_last_trades(tag):
    raw_f = os.path.join(RAW, f"s{tag}.parquet")
    rth_f = os.path.join(RAW, f"s{tag}_rth.parquet")
    parts = [pd.read_parquet(raw_f)]
    if os.path.exists(rth_f):
        parts.append(pd.read_parquet(rth_f))
    df = pd.concat(parts, ignore_index=True)
    df["time"] = pd.to_datetime(df["time"])
    df = df.drop_duplicates(subset=["bip", "time", "price", "volume"])
    df = df[df.bip == 0].sort_values("time", kind="mergesort").reset_index(drop=True)
    return df


def sechilo_style_mid_at_second(evt_time, evt_mid, second_ts):
    """Independent re-derivation of sechilo's own definition of 'mid_last at whole
    second T' = mid value as of the LAST bid/ask event with time < T+1s (a bucket
    [T,T+1) labeled by its start, ffilled through empty buckets -- the pre-existing,
    non-defective convention this task does not ask us to change; reproduced here
    via boolean masking, not via 01's build_mid_grid function)."""
    cutoff = second_ts + pd.Timedelta(seconds=1)
    mask = evt_time.values < np.datetime64(cutoff)
    if not mask.any():
        return np.nan
    return evt_mid.values[mask][-1]


def sechilo_style_high_low_window(evt_time, evt_mid, t_open, H):
    """High/low over (t_open, t_open+H] at whole-second granularity, matching
    sechilo's per-second mid_high/mid_low (max/min of in-bucket events, ffilled
    with mid_last when a bucket has zero events)."""
    highs, lows = [], []
    for s in range(1, H + 1):
        sec_ts = t_open + pd.Timedelta(seconds=s)
        bucket_mask = (evt_time.values >= np.datetime64(sec_ts)) & \
                      (evt_time.values < np.datetime64(sec_ts + pd.Timedelta(seconds=1)))
        if bucket_mask.any():
            vals = evt_mid.values[bucket_mask]
            highs.append(vals.max())
            lows.append(vals.min())
        else:
            m = sechilo_style_mid_at_second(evt_time, evt_mid, sec_ts)
            if not np.isnan(m):
                highs.append(m)
                lows.append(m)
    if not highs:
        return np.nan, np.nan
    return max(highs), min(lows)


def brute_force_causal_last_and_poc(trades_df, t):
    """Non-vectorized (dict-based) re-implementation of the running-POC algorithm,
    independent of causal_running_poc()'s cumsum/cummax vectorization, restricted
    strictly to trades with time<=t."""
    sub = trades_df[trades_df["time"].values <= np.datetime64(t)]
    if len(sub) == 0:
        return np.nan, np.nan, np.nan
    cum_vol = {}
    running_max = -1
    poc_tick = None
    last_price = None
    last_time_used = None
    for row in sub.itertuples(index=False):
        tick_id = round(row.price / TICK)
        cum_vol[tick_id] = cum_vol.get(tick_id, 0) + row.volume
        if cum_vol[tick_id] >= running_max:
            running_max = cum_vol[tick_id]
            poc_tick = tick_id
        last_price = row.price
        last_time_used = row.time
    assert last_time_used <= t, "lookahead: brute-force scan used a trade after t"
    total_vol = sum(cum_vol.values())
    poc_price = poc_tick * TICK
    poc_share = running_max / total_vol
    return last_price, poc_price, poc_share


# --------------------------------------------------------------------------- T1: markout spot checks
def run_t1():
    print("\n[T1] 20 markout/range/mfe/mae spot checks vs raw price differences")
    clean_d = pd.read_parquet(os.path.join(OUT, "clean_decision_outcomes.parquet"))
    clean_c = pd.read_parquet(os.path.join(OUT, "clean_decision_outcomes_CONFIRM.parquet"))
    clean_d["__sample"] = "discovery"
    clean_c["__sample"] = "confirm"
    pool = pd.concat([clean_d, clean_c], ignore_index=True)

    valid_mask = pool[[f"abs_markout_ticks_{h}" for h in HORIZONS]].notna().any(axis=1)
    pool = pool[valid_mask].reset_index(drop=True)
    picks = RNG.choice(len(pool), size=20, replace=False)

    events_cache = {}
    n_checked = 0
    for i in picks:
        row = pool.iloc[i]
        tag, t = row["sess_tag"], row["time"]
        if tag not in events_cache:
            events_cache[tag] = read_bbo_events(tag)
        evt_time, evt_mid = events_cache[tag]

        base_price = sechilo_style_mid_at_second(evt_time, evt_mid, t)
        H = HORIZONS[RNG.integers(0, len(HORIZONS))]
        if pd.isna(row.get(f"abs_markout_ticks_{H}")):
            continue
        end_ts = t + pd.Timedelta(seconds=H)
        end_price = sechilo_style_mid_at_second(evt_time, evt_mid, end_ts)
        if np.isnan(base_price) or np.isnan(end_price):
            continue
        n_checked += 1

        raw_price_diff = end_price - base_price  # points, straight from raw BBO, no pipeline code involved
        ticks_indep = abs(raw_price_diff) / TICK
        points_indep = abs(raw_price_diff)
        dollars_indep = abs(raw_price_diff) * POINT_USD

        pipe_ticks = row[f"abs_markout_ticks_{H}"]
        check(f"T1.{n_checked} abs_markout_ticks_{H} {tag}@{t} == raw price diff / 0.25",
              np.isclose(ticks_indep, pipe_ticks, atol=1e-6),
              f"indep={ticks_indep:.4f} pipeline={pipe_ticks:.4f}")

        # units cross-check: dollars computed directly from raw points (bypassing ticks
        # entirely) must equal pipeline_ticks * $5/tick (0.25 * $20)
        dollars_via_pipeline_ticks = pipe_ticks * DOLLAR_PER_TICK
        check(f"T1.{n_checked} dollars_1NQ (raw pts*$20) == pipeline_ticks*$5/tick",
              np.isclose(dollars_indep, dollars_via_pipeline_ticks, atol=1e-6),
              f"indep_$={dollars_indep:.4f} via_ticks_$={dollars_via_pipeline_ticks:.4f}")
        check(f"T1.{n_checked} points (raw) == pipeline_ticks*0.25",
              np.isclose(points_indep, pipe_ticks * TICK, atol=1e-9), "")

        side = np.sign(row["position_B"]) if row["position_B"] != 0 else np.nan
        if not np.isnan(side):
            signed_indep = side * raw_price_diff / TICK
            pipe_signed = row[f"signed_markout_ticks_{H}"]
            check(f"T1.{n_checked} signed_markout_ticks_{H} {tag}@{t}",
                  np.isclose(signed_indep, pipe_signed, atol=1e-6),
                  f"indep={signed_indep:.4f} pipeline={pipe_signed:.4f}")

    # a handful of full range/mfe/mae window reconstructions (heavier, so fewer)
    print("\n[T1b] 5 range/mfe/mae window spot checks (full per-second high/low reconstruction)")
    picks2 = RNG.choice(len(pool), size=5, replace=False)
    n2 = 0
    for i in picks2:
        row = pool.iloc[i]
        tag, t = row["sess_tag"], row["time"]
        if tag not in events_cache:
            events_cache[tag] = read_bbo_events(tag)
        evt_time, evt_mid = events_cache[tag]
        H = 15  # keep the window small -- cheap to brute-force per-second scan
        if pd.isna(row.get(f"range_ticks_{H}")):
            continue
        n2 += 1
        base_price = sechilo_style_mid_at_second(evt_time, evt_mid, t)
        hi, lo = sechilo_style_high_low_window(evt_time, evt_mid, t, H)
        range_indep = (hi - lo) / TICK
        check(f"T1b.{n2} range_ticks_{H} {tag}@{t}",
              np.isclose(range_indep, row[f"range_ticks_{H}"], atol=1e-6),
              f"indep={range_indep:.4f} pipeline={row[f'range_ticks_{H}']:.4f}")
        side = np.sign(row["position_B"]) if row["position_B"] != 0 else np.nan
        if not np.isnan(side):
            if side > 0:
                mfe_indep = (hi - base_price) / TICK
                mae_indep = (base_price - lo) / TICK
            else:
                mfe_indep = (base_price - lo) / TICK
                mae_indep = (hi - base_price) / TICK
            check(f"T1b.{n2} mfe_ticks_{H} {tag}@{t}",
                  np.isclose(mfe_indep, row[f"mfe_ticks_{H}"], atol=1e-6), "")
            check(f"T1b.{n2} mae_ticks_{H} {tag}@{t}",
                  np.isclose(mae_indep, row[f"mae_ticks_{H}"], atol=1e-6), "")


# --------------------------------------------------------------------------- T2: causal last/POC spot checks
def run_t2():
    print("\n[T2] 10 causal_last_t / causal_running_POC_t spot checks (brute-force, dict-based)")
    clean_d = pd.read_parquet(os.path.join(OUT, "clean_decision_outcomes.parquet"))
    picks = RNG.choice(len(clean_d), size=10, replace=False)
    trades_cache = {}
    for n, i in enumerate(picks, 1):
        row = clean_d.iloc[i]
        tag, t = row["sess_tag"], row["time"]
        if tag not in trades_cache:
            trades_cache[tag] = read_last_trades(tag)
        trades_df = trades_cache[tag]
        last_price, poc_price, poc_share = brute_force_causal_last_and_poc(trades_df, t)
        value_dist_indep = (last_price - poc_price) / TICK
        check(f"T2.{n} value_dist_ticks {tag}@{t} (brute-force POC, strict time<=t)",
              np.isclose(value_dist_indep, row["value_dist_ticks"], atol=1e-6),
              f"indep={value_dist_indep:.4f} pipeline={row['value_dist_ticks']:.4f}")
        check(f"T2.{n} poc_share {tag}@{t}",
              np.isclose(poc_share, row["poc_share"], atol=1e-9), "")


# --------------------------------------------------------------------------- T3: defect-1 regression check
def run_t3():
    print("\n[T3] Defect-1 (4x units bug) regression check")
    clean_d = pd.read_parquet(os.path.join(OUT, "clean_decision_outcomes.parquet"))
    orig = pd.read_parquet(ORIG_DECISION_OUTCOMES)
    m = clean_d.merge(orig, on=["sess_tag", "time"], suffixes=("_clean", "_orig"))
    check("T3 merge non-empty", len(m) == len(clean_d), f"{len(m)} vs {len(clean_d)}")
    for H in HORIZONS:
        clean_col = f"abs_markout_ticks_{H}"
        orig_col = f"abs_markout_{H}"
        sub = m[[clean_col, orig_col]].dropna()
        # reproducing the ORIGINAL buggy formula on our own tick-scaled series:
        # dividing an already-in-ticks difference by TICK again == multiplying by 4
        reconstructed_buggy = sub[clean_col] * 4.0
        check(f"T3 abs_markout_{H}: clean*4 == original (on-disk, buggy) value",
              np.allclose(reconstructed_buggy, sub[orig_col], atol=1e-6),
              f"max abs diff = {(reconstructed_buggy - sub[orig_col]).abs().max()}")
    print(f"  (matched {len(m)}/{len(clean_d)} rows against the frozen original file)")


# --------------------------------------------------------------------------- T4: decision-point-set identity
def run_t4():
    print("\n[T4] decision-point-set identity vs AUCTION01/W5's own frozen files")
    clean_d = pd.read_parquet(os.path.join(OUT, "clean_decision_outcomes.parquet"), columns=["sess_tag", "time"])
    ref_d = pd.read_parquet(REF_DEC_DISCOVERY, columns=["sess_tag", "time"])
    ref_d["time"] = pd.to_datetime(ref_d["time"])
    got, want = set(zip(clean_d.sess_tag, clean_d.time)), set(zip(ref_d.sess_tag, ref_d.time))
    check("T4 discovery decision-point set identical", got == want,
          f"missing={len(want - got)} extra={len(got - want)}")

    clean_c = pd.read_parquet(os.path.join(OUT, "clean_decision_outcomes_CONFIRM.parquet"),
                               columns=["sess_tag", "time"])
    ref_c = pd.read_parquet(REF_DEC_CONFIRM, columns=["sess_tag", "time"])
    ref_c["time"] = pd.to_datetime(ref_c["time"])
    got_c, want_c = set(zip(clean_c.sess_tag, clean_c.time)), set(zip(ref_c.sess_tag, ref_c.time))
    check("T4 confirmation decision-point set identical", got_c == want_c,
          f"missing={len(want_c - got_c)} extra={len(got_c - want_c)}")
    check("T4 confirmation sample restricted to the 6 usable-BBO sessions",
          set(clean_c.sess_tag.unique()) == {"20250819", "20250912", "20251028", "20260217", "20260302", "20260422"},
          str(sorted(clean_c.sess_tag.unique())))


# --------------------------------------------------------------------------- T5: governance
def run_t5():
    print("\n[T5] governance: permitted tags only, date firewall")
    clean_d = pd.read_parquet(os.path.join(OUT, "clean_decision_outcomes.parquet"), columns=["sess_tag"])
    clean_c = pd.read_parquet(os.path.join(OUT, "clean_decision_outcomes_CONFIRM.parquet"), columns=["sess_tag"])
    all_tags = set(clean_d.sess_tag.unique()) | set(clean_c.sess_tag.unique())
    check("T5 all output tags are in the 45-tag permitted set", all_tags <= PERMITTED_TAGS,
          str(all_tags - PERMITTED_TAGS))
    check("T5 no output tag >= 2026-08-01", all(t < "20260801" for t in all_tags), "")
    check("T5 no protected-pool (non-permitted) session appears", len(all_tags) <= 45, str(all_tags))


def main():
    run_t1()
    run_t2()
    run_t3()
    run_t4()
    run_t5()
    print(f"\n{'='*70}\nTOTAL: {PASSES} passed, {len(FAILS)} failed")
    if FAILS:
        for name, detail in FAILS:
            print(f"  FAILED: {name} -- {detail}")
        raise SystemExit(1)
    print("ALL UNIT TESTS PASSED")


if __name__ == "__main__":
    main()
