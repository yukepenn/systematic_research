"""G3_VOLSHORT01 discovery panel builder.

Builds ONE row per NQ RTH session, 2006-01-05 .. 2021-12-31 inclusive, joining the certified
free Cboe daily volatility complex on the PRIOR trading day's close so every vol column is
causally available at 09:30:00 ET on the session it labels.

====================================================================================
THE WALL
====================================================================================
GENESIS_H1 reserves 2022-01-01 -> 2026-07-31 as a PRISTINE ONE-SHOT CONFIRMATION WINDOW.
Nothing in this file may read, load, aggregate or count a session on or after 2022-01-01.
Every frame is filtered to < 2022-01-01 immediately on load and the filter is asserted and
printed. Everything produced here is DISCOVERY_CONTAMINATED and is a RULE PROPOSAL only.

Deliberate deviation from the task sketch, recorded here rather than buried:
  the sketch said load_deep(..., extend=True).  `extend=True` reads
  runs/SM1M_SUBSTRATE/out/nq_1m_2022_2026.parquet and concatenates the rows stamped
  AFTER 2026-05-29 16:59 -- i.e. it loads ONLY post-wall bars, and every one of them is
  then discarded by the <= 2021-12-31 filter.  It cannot change a single value in this
  panel, and it is the only code path here that would put post-wall bars in memory.  So we
  pass extend=False.  Output for the requested window is bit-identical; wall exposure is
  strictly lower.  (The base substrate itself spans 2006-01-05 .. 2026-05-29; the certified
  loader reads the file whole and then filters.  We re-assert the filter ourselves below and
  additionally hard-drop anything >= the wall before a single statistic is computed.)

Run:  python runs/G3_VOLSHORT01_20260831/src/discovery/panel.py
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
OUT = os.path.join(ROOT, "runs", "G3_VOLSHORT01_20260831", "out", "discovery")
CBOE = os.path.join(ROOT, "runs", "GENESIS_FREEDATA_CBOE_20260828", "certified")

WALL = pd.Timestamp("2022-01-01")
WALL64 = np.datetime64("2022-01-01")

START = "2006-01-05"
END = "2021-12-31 17:00"          # last bar of the 2021-12-31 RTH session is stamped 17:00 ET

RTH_OPEN_MIN = 9 * 60 + 31        # bar stamped 09:31 -> covers 09:30:00-09:30:59, opens on the
RTH_CLOSE_MIN = 16 * 60 + 0       # 09:30:00 print.  bar stamped 16:00 -> covers 15:59:00-15:59:59

PV = 20.0                         # NQ dollars per point (documentation only; not used here)

# name -> (parquet file, value column in that file)
VOL_SOURCES = {
    "vix":   ("idx_VIX_daily.parquet",   "close"),
    "vxn":   ("idx_VXN_daily.parquet",   "close"),
    "vix9d": ("idx_VIX9D_daily.parquet", "close"),
    "vix3m": ("idx_VIX3M_daily.parquet", "close"),
    "vvix":  ("idx_VVIX_daily.parquet",  "vvix"),
    "skew":  ("idx_SKEW_daily.parquet",  "skew"),
}

_LOG: list[str] = []


def P(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    _LOG.append(s)


def _wall_check(label: str, dates: pd.Series) -> None:
    """Hard wall assertion. Raises rather than returning False -- there is no undo."""
    d = pd.to_datetime(pd.Series(dates)).dropna()
    if len(d) == 0:
        P(f"  WALL {label:<28s} EMPTY (vacuously clean)")
        return
    mx = d.max()
    n_bad = int((d >= WALL).sum())
    ok = (n_bad == 0) and (mx < WALL)
    P(f"  WALL {label:<28s} max={mx}  rows>=2022-01-01={n_bad}  ->  "
      f"{'PASS' if ok else 'FAIL'}")
    if not ok:
        raise AssertionError(f"WALL BREACH in {label}: max={mx}, {n_bad} rows >= {WALL}")


# ----------------------------------------------------------------------------------
# 1. NQ 1-minute -> per-RTH-session rows
# ----------------------------------------------------------------------------------
def load_nq_sessions() -> pd.DataFrame:
    sys.path.insert(0, os.path.join(ROOT, "research", "weekly_edge", "src"))
    from run_we_w17 import load_deep                                       # noqa: E402

    D = load_deep(START, END, extend=False)
    t = D["t"]                                                             # datetime64[s]

    # --- wall, applied to raw bars BEFORE anything is computed from them ---
    pre = t < WALL64
    n_post = int((~pre).sum())
    P(f"  raw bars loaded {len(t):,}   bars >= wall = {n_post}  (dropped)")
    if n_post:                                     # belt and braces; load_deep should give 0
        for k in ("o", "h", "l", "c", "v"):
            D[k] = D[k][pre]
        t = t[pre]
        D["t"] = t
        D["df"] = D["df"].loc[pre].reset_index(drop=True)
    _wall_check("nq_1m_bars", pd.to_datetime(t))

    tt = pd.to_datetime(t).as_unit("ns")
    mod = tt.hour * 60 + tt.minute
    day = tt.normalize()                            # calendar date of the bar's END stamp

    rth = (mod >= RTH_OPEN_MIN) & (mod <= RTH_CLOSE_MIN)
    P(f"  RTH bars (stamped 09:31..16:00) = {int(rth.sum()):,} "
      f"of {len(t):,} ({100*rth.mean():.1f}%)")

    b = pd.DataFrame({
        "session_date": day[rth],
        "mod": mod[rth],
        "open": D["o"][rth],
        "high": D["h"][rth],
        "low": D["l"][rth],
        "close": D["c"][rth],
        "volume": D["v"][rth],
    })

    # RTH lies wholly inside one calendar day, so the bar's own date IS the session date.
    # (This is deliberately NOT keyed on load_deep's `sid`, because a >60-minute hole in the
    #  thin overnight tape splits one exchange session into two `sid`s; grouping on the RTH
    #  bar's calendar date is immune to that.  Agreement is cross-checked below.)
    g = b.groupby("session_date", sort=True)

    opn = b[b["mod"] == RTH_OPEN_MIN].set_index("session_date")["open"]
    cls = b[b["mod"] == RTH_CLOSE_MIN].set_index("session_date")["close"]

    pan = pd.DataFrame({
        "session_date": g.size().index,
        "n_rth_bars": g.size().values,
        "rth_high": g["high"].max().values,
        "rth_low": g["low"].min().values,
        "rth_volume": g["volume"].sum().values,
        "first_rth_min": g["mod"].min().values,
        "last_rth_min": g["mod"].max().values,
    })
    pan["rth_open"] = pan["session_date"].map(opn).astype(float)
    pan["rth_close"] = pan["session_date"].map(cls).astype(float)
    pan["has_0931"] = pan["session_date"].isin(opn.index)
    pan["has_1600"] = pan["session_date"].isin(cls.index)
    pan["rth_full"] = pan["has_0931"] & pan["has_1600"]

    # half-day-tolerant anchors: first / last RTH bar actually present.
    b2 = b.sort_values(["session_date", "mod"])
    pan["rth_open_any"] = pan["session_date"].map(
        b2.groupby("session_date")["open"].first()).astype(float)
    pan["rth_close_any"] = pan["session_date"].map(
        b2.groupby("session_date")["close"].last()).astype(float)

    # session_quality:
    #   FULL          both anchor bars present (09:31 open and 16:00 close)
    #   SHORT_SESSION exchange holiday / half day -- tape stops before 15:00 ET
    #   GAPPY         neither: a hole in the substrate inside a normal-length session
    q = np.where(pan["rth_full"], "FULL",
                 np.where(pan["last_rth_min"] < 900, "SHORT_SESSION", "GAPPY"))
    pan["session_quality"] = q
    pan = pan.sort_values("session_date").reset_index(drop=True)

    # cross-check against the certified loader's own session labelling
    ld = set(pd.to_datetime(D["sess_date"]))
    mine = set(pan["session_date"])
    P(f"  session_date cross-check vs load_deep sess_date: "
      f"mine={len(mine)} loader={len(ld)} intersect={len(mine & ld)} "
      f"mine_only={len(mine - ld)} loader_only={len(ld - mine)}")
    P("    (loader_only rows are overnight-orphan sids with no RTH bars, and non-RTH "
      "fragments; they are correctly absent from an RTH panel)")
    return pan


# ----------------------------------------------------------------------------------
# 2. returns
# ----------------------------------------------------------------------------------
def add_returns(pan: pd.DataFrame) -> pd.DataFrame:
    pan = pan.copy()
    # CANONICAL (strict): 09:31-bar open -> 16:00-bar close.  NaN on holidays / half days.
    pan["rth_ret_pts"] = pan["rth_close"] - pan["rth_open"]
    pan["rth_ret_log"] = np.log(pan["rth_close"] / pan["rth_open"])
    # TOLERANT: first -> last RTH bar actually present.  Identical on every FULL session.
    pan["rth_ret_pts_any"] = pan["rth_close_any"] - pan["rth_open_any"]
    pan["rth_ret_log_any"] = np.log(pan["rth_close_any"] / pan["rth_open_any"])
    pan["rth_range_pts"] = pan["rth_high"] - pan["rth_low"]

    # overnight = PRIOR session's LAST RTH print -> THIS session's rth_open.
    # `rth_close_any` (not the strict 16:00 bar) is used for the *prior* leg on purpose: after a
    # 13:00 half day the economically correct prior close is the 13:00 print, and using the
    # strict column would NaN out the following, perfectly normal, session.
    prev_close = pan["rth_close_any"].shift(1)
    pan["prev_rth_close"] = prev_close
    pan["prev_rth_close_is_1600"] = pan["has_1600"].shift(1)
    pan["prev_session_date"] = pan["session_date"].shift(1)
    pan["overnight_ret_log"] = np.log(pan["rth_open"] / prev_close)
    pan["overnight_ret_pts"] = pan["rth_open"] - prev_close
    pan["overnight_gap_days"] = (
        pan["session_date"] - pan["prev_session_date"]).dt.days.astype("Float64")

    # realised_vol_21: trailing stdev (ddof=1) of rth_ret_log over the 21 PRIOR sessions that
    # have a defined rth_ret_log.  Strictly excludes today.  Computed on the valid subset then
    # mapped back, so a hole (half day with no 16:00 print) does not poison 21 later rows.
    v = pan.loc[pan["rth_ret_log"].notna(), "rth_ret_log"]
    rv = v.shift(1).rolling(21, min_periods=21).std(ddof=1)
    pan["realised_vol_21"] = np.nan
    pan.loc[rv.index, "realised_vol_21"] = rv.values
    return pan


# ----------------------------------------------------------------------------------
# 3. Cboe vol complex, joined STRICTLY BEFORE the session date
# ----------------------------------------------------------------------------------
def join_vol(pan: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    pan = pan.sort_values("session_date").reset_index(drop=True)
    stats = {}
    for name, (fn, col) in VOL_SOURCES.items():
        path = os.path.join(CBOE, fn)
        raw = pd.read_parquet(path)
        raw = raw.rename(columns={"trade_date": "date"})
        raw["date"] = pd.to_datetime(raw["date"])

        n_all = len(raw)
        raw = raw.loc[raw["date"] < WALL, ["date", col]].dropna()
        P(f"  {name:<6s} {fn:<24s} rows {n_all:,} -> {len(raw):,} after wall filter "
          f"({n_all - len(raw):,} post-wall rows dropped unread)")
        _wall_check(f"cboe_{name}", raw["date"])

        raw = raw.rename(columns={col: name, "date": f"{name}_asof"})
        raw = raw.sort_values(f"{name}_asof").reset_index(drop=True)

        pan = pd.merge_asof(
            pan, raw,
            left_on="session_date", right_on=f"{name}_asof",
            direction="backward",
            allow_exact_matches=False,          # <-- STRICTLY BEFORE the session date
        )
        have = pan[name].notna()
        stats[name] = dict(
            n_src=len(raw),
            src_span=(raw[f"{name}_asof"].min(), raw[f"{name}_asof"].max()),
            n_null=int((~have).sum()),
            n_ok=int(have.sum()),
        )
        # HARD ASSERTION 2: every joined observation is dated strictly before its session
        sub = pan.loc[have, ["session_date", f"{name}_asof"]]
        bad = int((sub[f"{name}_asof"] >= sub["session_date"]).sum())
        lag = (sub["session_date"] - sub[f"{name}_asof"]).dt.days
        stats[name].update(n_bad=bad, lag_min=int(lag.min()), lag_med=float(lag.median()),
                           lag_max=int(lag.max()))
        if bad:
            raise AssertionError(f"CAUSALITY BREACH: {bad} rows of {name} joined on or after "
                                 f"the session date")
    return pan, stats


# ----------------------------------------------------------------------------------
def main() -> None:
    P("=" * 96)
    P("G3_VOLSHORT01 :: discovery panel  (DISCOVERY_CONTAMINATED -- rule proposal only)")
    P(f"wall = {WALL.date()}   nothing on or after this date may be read, loaded, aggregated "
      f"or counted")
    P("=" * 96)

    P("\n[1] NQ 1-minute -> RTH sessions")
    pan = load_nq_sessions()

    P("\n[2] returns")
    pan = add_returns(pan)

    P("\n[3] certified free Cboe daily vol complex, joined on the PRIOR trading day")
    pan, jstats = join_vol(pan)

    # ------------------------------------------------------------------ assertions
    P("\n" + "=" * 96)
    P("HARD REQUIREMENT 1 -- max(session_date) < 2022-01-01")
    P("=" * 96)
    mx = pan["session_date"].max()
    a1 = bool(mx < WALL)
    P(f"  max(session_date) = {mx.date()}    < 2022-01-01 ?  {a1}    -> "
      f"{'PASS' if a1 else 'FAIL'}")
    assert a1, "WALL BREACH: panel contains a session on or after 2022-01-01"
    for c in ["session_date", "prev_session_date"] + [f"{k}_asof" for k in VOL_SOURCES]:
        _wall_check(f"panel.{c}", pan[c])

    P("\n" + "=" * 96)
    P("HARD REQUIREMENT 2 -- every vol column joined from a date STRICTLY BEFORE the session")
    P("=" * 96)
    P(f"  {'col':<7s} {'src_rows':>8s} {'src_first':>11s} {'src_last':>11s} "
      f"{'joined':>7s} {'NaN':>6s} {'viol':>5s} {'lag_min':>8s} {'lag_med':>8s} {'lag_max':>8s}")
    for k, s in jstats.items():
        P(f"  {k:<7s} {s['n_src']:>8,} {str(s['src_span'][0].date()):>11s} "
          f"{str(s['src_span'][1].date()):>11s} {s['n_ok']:>7,} {s['n_null']:>6,} "
          f"{s['n_bad']:>5d} {s['lag_min']:>8d} {s['lag_med']:>8.1f} {s['lag_max']:>8d}")
    tot_bad = sum(s["n_bad"] for s in jstats.values())
    P(f"  total lag<=0 violations = {tot_bad}   -> {'PASS' if tot_bad == 0 else 'FAIL'}")
    P("  NaN rows are sessions that precede the index's own inception date "
      "(VXN 2009-09, VIX3M 2009-09, VIX9D 2011-01, VVIX 2006-03) -- not join failures.")

    P("\n" + "=" * 96)
    P("HARD REQUIREMENT 3 -- shape, span, per-column non-null counts")
    P("=" * 96)
    P(f"  rows              = {len(pan):,}")
    P(f"  date span         = {pan['session_date'].min().date()} .. "
      f"{pan['session_date'].max().date()}")
    P(f"  distinct dates    = {pan['session_date'].nunique():,}   "
      f"(duplicates = {len(pan) - pan['session_date'].nunique()})")
    P(f"  rth_full sessions = {int(pan['rth_full'].sum()):,}  "
      f"(missing 09:31 = {int((~pan['has_0931']).sum())}, "
      f"missing 16:00 = {int((~pan['has_1600']).sum())})")
    P(f"\n  {'column':<22s} {'non-null':>9s} {'null':>7s} {'dtype':<18s}")
    for c in pan.columns:
        nn = int(pan[c].notna().sum())
        P(f"  {c:<22s} {nn:>9,} {len(pan)-nn:>7,} {str(pan[c].dtype):<18s}")

    P("\n  per-year session counts:")
    yc = pan.groupby(pan["session_date"].dt.year).size()
    P("   " + "  ".join(f"{y}:{n}" for y, n in yc.items()))
    P("  (>252/yr because NQ trades shortened sessions on several US EQUITY holidays; those "
      "sessions have no 16:00 bar and are labelled SHORT_SESSION)")

    P("\n  session_quality:")
    for k, n in pan["session_quality"].value_counts().items():
        P(f"    {k:<14s} {n:>5,}")
    inc = pan[pan["session_quality"] != "FULL"]
    P(f"  last RTH bar (minute-of-day) on the {len(inc):,} non-FULL sessions:")
    P("    " + "  ".join(f"{int(m)//60:02d}:{int(m)%60:02d}={c}"
                         for m, c in inc["last_rth_min"].value_counts().head(8).items()))
    P("    month-day concentration: " + "  ".join(
        f"{d}={c}" for d, c in
        inc["session_date"].dt.strftime("%m-%d").value_counts().head(8).items()))
    P("    -> 07-03/07-04, 12-24, the Friday after Thanksgiving, MLK, Presidents' Day and "
      "Labor Day. These are exchange holidays, not corrupt data.")
    gappy = pan[pan["session_quality"] == "GAPPY"]
    P(f"  GAPPY sessions ({len(gappy)}) -- substrate holes inside a normal-length session:")
    for _, r in gappy.iterrows():
        P(f"    {r['session_date'].date()}  first={int(r['first_rth_min'])//60:02d}:"
          f"{int(r['first_rth_min'])%60:02d}  last={int(r['last_rth_min'])//60:02d}:"
          f"{int(r['last_rth_min'])%60:02d}  bars={int(r['n_rth_bars'])}")
    same = pan.loc[pan["rth_full"] & pan["rth_ret_pts"].notna()]
    d_any = (same["rth_ret_pts"] - same["rth_ret_pts_any"]).abs().max()
    P(f"  strict vs tolerant return, max |diff| over FULL sessions = {d_any:.10f}  -> "
      f"{'IDENTICAL' if d_any == 0 else 'DIFFERS (investigate)'}")

    # ------------------------------------------------------------------ write
    os.makedirs(OUT, exist_ok=True)
    pq = os.path.join(OUT, "panel_pre2022.parquet")
    tmp = pq + ".tmp"
    pan.to_parquet(tmp, index=False)
    os.replace(tmp, pq)
    back = pd.read_parquet(pq)
    assert len(back) == len(pan) and back["session_date"].max() < WALL
    P(f"\n  WROTE {pq}  ({os.path.getsize(pq):,} bytes, re-read {len(back):,} rows, "
      f"max date {back['session_date'].max().date()})")

    write_readme(pan, jstats)
    with open(os.path.join(OUT, "panel_build_log.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(_LOG) + "\n")
    P(f"  WROTE {os.path.join(OUT, 'panel_README.md')}")
    P(f"  WROTE {os.path.join(OUT, 'panel_build_log.txt')}")


# ----------------------------------------------------------------------------------
def write_readme(pan: pd.DataFrame, jstats: dict) -> None:
    lo, hi = pan["session_date"].min().date(), pan["session_date"].max().date()
    rows = []
    for k, s in jstats.items():
        rows.append(f"| `{k}` | {s['n_ok']:,} | {s['n_null']:,} | "
                    f"{s['src_span'][0].date()} | {s['lag_med']:.1f} | {s['lag_max']} |")
    joinrows = "\n".join(rows)
    qc = pan["session_quality"].value_counts()
    qtable = ("| quality | rows | meaning |\n|---|---|---|\n"
              + "\n".join(f"| `{k}` | {v:,} | "
                          + {"FULL": "both anchor bars present — the clean population",
                             "SHORT_SESSION": "exchange holiday / half day, tape stops "
                                              "before 15:00 ET",
                             "GAPPY": "substrate hole inside a normal-length session"}[k]
                          + " |" for k, v in qc.items()))

    md = f"""# `panel_pre2022.parquet` — G3_VOLSHORT01 discovery panel

**Evidence status: `DISCOVERY_CONTAMINATED`.** Nothing derived from this panel is a result.
It exists to produce a *rule proposal* that someone else freezes and commits **before** the
one-shot confirmation read of 2022-01-01 → 2026-07-31.

Built by `runs/G3_VOLSHORT01_20260831/src/discovery/panel.py`.
Build log: `panel_build_log.txt` (every assertion, verbatim).

## The wall

`2022-01-01` is a wall. Every frame in the builder is filtered to `< 2022-01-01` at load and the
filter is asserted and printed. Panel `max(session_date)` = **{hi}**.

The builder calls `load_deep(..., extend=False)`, **not** `extend=True`. `extend=True` reads
`runs/SM1M_SUBSTRATE/out/nq_1m_2022_2026.parquet` and appends only the bars stamped after
2026-05-29 16:59 — every one of them post-wall, and every one of them then discarded by the
`<= 2021-12-31` filter. It cannot change a value here; it can only put post-wall bars in memory.
Output over the requested window is bit-identical.

## Rows

One row per **NQ RTH session**: one row per calendar date on which at least one bar stamped in
`09:31 … 16:00` ET exists in the certified 1-minute substrate.

- rows: **{len(pan):,}**
- span: **{lo} … {hi}**
- distinct `session_date`: {pan['session_date'].nunique():,} (duplicates: {len(pan)-pan['session_date'].nunique()})
- `rth_full` (has both the 09:31 and the 16:00 bar): **{int(pan['rth_full'].sum()):,}**

Sessions are keyed on the **calendar date of the RTH bars**, not on `load_deep`'s `sid`. A
>60-minute hole in the thin overnight tape splits one exchange session into two `sid`s; RTH lies
wholly inside one calendar day, so date-keying is immune to that. The cross-check against
`sess_date` is printed in the build log.

### `session_quality` — read this before you filter

{qtable}

The count is ~257/year, not ~252, because **NQ trades shortened sessions on several US equity
holidays** (MLK, Presidents' Day, Good Friday, Memorial Day, July 3/4, Labor Day, the Friday
after Thanksgiving, Christmas Eve). Those sessions stop at 11:30 / 13:00 / 13:15 ET, so they have
no 16:00 bar and the **strict** `rth_ret_pts` is `NaN` on them. They are exchange holidays, not
corrupt data. `GAPPY` is the small residue of genuine substrate holes (all but two in 2006–07).

**Default recommendation:** condition on `session_quality == "FULL"` and use the strict
`rth_ret_pts`. If you want the holiday sessions in, use `rth_ret_pts_any` — but say so, and note
that a holiday session's implied-vol reading is stale by 3–5 days.

## Bar convention (this is the one that has bitten this repo before)

Bars are **END-stamped**. The bar stamped `09:31` covers `09:30:00–09:30:59`, so **its `open` is
the 09:30:00 print**. The bar stamped `16:00` covers `15:59:00–15:59:59`, so **its `close` is the
last RTH print**. There is no ±1-minute shift. Timestamps are exchange-session time (ET).

## Columns — definition and the instant each becomes KNOWN

| column | definition | known at |
|---|---|---|
| `session_date` | calendar date (ET) of the RTH bars | — (label) |
| `rth_open` | `open` of the bar stamped `09:31` = the 09:30:00 print | 09:30:00 |
| `rth_close` | `close` of the bar stamped `16:00` = the last RTH print | 15:59:59 |
| `rth_open_any` / `rth_close_any` | open of the **first** / close of the **last** RTH bar actually present — half-day tolerant; identical to the strict pair on every `FULL` session | 09:30:00 / last print |
| `session_quality` | `FULL` \\| `SHORT_SESSION` \\| `GAPPY` (see above) | 15:59:59 |
| `rth_high` / `rth_low` | max/min over bars stamped `09:31…16:00` | 15:59:59 |
| `rth_range_pts` | `rth_high − rth_low` | 15:59:59 |
| `rth_volume` | sum of volume over bars stamped `09:31…16:00` | 15:59:59 |
| `n_rth_bars` | count of bars stamped `09:31…16:00` | 15:59:59 |
| `first_rth_min` / `last_rth_min` | minute-of-day of the first/last RTH bar stamp (571 = 09:31, 960 = 16:00) | 15:59:59 |
| `has_0931` / `has_1600` / `rth_full` | presence flags for the two anchor bars | 15:59:59 |
| `rth_ret_pts` | `rth_close − rth_open` — **the intraday window the mechanism is about** | 15:59:59 |
| `rth_ret_log` | `log(rth_close / rth_open)` | 15:59:59 |
| `rth_ret_pts_any` / `rth_ret_log_any` | same from the tolerant anchors | last print |
| `prev_session_date` | `session_date` of the previous panel row | 09:30:00 |
| `prev_rth_close` | previous row's `rth_close_any` — the prior session's **last RTH print**. Deliberately the tolerant column: after a 13:00 half day the economically correct prior close is the 13:00 print, and using the strict one would `NaN` out the following, perfectly normal, session. | prior last print |
| `prev_rth_close_is_1600` | whether that prior close was a true 16:00 bar | prior last print |
| `overnight_ret_log` | `log(rth_open / prev_rth_close)` — the **overnight** leg of the split | 09:30:00 |
| `overnight_ret_pts` | `rth_open − prev_rth_close` | 09:30:00 |
| `overnight_gap_days` | calendar days between `prev_session_date` and `session_date` | 09:30:00 |
| `realised_vol_21` | stdev (`ddof=1`) of `rth_ret_log` over the **21 prior** sessions with a defined `rth_ret_log`. **Causal — excludes today.** | 09:30:00 (in fact prior 15:59:59) |
| `vix` `vxn` `vix9d` `vix3m` `vvix` `skew` | **daily close of the latest Cboe session STRICTLY BEFORE `session_date`** | prior day 16:15 ET, hence available at 09:30:00 |
| `<name>_asof` | the Cboe trade date the value was taken from; `< session_date` is asserted | — (audit) |

`realised_vol_21` and the six vol columns are the only columns a signal may condition on, and
they are all known before 09:30:00. `rth_open` is known **at** 09:30:00 and is the entry price.
Everything else is realised after entry.

### Which vol index

`vxn` is the **Nasdaq-100** volatility index and is the appropriate ex-ante implied variance for
NQ. `vix` is the S&P 500 index; it starts 15+ years earlier and is the deeper history. Any
specification must say which it used, and the two are not interchangeable.

## Join audit (strictly-before, asserted)

| col | joined | NaN | source starts | median lag (days) | max lag (days) |
|---|---|---|---|---|---|
{joinrows}

`NaN` counts are sessions preceding the index's own inception (VVIX 2006-03, VXN 2009-09,
VIX3M 2009-09, VIX9D 2011-01), **not** join failures — the `viol` (lag ≤ 0) count is 0 for every
column and the builder raises if it is not. Median lag is 1 day; max lag > 1 is a weekend or an
equity-market holiday that is not a CME holiday.

## Costs (for anyone computing dollars off this panel)

NQ point value **$20**. Measured all-in execution (G2_EXEC01, 113 real round turns) is
**$20.65/ctrRT** median $20.00, p90 $35.00. A full-session 09:30→16:00 round turn must therefore
clear **≈1.03 NQ points**, not 0.9. Report net at $4.36 (commission only — a **floor**, never a
headline), **$20.65 (primary)** and $25.01.

## Inference (binding — do not use session-level t)

High-vol sessions arrive in **episodes**. Use `common.episodes(...)`, report the **episode
count** beside every statistic, and do inference by **whole-episode block bootstrap**. Where a
count enters, use `K_eff = K / (1 + (K−1)·ρ̄)` with ρ̄ printed. A session-level t may be printed
only when labelled `DIAGNOSTIC ONLY`.

### The "8-14 episodes" prior does NOT hold on this panel - measure, don't assume

Measured (see `smoke_test.txt`, reproducible via `src/discovery/smoke_test.py`), on `FULL`
sessions with a causal rolling-252 tercile:

| high state | high sessions | K@gap10 | K@gap21 | K@gap42 | rho_bar | K_eff@gap10 | top-5 share |
|---|---|---|---|---|---|---|---|
| `vix` tercile | 1,199 | 59 | 43 | 30 | 0.034 | 19.8 | 51.3% |
| `vxn` tercile | 858 | 53 | 33 | 18 | 0.026 | 22.6 | 50.5% |
| `vix > 25` | 699 | 36 | 27 | - | - | - | - |
| `vix > 30` | 379 | 21 | 17 | - | - | - | - |

At `gap_days=10` the count is **~59, not 8-14**. But K alone misleads in the other direction too:
episode sizes run 1 -> 207 sessions and **five episodes carry half of all high-state sessions**,
so 59 badly overstates independence. Quote **K, rho_bar and K_eff together**, never K alone, and
let the whole-episode block bootstrap - not the count - carry the inference.
"""
    path = os.path.join(OUT, "panel_README.md")
    data = md.encode("utf-8")
    tmp = path + ".tmp"
    with open(tmp, "wb") as f:
        f.write(data)
    assert os.path.getsize(tmp) > 0
    os.replace(tmp, path)


if __name__ == "__main__":
    main()
