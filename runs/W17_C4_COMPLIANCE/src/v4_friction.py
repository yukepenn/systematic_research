"""V4 + V4a -- FRICTION SHARE LEDGER AND COMMISSION SENSITIVITY BAND.

Run: python runs/W17_C4_COMPLIANCE/src/v4_friction.py [optional_json_dump_path]

Covers three objects, all on the frozen dev window 2022-01-03 .. 2026-05-29:
  A   Product A  SolarWaveSMMaster_v2   (MNQ execution, multi-contract, real per-fill
      commission column)                 <- runs/SMV2M_MASTER_BUILD/out/nt8/smm_v2_fills.csv
  BN  Product B  BEST_ONE_NQ            <- runs/PRODUCTB_ONECONTRACT_FINAL/out/nt_trades_nq.csv
  BM  Product B  BEST_ONE_MNQ           <- runs/PRODUCTB_ONECONTRACT_FINAL/out/nt_trades_mnq.csv
      (BEST_ONE_MNQ carries the KNOWN_ERRORS #7 no-voluntary-exit defect: its numbers are
       PROVISIONAL.  Labelled everywhere in the output.)

DEFINITIONS (stated once, used everywhere):
  slip_$        measured adverse fill displacement vs the fill bar's reference price
                (bar OPEN for a next-bar fill, bar CLOSE for a session-close backstop fill),
                signed so that positive = cost to the strategy.  MEASURED, not assumed.
  G_raw         gross P&L at the unslipped reference prices  (= G + slip_$)
  G             gross P&L after slippage, before commission  (= net + commission)
  comm          commission actually charged in the backtest
  net           P&L after slippage and commission (NT8 ProfitCurrency / fill-ledger cash)

  FS_comm  = comm / G                         <- the narrow, commission-only friction share
  FS_house = (comm + slip_$) / G_raw          <- the HOUSE definition already used by
              runs/SMV2U_CLOCK_CHALLENGE/step1_clock_arms.py and
              runs/SMV2AE_1MIN_RESCALE/step2_rescaled_ensemble.py, i.e. the definition behind
              the 1.020 (1m unscaled) / 0.470 (1m rescaled) / 0.326 (3m ensemble arm) numbers.
              Reported so this run is comparable to those, using MEASURED slip; an ANALYTIC
              variant (1 tick x point value per contract-side, the house's own assumption) is
              printed alongside.
  Both ratios are only meaningful when the denominator is positive; any subset with
  denominator <= 0 prints "n/a (gross<=0)" instead of a ratio.

DAILY AGGREGATION: NT8 SESSION DATE (18:00 ET roll), taken from each object's own 3-minute bar
grid (session date = calendar date of the session's LAST bar), NOT calendar date of the
timestamp.  Sharpe = mean/std(ddof=1)*sqrt(252) on the session-keyed daily NET series,
zero-filled across every session of the relevant calendar (house convention, sm_metrics.py).
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np
import pandas as pd

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
os.chdir(REPO)

TICK = 0.25
ANN = 252
DEV_START = pd.Timestamp("2022-01-03").date()
DEV_END = pd.Timestamp("2026-05-29").date()

NQ_BARS = "runs/AUDIT03_BARS/nq_3m_2022_2026.csv"
MNQ_BARS = "runs/PRODUCTB_ONECONTRACT_FINAL/out/mnq_3m_raw.csv"
A_FILLS = "runs/SMV2M_MASTER_BUILD/out/nt8/smm_v2_fills.csv"
A_BARS = "runs/SMV2M_MASTER_BUILD/out/nt8/smm_v2_bars.csv"
BN_TR = "runs/PRODUCTB_ONECONTRACT_FINAL/out/nt_trades_nq.csv"
BM_TR = "runs/PRODUCTB_ONECONTRACT_FINAL/out/nt_trades_mnq.csv"

# coded round-turn commission (CONFIRMED as what was CODED, not confirmed as the live rate)
RT_NQ, RT_MNQ = 4.36, 1.30
SIDE_NQ, SIDE_MNQ = 2.18, 0.65
PV_NQ, PV_MNQ = 20.0, 2.0

MULTS = [0.5, 0.75, 1.0, 1.5, 2.0, 3.0]

OUT = {}


def log(*a):
    print(*a, flush=True)


# --------------------------------------------------------------------------- bar grids
def load_grid(path, fbos_col):
    df = pd.read_csv(path, comment="#")
    df["time"] = pd.to_datetime(df["time"])
    df["sess_id"] = df[fbos_col].astype(int).cumsum()
    last_t = df.groupby("sess_id")["time"].transform("max")
    df["sess_date"] = last_t.dt.date
    df["is_last"] = df["time"].eq(last_t)
    return df.set_index("time")


def grid_from_smm_bars(path):
    df = pd.read_csv(path, comment="#")
    df["time"] = pd.to_datetime(df["time"])
    # sess_end is an END flag: the session id increments AFTER a flagged bar
    df["sess_id"] = df["sess_end"].astype(int).shift(1, fill_value=0).cumsum()
    last_t = df.groupby("sess_id")["time"].transform("max")
    df["sess_date"] = last_t.dt.date
    df["is_last"] = df["sess_end"].astype(bool)
    return df.set_index("time")


def sess_fallback(ts):
    """18:00 ET roll fallback for any timestamp not on the bar grid."""
    ts = pd.Timestamp(ts)
    return (ts + pd.Timedelta(days=1)).date() if ts.hour >= 18 else ts.date()


def map_sess(times, grid, tag):
    s = pd.Series(pd.to_datetime(times)).map(grid["sess_date"])
    n_un = int(s.isna().sum())
    if n_un:
        fb = pd.Series(pd.to_datetime(times))[s.isna()].map(sess_fallback)
        s.loc[s.isna()] = fb
        log(f"  [{tag}] {n_un} timestamps not on the bar grid -> 18:00-roll fallback")
    return s.to_numpy(), n_un


# --------------------------------------------------------------------------- metrics
def sharpe(daily_vals):
    x = np.asarray(daily_vals, dtype=float)
    if x.size < 2:
        return float("nan")
    sd = x.std(ddof=1)
    return float("nan") if sd == 0 else float(x.mean() / sd * np.sqrt(ANN))


def ratio(num, den):
    return float(num / den) if den > 0 else None


def fmt_ratio(r):
    return "n/a (gross<=0)" if r is None else f"{r:.4f}"


# --------------------------------------------------------------------------- Product B
def build_product_b(name, path, grid, pv, rt, provisional):
    tr = pd.read_csv(path, parse_dates=["entry_time", "exit_time"])
    tr["gross"] = (tr["exit_px"] - tr["entry_px"]) * tr["dir"] * pv
    tr["comm"] = rt
    tr["net"] = tr["pnl"]

    # --- exactness of the trade-list arithmetic (DIRECT evidence for item 4)
    resid = (tr["gross"] - tr["comm"] - tr["net"]).abs()
    off_grid = int((((pd.concat([tr["entry_px"], tr["exit_px"]]) / TICK) % 1) != 0).sum())

    # --- MEASURED slippage vs the object's own bar grid
    e_open = tr["entry_time"].map(grid["open"])
    e_high = tr["entry_time"].map(grid["high"])
    e_low = tr["entry_time"].map(grid["low"])
    x_open = tr["exit_time"].map(grid["open"])
    x_close = tr["exit_time"].map(grid["close"])
    x_islast = tr["exit_time"].map(grid["is_last"]).astype(float).fillna(0.0).astype(bool)
    n_miss = int(e_open.isna().sum() + x_open.isna().sum())
    # trade lists carry no fill label, so the session-close backstop is identified as "the exit
    # bar is the session's last bar" (Product B exits voluntarily at 16:42, never on the last
    # bar, so this is unambiguous here -- the resulting slip histogram confirms it).
    x_base = np.where(x_islast.to_numpy(), x_close, x_open)
    # entry side = dir (buy for long), exit side = -dir
    tr["slip_entry_ticks"] = (tr["entry_px"] - e_open) * tr["dir"] / TICK
    tr["slip_exit_ticks"] = (x_base - tr["exit_px"]) * tr["dir"] / TICK
    tr["slip_ticks"] = tr["slip_entry_ticks"] + tr["slip_exit_ticks"]
    tr["slip_$"] = tr["slip_ticks"] * TICK * pv
    tr["gross_raw"] = tr["gross"] + tr["slip_$"]

    # --- session mapping
    tr["sess_entry"], _ = map_sess(tr["entry_time"], grid, name + " entry")
    tr["sess"], n_un = map_sess(tr["exit_time"], grid, name + " exit")
    n_cross = int((tr["sess_entry"] != tr["sess"]).sum())

    tr["in_dev"] = (tr["sess"] >= DEV_START) & (tr["sess"] <= DEV_END)

    diag = {
        "object": name, "provisional": provisional, "point_value": pv,
        "coded_rt_commission": rt, "n_trades_file": int(len(tr)),
        "max_abs_pnl_reconstruction_residual": float(resid.max()),
        "prices_off_0.25_tick_grid": off_grid,
        "n_fill_timestamps_off_bar_grid": n_miss,
        "n_exits_on_session_last_bar": int(x_islast.sum()),
        "n_zero_slip_entries": int((tr["slip_entry_ticks"] == 0).sum()),
        "n_zero_slip_entries_explained_by_bar_range_cap": int((
            (tr["slip_entry_ticks"] == 0) &
            (((tr["dir"] == 1) & (e_open == e_high)) | ((tr["dir"] == -1) & (e_open == e_low)))).sum()),
        "n_trades_entry_session_ne_exit_session": n_cross,
        "n_trades_outside_dev": int((~tr["in_dev"]).sum()),
        "first_sess": str(tr["sess"].min()), "last_sess": str(tr["sess"].max()),
        "slip_entry_tick_histogram": {str(k): int(v) for k, v in
                                      tr["slip_entry_ticks"].round(4).value_counts().items()},
        "slip_exit_tick_histogram": {str(k): int(v) for k, v in
                                     tr["slip_exit_ticks"].round(4).value_counts().items()},
    }
    return tr, diag


# --------------------------------------------------------------------------- Product A
def build_product_a(grid, pv=PV_MNQ):
    f = pd.read_csv(A_FILLS, comment="#")
    f["time"] = pd.to_datetime(f["time"])
    f["side"] = np.where(f["order_action"].isin(["Buy", "BuyToCover"]), 1, -1)
    f["delta"] = f["side"] * f["qty"]
    f["cash"] = -f["delta"] * f["price"] * pv          # realized cash flow, $ (PV applied)
    f["comm"] = f["commission"].astype(float)

    # per-fill commission is exactly qty * side rate?
    implied = (f["comm"] / f["qty"]).round(6)
    diag_rate = {str(k): int(v) for k, v in implied.value_counts().items()}

    # MEASURED slippage vs the object's own bar grid
    # Reference price: NT8 fills a next-bar market order at that bar's OPEN, but fills the
    # ExitOnSessionClose backstop at the session-close bar's CLOSE.  The fill ledger labels the
    # latter explicitly ("Exit on session close"), so use the label, NOT "is this the last bar" --
    # on the 43 holiday early-close sessions the object can also ENTER on the session's final bar
    # (measured: 2022-02-21 13:00 and 2025-12-24 13:15), and those entries fill at the OPEN.
    b_open = f["time"].map(grid["open"])
    b_close = f["time"].map(grid["close"])
    b_high = f["time"].map(grid["high"])
    b_low = f["time"].map(grid["low"])
    f["is_soc"] = f["name"].astype(str).str.strip().eq("Exit on session close")
    n_miss = int(b_open.isna().sum())
    base = np.where(f["is_soc"].to_numpy(), b_close, b_open)
    f["slip_ticks_per_ct"] = (f["price"] - base) * f["side"] / TICK
    f["slip_$"] = (f["slip_ticks_per_ct"] * TICK * pv * f["qty"]).fillna(0.0)
    # zero-slip fills should be range-capped (buy at bar high / sell at bar low)
    z = f["slip_ticks_per_ct"].eq(0) & b_open.notna() & ~f["is_soc"]
    n_zero = int(z.sum())
    n_capped = int((z & (((f["side"] == 1) & (b_open == b_high)) |
                         ((f["side"] == -1) & (b_open == b_low)))).sum())

    f["sess"], n_un = map_sess(f["time"], grid, "A fills")
    f["in_dev"] = (f["sess"] >= DEV_START) & (f["sess"] <= DEV_END)

    # flatness check per session
    f = f.sort_values("time").reset_index(drop=True)
    endpos = f.groupby("sess")["delta"].sum()
    n_nonflat = int((endpos != 0).sum())

    # flat-to-flat cycles ("trades")
    pos = 0
    cyc_id = np.zeros(len(f), dtype=int)
    cur = 0
    for i, d in enumerate(f["delta"].to_numpy()):
        if pos == 0:
            cur += 1
        cyc_id[i] = cur
        pos += d
    f["cycle"] = cyc_id
    cyc = f.groupby("cycle").agg(
        sess=("sess", "first"), t0=("time", "first"), t1=("time", "last"),
        gross=("cash", "sum"), comm=("comm", "sum"), slip=("slip_$", "sum"),
        contracts=("qty", "sum")).reset_index()
    cyc["net"] = cyc["gross"] - cyc["comm"]
    cyc["gross_raw"] = cyc["gross"] + cyc["slip"]
    cyc["in_dev"] = (cyc["sess"] >= DEV_START) & (cyc["sess"] <= DEV_END)

    diag = {
        "object": "Product A SolarWaveSMMaster_v2", "provisional": False, "point_value": pv,
        "coded_rt_commission_per_contract": 2 * SIDE_MNQ,
        "n_fills": int(len(f)), "n_flat_to_flat_cycles": int(len(cyc)),
        "per_fill_commission_per_contract_histogram": diag_rate,
        "n_sessions_not_ending_flat": n_nonflat,
        "n_fill_timestamps_off_price_grid": n_miss,
        "n_fill_timestamps_off_price_grid_INSIDE_dev": int((b_open.isna() & f["in_dev"]).sum()),
        "n_exit_on_session_close_fills": int(f["is_soc"].sum()),
        "n_zero_slip_fills": n_zero, "n_zero_slip_explained_by_bar_range_cap": n_capped,
        "first_sess": str(f["sess"].min()), "last_sess": str(f["sess"].max()),
        "n_fills_outside_dev": int((~f["in_dev"]).sum()),
        "slip_tick_histogram_per_contract": {str(k): int(v) for k, v in
                                             f["slip_ticks_per_ct"].round(4).value_counts().items()},
    }
    return f, cyc, diag


# --------------------------------------------------------------------------- ledger
def daily_frame(sess, gross, comm, slip, calendar):
    d = pd.DataFrame({"sess": sess, "gross": gross, "comm": comm, "slip": slip})
    g = d.groupby("sess")[["gross", "comm", "slip"]].sum()
    g = g.reindex(calendar, fill_value=0.0)
    g["net"] = g["gross"] - g["comm"]
    g["gross_raw"] = g["gross"] + g["slip"]
    return g


def subset_row(label, dly, n_rt, trades_net, trades_gross, contract_sides=None, pv=None):
    G = float(dly["gross"].sum())
    C = float(dly["comm"].sum())
    S = float(dly["slip"].sum())
    N = float(dly["net"].sum())
    Graw = G + S
    tn = np.asarray(trades_net, dtype=float)
    tg = np.asarray(trades_gross, dtype=float)
    wins = tn[tn > 0]
    loss = tn[tn < 0]
    gross_profit = float(tg[tg > 0].sum())
    row = {
        "label": label, "n_sessions": int(len(dly)), "n_round_turns": int(n_rt),
        "gross_raw_$": Graw, "slip_$": S, "gross_$": G, "commission_$": C, "net_$": N,
        "FS_comm": ratio(C, G), "FS_house_measured": ratio(C + S, Graw),
        "gross_profit_$": gross_profit, "comm_over_gross_profit": ratio(C, gross_profit),
        # commission multiple at which THIS subset's net reaches $0 (gross held fixed)
        "breakeven_comm_mult": (G / C) if C > 0 else None,
        "daily_vol_$": float(dly["net"].std(ddof=1)) if len(dly) > 1 else float("nan"),
        "net_over_gross": ratio(N, G),
        "avg_gross_per_rt_$": float(tg.mean()) if len(tg) else float("nan"),
        "avg_comm_per_rt_$": (C / n_rt) if n_rt else float("nan"),
        "avg_net_per_rt_$": float(tn.mean()) if len(tn) else float("nan"),
        "win_rate_net": float((tn > 0).mean()) if len(tn) else float("nan"),
        "win_rate_gross": float((tg > 0).mean()) if len(tg) else float("nan"),
        "payoff_net": float(wins.mean() / abs(loss.mean())) if len(wins) and len(loss) else float("nan"),
        "profit_factor_net": float(wins.sum() / abs(loss.sum())) if len(loss) and loss.sum() != 0 else float("nan"),
        "avg_win_$": float(wins.mean()) if len(wins) else float("nan"),
        "avg_loss_$": float(loss.mean()) if len(loss) else float("nan"),
        "sharpe_daily": sharpe(dly["net"].to_numpy()),
    }
    # per-contract-round-turn ledger denominated in TICKS (1 contract in, 1 contract out)
    if contract_sides and pv:
        crt = contract_sides / 2.0
        tv = TICK * pv
        row.update({
            "contract_round_turns": crt,
            "gross_raw_ticks_per_crt": Graw / crt / tv,
            "slip_ticks_per_crt": S / crt / tv,
            "comm_ticks_per_crt": C / crt / tv,
            "net_ticks_per_crt": N / crt / tv,
        })
    return row


def sensitivity(dly, mults=MULTS):
    G = float(dly["gross"].sum())
    C = float(dly["comm"].sum())
    g = dly["gross"].to_numpy()
    c = dly["comm"].to_numpy()
    rows = []
    for k in mults:
        n = g - k * c
        rows.append({"mult": k, "net_$": float(n.sum()), "commission_$": float(k * C),
                     "sharpe_daily": sharpe(n), "FS_comm": ratio(k * C, G)})
    be_net = (G / C) if C > 0 else float("inf")

    def sh(k):
        return sharpe(g - k * c)

    k_sharpe05 = None
    if sh(0.0) is not None and not np.isnan(sh(0.0)):
        if sh(0.0) < 0.5:
            k_sharpe05 = 0.0
        else:
            lo, hi = 0.0, 1.0
            while hi < 4096 and sh(hi) >= 0.5:
                lo, hi = hi, hi * 2
            if sh(hi) >= 0.5:
                k_sharpe05 = float("inf")
            else:
                for _ in range(200):
                    mid = 0.5 * (lo + hi)
                    if sh(mid) >= 0.5:
                        lo = mid
                    else:
                        hi = mid
                k_sharpe05 = 0.5 * (lo + hi)
    return rows, be_net, k_sharpe05


# =========================================================================== MAIN
log("=" * 78)
log("V4 + V4a  FRICTION SHARE LEDGER AND COMMISSION SENSITIVITY BAND")
log(f"dev window (session dates): {DEV_START} .. {DEV_END}")
log("daily aggregation = NT8 SESSION DATE (18:00 ET roll), from each object's own 3m bar grid")
log("=" * 78)

grid_nq = load_grid(NQ_BARS, "first_bar_of_session")
grid_mnq = load_grid(MNQ_BARS, "fbos")
grid_a = grid_from_smm_bars(A_BARS)

# cross-check the two MNQ grids agree where they overlap
ov = grid_mnq.index.intersection(grid_a.index)
agree = int((grid_mnq.loc[ov, "sess_date"].to_numpy() == grid_a.loc[ov, "sess_date"].to_numpy()).sum())
log(f"\nsession-map cross-check: MNQ raw grid vs Master-v2 bar grid overlap {len(ov)} bars, "
    f"session dates agree on {agree} ({agree/max(len(ov),1):.6%})")
OUT["session_map_crosscheck"] = {"overlap_bars": int(len(ov)), "agree": agree}

# --- dev calendars
CAL_NQ = sorted({d for d in grid_nq["sess_date"].unique() if DEV_START <= d <= DEV_END})
CAL_MNQ = sorted({d for d in grid_mnq["sess_date"].unique() if DEV_START <= d <= DEV_END})
CAL_A = sorted({d for d in grid_a["sess_date"].unique() if DEV_START <= d <= DEV_END})
log(f"dev session counts: NQ grid {len(CAL_NQ)} | MNQ grid {len(CAL_MNQ)} | Master-v2 grid {len(CAL_A)}")
OUT["dev_session_counts"] = {"NQ": len(CAL_NQ), "MNQ": len(CAL_MNQ), "A": len(CAL_A)}

log("\n--- loading objects ---")
bn, dbn = build_product_b("BEST_ONE_NQ", BN_TR, grid_nq, PV_NQ, RT_NQ, False)
bm, dbm = build_product_b("BEST_ONE_MNQ", BM_TR, grid_mnq, PV_MNQ, RT_MNQ, True)
# Product A executes MNQ, so its price/session reference is the MNQ 3-minute raw grid, which
# covers the whole dev window exactly (2022-01-02 18:03 .. 2026-05-29 16:57).  The object's own
# decision-bar grid (smm_v2_bars.csv) is used only as a cross-check: it agrees on the session
# date for 100% of overlapping bars but is missing a handful of bars (e.g. 2023-04-05 17:00),
# so it is NOT used as the mapping authority.
fa, cyc, dfa = build_product_a(grid_mnq)
OUT["diagnostics"] = {"BEST_ONE_NQ": dbn, "BEST_ONE_MNQ": dbm, "ProductA": dfa}
for d in (dbn, dbm, dfa):
    log(json.dumps(d, indent=2, default=str))

# --- assemble a common (sess, gross, comm, slip, per-trade net/gross) view per object
OBJ = {}
for nm, tr, cal, prov in [("BEST_ONE_NQ", bn, CAL_NQ, False), ("BEST_ONE_MNQ", bm, CAL_MNQ, True)]:
    t = tr[tr["in_dev"]].copy()
    OBJ[nm] = {"sess": t["sess"].to_numpy(), "gross": t["gross"].to_numpy(),
               "comm": t["comm"].to_numpy(), "slip": t["slip_$"].to_numpy(),
               "tnet": t["net"].to_numpy(), "tgross": t["gross"].to_numpy(),
               "cal": cal, "prov": prov, "rt_rate": RT_NQ if nm == "BEST_ONE_NQ" else RT_MNQ,
               "pv": PV_NQ if nm == "BEST_ONE_NQ" else PV_MNQ}
c = cyc[cyc["in_dev"]].copy()
OBJ["ProductA"] = {"sess": c["sess"].to_numpy(), "gross": c["gross"].to_numpy(),
                   "comm": c["comm"].to_numpy(), "slip": c["slip"].to_numpy(),
                   "tnet": c["net"].to_numpy(), "tgross": c["gross"].to_numpy(),
                   "cal": CAL_A, "prov": False, "rt_rate": RT_MNQ, "pv": PV_MNQ,
                   "contracts": c["contracts"].to_numpy()}

# also carry Product A's contract-level round-turn count
A_CONTRACT_RT = float(fa.loc[fa["in_dev"], "qty"].sum()) / 2.0
OUT["productA_contract_round_turns_dev"] = A_CONTRACT_RT

# --------------------------------------------------------------------- ledgers
LED = {}
for nm, o in OBJ.items():
    dly = daily_frame(o["sess"], o["gross"], o["comm"], o["slip"], o["cal"])
    o["daily"] = dly
    # contract-sides per trade/cycle (Product B = 1 in + 1 out; Product A = the cycle's own qty)
    cs = o.get("contracts")
    cs = (2.0 * np.ones(len(o["tnet"]))) if cs is None else np.asarray(cs, dtype=float)
    pv = o["pv"]

    def row(lab, sub_dly, mask):
        return subset_row(lab, sub_dly, int(mask.sum()), o["tnet"][mask], o["tgross"][mask],
                          float(cs[mask].sum()), pv)

    allm = np.ones(len(o["tnet"]), dtype=bool)
    rows = [row("FULL DEV 2022-01-03..2026-05-29", dly, allm)]

    # per year
    yrs = pd.Series([d.year for d in dly.index], index=dly.index)
    tyr = np.array([s.year for s in o["sess"]])
    for y in sorted(yrs.unique()):
        rows.append(row(f"YEAR {y}", dly[yrs == y], tyr == y))

    # recency tiers -- DISCLOSURE ONLY, never selection
    for lab, start in [("TRAILING 2Y (disclosure only)", pd.Timestamp("2024-05-30").date()),
                       ("TRAILING 1Y (disclosure only)", pd.Timestamp("2025-05-30").date())]:
        rows.append(row(lab, dly[[d >= start for d in dly.index]], o["sess"] >= start))

    LED[nm] = pd.DataFrame(rows)

# analytic (house-assumption) slippage for comparison
for nm, o in OBJ.items():
    if nm == "ProductA":
        ct = float(fa.loc[fa["in_dev"], "qty"].sum())
    else:
        ct = 2.0 * len(o["tnet"])
    o["analytic_slip"] = ct * TICK * o["pv"]
    o["contract_sides"] = ct

log("\n" + "=" * 78)
log("LEDGERS")
log("=" * 78)
COLS = ["label", "n_sessions", "n_round_turns", "gross_raw_$", "slip_$", "gross_$",
        "commission_$", "net_$", "FS_comm", "FS_house_measured", "comm_over_gross_profit",
        "avg_gross_per_rt_$", "avg_comm_per_rt_$", "win_rate_net", "payoff_net",
        "profit_factor_net", "daily_vol_$", "sharpe_daily"]
TCOLS = ["label", "contract_round_turns", "gross_raw_ticks_per_crt", "slip_ticks_per_crt",
         "comm_ticks_per_crt", "net_ticks_per_crt", "breakeven_comm_mult"]
for nm in ["ProductA", "BEST_ONE_NQ", "BEST_ONE_MNQ"]:
    log(f"\n### {nm}{'   [PROVISIONAL - KNOWN_ERRORS #7]' if OBJ[nm]['prov'] else ''}")
    df = LED[nm][COLS].copy()
    log(df.to_string(index=False, float_format=lambda v: f"{v:,.4f}"))
    log("  -- per CONTRACT round turn, in TICKS (1 tick = $%.2f) --" % (TICK * OBJ[nm]["pv"]))
    log(LED[nm][TCOLS].to_string(index=False, float_format=lambda v: f"{v:,.3f}"))
    o = OBJ[nm]
    S_meas = float(o["daily"]["slip"].sum())
    log(f"  measured slip ${S_meas:,.2f} vs analytic (1 tick x PV x {o['contract_sides']:.0f} "
        f"contract-sides) ${o['analytic_slip']:,.2f}  "
        f"-> measured/analytic = {S_meas/o['analytic_slip']:.4f}")
    Graw = float(o["daily"]["gross_raw"].sum())
    log(f"  FS_house with ANALYTIC slip = "
        f"{fmt_ratio(ratio(float(o['daily']['comm'].sum()) + o['analytic_slip'], float(o['daily']['gross'].sum()) + o['analytic_slip']))}")
    log(f"  slip_$ per round turn = ${S_meas/max(len(o['tnet']),1):,.2f}; "
        f"slip share of gross_raw = {fmt_ratio(ratio(S_meas, Graw))}")

log("\n--- comparability to the house 1-minute friction-share numbers "
    "(runs/SMV2AE_1MIN_RESCALE/out/friction_share.csv) ---")
house = pd.read_csv("runs/SMV2AE_1MIN_RESCALE/out/friction_share.csv")
log(house.to_string(index=False))
log("  those use FRICTION_PER_CONTRACT_SIDE = 1 tick x MNQ point value + $0.65 = $1.15/side")
rows = []
for nm in ["ProductA", "BEST_ONE_NQ", "BEST_ONE_MNQ"]:
    o = OBJ[nm]
    C = float(o["daily"]["comm"].sum())
    G = float(o["daily"]["gross"].sum())
    rows.append({"arm": nm + " (this run, 3m)", "net": float(o["daily"]["net"].sum()),
                 "total_contracts_traded": o["contract_sides"],
                 "total_friction_$": C + o["analytic_slip"], "gross_$": G + o["analytic_slip"],
                 "friction_share": (C + o["analytic_slip"]) / (G + o["analytic_slip"])})
cmp_df = pd.DataFrame(rows)
log(cmp_df.to_string(index=False, float_format=lambda v: f"{v:,.4f}"))
OUT["house_comparison"] = {"house_rows": house.to_dict(orient="records"),
                           "this_run_rows": cmp_df.to_dict(orient="records")}

OUT["ledgers"] = {nm: LED[nm].to_dict(orient="records") for nm in LED}
OUT["slippage"] = {nm: {"measured_$": float(OBJ[nm]["daily"]["slip"].sum()),
                        "analytic_$": OBJ[nm]["analytic_slip"],
                        "contract_sides": OBJ[nm]["contract_sides"],
                        "measured_per_round_turn_$": float(OBJ[nm]["daily"]["slip"].sum()) / max(len(OBJ[nm]["tnet"]), 1)}
                   for nm in OBJ}

# --------------------------------------------------------------------- V4a band
log("\n" + "=" * 78)
log("V4a  COMMISSION SENSITIVITY BAND (multiples of the CODED round-turn rate)")
log("=" * 78)
BAND = {}
for nm in ["ProductA", "BEST_ONE_NQ", "BEST_ONE_MNQ"]:
    o = OBJ[nm]
    rows, be, k05 = sensitivity(o["daily"])
    BAND[nm] = {"rows": rows, "breakeven_mult_net_zero": be, "mult_sharpe_below_0.5": k05,
                "coded_rt_$": o["rt_rate"]}
    log(f"\n### {nm}   coded RT = ${o['rt_rate']:.2f}"
        f"{'   [PROVISIONAL]' if o['prov'] else ''}")
    d = pd.DataFrame(rows)
    d["rt_$"] = d["mult"] * o["rt_rate"]
    log(d[["mult", "rt_$", "commission_$", "net_$", "sharpe_daily", "FS_comm"]].to_string(
        index=False, float_format=lambda v: f"{v:,.4f}"))
    log(f"  breakeven multiple (net = $0): {be:,.3f}x  -> RT = ${be*o['rt_rate']:,.2f}")
    if k05 is None:
        k05_txt = "undefined"
    elif k05 == float("inf"):
        k05_txt = "never in [0, 4096]x"
    elif k05 == 0.0:
        k05_txt = "already below 0.50 at zero commission"
    else:
        k05_txt = f"{k05:,.3f}x -> RT = ${k05*o['rt_rate']:,.2f}"
    log(f"  multiple at which daily Sharpe drops below 0.50: {k05_txt}")

    # quarterly-revision sensitivity: +/-25% on the RT rate
    base = [r for r in rows if r["mult"] == 1.0][0]
    lo = sharpe(o["daily"]["gross"].to_numpy() - 0.75 * o["daily"]["comm"].to_numpy())
    hi = sharpe(o["daily"]["gross"].to_numpy() - 1.25 * o["daily"]["comm"].to_numpy())
    nlo = float((o["daily"]["gross"] - 0.75 * o["daily"]["comm"]).sum())
    nhi = float((o["daily"]["gross"] - 1.25 * o["daily"]["comm"]).sum())
    log(f"  +/-25% rate revision (one plausible quarterly step): "
        f"net ${nhi:,.0f} .. ${nlo:,.0f} (base ${base['net_$']:,.0f}, "
        f"span {100*(nlo-nhi)/abs(base['net_$']):.2f}% of base); "
        f"Sharpe {hi:.4f} .. {lo:.4f} (base {base['sharpe_daily']:.4f})")
    BAND[nm]["pm25pct"] = {"net_lo_$": nhi, "net_hi_$": nlo, "sharpe_lo": hi, "sharpe_hi": lo,
                           "net_span_pct_of_base": 100 * (nlo - nhi) / abs(base["net_$"])}
OUT["band"] = BAND

# --------------------------------------------------------------------- cross-checks
log("\n" + "=" * 78)
log("CROSS-CHECKS")
log("=" * 78)
chk = {}
a_net = float(OBJ["ProductA"]["daily"]["net"].sum())
chk["ProductA_net_dev"] = a_net
chk["ProductA_net_vs_nt8_dev_battery_177315.10"] = a_net - 177315.09999995603
log(f"Product A dev net from fill ledger: ${a_net:,.2f}   "
    f"delta vs nt8_dev_battery NT8_EXECUTABLE_dev (177,315.10): "
    f"${a_net-177315.09999995603:,.2f}")
for nm, ref in [("BEST_ONE_NQ", 303448.9999999999), ("BEST_ONE_MNQ", 28900.700000000015)]:
    v = float(OBJ[nm]["daily"]["net"].sum())
    full = float(pd.read_csv(BN_TR if nm == "BEST_ONE_NQ" else BM_TR)["pnl"].sum())
    chk[nm + "_net_dev"] = v
    chk[nm + "_net_full_file"] = full
    log(f"{nm} dev net ${v:,.2f} | whole-file net ${full:,.2f} (parity json reports ${ref:,.2f})")
OUT["crosschecks"] = chk

if len(sys.argv) > 1:
    with open(sys.argv[1], "w", encoding="utf-8") as fh:
        json.dump(OUT, fh, indent=2, default=str)
    log(f"\nJSON dumped to {sys.argv[1]}")
log("\nDONE")
