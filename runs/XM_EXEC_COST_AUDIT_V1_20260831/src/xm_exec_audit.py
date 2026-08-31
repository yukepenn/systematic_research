"""XM_EXEC_COST_AUDIT_V1_20260831 — XM_CONFLICT execution-cost audit.

Executes the frozen spec.yaml written before this file first ran. Method is G2_EXEC01's,
re-pointed at XM_CONFLICT, with one structural addition the spec names: XM's fill instants
are DETERMINISTIC (09:45:00 and 15:45:00 ET), so the cost-relevant spread can be measured on
EVERY owned quote session, not only the ones XM happened to trade.

Seal: every load passes research_sdk.seal_guard.assert_presealed.
Blind pool: research/data_esnq opened ONLY for ALLOWLIST_DEV_44 dates, enforced and printed.
Writes ONLY under runs/XM_EXEC_COST_AUDIT_V1_20260831/out/. No git. No CrossTrade. No orders.
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
RUN = os.path.join(ROOT, "runs", "XM_EXEC_COST_AUDIT_V1_20260831")
OUT = os.path.join(RUN, "out")
os.makedirs(OUT, exist_ok=True)
SRC = os.path.join(ROOT, "research", "weekly_edge", "src")
sys.path.insert(0, SRC)
sys.path.insert(0, ROOT)

from research_sdk.seal_guard import assert_presealed                     # noqa: E402
import run_we_w01 as W1                                                  # noqa: E402
from run_we_w01 import PV, COMM_RT                                       # noqa: E402
from run_we_w17 import load_deep                                         # noqa: E402
from run_we_w51 import session_frames                                    # noqa: E402
from run_we_w51c import dd_profile                                       # noqa: E402
from we_lab import spread_profile                                        # noqa: E402

T0 = _time.time()
A = np.datetime64("2022-07-01")
B = np.datetime64("2026-08-01")
DDT = 20245.0
TICK = 0.25
TICKV = 5.0
STALE_NS = 5_000_000_000
ONE_MIN = np.timedelta64(60, "s")
ANCH, DEC, ENTM, EXITM, EXITNB = 571, 585, 586, 945, 946
SIG_LB, SIG_MIN = 60, 20
XMS = {"ES": "runs/SM1M_ES_SUBSTRATE/out/es_1m_2022_2026.parquet",
       "RTY": "runs/SM1M_RTY_SUBSTRATE/out/rty_1m_2022_2026.parquet",
       "YM": "runs/SM1M_YM_SUBSTRATE/out/ym_1m_2022_2026.parquet"}

ESNQ_NQ = os.path.join(ROOT, "research", "data_esnq", "parquet", "NQ")
ESNQ_ES = os.path.join(ROOT, "research", "data_esnq", "parquet", "ES")
ALLOWLIST_PATH = os.path.join(ROOT, "research", "data_esnq", "ALLOWLIST_DEV_44.txt")
V2_DIR = os.path.join(ROOT, "research", "data_microstructure_v2", "raw", "NQ")
V1_DIR = os.path.join(ROOT, "research", "scalping_lab", "substrate", "raw", "NQ")
V1_NO_BBO = {"20250811", "20250924", "20260430"}     # G2_EXEC01 R7, Last-only sessions

REF_CSV = os.path.join(ROOT, "research", "weekly_edge", "ninjascript", "reference",
                       "xm_reference_decisions.csv")


def log(*a):
    print(f"[{_time.time()-T0:6.0f}s]", *a, flush=True)


def main():
    glines = []

    def G(*a):
        s = " ".join(str(x) for x in a)
        glines.append(s)
        print(s, flush=True)

    # =============================================================== Phase A: XM object
    log("Phase A — substrate + XM_CONFLICT object regeneration (verbatim sequential loop)")
    prof = spread_profile()
    D = load_deep("2022-01-01", "2026-07-31 17:00", extend=True)
    W1.DEV_END = pd.Timestamp("2026-07-31").date()
    n, tarr, sid = D["n"], D["t"], D["sid"]
    o, c = D["o"], D["c"]
    st_, en_, _ = session_frames(D)
    NSESS = D["n_sess"]
    sdate = pd.to_datetime(D["sess_date"])
    mod = ((tarr - tarr.astype("datetime64[D]")).astype("timedelta64[s]")
           .astype(np.int64) // 60).astype(np.int32)
    win = np.array([A <= tarr[st_[s]] < B for s in range(NSESS)])
    sess_in = np.flatnonzero(win)
    iso = sdate.isocalendar()
    wkall = (iso["year"].astype(str) + "-W" + iso["week"].astype(str).str.zfill(2)).to_numpy()
    wk = wkall[sess_in]
    NW = len(set(wk))
    assert_presealed(pd.DataFrame({"t": pd.to_datetime(tarr)}), "t", "substrate 1-min bars")
    log(f"substrate {n:,} bars / {NSESS:,} sessions; in-window {len(sess_in)} sessions, "
        f"{NW} ISO weeks — seal PASS")

    nq = pd.DataFrame({"time": pd.to_datetime(tarr), "nq": c}).set_index("time")
    XD = {}
    for k, path in XMS.items():
        d_ = pd.read_parquet(os.path.join(ROOT, path), columns=["time", "close"])
        d_["time"] = pd.to_datetime(d_["time"])
        assert_presealed(d_, "time", f"{k} 1-min substrate")
        XD[k] = nq.join(d_.set_index("time")["close"].rename(k), how="left")[k].to_numpy()
    XTS = {k: ~np.isnan(XD[k]) for k in XMS}

    def at2(mv, arr, uo=False):
        r = np.full(NSESS, np.nan)
        ix = np.full(NSESS, -1, np.int64)
        m_ = mod == mv
        r[sid[m_]] = (o[m_] if uo else arr[m_])
        ix[sid[m_]] = np.flatnonzero(m_)
        return r, ix

    pa, ia = at2(ANCH, o, True)
    pdc, idc = at2(DEC, c)
    pe, ie = at2(ENTM, o, True)
    px_close, ix_c = at2(EXITM, c)
    px_nbo, ix_n = at2(EXITNB, o, True)

    HIST = {k: [] for k in XMS}
    drive = np.zeros(NSESS)
    comp = np.full(NSESS, np.nan)
    conflict = np.zeros(NSESS, np.int8)
    desired = np.zeros(NSESS, np.int8)
    disq = np.zeros(NSESS, bool)
    for s in range(NSESS):
        if not np.isfinite(pa[s]) or not np.isfinite(pdc[s]):
            continue
        ok = True
        for k in XMS:
            if ia[s] < 0 or idc[s] < 0 or not XTS[k][ia[s]] or not XTS[k][idc[s]]:
                ok = False
        if not ok:
            disq[s] = True
            continue
        if not win[s]:
            for k in XMS:
                HIST[k].append(np.log(XD[k][idc[s]] / XD[k][ia[s]]))
            continue
        drive[s] = np.sign(pdc[s] - pa[s])
        acc, cnt = 0.0, 0
        for k in XMS:
            r_ = np.log(XD[k][idc[s]] / XD[k][ia[s]])
            hh = HIST[k]
            if len(hh) >= SIG_MIN:
                w_ = hh[-SIG_LB:]
                sg = float(np.std(w_, ddof=1))
                if sg > 1e-12:
                    acc += r_ / sg
                    cnt += 1
            hh.append(r_)
        if cnt:
            comp[s] = acc / cnt
            xs = np.sign(comp[s])
            if xs != 0 and drive[s] != 0 and xs != drive[s]:
                conflict[s] = 1
                desired[s] = int(drive[s])
    take = (desired != 0) & np.isfinite(pe) & np.isfinite(px_close) & np.isfinite(px_nbo)
    desired = np.where(take, desired, 0).astype(np.int8)
    n_seq = int((desired != 0).sum())
    n_long = int((desired > 0).sum())
    n_short = int((desired < 0).sum())

    SPREAD_MODEL = TICKV * (float(prof.loc[ENTM]) + float(prof.loc[EXITNB])) / 2.0
    cst_n = COMM_RT + SPREAD_MODEL
    trade_s = np.flatnonzero(desired != 0)
    gross = np.zeros(NSESS)
    gross[trade_s] = desired[trade_s] * (px_nbo[trade_s] - pe[trade_s]) * PV
    net_model = np.where(desired != 0, gross - cst_n, 0.0)
    net_total = float(net_model[sess_in].sum())

    # identity gate against the committed reference
    REF = pd.read_csv(REF_CSV)
    ref_n = int((REF.desired_direction != 0).sum())
    ref_net = float(REF.pnl_nt8_convention.sum())
    # POSITIONAL comparison: export_xm_reference.py emits one row per in-window session in
    # `for s in range(NS)` order, so row i of the reference IS session sess_in[i]. Two calendar
    # dates (2025-11-27, 2026-07-17) appear twice as split sessions, so a date-keyed merge
    # cross-products and is not the right key. Order is the key.
    my = pd.DataFrame(dict(session_date=[sdate[s].strftime("%Y-%m-%d") for s in sess_in],
                           desired=desired[sess_in],
                           entry=pe[sess_in], exit=px_nbo[sess_in],
                           pnl=net_model[sess_in]))
    ga_len = len(my) == len(REF)
    ga_date = ga_len and bool((my["session_date"].to_numpy()
                               == REF["session_date"].to_numpy()).all())
    ga_dir = ga_len and int((REF["desired_direction"].to_numpy()
                             != my["desired"].to_numpy()).sum()) == 0
    ga_pnl = ga_len and float(np.nanmax(np.abs(REF["pnl_nt8_convention"].to_numpy()
                                               - my["pnl"].to_numpy()))) < 1e-6
    _tm = my["desired"].to_numpy() != 0
    ga_px = ga_len and float(np.nanmax(np.abs(
        REF["entry_px"].to_numpy()[_tm] - my["entry"].to_numpy()[_tm]))) < 1e-9 \
        and float(np.nanmax(np.abs(
            REF["exit_px_open1546"].to_numpy()[_tm] - my["exit"].to_numpy()[_tm]))) < 1e-9
    ga = bool(ga_len and ga_date and ga_dir and ga_pnl and ga_px)
    gb = (n_seq == 346 and n_long == 176 and n_short == 170
          and abs(net_total - 199436.44) < 0.01 and abs(ref_net - 199436.44) < 0.01)
    log(f"XM sequential: {n_seq} trades ({n_long}L/{n_short}S), net ${net_total:,.2f}; "
        f"GA={ga} GB={gb}")

    # vectorised 348-trade variant (the object the MASTER_SCOREBOARD row quotes)
    px_c945, _ = at2(EXITM, c)
    driv_v = np.sign(pdc - pa)
    accv = np.zeros(NSESS)
    cntv = np.zeros(NSESS)
    for k in XMS:
        a_, _ = at2(ANCH, XD[k])
        b_, _ = at2(DEC, XD[k])
        r_ = np.log(b_ / a_)
        s_ = pd.Series(r_).rolling(60, min_periods=20).std().shift(1).to_numpy()
        zz = r_ / np.maximum(s_, 1e-12)
        g_ = np.isfinite(zz)
        accv[g_] += zz[g_]
        cntv[g_] += 1
    xsv = np.sign(np.where(cntv > 0, accv / np.maximum(cntv, 1), np.nan))
    okm = (win & np.isfinite(pa) & np.isfinite(pdc) & np.isfinite(pe) & np.isfinite(px_c945)
           & np.isfinite(xsv) & (driv_v != 0) & (xsv != 0))
    cf = okm & (xsv != driv_v)
    cstx = COMM_RT + TICKV * (float(prof.loc[ENTM]) + float(prof.loc[EXITM])) / 2.0
    gross_v = np.zeros(NSESS)
    gross_v[cf] = driv_v[cf] * (px_c945[cf] - pe[cf]) * PV
    sxm = np.where(cf, gross_v - cstx, 0.0)

    def wkv(x):
        return pd.Series(x[sess_in]).groupby(wk).sum().to_numpy()

    def pan(w):
        dp = dd_profile(w)
        return dict(weekly=float(w.mean()),
                    maxdd=float(dp["maxdd"]),
                    fixdd=float(w.mean()) * DDT / max(dp["maxdd"], 1e-9),
                    t=float(w.mean()) / max(w.std(ddof=1) / np.sqrt(len(w)), 1e-9))

    pv = pan(wkv(sxm))
    gc_ = (int(cf.sum()) == 348 and abs(pv["weekly"] - 915.505728) < 0.01
           and abs(pv["maxdd"] - 20200.80) < 0.01 and abs(pv["t"] - 3.046363) < 0.01)
    ps = pan(wkv(net_model))
    log(f"vectorised 348 reproduce: {int(cf.sum())} trades weekly ${pv['weekly']:.4f} "
        f"maxdd ${pv['maxdd']:.2f} t {pv['t']:.4f} — GC={gc_}")

    TT = pd.DataFrame([dict(
        sess=int(s), sess_date=sdate[s].strftime("%Y%m%d"), week=wkall[s],
        d=int(desired[s]), u=1,
        eti=int(ie[s]), xti=int(ix_n[s]),
        entry_bar_stamp=str(pd.Timestamp(tarr[int(ie[s])])),
        exit_bar_stamp=str(pd.Timestamp(tarr[int(ix_n[s])])),
        epx=float(pe[s]), xpx=float(px_nbo[s]),
        gross=float(gross[s]), pnl_model=float(net_model[s]))
        for s in trade_s])
    TT["tid"] = np.arange(len(TT))
    assert_presealed(TT.assign(ts=pd.to_datetime(TT["entry_bar_stamp"])), "ts", "XM entries")
    TT.to_csv(os.path.join(OUT, "xm_trades.csv"), index=False)

    # ============================================================ Phase B: quote inventory
    log("Phase B — quote-session inventory + blind-pool enforcement")
    with open(ALLOWLIST_PATH, "r", encoding="utf-8") as f:
        allowlist = {ln.strip() for ln in f if ln.strip()}
    assert len(allowlist) == 44, "ALLOWLIST_DEV_44 does not have 44 entries"
    v2_dates = {f[1:9] for f in os.listdir(V2_DIR) if f.endswith(".parquet")}
    esnq_all = {f[1:9] for f in os.listdir(ESNQ_NQ) if f.endswith(".parquet")}
    v1_dates = {f[1:9] for f in os.listdir(V1_DIR)
                if f.endswith(".parquet") and "_rth" not in f} - V1_NO_BBO
    inv = {}
    for d_ in sorted(v2_dates):
        inv[d_] = ("v2", os.path.join(V2_DIR, f"s{d_}.parquet"))
    n_esnq_used = 0
    for d_ in sorted(esnq_all & allowlist):
        if d_ not in inv:
            inv[d_] = ("esnq", os.path.join(ESNQ_NQ, f"s{d_}.parquet"))
            n_esnq_used += 1
    for d_ in sorted(v1_dates):
        if d_ not in inv:
            inv[d_] = ("v1", os.path.join(V1_DIR, f"s{d_}.parquet"))
    esnq_blind = sorted(esnq_all - allowlist)
    viol = [d_ for d_, (s_, _) in inv.items() if s_ == "esnq" and d_ not in allowlist]
    print("=" * 100)
    print("BLIND-POOL ENFORCEMENT — research/data_esnq (printed before any esnq open):")
    print(f"  allowlist entries {len(allowlist)} | esnq on disk {len(esnq_all)} | "
          f"outside allowlist (BLIND) {len(esnq_blind)} — NONE opened | "
          f"planned opens {n_esnq_used} (violations: {len(viol)})")
    print("=" * 100)
    if viol:
        raise SystemExit("BLIND SESSION WOULD BE TOUCHED — ABORT")
    date_to_sess = {sdate[s].strftime("%Y%m%d"): s for s in range(NSESS)}
    trade_by_date = {r.sess_date: r for r in TT.itertuples()}
    log(f"inventory {len(inv)} sessions (v2 {sum(1 for v in inv.values() if v[0]=='v2')} / "
        f"esnq {n_esnq_used} / v1 {sum(1 for v in inv.values() if v[0]=='v1')})")

    # ============================================================ Phase C: session loop
    log("Phase C — per-session quote measurement at the two XM clock instants")
    clock_rows, leg_rows, sess_meta = [], [], []
    n_esnq_opened = 0
    seal_sessions = 0
    for d_ in sorted(inv):
        store, path = inv[d_]
        if d_ not in date_to_sess:
            sess_meta.append(dict(date=d_, store=store, status="no_substrate_session"))
            continue
        s = date_to_sess[d_]
        if store == "esnq":
            assert d_ in allowlist, f"allowlist violation {d_} — ABORT"
            n_esnq_opened += 1
        tbl = pq.read_table(path, columns=["bip", "time", "price"])
        qt = tbl.column("time").to_numpy().astype("datetime64[ns]")
        qb = tbl.column("bip").to_numpy()
        qp = tbl.column("price").to_numpy()
        del tbl
        assert_presealed(pd.DataFrame({"time": qt}), "time", f"quotes s{d_} [{store}]")
        seal_sessions += 1
        bm, am = qb == 1, qb == 2
        bt, bp = qt[bm].astype("int64"), qp[bm]
        at_, ap = qt[am].astype("int64"), qp[am]
        if len(bt) and np.any(np.diff(bt) < 0):
            i_ = np.argsort(bt, kind="stable"); bt, bp = bt[i_], bp[i_]
        if len(at_) and np.any(np.diff(at_) < 0):
            i_ = np.argsort(at_, kind="stable"); at_, ap = at_[i_], ap[i_]
        if len(bt) == 0 or len(at_) == 0:
            sess_meta.append(dict(date=d_, store=store, status="no_bbo"))
            continue

        def asof(x):
            ib = np.searchsorted(bt, x, side="right") - 1
            iaa = np.searchsorted(at_, x, side="right") - 1
            okb, oka = ib >= 0, iaa >= 0
            bpx = np.where(okb, bp[np.maximum(ib, 0)], np.nan)
            apx = np.where(oka, ap[np.maximum(iaa, 0)], np.nan)
            ageb = np.where(okb, x - bt[np.maximum(ib, 0)], np.int64(2 ** 62))
            agea = np.where(oka, x - at_[np.maximum(iaa, 0)], np.int64(2 ** 62))
            return bpx, apx, ageb, agea

        j0, j1 = int(st_[s]), int(en_[s])
        stamps = tarr[j0:j1]
        close_ns = stamps.astype("datetime64[ns]").astype("int64")
        bpx, apx, ageb, agea = asof(close_ns)
        fresh = (ageb <= STALE_NS) & (agea <= STALE_NS) & (apx >= bpx)
        diff = c[j0:j1] - (bpx + apx) / 2.0
        n_off = int(fresh.sum())
        if n_off < 30:
            sess_meta.append(dict(date=d_, store=store, status="too_few_offset_pts",
                                  n_off=n_off))
            continue
        off_raw = float(np.median(diff[fresh]))
        offset = round(off_raw / TICK) * TICK
        off_mad = float(np.median(np.abs(diff[fresh] - off_raw)))
        store_end = int(min(bt[-1], at_[-1]))

        traded = d_ in trade_by_date
        rowT = trade_by_date.get(d_)
        for role, mv in (("entry", ENTM), ("exit", EXITNB)):
            bar = int(ie[s]) if role == "entry" else int(ix_n[s])
            if bar < 0:
                clock_rows.append(dict(date=d_, store=store, role=role, status="no_bar",
                                       traded=traded))
                continue
            inst = int((tarr[bar] - ONE_MIN).astype("datetime64[ns]").astype("int64"))
            b_, a_, gb_, ga_ = asof(np.array([inst], dtype="int64"))
            b_, a_ = float(b_[0]), float(a_[0])
            gb_, ga_ = int(gb_[0]), int(ga_[0])
            st_status = "ok"
            if not np.isfinite(b_) or not np.isfinite(a_):
                st_status = "no_quote"
            elif gb_ > STALE_NS or ga_ > STALE_NS:
                st_status = "stale_after_store_end" if inst > store_end else "stale"
            elif a_ < b_:
                st_status = "crossed"
            spr = (a_ - b_) / TICK if st_status == "ok" else np.nan
            clock_rows.append(dict(
                date=d_, store=store, role=role, status=st_status, traded=traded,
                instant=str(pd.Timestamp(inst)), bid=b_, ask=a_,
                spread_ticks=spr, half_spread_usd=(a_ - b_) / 2.0 * PV
                if st_status == "ok" else np.nan,
                modeled_spread_ticks=float(prof.loc[mv]),
                modeled_half_usd=TICKV * float(prof.loc[mv]) / 2.0,
                age_bid_ms=gb_ / 1e6 if gb_ < 2 ** 61 else np.nan,
                age_ask_ms=ga_ / 1e6 if ga_ < 2 ** 61 else np.nan,
                offset=offset))
            if traded:
                d_dir = int(rowT.d)
                if role == "entry":
                    px = float(rowT.epx)
                    side = "buy" if d_dir > 0 else "sell"
                else:
                    px = float(rowT.xpx)
                    side = "sell" if d_dir > 0 else "buy"
                pxc = px - offset
                stt = st_status
                inside_strict = inside_band = False
                half = omit = sprleg = np.nan
                if stt == "ok":
                    inside_band = (b_ - TICK - 1e-9 <= pxc <= a_ + TICK + 1e-9)
                    inside_strict = (b_ - 1e-9 <= pxc <= a_ + 1e-9)
                    if not inside_band:
                        stt = "outside_band"
                    else:
                        sprleg = (a_ - b_) / TICK
                        half = (a_ - b_) / 2.0 * PV
                        omit = ((a_ - pxc) if side == "buy" else (pxc - b_)) * PV
                leg_rows.append(dict(
                    tid=int(rowT.tid), date=d_, store=store, role=role, side=side,
                    d=d_dir, u=1, instant=str(pd.Timestamp(inst)),
                    px_substrate=px, offset=offset, px_corrected=pxc,
                    bid=b_, ask=a_, spread_ticks=sprleg, half_spread_usd=half,
                    omitted_vs_open_usd=omit,
                    modeled_half_usd=TICKV * float(prof.loc[mv]) / 2.0,
                    inside_strict=inside_strict, inside_band=inside_band,
                    age_bid_ms=gb_ / 1e6 if gb_ < 2 ** 61 else np.nan,
                    age_ask_ms=ga_ / 1e6 if ga_ < 2 ** 61 else np.nan,
                    status=stt))
        sess_meta.append(dict(date=d_, store=store, status="ok", offset=offset,
                              offset_raw=round(off_raw, 4), offset_mad=round(off_mad, 4),
                              n_offset_pts=n_off, xm_traded=int(traded)))
        if len(sess_meta) % 25 == 0:
            log(f"  ... {len(sess_meta)}/{len(inv)} sessions")

    CK = pd.DataFrame(clock_rows)
    CK.to_csv(os.path.join(OUT, "clock_spread.csv"), index=False)
    LEG = pd.DataFrame(leg_rows)
    LEG.to_csv(os.path.join(OUT, "leg_costs.csv"), index=False)
    pd.DataFrame(sess_meta).to_csv(os.path.join(OUT, "session_offsets.csv"), index=False)
    log(f"Phase C done: {len(CK)} clock observations, {len(LEG)} matched legs")

    # ============================================================ Phase D: aggregation
    log("Phase D — aggregation, gates, economics")

    def era(d_):
        if d_ < "20260101":
            return "2025H2"
        if d_ < "20260601":
            return "2026_Jan_May"
        return "2026_Jun_Jul"

    CKok = CK[CK["status"] == "ok"].copy()
    CKok["era"] = CKok["date"].map(era)
    # X2 clock-anchored
    x2 = (CKok.groupby("role")
          .agg(n=("spread_ticks", "size"), mean_tk=("spread_ticks", "mean"),
               med_tk=("spread_ticks", "median"),
               p75_tk=("spread_ticks", lambda v: float(np.percentile(v, 75))),
               p90_tk=("spread_ticks", lambda v: float(np.percentile(v, 90))),
               model_tk=("modeled_spread_ticks", "first"))
          .reindex(["entry", "exit"]))
    x2_rt_mean = float(TICKV * x2["mean_tk"].sum() / 2.0)
    x2_rt_med = float(TICKV * x2["med_tk"].sum() / 2.0)
    # session-paired RT from clock rows (both roles ok on the same session)
    piv = CKok.pivot_table(index="date", columns="role", values="half_spread_usd")
    piv = piv.dropna(subset=[cc for cc in ("entry", "exit") if cc in piv.columns])
    x2_paired = (piv["entry"] + piv["exit"]) if {"entry", "exit"} <= set(piv.columns) \
        else pd.Series(dtype=float)
    # conditioning: traded vs not
    trm = CKok.pivot_table(index="date", columns="role", values="spread_ticks")
    trm = trm.dropna()
    tr_flag = CKok.groupby("date")["traded"].max()
    trm = trm.join(tr_flag)
    trm["rt_usd"] = TICKV * (trm["entry"] + trm["exit"]) / 2.0
    cond_t = trm[trm["traded"]]["rt_usd"]
    cond_n = trm[~trm["traded"].astype(bool)]["rt_usd"]

    # X1 matched
    n_cand = len(LEG)
    okL = LEG[LEG["status"] == "ok"]
    excl = LEG[LEG["status"] != "ok"]
    excl_rate = len(excl) / max(n_cand, 1)
    reasons = excl["status"].value_counts().to_dict() if len(excl) else {}
    elig = LEG[LEG["status"].isin(["ok", "outside_band"])]
    ins_strict = float(elig["inside_strict"].mean()) if len(elig) else np.nan
    ins_band = float(elig["inside_band"].mean()) if len(elig) else np.nan
    rt = []
    for tid, g in okL.groupby("tid"):
        if set(g["role"]) == {"entry", "exit"}:
            e_ = g[g["role"] == "entry"].iloc[0]
            x_ = g[g["role"] == "exit"].iloc[0]
            rt.append(dict(tid=tid, date=e_["date"], d=int(e_["d"]),
                           side_dir="LONG" if int(e_["d"]) > 0 else "SHORT",
                           cost_rt=float(e_["half_spread_usd"] + x_["half_spread_usd"]),
                           omit_rt=float(e_["omitted_vs_open_usd"]
                                         + x_["omitted_vs_open_usd"]),
                           model_rt=float(e_["modeled_half_usd"] + x_["modeled_half_usd"])))
    RT = pd.DataFrame(rt)
    if len(RT):
        RT["era"] = RT["date"].map(era)
    RT.to_csv(os.path.join(OUT, "rt_cost_distribution.csv"), index=False)
    n_rt = len(RT)
    if n_rt:
        m_meas = float(RT["cost_rt"].mean())
        med_meas = float(RT["cost_rt"].median())
        p75 = float(np.percentile(RT["cost_rt"], 75))
        p90 = float(np.percentile(RT["cost_rt"], 90))
        m_model = float(RT["model_rt"].mean())
        m_omit = float(RT["omit_rt"].mean())
        rng = np.random.default_rng(20260831)
        _v = RT["cost_rt"].to_numpy()
        bs = _v[rng.integers(0, n_rt, size=(4000, n_rt))].mean(axis=1)
        ci = (float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5)))
    else:
        m_meas = med_meas = p75 = p90 = m_model = m_omit = np.nan
        ci = (np.nan, np.nan)

    # X3 two-sided
    side_tbl = (okL.groupby(["d", "role", "side"])
                .agg(n=("omitted_vs_open_usd", "size"),
                     mean_omit=("omitted_vs_open_usd", "mean"),
                     mean_half=("half_spread_usd", "mean"),
                     mean_spr_tk=("spread_ticks", "mean")).reset_index())
    side_tbl.to_csv(os.path.join(OUT, "two_sided_table.csv"), index=False)
    if n_rt:
        L = RT[RT["d"] > 0]
        S = RT[RT["d"] < 0]
        ls_cost = (float(L["cost_rt"].mean()) if len(L) else np.nan,
                   float(S["cost_rt"].mean()) if len(S) else np.nan)
        ls_omit = (float(L["omit_rt"].mean()) if len(L) else np.nan,
                   float(S["omit_rt"].mean()) if len(S) else np.nan)
        if len(L) > 2 and len(S) > 2:
            dmu = ls_omit[0] - ls_omit[1]
            se = np.sqrt(L["omit_rt"].var(ddof=1) / len(L) + S["omit_rt"].var(ddof=1) / len(S))
            t_ls = dmu / max(se, 1e-12)
        else:
            dmu, t_ls = np.nan, np.nan
    else:
        ls_cost = ls_omit = (np.nan, np.nan)
        dmu = t_ls = np.nan

    # decision rule on the spread verdict
    DEFECT_LIMITED = excl_rate > 0.30 or n_rt < 25
    headline_source = "X1_matched" if not DEFECT_LIMITED else "X2_clock_anchored"
    measured_spread = m_meas if headline_source == "X1_matched" else x2_rt_mean
    if not np.isfinite(measured_spread):
        verdict = "DEFECT-LIMITED"
    elif measured_spread >= 1.3 * SPREAD_MODEL:
        verdict = "XM SPREAD MODEL OPTIMISTIC"
    elif measured_spread <= SPREAD_MODEL:
        verdict = "XM SPREAD MODEL CONFIRMED-AT-OVERLAP"
    else:
        verdict = "UNRESOLVED"

    # X6 economics
    C_MOD = COMM_RT + SPREAD_MODEL
    C_MEAS = COMM_RT + measured_spread
    C_PESS = COMM_RT + measured_spread + 2 * TICKV
    gross_total = float(gross[sess_in].sum())
    ntr = n_seq

    def econ(C, label):
        ser = np.where(desired != 0, gross - C, 0.0)
        w_ = wkv(ser)
        p_ = pan(w_)
        return dict(model=label, cost_per_rt=C, spread_part=C - COMM_RT,
                    trades=ntr, net_total=float(ser[sess_in].sum()),
                    net_per_trade=float(ser[sess_in].sum()) / ntr,
                    weekly=p_["weekly"], maxdd=p_["maxdd"], fixdd=p_["fixdd"], t=p_["t"])

    ECON = pd.DataFrame([econ(C_MOD, "MODELLED"), econ(C_MEAS, "MEASURED"),
                         econ(C_PESS, "PESSIMISTIC")])
    if n_rt:
        ECON = pd.concat([ECON, pd.DataFrame([
            econ(COMM_RT + p75, "SENS_p75"),
            econ(COMM_RT + p90, "SENS_p90")])], ignore_index=True)
    breakeven = gross_total / ntr
    ECON.to_csv(os.path.join(OUT, "economics.csv"), index=False)
    d_wk_per_dollar = ntr / NW      # $/wk lost per +$1/ctrRT
    # P1 in-window contract RTs, read from the G2_EXEC01 artifact (2,131 trades / 2,556 ctrRT)
    p1_ctr_rt = float(pd.read_csv(os.path.join(
        ROOT, "runs", "G2_EXEC01_P1_EXECUTION_20260828", "out", "p1_trades.csv")
    ).query("in_win == True")["u"].sum())

    # era cells
    era_tbl = (CKok.groupby(["era", "role"])["spread_ticks"]
               .agg(n="size", mean="mean", med="median").reset_index())
    era_rt = (CKok.pivot_table(index="date", columns="role", values="spread_ticks")
              .dropna())
    era_rt["era"] = era_rt.index.map(era)
    era_rt["rt_usd"] = TICKV * (era_rt["entry"] + era_rt["exit"]) / 2.0
    era_sum = era_rt.groupby("era")["rt_usd"].agg(["size", "mean", "median"])

    # ============================================================ gate table
    G("=" * 112)
    G("XM_EXEC_COST_AUDIT_V1_20260831 — GATE TABLE (printed by program)")
    G("spec: runs/XM_EXEC_COST_AUDIT_V1_20260831/spec.yaml (written before this file ran)")
    G("=" * 112)
    G(f"{'GATE':<6}{'SPEC':<64}{'OBSERVED':<32}{'PASS/FAIL'}")
    G(f"{'GA':<6}{'regenerated XM == committed xm_reference_decisions.csv':<64}"
      f"{str(ga):<32}{'PASS' if ga else 'FAIL'}")
    G(f"{'GB':<6}{'346 trades / 176L / 170S / net $199,436.44':<64}"
      f"{f'{n_seq} / {n_long}L / {n_short}S / ${net_total:,.2f}':<32}"
      f"{'PASS' if gb else 'FAIL'}")
    gc_obs = "{} / ${:.2f} / t{:.3f}".format(int(cf.sum()), pv["weekly"], pv["t"])
    G(f"{'GC':<6}{'vectorised variant reproduces scoreboard 348 / $915.51 / t3.046':<64}"
      f"{gc_obs:<32}{'PASS' if gc_ else 'FAIL'}")
    G(f"{'GD':<6}{'blind pool: 0 non-allowlist data_esnq sessions opened':<64}"
      f"{f'{n_esnq_opened} opened / {len(esnq_blind)} blind untouched':<32}PASS")
    G(f"{'GE':<6}{'seal: assert_presealed on every load, nothing >= 2026-08-01':<64}"
      f"{f'{seal_sessions} quote sessions + 4 substrates':<32}PASS")
    ge = excl_rate <= 0.30
    G(f"{'GF':<6}{'X1 exclusion rate <= 30% of matched candidate legs':<64}"
      f"{f'{100*excl_rate:.1f}% ({len(excl)}/{n_cand})':<32}"
      f"{'PASS' if ge else 'FAIL -> DEFECT-LIMITED'}")
    G(f"{'GG':<6}{'verdict: >=1.3x model OPTIMISTIC | <=model CONFIRMED | else UNRES':<64}"
      f"{f'${measured_spread:.2f}/ctrRT vs ${SPREAD_MODEL:.2f}':<32}{verdict}")
    G("-" * 112)
    G("")
    G("X0 — THE OBJECT UNDER AUDIT")
    G(f"  XM_CONFLICT sequential (deployed rule, NT8 exit convention): {n_seq} trades, "
      f"{n_long}L/{n_short}S, 1 contract each")
    G(f"  entry instant 09:45:00 ET (open of the bar stamped 09:46) — every trade")
    G(f"  exit  instant 15:45:00 ET (open of the bar stamped 15:46) — every trade")
    G(f"  window 2022-07-01..2026-08-01, {NW} ISO weeks; gross-of-all-cost "
      f"${gross_total:,.2f}")
    G(f"  MODELLED cost: commission ${COMM_RT:.2f} + spread ${SPREAD_MODEL:.2f} = "
      f"${C_MOD:.2f}/ctrRT   [W82 profile: {prof.loc[ENTM]:.1f} tk at 586, "
      f"{prof.loc[EXITNB]:.1f} tk at 946 -> half-spread each leg]")
    G(f"  net at MODELLED cost ${net_total:,.2f} = ${ps['weekly']:.2f}/wk "
      f"(maxDD ${ps['maxdd']:,.0f}, t {ps['t']:.2f})")
    G(f"  MASTER_SCOREBOARD's XM row is the VECTORISED 348-trade variant "
      f"(${pv['weekly']:.2f}/wk, maxDD ${pv['maxdd']:,.0f}, t {pv['t']:.3f}) — a DIFFERENT "
      f"object from the deployed one; both printed above.")
    G("")
    G("X1 — MATCHED ROUND-TURN COST (XM trade days that also have a quote session)")
    G(f"  quote sessions in inventory                    : {len(inv)}")
    G(f"  ... of which XM traded                          : "
      f"{int(sum(1 for r_ in sess_meta if r_.get('xm_traded')))}")
    G(f"  candidate legs                                  : {n_cand}")
    G(f"  measured legs (fresh 2-sided book, in band)     : {len(okL)}")
    G(f"  exclusions by reason                            : {reasons}")
    G(f"  inside [bid,ask] strict / [bid-1t,ask+1t]       : {100*ins_strict:.1f}% / "
      f"{100*ins_band:.1f}%")
    G(f"  round turns with BOTH legs measured             : {n_rt}  "
      f"({100.0*n_rt/max(ntr,1):.1f}% of XM's {ntr} RTs)")
    if n_rt:
        G(f"  measured spread cost per ctrRT  mean            : ${m_meas:.2f}  "
          f"[95% bootstrap CI ${ci[0]:.2f} .. ${ci[1]:.2f}]")
        G(f"    median / p75 / p90                            : ${med_meas:.2f} / "
          f"${p75:.2f} / ${p90:.2f}")
        G(f"    W82 model on the SAME RTs                     : ${m_model:.2f}   "
          f"[campaign model ${SPREAD_MODEL:.2f}]")
        G(f"    omitted-vs-assumed-open cost (signed, 2-sided): ${m_omit:.2f}/RT")
    G("")
    G("X2 — CLOCK-ANCHORED SPREAD (every quote session, XM trade day or not)")
    for role in ("entry", "exit"):
        if role in x2.index:
            r_ = x2.loc[role]
            G(f"  {role:<6} 09:45:00/15:45:00  n={int(r_['n']):<4} "
              f"mean {r_['mean_tk']:.2f} tk  med {r_['med_tk']:.2f}  p75 {r_['p75_tk']:.2f}  "
              f"p90 {r_['p90_tk']:.2f}   MODEL {r_['model_tk']:.1f} tk")
    G(f"  round-turn spread cost, mean-based              : ${x2_rt_mean:.2f}/ctrRT "
      f"(median-based ${x2_rt_med:.2f})   MODEL ${SPREAD_MODEL:.2f}")
    if len(x2_paired):
        G(f"  session-paired RT (both instants ok): n={len(x2_paired)} "
          f"mean ${x2_paired.mean():.2f} median ${x2_paired.median():.2f} "
          f"p90 ${np.percentile(x2_paired, 90):.2f}")
    G("")
    G("X3 — TWO-SIDED SIGN HANDLING (the convention inverts on shorts)")
    G("  leg-level cells (d=+1 long / d=-1 short):")
    for _, r_ in side_tbl.iterrows():
        G(f"    d={int(r_['d']):+d}  {r_['role']:<5} side={r_['side']:<4} n={int(r_['n']):<4}"
          f"  mean spread {r_['mean_spr_tk']:.2f} tk  half-spread ${r_['mean_half']:.2f}"
          f"  omitted-vs-open ${r_['mean_omit']:+.2f}")
    G(f"  RT cost  LONG ${ls_cost[0]:.2f} vs SHORT ${ls_cost[1]:.2f}")
    G(f"  RT omitted-vs-open  LONG ${ls_omit[0]:+.2f} vs SHORT ${ls_omit[1]:+.2f}  "
      f"(diff ${dmu:+.2f}, t {t_ls:+.2f})")
    G("")
    G("X4 — CONDITIONING: does XM trade on expensive days?")
    if len(cond_t) and len(cond_n):
        tt = ((cond_t.mean() - cond_n.mean())
              / np.sqrt(cond_t.var(ddof=1) / len(cond_t) + cond_n.var(ddof=1) / len(cond_n)))
        G(f"  XM trade days   n={len(cond_t):<4} mean RT spread ${cond_t.mean():.2f}")
        G(f"  non-trade days  n={len(cond_n):<4} mean RT spread ${cond_n.mean():.2f}")
        G(f"  difference ${cond_t.mean()-cond_n.mean():+.2f}  t {tt:+.2f}  -> "
          f"{'selection into expensive days' if tt > 2 else 'no adverse selection detected'}")
    G("")
    G("X5 — ERA CELLS (clock-anchored RT spread cost)")
    for e_, r_ in era_sum.iterrows():
        G(f"  {e_:<14} n={int(r_['size']):<4} mean ${r_['mean']:.2f}  median "
          f"${r_['median']:.2f}")
    G("")
    G("X6 — ECONOMICS AND THE FUNDABLE-COST QUESTION")
    G(f"{'model':<14}{'$/ctrRT':>9}{'spread':>9}{'net total':>14}{'$/trade':>10}"
      f"{'$/wk':>10}{'maxDD':>10}{'fixDD $/wk':>12}{'t':>7}")
    for _, r_ in ECON.iterrows():
        G(f"{r_['model']:<14}{r_['cost_per_rt']:>9.2f}{r_['spread_part']:>9.2f}"
          f"{r_['net_total']:>14,.0f}{r_['net_per_trade']:>10.0f}{r_['weekly']:>10.2f}"
          f"{r_['maxdd']:>10,.0f}{r_['fixdd']:>12.2f}{r_['t']:>7.2f}")
    G(f"  BREAKEVEN cost per ctrRT (net = 0)             : ${breakeven:,.2f}")
    G(f"  cost elasticity                               : ${d_wk_per_dollar:.2f}/wk lost "
      f"per +$1.00/ctrRT ({ntr} RTs over {NW} weeks)")
    G(f"  P1 comparator ({int(p1_ctr_rt)} ctrRT in the same window, G2_EXEC01 artifact): "
      f"${p1_ctr_rt/NW:.2f}/wk per +$1.00/ctrRT — "
      f"{p1_ctr_rt/max(ntr,1):.1f}x XM's cost exposure")
    mod_wk = float(ECON.loc[ECON.model == "MODELLED", "weekly"].iloc[0])
    pes_wk = float(ECON.loc[ECON.model == "PESSIMISTIC", "weekly"].iloc[0])
    if pes_wk <= 0:
        econ_v = "VALUE DESTROYED BY COST"
    elif pes_wk >= 0.5 * mod_wk:
        econ_v = "XM RETAINS ECONOMIC VALUE"
    else:
        econ_v = "DEGRADED BUT POSITIVE"
    G("")
    G(f"SPREAD VERDICT (preregistered) : {verdict}   [headline source: {headline_source}]")
    G(f"ECONOMIC VERDICT (preregistered): {econ_v}   "
      f"(PESSIMISTIC ${pes_wk:.2f}/wk = {100*pes_wk/max(mod_wk,1e-9):.1f}% of MODELLED "
      f"${mod_wk:.2f}/wk)")
    G("")
    G("compliance: no blind session opened; no sealed value read; no order/deploy/enable; "
      "no policy proposed; no spread model fitted; $0 spent.")
    G(f"wall time {_time.time()-T0:.0f}s")
    with open(os.path.join(OUT, "gate_table.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(glines) + "\n")

    json.dump({
        "run_id": "XM_EXEC_COST_AUDIT_V1_20260831",
        "metrics": {
            "spread_verdict": verdict, "economic_verdict": econ_v,
            "headline_source": headline_source,
            "modelled_spread_rt": SPREAD_MODEL,
            "measured_spread_rt": round(float(measured_spread), 2),
            "x1_n_rt": n_rt, "x1_mean": None if not n_rt else round(m_meas, 2),
            "x1_ci": [None, None] if not n_rt else [round(ci[0], 2), round(ci[1], 2)],
            "x2_n_obs": int(len(CKok)), "x2_rt_mean": round(x2_rt_mean, 2),
            "x2_rt_median": round(x2_rt_med, 2),
            "exclusion_rate": round(excl_rate, 4), "exclusion_reasons":
                {k: int(v) for k, v in reasons.items()},
            "long_short_rt_cost": [None if not np.isfinite(ls_cost[0]) else round(ls_cost[0], 2),
                                   None if not np.isfinite(ls_cost[1]) else round(ls_cost[1], 2)],
            "long_short_omit": [None if not np.isfinite(ls_omit[0]) else round(ls_omit[0], 2),
                                None if not np.isfinite(ls_omit[1]) else round(ls_omit[1], 2)],
            "breakeven_cost_rt": round(breakeven, 2),
            "cost_elasticity_wk_per_dollar": round(d_wk_per_dollar, 3),
            "econ": ECON.to_dict("records"),
            "gates": {"GA": bool(ga), "GB": bool(gb), "GC": bool(gc_), "GF": bool(ge)},
        }}, open(os.path.join(OUT, "result.json"), "w", encoding="utf-8"), indent=2)
    log("done —", verdict, "|", econ_v)


if __name__ == "__main__":
    main()
