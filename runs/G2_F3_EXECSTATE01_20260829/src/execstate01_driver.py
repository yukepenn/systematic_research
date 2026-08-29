"""G2_F3_EXECSTATE01_20260829 — TEAM EXECSTATE01 driver (ledger trial G00023).

Executes the frozen spec.yaml: second-of-minute effective-spread + 30s-markout profile
(primary gate: sec-0 AND sec-30 penalty >= 0.25 tick vs mid-minute), conditional
re-timing pricing of P1's frozen entries; secondaries: OFI->mid-move slope by
spread/depth state, matched-vol 10:00-vs-15:00 cost, fitted cost f(spread,depth,hour)
with divergence check vs the $25-33/RT all-in band.

All ambiguity resolutions frozen in out/spec_resolutions.txt (R1..R12) BEFORE this file
first ran. No parameter search. Gate tables printed by program. Writes ONLY under this
run's out/. Seal: every load through research_sdk.seal_guard.assert_presealed. Blind
pools: data_esnq opened ONLY via ALLOWLIST_DEV_44 AND pre-burn, enforcement printed.

REVISION NOTE (recorded, not hidden): the first execution of this file had a unit defect
in the P1 leg-instant computation only — np.datetime64(pd.Timestamp) yields MICROSECOND
resolution, so leg instants compared as us against ns event times and every leg excluded
as no_quote (n=0 in Secondary 3). Fixed by the explicit .astype("datetime64[ns]") cast
(the second-grid path always had it). The primary gate reads the quote grid only and is
UNCHANGED by this fix; no threshold, resolution, or parameter was altered.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import time as _time
from datetime import date as _date

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
RUN = os.path.join(ROOT, "runs", "G2_F3_EXECSTATE01_20260829")
OUT = os.path.join(RUN, "out")
os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, ROOT)

from research_sdk.seal_guard import assert_presealed                     # noqa: E402
from research_sdk.session_boundary import assert_not_locked_forward      # noqa: E402

T0 = _time.time()
TICK = 0.25
PV = 20.0                 # $/point  (run_we_w01.PV)
TICKV = 5.0               # $/tick
COMM_RT = 4.36            # $/ctrRT commission (charged separately everywhere)
STALE_NS = 5_000_000_000  # R2: 5 s per side
NS = 1_000_000_000
SEC_GRID = 82_800         # 18:00:00 -> 16:59:59 ET
BURN_FIRST = "20260531"   # R1: pre-burn = strictly before this session date
N_WEEKS = 213             # EXEC01 program-printed in-window ISO weeks (R6, reused)
BAND_LO, BAND_HI = 25.0, 33.0   # R9 all-in $/ctrRT band
EXEC01_OUT = os.path.join(ROOT, "runs", "G2_EXEC01_P1_EXECUTION_20260828", "out")
ESNQ_DIR = os.path.join(ROOT, "research", "data_esnq", "parquet", "NQ")
ALLOWLIST_PATH = os.path.join(ROOT, "research", "data_esnq", "ALLOWLIST_DEV_44.txt")
V2_DIR = os.path.join(ROOT, "research", "data_microstructure_v2", "raw", "NQ")


def log(*a):
    print(f"[{_time.time()-T0:6.0f}s]", *a, flush=True)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def session_open_ns(date8: str) -> int:
    """Naive-ET open instant (18:00:00 previous calendar day) of session date8."""
    d = pd.Timestamp(date8) - pd.Timedelta(days=1) + pd.Timedelta(hours=18)
    return int(np.datetime64(d).astype("datetime64[ns]").astype("int64"))


def load_session(path):
    tbl = pq.read_table(path, columns=["bip", "time", "price", "volume"])
    qt = tbl.column("time").to_numpy().astype("datetime64[ns]")
    qb = tbl.column("bip").to_numpy()
    qp = tbl.column("price").to_numpy()
    qv = tbl.column("volume").to_numpy().astype("float64")
    del tbl
    return qt, qb, qp, qv


def make_asof(bt, bp, bv, at, ap, av):
    def asof(instants_ns):
        ib = np.searchsorted(bt, instants_ns, side="right") - 1
        ia = np.searchsorted(at, instants_ns, side="right") - 1
        okb, oka = ib >= 0, ia >= 0
        ibc, iac = np.maximum(ib, 0), np.maximum(ia, 0)
        bpx = np.where(okb, bp[ibc], np.nan)
        apx = np.where(oka, ap[iac], np.nan)
        bsz = np.where(okb, bv[ibc], np.nan)
        asz = np.where(oka, av[iac], np.nan)
        ageb = np.where(okb, instants_ns - bt[ibc], np.int64(2 ** 62))
        agea = np.where(oka, instants_ns - at[iac], np.int64(2 ** 62))
        return bpx, apx, bsz, asz, ageb, agea
    return asof


def ofi_contrib(t_ns, p, q):
    """Per-event OFI contribution for one side stream (R7). Returns (times, contrib_bid_form).
    Caller negates/adjusts per side. First event skipped."""
    if len(t_ns) < 2:
        return t_ns[:0], np.zeros(0)
    p1, p0 = p[1:], p[:-1]
    q1, q0 = q[1:], q[:-1]
    up = (p1 >= p0).astype(np.float64)
    dn = (p1 <= p0).astype(np.float64)
    return t_ns[1:], up, dn, q1, q0


def main():
    glines = []

    def G(*a):
        s = " ".join(str(x) for x in a)
        glines.append(s)
        print(s, flush=True)

    # ---------------------------------------------------------------- reused artifacts
    log("Phase 0 — reused artifacts (read-only) + identity gates")
    p1_path = os.path.join(EXEC01_OUT, "p1_trades.csv")
    off_path = os.path.join(EXEC01_OUT, "session_offsets.csv")
    ms_path = os.path.join(EXEC01_OUT, "minute_samples.csv.gz")
    hashes = {os.path.basename(p): sha256(p) for p in (p1_path, off_path, ms_path)}

    TT = pd.read_csv(p1_path, dtype={"sess_date": str})
    assert_presealed(TT.assign(et_ts=pd.to_datetime(TT["et"])), "et_ts", "p1_trades et")
    assert_presealed(TT.assign(xt_ts=pd.to_datetime(TT["xt"])), "xt_ts", "p1_trades xt")
    ga = (len(TT) == 2401) and (int(TT["in_win"].sum()) == 2131)
    TIN = TT[TT["in_win"]].reset_index(drop=True)
    total_entry_ctr = int(TIN["u"].sum())
    log(f"p1_trades: {len(TT)} total / {int(TT['in_win'].sum())} in-window — GA={ga}; "
        f"in-window entry contracts {total_entry_ctr}")

    OFF = pd.read_csv(off_path, dtype={"date": str})
    off_map = {r["date"]: float(r["offset"]) for _, r in OFF.iterrows()
               if r["status"] == "ok" and np.isfinite(r["offset"])}

    # ---------------------------------------------------------------- inventory (R1)
    log("Phase 1 — inventory: v2 pre-burn + esnq (allowlist AND pre-burn); no v1")
    with open(ALLOWLIST_PATH, "r", encoding="utf-8") as f:
        allowlist = {ln.strip() for ln in f if ln.strip()}
    assert len(allowlist) == 44, "ALLOWLIST_DEV_44 does not have 44 entries"
    v2_all = {f[1:9] for f in os.listdir(V2_DIR) if f.endswith(".parquet")}
    esnq_all = {f[1:9] for f in os.listdir(ESNQ_DIR) if f.endswith(".parquet")}
    v2_dates = {d for d in v2_all if d < BURN_FIRST}
    esnq_ok = {d for d in (esnq_all & allowlist) if d < BURN_FIRST}
    inv = {}
    for d in sorted(v2_dates):
        inv[d] = ("v2", os.path.join(V2_DIR, f"s{d}.parquet"))
    n_esnq_used = 0
    for d in sorted(esnq_ok):
        if d not in inv:
            inv[d] = ("esnq", os.path.join(ESNQ_DIR, f"s{d}.parquet"))
            n_esnq_used += 1
    esnq_blind = sorted(esnq_all - allowlist)
    esnq_planned = sorted(d for d, (s, _) in inv.items() if s == "esnq")
    viol = [d for d in esnq_planned if d not in allowlist or d >= BURN_FIRST]
    burn_excluded = sorted([d for d in v2_all if d >= BURN_FIRST]
                           + [d for d in (esnq_all & allowlist) if d >= BURN_FIRST])
    print("=" * 100)
    print("BLIND-POOL / SCOPE ENFORCEMENT (printed before any quote-store open):")
    print(f"  ALLOWLIST_DEV_44 entries               : {len(allowlist)}")
    print(f"  esnq sessions on disk                  : {len(esnq_all)}")
    print(f"  esnq outside allowlist (BLIND)         : {len(esnq_blind)} — NONE opened")
    print(f"  esnq this run opens                    : {len(esnq_planned)} "
          f"(all allowlisted AND pre-burn: {'YES' if not viol else 'NO — ABORT'})")
    print(f"  burn-window sessions excluded (R1)     : {len(burn_excluded)} {burn_excluded}")
    print(f"  v1 scalping store                      : NOT OPENED (not in launch grant)")
    print("=" * 100)
    if viol:
        raise SystemExit("SCOPE VIOLATION — ABORT")
    max_date = max(inv)
    assert max_date < BURN_FIRST
    assert_not_locked_forward(_date(int(max_date[:4]), int(max_date[4:6]), int(max_date[6:])))
    log(f"inventory: {len(inv)} sessions (v2 {len(inv)-n_esnq_used} / esnq {n_esnq_used}); "
        f"max date {max_date}")

    # ---------------------------------------------------------------- per-session loop
    log(f"Phase 2 — per-session pass ({len(inv)} sessions, bounded memory)")
    nbin = np.zeros(60, dtype=np.int64)          # spread samples per sec bin
    sbin = np.zeros(60)                          # sum spread ticks
    s2bin = np.zeros(60)                         # sum spread^2
    hist = np.zeros((60, 402), dtype=np.int64)   # tick histogram, cap 400 + overflow
    mkn = np.zeros(60, dtype=np.int64)           # markout n
    mks = np.zeros(60)                           # sum drift ticks (buy-signed)
    mks2 = np.zeros(60)
    mksa = np.zeros(60)                          # sum |drift|
    sess_bin_n, sess_bin_s = [], []              # per-session 60-vectors (spread)
    sess_mk_n, sess_mk_s = [], []                # per-session 60-vectors (markout)
    ivals = []                                   # interval rows for OFI / fitted cost
    leg_rows = []                                # P1 fill legs (state measurement)
    n_valid_total = 0
    n_grid_total = 0
    seal_ok_sessions = 0
    usable_dates = []

    TIN_bydate = {d: g for d, g in TIN.groupby("sess_date")}

    for d in sorted(inv):
        store, path = inv[d]
        if store == "esnq":
            assert d in allowlist and d < BURN_FIRST, f"scope violation {d} — ABORT"
            print(f"  esnq open {d} (allowlisted+pre-burn: YES)", flush=True)
        qt, qb, qp, qv = load_session(path)
        assert_presealed(pd.DataFrame({"time": qt}), "time", f"quotes s{d} [{store}]")
        seal_ok_sessions += 1
        bm, am = qb == 1, qb == 2
        bt = qt[bm].astype("int64"); bp = qp[bm]; bv = qv[bm]
        at = qt[am].astype("int64"); ap = qp[am]; av = qv[am]
        del qt, qb, qp, qv
        if len(bt) == 0 or len(at) == 0:
            continue
        if np.any(np.diff(bt) < 0):
            o_ = np.argsort(bt, kind="stable"); bt, bp, bv = bt[o_], bp[o_], bv[o_]
        if np.any(np.diff(at) < 0):
            o_ = np.argsort(at, kind="stable"); at, ap, av = at[o_], ap[o_], av[o_]
        store_end = int(min(bt[-1], at[-1]))
        asof = make_asof(bt, bp, bv, at, ap, av)

        open_ns = session_open_ns(d)
        grid = open_ns + np.arange(SEC_GRID, dtype=np.int64) * NS
        bpx, apx, bsz, asz, ageb, agea = asof(grid)
        valid = ((ageb <= STALE_NS) & (agea <= STALE_NS) & (apx >= bpx)
                 & (grid <= store_end))
        spr = (apx - bpx) / TICK
        mid = (bpx + apx) / 2.0
        secs = np.tile(np.arange(60), SEC_GRID // 60)

        n_grid_total += SEC_GRID
        n_valid_total += int(valid.sum())
        if valid.sum() == 0:
            continue
        usable_dates.append(d)

        # per-bin spread accumulation
        v = valid
        nb = np.bincount(secs[v], minlength=60)
        sb = np.bincount(secs[v], weights=spr[v], minlength=60)
        nbin += nb; sbin += sb
        s2bin += np.bincount(secs[v], weights=spr[v] ** 2, minlength=60)
        tk = np.minimum(np.round(spr[v]).astype(np.int64), 401)
        np.add.at(hist, (secs[v], tk), 1)
        sess_bin_n.append(nb); sess_bin_s.append(sb)

        # markout: drift over +30 s, buy-signed (R5)
        vm = np.zeros(SEC_GRID, dtype=bool)
        vm[:-30] = valid[:-30] & valid[30:]
        drift = np.full(SEC_GRID, np.nan)
        drift[:-30] = (mid[30:] - mid[:-30]) / TICK
        mn = np.bincount(secs[vm], minlength=60)
        msum = np.bincount(secs[vm], weights=drift[vm], minlength=60)
        mkn += mn; mks += msum
        mks2 += np.bincount(secs[vm], weights=drift[vm] ** 2, minlength=60)
        mksa += np.bincount(secs[vm], weights=np.abs(drift[vm]), minlength=60)
        sess_mk_n.append(mn); sess_mk_s.append(msum)

        # OFI intervals (R7): 10 s non-overlapping, k = 0..8278
        K = SEC_GRID // 10 - 1
        st_idx = np.arange(K) * 10
        en_idx = st_idx + 10
        iv_valid = valid[st_idx] & valid[en_idx]
        ofi = np.zeros(K)
        for side, (tarr_, parr_, qarr_) in (("bid", (bt, bp, bv)), ("ask", (at, ap, av))):
            if len(tarr_) < 2:
                continue
            te, up, dn, q1, q0 = ofi_contrib(tarr_, parr_, qarr_)
            contrib = (q1 * up - q0 * dn) if side == "bid" else (q0 * up - q1 * dn)
            rel = te - open_ns
            k = (rel - 1) // (10 * NS)
            okk = (rel >= 1) & (k >= 0) & (k < K)
            ofi += np.bincount(k[okk].astype(np.int64), weights=contrib[okk], minlength=K)
        ivals.append(pd.DataFrame({
            "date": d, "hour": pd.DatetimeIndex(grid[st_idx]).hour,
            "spr_tk": spr[st_idx], "depth": bsz[st_idx] + asz[st_idx],
            "ofi": ofi, "mm_tk": (mid[en_idx] - mid[st_idx]) / TICK,
            "valid": iv_valid}))

        # P1 fill legs (state measurement; R6 band check with reused offset)
        if d in TIN_bydate:
            offset = off_map.get(d, np.nan)
            for _, x in TIN_bydate[d].iterrows():
                for role in ("entry", "exit"):
                    if role == "entry":
                        inst = int(np.datetime64(pd.Timestamp(x["et"])
                                                 - pd.Timedelta(seconds=60))
                                   .astype("datetime64[ns]").astype("int64"))
                        px = float(x["epx"]); side = "buy" if x["d"] > 0 else "sell"
                    else:
                        base = pd.Timestamp(x["xt"])
                        inst = int(np.datetime64(
                            base - pd.Timedelta(seconds=60) if x["xkind"] == "open" else base
                        ).astype("datetime64[ns]").astype("int64"))
                        px = float(x["xpx"]); side = "sell" if x["d"] > 0 else "buy"
                    b_, a_, bs_, as_, gb_, ga_ = asof(np.array([inst], dtype="int64"))
                    b_, a_ = float(b_[0]), float(a_[0])
                    status = "ok"
                    if not np.isfinite(offset):
                        status = "no_offset"
                    elif not np.isfinite(b_) or not np.isfinite(a_):
                        status = "no_quote"
                    elif int(gb_[0]) > STALE_NS or int(ga_[0]) > STALE_NS:
                        status = "stale_after_store_end" if inst > store_end else "stale"
                    elif a_ < b_:
                        status = "crossed"
                    else:
                        pxc = px - offset
                        if not (b_ - TICK - 1e-9 <= pxc <= a_ + TICK + 1e-9):
                            status = "outside_band"
                    leg_rows.append(dict(
                        tid=int(x["tid"]), date=d, role=role, side=side, u=int(x["u"]),
                        instant=inst, hour=pd.Timestamp(inst).hour,
                        spr_tk=((a_ - b_) / TICK if status == "ok" else np.nan),
                        depth=(float(bs_[0] + as_[0]) if status == "ok" else np.nan),
                        status=status))
        if len(usable_dates) % 20 == 0:
            log(f"  ... {len(usable_dates)} usable sessions")

    n_sess = len(usable_dates)
    valid_share = n_valid_total / max(n_grid_total, 1)
    log(f"Phase 2 done: {n_sess} usable sessions, valid share {100*valid_share:.1f}%")

    # ---------------------------------------------------------------- profile + gate
    log("Phase 3 — profile, MDE, primary gate")
    S = np.where(nbin > 0, sbin / np.maximum(nbin, 1), np.nan)
    n_non = nbin.sum() - nbin[0] - nbin[30]
    B = (sbin.sum() - sbin[0] - sbin[30]) / max(n_non, 1)
    P0, P30 = S[0] - B, S[30] - B

    # session-clustered penalties
    p0j, p30j = [], []
    for nb, sb in zip(sess_bin_n, sess_bin_s):
        nn = nb.sum() - nb[0] - nb[30]
        if nb[0] > 0 and nb[30] > 0 and nn > 0:
            bj = (sb.sum() - sb[0] - sb[30]) / nn
            p0j.append(sb[0] / nb[0] - bj)
            p30j.append(sb[30] / nb[30] - bj)
    p0j, p30j = np.array(p0j), np.array(p30j)
    se0 = p0j.std(ddof=1) / np.sqrt(len(p0j)) if len(p0j) > 1 else np.nan
    se30 = p30j.std(ddof=1) / np.sqrt(len(p30j)) if len(p30j) > 1 else np.nan
    mde0, mde30 = 1.96 * se0, 1.96 * se30

    # medians from histograms
    med = np.zeros(60)
    for s in range(60):
        cs = np.cumsum(hist[s]); tot = cs[-1]
        med[s] = float(np.searchsorted(cs, (tot + 1) // 2)) if tot else np.nan
    sd = np.sqrt(np.maximum(s2bin / np.maximum(nbin, 1) - S ** 2, 0))
    mdrift = mks / np.maximum(mkn, 1)
    mdrift_sd = np.sqrt(np.maximum(mks2 / np.maximum(mkn, 1) - mdrift ** 2, 0))
    mabs = mksa / np.maximum(mkn, 1)

    prof = pd.DataFrame({
        "sec": np.arange(60), "n_spread": nbin, "mean_spread_tk": S,
        "median_spread_tk": med, "sd_spread_tk": sd, "n_markout": mkn,
        "mean_markout30_buy_tk": mdrift, "sd_markout30_tk": mdrift_sd,
        "mean_abs_markout30_tk": mabs})
    prof.to_csv(os.path.join(OUT, "second_profile.csv"), index=False)

    s_star = int(np.nanargmin(S))
    ge = (n_sess >= 30) and (valid_share >= 0.50)
    gf = bool(ge and (P0 >= 0.25) and (P30 >= 0.25))

    # ---------------------------------------------------------------- OFI secondary
    log("Phase 4 — OFI->mid-move by spread/depth state (R7)")
    IV = pd.concat(ivals, ignore_index=True)
    IVv = IV[IV["valid"] & np.isfinite(IV["spr_tk"]) & np.isfinite(IV["depth"])
             & np.isfinite(IV["mm_tk"])].copy()
    s_edges = np.percentile(IVv["spr_tk"], [100 / 3, 200 / 3])
    d_edges = np.percentile(IVv["depth"], [100 / 3, 200 / 3])

    def ter(v, e):
        return np.where(v <= e[0], "T1", np.where(v <= e[1], "T2", "T3"))

    IVv["s_ter"] = ter(IVv["spr_tk"].to_numpy(), s_edges)
    IVv["d_ter"] = ter(IVv["depth"].to_numpy(), d_edges)
    ofi_rows = []
    for (st_, dt_), g in IVv.groupby(["s_ter", "d_ter"]):
        x, y = g["ofi"].to_numpy(), g["mm_tk"].to_numpy()
        vx = x.var(ddof=1)
        if len(g) < 30 or vx <= 0:
            continue
        slope = float(np.cov(x, y, ddof=1)[0, 1] / vx)
        resid = y - y.mean() - slope * (x - x.mean())
        se = float(np.sqrt(resid.var(ddof=2) / (vx * (len(g) - 1))))
        ofi_rows.append(dict(s_ter=st_, d_ter=dt_, n=len(g), slope_tk_per_ctr=slope,
                             se=se, t=slope / se if se > 0 else np.nan))
    OFI_T = pd.DataFrame(ofi_rows)
    OFI_T.to_csv(os.path.join(OUT, "ofi_state_slope.csv"), index=False)

    # ---------------------------------------------------------------- fitted cost (R9)
    log("Phase 5 — fitted cost f(spread_state, depth_state, hour) + divergence")
    IVv["half_usd"] = IVv["spr_tk"] * TICKV / 2.0
    cell = IVv.groupby(["s_ter", "d_ter", "hour"])["half_usd"].agg(["mean", "count"])
    cell_sh = IVv.groupby(["s_ter", "hour"])["half_usd"].mean()
    cell_h = IVv.groupby(["hour"])["half_usd"].mean()
    g_mean = float(IVv["half_usd"].mean())
    cell.reset_index().to_csv(os.path.join(OUT, "fitted_cost_cells.csv"), index=False)

    LEG = pd.DataFrame(leg_rows)
    n_cand_legs = len(LEG)
    okL = LEG[LEG["status"] == "ok"].copy()
    fb_counts = {"cell": 0, "s_hour": 0, "hour": 0, "global": 0}

    def f_pred(row):
        st_ = ("T1" if row["spr_tk"] <= s_edges[0]
               else "T2" if row["spr_tk"] <= s_edges[1] else "T3")
        dt_ = ("T1" if row["depth"] <= d_edges[0]
               else "T2" if row["depth"] <= d_edges[1] else "T3")
        key = (st_, dt_, row["hour"])
        if key in cell.index and cell.loc[key, "count"] >= 10:
            fb_counts["cell"] += 1
            return float(cell.loc[key, "mean"])
        if (st_, row["hour"]) in cell_sh.index:
            fb_counts["s_hour"] += 1
            return float(cell_sh.loc[(st_, row["hour"])])
        if row["hour"] in cell_h.index:
            fb_counts["hour"] += 1
            return float(cell_h.loc[row["hour"]])
        fb_counts["global"] += 1
        return g_mean

    fitted_cw = div = np.nan
    n_rt_eval = n_rt_ctr = 0
    meas_cw = np.nan
    if len(okL):
        okL["pred_half"] = okL.apply(f_pred, axis=1)
        rts = []
        for tid, g in okL.groupby("tid"):
            if set(g["role"]) == {"entry", "exit"}:
                rts.append(dict(u=int(g["u"].iloc[0]),
                                pred=float(g["pred_half"].sum()) + COMM_RT,
                                meas=float(g["spr_tk"].sum()) * TICKV / 2.0 + COMM_RT))
        RT = pd.DataFrame(rts)
        if len(RT):
            n_rt_eval = len(RT); n_rt_ctr = int(RT["u"].sum())
            fitted_cw = float(np.average(RT["pred"], weights=RT["u"]))
            meas_cw = float(np.average(RT["meas"], weights=RT["u"]))
            if BAND_LO <= fitted_cw <= BAND_HI:
                div = 0.0
            elif fitted_cw < BAND_LO:
                div = (BAND_LO - fitted_cw) / BAND_LO
            else:
                div = (fitted_cw - BAND_HI) / BAND_HI
    revision_flag = bool(np.isfinite(div) and div > 0.20)

    # ---------------------------------------------------------------- matched vol (R8)
    log("Phase 6 — matched-vol 10:00 vs 15:00 (reused minute samples, scope-filtered)")
    MS = pd.read_csv(ms_path, dtype={"date": str})
    assert_presealed(MS.assign(ds=MS["date"]), "ds", "minute_samples dates")
    MS = MS[MS["date"].isin(set(inv))]
    M10 = MS[(MS["hour"] == 10) & np.isfinite(MS["vol"])]
    M15 = MS[(MS["hour"] == 15) & np.isfinite(MS["vol"])]
    naive_diff = float(M15["spr_tk"].mean() - M10["spr_tk"].mean())
    pool = np.concatenate([M10["vol"], M15["vol"]])
    dec = np.percentile(pool, np.arange(10, 100, 10))
    rows_mv = []
    wsum = dsum = 0.0
    for k in range(10):
        lo = -np.inf if k == 0 else dec[k - 1]
        hi = np.inf if k == 9 else dec[k]
        a = M10[(M10["vol"] > lo) & (M10["vol"] <= hi)]
        b = M15[(M15["vol"] > lo) & (M15["vol"] <= hi)]
        if len(a) and len(b):
            w = min(len(a), len(b))
            diff = float(b["spr_tk"].mean() - a["spr_tk"].mean())
            wsum += w; dsum += w * diff
            rows_mv.append(dict(decile=k + 1, n10=len(a), n15=len(b),
                                mean10_tk=float(a["spr_tk"].mean()),
                                mean15_tk=float(b["spr_tk"].mean()), diff_tk=diff))
    matched_diff = dsum / wsum if wsum else np.nan
    pd.DataFrame(rows_mv).to_csv(os.path.join(OUT, "matched_vol_10_15.csv"), index=False)

    # ---------------------------------------------------------------- re-timing (R6)
    log("Phase 7 — re-timing pricing (only if primary gate PASS)")
    rt_lines = [f"G2_F3_EXECSTATE01_20260829 — re-timing saving (printed by program)",
                f"cheapest in-minute offset on frozen 60-bin profile: sec-{s_star} "
                f"(S={S[s_star]:.3f} tk vs S(0)={S[0]:.3f} tk)"]
    saving_wk = save_per_ctr = save_se = np.nan
    n_saved_legs = 0
    if gf:
        ent = okL[okL["role"] == "entry"]
        savings, weights, sess_of = [], [], []
        for d, gg in ent.groupby("date"):
            store, path = inv[d]
            qt, qb, qp, qv = load_session(path)
            assert_presealed(pd.DataFrame({"time": qt}), "time", f"retime s{d} [{store}]")
            bm, am = qb == 1, qb == 2
            bt = qt[bm].astype("int64"); bp = qp[bm]; bv = qv[bm]
            at = qt[am].astype("int64"); ap = qp[am]; av = qv[am]
            del qt, qb, qp, qv
            store_end = int(min(bt[-1], at[-1]))
            asof = make_asof(bt, bp, bv, at, ap, av)
            for _, x in gg.iterrows():
                t0 = int(x["instant"]); t1 = t0 + s_star * NS
                b0, a0, _, _, g0b, g0a = asof(np.array([t0], dtype="int64"))
                b1, a1, _, _, g1b, g1a = asof(np.array([t1], dtype="int64"))
                ok0 = (np.isfinite(b0[0]) and np.isfinite(a0[0]) and int(g0b[0]) <= STALE_NS
                       and int(g0a[0]) <= STALE_NS and a0[0] >= b0[0])
                ok1 = (np.isfinite(b1[0]) and np.isfinite(a1[0]) and int(g1b[0]) <= STALE_NS
                       and int(g1a[0]) <= STALE_NS and a1[0] >= b1[0] and t1 <= store_end)
                if not (ok0 and ok1):
                    continue
                sv = (float(a0[0] - a1[0]) if x["side"] == "buy"
                      else float(b1[0] - b0[0])) * PV
                savings.append(sv); weights.append(int(x["u"])); sess_of.append(d)
        savings = np.array(savings); weights = np.array(weights, dtype=float)
        n_saved_legs = len(savings)
        if n_saved_legs >= 2:
            save_per_ctr = float(np.average(savings, weights=weights))
            sd_ = float(np.sqrt(np.average((savings - save_per_ctr) ** 2, weights=weights)))
            save_se = sd_ / np.sqrt(n_saved_legs)
            saving_wk = save_per_ctr * total_entry_ctr / N_WEEKS
        rt_lines += [
            f"gate PASS -> priced. measured entry legs: {n_saved_legs} "
            f"(of {len(ent)} ok entries in scope)",
            f"saving per entry contract (marketable, quote-to-quote): "
            f"${save_per_ctr:+.2f} (SE ${save_se:.2f})",
            f"profile-implied half-spread saving: "
            f"{(S[0]-S[s_star])/2:.3f} tk = ${(S[0]-S[s_star])/2*TICKV:.2f}/leg-ctr",
            f"extrapolated to frozen action set: {total_entry_ctr} in-window entry "
            f"contracts / {N_WEEKS} ISO wks -> ${saving_wk:+.2f}/wk",
            "STATUS: MODEL row (status_rule) — not a measurement until validated "
            "against the 2026-09-01 shadow; does not enter any scoreboard."]
    else:
        rt_lines += [
            "PRIMARY GATE FAILED (boundary-second penalty < 0.25 tick) — per spec, "
            "re-timing is NOT priced. A FAIL is a FAIL.",
            f"informational: P0={P0:+.4f} tk, P30={P30:+.4f} tk, threshold +0.25 tk."]
    with open(os.path.join(OUT, "retiming_saving.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(rt_lines) + "\n")

    # ---------------------------------------------------------------- gate table
    G("=" * 108)
    G("G2_F3_EXECSTATE01_20260829 — GATE TABLE (printed by program; trial G00023)")
    G("spec: runs/G2_F3_EXECSTATE01_20260829/spec.yaml (frozen); resolutions R1-R12")
    G("reused artifacts sha256: " + "  ".join(f"{k}={v[:16]}" for k, v in hashes.items()))
    G("=" * 108)
    G("EVENT COUNTS AND MDEs (printed BEFORE verdicts, launch rule 7):")
    G(f"  usable quote sessions {n_sess} (v2 {len(inv)-n_esnq_used} / esnq {n_esnq_used} "
      f"/ v1 0); grid instants {n_grid_total:,}; valid {n_valid_total:,} "
      f"({100*valid_share:.1f}%)")
    G(f"  sec-0 samples {nbin[0]:,} | sec-30 samples {nbin[30]:,} | mid-minute samples "
      f"{n_non:,}; markout samples {mkn.sum():,}")
    G(f"  session-clustered MDE(95%): sec-0 {mde0:.4f} tk | sec-30 {mde30:.4f} tk "
      f"(threshold 0.25 tk; {len(p0j)} cluster sessions)")
    G("-" * 108)
    G(f"{'GATE':<6}{'SPEC':<62}{'OBSERVED':<30}{'PASS/FAIL'}")
    G(f"{'GA':<6}{'P1 frozen stream identity: 2401 total / 2131 in-window':<62}"
      f"{f'{len(TT)} / {int(TT.in_win.sum())}':<30}{'PASS' if ga else 'FAIL -> DEFECT'}")
    gb_ok = not viol and n_esnq_used <= 44
    G(f"{'GB':<6}{'esnq via ALLOWLIST_DEV_44 AND pre-burn only; 0 blind':<62}"
      f"{f'{n_esnq_used} opened / {len(esnq_blind)} blind untouched':<30}"
      f"{'PASS' if gb_ok else 'FAIL'}")
    G(f"{'GC':<6}{'seal: every load assert_presealed, no value >= 2026-08-01':<62}"
      f"{f'{seal_ok_sessions} quote loads + 3 reused artifacts':<30}PASS")
    G(f"{'GD':<6}{'scope: all sessions pre-burn (< 2026-05-31); no v1 store':<62}"
      f"{f'max session {max_date}':<30}{'PASS' if max_date < BURN_FIRST else 'FAIL'}")
    G(f"{'GE':<6}{'sufficiency: >=30 usable sessions AND valid share >=50% (R10)':<62}"
      f"{f'{n_sess} sess / {100*valid_share:.1f}%':<30}"
      f"{'PASS' if ge else 'FAIL -> DEFECT-LIMITED'}")
    G(f"{'GF':<6}{'PRIMARY: penalty(sec-0) AND penalty(sec-30) >= 0.25 tk (R4)':<62}"
      f"{f'P0={P0:+.4f} P30={P30:+.4f} tk':<30}{'PASS' if gf else 'FAIL'}")
    G("-" * 108)
    G("")
    G("SECOND-OF-MINUTE PROFILE (second_profile.csv; pooled means, ticks)")
    G(f"  S(0)={S[0]:.4f}  S(30)={S[30]:.4f}  mid-minute baseline B={B:.4f}")
    G(f"  penalties: P0={P0:+.4f} (SE {se0:.4f})  P30={P30:+.4f} (SE {se30:.4f})")
    top5 = np.argsort(-S)[:5]
    G(f"  5 most expensive seconds: " + "  ".join(f"s{int(s)}={S[s]:.3f}" for s in top5))
    G(f"  cheapest second: s{s_star}={S[s_star]:.4f}  (profile grid only, no search)")
    G(f"  markout(+30s, buy-signed) at sec-0: {mdrift[0]:+.4f} tk  sec-30: "
      f"{mdrift[30]:+.4f} tk  grand mean: {mks.sum()/max(mkn.sum(),1):+.4f} tk")
    G("")
    G("SECONDARY 1 — OFI -> mid-move slope by spread/depth tercile (ofi_state_slope.csv)")
    G(f"  interval samples (10 s, valid both ends): {len(IVv):,}; spread edges "
      f"{s_edges[0]:.2f}/{s_edges[1]:.2f} tk; depth edges {d_edges[0]:.1f}/{d_edges[1]:.1f} ctr")
    for _, r in OFI_T.iterrows():
        G(f"    {r['s_ter']}xD{r['d_ter'][1]}: slope {r['slope_tk_per_ctr']:+.5f} tk/ctr "
          f"(t={r['t']:+.1f}, n={int(r['n']):,})")
    G("")
    G("SECONDARY 2 — matched-vol 10:00 vs 15:00 quoted-spread cost (matched_vol_10_15.csv)")
    G(f"  n10={len(M10):,} n15={len(M15):,}; naive diff (15h-10h) {naive_diff:+.3f} tk; "
      f"MATCHED diff {matched_diff:+.3f} tk ({matched_diff*TICKV/2:+.2f} $/leg-ctr)")
    G("")
    G("SECONDARY 3 — fitted cost f(spread,depth,hour) vs $25-33/RT all-in band (R9)")
    G(f"  P1 RTs evaluated (both legs state-measured): {n_rt_eval} trades / {n_rt_ctr} ctrRT"
      f" of {n_cand_legs//2} in-scope trades; leg exclusions "
      f"{LEG['status'].value_counts().to_dict()}")
    G(f"  fallback usage: {fb_counts}")
    G(f"  fitted all-in cost (cw): ${fitted_cw:.2f}/ctrRT   measured-in-scope all-in "
      f"(same RTs): ${meas_cw:.2f}/ctrRT")
    G(f"  band [$25,$33] (EXEC01 pooled $20.65+comm to worst-era $28.69+comm); "
      f"divergence {100*div:.1f}% -> "
      f"{'COST-MODEL REVISION FLAGGED' if revision_flag else 'within tolerance'}")
    G("")
    verdict = ("DEFECT" if not ga else
               "DEFECT-LIMITED" if not ge else
               "BOUNDARY PENALTY CONFIRMED" if gf else "NO HARVESTABLE BOUNDARY PENALTY")
    G(f"VERDICT (preregistered): {verdict}")
    if gf:
        G(f"  re-timed saving ${saving_wk:+.2f}/wk = MODEL row until 2026-09-01 shadow "
          f"validation (status_rule) — never a measurement before that.")
    G("")
    G("prohibition compliance: no strategy signal; no entry-rule change beyond the priced "
      "re-timing simulation; offsets only from the frozen 60-bin profile; no sealed read; "
      "blind pools untouched; SEARCH_LEDGER not appended; no git; no CrossTrade; $0.")
    wall = _time.time() - T0
    G(f"wall time: {wall:.0f} s")
    with open(os.path.join(OUT, "gate_table.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(glines) + "\n")

    result = ("DEFECT" if verdict in ("DEFECT", "DEFECT-LIMITED")
              else "PASS" if gf else "NULL")
    payload = {
        "trial_id": "G00023",
        "metrics": {
            "verdict": verdict,
            "n_sessions": n_sess, "valid_share": round(valid_share, 4),
            "sec0_samples": int(nbin[0]), "sec30_samples": int(nbin[30]),
            "S0_tk": round(float(S[0]), 4), "S30_tk": round(float(S[30]), 4),
            "baseline_tk": round(float(B), 4),
            "penalty_sec0_tk": round(float(P0), 4),
            "penalty_sec30_tk": round(float(P30), 4),
            "se0_clustered": round(float(se0), 4), "se30_clustered": round(float(se30), 4),
            "mde95_sec0_tk": round(float(mde0), 4), "mde95_sec30_tk": round(float(mde30), 4),
            "cheapest_second": s_star,
            "markout30_sec0_buy_tk": round(float(mdrift[0]), 4),
            "retiming_saving_per_wk": (round(saving_wk, 2) if np.isfinite(saving_wk)
                                       else None),
            "retiming_status": ("MODEL_ROW_PENDING_SHADOW" if gf else "NOT_PRICED_GATE_FAIL"),
            "matched_vol_15_minus_10_tk": round(matched_diff, 3),
            "fitted_cost_all_in": (round(fitted_cw, 2) if np.isfinite(fitted_cw) else None),
            "band_divergence_pct": (round(100 * div, 1) if np.isfinite(div) else None),
            "cost_model_revision_flag": revision_flag,
            "n_rt_state_evaluated": n_rt_eval,
            "wall_s": round(wall),
        },
        "result": result,
        "note": (f"MC-47 within-minute execution timing. Preregistered gate: sec-0 AND "
                 f"sec-30 spread penalty >= 0.25 tk vs mid-minute -> {verdict}. "
                 f"P0={P0:+.3f} tk, P30={P30:+.3f} tk (MDE95 {mde0:.3f}/{mde30:.3f} tk, "
                 f"{n_sess} pre-burn sessions). "
                 + (f"Re-timed entry saving ${saving_wk:+.2f}/wk is a MODEL row pending "
                    f"the 2026-09-01 shadow." if gf else
                    "Re-timing not priced (gate FAIL). ")
                 + (" COST-MODEL REVISION flagged." if revision_flag else "")),
    }
    with open(os.path.join(OUT, "ledger_result_pending.json"), "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    log("ledger_result_pending.json written —", result, "|", verdict)


if __name__ == "__main__":
    main()
