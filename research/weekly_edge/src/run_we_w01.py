"""WE_W01 (spec preregistered, commit 4ad8663): the 1-min NQ sleeve map.

Engines are imported UNCHANGED from campaigns #1/#6; the only new code is (a) the faithful
1-min port of Product B's decision stack (transcribed from SolarWaveOneContractNQ_v5.cs,
lines 150-445, read 2026-08-25), (b) weekly book-keeping, (c) fixed portfolios + weekly
loss-limit overlay. Dev 2022-01-02 18:00 -> 2026-05-29 17:00; holdout 2026-05-31 -> 07-31,
read once at the end. Nothing >= 2026-08-01 exists in the input file.
"""
from __future__ import annotations

import os
import sys
import time as _time

import numpy as np
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
sys.path.insert(0, os.path.join(ROOT, "research", "original_trader_reconstruction",
                                "solar_family", "src"))
sys.path.insert(0, os.path.join(ROOT, "research", "original_trader_reconstruction",
                                "vwap_flux_family", "src"))
from solarwave import SolarWaveParams                                   # noqa: E402
import inverse_core as IC                                               # noqa: E402
from run_r13_strict_master import run_master                            # noqa: E402
from run_r30c_exitfamilies import layer_b_exit                          # noqa: E402
from run_r32_joint import layer_a_v2                                    # noqa: E402
from run_r7_signal_id import ema, trend_states                          # noqa: E402
from vf_core import vf_levels                                           # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W01_SLEEVE_MAP", "out")
os.makedirs(OUT, exist_ok=True)
PV = 20.0
COMM_RT = 4.36
STRESS_RT = 10.0          # 2 NQ ticks on top of commission -> C1 line ($14.36/RT all-in)
DEV_END = pd.Timestamp("2026-05-29").date()

# ------------------------------------------------------------------ data / sessions / weeks
def load():
    df = pd.read_parquet(os.path.join(ROOT, "runs", "SM1M_SUBSTRATE", "out",
                                      "nq_1m_2022_2026.parquet"))
    df["time"] = pd.to_datetime(df["time"])
    df = df.sort_values("time").reset_index(drop=True)
    t = df["time"].values.astype("datetime64[s]")
    o, h, l, c = (df[k].values.astype(float) for k in ("open", "high", "low", "close"))
    v = df["volume"].values.astype(float)
    n = len(df)
    fb = np.zeros(n, bool); fb[0] = True
    fb[1:] = np.diff(t).astype("timedelta64[m]").astype(np.int64) > 60
    lb = np.zeros(n, bool); lb[:-1] = fb[1:]; lb[-1] = True
    sid = np.cumsum(fb) - 1
    n_sess = sid[-1] + 1
    last_of = np.zeros(n_sess, np.int64)
    last_of[sid[lb]] = np.nonzero(lb)[0]
    sess_end = t[last_of] + np.timedelta64(60, "s")        # bar-END stamps; close = last+1min
    sess_date = sess_end.astype("datetime64[D]")
    iso = pd.Series(pd.to_datetime(sess_date)).dt.isocalendar()
    week_of_sess = (iso["year"].astype(str) + "-W" + iso["week"].astype(str).str.zfill(2)).values
    return dict(df=df, t=t, o=o, h=h, l=l, c=c, v=v, n=n, fb=fb, lb=lb, sid=sid,
                n_sess=n_sess, sess_end=sess_end, sess_date=sess_date, wk=week_of_sess)


def week_table(trades, D, tkey):
    """trades -> per-session {net, n}; sessions -> weeks. tkey gives each trade's exit time."""
    per_s = {}
    tarr = D["t"]
    for x in trades:
        ts = np.datetime64(tkey(x))
        i = int(np.searchsorted(tarr, ts))
        i = min(i, D["n"] - 1)
        s = int(D["sid"][i])
        a = per_s.setdefault(s, [0.0, 0])
        a[0] += x["pnl"]; a[1] += 1
    return per_s


# ------------------------------------------------------------------ S4/S5: Product B 1-min port
def round_away(x):
    return int(np.floor(x + 0.5)) if x >= 0 else int(np.ceil(x - 0.5))


def sm14_1m(D, vol_period, with_solar=True, with_bmom=True):
    """Faithful port of SolarWaveOneContractNQ_v5 decision stack to 1-min bars.

    Declared port choices (spec): B-MOM reset at bar-end 09:31, signal cutoff 15:54, flatten
    15:57; VolPeriod counted in 1-min bars. Returns (trades, legs) with next-bar-open fills.
    """
    t, o, c, v = D["t"], D["o"], D["c"], D["v"]
    fb, lb, sid, n = D["fb"], D["lb"], D["sid"], D["n"]
    sess_end = D["sess_end"]
    TICK = 0.25
    VOLM = [6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30]
    NMEM = 13
    SMIN, SMAX, STOPM = 40 * TICK, 1200 * TICK, 179 * TICK
    hm = ((t - t.astype("datetime64[D]")).astype("timedelta64[s]").astype(np.int64))
    hhmmss = (hm // 3600) * 10000 + ((hm // 60) % 60) * 100          # bar-END hhmmss*? end-stamped

    vol_sum, vol_cnt, prev_close = 0.0, 0, np.nan
    diffs = []                                                        # rolling |dClose| buffer
    m_up = [False] * NMEM; m_anchor = [0.0] * NMEM; m_S = [STOPM] * NMEM
    m_sig = [0] * NMEM; m_pos = [0] * NMEM; m_pend = [0] * NMEM
    initialized = False
    sess_closes = []; tilt = 0
    bmom = 0; rth_open = False; open0930 = 0.0; vpv = 0.0; vv = 0.0
    today_slots = {}; slot_hist = {}; rth_days = 0

    def sigma():
        return (vol_sum / vol_cnt) if vol_cnt >= 30 else np.nan

    def resolve_s(mult):
        sg = sigma()
        if np.isnan(sg) or sg <= 0:
            return STOPM
        return min(max(mult * sg, SMIN), SMAX)

    tgt_arr = np.zeros(n, np.int8)                                    # decision at bar close
    for i in range(n):
        px = c[i]
        # apply pending
        for m in range(NMEM):
            m_pos[m] = m_pend[m]
        # UpdateVol
        if not np.isnan(prev_close):
            d = abs(px - prev_close)
            vol_sum += d; vol_cnt += 1; diffs.append(d)
            if vol_cnt > vol_period:
                diffs = diffs[-vol_period:]
                vol_sum = float(sum(diffs)); vol_cnt = len(diffs)
        prev_close = px
        # UpdateMachine
        for m in range(NMEM):
            m_sig[m] = 0
            if not initialized:
                m_up[m] = False; m_anchor[m] = px; m_S[m] = resolve_s(VOLM[m])
                continue
            if m_up[m]:
                if px >= m_anchor[m]:
                    m_anchor[m] = px
                elif px < m_anchor[m] - m_S[m]:
                    m_up[m] = False; m_S[m] = resolve_s(VOLM[m]); m_anchor[m] = px; m_sig[m] = -1
            else:
                if px <= m_anchor[m]:
                    m_anchor[m] = px
                elif px > m_anchor[m] + m_S[m]:
                    m_up[m] = True; m_S[m] = resolve_s(VOLM[m]); m_anchor[m] = px; m_sig[m] = 1
        if not initialized:
            initialized = True
        # Decide
        for m in range(NMEM):
            if i < 20:
                m_pend[m] = m_pos[m]; continue
            xl = m_anchor[m] - m_S[m] if m_up[m] else m_anchor[m] + m_S[m]
            if m_pos[m] > 0 and px <= xl:
                m_pend[m] = 0
            elif m_pos[m] < 0 and px >= xl:
                m_pend[m] = 0
            elif m_pos[m] != 0:
                m_pend[m] = m_pos[m]
            else:
                m_pend[m] = m_sig[m]
        # BmomBar
        se = bool(lb[i]); hmv = int(hhmmss[i])
        if hmv == 93100:
            open0930 = o[i]; vpv = 0.0; vv = 0.0; rth_open = True
            today_slots = {}; bmom = 0
        if rth_open and 93100 <= hmv <= 160000:
            vpv += px * v[i]; vv += v[i]
            vwap = vpv / vv if vv > 0 else px
            today_slots[hmv] = abs(px - open0930)
            if hmv <= 155400 and rth_days >= 14:
                past = slot_hist.get(hmv)
                if past:
                    k = min(14, len(past))
                    mtod = sum(past[-k:]) / k
                    s = 0
                    if px > max(open0930 + mtod, vwap):
                        s = 1
                    elif px < min(open0930 - mtod, vwap):
                        s = -1
                    if s != 0:
                        bmom = s
            if hmv >= 155700 or se:
                bmom = 0
        if se and rth_open:
            for kslot, val in today_slots.items():
                lst = slot_hist.setdefault(kslot, [])
                lst.append(val)
                if len(lst) > 60:
                    lst.pop(0)
            rth_days += 1; rth_open = False
        # session end: zero members, tilt
        if se:
            for m in range(NMEM):
                m_pos[m] = 0; m_pend[m] = 0
            sess_closes.append(px)
            if len(sess_closes) > 50:
                tilt = int(np.sign(px - float(np.mean(sess_closes[-50:]))))
            if len(sess_closes) > 600:
                sess_closes.pop(0)
        # combiner
        sum_next = sum(m_pend) if with_solar else 0
        T = max(-10, min(10, round_away(sum_next / 13.0 * 10.0)))
        mm = 1.25 if (sum_next != 0 and tilt != 0 and np.sign(sum_next) == tilt) else 1.0
        Tp = max(-13, min(13, round_away(T * mm * 0.9026)))
        M = (0.7086 * Tp if with_solar else 0.0) + (2.83 * bmom if with_bmom else 0.0)
        # hysteresis on current physical target (fills applied next bar; decision uses tgt path)
        p = tgt_arr[i - 1] if i > 0 and not fb[i] else 0
        tgt = p
        blocked = t[i] >= sess_end[sid[i]] - np.timedelta64(30 * 60, "s")
        flat = t[i] >= sess_end[sid[i]] - np.timedelta64(21 * 60, "s")
        if not with_solar and with_bmom:
            # amendment_2: S5 per spec is the B-MOM leg as a DIRECT +-1 position (2.83*bmom
            # can never cross the 3.0 hysteresis entry level, so routing it through the
            # hysteresis was an implementation error that produced zero trades).
            tgt_arr[i] = 0 if flat else bmom
            continue
        if flat:
            tgt = 0
        elif p == 0:
            if not blocked:
                if M >= 3.0:
                    tgt = 1
                elif M <= -3.0:
                    tgt = -1
        elif p > 0:
            if M <= -3.0 and not blocked:
                tgt = -1
            elif M <= 1.0:
                tgt = 0
        else:
            if M >= 3.0 and not blocked:
                tgt = 1
            elif M >= -1.0:
                tgt = 0
        tgt_arr[i] = tgt

    # fills: decision at bar i -> position over bar i+1..; entry/exit at next bar open
    trades = []
    pos = 0; epx = 0.0; eti = -1
    for i in range(n):
        want = int(tgt_arr[i - 1]) if i > 0 and not fb[i] else 0
        if want != pos:
            if pos != 0:
                trades.append(dict(d=pos, et=str(t[eti]), xt=str(t[i]),
                                   pnl=pos * (o[i] - epx) * PV - COMM_RT))
            pos = want
            if pos != 0:
                epx, eti = o[i], i
        if lb[i] and pos != 0:                                        # engine backstop
            trades.append(dict(d=pos, et=str(t[eti]), xt=str(t[i]),
                               pnl=pos * (c[i] - epx) * PV - COMM_RT))
            pos = 0
    return trades


# ------------------------------------------------------------------ metrics
def summarize(per_s, D, which, n_tr_key=1):
    rows = {}
    for s, (net, ntr) in per_s.items():
        d = D["sess_date"][s].astype(object)
        if which == "dev" and d > DEV_END:
            continue
        if which == "hold" and d <= DEV_END:
            continue
        w = D["wk"][s]
        r = rows.setdefault(w, [0.0, 0])
        r[0] += net; r[1] += ntr
    if not rows:
        return None
    wk = sorted(rows)
    net = np.array([rows[w][0] for w in wk])
    ntr = np.array([rows[w][1] for w in wk])
    eq = np.cumsum(net)
    dd = float((eq - np.maximum.accumulate(np.concatenate([[0.0], eq]))[1:]).min())
    return dict(weeks=len(wk), mean=float(net.mean()), median=float(np.median(net)),
                pos=float((net > 0).mean() * 100), worst=float(net.min()),
                best=float(net.max()),
                sharpe=float(net.mean() / net.std(ddof=1)) if len(net) > 1 else np.nan,
                maxdd=dd, tpw=float(ntr.mean()),
                per_trade=float(net.sum() / ntr.sum()) if ntr.sum() else np.nan,
                total=float(net.sum()), _wk=wk, _net=net, _ntr=ntr)


def main():
    t0 = _time.time()
    D = load()
    print(f"bars {D['n']:,}  sessions {D['n_sess']:,}  "
          f"{D['t'][0]} -> {D['t'][-1]}   [{_time.time()-t0:.0f}s]", flush=True)

    seg = D["df"]
    bb = IC.prepare(seg, SolarWaveParams())
    print(f"solar signals ready [{_time.time()-t0:.0f}s]", flush=True)

    members = {}          # name -> per-session table

    # ---- S1 + harness check ------------------------------------------------------------
    sub = seg[(seg["time"] >= "2023-01-02 18:00") & (seg["time"] <= "2025-02-01 17:00")]
    bb23 = IC.prepare(sub.reset_index(drop=True), SolarWaveParams())
    tr23 = run_master(bb23, exit_strict=False, gate=True, comm=4.18)
    net23 = sum(x["pnl"] for x in tr23)
    # amendment_1: parquet-based frozen artifact is 4577 / $260,003.14 (r13 CSV), reproduced
    # to the cent; the 4598/$264,955 figure is the r1j LEDGER-based variant.
    okh = abs(len(tr23) - 4577) <= 2 and abs(net23 - 260003.14) < 500
    print(f"HARNESS S1 2023-window: n={len(tr23)} net=${net23:,.0f} -> "
          f"{'PASS' if okh else 'FAIL - VOID'}", flush=True)
    if not okh:
        return
    tr = run_master(bb, exit_strict=False, gate=True, comm=COMM_RT)
    members["S1_CAND2"] = week_table(
        [dict(pnl=x["pnl"], xt=str(bb["t"][x["xi"]])) for x in tr], D, lambda x: x["xt"])
    print(f"S1 done: {len(tr)} trades [{_time.time()-t0:.0f}s]", flush=True)

    # ---- S2: Solar T1 x skew exits -----------------------------------------------------
    st = bb["st"]
    sig = np.where(np.abs(st) == 1, np.sign(st), 0).astype(np.int8)
    sig[:20] = 0; sig[D["fb"]] = 0
    trr = np.maximum(D["h"] - D["l"],
                     np.maximum(np.abs(D["h"] - np.roll(D["c"], 1)),
                                np.abs(D["l"] - np.roll(D["c"], 1))))
    trr[0] = D["h"][0] - D["l"][0]
    atr = pd.Series(trr).rolling(14, min_periods=1).mean().values
    bars2 = dict(n=D["n"], t=D["t"], o=D["o"], h=D["h"], l=D["l"], c=D["c"],
                 lb=D["lb"], lv=np.zeros((D["n"], 5)))
    for fam, par in (("X_OPP", None), ("X_TRAIL_PTS", 25), ("X_TRAIL_PTS", 50),
                     ("X_TRAIL_PTS", 80), ("X_TARGET", 60)):
        for stop in (65, 130):
            trl = layer_b_exit(bars2, None, sig, atr, fam, par, stop=stop)
            for x in trl:
                x["pnl"] -= COMM_RT
            nm = f"S2_{fam}{'' if par is None else par}_s{stop}"
            members[nm] = week_table(trl, D, lambda x: x["xt"])
            print(f"{nm}: {len(trl)} trades [{_time.time()-t0:.0f}s]", flush=True)

    # ---- S3: VF frozen configs ---------------------------------------------------------
    lv_path = os.path.join(OUT, "vf_levels_cache.npy")
    if os.path.exists(lv_path):
        lv = np.load(lv_path)
    else:
        lv = vf_levels(D["t"], D["c"], D["v"], 60, 5,
                       lifecycle="anchor", formula="percentile_linear")
        np.save(lv_path, lv)
    print(f"vf_levels ready [{_time.time()-t0:.0f}s]", flush=True)
    bars3 = dict(n=D["n"], t=D["t"], o=D["o"], h=D["h"], l=D["l"], c=D["c"],
                 lb=D["lb"], lv=lv)
    trend = trend_states("T_C", D["c"], D["l"], D["h"], lv, ema(D["c"], 20))
    for nm, (P, C_, X, xp) in (("S3_VF_incumbent", ("P_MED", "C_DIR", "X_OPP", None)),
                               ("S3_VF_leading", ("P_IN", "C_REC", "X_TRAIL_PTS", 80))):
        s3 = layer_a_v2(bars3, trend, "D_MOM", "G_WITH", P, C_, "H1a")
        trl = layer_b_exit(bars3, trend, s3, atr, X, xp)
        for x in trl:
            x["pnl"] -= COMM_RT
        members[nm] = week_table(trl, D, lambda x: x["xt"])
        print(f"{nm}: {len(trl)} trades [{_time.time()-t0:.0f}s]", flush=True)

    # ---- S6: VF manual 1-minute suggested preset (amendment_1) -------------------------
    lv6_path = os.path.join(OUT, "vf_levels_preset1m_cache.npy")
    if os.path.exists(lv6_path):
        lv6 = np.load(lv6_path)
    else:
        lv6 = vf_levels(D["t"], D["c"], D["v"], 20, 7,
                        pcts=(10, 40, 50, 60, 80),
                        lifecycle="anchor", formula="percentile_linear")
        np.save(lv6_path, lv6)
    print(f"vf_levels preset ready [{_time.time()-t0:.0f}s]", flush=True)
    bars6 = dict(n=D["n"], t=D["t"], o=D["o"], h=D["h"], l=D["l"], c=D["c"],
                 lb=D["lb"], lv=lv6)
    trend6 = trend_states("T_C", D["c"], D["l"], D["h"], lv6, ema(D["c"], 20))
    for cthr in (0.10, 0.30):
        s6 = layer_a_v2(bars6, trend6, "D_MOM", "G_WITH", "P_IN", "C_REC", "H1a",
                        qty=5, split=15, close_thr=cthr)
        for X, xp in (("X_OPP", None), ("X_TRAIL_PTS", 80)):
            trl = layer_b_exit(bars6, trend6, s6, atr, X, xp)
            for x in trl:
                x["pnl"] -= COMM_RT
            nm = f"S6_VF1M_c{int(cthr*100)}_{X}{'' if xp is None else xp}"
            members[nm] = week_table(trl, D, lambda x: x["xt"])
            print(f"{nm}: {len(trl)} trades [{_time.time()-t0:.0f}s]", flush=True)

    # ---- S4 / S5 -----------------------------------------------------------------------
    for nm, vp, ws, wb in (("S4_SM14_vp460", 460, True, True),
                           ("S4_SM14_vp1380", 1380, True, True),
                           ("S4_SOLAR13_only", 460, True, False),
                           ("S5_BMOM", 460, False, True)):
        trl = sm14_1m(D, vp, with_solar=ws, with_bmom=wb)
        members[nm] = week_table(trl, D, lambda x: x["xt"])
        print(f"{nm}: {len(trl)} trades [{_time.time()-t0:.0f}s]", flush=True)

    # ---- portfolios (fixed, preregistered) --------------------------------------------
    def combine(names):
        out = {}
        for nm in names:
            for s, (net, ntr) in members[nm].items():
                a = out.setdefault(s, [0.0, 0])
                a[0] += net; a[1] += ntr
        return out

    ports = {"P1": combine(["S1_CAND2", "S4_SM14_vp460", "S5_BMOM"]),
             "P2": combine(["S1_CAND2", "S4_SM14_vp460"]),
             "P3": combine(["S1_CAND2", "S2_X_TRAIL_PTS80_s130", "S4_SM14_vp460"]),
             "P4": combine(["S2_X_OPP_s130", "S2_X_TRAIL_PTS25_s130",
                            "S2_X_TRAIL_PTS50_s130", "S2_X_TRAIL_PTS80_s130",
                            "S2_X_TARGET60_s130"])}

    def overlay(per_s, limit):
        if limit is None:
            return per_s
        out = {}
        by_wk = {}
        for s in sorted(per_s):
            by_wk.setdefault(D["wk"][s], []).append(s)
        for w, ss in by_wk.items():
            cum = 0.0; halted = False
            for s in ss:
                if halted:
                    continue
                net, ntr = per_s[s]
                out[s] = [net, ntr]
                cum += net
                if cum <= -limit:
                    halted = True
        return out

    all_rows = []
    for nm, per_s in list(members.items()) + list(ports.items()):
        for lim in ((None, 3000, 5000) if nm in ("P1", "P2", "P3", "P4") else (None,)):
            ps = overlay(per_s, lim)
            tag = nm if lim is None else f"{nm}_wl{lim}"
            for which in ("dev", "hold"):
                r = summarize(ps, D, which)
                if r is None:
                    continue
                stress_net = np.array(r["_net"]) - STRESS_RT * np.array(r["_ntr"])
                all_rows.append(dict(
                    member=tag, sample=which, weeks=r["weeks"], mean=round(r["mean"]),
                    median=round(r["median"]), pos_pct=round(r["pos"], 1),
                    worst=round(r["worst"]), best=round(r["best"]),
                    sharpe=round(r["sharpe"], 3), maxdd=round(r["maxdd"]),
                    tpw=round(r["tpw"], 1), per_trade=round(r["per_trade"], 1),
                    total=round(r["total"]),
                    stress_mean=round(float(stress_net.mean())),
                    stress_pos_pct=round(float((stress_net > 0).mean() * 100), 1),
                    stress_total=round(float(stress_net.sum()))))

    sm = pd.DataFrame(all_rows)
    sm.to_csv(os.path.join(OUT, "summary.csv"), index=False)
    # weekly detail for portfolios + S1 (for the report)
    det = []
    for nm in ("S1_CAND2", "P1", "P2", "P3", "P4"):
        per_s = members.get(nm) or ports[nm]
        for which in ("dev", "hold"):
            r = summarize(per_s, D, which)
            if r:
                for w, netv, ntrv in zip(r["_wk"], r["_net"], r["_ntr"]):
                    det.append(dict(member=nm, sample=which, week=w,
                                    net=round(float(netv), 2), trades=int(ntrv)))
    pd.DataFrame(det).to_csv(os.path.join(OUT, "portfolio_weekly.csv"), index=False)

    pd.set_option("display.width", 250)
    for which in ("dev", "hold"):
        s = sm[sm["sample"] == which].sort_values("sharpe", ascending=False)
        print(f"\n================ {which.upper()} ================")
        print(s[["member", "weeks", "mean", "pos_pct", "worst", "sharpe", "maxdd",
                 "tpw", "per_trade", "total", "stress_mean", "stress_pos_pct"]]
              .to_string(index=False))
    print(f"\ndone [{_time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
