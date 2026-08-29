"""G2_F1_ORB01_20260829 — 15-min opening-range breakout continuation on modern NQ.

Preregistered spec: runs/G2_F1_ORB01_20260829/spec.yaml (FROZEN).
Ambiguity resolutions: out/spec_resolutions.txt (written before any affected number).
Ledger trial G00016. Gate table is PRINTED BY THIS PROGRAM (GATE/SPEC/OBSERVED/PASS-FAIL).

No parameter search of any kind occurs in this file: OR length (15 min), entry (+1 tick
stop), exit (15:59 close), costs ($25.01 primary / $33 stress) are all spec constants.
"""
from __future__ import annotations

import json
import math
import os
import sys
from datetime import date

import numpy as np
import pandas as pd

REPO = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, REPO)

from research_sdk.seal_guard import assert_presealed, truncate_presealed
from research_sdk.session_boundary import assert_not_locked_forward
from research_sdk.null_guard import run_circular_null, verify_null_sensitivity

RUN_DIR = os.path.join(REPO, "runs", "G2_F1_ORB01_20260829")
OUT = os.path.join(RUN_DIR, "out")

MODERN_PARQUET = os.path.join(REPO, r"runs\SM1M_SUBSTRATE\out\nq_1m_2022_2026.parquet")
DEEP_PARQUET = os.path.join(REPO, r"research\scalping_lab\substrate\minute\NQ\nq1m_2005_202605.parquet")

TICK = 0.25
PT_USD = 20.0
COST_PRIMARY = 25.01
COST_STRESS = 33.00

# END-stamped minute-of-day slots: OR bars stamped 09:31..09:45; scan bars 09:46..15:59
MOD_OR_LO, MOD_OR_HI = 9 * 60 + 31, 9 * 60 + 45      # 571..585
MOD_SCAN_LO, MOD_SCAN_HI = 9 * 60 + 46, 15 * 60 + 59  # 586..959
GRID_LO, GRID_HI = MOD_OR_LO, MOD_SCAN_HI              # canonical grid 09:31..15:59 (389 slots)
NGRID = GRID_HI - GRID_LO + 1

GATE_FIRST, GATE_LAST = date(2022, 1, 1), date(2026, 7, 31)
DEEP_FIRST, DEEP_LAST = date(2006, 1, 1), date(2021, 12, 31)


# ----------------------------------------------------------------------------------
def load_window(path: str, first: date, last: date, ctx: str, parse_str: bool) -> pd.DataFrame:
    """Load a substrate, pass it through seal_guard, cut to the session window, keep RTH."""
    df = pd.read_parquet(path, columns=["time", "open", "high", "low", "close"])
    if parse_str:
        df["time"] = pd.to_datetime(df["time"], format="%Y-%m-%d %H:%M:%S")
    df, n_dropped = truncate_presealed(df, "time", ctx)          # mechanical seal cut, count printed
    assert_presealed(df, "time", ctx + ":post-truncate")          # certify clean
    print(f"seal_guard PASS [{ctx}]: {n_dropped} sealed row(s) mechanically dropped, frame certified pre-seal")
    assert_not_locked_forward(last)                               # window itself inside LOCKED_FORWARD
    # session_id: 18:00->17:00 ET unit; hour>=18 rolls to next calendar day's label
    t = df["time"]
    sess = t.dt.date.where(t.dt.hour < 18, (t + pd.Timedelta(days=1)).dt.date)
    df["session"] = sess
    df = df[(df["session"] >= first) & (df["session"] <= last)]
    mod = t.dt.hour * 60 + t.dt.minute
    df = df[(mod >= GRID_LO) & (mod <= GRID_HI)]                  # RTH slice only (09:31..15:59 stamps)
    df = df.sort_values("time", kind="stable").reset_index(drop=True)
    print(f"loaded [{ctx}]: {len(df):,} RTH bars, {df['session'].nunique():,} sessions "
          f"({df['session'].min()} .. {df['session'].max()})")
    return df


# ----------------------------------------------------------------------------------
def orb_decisions(df: pd.DataFrame) -> dict:
    """The FROZEN ORB policy, computed only from `df` (black-box for the null too).

    Returns per-session-block arrays (block order = order of first appearance):
      uniques, has_or, has_scan, eligible, traded, direction (+1/-1/0), entry_slot,
      entry_pos (row index into df), fill, bothside,
      exit_close, exit_ts, first_scan_open (control entry), or_high, or_low.
    """
    codes, uniques = pd.factorize(df["session"], sort=False)
    n = len(uniques)
    t = df["time"]
    mod = (t.dt.hour * 60 + t.dt.minute).to_numpy()
    high = df["high"].to_numpy()
    low = df["low"].to_numpy()
    opn = df["open"].to_numpy()
    cls = df["close"].to_numpy()

    or_mask = (mod >= MOD_OR_LO) & (mod <= MOD_OR_HI)
    scan_mask = (mod >= MOD_SCAN_LO) & (mod <= MOD_SCAN_HI)

    orh = np.full(n, np.nan)
    orl = np.full(n, np.nan)
    g = pd.DataFrame({"c": codes[or_mask], "h": high[or_mask], "l": low[or_mask]}).groupby("c")
    agg = g.agg(h=("h", "max"), l=("l", "min"))
    orh[agg.index.to_numpy()] = agg["h"].to_numpy()
    orl[agg.index.to_numpy()] = agg["l"].to_numpy()
    has_or = ~np.isnan(orh)

    scan_pos = np.flatnonzero(scan_mask)
    sc = codes[scan_pos]
    has_scan = np.zeros(n, dtype=bool)
    has_scan[np.unique(sc)] = True
    eligible = has_or & has_scan

    # exit bar = last scan bar per session; control entry = first scan bar's open
    firsts = np.unique(sc, return_index=True)
    lasts = np.unique(sc[::-1], return_index=True)
    exit_close = np.full(n, np.nan)
    exit_ts = np.full(n, np.datetime64("NaT"), dtype="datetime64[ns]")
    first_scan_open = np.full(n, np.nan)
    f_codes, f_idx = firsts
    l_codes, l_idx = lasts
    first_scan_open[f_codes] = opn[scan_pos[f_idx]]
    last_rows = scan_pos[len(sc) - 1 - l_idx]
    exit_close[l_codes] = cls[last_rows]
    exit_ts[l_codes] = t.to_numpy()[last_rows]

    # first breach (stop-entry levels OR_high+1t / OR_low-1t), NaN levels never trigger
    lvl_l = orh[sc] + TICK
    lvl_s = orl[sc] - TICK
    trig_l = high[scan_pos] >= lvl_l
    trig_s = low[scan_pos] <= lvl_s
    trig = trig_l | trig_s
    tp = np.flatnonzero(trig)
    tc = sc[tp]
    u_codes, u_first = np.unique(tc, return_index=True)   # first occurrence = earliest in time (blocks contiguous)
    breach_rows = scan_pos[tp[u_first]]

    traded = np.zeros(n, dtype=bool)
    bothside = np.zeros(n, dtype=bool)
    direction = np.zeros(n, dtype=np.int8)
    entry_slot = np.full(n, -1, dtype=np.int64)
    entry_pos = np.full(n, -1, dtype=np.int64)
    fill = np.full(n, np.nan)

    bL = trig_l[tp[u_first]]
    bS = trig_s[tp[u_first]]
    both = bL & bS
    bothside[u_codes] = both
    ok = ~both
    oc = u_codes[ok]
    orow = breach_rows[ok]
    d = np.where(bL[ok], 1, -1).astype(np.int8)
    direction[oc] = d
    traded[oc] = True
    entry_pos[oc] = orow
    entry_slot[oc] = mod[orow] - GRID_LO
    f_long = np.maximum(orh[oc] + TICK, opn[orow])
    f_short = np.minimum(orl[oc] - TICK, opn[orow])
    fill[oc] = np.where(d == 1, f_long, f_short)

    # a session ineligible by R5 takes no trade and is not a both-side count either
    traded &= eligible
    bothside &= eligible

    return dict(uniques=uniques, has_or=has_or, has_scan=has_scan, eligible=eligible,
                traded=traded, direction=direction, entry_slot=entry_slot, entry_pos=entry_pos,
                fill=fill, bothside=bothside, exit_close=exit_close, exit_ts=exit_ts,
                first_scan_open=first_scan_open, or_high=orh, or_low=orl)


def build_trades(df: pd.DataFrame, dec: dict) -> pd.DataFrame:
    """Trade table [session_id, entry_ts, direction, entry_px, exit_px, gross_pts, net_usd]."""
    idx = np.flatnonzero(dec["traded"])
    tarr = df["time"].to_numpy()
    rows = []
    for j in idx:
        d = int(dec["direction"][j])
        fill = float(dec["fill"][j])
        exit_px = float(dec["exit_close"][j])
        gross = (exit_px - fill) * d
        rows.append({
            "session_id": dec["uniques"][j].isoformat(),
            "entry_ts": pd.Timestamp(tarr[dec["entry_pos"][j]]).isoformat(sep=" "),
            "direction": "long" if d == 1 else "short",
            "entry_px": fill,
            "exit_px": exit_px,
            "gross_pts": gross,
            "net_usd": gross * PT_USD - COST_PRIMARY,
        })
    return pd.DataFrame(rows, columns=["session_id", "entry_ts", "direction",
                                       "entry_px", "exit_px", "gross_pts", "net_usd"])


# ----------------------------------------------------------------------------------
def weekly_series(dec: dict, trades: pd.DataFrame) -> pd.DataFrame:
    """ISO-week clustered net series over every week containing >=1 session with RTH bars."""
    sess = pd.Series(list(dec["uniques"]))
    iso = pd.to_datetime(sess.astype(str)).dt.isocalendar()
    skey = iso["year"].astype(str) + "-W" + iso["week"].astype(str).str.zfill(2)
    per_sess_net = pd.Series(0.0, index=sess.astype(str))
    if len(trades):
        tn = trades.groupby("session_id")["net_usd"].sum()
        per_sess_net.loc[tn.index] = tn.to_numpy()
    wk = pd.DataFrame({"week": skey.to_numpy(), "session": sess.astype(str).to_numpy(),
                       "net_usd": per_sess_net.to_numpy()})
    n_tr = trades.groupby("session_id").size() if len(trades) else pd.Series(dtype=int)
    wk["n_trades"] = wk["session"].map(n_tr).fillna(0).astype(int)
    out = wk.groupby("week", sort=True).agg(n_sessions=("session", "size"),
                                            n_trades=("n_trades", "sum"),
                                            net_usd=("net_usd", "sum")).reset_index()
    return out


def weekly_t(wknet: np.ndarray) -> tuple[float, float, int]:
    nw = len(wknet)
    m = float(np.mean(wknet))
    sd = float(np.std(wknet, ddof=1))
    tstat = m / (sd / math.sqrt(nw)) if sd > 0 else float("inf") * np.sign(m or 1)
    return tstat, sd, nw


# ----------------------------------------------------------------------------------
def make_null_functions(frame: pd.DataFrame):
    """null_guard contract: decision_fn re-runs the frozen policy on the (shifted) frame;
    statistic_fn scores block-j decisions against ORIGINAL block-j outcomes (R8)."""
    cache: dict[int, tuple[np.ndarray, np.ndarray]] = {}

    def decision_fn(f: pd.DataFrame) -> np.ndarray:
        dc = orb_decisions(f)
        return np.column_stack([dc["traded"].astype(np.int64),
                                dc["direction"].astype(np.int64),
                                dc["entry_slot"]])

    def base_grids(base: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
        key = id(base)
        if key not in cache:
            codes, uniques = pd.factorize(base["session"], sort=False)
            mod = (base["time"].dt.hour * 60 + base["time"].dt.minute).to_numpy()
            slot = mod - GRID_LO
            grid = np.full((len(uniques), NGRID), np.nan)
            grid[codes, slot] = base["close"].to_numpy()
            gdf = pd.DataFrame(grid)
            grid = gdf.ffill(axis=1).bfill(axis=1).to_numpy()
            cache[key] = (grid, grid[:, -1].copy())
        return cache[key]

    def statistic_fn(decisions: np.ndarray, base: pd.DataFrame) -> float:
        grid, last = base_grids(base)
        traded = decisions[:, 0] == 1
        if not traded.any():
            return 0.0
        j = np.flatnonzero(traded)
        d = decisions[j, 1].astype(float)
        ref = grid[j, decisions[j, 2] - 1]           # entry_slot>=15 so slot-1>=14 exists
        pnl = PT_USD * d * (last[j] - ref) - COST_PRIMARY
        return float(np.sum(pnl))

    return decision_fn, statistic_fn


# ----------------------------------------------------------------------------------
def main() -> None:
    print("data_esnq NOT read by this run (no ES leg in spec) — ALLOWLIST_DEV_44 not exercised.")
    modern = load_window(MODERN_PARQUET, GATE_FIRST, GATE_LAST, "ORB01:modern-gate", parse_str=False)
    deep = load_window(DEEP_PARQUET, DEEP_FIRST, DEEP_LAST, "ORB01:deep-diagnostic", parse_str=True)

    # ---------------- primary (modern gate window) ----------------
    dec = orb_decisions(modern)
    trades = build_trades(modern, dec)
    n_elig = int(dec["eligible"].sum())
    n_sess = len(dec["uniques"])
    n_both = int(dec["bothside"].sum())
    n_long = int((trades["direction"] == "long").sum())
    n_short = int((trades["direction"] == "short").sum())
    net25 = float(trades["net_usd"].sum())
    gross_pts = float(trades["gross_pts"].sum())
    net33 = float((trades["gross_pts"] * PT_USD - COST_STRESS).sum())
    long_net = float(trades.loc[trades["direction"] == "long", "net_usd"].sum())
    short_net = float(trades.loc[trades["direction"] == "short", "net_usd"].sum())

    wk = weekly_series(dec, trades)
    tstat, sd_w, n_w = weekly_t(wk["net_usd"].to_numpy())
    mde_w = 2.0 * sd_w / math.sqrt(n_w)

    # ---------------- O2 null (sensitivity first, then >=300 shifts) ----------------
    frame = modern[["time", "open", "high", "low", "close", "session"]].copy()
    loader = lambda: frame
    decision_fn, statistic_fn = make_null_functions(frame)
    sens = verify_null_sensitivity(loader, decision_fn, statistic_fn,
                                   shifts=[1, 7, 61], unit="session")
    print(f"null sensitivity VERIFIED: real={sens['real_stat']:.2f} spread={sens['spread']:.2f} "
          f"across probe shifts [1,7,61] — the null can move")
    null = run_circular_null(loader, decision_fn, statistic_fn,
                             n_shifts=300, unit="session", seed=0)
    null_stats = np.asarray(null["null_stats"])
    p95 = float(np.percentile(null_stats, 95))
    o2_real = float(null["real_stat"])
    o2_pct = float(null["percentile"]) * 100.0
    o2_pge = float(null["p_ge"])

    # ---------------- O3 control ----------------
    el = np.flatnonzero(dec["eligible"])
    ctrl_gross = dec["exit_close"][el] - dec["first_scan_open"][el]
    ctrl_net = float(np.sum(ctrl_gross * PT_USD - COST_PRIMARY))

    # ---------------- deep diagnostic (2006-2021, non-gate) ----------------
    dec_d = orb_decisions(deep)
    trades_d = build_trades(deep, dec_d)
    net25_d = float(trades_d["net_usd"].sum())
    n_elig_d = int(dec_d["eligible"].sum())
    n_both_d = int(dec_d["bothside"].sum())
    sign_flip = (np.sign(net25_d) != np.sign(net25)) and net25 != 0 and net25_d != 0

    # ---------------- diagnostics ----------------
    trades["year"] = trades["session_id"].str[:4].astype(int)
    trades_d["year"] = trades_d["session_id"].str[:4].astype(int)
    sess_year = pd.Series([u.year for u in dec["uniques"]])
    elig_year = sess_year[dec["eligible"]].value_counts().sort_index()
    both_year = sess_year[dec["bothside"]].value_counts().sort_index()

    per_year_rows = []
    for y in sorted(set(trades["year"].unique()) | set(elig_year.index)):
        ty = trades[trades["year"] == y]
        per_year_rows.append(dict(
            year=y, n_eligible=int(elig_year.get(y, 0)), n_trades=len(ty),
            n_long=int((ty["direction"] == "long").sum()),
            n_short=int((ty["direction"] == "short").sum()),
            n_bothside=int(both_year.get(y, 0)),
            net25=float(ty["net_usd"].sum()),
            net33=float((ty["gross_pts"] * PT_USD - COST_STRESS).sum())))
    per_year = pd.DataFrame(per_year_rows)

    per_year_d = trades_d.groupby("year").agg(
        n_trades=("net_usd", "size"), net25=("net_usd", "sum")).reset_index()

    # leave-one-year-out (gate window)
    loyo_rows = []
    for y in sorted(per_year["year"].unique()):
        keep = np.array([u.year != y for u in dec["uniques"]])
        dec_k = {k: (v[keep] if isinstance(v, np.ndarray) and len(v) == n_sess else v)
                 for k, v in dec.items()}
        dec_k["uniques"] = dec["uniques"][keep]
        tr_k = trades[trades["year"] != y]
        wk_k = weekly_series(dec_k, tr_k)
        t_k, _, nw_k = weekly_t(wk_k["net_usd"].to_numpy())
        loyo_rows.append(dict(excl_year=y, net25=float(tr_k["net_usd"].sum()),
                              t_weekly=t_k, n_weeks=nw_k))
    loyo = pd.DataFrame(loyo_rows)

    # top-decile traded-session concentration
    sess_net = trades.groupby("session_id")["net_usd"].sum().sort_values(ascending=False)
    k10 = math.ceil(0.10 * len(sess_net)) if len(sess_net) else 0
    top_dec_net = float(sess_net.iloc[:k10].sum()) if k10 else 0.0
    top_dec_share = (top_dec_net / net25) if net25 > 0 else float("nan")

    # ---------------- gates ----------------
    o1_pass = (net25 > 0) and (tstat >= 2.0)
    o2_pass = o2_real > p95
    o3_pass = net25 > ctrl_net
    survived = o1_pass and o2_pass and o3_pass
    fragile = net33 <= 0
    verdict = "SURVIVED-DISCOVERY" if survived else "NULL"
    verdict_line = verdict + (" [REGIME-FRAGILE at $33/RT]" if fragile else "")
    if survived:
        verdict_line += " -> routes to robustness + independent implementation, NOT promotion"
    else:
        verdict_line += " — closed at formulation"

    # ---------------- gate table (printed by program) ----------------
    L = []
    A = L.append
    A("G2_F1_ORB01_20260829 — GATE TABLE (printed by program; ledger trial G00016)")
    A("primary: 15-min ORB, +1-tick stop-entry, first breach only, exit 15:59 close, 1ct $20/pt")
    A(f"gate window sessions {GATE_FIRST} .. {GATE_LAST} | sessions with RTH bars {n_sess} | eligible {n_elig}")
    A("evidence status: DISCOVERY_CONSUMED (gate window includes the burned 2026-05-31..07-31 span; no sealed reads)")
    A("")
    A(f"{'GATE':<6}{'SPEC':<58}{'OBSERVED':<64}{'PASS-FAIL'}")
    A(f"{'O1a':<6}{'modern net > 0 at $25.01/RT':<58}"
      f"{f'net ${net25:,.2f} ({len(trades)} trades, {gross_pts:+.2f} pts gross)':<64}"
      f"{'PASS' if net25 > 0 else 'FAIL'}")
    A(f"{'O1b':<6}{'weekly session-clustered t >= 2.0':<58}"
      f"{f't = {tstat:.3f} (Nw={n_w}, mean ${np.mean(wk.net_usd):,.2f}/wk, sd ${sd_w:,.2f})':<64}"
      f"{'PASS' if tstat >= 2.0 else 'FAIL'}")
    A(f"{'O2':<6}{'>=300 whole-session circular shifts; real above p95':<58}"
      f"{f'real ${o2_real:,.2f} vs null p95 ${p95:,.2f} (300 shifts, pct {o2_pct:.1f}%, p_ge {o2_pge:.4f})':<64}"
      f"{'PASS' if o2_pass else 'FAIL'}")
    A(f"{'O3':<6}{'ORB net > always-long 09:46->15:59 control net':<58}"
      f"{f'ORB ${net25:,.2f} vs control ${ctrl_net:,.2f} ({n_elig} ctrl RTs)':<64}"
      f"{'PASS' if o3_pass else 'FAIL'}")
    A("")
    A(f"null sensitivity: VERIFIED FIRST (spread ${sens['spread']:,.2f} over probe shifts [1,7,61]) — teeth confirmed")
    A(f"legs: long {n_long} trades ${long_net:,.2f} | short {n_short} trades ${short_net:,.2f}"
      + ("  [dead short leg recorded, not hidden]" if short_net <= 0 else ""))
    A(f"stress (non-gate): net at $33/RT = ${net33:,.2f}" + ("  -> REGIME-FRAGILE" if fragile else ""))
    A(f"both-side-break: modern {n_both}/{n_elig} eligible sessions ({n_both / max(n_elig, 1):.2%}); "
      f"deep {n_both_d}/{n_elig_d} ({n_both_d / max(n_elig_d, 1):.2%})")
    A(f"deep diagnostic 2006-2021 (non-gate): net ${net25_d:,.2f} over {len(trades_d)} trades — "
      + ("SIGN FLIP vs modern RECORDED" if sign_flip else "no sign flip vs modern"))
    A(f"top-decile traded-session concentration: top {k10} sessions net ${top_dec_net:,.2f}"
      + (f" = {top_dec_share:.1%} of total" if net25 > 0 else " (share not meaningful; total net <= 0)"))
    A("")
    A("per-year (modern gate window):")
    A(per_year.to_string(index=False))
    A("")
    A("leave-one-year-out (modern):")
    A(loyo.to_string(index=False))
    A("")
    A("per-year (deep 2006-2021 diagnostic, $25.01/RT):")
    A(per_year_d.to_string(index=False))
    A("")
    A(f"MDE (printed before verdict): weekly mean net required for t=2.0 at observed sd/Nw = "
      f"${mde_w:,.2f}/wk  (~${mde_w * 52:,.0f}/yr; ~${mde_w * n_w / max(n_elig, 1):,.2f}/eligible session). "
      f"Observed weekly mean ${np.mean(wk.net_usd):,.2f}/wk.")
    A(f"VERDICT: {verdict_line}")
    table = "\n".join(L)
    print(table)
    with open(os.path.join(OUT, "gate_table.txt"), "wb") as f:
        f.write(table.encode("utf-8"))

    # ---------------- outputs ----------------
    trades.drop(columns=["year"]).to_csv(os.path.join(OUT, "trades.csv"), index=False)
    trades_d.drop(columns=["year"]).to_csv(os.path.join(OUT, "trades_deep_diagnostic.csv"), index=False)
    wk.rename(columns={"week": "iso_week"}).to_csv(os.path.join(OUT, "weekly_series.csv"), index=False)

    ledger = {
        "trial_id": "G00016",
        "metrics": {
            "window": "2022-01-01..2026-07-31 sessions (modern gate)",
            "n_sessions_rth": n_sess, "n_eligible": n_elig, "n_trades": len(trades),
            "n_long": n_long, "n_short": n_short, "n_bothside_no_trade": n_both,
            "gross_pts": round(gross_pts, 2),
            "net_usd_25_01": round(net25, 2), "net_usd_33_stress": round(net33, 2),
            "long_net_usd": round(long_net, 2), "short_net_usd": round(short_net, 2),
            "t_weekly_clustered": round(tstat, 4), "n_weeks": n_w,
            "weekly_mean_usd": round(float(np.mean(wk.net_usd)), 2),
            "weekly_sd_usd": round(sd_w, 2), "mde_weekly_usd_t2": round(mde_w, 2),
            "o2_real_stat_usd": round(o2_real, 2), "o2_null_p95_usd": round(p95, 2),
            "o2_percentile": round(float(null["percentile"]), 4),
            "o2_p_ge": round(float(null["p_ge"]), 4), "o2_n_shifts": 300,
            "o3_control_net_usd": round(ctrl_net, 2),
            "deep_2006_2021_net_usd_25_01": round(net25_d, 2),
            "deep_n_trades": len(trades_d), "deep_sign_flip_vs_modern": bool(sign_flip),
            "gates": {"O1": bool(o1_pass), "O2": bool(o2_pass), "O3": bool(o3_pass)},
            "regime_fragile_at_33": bool(fragile),
            "evidence_status": "DISCOVERY_CONSUMED",
        },
        "result": verdict,
        "note": ("15-min ORB continuation, policy-minimal primary per frozen spec; card MC-01. "
                 "Verdict line: " + verdict_line + ". Resolutions in out/spec_resolutions.txt; "
                 "trades.csv is the frozen action set for COND01."),
    }
    with open(os.path.join(OUT, "ledger_result_pending.json"), "wb") as f:
        f.write(json.dumps(ledger, indent=2).encode("utf-8"))
    print("\noutputs written: gate_table.txt, trades.csv, trades_deep_diagnostic.csv, "
          "weekly_series.csv, ledger_result_pending.json")


if __name__ == "__main__":
    main()
