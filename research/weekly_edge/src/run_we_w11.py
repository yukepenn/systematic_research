"""WE_W11 DIMENSIONS (spec preregistered): time-of-day, multi-instrument, low-range fade."""
from __future__ import annotations

import os
import sys
import time as _time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from run_we_w01 import ROOT, PV, COMM_RT, STRESS_RT, load, week_table, summarize, sm14_1m
from run_we_w03 import fills, cd_signals                                 # noqa: E402
from run_we_w06a import available_move                                   # noqa: E402
from run_we_w09 import intraday_features                                 # noqa: E402
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
sys.path.insert(0, os.path.join(ROOT, "research", "original_trader_reconstruction",
                                "solar_family", "src"))
from solarwave import SolarWaveParams                                    # noqa: E402
import inverse_core as IC                                                # noqa: E402
from run_r13_strict_master import run_master                             # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W11_DIMENSIONS", "out")
os.makedirs(OUT, exist_ok=True)
SEGS = [("ASIA", 1080, 1439), ("ASIA2", 0, 179), ("EUROPE", 180, 509),
        ("PREOPEN", 510, 569), ("RTH_AM", 570, 749), ("RTH_PM", 750, 959),
        ("CLOSE", 960, 1020)]


def seg_of(minute_of_day):
    out = np.full(len(minute_of_day), "OTHER", dtype=object)
    for nm, a, b in SEGS:
        out[(minute_of_day >= a) & (minute_of_day <= b)] = "ASIA" if nm == "ASIA2" else nm
    return out


def load_other(sym, fname):
    d = pd.read_parquet(os.path.join(ROOT, "runs", f"SM1M_{sym}_SUBSTRATE", "out", fname))
    d["time"] = pd.to_datetime(d["time"])
    d = d.sort_values("time").reset_index(drop=True)
    t = d["time"].values.astype("datetime64[s]")
    n = len(d)
    fb = np.zeros(n, bool); fb[0] = True
    fb[1:] = np.diff(t).astype("timedelta64[m]").astype(np.int64) > 60
    lb = np.zeros(n, bool); lb[:-1] = fb[1:]; lb[-1] = True
    sid = np.cumsum(fb) - 1
    n_sess = sid[-1] + 1
    idx = np.arange(n)
    last_of = np.zeros(n_sess, np.int64)
    last_of[sid[lb]] = idx[lb]
    sess_end = t[last_of] + np.timedelta64(60, "s")
    sess_date = sess_end.astype("datetime64[D]")
    iso = pd.Series(pd.to_datetime(sess_date)).dt.isocalendar()
    wk = (iso["year"].astype(str) + "-W" + iso["week"].astype(str).str.zfill(2)).values
    return dict(df=d, t=t, o=d["open"].values.astype(float), h=d["high"].values.astype(float),
                l=d["low"].values.astype(float), c=d["close"].values.astype(float),
                v=d["volume"].values.astype(float), n=n, fb=fb, lb=lb, sid=sid,
                n_sess=n_sess, sess_end=sess_end, sess_date=sess_date, wk=wk)


def fade_trades(D, active, k, stop=130.0, max_per=3):
    """Low-range mean-reversion: fade k*ATR from session VWAP, target = VWAP. Causal."""
    t, o, h, l, c, v = D["t"], D["o"], D["h"], D["l"], D["c"], D["v"]
    fb, lb, n = D["fb"], D["lb"], D["n"]
    tr = np.maximum(h - l, np.maximum(np.abs(h - np.roll(c, 1)), np.abs(l - np.roll(c, 1))))
    tr[0] = h[0] - l[0]
    atr = pd.Series(tr).rolling(14, min_periods=1).mean().values
    atr = np.concatenate([[atr[0]], atr[:-1]])
    trades = []
    pos = 0; epx = 0.0; eti = -1; pend = 0; cnt = 0
    pv_ = 0.0; vv = 0.0; vwap_prev = np.nan
    for i in range(n):
        if fb[i]:
            pv_ = 0.0; vv = 0.0; cnt = 0; vwap_prev = np.nan
        if pend != 0 and pos == 0:
            pos = pend; epx, eti = o[i], i; cnt += 1
        pend = 0
        if pos != 0:
            lvl = epx - pos * stop
            if (l[i] <= lvl) if pos > 0 else (h[i] >= lvl):
                gap = (o[i] <= lvl) if pos > 0 else (o[i] >= lvl)
                px = o[i] if gap else lvl
                trades.append(dict(d=pos, et=str(t[eti]), xt=str(t[i]),
                                   pnl=pos * (px - epx) * PV - COMM_RT))
                pos = 0
        if pos != 0 and not np.isnan(vwap_prev):
            tgt = vwap_prev
            if (h[i] >= tgt) if pos > 0 else (l[i] <= tgt):
                px = o[i] if ((o[i] >= tgt) if pos > 0 else (o[i] <= tgt)) else tgt
                trades.append(dict(d=pos, et=str(t[eti]), xt=str(t[i]),
                                   pnl=pos * (px - epx) * PV - COMM_RT))
                pos = 0
        if lb[i]:
            if pos != 0:
                trades.append(dict(d=pos, et=str(t[eti]), xt=str(t[i]),
                                   pnl=pos * (c[i] - epx) * PV - COMM_RT))
                pos = 0
            pv_ = 0.0; vv = 0.0; cnt = 0; vwap_prev = np.nan
            continue
        if (pos == 0 and cnt < max_per and active[i] and i >= 20
                and not np.isnan(vwap_prev) and atr[i] > 0):
            dev = c[i - 1] - vwap_prev if i > 0 else 0.0
            if dev >= k * atr[i]:
                pend = -1
            elif dev <= -k * atr[i]:
                pend = 1
        pv_ += c[i] * v[i]; vv += v[i]
        vwap_prev = pv_ / vv if vv > 0 else np.nan
    return trades


def main():
    t0 = _time.time()
    D = load()
    n_sess, tarr = D["n_sess"], D["t"]
    idx = np.arange(D["n"])
    starts = np.zeros(n_sess, np.int64)
    for s in range(n_sess):
        starts[s] = idx[D["sid"] == s][0]
    avail = np.zeros(n_sess)
    for s in range(n_sess):
        m = idx[D["sid"] == s]
        avail[s], _, _, _ = available_move(D["c"], m[0], m[-1] + 1)
    big = avail >= 500
    rng, dmove, atr, norm = intraday_features(D)
    ratio = np.where(norm > 0, rng / np.maximum(norm, 1e-9), 1.0)
    mod = ((D["t"] - D["t"].astype("datetime64[D]")).astype("timedelta64[s]")
           .astype(np.int64) // 60)
    segs = seg_of(mod)

    def lag_b(a):
        return np.concatenate([[True], a[:-1]])
    _, cd_arr = cd_signals(D)
    aL0, aS0 = lag_b(cd_arr >= 0), lag_b(cd_arr <= 0)
    ok08 = (norm <= 0) | (ratio >= 0.8)
    tgn = sm14_1m(D, 460, return_targets=True, volmults=[6, 8, 10, 12, 14, 16])
    bb = IC.prepare(D["df"], SolarWaveParams())
    S = {"S1": [dict(d=x["d"], pnl=x["pnl"], et=str(bb["t"][x["ei"]]),
                     xt=str(bb["t"][x["xi"]]))
                for x in run_master(bb, exit_strict=False, gate=True, comm=COMM_RT)],
         "S4n.A0.8": fills(D, tgn, allow_long=aL0 & ok08, allow_short=aS0 & ok08)}
    print(f"bases ready [{_time.time()-t0:.0f}s]", flush=True)

    out = open(os.path.join(OUT, "dimensions.txt"), "w", encoding="utf-8")

    def P(*a):
        print(*a, flush=True); print(*a, file=out)

    # ---------- AXIS 1: time of day ----------
    P("=== AXIS 1: TIME-OF-DAY ATTRIBUTION (entry segment) ===")
    seg_names = ["ASIA", "EUROPE", "PREOPEN", "RTH_AM", "RTH_PM", "CLOSE", "OTHER"]
    keep_segs = {}
    for nm, trl in S.items():
        P(f"\n{nm}")
        P(f"{'segment':<10}{'n':>7}{'net':>12}{'$/trade':>10}{'share%':>9}")
        tot = sum(x["pnl"] for x in trl)
        pos_segs = []
        for sg in seg_names:
            xs = [x for x in trl
                  if segs[int(min(np.searchsorted(tarr, np.datetime64(x["et"])),
                                  D["n"] - 1))] == sg]
            if not xs:
                continue
            net = sum(x["pnl"] for x in xs)
            P(f"{sg:<10}{len(xs):>7}{net:>12,.0f}{net/len(xs):>10.1f}"
              f"{100*net/tot:>9.1f}")
            if net > 0:
                pos_segs.append(sg)
        keep_segs[nm] = pos_segs
        P(f"  positive segments (rule-formed): {pos_segs}")

    P("\n--- D2: restrict entries to those segments ---")
    P(f"{'variant':<24}{'n':>7}{'wkMean':>9}{'wkPos':>7}{'wkWorst':>10}{'wkShrp':>8}"
      f"{'strs':>8}{'hShrp':>8}")
    rows = []
    for nm, trl in S.items():
        for tag, sel in (("base", None), ("posseg", set(keep_segs[nm]))):
            xs = trl if sel is None else [
                x for x in trl
                if segs[int(min(np.searchsorted(tarr, np.datetime64(x["et"])),
                                D["n"] - 1))] in sel]
            wt = week_table(xs, D, lambda x: x["xt"])
            r = summarize(wt, D, "dev"); rh = summarize(wt, D, "hold")
            st = float((np.array(r["_net"]) - STRESS_RT * np.array(r["_ntr"])).mean())
            P(f"{nm+'.'+tag:<24}{len(xs):>7}{r['mean']:>9,.0f}{r['pos']:>7.1f}"
              f"{r['worst']:>10,.0f}{r['sharpe']:>8.3f}{st:>8,.0f}{rh['sharpe']:>8.3f}")
            rows.append(dict(axis="tod", name=f"{nm}.{tag}", n=len(xs),
                             wk_mean=round(r["mean"]), wk_pos=round(r["pos"], 1),
                             wk_worst=round(r["worst"]), wk_sharpe=round(r["sharpe"], 3),
                             stress=round(st), hold_sharpe=round(rh["sharpe"], 3)))

    # ---------- AXIS 2: multi-instrument ----------
    P("\n=== AXIS 2: MULTI-INSTRUMENT (same engine, other index futures) ===")
    P(f"{'instrument':<12}{'n':>7}{'net':>13}{'wkMean':>9}{'wkPos':>7}{'wkWorst':>10}"
      f"{'wkShrp':>8}")
    inst = {"NQ": (D, 20.0, S["S4n.A0.8"])}
    for sym, fn, pvv in (("ES", "es_1m_2022_2026.parquet", 50.0),
                         ("RTY", "rty_1m_2022_2026.parquet", 50.0),
                         ("YM", "ym_1m_2022_2026.parquet", 5.0)):
        Dx = load_other(sym, fn)
        import run_we_w01 as W1
        old = W1.PV
        W1.PV = pvv
        import run_we_w03 as W3
        oldw3 = W3.PV
        W3.PV = pvv
        tgx = sm14_1m(Dx, 460, return_targets=True, volmults=[6, 8, 10, 12, 14, 16])
        _, cdx = cd_signals(Dx)
        axL, axS = lag_b(cdx >= 0), lag_b(cdx <= 0)
        rngx, _, _, normx = intraday_features(Dx)
        ratx = np.where(normx > 0, rngx / np.maximum(normx, 1e-9), 1.0)
        okx = (normx <= 0) | (ratx >= 0.8)
        trx = fills(Dx, tgx, allow_long=axL & okx, allow_short=axS & okx)
        W1.PV = old; W3.PV = oldw3
        inst[sym] = (Dx, pvv, trx)
        wt = week_table(trx, Dx, lambda x: x["xt"])
        r = summarize(wt, Dx, "dev")
        P(f"{sym:<12}{len(trx):>7}{sum(x['pnl'] for x in trx):>13,.0f}{r['mean']:>9,.0f}"
          f"{r['pos']:>7.1f}{r['worst']:>10,.0f}{r['sharpe']:>8.3f}")
        rows.append(dict(axis="multi", name=sym, n=len(trx),
                         wk_mean=round(r["mean"]), wk_pos=round(r["pos"], 1),
                         wk_worst=round(r["worst"]), wk_sharpe=round(r["sharpe"], 3)))
        print(f"   {sym} done [{_time.time()-t0:.0f}s]", flush=True)

    wvs = {}
    for sym, (Dx, pvv, trx) in inst.items():
        t_ = week_table(trx, Dx, lambda x: x["xt"])
        d = {}
        for s, (net, _) in t_.items():
            d[Dx["wk"][s]] = d.get(Dx["wk"][s], 0.0) + net
        wvs[sym] = d
    keys = list(wvs)
    allw = sorted(set().union(*[set(wvs[k]) for k in keys]))
    M = np.array([[wvs[k].get(w, 0.0) for w in allw] for k in keys])
    C = np.corrcoef(M)
    P("\nweekly-net correlations:")
    P("        " + "".join(f"{k:>9}" for k in keys))
    for i, k in enumerate(keys):
        P(f"{k:<8}" + "".join(f"{C[i, j]:>9.2f}" for j in range(len(keys))))
    maxoff = max(C[i, j] for i in range(len(keys)) for j in range(len(keys)) if i != j)
    P(f"max off-diagonal correlation {maxoff:.2f} -> "
      f"{'FB FIRES (leverage, not diversification)' if maxoff > 0.7 else 'genuine diversification'}")
    pw = {}
    for sym in keys:
        for w, netv in wvs[sym].items():
            pw[w] = pw.get(w, 0.0) + netv
    v = np.array([pw[w] for w in sorted(pw)])
    P(f"equal-weight 4-instrument portfolio: weeks {len(v)}  mean {v.mean():,.0f}  "
      f"pos {100*(v>0).mean():.1f}%  worst {v.min():,.0f}  "
      f"sharpe {v.mean()/v.std(ddof=1):.3f}")

    # ---------- AXIS 3: low-range fade ----------
    P("\n=== AXIS 3: LOW-RANGE FADE (trade the regime we stand aside in) ===")
    low = (norm > 0) & (ratio < 0.8)
    P(f"low-range bars: {100*low.mean():.1f}%")
    P(f"{'variant':<14}{'n':>7}{'net':>12}{'$/tr':>9}{'wkMean':>9}{'wkPos':>7}"
      f"{'wkWorst':>10}{'wkShrp':>8}{'strs':>8}")
    for k in (1.0, 1.5, 2.0):
        trl = fade_trades(D, low, k)
        if len(trl) < 100:
            P(f"FADE k={k}: only {len(trl)} trades")
            continue
        wt = week_table(trl, D, lambda x: x["xt"])
        r = summarize(wt, D, "dev")
        st = float((np.array(r["_net"]) - STRESS_RT * np.array(r["_ntr"])).mean())
        net = sum(x["pnl"] for x in trl)
        P(f"FADE k={k:<8}{len(trl):>7}{net:>12,.0f}{net/len(trl):>9.1f}{r['mean']:>9,.0f}"
          f"{r['pos']:>7.1f}{r['worst']:>10,.0f}{r['sharpe']:>8.3f}{st:>8,.0f}")
        rows.append(dict(axis="fade", name=f"k{k}", n=len(trl), wk_mean=round(r["mean"]),
                         wk_pos=round(r["pos"], 1), wk_worst=round(r["worst"]),
                         wk_sharpe=round(r["sharpe"], 3), stress=round(st)))
    pd.DataFrame(rows).to_csv(os.path.join(OUT, "summary.csv"), index=False)
    out.close()
    print(f"done [{_time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
