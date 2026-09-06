"""STEP 1 — extract the 6E (CME Euro FX) DAILY series from the local per-contract db/day .ncd store.

PURE PYTHON. No NT8, no CrossTrade, no Custom.dll recompile. The 48-byte DAY record layout was
resolved by VOLUME00 and lives in research/multi_market/src/ncd_day.py::read_ncd_day (validated
against GetBars on ES 12-11: close AND volume matched exactly). We REUSE that reader, the causal
volume-crossover roll (roll.py, s6) and the basis-invariant self-financing point return
(roll.py::economic_returns, s7). Nothing here re-invents the transport.

Two continuous series are emitted, because a single one would be wrong for one of the two uses:
  * POINT-DIFFERENCE (additive back-adjusted) — correct daily point changes, correct ranges;
    absolute LEVELS in history are shifted by the cumulative roll offset. For level / range work.
  * RATIO-STITCHED (multiplicative) — the self-financing return expressed as a ratio and cumulated;
    correct cross-era PERCENT returns. For % / return work. (DELEV01: additive back-adjust distorts
    cross-era percent thresholds — that closure is exactly why the ratio series exists.)

SEAL: every session >= 2026-08-01 is hard-dropped at load and the retained boundary is asserted.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(RUN))
MM = os.path.join(ROOT, "research", "multi_market", "src")
sys.path.insert(0, MM)

import ncd_day as N            # noqa: E402  read_ncd_day / contracts_for / PV / CYCLES / SECTOR
import roll as R              # noqa: E402  build_roll_ledger / designated_contract / economic_returns
from contract_truth import load_root   # noqa: E402

OUT = os.path.join(RUN, "out")
os.makedirs(OUT, exist_ok=True)
SEAL = pd.Timestamp("2026-08-01")
ROOT_SYM = "6E"
Y0, Y1 = 2009, 2027


def build_root_series(root: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return (daily_series, ledger). daily_series carries raw held-contract OHLCV, the s7
    point + ratio returns, and both continuous adjusted price series."""
    panel = load_root(root, Y0, Y1)
    panel = panel[panel["date"] < SEAL].reset_index(drop=True)
    assert panel["date"].max() < SEAL, "SEAL VIOLATION in panel"

    led = R.build_roll_ledger(panel, root)
    held = R.designated_contract(panel, led)          # step function, ffilled, index = all dates

    # certified point returns (s7) — we will assert our own point column reproduces these exactly
    er = R.economic_returns(panel, held)
    er = er.set_index("date")

    o = panel.pivot_table(index="date", columns="contract_id", values="open").sort_index()
    h = panel.pivot_table(index="date", columns="contract_id", values="high").sort_index()
    lo = panel.pivot_table(index="date", columns="contract_id", values="low").sort_index()
    c = panel.pivot_table(index="date", columns="contract_id", values="close").sort_index()
    vol = panel.pivot_table(index="date", columns="contract_id", values="volume").sort_index()

    dates = held.index
    rows = []
    for i in range(len(dates)):
        d = dates[i]
        tgt = held.get(d)
        if not isinstance(tgt, str):
            continue
        try:
            bar_o, bar_h, bar_l, bar_c = o.at[d, tgt], h.at[d, tgt], lo.at[d, tgt], c.at[d, tgt]
            bar_v = vol.at[d, tgt]
        except KeyError:
            continue
        if any(pd.isna(x) for x in (bar_o, bar_h, bar_l, bar_c)):
            continue
        rec = dict(date=d, contract=tgt, open=float(bar_o), high=float(bar_h),
                   low=float(bar_l), close=float(bar_c),
                   volume=(int(bar_v) if not pd.isna(bar_v) else 0))
        # self-financing returns (POINT and RATIO) — never differences two contracts
        if i == 0:
            rec.update(ret_points=np.nan, ret_pct=np.nan, overnight_points=np.nan,
                       intraday_points=np.nan, rolled=0)
        else:
            dp = dates[i - 1]
            old = held.get(dp)
            try:
                old_c_prev, old_o = c.at[dp, old], o.at[d, old]
                tgt_o, tgt_c = o.at[d, tgt], c.at[d, tgt]
            except KeyError:
                old_c_prev = np.nan
            if not isinstance(old, str) or pd.isna(old_c_prev) or pd.isna(old_o) \
                    or pd.isna(tgt_o) or pd.isna(tgt_c) or old_c_prev <= 0 or tgt_o <= 0:
                rec.update(ret_points=np.nan, ret_pct=np.nan, overnight_points=np.nan,
                           intraday_points=np.nan, rolled=int(old != tgt))
            else:
                overnight = old_o - old_c_prev               # OLD contract carries the gap
                intraday = tgt_c - tgt_o                      # TARGET carries the intraday leg
                ret_points = overnight + intraday
                ret_pct = (old_o / old_c_prev) * (tgt_c / tgt_o) - 1.0
                rec.update(ret_points=float(ret_points), ret_pct=float(ret_pct),
                           overnight_points=float(overnight), intraday_points=float(intraday),
                           rolled=int(old != tgt))
        rows.append(rec)

    s = pd.DataFrame(rows).sort_values("date").reset_index(drop=True)

    # ---- cross-check: our point return must equal the certified economic_returns.ret_points
    chk = s.set_index("date")["ret_points"].dropna()
    ref = er["ret_points"].reindex(chk.index)
    max_abs = float(np.max(np.abs(chk.values - ref.values)))
    assert max_abs < 1e-6, f"point-return reproduction mismatch vs certified s7: {max_abs}"
    s.attrs["point_repro_max_abs_err"] = max_abs
    s.attrs["point_repro_n"] = int(len(chk))

    # ---- POINT-DIFFERENCE continuous (additive back-adjusted). Daily changes == ret_points.
    rp = s["ret_points"].fillna(0.0).values
    cum = np.cumsum(rp)                                   # arbitrary origin
    add_close = s["close"].iloc[0] + cum
    # constant shift so the MOST RECENT value equals the true front close (levels anchored to truth)
    shift = float(s["close"].iloc[-1] - add_close[-1])
    s["close_add"] = add_close + shift
    off = (s["close_add"] - s["close"]).values           # piecewise-constant per contract segment
    s["open_add"] = s["open"].values + off
    s["high_add"] = s["high"].values + off
    s["low_add"] = s["low"].values + off

    # ---- RATIO-STITCHED continuous (multiplicative). Cross-era percent-safe (DELEV01).
    rr = s["ret_pct"].fillna(0.0).values
    ratio_idx = np.cumprod(1.0 + rr)
    scale = float(s["close"].iloc[-1] / ratio_idx[-1])
    s["close_ratio"] = ratio_idx * scale

    # ---- USD point value context
    s["ret_usd"] = s["ret_points"] * N.PV[root]

    # ---- roll_dist: sessions to nearest roll effective_date (feature-hygiene embargo helper)
    roll_dates = set(pd.to_datetime(led["effective_date"]).tolist()) - {s["date"].iloc[0]}
    idx = list(s["date"])
    pos = {d: i for i, d in enumerate(idx)}
    rpos = sorted(pos[d] for d in roll_dates if d in pos)
    dist = np.full(len(idx), 10 ** 6, dtype=np.int64)
    for r_ in rpos:
        lo_, hi_ = max(0, r_ - 15), min(len(idx), r_ + 16)
        for j in range(lo_, hi_):
            dist[j] = min(dist[j], abs(j - r_))
    s["roll_dist"] = dist
    return s, led


def sha256_file(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def main():
    s, led = build_root_series(ROOT_SYM)

    # roll-method characterisation (FX never rolls on volume — name it, do not imply it)
    n_vol = int((led["reason"] == "VOLUME_CROSSOVER").sum())
    n_pre = int((led["reason"] == "PRE_EXPIRY_OVERRIDE").sum())
    n_init = int((led["reason"] == "INITIALISE").sum())

    parq = os.path.join(OUT, "6e_daily.parquet")
    s.to_parquet(parq, index=False)
    sha = sha256_file(parq)

    # NQ ratio-return series for the cross-asset correlation (built identically, seal-clean)
    nq, _ = build_root_series("NQ")
    nq[["date", "ret_pct", "ret_points", "close_add", "close_ratio"]].to_parquet(
        os.path.join(OUT, "nq_daily_for_corr.parquet"), index=False)

    meta = dict(
        root=ROOT_SYM, sector=N.SECTOR[ROOT_SYM], point_value=N.PV[ROOT_SYM],
        rows=int(len(s)), first_session=str(s["date"].min().date()),
        last_session=str(s["date"].max().date()),
        seal_boundary_retained=str(s["date"].max().date()),
        seal_assert=f"max session {s['date'].max().date()} < {SEAL.date()} : "
                    f"{bool(s['date'].max() < SEAL)}",
        contracts_used=int(s["contract"].nunique()),
        roll_method="causal volume-crossover (t-1 volume) + 5-day pre-expiry override, one-way "
                    "(roll.py s6). FX SPECIFIC REALITY: 6E produces "
                    f"{n_vol} VOLUME_CROSSOVER rolls and {n_pre} PRE_EXPIRY_OVERRIDE rolls, so the "
                    "6E roll is EFFECTIVELY A FIXED 5-DAY-PRE-EXPIRY RULE (contract lives barely "
                    "overlap; median ~3 sessions). This is s6-sanctioned when volume cannot be "
                    "trusted, and is named rather than implied.",
        roll_counts=dict(volume_crossover=n_vol, pre_expiry_override=n_pre, initialise=n_init),
        point_return_reproduction=dict(
            n=s.attrs.get("point_repro_n"), max_abs_err_vs_certified_s7=s.attrs.get(
                "point_repro_max_abs_err"),
            note="our ret_points reproduces research/multi_market/out/economic_returns.parquet "
                 "(6E) exactly — the certified basis-invariant s7 construction was reused, not "
                 "re-derived."),
        sha256_6e_daily_parquet=sha,
        reader="research/multi_market/src/ncd_day.py::read_ncd_day (48-byte DAY record; "
               "hdr28 int32 ver|f64 tick|f64 firstPrice|i64 firstTicks; rec48 i64 ticks|f64 OHLC|"
               "i64 vol). PURE PYTHON, no NT8.",
    )
    json.dump(meta, open(os.path.join(OUT, "extract_meta.json"), "w"), indent=2, default=str)

    print("=== 6E DAILY EXTRACT ===")
    for k, v in meta.items():
        print(f"  {k}: {v}")
    print("\n--- head ---")
    print(s.head(3).to_string())
    print("\n--- tail ---")
    print(s.tail(3).to_string())
    print(f"\n  ret_pct  mean {s['ret_pct'].mean():.6e}  sd {s['ret_pct'].std():.6e}")
    print(f"  close raw first/last: {s['close'].iloc[0]:.5f} / {s['close'].iloc[-1]:.5f}")
    print(f"  close_add first/last: {s['close_add'].iloc[0]:.5f} / {s['close_add'].iloc[-1]:.5f}")
    print(f"  close_ratio first/last: {s['close_ratio'].iloc[0]:.5f} / {s['close_ratio'].iloc[-1]:.5f}")


if __name__ == "__main__":
    main()
