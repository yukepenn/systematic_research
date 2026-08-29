"""GENESIS_H1_VOLSTATE_20260828 — shared primitives (PRIMARY implementation).

Everything here implements the frozen spec + out/spec_resolutions.txt (R1-R16).
No parameter is tunable from outside: 252 / 21 / terciles / 17:00 boundary are frozen.
"""
from __future__ import annotations

import calendar
import sys
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO))

from research_sdk.seal_guard import assert_presealed  # noqa: E402

RUN = REPO / "runs" / "GENESIS_H1_VOLSTATE_20260828"
CERT = REPO / "runs" / "GENESIS_FREEDATA_CBOE_20260828" / "certified"
DEEP_NQ = REPO / "research" / "scalping_lab" / "substrate" / "minute" / "NQ" / "nq1m_2005_202605.parquet"
MODERN_NQ = REPO / "runs" / "SM1M_SUBSTRATE" / "out" / "nq_1m_2022_2026.parquet"

EXCLUDE_BEFORE = pd.Timestamp("2007-03-26")      # LEGACY_10X_SUSPECT regime — excluded, not rescaled
DISC_START = pd.Timestamp("2007-04-01")
DISC_END = pd.Timestamp("2021-12-31")
HALF1_END = pd.Timestamp("2013-12-31")
CONF_START = pd.Timestamp("2022-01-01")
CONF_END = pd.Timestamp("2026-07-31")
TERCILE_WINDOW = 252
RV_WINDOW = 21
SESSION_CLOSE = pd.Timedelta(hours=17)           # R1: <=17:00 same-day label, >17:00 next day

_SEAL_ASSERTS = {"n": 0}


def sealed_load_parquet(path: Path, col: str, context: str, columns=None) -> pd.DataFrame:
    df = pq.read_table(path, columns=columns).to_pandas()
    assert_presealed(df, col, context)
    _SEAL_ASSERTS["n"] += 1
    return df


def seal_assert_count() -> int:
    return _SEAL_ASSERTS["n"]


# ---------------------------------------------------------------- expiry (R4)
def third_friday(year: int, month: int) -> date:
    c = calendar.Calendar()
    fridays = [d for d in c.itermonthdates(year, month)
               if d.month == month and d.weekday() == calendar.FRIDAY]
    return fridays[2]


def derived_expiry(cy: int, cm: int, trade_date_universe: set, universe_max: pd.Timestamp) -> pd.Timestamp:
    """R4b amended rule. anchor = 3rd Friday of the FOLLOWING month; if the anchor is
    inside the certified span but not an observed VX trade date (exchange holiday, e.g.
    Good Friday / Juneteenth), anchor -= 1 day (Thursday — CFE moves the SPX-expiry
    anchor). expiry = anchor - 30 calendar days; then holiday-adjust the expiry itself
    (<=2 back-steps, only where the universe can adjudicate)."""
    ny, nm = (cy + 1, 1) if cm == 12 else (cy, cm + 1)
    anchor = pd.Timestamp(third_friday(ny, nm))
    if anchor <= universe_max and anchor not in trade_date_universe:
        anchor = anchor - pd.Timedelta(days=1)
    e = anchor - pd.Timedelta(days=30)
    for _ in range(2):
        if e > universe_max or e in trade_date_universe:
            return e
        e = e - pd.Timedelta(days=1)
    return e


def build_expiry_table(vx: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Per (contract_year, contract_month): expiry = expiry_date_file if present else
    derived. Returns (table, validation dict on modern era)."""
    universe = set(pd.to_datetime(vx["trade_date"].unique()))
    universe_max = pd.Timestamp(vx["trade_date"].max())
    grp = vx.groupby(["contract_year", "contract_month"], as_index=False).agg(
        expiry_file=("expiry_date_file", "max"),
        era=("era", "max"),
        last_trade=("trade_date", "max"),
        n_rows=("trade_date", "size"),
    )
    derived = [derived_expiry(int(r.contract_year), int(r.contract_month), universe, universe_max)
               for r in grp.itertuples()]
    grp["expiry_derived"] = pd.to_datetime(derived)
    grp["expiry"] = grp["expiry_file"].fillna(grp["expiry_derived"])

    # R4b validation scope: contracts whose FILE expiry the trade-date universe can
    # adjudicate (expiry_date_file <= last certified trade date)
    has_file = grp["expiry_file"].notna() & (grp["expiry_file"] <= universe_max)
    diffs = (grp.loc[has_file, "expiry_derived"] - grp.loc[has_file, "expiry_file"]).dt.days
    val = {
        "n_excluded_post_span": int((grp["expiry_file"].notna() & (grp["expiry_file"] > universe_max)).sum()),
        "n_modern_with_file": int(has_file.sum()),
        "n_exact": int((diffs == 0).sum()),
        "pct_exact": float((diffs == 0).mean() * 100) if has_file.any() else float("nan"),
        "n_off_by_1": int((diffs.abs() == 1).sum()),
        "n_off_gt_1": int((diffs.abs() > 1).sum()),
        "max_abs_diff_days": int(diffs.abs().max()) if has_file.any() else -1,
        "diff_value_counts": diffs.value_counts().sort_index().to_dict(),
    }
    val["pass"] = (val["pct_exact"] >= 95.0) and (val["max_abs_diff_days"] <= 1)
    return grp, val


# ------------------------------------------------------------ front basis (R5, R6)
def build_front_basis(vx: pd.DataFrame, vix: pd.DataFrame, expiry_tab: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """BASIS(d) = front settle / VIX close - 1 on VX trade dates >= EXCLUDE_BEFORE."""
    et = expiry_tab.sort_values("expiry").reset_index(drop=True)
    exp_arr = et["expiry"].to_numpy()
    key_arr = list(zip(et["contract_year"].astype(int), et["contract_month"].astype(int)))

    settle_map = {}
    for r in vx.itertuples():
        settle_map[(r.trade_date, int(r.contract_year), int(r.contract_month))] = r.settle

    vix_map = dict(zip(vix["date"], vix["close"]))
    dates = np.sort(vx["trade_date"].unique())
    rows, n_no_front_row, n_bad_settle, n_no_vix = [], 0, 0, 0
    for d in dates:
        d = pd.Timestamp(d)
        i = int(np.searchsorted(exp_arr, np.datetime64(d), side="right"))  # first expiry > d (strict)
        if i >= len(exp_arr):
            n_no_front_row += 1
            continue
        cy, cm = key_arr[i]
        s = settle_map.get((d, cy, cm))
        if s is None:
            n_no_front_row += 1
            continue
        if not (np.isfinite(s) and s > 0):
            n_bad_settle += 1
            continue
        v = vix_map.get(d)
        if v is None or not (np.isfinite(v) and v > 0):
            n_no_vix += 1
            continue
        rows.append((d, f"{cy}-{cm:02d}", float(s), float(v), float(s / v - 1.0)))
    basis = pd.DataFrame(rows, columns=["date", "front_contract", "front_settle", "vix_close", "basis"])
    counts = {"n_vx_dates_post_exclusion": len(dates), "n_basis": len(basis),
              "n_no_front_settle_row": n_no_front_row, "n_nonpositive_settle": n_bad_settle,
              "n_no_vix": n_no_vix}
    return basis, counts


# ------------------------------------------------------------- terciles (R7)
def rolling_tercile_labels(values: np.ndarray, window: int = TERCILE_WINDOW):
    """Causal terciles: breakpoints from the `window` observations STRICTLY before i.
    Returns (labels object-array 'T1'/'T2'/'T3'/None, q33, q66)."""
    s = pd.Series(np.asarray(values, dtype=float))
    prior = s.shift(1)
    q33 = prior.rolling(window, min_periods=window).quantile(1.0 / 3.0, interpolation="linear").to_numpy()
    q66 = prior.rolling(window, min_periods=window).quantile(2.0 / 3.0, interpolation="linear").to_numpy()
    v = s.to_numpy()
    labels = np.full(len(v), None, dtype=object)
    ok = np.isfinite(q33) & np.isfinite(q66) & np.isfinite(v)
    labels[ok & (v <= q33)] = "T1"
    labels[ok & (v > q33) & (v <= q66)] = "T2"
    labels[ok & (v > q66)] = "T3"
    return labels, q33, q66


# ------------------------------------------------- NQ session closes (R1, R3)
def stream_session_closes(path: Path, context: str, max_label: pd.Timestamp | None = None) -> pd.DataFrame:
    """Stream a 1-min parquet row-group by row-group (bounded memory); END-stamped
    bars; label per R1; returns one row per session: label, close, last_ts, n_bars,
    n_halt_bars (bars stamped in (17:00,18:00])."""
    f = pq.ParquetFile(path)
    acc: dict[pd.Timestamp, list] = {}
    prev_last = None
    for g in range(f.metadata.num_row_groups):
        t = f.read_row_group(g, columns=["time", "close"]).to_pandas()
        if t["time"].dtype == object:
            t["time"] = pd.to_datetime(t["time"], format="%Y-%m-%d %H:%M:%S")
        assert_presealed(t, "time", f"{context} rg{g}")
        _SEAL_ASSERTS["n"] += 1
        if not t["time"].is_monotonic_increasing:
            raise RuntimeError(f"{context} rg{g}: time not monotonic non-decreasing")
        if prev_last is not None and t["time"].iloc[0] < prev_last:
            raise RuntimeError(f"{context} rg{g}: row-group ordering broken")
        prev_last = t["time"].iloc[-1]
        day = t["time"].dt.normalize()
        tod = t["time"] - day
        label = day.where(tod <= SESSION_CLOSE, day + pd.Timedelta(days=1))
        halt = (tod > SESSION_CLOSE) & (tod <= pd.Timedelta(hours=18))
        if max_label is not None:
            keep = label <= max_label
            if not keep.any():
                break
            t, day, label, halt = t[keep], day[keep], label[keep], halt[keep]
        t = t.assign(_label=label.to_numpy(), _halt=halt.to_numpy())
        for lab, sub in t.groupby("_label", sort=True):
            lab = pd.Timestamp(lab)
            rec = [float(sub["close"].iloc[-1]), sub["time"].iloc[-1], len(sub), int(sub["_halt"].sum())]
            if lab in acc:
                old = acc[lab]
                rec = [rec[0], rec[1], old[2] + rec[2], old[3] + rec[3]]  # later chunk's last bar wins
            acc[lab] = rec
        del t
    out = pd.DataFrame(
        [(k, v[0], v[1], v[2], v[3]) for k, v in sorted(acc.items())],
        columns=["session", "close", "last_ts", "n_bars", "n_halt_bars"],
    )
    return out


def next_session_returns(sess: pd.DataFrame) -> pd.DataFrame:
    """Within ONE substrate (R2/R3): row per PRIOR session s_i with the return of
    s_{i+1}. Percent (x100) and points; calendar gap in days."""
    s = sess.sort_values("session").reset_index(drop=True)
    out = pd.DataFrame({
        "session": s["session"].iloc[:-1].to_numpy(),
        "next_label": s["session"].iloc[1:].to_numpy(),
        "pct_next": (s["close"].iloc[1:].to_numpy() / s["close"].iloc[:-1].to_numpy() - 1.0) * 100.0,
        "pts_next": s["close"].iloc[1:].to_numpy() - s["close"].iloc[:-1].to_numpy(),
    })
    out["gap_days"] = (out["next_label"] - out["session"]).dt.days
    return out


# ----------------------------------------------------------- clustered t (R9)
def clustered_ols(y: np.ndarray, X: np.ndarray, groups: np.ndarray, contrast: np.ndarray):
    """OLS + CR1 cluster-robust covariance (statsmodels), t of a linear contrast.
    Returns dict(effect, se, t, n, n_clusters)."""
    import statsmodels.api as sm
    res = sm.OLS(y, X).fit(cov_type="cluster", cov_kwds={"groups": groups})
    tt = res.t_test(contrast)
    return {"effect": float(np.atleast_1d(tt.effect)[0]),
            "se": float(np.atleast_2d(tt.sd)[0, 0]),
            "t": float(np.atleast_1d(tt.tvalue.squeeze())),
            "n": int(len(y)),
            "n_clusters": int(pd.Series(groups).nunique())}


def diff_t_clustered(df: pd.DataFrame, label_col: str, y_col: str = "pct_next"):
    """F1/F4 estimator: on T1-union-T3 rows, y ~ const + 1[T3]; monthly clusters of the
    TARGET session (R9). Effect = T3 - T1 difference."""
    sub = df[df[label_col].isin(["T1", "T3"])]
    y = sub[y_col].to_numpy(dtype=float)
    X = np.column_stack([np.ones(len(sub)), (sub[label_col] == "T3").to_numpy(dtype=float)])
    g = sub["next_label"].dt.strftime("%Y-%m").to_numpy()
    return clustered_ols(y, X, g, np.array([0.0, 1.0]))


def gate_table_write(rows: list[dict], path: Path, header_note: str):
    w = [max(len(str(r[k])) for r in rows + [dict(zip("GATE SPEC OBSERVED VERDICT".split(),
                                                      ["GATE", "SPEC", "OBSERVED", "PASS-FAIL"]))])
         for k in ("GATE", "SPEC", "OBSERVED", "VERDICT")]
    lines = [header_note,
             f"{'GATE':<{w[0]}}  {'SPEC':<{w[1]}}  {'OBSERVED':<{w[2]}}  PASS-FAIL",
             "-" * (sum(w) + 15)]
    for r in rows:
        lines.append(f"{r['GATE']:<{w[0]}}  {r['SPEC']:<{w[1]}}  {r['OBSERVED']:<{w[2]}}  {r['VERDICT']}")
    text = "\n".join(lines) + "\n"
    path.write_text(text, encoding="utf-8")
    print(text)
