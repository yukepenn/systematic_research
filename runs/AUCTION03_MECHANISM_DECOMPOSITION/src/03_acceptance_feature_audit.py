"""AUCTION03 mechanism decomposition, part 3 -- STEP D mandatory lookahead
audit.

For 15 spot-checked (sess_tag, time) points across 5 sessions (4 discovery +
1 confirmation; one early-warmup point per session where the trailing 60s
window is NOT yet full, to explicitly exercise the min_periods edge), this
script recomputes accept_primary (candidate b) and accept_sensitivity
(candidate a) via a completely independent code path -- direct pandas
boolean masking on `last[last.time < cutoff]`, never calling
trailing_band_cumvol / rolling_trailing_sum / merge_asof from acceptance_lib
-- and asserts the result matches the vectorized full-session computation
(acceptance_lib.build_base_session + candidate_a/candidate_b) exactly.

Boundary convention audited (must match what the vectorized code actually
does): grid row `idx[t]` represents state as of the END of the 1-second
bucket [idx[t], idx[t]+1s) -- i.e. "known as of t" means
`last.time < idx[t] + 1s`. The trailing WINDOW_S-second window is the 60
one-second buckets [idx[t]-59s, idx[t]] inclusive, i.e.
`idx[t]-59s <= last.time < idx[t]+1s`. Both boundaries are re-derived here
from the merge_asof semantics actually used in trailing_band_cumvol
(backward-asof at query sec=idx[t] and sec=idx[t]-60s against buckets
labelled by floor('1s')), not merely asserted.

Design note on what "independent" means here: this audit slices
`base['last']` -- the tick-level causal_running_poc frame that
build_base_session computes once for the whole session -- down to
`time < cutoff` rather than re-deriving it from a second, freshly re-sorted
`causal_running_poc(known)` call. This is a deliberate fix for a genuine
(if narrow) reproducibility artifact found during the first audit run:
causal_running_poc's internal `.sort_values("time")` uses pandas' default
UNSTABLE quicksort, and re-invoking it on a differently-sized subset of the
same tied-timestamp data can pick a different trade among exact-millisecond
ties than the single full-session sort the production pipeline performs --
2 of the first 15 spot checks failed for exactly this reason (row=10 on
20260406 and 20260511, both driven by a multi-trade tie at the session's
9th/10th second). This is NOT a lookahead bug: cumsum/cummax are causal by
construction regardless of array length, so `base['last']` at any row i
never depends on data after row i either way -- it is simply a tie-break
nondeterminism artifact of calling an unstable sort twice on differently-
shaped inputs. Slicing the once-computed, already-causal frame removes that
confound so the audit tests what actually needs testing: the NEW trailing-
window/band/rolling logic (trailing_band_cumvol, rolling_trailing_sum,
reference-tick gather), which is independent of and does not call any of
those production functions. The current-price reference is read from
grid1s's own `last` column, exactly like build_base_session does (and for
the identical, already-disclosed reason: that tie-break is the campaign's
established canonical choice for "last price of second t").
"""
import json
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
from acceptance_lib import (
    ROOT, TICK, WINDOW_S, GRID1S,
    build_base_session,
    candidate_a_excursion_side_share, candidate_b_near_price_acceptance,
)

OUT = os.path.join(ROOT, "runs", "AUCTION03_MECHANISM_DECOMPOSITION", "out")
os.makedirs(OUT, exist_ok=True)

AUDIT_SESSIONS = ["20250901", "20251209", "20260406", "20260511", "20260302"]  # last is confirmation
OFFSETS = [10, None, -50]  # None -> midpoint; 10 = early warmup (<60s of history); -50 = late in session


def manual_recompute(last_causal: pd.DataFrame, grid_last: pd.DataFrame, t: pd.Timestamp):
    """Independent recomputation of accept_primary/accept_sensitivity at
    grid second t, using ONLY rows with time < t + 1s (i.e. only trade
    prints with timestamp <= t, floor('1s')-bucketed exactly like the
    production grid). `last_causal` is base['last'] (the tick-level
    causal_running_poc frame, causal by construction of cumsum/cummax --
    see module docstring for why this is a legitimate, non-circular
    ground truth here). No rolling/merge_asof helper from acceptance_lib
    is called."""
    cutoff_now = t + pd.Timedelta(seconds=1)
    cutoff_lag = t - pd.Timedelta(seconds=WINDOW_S - 1)  # window is [t-59s, t] inclusive

    known = last_causal[last_causal["time"] < cutoff_now]
    if len(known) == 0:
        return dict(accept_primary=np.nan, accept_sensitivity=np.nan, n_known=0, n_window=0)

    poc_price_ref = known["poc_price"].values[-1]
    poc_tick_ref = int(round(poc_price_ref / TICK))

    # current price: grid1s's own canonical `last` as of second t (identical
    # source/convention to build_base_session, sidestepping the tie-break
    # ambiguity in "which trade is *the* last one of a tied millisecond")
    grid_row = grid_last[grid_last["time"] <= t]
    cur_price_ref = grid_row["last"].values[-1]
    cur_tick_ref = int(round(cur_price_ref / TICK))
    D_t = (cur_price_ref - poc_price_ref) / TICK
    side_now = np.sign(D_t)

    window = known[(known["time"] >= cutoff_lag) & (known["time"] < cutoff_now)]
    n_window = len(window)

    # ---- candidate b (primary): near-current vs near-poc trailing volume share
    vol_near_cur = float(window.loc[(window["tick_id"] - cur_tick_ref).abs() <= 2, "volume"].sum())
    vol_near_poc = float(window.loc[(window["tick_id"] - poc_tick_ref).abs() <= 2, "volume"].sum())
    denom_b = vol_near_cur + vol_near_poc
    accept_primary = vol_near_cur / denom_b if denom_b > 0 else np.nan

    # ---- candidate a (sensitivity): trailing volume share on the current excursion side
    # each trade's own side = sign(price_i - poc_price_i) using the RUNNING poc at that
    # trade's own row (full-prefix causal poc, i.e. poc_known's own poc_price column)
    side_tick = np.sign(window["price"].values - window["poc_price"].values)
    tot_vol = float(window["volume"].sum())
    if side_now > 0:
        num = float(window.loc[side_tick > 0, "volume"].sum())
        accept_sensitivity = num / tot_vol if tot_vol > 0 else np.nan
    elif side_now < 0:
        num = float(window.loc[side_tick < 0, "volume"].sum())
        accept_sensitivity = num / tot_vol if tot_vol > 0 else np.nan
    else:
        accept_sensitivity = np.nan

    return dict(accept_primary=accept_primary, accept_sensitivity=accept_sensitivity,
                n_known=len(known), n_window=n_window)


def main():
    print(f"[audit] sessions: {AUDIT_SESSIONS}", flush=True)
    checks = []
    all_pass = True

    for tag in AUDIT_SESSIONS:
        base = build_base_session(tag)
        last_causal = base["last"]  # tick-level causal_running_poc frame (causal by construction)
        grid_f = os.path.join(GRID1S, f"s{tag}.parquet")
        grid_last = pd.read_parquet(grid_f, columns=["time", "last"])
        grid_last["time"] = pd.to_datetime(grid_last["time"])
        a_vec = candidate_a_excursion_side_share(base)
        b_vec, _, _ = candidate_b_near_price_acceptance(base)
        idx = base["idx"]
        n = base["n"]

        row_offsets = [o if o is not None else n // 2 for o in OFFSETS]
        for o in row_offsets:
            row = o if o >= 0 else n + o
            t = idx[row]
            manual = manual_recompute(last_causal, grid_last, t)
            vec_primary = float(b_vec[row])
            vec_sensitivity = float(a_vec[row])

            def close(x, y):
                if (x != x) and (y != y):  # both NaN
                    return True
                if (x != x) or (y != y):
                    return False
                return abs(x - y) < 1e-9

            ok_primary = close(manual["accept_primary"], vec_primary)
            ok_sensitivity = close(manual["accept_sensitivity"], vec_sensitivity)
            ok = ok_primary and ok_sensitivity
            all_pass = all_pass and ok

            rec = {
                "sess_tag": tag, "row": int(row), "time": str(t),
                "n_window_trades": manual["n_window"], "n_known_trades": manual["n_known"],
                "manual_accept_primary": manual["accept_primary"], "vector_accept_primary": vec_primary,
                "manual_accept_sensitivity": manual["accept_sensitivity"], "vector_accept_sensitivity": vec_sensitivity,
                "pass_primary": ok_primary, "pass_sensitivity": ok_sensitivity, "pass": ok,
            }
            checks.append(rec)
            print(f"[audit] {tag} row={row} t={t} window_trades={manual['n_window']} "
                  f"primary manual={manual['accept_primary']:.6f} vec={vec_primary:.6f} pass={ok_primary} | "
                  f"sensitivity manual={manual['accept_sensitivity']:.6f} vec={vec_sensitivity:.6f} pass={ok_sensitivity}",
                  flush=True)
        del base

    n_checks = len(checks)
    n_pass = sum(c["pass"] for c in checks)
    result = {
        "audit_sessions": AUDIT_SESSIONS, "offsets_per_session": OFFSETS,
        "n_checks": n_checks, "n_pass": n_pass, "all_pass": bool(all_pass),
        "checks": checks,
    }
    out_path = os.path.join(OUT, "step_d_lookahead_audit.json")
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"[audit] {n_pass}/{n_checks} checks passed. ALL_PASS={all_pass}", flush=True)
    print(f"[audit] wrote {out_path}", flush=True)
    print("AUDIT DONE", flush=True)


if __name__ == "__main__":
    main()
