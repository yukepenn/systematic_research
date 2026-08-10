"""AUCTION04_CLEAN_CAUSAL_SUBSTRATE -- strictly event-time-correct Auction substrate,
built directly from raw per-trade data (research/scalping_lab/substrate/raw/NQ/*.parquet,
bip==0 Last trade prints), avoiding grid1s's ambiguous 1-second-bucket semantics entirely.

Fixes the two defects AUCTION03_MECHANISM_DECOMPOSITION/REPORT.md sec6 disclosed:

  DEFECT 1 (units, 4x): decision_outcomes(_CONFIRM).parquet's on-disk
  abs/signed_markout_H, mfe_H, mae_H, range_H columns are exactly 4x too large.
  Root cause (confirmed by reading the actual code): build_sechilo.py line 27 stores
  mid_last/mid_high/mid_low ALREADY in TICK units (`mid = price / 0.25`). AUCTION01's
  03_diagnostics.py (and W5's byte-identical 02_diagnostics_confirmation.py) then
  compute e.g. `abs(end_mid - mid_last_t) / TICK` -- dividing an already-tick-scaled
  DIFFERENCE by TICK=0.25 again, i.e. multiplying by 1/0.25 = 4. Fix: since both
  operands are already tick counts, their difference IS already in ticks -- do not
  divide again.

  DEFECT 2 (lookahead): grid1s's `last` column (the numerator of the original
  value_dist_ticks) is built by build_grid1s.py line 21-25 as
  `df["time"].dt.floor("1s")` then `.last()` within each bucket -- a bucket labeled T
  aggregates trades in [T, T+1), so a row labeled T can reflect a trade up to ~1s
  AFTER T. This script never reads grid1s's `last` column (or poc_1s_full.parquet's
  poc_price) at all. causal_last_t and causal_running_POC_t are rebuilt directly,
  in this script, from raw bip==0 trade prints, with a strict timestamp<=t causal
  cutoff enforced by searchsorted (see `causal_lookup`) -- exact, not approximate.

Decision-point set: IDENTICAL (sess_tag,time) pairs to AUCTION01 / W5's own frozen
decision_points_30s(.parquet|_CONFIRM.parquet) -- read directly from those files (not
re-derived), so this substrate covers the same sample, not a different one (per task
instruction). M and position_B are carried over unchanged from those same files (a
per-row sess_tag+time copy -- those columns were never part of either defect, no need
to rebuild).

mid_last_t and the forward markout/mfe/mae/range outcomes ARE rebuilt in this script
directly from research/scalping_lab/substrate/sechilo/NQ/*.parquet (BBO mid, bip in
{1,2}), using the same non-defective continuous-1s-grid-plus-ffill aggregation method
as the original build (that method itself was never flagged as either defect) -- only
the double-division arithmetic bug is fixed. This keeps the change surface limited to
exactly the two disclosed defects, per the task's explicit scope instruction.

Governance: only the 45 permitted session dates below are read (37 discovery + 8
confirmation-pool, of which 6 have usable RTH BBO); nothing >=2026-08-01; none of the
160 still-protected AMENDMENT_3 sessions. Only raw/NQ and sechilo/NQ under
research/scalping_lab/substrate/ are opened, plus the two frozen reference files named
above (read-only) for M/position_B/decision-point timestamps.
"""
import os
import numpy as np
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
RAW = os.path.join(ROOT, "research", "scalping_lab", "substrate", "raw", "NQ")
SECHILO = os.path.join(ROOT, "research", "scalping_lab", "substrate", "sechilo", "NQ")
OUT = os.path.join(ROOT, "runs", "AUCTION04_CLEAN_CAUSAL_SUBSTRATE", "out")
os.makedirs(OUT, exist_ok=True)

REF_DEC_DISCOVERY = os.path.join(ROOT, "runs", "AUCTION01_VALUE_STATE", "out", "decision_points_30s.parquet")
REF_DEC_CONFIRM = os.path.join(ROOT, "runs", "W5_PROTECTED_CONFIRMATION", "results", "out",
                                "decision_points_30s_CONFIRM.parquet")

TICK = 0.25
POINT_USD = 20.0  # NQ direct point value: $20/pt, tick $5.00 -- BASELINE_MODELS.md line 530
HORIZONS = [15, 60, 300]

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
assert len(DISCOVERY_TAGS) == 37 and len(CONFIRMATION_TAGS) == 8 and len(PERMITTED_TAGS) == 45
for d in PERMITTED_TAGS:
    assert d < "20260801", f"date-firewall violation: {d} >= 2026-08-01"


# --------------------------------------------------------------------------- construction
def load_raw_last(tag):
    """bip==0 (Last trade print) rows for one session, sorted by time (stable sort --
    a deliberate, disclosed refinement over the original's default quicksort: ties at
    the exact same millisecond timestamp are broken by original arrival order, which
    matters for a 'strictly event-time-correct' causal lookup at t == a trade time.
    The running-POC *formula* itself is unchanged from AUCTION01/W5 -- only tie order
    among simultaneous prints is now guaranteed deterministic)."""
    raw_f = os.path.join(RAW, f"s{tag}.parquet")
    if not os.path.exists(raw_f):
        return None
    rth_f = os.path.join(RAW, f"s{tag}_rth.parquet")
    parts = [pd.read_parquet(raw_f)]
    if os.path.exists(rth_f):
        parts.append(pd.read_parquet(rth_f))
    df = pd.concat(parts, ignore_index=True)
    df["time"] = pd.to_datetime(df["time"])
    df = df.drop_duplicates(subset=["bip", "time", "price", "volume"])
    last = df[df.bip == 0][["time", "price", "volume"]].copy()
    last = last.sort_values("time", kind="mergesort").reset_index(drop=True)
    return last


def causal_running_poc(last):
    """Same algorithm as AUCTION01_VALUE_STATE/spec.yaml's 'construction' section /
    02_build_poc_substrate.py's causal_running_poc(): tick_id=round(price/TICK);
    cum_vol_at_price = groupby(tick_id)[volume].cumsum() (causal: only rows up to and
    including the current one); running_max_vol = cummax(); a row sets a new POC
    record iff cum_vol_at_price[i] >= running_max_vol[i]; poc_tick ffilled from record
    rows. Re-derived here directly from raw ticks so this script owns its causality
    rather than trusting poc_1s_full.parquet."""
    tick_id = np.round(last["price"].values / TICK).astype(np.int64)
    last = last.copy()
    last["tick_id"] = tick_id
    last["cum_vol_at_price"] = last.groupby("tick_id")["volume"].cumsum()
    running_max = last["cum_vol_at_price"].cummax()
    is_record = last["cum_vol_at_price"].values >= running_max.values
    poc_tick = np.where(is_record, tick_id, np.nan)
    poc_tick = pd.Series(poc_tick).ffill().values
    last["poc_price"] = poc_tick * TICK
    cum_total_vol = last["volume"].cumsum()
    last["poc_share"] = running_max.values / cum_total_vol.values
    return last


def causal_lookup(times_arr, values_arr, query_times):
    """For each t in query_times return values_arr[pos], pos = index of the LAST row
    with times_arr[pos] <= t (strict: no future information). NaN + pos=-1 if no such
    row exists (t before the first observation)."""
    pos = np.searchsorted(times_arr, query_times, side="right") - 1
    out = np.full(len(query_times), np.nan)
    ok = pos >= 0
    out[ok] = values_arr[pos[ok]]
    return out, pos


def build_mid_grid(tag):
    """BBO mid (bip in {1,2}), from sechilo/NQ directly -- same non-defective
    continuous-1s-grid + ffill-through-gaps convention as the original build (not
    part of either defect, only reproduced here so this script does not depend on
    the frozen poc_1s_full(.parquet|_CONFIRM.parquet) intermediate for outcome
    computation). Values are already in TICK units (sechilo's own convention:
    mid = price/0.25) -- do not divide by TICK again downstream."""
    sech_f = os.path.join(SECHILO, f"s{tag}.parquet")
    if not os.path.exists(sech_f):
        return None
    sech = pd.read_parquet(sech_f)
    if len(sech) == 0:
        return None
    sech["time"] = pd.to_datetime(sech["time"])
    idx = pd.date_range(sech["time"].min(), sech["time"].max(), freq="1s")
    s = sech.set_index("time")[["mid_last", "mid_high", "mid_low"]].reindex(idx)
    s["mid_last"] = s["mid_last"].ffill()
    s["mid_high"] = s["mid_high"].fillna(s["mid_last"])
    s["mid_low"] = s["mid_low"].fillna(s["mid_last"])
    return s


def process_session(tag, dec_rows):
    """dec_rows: reference decision_points_30s(.parquet|_CONFIRM.parquet) rows for
    this session (time, position_B, M), sorted by time. Returns a DataFrame in the
    clean_decision_outcomes schema, or None if the session cannot be processed
    (matches the original's own natural session-skip behaviour -- not forced)."""
    last = load_raw_last(tag)
    if last is None or len(last) == 0:
        return None
    poc = causal_running_poc(last)
    times_arr = poc["time"].values
    price_arr = poc["price"].values.astype(np.float64)
    poc_price_arr = poc["poc_price"].values
    poc_share_arr = poc["poc_share"].values

    mid_grid = build_mid_grid(tag)
    if mid_grid is None:
        return None
    idx = mid_grid.index
    mid_last_arr = mid_grid["mid_last"].values
    mid_high_arr = mid_grid["mid_high"].values
    mid_low_arr = mid_grid["mid_low"].values

    t = dec_rows["time"].values
    n = len(t)

    causal_last_t, _ = causal_lookup(times_arr, price_arr, t)
    causal_poc_t, _ = causal_lookup(times_arr, poc_price_arr, t)
    causal_share_t, _ = causal_lookup(times_arr, poc_share_arr, t)
    t_minus60 = t - np.timedelta64(60, "s")
    poc_tminus60, _ = causal_lookup(times_arr, poc_price_arr, t_minus60)

    value_dist_ticks = (causal_last_t - causal_poc_t) / TICK
    poc_migration_60s_ticks = (causal_poc_t - poc_tminus60) / TICK

    p_mid = idx.searchsorted(t)
    p_mid_c = np.clip(p_mid, 0, len(idx) - 1)
    exact = (p_mid < len(idx)) & (idx.values[p_mid_c] == t)
    mid_last_t = np.full(n, np.nan)
    mid_last_t[exact] = mid_last_arr[p_mid_c[exact]]

    position_B = dec_rows["position_B"].values.astype(np.float64)
    M = dec_rows["M"].values.astype(np.float64)
    side = np.where(position_B > 0, 1.0, np.where(position_B < 0, -1.0, np.nan))

    out = {
        "sess_tag": tag, "time": t, "poc_share": causal_share_t,
        "value_dist_ticks": value_dist_ticks, "poc_migration_60s_ticks": poc_migration_60s_ticks,
        "position_B": position_B, "M": M, "mid_last_t": mid_last_t,
    }

    for H in HORIZONS:
        end_t = t + np.timedelta64(H, "s")
        q = idx.searchsorted(end_t)
        q_c = np.clip(q, 0, len(idx) - 1)
        valid = exact & (q < len(idx))
        tol_ok = np.zeros(n, dtype=bool)
        tol_ok[valid] = (idx.values[q_c[valid]] - end_t[valid]) <= np.timedelta64(2, "s")
        good = valid & tol_ok

        abs_mo = np.full(n, np.nan)
        rng = np.full(n, np.nan)
        sm = np.full(n, np.nan)
        mfe = np.full(n, np.nan)
        mae = np.full(n, np.nan)

        for i in np.where(good)[0]:
            pi, qi = p_mid_c[i], q_c[i]
            fwd_hi = mid_high_arr[pi + 1: qi + 1]
            fwd_lo = mid_low_arr[pi + 1: qi + 1]
            if len(fwd_hi) == 0:
                continue
            end_mid = mid_last_arr[qi]
            base = mid_last_t[i]
            abs_mo[i] = abs(end_mid - base)  # already ticks: no /TICK (defect 1 fix)
            rng[i] = fwd_hi.max() - fwd_lo.min()
            s = side[i]
            if not np.isnan(s):
                sm[i] = s * (end_mid - base)
                if s > 0:
                    mfe[i] = fwd_hi.max() - base
                    mae[i] = base - fwd_lo.min()
                else:
                    mfe[i] = base - fwd_lo.min()
                    mae[i] = fwd_hi.max() - base

        out[f"abs_markout_ticks_{H}"] = abs_mo
        out[f"range_ticks_{H}"] = rng
        out[f"signed_markout_ticks_{H}"] = sm
        out[f"mfe_ticks_{H}"] = mfe
        out[f"mae_ticks_{H}"] = mae

    return pd.DataFrame(out)


SCHEMA_COLS = (
    ["sess_tag", "time", "poc_share", "value_dist_ticks", "poc_migration_60s_ticks",
     "position_B", "M", "mid_last_t"]
    + [f"{m}_ticks_{H}" for H in HORIZONS
       for m in ["abs_markout", "range", "signed_markout", "mfe", "mae"]]
)


def build_sample(tags, ref_dec_path, out_name, log):
    ref = pd.read_parquet(ref_dec_path, columns=["sess_tag", "time", "position_B", "M"])
    ref["time"] = pd.to_datetime(ref["time"])
    ref_tags = sorted(ref["sess_tag"].unique())
    log(f"[{out_name}] reference decision-point file: {ref_dec_path}")
    log(f"[{out_name}] reference contributes {len(ref)} decision points across "
        f"{len(ref_tags)} sessions: {ref_tags}")
    assert set(ref_tags) <= set(tags), (
        f"[{out_name}] reference decision-point sessions {set(ref_tags) - set(tags)} "
        f"not in the permitted tag list for this sample -- refusing to proceed")

    frames = []
    for tag in tags:
        dg = ref[ref["sess_tag"] == tag].sort_values("time")
        if len(dg) == 0:
            log(f"[{out_name}] {tag}: 0 reference decision points, skipping "
                f"(matches original's own natural session behaviour)")
            continue
        res = process_session(tag, dg)
        if res is None:
            log(f"[{out_name}] {tag}: process_session returned None (no raw/sechilo "
                f"data), skipping -- {len(dg)} reference points LOST")
            continue
        n_mid_nan = res["mid_last_t"].isna().sum()
        n_last_nan = pd.isna((res["value_dist_ticks"])).sum()
        log(f"[{out_name}] {tag}: {len(res)} decision points built "
            f"(mid_last_t NaN: {n_mid_nan}, value_dist_ticks NaN: {n_last_nan})")
        frames.append(res)

    full = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame(columns=SCHEMA_COLS)
    full = full[SCHEMA_COLS]

    # integrity: identical decision-point set as the reference (task requirement)
    got = set(zip(full["sess_tag"], full["time"]))
    want = set(zip(ref["sess_tag"], ref["time"]))
    assert got == want, (
        f"[{out_name}] decision-point set mismatch vs reference: "
        f"missing={len(want - got)} extra={len(got - want)}")
    log(f"[{out_name}] decision-point set IDENTICAL to reference: {len(got)} points "
        f"({len(full)} rows in output)")

    bad_tags = set(full["sess_tag"].unique()) - PERMITTED_TAGS
    assert not bad_tags, f"[{out_name}] governance violation: non-permitted tags {bad_tags}"
    bad_dates = [t for t in full["sess_tag"].unique() if t >= "20260801"]
    assert not bad_dates, f"[{out_name}] date-firewall violation: {bad_dates}"

    out_path = os.path.join(OUT, out_name)
    full.to_parquet(out_path, compression="zstd", index=False)
    log(f"[{out_name}] WROTE {out_path}: {full.shape}")
    return full


def main():
    log_path = os.path.join(OUT, "build_log.txt")
    lines = []

    def log(msg):
        print(msg, flush=True)
        lines.append(msg)

    log("AUCTION04_CLEAN_CAUSAL_SUBSTRATE build starting")
    log(f"Permitted tags: {len(PERMITTED_TAGS)} (37 discovery + 8 confirmation)")

    disc = build_sample(DISCOVERY_TAGS, REF_DEC_DISCOVERY, "clean_decision_outcomes.parquet", log)

    conf_all = pd.read_parquet(REF_DEC_CONFIRM, columns=["sess_tag"])
    conf_bbo_tags = sorted(conf_all["sess_tag"].unique())
    log(f"Confirmation sessions with usable RTH BBO per reference file "
        f"(defines the sample, not forced): {conf_bbo_tags}")
    expected_no_bbo = {"20251125", "20260512"}
    missing = expected_no_bbo - (set(CONFIRMATION_TAGS) - set(conf_bbo_tags))
    log(f"Confirmation sessions with zero RTH-liquid decision points "
        f"(expected {sorted(expected_no_bbo)}): {sorted(set(CONFIRMATION_TAGS) - set(conf_bbo_tags))}")

    conf = build_sample(CONFIRMATION_TAGS, REF_DEC_CONFIRM, "clean_decision_outcomes_CONFIRM.parquet", log)

    assert set(conf["sess_tag"].unique()) == set(conf_bbo_tags), (
        "confirmation output sessions do not match the naturally-BBO-usable set")
    log(f"Confirmation output sessions: {sorted(conf['sess_tag'].unique())} "
        f"(6 expected, matches AUCTION03's disclosed count)")

    log("BUILD DONE")
    with open(log_path, "w") as f:
        f.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
