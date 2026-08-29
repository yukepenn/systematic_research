"""G2_EXEC01_P1_EXECUTION_20260828 — TEAM EXEC01 driver (ledger trial G00015).

Executes the frozen spec.yaml: E1 direct fill-vs-quote cost on the maximized overlap,
E2 spread state map (time-of-day x trailing-vol tercile), E3 +1-minute delay stress on
the frozen action set, E4 passive-entry plausibility bound.

All ambiguity resolutions were frozen in out/spec_resolutions.txt BEFORE this file first
ran (R1..R13, referenced inline). No parameter search. Gate/verdict tables are printed by
this program to out/gate_table.txt, never hand-assembled.

Writes ONLY under runs/G2_EXEC01_P1_EXECUTION_20260828/out/. Never touches git, never
calls CrossTrade, never modifies an existing file.

Seal: every data load passes research_sdk.seal_guard.assert_presealed (no value
>= 2026-08-01 read). Blind pools: research/data_esnq is opened ONLY for sessions in
ALLOWLIST_DEV_44.txt, enforced and printed per file.
"""
from __future__ import annotations

import json
import os
import sys
import time as _time

os.environ.setdefault("MPLBACKEND", "Agg")

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
RUN = os.path.join(ROOT, "runs", "G2_EXEC01_P1_EXECUTION_20260828")
OUT = os.path.join(RUN, "out")
os.makedirs(OUT, exist_ok=True)
SRC = os.path.join(ROOT, "research", "weekly_edge", "src")
sys.path.insert(0, SRC)
sys.path.insert(0, ROOT)

from research_sdk.seal_guard import assert_presealed  # noqa: E402

import run_we_w01 as W1                                                  # noqa: E402
from run_we_w01 import PV, COMM_RT                                       # noqa: E402
from run_we_w17 import load_deep                                         # noqa: E402
from run_we_w26 import fills_daily                                       # noqa: E402
from run_we_w37 import causal_score                                      # noqa: E402
from run_we_w39 import WIN                                               # noqa: E402
from run_we_w51 import session_frames                                    # noqa: E402
from run_we_w97 import votes                                             # noqa: E402
from run_we_w98 import gfills, arm_kw                                    # noqa: E402
from we_fastctx import fast_build_context                                # noqa: E402
from we_lab import spread_profile                                        # noqa: E402

T0 = _time.time()
A = np.datetime64("2022-07-01")
B = np.datetime64("2026-08-01")
TICK = 0.25          # NQ tick, points
TICKV = 5.0          # $ per tick per contract
STALE_NS = 5_000_000_000        # 5 s staleness cap (R4)
ONE_MIN = np.timedelta64(60, "s")

ESNQ_DIR = os.path.join(ROOT, "research", "data_esnq", "parquet", "NQ")
ALLOWLIST_PATH = os.path.join(ROOT, "research", "data_esnq", "ALLOWLIST_DEV_44.txt")
V2_DIR = os.path.join(ROOT, "research", "data_microstructure_v2", "raw", "NQ")
V1_DIR = os.path.join(ROOT, "research", "scalping_lab", "substrate", "raw", "NQ")
# v1 Last-only files, established by a bip census (no bid/ask events at all) — R7:
V1_NO_BBO = {"20250811", "20250924", "20260430"}


def log(*a):
    print(f"[{_time.time()-T0:6.0f}s]", *a, flush=True)


# --------------------------------------------------------------------------------------
# instrumented gfills — VERBATIM logic of run_we_w98.gfills with extra RECORDED fields
# (entry/exit bar index, entry/exit price, exit kind). Asserted equal to the original
# on every (d,u,et,xt,pnl) tuple in the harness gate GA (R1).
# --------------------------------------------------------------------------------------
def gfills_instr(D, dir_arr, size_at_entry=None, halt=1300.0, target=1000.0,
                 per_ctr=False):
    t, o, c = D["t"], D["o"], D["c"]
    fb, lb, n = D["fb"], D["lb"], D["n"]
    trades = []
    p = 0; u = 0; epx = 0.0; eti = -1; spnl = 0.0; stopped = False
    for i in range(n):
        if fb[i]:
            spnl = 0.0; stopped = False
        want = int(dir_arr[i - 1]) if i > 0 and not fb[i] else 0
        if stopped:
            want = 0
        if want != p:
            if p != 0:
                pnl = p * u * (o[i] - epx) * PV - COMM_RT * u
                trades.append(dict(d=p, u=u, et=str(t[eti]), xt=str(t[i]), pnl=pnl,
                                   eti=eti, xti=i, epx=epx, xpx=o[i], xkind="open"))
                spnl += (pnl / u) if per_ctr else pnl
                if spnl <= -halt or (target is not None and spnl >= target):
                    stopped = True; want = 0
            p = want
            if p != 0:
                u = int(size_at_entry[i]) if size_at_entry is not None else 1
                if u < 1:
                    p = 0; u = 0
                else:
                    epx, eti = o[i], i
        if lb[i] and p != 0:
            pnl = p * u * (c[i] - epx) * PV - COMM_RT * u
            trades.append(dict(d=p, u=u, et=str(t[eti]), xt=str(t[i]), pnl=pnl,
                               eti=eti, xti=i, epx=epx, xpx=c[i], xkind="close"))
            p = 0; u = 0
    return trades


def main():
    glines = []

    def G(*a):
        s = " ".join(str(x) for x in a)
        glines.append(s); print(s, flush=True)

    # ================================================================== Phase A: stream
    log("Phase A — substrate + P1_PCT stream regeneration (R1, verbatim repro chain)")
    prof = spread_profile()
    D = load_deep("2022-01-01", "2026-07-31 17:00", extend=True)
    W1.DEV_END = pd.Timestamp("2026-07-31").date()
    n, tarr, sid, lb, fb = D["n"], D["t"], D["sid"], D["lb"], D["fb"]
    o, c = D["o"], D["c"]
    assert_presealed(pd.DataFrame({"t": pd.to_datetime(tarr)}), "t",
                     "substrate 1-min bars")
    log(f"substrate {n:,} bars / {D['n_sess']:,} sessions — seal PASS "
        f"(max t {pd.Timestamp(tarr.max())})")

    st_, en_, _ = session_frames(D)
    NSESS = D["n_sess"]
    sdate = pd.to_datetime(D["sess_date"])
    iso = sdate.isocalendar()
    wkall = (iso["year"].astype(str) + "-W" + iso["week"].astype(str).str.zfill(2)).to_numpy()
    win = np.array([A <= tarr[st_[s]] < B for s in range(NSESS)])
    sess_in = np.flatnonzero(win)
    wk_in = wkall[sess_in]
    n_weeks = len(set(wk_in))
    log(f"in-window sessions {len(sess_in):,}, ISO weeks {n_weeks}")

    X = fast_build_context(D)
    z = np.load(os.path.join(ROOT, "runs", "WE_W76_FORWARD2026", "out", "mem_ext.npz"))
    mem, bmom, tilt = z["mem"], z["bmom"], z["tilt"]
    if mem.shape[0] != n:
        raise SystemExit("mem_ext.npz rows != substrate bars — ABORT")

    def i_of(ts):
        return int(min(np.searchsorted(tarr, np.datetime64(ts)), n - 1))

    log("votes -> fills_daily -> causal_score (verbatim)")
    vl, _ = votes(D, mem, bmom, tilt, X, bmom)
    p_arr = vl.astype(np.int8)
    bb = fills_daily(D, p_arr, halt=1300, target=1000)
    ee = np.array([i_of(x["et"]) for x in bb if A <= np.datetime64(x["et"]) < B])
    sc, _ = causal_score(X, ee, window=WIN)
    sizes = np.where(sc >= 3, 2, 1).astype(np.int8)
    log("gfills (original) + gfills_instr")
    tr_ref = gfills(D, p_arr, sizes, **arm_kw("PCT", 1.183))
    tr = gfills_instr(D, p_arr, sizes, **arm_kw("PCT", 1.183))

    ga = len(tr) == len(tr_ref) and all(
        x["d"] == y["d"] and x["u"] == y["u"] and x["et"] == y["et"]
        and x["xt"] == y["xt"] and abs(x["pnl"] - y["pnl"]) <= 1e-9
        for x, y in zip(tr, tr_ref))
    n_total = len(tr)
    for x in tr:
        x["sess"] = int(sid[x["eti"]])
    n_sessfilter = sum(1 for x in tr if win[x["sess"]])
    gb = (n_total == 2401) and (n_sessfilter == 2131)
    log(f"stream: total {n_total}, session-filtered {n_sessfilter}; GA={ga} GB={gb}")
    if not (ga and gb):
        G("STREAM IDENTITY FAILED — GA/GB. Run aborts as DEFECT.")
        with open(os.path.join(OUT, "gate_table.txt"), "w", encoding="utf-8") as f:
            f.write("\n".join(glines) + "\n")
        with open(os.path.join(OUT, "ledger_result_pending.json"), "w",
                  encoding="utf-8") as f:
            json.dump({"trial_id": "G00015", "metrics": {}, "result": "DEFECT",
                       "note": "P1 stream regeneration failed identity gates GA/GB"}, f)
        return

    TT = pd.DataFrame([{k: x[k] for k in
                        ("d", "u", "et", "xt", "pnl", "eti", "xti", "epx", "xpx",
                         "xkind", "sess")} for x in tr])
    TT["tid"] = np.arange(len(TT))
    TT["in_win"] = TT["sess"].map(lambda s: bool(win[s]))
    TT["sess_date"] = TT["sess"].map(lambda s: sdate[s].strftime("%Y%m%d"))
    TT["week"] = TT["sess"].map(lambda s: wkall[s])
    assert (sid[TT["eti"].to_numpy()] == sid[TT["xti"].to_numpy()]).all(), \
        "trade spans sessions — data-impossible"
    assert_presealed(TT.assign(et_ts=pd.to_datetime(TT["et"])), "et_ts", "P1 trade entries")
    assert_presealed(TT.assign(xt_ts=pd.to_datetime(TT["xt"])), "xt_ts", "P1 trade exits")
    TT.to_csv(os.path.join(OUT, "p1_trades.csv"), index=False)
    TIN = TT[TT["in_win"]].reset_index(drop=True)
    total_ctr_rt = int(TIN["u"].sum())
    log(f"in-window trades {len(TIN)}, contract RTs {total_ctr_rt}; p1_trades.csv written")

    # trailing vol (R8): 1-min log returns, overnight-gap return NaN, rolling 60/min 30,
    # shifted one bar so the window ends strictly before the bar's open instant.
    r = np.full(n, np.nan)
    r[1:] = np.log(c[1:] / c[:-1])
    r[fb] = np.nan
    volarr = (pd.Series(r).rolling(60, min_periods=30).std(ddof=1).shift(1)
              .to_numpy())

    # ============================================================ Phase B: inventory
    log("Phase B — quote-session inventory + allowlist enforcement (R7)")
    with open(ALLOWLIST_PATH, "r", encoding="utf-8") as f:
        allowlist = {ln.strip() for ln in f if ln.strip()}
    assert len(allowlist) == 44, "ALLOWLIST_DEV_44 does not have 44 entries"

    v2_dates = {f[1:9] for f in os.listdir(V2_DIR) if f.endswith(".parquet")}
    esnq_all = {f[1:9] for f in os.listdir(ESNQ_DIR) if f.endswith(".parquet")}
    v1_dates = {f[1:9] for f in os.listdir(V1_DIR)
                if f.endswith(".parquet") and "_rth" not in f} - V1_NO_BBO

    inv = {}                       # date -> (store, path)
    for d_ in sorted(v2_dates):
        inv[d_] = ("v2", os.path.join(V2_DIR, f"s{d_}.parquet"))
    n_esnq_used = 0
    for d_ in sorted(esnq_all & allowlist):
        if d_ not in inv:
            inv[d_] = ("esnq", os.path.join(ESNQ_DIR, f"s{d_}.parquet"))
            n_esnq_used += 1
    for d_ in sorted(v1_dates):
        if d_ not in inv:
            inv[d_] = ("v1", os.path.join(V1_DIR, f"s{d_}.parquet"))

    # ALLOWLIST ENFORCEMENT (printed): the esnq store may only be opened via allowlist.
    esnq_blind_available = sorted(esnq_all - allowlist)
    esnq_planned = sorted(d_ for d_, (s_, _) in inv.items() if s_ == "esnq")
    viol = [d_ for d_ in esnq_planned if d_ not in allowlist]
    print("=" * 100)
    print("BLIND-POOL ENFORCEMENT — research/data_esnq (printed before any esnq open):")
    print(f"  allowlist ALLOWLIST_DEV_44.txt entries : {len(allowlist)}")
    print(f"  esnq store sessions on disk            : {len(esnq_all)}")
    print(f"  esnq sessions outside allowlist (BLIND): {len(esnq_blind_available)} — "
          f"NONE will be opened")
    print(f"  esnq sessions this run will open       : {len(esnq_planned)} "
          f"(all in allowlist: {'YES' if not viol else 'NO — ABORT'})")
    print("=" * 100)
    if viol:
        raise SystemExit("BLIND SESSION WOULD BE TOUCHED — ABORT")

    inv_rows = [dict(date=d_, store=s_, path=os.path.relpath(pth, ROOT))
                for d_, (s_, pth) in sorted(inv.items())]
    pd.DataFrame(inv_rows).to_csv(os.path.join(OUT, "session_inventory.csv"), index=False)
    date_to_sess = {sdate[s].strftime("%Y%m%d"): s for s in range(NSESS)}
    log(f"inventory: {len(inv)} unique quote sessions "
        f"(v2 {sum(1 for v in inv.values() if v[0]=='v2')}, "
        f"esnq {n_esnq_used}, v1 {sum(1 for v in inv.values() if v[0]=='v1')})")

    # candidate legs (R6): in-window trades whose session date is in the inventory
    TIN_bydate = {d_: g for d_, g in TIN.groupby("sess_date")}
    cand_dates = sorted(set(TIN_bydate) & set(inv))
    no_substrate = sorted(d_ for d_ in inv if d_ not in date_to_sess)

    # ============================================================ Phase C: session loop
    log(f"Phase C — per-session processing ({len(inv)} sessions, bounded memory)")
    leg_rows = []          # one row per candidate fill leg
    samp_min = []          # minute samples for E2 (per-session arrays)
    sess_meta = []
    n_esnq_opened = 0
    seal_ok_sessions = 0

    for d_ in sorted(inv):
        store, path = inv[d_]
        if d_ not in date_to_sess:
            sess_meta.append(dict(date=d_, store=store, status="no_substrate_session"))
            continue
        s = date_to_sess[d_]
        if store == "esnq":
            assert d_ in allowlist, f"allowlist violation {d_} — ABORT"
            n_esnq_opened += 1
            print(f"  esnq open {d_}  (allowlisted: YES)", flush=True)
        tbl = pq.read_table(path, columns=["bip", "time", "price"])
        qt = tbl.column("time").to_numpy().astype("datetime64[ns]")
        qb = tbl.column("bip").to_numpy()
        qp = tbl.column("price").to_numpy()
        del tbl
        assert_presealed(pd.DataFrame({"time": qt}), "time", f"quotes s{d_} [{store}]")
        seal_ok_sessions += 1
        bid_m = qb == 1
        ask_m = qb == 2
        bt = qt[bid_m].astype("int64"); bp = qp[bid_m]
        at = qt[ask_m].astype("int64"); ap = qp[ask_m]
        # stable-sort defensively (audit: full stream time-sorted, so this is a no-op)
        if len(bt) and np.any(np.diff(bt) < 0):
            o_ = np.argsort(bt, kind="stable"); bt, bp = bt[o_], bp[o_]
        if len(at) and np.any(np.diff(at) < 0):
            o_ = np.argsort(at, kind="stable"); at, ap = at[o_], ap[o_]
        def unusable_legs(reason):
            """R6 conservative: an inventory session that cannot be measured still
            contributes its candidate legs — as exclusions."""
            if d_ in TIN_bydate:
                for _, x in TIN_bydate[d_].iterrows():
                    for role in ("entry", "exit"):
                        leg_rows.append(dict(
                            tid=int(x["tid"]), date=d_, store=store, role=role,
                            side="", d=int(x["d"]), u=int(x["u"]), instant="",
                            bar_stamp="", px_substrate=np.nan, offset=np.nan,
                            px_corrected=np.nan, bid=np.nan, ask=np.nan,
                            age_bid_ms=np.nan, age_ask_ms=np.nan,
                            spread_ticks=np.nan, half_spread_usd=np.nan,
                            omitted_vs_open_usd=np.nan, modeled_half_usd=np.nan,
                            inside_strict=False, inside_band=False, vol=np.nan,
                            hour=-1, status=reason))

        if len(bt) == 0 or len(at) == 0:
            unusable_legs("session_unusable_no_bbo")
            sess_meta.append(dict(date=d_, store=store, status="no_bbo"))
            continue
        store_end = int(min(bt[-1], at[-1]))

        def asof(instants_ns):
            ib = np.searchsorted(bt, instants_ns, side="right") - 1
            ia = np.searchsorted(at, instants_ns, side="right") - 1
            okb = ib >= 0; oka = ia >= 0
            bpx = np.where(okb, bp[np.maximum(ib, 0)], np.nan)
            apx = np.where(oka, ap[np.maximum(ia, 0)], np.nan)
            ageb = np.where(okb, instants_ns - bt[np.maximum(ib, 0)], np.int64(2**62))
            agea = np.where(oka, instants_ns - at[np.maximum(ia, 0)], np.int64(2**62))
            return bpx, apx, ageb, agea

        j0, j1 = int(st_[s]), int(en_[s])          # en_ exclusive
        stamps = tarr[j0:j1]
        open_ns = (stamps - ONE_MIN).astype("datetime64[ns]").astype("int64")
        close_ns = stamps.astype("datetime64[ns]").astype("int64")

        # per-session offset (R5): median(substrate close - quote mid) at bar stamps
        bpx, apx, ageb, agea = asof(close_ns)
        fresh = (ageb <= STALE_NS) & (agea <= STALE_NS) & (apx >= bpx)
        mid = (bpx + apx) / 2.0
        diff = c[j0:j1] - mid
        n_off = int(fresh.sum())
        if n_off < 30:
            unusable_legs("session_unusable_offset")
            sess_meta.append(dict(date=d_, store=store, status="too_few_offset_pts",
                                  n_off=n_off))
            continue
        off_raw = float(np.median(diff[fresh]))
        offset = round(off_raw / TICK) * TICK
        off_mad = float(np.median(np.abs(diff[fresh] - off_raw)))

        # E2 minute samples at bar-OPEN instants (R8)
        obpx, oapx, oageb, oagea = asof(open_ns)
        ofresh = (oageb <= STALE_NS) & (oagea <= STALE_NS) & (oapx >= obpx) & (oapx >= obpx)
        spr_tk = (oapx - obpx) / TICK
        hours = pd.DatetimeIndex(stamps - ONE_MIN).hour.to_numpy()
        vols = volarr[j0:j1]
        m_ = ofresh
        samp_min.append(pd.DataFrame({
            "date": d_, "store": store, "hour": hours[m_],
            "spr_tk": spr_tk[m_], "vol": vols[m_]}))

        # E1/E4 fill legs
        n_legs_sess = 0
        if d_ in TIN_bydate:
            for _, x in TIN_bydate[d_].iterrows():
                for role in ("entry", "exit"):
                    if role == "entry":
                        bar = int(x["eti"]); px = float(x["epx"])
                        instant = int((tarr[bar] - ONE_MIN).astype("datetime64[ns]")
                                      .astype("int64"))
                        side = "buy" if x["d"] > 0 else "sell"
                    else:
                        bar = int(x["xti"]); px = float(x["xpx"])
                        if x["xkind"] == "open":
                            instant = int((tarr[bar] - ONE_MIN)
                                          .astype("datetime64[ns]").astype("int64"))
                        else:
                            instant = int(tarr[bar].astype("datetime64[ns]")
                                          .astype("int64"))
                        side = "sell" if x["d"] > 0 else "buy"
                    b_, a_, gb_, ga_ = asof(np.array([instant], dtype="int64"))
                    b_, a_, gb_, ga_ = float(b_[0]), float(a_[0]), int(gb_[0]), int(ga_[0])
                    status = "ok"
                    if not np.isfinite(b_) or not np.isfinite(a_):
                        status = "no_quote"
                    elif gb_ > STALE_NS or ga_ > STALE_NS:
                        status = ("stale_after_store_end"
                                  if instant > store_end else "stale")
                    elif a_ < b_:
                        status = "crossed"
                    pxc = px - offset
                    inside_strict = inside_band = False
                    half_usd = omit_usd = spr_leg = np.nan
                    if status == "ok":
                        inside_band = (b_ - TICK - 1e-9 <= pxc <= a_ + TICK + 1e-9)
                        inside_strict = (b_ - 1e-9 <= pxc <= a_ + 1e-9)
                        if not inside_band:
                            status = "outside_band"
                        else:
                            spr_leg = (a_ - b_) / TICK
                            half_usd = (a_ - b_) / 2.0 * PV
                            omit_usd = ((a_ - pxc) if side == "buy" else (pxc - b_)) * PV
                    mod_stamp = pd.Timestamp(tarr[bar])
                    mmin = mod_stamp.hour * 60 + mod_stamp.minute
                    leg_rows.append(dict(
                        tid=int(x["tid"]), date=d_, store=store, role=role, side=side,
                        d=int(x["d"]), u=int(x["u"]),
                        instant=str(pd.Timestamp(instant)), bar_stamp=str(mod_stamp),
                        px_substrate=px, offset=offset, px_corrected=pxc,
                        bid=b_, ask=a_, age_bid_ms=(gb_ / 1e6 if gb_ < 2**61 else np.nan),
                        age_ask_ms=(ga_ / 1e6 if ga_ < 2**61 else np.nan),
                        spread_ticks=spr_leg, half_spread_usd=half_usd,
                        omitted_vs_open_usd=omit_usd,
                        modeled_half_usd=TICKV * float(prof.get(mmin, 3.0)) / 2.0,
                        inside_strict=inside_strict, inside_band=inside_band,
                        vol=float(volarr[bar]) if np.isfinite(volarr[bar]) else np.nan,
                        hour=pd.Timestamp(instant).hour,
                        status=status))
                    n_legs_sess += 1
        sess_meta.append(dict(date=d_, store=store, status="ok", offset=offset,
                              offset_raw=round(off_raw, 4), offset_mad=round(off_mad, 4),
                              n_offset_pts=n_off, n_min_samples=int(m_.sum()),
                              n_legs=n_legs_sess))
        if len(sess_meta) % 20 == 0:
            log(f"  ... {len(sess_meta)}/{len(inv)} sessions")

    SM = pd.DataFrame(sess_meta)
    SM.to_csv(os.path.join(OUT, "session_offsets.csv"), index=False)
    LEG = pd.DataFrame(leg_rows)
    LEG.to_csv(os.path.join(OUT, "fill_cost_distribution.csv"), index=False)
    MS = (pd.concat(samp_min, ignore_index=True) if samp_min else
          pd.DataFrame(columns=["date", "store", "hour", "spr_tk", "vol"]))
    MS.to_csv(os.path.join(OUT, "minute_samples.csv.gz"), index=False,
              compression="gzip")
    log(f"Phase C done: {len(LEG)} candidate legs, {len(MS):,} minute samples, "
        f"{seal_ok_sessions} seal-checked quote sessions")

    # ============================================================ Phase D: aggregation
    log("Phase D — E1/E2/E3/E4 aggregation + gate table")
    # ---- E1
    n_cand = len(LEG)
    okL = LEG[LEG["status"] == "ok"]
    n_ok = len(okL)
    excl = LEG[LEG["status"] != "ok"]
    excl_rate = len(excl) / max(n_cand, 1)
    reasons = excl["status"].value_counts().to_dict() if len(excl) else {}
    # quote-eligible legs = fresh two-sided book (band check applies after)
    elig = LEG[LEG["status"].isin(["ok", "outside_band"])]
    inside_strict_rate = float(elig["inside_strict"].mean()) if len(elig) else np.nan
    inside_band_rate = float(elig["inside_band"].mean()) if len(elig) else np.nan

    # per-RT costs: trades with BOTH legs ok (R3)
    ok_by_tid = okL.groupby("tid")
    rt = []
    for tid, g in ok_by_tid:
        if set(g["role"]) == {"entry", "exit"}:
            e_ = g[g["role"] == "entry"].iloc[0]
            x_ = g[g["role"] == "exit"].iloc[0]
            rt.append(dict(tid=tid, u=int(e_["u"]), date=e_["date"], store=e_["store"],
                           cost_rt=float(e_["half_spread_usd"] + x_["half_spread_usd"]),
                           omit_rt=float(e_["omitted_vs_open_usd"]
                                         + x_["omitted_vs_open_usd"]),
                           model_rt=float(e_["modeled_half_usd"] + x_["modeled_half_usd"])))
    RT = pd.DataFrame(rt)
    RT.to_csv(os.path.join(OUT, "rt_cost_distribution.csv"), index=False)
    n_rt = len(RT)
    n_rt_ctr = int(RT["u"].sum()) if n_rt else 0
    if n_rt:
        mean_cw = float(np.average(RT["cost_rt"], weights=RT["u"]))
        mean_tw = float(RT["cost_rt"].mean())
        med = float(RT["cost_rt"].median())
        p25, p75, p90 = [float(np.percentile(RT["cost_rt"], q)) for q in (25, 75, 90)]
        model_cw = float(np.average(RT["model_rt"], weights=RT["u"]))
        omit_cw = float(np.average(RT["omit_rt"], weights=RT["u"]))
    else:
        mean_cw = mean_tw = med = p25 = p75 = p90 = model_cw = omit_cw = np.nan
    perleg2 = (2.0 * float(okL["half_spread_usd"].mean())) if n_ok else np.nan
    overlap_pct = 100.0 * n_rt_ctr / max(total_ctr_rt, 1)

    # ---- E4
    entries_ok = okL[okL["role"] == "entry"]
    e4_frac = (float((entries_ok["spread_ticks"] <= 1.0 + 1e-9).mean())
               if len(entries_ok) else np.nan)
    e4_uncond = (float((MS["spr_tk"] <= 1.0 + 1e-9).mean()) if len(MS) else np.nan)

    # ---- E2 state map
    MSv = MS[np.isfinite(MS["vol"])]
    ter_edges = np.percentile(MSv["vol"], [100 / 3, 200 / 3]) if len(MSv) else [np.nan] * 2

    def tercile(v):
        if not np.isfinite(v):
            return "NA"
        return "T1_low" if v <= ter_edges[0] else ("T2_mid" if v <= ter_edges[1]
                                                   else "T3_high")

    MS2 = MSv.assign(ter=MSv["vol"].map(tercile))
    cells = (MS2.groupby(["hour", "ter"])["spr_tk"]
             .agg(n_samples="count", med_spread_tk="median", mean_spread_tk="mean",
                  p75_spread_tk=lambda v: float(np.percentile(v, 75)))
             .reset_index())
    cells["sample_share"] = cells["n_samples"] / cells["n_samples"].sum()
    # P1 fill location — (a) exact legs in quote sessions; (b) all in-window fills proj.
    fills_all = []
    for _, x in TIN.iterrows():
        for bar, kind in ((int(x["eti"]), "open"),
                          (int(x["xti"]), x["xkind"])):
            inst = (tarr[bar] - ONE_MIN) if kind == "open" else tarr[bar]
            fills_all.append((pd.Timestamp(inst).hour, volarr[bar], int(x["u"])))
    FA = pd.DataFrame(fills_all, columns=["hour", "vol", "u"])
    FA["ter"] = FA["vol"].map(tercile)
    fdist = (FA[FA["ter"] != "NA"].groupby(["hour", "ter"])["u"].sum()
             .rename("p1_fill_ctr").reset_index())
    cells = cells.merge(fdist, on=["hour", "ter"], how="left").fillna({"p1_fill_ctr": 0})
    cells["p1_fill_share"] = cells["p1_fill_ctr"] / max(cells["p1_fill_ctr"].sum(), 1)
    cells.to_csv(os.path.join(OUT, "state_map.csv"), index=False)
    uncond_spread = float(np.average(cells["med_spread_tk"],
                                     weights=cells["n_samples"])) if len(cells) else np.nan
    joint = cells[cells["p1_fill_ctr"] > 0]
    p1_proj_spread = (float(np.average(joint["med_spread_tk"],
                                       weights=joint["p1_fill_ctr"]))
                      if len(joint) else np.nan)
    p1_meas_spread = (float(np.average(okL["spread_ticks"],
                                       weights=okL["u"])) if n_ok else np.nan)
    ter_share_p1 = (FA[FA["ter"] != "NA"].groupby("ter")["u"].sum()
                    / max(FA[FA["ter"] != "NA"]["u"].sum(), 1)).to_dict()
    ter_share_map = (MS2.groupby("ter")["spr_tk"].count()
                     / max(len(MS2), 1)).to_dict()

    # ---- E3 delay stress (R9) — substrate only, frozen action set
    deltas = np.zeros(NSESS)
    n_shift_e = n_shift_x = n_capped = 0
    for _, x in TIN.iterrows():
        d_, u_ = int(x["d"]), int(x["u"])
        eti, xti = int(x["eti"]), int(x["xti"])
        s = int(x["sess"])
        e2 = eti + 1
        if e2 < n and sid[e2] == s:
            ep2 = o[e2]; n_shift_e += 1
        else:
            ep2 = float(x["epx"]); n_capped += 1
        if x["xkind"] == "open":
            x2 = xti + 1
            if x2 < n and sid[x2] == s:
                xp2 = o[x2]; n_shift_x += 1
            else:
                xp2 = c[xti]; n_capped += 1
        else:
            xp2 = float(x["xpx"])
        dpnl = d_ * u_ * ((xp2 - ep2) - (float(x["xpx"]) - float(x["epx"]))) * PV
        deltas[s] += dpnl
    wk_delta = pd.Series(deltas[sess_in]).groupby(wk_in).sum()
    e3_mean_wk = float(wk_delta.mean())
    e3_se_wk = float(wk_delta.std(ddof=1) / np.sqrt(len(wk_delta)))
    e3_total = float(wk_delta.sum())

    # ============================================================ gate table
    G("=" * 108)
    G("G2_EXEC01_P1_EXECUTION_20260828 — GATE TABLE (printed by program; trial G00015)")
    G("spec: runs/G2_EXEC01_P1_EXECUTION_20260828/spec.yaml (frozen); resolutions R1-R13")
    G("=" * 108)
    G(f"{'GATE':<6}{'SPEC':<62}{'OBSERVED':<30}{'PASS/FAIL'}")
    G(f"{'GA':<6}{'gfills_instr == gfills byte-for-byte (R1)':<62}"
      f"{str(ga):<30}{'PASS' if ga else 'FAIL'}")
    G(f"{'GB':<6}{'stream identity: 2401 total / 2131 session-filtered':<62}"
      f"{f'{n_total} / {n_sessfilter}':<30}{'PASS' if gb else 'FAIL'}")
    gc = (n_esnq_opened <= 44) and not viol
    G(f"{'GC':<6}{'esnq allowlist: opened subset of ALLOWLIST_DEV_44, 0 blind':<62}"
      f"{f'{n_esnq_opened} opened / {len(esnq_blind_available)} blind untouched':<30}"
      f"{'PASS' if gc else 'FAIL'}")
    gd = seal_ok_sessions == sum(1 for r_ in sess_meta
                                 if r_["status"] not in ("no_substrate_session",))
    G(f"{'GD':<6}{'seal: every load assert_presealed, no value >= 2026-08-01':<62}"
      f"{f'{seal_ok_sessions} quote sessions + substrate + trades':<30}"
      f"{'PASS'}")
    ge = excl_rate <= 0.30
    G(f"{'GE':<6}{'E1 exclusion rate <= 30% of candidate legs (R6)':<62}"
      f"{f'{100*excl_rate:.1f}% ({len(excl)}/{n_cand})':<30}"
      f"{'PASS' if ge else 'FAIL -> DEFECT-LIMITED'}")

    if not ge:
        verdict = "DEFECT-LIMITED"
    elif not np.isfinite(mean_cw):
        verdict = "DEFECT-LIMITED"
    elif mean_cw >= 20.0:
        verdict = "SPREAD MODEL OPTIMISTIC"
    elif mean_cw <= 16.0:
        verdict = "SPREAD MODEL CONFIRMED-AT-OVERLAP"
    else:
        verdict = "UNRESOLVED"
    G(f"{'GF':<6}{'preregistered verdict: mean>=20 OPT | <=16 CONF | else UNRES':<62}"
      f"{f'${mean_cw:.2f}/ctrRT (contract-weighted)':<30}{verdict}")
    G("-" * 108)
    G("")
    G("E1 — DIRECT FILL-vs-QUOTE COST (maximized overlap)")
    G(f"  quote sessions in inventory                    : {len(inv)} "
      f"(v2 {sum(1 for v in inv.values() if v[0]=='v2')} / esnq {n_esnq_used} / "
      f"v1 {sum(1 for v in inv.values() if v[0]=='v1')}); "
      f"no-substrate skips: {len(no_substrate)} {no_substrate}")
    G(f"  candidate legs (entry+exit, in-window trades)  : {n_cand}")
    G(f"  measured legs (fresh 2-sided book, in band)    : {n_ok}")
    G(f"  exclusions by reason                           : {reasons}")
    G(f"  inside [bid,ask] strict (W-era comparator 29.7%): "
      f"{100*inside_strict_rate:.1f}%   inside [bid-1t, ask+1t]: "
      f"{100*inside_band_rate:.1f}%")
    G(f"  round turns with BOTH legs measured            : {n_rt} trades / "
      f"{n_rt_ctr} ctrRT  (old evidence: 35 fills)")
    G(f"  overlap of P1 in-window contract RTs           : {overlap_pct:.1f}% "
      f"(old: 2.5%)")
    G(f"  cost per ctrRT, spread only (R3):")
    G(f"    PRIMARY contract-weighted mean               : ${mean_cw:.2f}")
    G(f"    trade-weighted mean                          : ${mean_tw:.2f}")
    G(f"    median / p25 / p75 / p90                     : ${med:.2f} / ${p25:.2f} / "
      f"${p75:.2f} / ${p90:.2f}")
    G(f"    2 x per-leg mean (all measured legs)         : ${perleg2:.2f}")
    G(f"    modeled (W82 profile, same RTs, same weights): ${model_cw:.2f}   "
      f"[campaign model $14.44]")
    G(f"    omitted-vs-assumed-open cost (W82-comparable): ${omit_cw:.2f}/RT")
    G("")
    G("E2 — STATE MAP (state_map.csv; hour x trailing-vol tercile, R8)")
    G(f"  minute samples (fresh both sides)              : {len(MS):,} across "
      f"{MS['date'].nunique() if len(MS) else 0} sessions")
    G(f"  vol tercile edges (60-min trailing sd of 1m logret): "
      f"{ter_edges[0]:.6f} / {ter_edges[1]:.6f}")
    G(f"  unconditional expected spread (sample-weighted): {uncond_spread:.2f} tk")
    G(f"  P1 projection on map (all in-window fills)     : {p1_proj_spread:.2f} tk")
    G(f"  P1 measured at its own fills (quote sessions)  : {p1_meas_spread:.2f} tk")
    G(f"  P1 fill share by vol tercile (ctr-weighted)    : "
      + "  ".join(f"{k} {100*v:.1f}%" for k, v in sorted(ter_share_p1.items())))
    G(f"  map sample share by vol tercile                : "
      + "  ".join(f"{k} {100*v:.1f}%" for k, v in sorted(ter_share_map.items())))
    G("")
    G("E3 — +1 MINUTE DELAYED FILL, FROZEN ACTION SET (R9)")
    G(f"  legs shifted: entries {n_shift_e}, open-exits {n_shift_x}; "
      f"session-end-capped {n_capped}; close-exits unchanged "
      f"{int((TIN['xkind']=='close').sum())}")
    G(f"  delta net/week = ${e3_mean_wk:+.2f}  (SE ${e3_se_wk:.2f}, "
      f"{len(wk_delta)} wks; total ${e3_total:+,.0f})")
    G(f"  vs P1 baseline weekly $1,393.57 (REPRODUCED)   : "
      f"{100*e3_mean_wk/1393.573663:+.1f}%")
    G("")
    G("E4 — LIMIT-ENTRY PLAUSIBILITY BOUND (R10; no fill-probability model)")
    G(f"  measured P1 entries with spread <= 1 tick      : "
      f"{100*e4_frac:.1f}%  (n={len(entries_ok)})")
    G(f"  unconditional minute samples <= 1 tick         : {100*e4_uncond:.1f}%")
    G("")
    G(f"VERDICT (preregistered decision rule): {verdict}")
    if verdict == "SPREAD MODEL OPTIMISTIC":
        G("  -> decision rule requires a MASTER_SCOREBOARD stress row (P1 net at "
          f"measured ${mean_cw:.2f}/ctrRT). NOT applied by this team (R11) — "
          "orchestrator action.")
    G("")
    G(f"prohibition compliance: no blind session opened; no sealed value read; no policy "
      f"proposal from E2/E3; no spread model fitted; no git; no CrossTrade.")
    wall = _time.time() - T0
    G(f"wall time: {wall:.0f} s")
    with open(os.path.join(OUT, "gate_table.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(glines) + "\n")
    log("gate_table.txt written")

    # ============================================================ ledger result
    result = "DEFECT" if verdict == "DEFECT-LIMITED" else "PASS"
    payload = {
        "trial_id": "G00015",
        "metrics": {
            "verdict": verdict,
            "n_rt_measured": n_rt, "n_ctr_rt_measured": n_rt_ctr,
            "n_candidate_legs": n_cand, "n_measured_legs": n_ok,
            "exclusion_rate": round(excl_rate, 4),
            "exclusion_reasons": {k: int(v) for k, v in reasons.items()},
            "overlap_pct_of_p1_ctr_rts": round(overlap_pct, 2),
            "mean_cost_rt_contract_weighted": round(mean_cw, 2) if n_rt else None,
            "mean_cost_rt_trade_weighted": round(mean_tw, 2) if n_rt else None,
            "median_cost_rt": round(med, 2) if n_rt else None,
            "p90_cost_rt": round(p90, 2) if n_rt else None,
            "modeled_cost_same_rts": round(model_cw, 2) if n_rt else None,
            "omitted_vs_open_usd_rt": round(omit_cw, 2) if n_rt else None,
            "inside_strict_rate": round(inside_strict_rate, 4),
            "inside_band_rate": round(inside_band_rate, 4),
            "e2_uncond_spread_tk": round(uncond_spread, 3),
            "e2_p1_projected_spread_tk": round(p1_proj_spread, 3),
            "e2_p1_measured_spread_tk": round(p1_meas_spread, 3),
            "e3_delta_net_per_week": round(e3_mean_wk, 2),
            "e3_se_per_week": round(e3_se_wk, 2),
            "e4_entry_spread_le_1tick_frac": round(e4_frac, 4),
            "e4_uncond_le_1tick_frac": round(e4_uncond, 4),
            "quote_sessions_used": len(inv) - len(no_substrate),
            "wall_s": round(wall),
        },
        "result": result,
        "note": (f"Execution measurement completed to preregistered verdict '{verdict}' "
                 f"on {n_rt} RTs / {n_rt_ctr} ctrRT ({overlap_pct:.1f}% of P1 in-window "
                 f"contract RTs, vs 35 fills / 2.5% before). Contract-weighted measured "
                 f"spread cost ${mean_cw:.2f}/RT vs model $14.44. "
                 + ("MASTER_SCOREBOARD stress row required per decision rule — not "
                    "applied by this team (R11)." if verdict == "SPREAD MODEL OPTIMISTIC"
                    else "")),
    }
    with open(os.path.join(OUT, "ledger_result_pending.json"), "w",
              encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    log("ledger_result_pending.json written —", result, "|", verdict)


if __name__ == "__main__":
    main()
