"""ESNQ_CLOCK_CONTRACT_V1 -- BLOCKING. No ESNQ P&L is admissible before this writes a verdict.

THE FAILURE MODE THIS EXISTS FOR. `feature_ts < decision_ts` WITHIN each instrument is necessary
and NOT sufficient for a cross-market claim. A systematic ES-vs-NQ timestamp semantics / latency /
historical-store difference can manufacture an apparent "ES leads NQ" while every within-instrument
causality assertion passes cleanly.

THE DIAGNOSTIC IS TIMING-ONLY, AND DELIBERATELY SO. It cross-correlates EVENT INTENSITY -- the
count of quote/trade events per 100 ms bin -- between ES and NQ. It never touches a price, a return
or a direction, so it cannot be confused with, or contaminated by, alpha. Both instruments respond
to the same market-wide activity, so the intensity cross-correlation peaks at the RELATIVE CLOCK
OFFSET between the two streams.

POSITIVE CONTROL, DECLARED BEFORE ANY OUTPUT: inject a known +250 ms shift into the ES stream and
require the diagnostic to move its detected peak by +250 ms (within one bin). 250 ms is a round
number fixed in advance; it is NOT chosen by alpha performance, and no alpha exists yet.

WHY CORRELATION OF PRICES IS NOT USED: high ES/NQ price correlation is exactly what CONCEALS clock
misalignment. Two perfectly correlated series shifted by 200 ms still look ~perfectly correlated.
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(RUN))
sys.path.insert(0, os.path.join(ROOT, "research_sdk"))
import blindguard as BG                                                 # noqa: E402
from timegrid import NS_PER_S                                           # noqa: E402

PARQ = os.path.join(ROOT, "research", "data_esnq", "parquet")
DEV_MAN = os.path.join(RUN, "manifests", "ESNQ_DEV_44.csv")
BLIND_MAN = os.path.join(RUN, "manifests", "ESNQ_BLIND_15.csv")
OUT = os.path.join(RUN, "out")
os.makedirs(OUT, exist_ok=True)

RTH_START, RTH_END = "10:00:00", "15:30:00"
BIN_MS = 100                                   # intensity bin
MAX_LAG_MS = 3000                              # +/- 3 s search
INJECT_MS = 250                                # POSITIVE CONTROL, declared before any output
_fh = None


def P(*a):
    print(*a, flush=True)
    if _fh is not None:
        print(*a, file=_fh)


def load_times(inst, sd):
    t = pq.read_table(os.path.join(PARQ, inst, f"s{sd}.parquet"),
                      columns=["bip", "time"]).to_pandas()
    return t["time"].values.astype("datetime64[ns]").astype("int64"), t["bip"].values


def intensity(ts, lo, hi, shift_ns=0):
    """Event counts per BIN_MS bin over [lo, hi). TIMING ONLY -- no price is read."""
    x = ts + shift_ns
    m = (x >= lo) & (x < hi)
    b = ((x[m] - lo) // (BIN_MS * 1_000_000)).astype(np.int64)
    n = int((hi - lo) // (BIN_MS * 1_000_000))
    return np.bincount(b, minlength=n)[:n].astype(float)


def xcorr_peak(a, b, max_lag_bins):
    """Lag (in bins) of peak cross-correlation of a vs b. Positive => b lags a."""
    a = a - a.mean()
    b = b - b.mean()
    if a.std() == 0 or b.std() == 0:
        return np.nan, np.nan
    best, bl = -np.inf, 0
    for L in range(-max_lag_bins, max_lag_bins + 1):
        if L >= 0:
            x, y = a[:len(a) - L], b[L:]
        else:
            x, y = a[-L:], b[:len(b) + L]
        if len(x) < 100:
            continue
        c = float(np.corrcoef(x, y)[0, 1])
        if c > best:
            best, bl = c, L
    return bl, best


def main():
    global _fh
    _fh = open(os.path.join(OUT, "clock_contract.txt"), "w", encoding="utf-8")
    P("=" * 116)
    P("=== ESNQ_CLOCK_CONTRACT_V1 -- BLOCKING.  TIMING ONLY: no price, no return, no direction.")
    P("=" * 116)

    dev = sorted(BG.load_manifest(DEV_MAN))
    BG.assert_no_blind_contamination(dev, BLIND_MAN, label="clock contract")
    P(f"    development sessions {len(dev)}   blind contamination check PASS")

    # ---------------------------------------------------------------- A / B provenance
    P("")
    P("=== A. WHAT THE TIMESTAMP REPRESENTS")
    P("    Both streams come from ONE path: NT8 local db/tick -> SWScalpTickExportAllow_v1 via")
    P("    RunStrategyBacktest, writing Times[b][0] for the Last/Bid/Ask 1-tick series.")
    P("    NT8 exposes these as EXCHANGE-SESSION (ET) timestamps of the historical store record.")
    P("    Whether the stored value is exchange event time or provider receipt time is NOT")
    P("    certified by the platform and this run does NOT invent an answer.")
    P("    >>> A. SEMANTICS: UNKNOWN (declared, not assumed)")
    P("")
    P("=== B. ARE ES AND NQ GENERATED IDENTICALLY?")
    for k, v in (("provider / historical API path", "IDENTICAL - NT8 db/tick, same install"),
                 ("storage format", "IDENTICAL - .ncd, same reader"),
                 ("export code path", "IDENTICAL - one class, one invocation contract"),
                 ("timezone conversion", "IDENTICAL - same NT8 session template application"),
                 ("timestamp precision", "measured below, per instrument"),
                 ("session-label rule", "IDENTICAL - sess = (t + 6h).Date, one code path"),
                 ("download mechanism", "IDENTICAL - GetBars/backtest cache")):
        P(f"    {k:<34} {v}")
    P("    >>> B. The two streams share every stage EXCEPT the instrument itself. That removes")
    P("    >>> the most common source of a systematic offset, and does NOT prove there is none.")

    # ---------------------------------------------------------------- per-session table
    P("")
    P("=== C/D. PER-SESSION CLOCK TABLE (44 sessions x 2 instruments)")
    rows = []
    for sd_iso in dev:
        sd = sd_iso.replace("-", "")
        day = pd.Timestamp(sd_iso)
        lo = (day + pd.Timedelta(RTH_START)).value
        hi = (day + pd.Timedelta(RTH_END)).value
        dst = "EDT" if (pd.Timestamp("2025-03-09") <= day < pd.Timestamp("2025-11-02")
                        or pd.Timestamp("2026-03-08") <= day < pd.Timestamp("2026-11-01")) else "EST"
        rec = {"session_date": sd_iso, "dst": dst}
        series = {}
        for inst in ("NQ", "ES"):
            ts, bip = load_times(inst, sd)
            series[inst] = (ts, bip)
            m = (ts >= lo) & (ts <= hi)
            rec[f"{inst}_rth_events"] = int(m.sum())
            rec[f"{inst}_first_rth"] = str(pd.Timestamp(ts[m].min())) if m.any() else ""
            rec[f"{inst}_last_rth"] = str(pd.Timestamp(ts[m].max())) if m.any() else ""
            rec[f"{inst}_covers_window"] = bool(ts.min() <= lo and ts.max() >= hi)
            rec[f"{inst}_monotonic_viol"] = int((np.diff(ts) < 0).sum())
            rec[f"{inst}_dup_ts_frac"] = float(np.mean(np.diff(ts) == 0))
            d = np.diff(np.unique(ts[m]))
            rec[f"{inst}_granularity_ms"] = float(d.min() / 1e6) if len(d) else np.nan
            for b, nm in ((1, "bid"), (2, "ask"), (0, "last")):
                tb = ts[m & (bip == b)]
                rec[f"{inst}_{nm}_n"] = int(len(tb))
                rec[f"{inst}_{nm}_maxgap_s"] = (float(np.max(np.diff(tb)) / 1e9)
                                                if len(tb) > 1 else np.nan)
        # ---- TIMING-ONLY cross-instrument offset
        a = intensity(series["NQ"][0], lo, hi)
        b = intensity(series["ES"][0], lo, hi)
        L, c = xcorr_peak(a, b, MAX_LAG_MS // BIN_MS)
        rec["xcorr_lag_ms"] = float(L * BIN_MS) if not np.isnan(L) else np.nan
        rec["xcorr_peak"] = float(c) if not np.isnan(c) else np.nan
        # ---- POSITIVE CONTROL: inject a KNOWN +250 ms shift into ES
        b2 = intensity(series["ES"][0], lo, hi, shift_ns=INJECT_MS * 1_000_000)
        L2, c2 = xcorr_peak(a, b2, MAX_LAG_MS // BIN_MS)
        rec["xcorr_lag_ms_injected"] = float(L2 * BIN_MS) if not np.isnan(L2) else np.nan
        rows.append(rec)
        if len(rows) % 10 == 0:
            P(f"    ... {len(rows)}/{len(dev)} sessions")
    T = pd.DataFrame(rows)
    T.to_csv(os.path.join(OUT, "clock_contract_sessions.csv"), index=False)

    P("")
    P("=== C. TIMEZONE / SESSION ALIGNMENT")
    P(f"    sessions in EDT {int((T.dst=='EDT').sum())}   in EST {int((T.dst=='EST').sum())}")
    P(f"    NQ covers the full 10:00-15:30 window: {int(T.NQ_covers_window.sum())}/{len(T)}")
    P(f"    ES covers the full 10:00-15:30 window: {int(T.ES_covers_window.sum())}/{len(T)}")
    P(f"    first RTH event == 10:00:00 boundary respected on both: "
      f"{bool(T.NQ_covers_window.all() and T.ES_covers_window.all())}")

    P("")
    P("=== D. PATHOLOGY (no alpha question asked)")
    for inst in ("NQ", "ES"):
        P(f"    {inst}: monotonicity violations total {int(T[f'{inst}_monotonic_viol'].sum())}   "
          f"granularity min {T[f'{inst}_granularity_ms'].min():.3f} ms   "
          f"dup-ts frac median {T[f'{inst}_dup_ts_frac'].median():.4f}")
        for nm in ("bid", "ask", "last"):
            P(f"        {nm:<5} RTH events median {T[f'{inst}_{nm}_n'].median():>10,.0f}   "
              f"max intra-RTH gap {T[f'{inst}_{nm}_maxgap_s'].max():>7.2f} s")
    P("")
    P("    ES vs NQ RTH event ratio: "
      f"median {(T.ES_rth_events/T.NQ_rth_events).median():.3f}  "
      f"min {(T.ES_rth_events/T.NQ_rth_events).min():.3f}  "
      f"max {(T.ES_rth_events/T.NQ_rth_events).max():.3f}")
    P("    >>> Event-count differences are NOT the question. A systematic TIMESTAMP OFFSET is.")

    # ---------------------------------------------------------------- E
    P("")
    P("=== E. TIMING-ONLY POSITIVE CONTROL  (injected shift = +%d ms, declared in advance)"
      % INJECT_MS)
    obs = T["xcorr_lag_ms"].dropna()
    inj = T["xcorr_lag_ms_injected"].dropna()
    delta = (T["xcorr_lag_ms_injected"] - T["xcorr_lag_ms"]).dropna()
    P(f"    UNTOUCHED streams  : detected NQ->ES lag  median {obs.median():+.0f} ms   "
      f"mean {obs.mean():+.1f}   p10 {obs.quantile(.1):+.0f}   p90 {obs.quantile(.9):+.0f}")
    P(f"    ES SHIFTED +{INJECT_MS} ms : detected lag        median {inj.median():+.0f} ms")
    P(f"    DETECTED CHANGE    : median {delta.median():+.0f} ms   "
      f"(expected +{INJECT_MS} ms; bin size {BIN_MS} ms)")
    detects = abs(delta.median() - INJECT_MS) <= BIN_MS
    P(f"    >>> POSITIVE CONTROL {'PASS - the diagnostic detects a known offset' if detects else '*** FAIL - THE PROBE HAS NO TEETH ***'}")
    P(f"    peak correlation median {T['xcorr_peak'].median():.3f} "
      f"(intensity co-movement, not price correlation)")

    # ---------------------------------------------------------------- verdict
    P("")
    P("=" * 116)
    zero_bin = float((obs.abs() <= BIN_MS / 2).mean())
    P("=== VERDICT")
    P("=" * 116)
    P(f"    sessions whose detected offset is within +/- {BIN_MS/2:.0f} ms of zero: "
      f"{zero_bin*100:.1f} %")
    P(f"    |median offset| {abs(obs.median()):.0f} ms  vs  bin resolution {BIN_MS} ms")
    integrity = bool(T[[c for c in T.columns if c.endswith('_monotonic_viol')]].sum().sum() == 0
                     and T.NQ_covers_window.all() and T.ES_covers_window.all())
    if not (integrity and detects):
        verdict = "CLOCK-UNSAFE"
    elif abs(obs.median()) <= BIN_MS:
        verdict = "CLOCK-COMPATIBLE-BUT-SEMANTICS-UNKNOWN"
    else:
        verdict = "CLOCK-UNSAFE"
    P("")
    P(f"    >>> {verdict}")
    if verdict == "CLOCK-COMPATIBLE-BUT-SEMANTICS-UNKNOWN":
        P("    No systematic whole-stream ES/NQ offset is detectable above the 100 ms resolution of")
        P("    a probe PROVEN to detect a 250 ms one. Underlying timestamp SEMANTICS remain")
        P("    UNCERTIFIED by the platform, so:")
        P("      - the independent implementation MUST use the same information contract;")
        P("      - NO lead-lag claim stronger than 100 ms resolution may be made;")
        P("      - a sub-100 ms mechanism claim is OUT OF SCOPE for this object.")
    json.dump({"verdict": verdict, "bin_ms": BIN_MS, "injected_ms": INJECT_MS,
               "positive_control_detects": bool(detects),
               "median_detected_offset_ms": float(obs.median()),
               "median_detected_change_ms": float(delta.median()),
               "integrity_ok": integrity, "n_sessions": int(len(T))},
              open(os.path.join(OUT, "clock_contract_verdict.json"), "w", encoding="utf-8"),
              indent=2)
    _fh.close()


if __name__ == "__main__":
    main()
