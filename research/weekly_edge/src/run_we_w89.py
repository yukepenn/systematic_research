"""WE_W89 - CANDIDATE-SPECIFIC FRICTION.

Spec: runs/WE_W89_CANDCOST/spec.yaml, committed BEFORE this ran.

W82 measured $14.65 per contract round turn by weighting the per-minute spread profile with
P1's OWN fill time-of-day distribution. The challenger is not P1. BMOM is an RTH-only channel
(reset 09:31, killed 15:57) while 61.6 % of P1's fills are overnight, and overnight NQ is 3.00
ticks against RTH's 2.00. A cost weighted by the wrong distribution is not the candidate's cost.

Second debt: the W88 ladder is reproduced here exactly (rtB 4.95 / rtX 9.35 / trailing 12m), and
those rates are TRADES per week. P1's 11.15 is CONTRACT round turns per week. X9a carries the
size-2 quality layer, so if it was charged per trade its friction was understated.
"""
from __future__ import annotations

import glob
import itertools
import os
import sys
import time as _time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_we_w01 as W1                                                  # noqa: E402
from run_we_w01 import ROOT, PV, COMM_RT, sm14_1m                        # noqa: E402
from run_we_w17 import load_deep                                         # noqa: E402
from run_we_w19 import MEMBERS, QS                                       # noqa: E402
from run_we_w26 import fills_daily                                       # noqa: E402
from run_we_w35 import fills_qexit                                       # noqa: E402
from run_we_w37 import causal_score                                      # noqa: E402
from run_we_w38 import sfills                                            # noqa: E402
from run_we_w39 import WIN                                               # noqa: E402
from run_we_w51c import dd_profile                                       # noqa: E402
from we_channels import build_channels                                   # noqa: E402
from we_fastctx import fast_build_context                                # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W89_CANDCOST", "out")
os.makedirs(OUT, exist_ok=True)
W76OUT = os.path.join(ROOT, "runs", "WE_W76_FORWARD2026", "out")
W82OUT = os.path.join(ROOT, "runs", "WE_W82_FILLAUDIT", "out")
G1S = os.path.join(ROOT, "research", "scalping_lab", "substrate", "grid1s", "NQ")

L13 = [6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30]
A = np.datetime64("2022-07-01")
B = np.datetime64("2026-08-01")
TICK = 0.25
DDT = 20245.0
BLANKET = 14.65                      # W82's P1-weighted number, the incumbent assumption


def main():
    t0 = _time.time()
    out = open(os.path.join(OUT, "candcost.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out); out.flush()

    # =========================================================== PHASE 0: the spread profile
    P_("=" * 118)
    P_("=== PHASE 0: rebuild the spread profile and ASSERT it against W82's committed file")
    P_("=" * 118)
    files = sorted(glob.glob(os.path.join(G1S, "*.parquet")))
    parts, skipped = [], []
    for p in files:
        d = pd.read_parquet(p, columns=["time", "bid", "ask"])
        d["time"] = pd.to_datetime(d["time"])
        if float((d["bid"] > 0).mean()) < 0.5:
            skipped.append(os.path.basename(p)); continue
        parts.append(d)
    Q = pd.concat(parts, ignore_index=True).sort_values("time").reset_index(drop=True)
    Q = Q[(Q["bid"] > 0) & (Q["ask"] > 0)]
    Q["sp_tk"] = (Q["ask"] - Q["bid"]) / TICK
    Q["mod"] = Q["time"].dt.hour * 60 + Q["time"].dt.minute
    prof_med = Q.groupby("mod")["sp_tk"].median()
    prof_p75 = Q.groupby("mod")["sp_tk"].quantile(0.75)
    ref = pd.read_csv(os.path.join(W82OUT, "spread_by_minute.csv")).set_index("mod")["sp_tk"]
    join = prof_med.reindex(ref.index)
    dmax = float(np.nanmax(np.abs(join.to_numpy() - ref.to_numpy())))
    P_(f"    {len(files)} files, {len(skipped)} excluded, {len(Q):,} two-sided second-quotes")
    P_(f"    {Q['time'].min()} -> {Q['time'].max()}")
    P_(f"    max |rebuilt - W82 committed| over {len(ref)} minutes = {dmax:.10f}   "
       f"{'ASSERT OK' if dmax == 0.0 else 'MISMATCH - STOP'}")
    if dmax != 0.0:
        P_("    the join is not what W82 committed. No cost number is issued.")
        out.close(); return
    qdates = pd.Index(Q["time"].dt.normalize().unique())
    P_(f"    quote sessions: {len(qdates)} calendar days, "
       f"{qdates.min().date()} -> {qdates.max().date()}")

    # =========================================================== PHASE 1: rebuild the objects
    P_("")
    P_("=" * 118)
    P_("=== PHASE 1: rebuild P1 / BMOM / X9a trade lists with timestamps, direction and size")
    P_("=" * 118)
    D = load_deep("2022-01-01", "2026-07-31 17:00", extend=True)
    W1.DEV_END = pd.Timestamp("2026-07-31").date()
    n, tarr, sid = D["n"], D["t"], D["sid"]
    X = fast_build_context(D)
    P_(f"    substrate {n:,} bars, {D['n_sess']:,} sessions [{_time.time()-t0:.0f}s]")

    z = np.load(os.path.join(W76OUT, "mem_ext.npz"))
    mem, bmom, tilt = z["mem"], z["bmom"], z["tilt"]
    fb, lb, sess_end = D["fb"], D["lb"], D["sess_end"]
    blocked = tarr >= sess_end[sid] - np.timedelta64(30 * 60, "s")
    flatm = tarr >= sess_end[sid] - np.timedelta64(21 * 60, "s")
    idx_l13 = {v: k for k, v in enumerate(L13)}

    st = np.zeros(D["n_sess"], np.int64)
    st[sid[fb]] = np.flatnonzero(fb)
    sess_in = np.array([s for s in range(D["n_sess"]) if A <= tarr[st[s]] < B])
    in_win = np.zeros(D["n_sess"], bool); in_win[sess_in] = True
    sdate = pd.to_datetime(D["sess_date"])[sess_in]
    sess_wk = np.array([D["wk"][s] for s in range(D["n_sess"])])
    keys_w = sorted(set(sess_wk[sess_in]))
    wk_idx = np.array([keys_w.index(sess_wk[s]) for s in sess_in])
    NW = len(keys_w)

    def i_of(ts):
        return int(min(np.searchsorted(tarr, np.datetime64(ts)), n - 1))

    def ra(x):
        return np.where(x >= 0, np.floor(x + 0.5), np.ceil(x - 0.5))

    def hyst(M):
        tgt = np.zeros(n, np.int8)
        for i in range(n):
            p = 0 if (i == 0 or fb[i]) else tgt[i - 1]
            g = p
            if flatm[i]:
                g = 0
            elif p == 0:
                if not blocked[i]:
                    g = 1 if M[i] >= 3.0 else (-1 if M[i] <= -3.0 else p)
            elif p > 0:
                g = -1 if (M[i] <= -3.0 and not blocked[i]) else (0 if M[i] <= 1.0 else p)
            else:
                g = 1 if (M[i] >= 3.0 and not blocked[i]) else (0 if M[i] >= -1.0 else p)
            tgt[i] = g
        return tgt

    def TG_for(chan):
        d = {}
        for name, vols in MEMBERS.items():
            cols = [idx_l13[v] for v in vols]
            s_ = mem[:, cols].sum(axis=1).astype(np.int32)
            T = np.clip(ra(s_ / float(len(cols)) * 10.0), -10, 10)
            ag = (np.sign(s_) == tilt) & (s_ != 0) & (tilt != 0)
            Tp = np.clip(ra(T * np.where(ag, 1.25, 1.0) * 0.9026), -13, 13)
            d[name] = hyst(0.7086 * Tp + 2.83 * chan.astype(float))
        return d

    def vote_(TGx, side):
        vs = []
        for m_ in MEMBERS:
            tg = TGx[m_]
            for q in QS:
                okv = np.ones(n, bool) if q is None else ((X["norm"] <= 0) | (X["ratio"] >= q))
                for dg in (True, False):
                    a_ = okv & (X["dL"] if side > 0 else X["dS"]) if dg else okv
                    hit = (tg > 0) if side > 0 else (tg < 0)
                    vs.append(np.where(hit & a_, 1, 0).astype(np.int8))
        return np.vstack(vs).mean(axis=0)

    def long_obj(TGx):
        p = (vote_(TGx, +1) >= 0.5).astype(np.int8)
        bb = fills_daily(D, p, halt=1300, target=1000)
        ee = np.array([i_of(x["et"]) for x in bb if A <= np.datetime64(x["et"]) < B])
        s_, _ = causal_score(X, ee, window=WIN)
        return [x for x in fills_qexit(D, p, np.where(s_ >= 3, 2, 1).astype(np.int8), s_)
                if in_win[int(sid[i_of(x["et"])])]]

    TR = {}
    TG0 = TG_for(bmom)
    TR["P1"] = long_obj(TG0)
    TR["BMOM"] = [x for x in sfills(D, np.where(flatm, 0, bmom).astype(np.int8),
                                    halt=1300.0, target=1000.0)
                  if in_win[int(sid[i_of(x["et"])])]]
    CH = build_channels(D, which=["X9a_disp_sessanchor"])
    TR["X9a"] = long_obj(TG_for(CH["X9a_disp_sessanchor"]))
    P_(f"    three trade lists built [{_time.time()-t0:.0f}s]")
    P_("")
    P_("    NOTE ON WHAT 'X9a' IS: it is long_obj(TG_for(X9a channel)) - the FULL P1 object with")
    P_("    the X9a channel substituted into the OR slot. It is NOT a standalone channel and it")
    P_("    is NOT a second engine. This is what streams_extended.csv calls 'w72:X9a'.")

    # ---------------------------------------------------------------- per-candidate profile
    P_("")
    P_(f"{'candidate':<8}{'trades':>9}{'ctrRT':>9}{'ctrRT/tr':>10}{'ctrRT/wk':>10}"
       f"{'W88 used':>10}{'size2 %':>9}")
    ROWS = {}
    for k, trl in TR.items():
        nt = len(trl)
        crt = sum(x["u"] for x in trl)
        s2 = 100.0 * sum(1 for x in trl if x["u"] >= 2) / max(nt, 1)
        used = {"P1": 11.15, "BMOM": 4.95, "X9a": 9.35}[k]
        ROWS[k] = dict(trades=nt, ctrRT=crt, per_wk=crt / NW, w88=used, size2=s2)
        P_(f"{k:<8}{nt:>9,}{crt:>9,}{crt/max(nt,1):>10.3f}{crt/NW:>10.2f}"
           f"{used:>10.2f}{s2:>8.1f}%")

    # ---------------------------------------------------------------- fills -> minute of day
    def seg(m):
        return np.where((m >= 570) & (m < 960), "RTH",
                        np.where((m >= 960) & (m < 1020), "POST", "OVERNIGHT"))

    P_("")
    P_(f"{'candidate':<8}{'OVERNIGHT':>12}{'RTH':>10}{'POST':>9}   (share of CONTRACT-weighted "
       f"fills; W82 measured P1 at 61.6 / 35.5 / 2.9 on TRADE-weighted fills)")
    FILLS = {}
    for k, trl in TR.items():
        f = pd.DataFrame(
            [dict(t=pd.Timestamp(x["et"]), u=x["u"]) for x in trl]
            + [dict(t=pd.Timestamp(x["xt"]), u=x["u"]) for x in trl])
        f["mod"] = f["t"].dt.hour * 60 + f["t"].dt.minute
        f["seg"] = seg(f["mod"].to_numpy())
        FILLS[k] = f
        tot = f["u"].sum()
        sh = {s: 100.0 * f[f["seg"] == s]["u"].sum() / tot for s in ("OVERNIGHT", "RTH", "POST")}
        P_(f"{k:<8}{sh['OVERNIGHT']:>11.1f}%{sh['RTH']:>9.1f}%{sh['POST']:>8.1f}%")
        ROWS[k].update({f"sh_{s}": sh[s] for s in sh})

    # ---------------------------------------------------------------- the weighted cost
    def weighted(f, prof):
        w = f.groupby("mod")["u"].sum()
        common = prof.index.intersection(w.index)
        cov = float(w.loc[common].sum() / w.sum())
        wt = w.loc[common] / w.loc[common].sum()
        return float((prof.loc[common] * wt).sum()), cov

    P_("")
    P_("=" * 118)
    P_("=== PHASE 2: THE CANDIDATE-SPECIFIC COST")
    P_("=" * 118)
    P_(f"{'candidate':<8}{'ticks(med)':>12}{'$/ctrRT':>10}{'vs 14.65':>11}"
       f"{'ticks(p75)':>12}{'$/ctrRT p75':>13}{'minute cov':>12}")
    for k in TR:
        tk, cov = weighted(FILLS[k], prof_med)
        tk75, _ = weighted(FILLS[k], prof_p75)
        c, c75 = tk * TICK * PV, tk75 * TICK * PV
        ROWS[k].update(tk=tk, cost=c, tk75=tk75, cost75=c75)
        P_(f"{k:<8}{tk:>12.3f}{c:>10.2f}{100*(c/BLANKET-1):>+10.1f}%"
           f"{tk75:>12.3f}{c75:>13.2f}{100*cov:>11.1f}%")

    # ---------------------------------------------------------------- direct-window coverage
    P_("")
    P_("=== sample coverage: how much of each candidate the 45 quote sessions actually touch")
    qset = set(qdates.date)
    for k, trl in TR.items():
        f = FILLS[k]
        ind = np.array([d_.date() in qset for d_ in f["t"]])
        cov_u = 100.0 * f["u"].to_numpy()[ind].sum() / f["u"].sum()
        ROWS[k]["direct_cov"] = cov_u
        P_(f"    {k:<6} {int(ind.sum()):>5,} of {len(f):>6,} fills "
           f"({100*ind.mean():>4.1f} %) in the quote window; "
           f"{cov_u:>4.1f} % of contract-weighted fills")
    P_("    scope inherited from W82: NQ 23,036-29,479, 2025-08 -> 2026-05. Applied to")
    P_("    2022-2026 only. It does NOT transport to 2006-2021 and no deep re-quote is made.")

    pd.DataFrame(ROWS).T.to_csv(os.path.join(OUT, "candidate_cost.csv"))

    # =========================================================== PHASE 3: reprice the ladder
    P_("")
    P_("=" * 118)
    P_("=== PHASE 3: THE LADDER, REPRICED")
    P_("=" * 118)
    d = pd.read_csv(os.path.join(W76OUT, "streams_extended.csv"))
    d["date"] = pd.to_datetime(d["date"]); ds = d["date"]
    cl = pd.read_csv(os.path.join(ROOT, "runs", "WE_W79_CLIQUE", "out", "members.csv"))
    iso = ds.dt.isocalendar()
    wk = (iso["year"].astype(str) + "-W" + iso["week"].astype(str).str.zfill(2)).to_numpy()
    P1d, BMd, X9d = d["P1"].to_numpy(), cl["BMOM"].to_numpy(), cl["X9a"].to_numpy()
    # the daily series must be the same object we just rebuilt - assert it
    for k, ser in (("P1", P1d), ("BMOM", BMd), ("X9a", X9d)):
        sp = np.zeros(D["n_sess"])
        for x in TR[k]:
            sp[int(sid[i_of(x["et"])])] += x["pnl"]
        diff = float(np.max(np.abs(sp[sess_in] - ser)))
        P_(f"    rebuilt {k:<5} vs committed daily series: max |diff| = {diff:.6f}   "
           f"{'OK' if diff < 1e-6 else '*** MISMATCH ***'}")

    t12 = (ds >= pd.Timestamp("2025-08-01")).to_numpy()
    PERIODS = {"full": np.ones(len(ds), bool), "t12": t12,
               "y26": (ds.dt.year == 2026).to_numpy()}

    def panel(v, msk, cost_wk):
        w = pd.Series(v[msk]).groupby(wk[msk]).sum().to_numpy() - cost_wk
        dp = dd_profile(w)
        stk = max((len(list(g)) for c_, g in itertools.groupby(w < 0) if c_), default=0)
        return dict(nwk=len(w), wkpos=100 * float((w > 0).mean()), weekly=float(w.mean()),
                    medwk=float(np.median(w)), maxdd=dp["maxdd"], top5=dp["dd_mean_top5"],
                    worst=float(w.min()), streak=int(stk), ann=52.0 * float(w.mean()))

    LINES = {
        "W88 blanket $14.65 (trade-rate)": lambda nb, nx: BLANKET * (nb * 4.95 + nx * 9.35),
        "candidate-specific WORKING": lambda nb, nx: (nb * ROWS["BMOM"]["cost"]
                                                      * ROWS["BMOM"]["per_wk"]
                                                      + nx * ROWS["X9a"]["cost"]
                                                      * ROWS["X9a"]["per_wk"]),
        "candidate-specific PESSIMISTIC (p75)": lambda nb, nx: (nb * ROWS["BMOM"]["cost75"]
                                                                * ROWS["BMOM"]["per_wk"]
                                                                + nx * ROWS["X9a"]["cost75"]
                                                                * ROWS["X9a"]["per_wk"]),
    }
    P1_LINES = {
        "W88 blanket $14.65 (trade-rate)": BLANKET * 11.15,
        "candidate-specific WORKING": ROWS["P1"]["cost"] * ROWS["P1"]["per_wk"],
        "candidate-specific PESSIMISTIC (p75)": ROWS["P1"]["cost75"] * ROWS["P1"]["per_wk"],
    }
    rows = []
    for lab, fn in LINES.items():
        P_("")
        P_(f"--- {lab} ---")
        P_(f"{'basket':<14}{'nom ctr':>9}{'$/wk cost':>11}{'wk$ t12':>10}{'ann t12':>12}"
           f"{'wk+% t12':>10}{'maxDD':>11}{'top5DD':>10}{'worst wk':>11}{'wk$ full':>10}")
        for nb, nx in [(1, 1), (1, 2), (2, 3), (1, 0), (0, 1)]:
            v = nb * BMd + nx * X9d
            cw = fn(nb, nx)
            a = panel(v, t12, cw); f_ = panel(v, PERIODS["full"], cw)
            nm = f"{nb} BMOM:{nx} X9a" if nb and nx else ("BMOM alone" if nb else "X9a alone")
            P_(f"{nm:<14}{nb+nx:>9}{cw:>11,.0f}{a['weekly']:>10,.0f}{a['ann']:>12,.0f}"
               f"{a['wkpos']:>9.1f}%{f_['maxdd']:>11,.0f}{f_['top5']:>10,.0f}"
               f"{f_['worst']:>11,.0f}{f_['weekly']:>10,.0f}")
            rows.append(dict(line=lab, basket=nm, nb=nb, nx=nx, nominal=nb + nx, cost_wk=cw,
                             **{f"t12_{k2}": v2 for k2, v2 in a.items()},
                             **{f"full_{k2}": v2 for k2, v2 in f_.items()}))
        ap = panel(P1d, t12, P1_LINES[lab]); fp = panel(P1d, PERIODS["full"], P1_LINES[lab])
        P_(f"{'P1 (1 unit)':<14}{1.27:>9.2f}{P1_LINES[lab]:>11,.0f}{ap['weekly']:>10,.0f}"
           f"{ap['ann']:>12,.0f}{ap['wkpos']:>9.1f}%{fp['maxdd']:>11,.0f}{fp['top5']:>10,.0f}"
           f"{fp['worst']:>11,.0f}{fp['weekly']:>10,.0f}")
        rows.append(dict(line=lab, basket="P1", nb=0, nx=0, nominal=1.27,
                         cost_wk=P1_LINES[lab],
                         **{f"t12_{k2}": v2 for k2, v2 in ap.items()},
                         **{f"full_{k2}": v2 for k2, v2 in fp.items()}))
    pd.DataFrame(rows).to_csv(os.path.join(OUT, "ladder.csv"), index=False)

    # ---------------------------------------------------------------- true exposure (H3)
    P_("")
    P_("=== H3: what 'contracts' actually means for each rung (nominal understates it)")
    P_(f"{'basket':<14}{'nominal':>9}{'time-wtd':>11}{'peak':>7}{'X9a avg u':>11}")
    posu = {}
    for k, trl in TR.items():
        occ = np.zeros(n)
        for x in trl:
            occ[i_of(x["et"]):i_of(x["xt"])] += x["u"]
        posu[k] = occ
    inw = np.array([in_win[s] for s in sid])
    for nb, nx in [(1, 1), (1, 2), (2, 3)]:
        tot = nb * posu["BMOM"] + nx * posu["X9a"]
        P_(f"{f'{nb} BMOM:{nx} X9a':<14}{nb+nx:>9}{tot[inw].mean():>11.3f}"
           f"{tot[inw].max():>7.0f}{posu['X9a'][inw][posu['X9a'][inw]>0].mean():>11.3f}")
    P_(f"{'P1 (1 unit)':<14}{1:>9}{posu['P1'][inw].mean():>11.3f}{posu['P1'][inw].max():>7.0f}")
    P_("    'time-weighted' is average contracts held across every in-window minute, so it is")
    P_("    low for objects that are flat most of the time. PEAK is what the account must carry.")
    P_("")
    P_("    reconciliation with the campaign's '1.27 time-weighted contracts' for P1:")
    for k in TR:
        occ = posu[k][inw]
        P_(f"      {k:<5} mean size WHILE IN A POSITION = {occ[occ>0].mean():.3f}   "
           f"in a position on {100*(occ>0).mean():.1f} % of in-window minutes")
    P_("    -> '1.27' is the mean size while holding, NOT contracts carried by the account.")
    P_("    Comparing P1's 1.27 against a basket's NOMINAL order count mixes two units. The")
    P_("    matched-income table in PHASE 5 uses PEAK and TIME-WEIGHTED for both sides.")

    # =========================================================== PHASE 4: gate at real costs
    P_("")
    P_("=" * 118)
    P_("=== PHASE 4: the corrected rolling gate, re-scored at candidate-specific cost")
    P_("=" * 118)
    ends = pd.date_range(ds.min() + pd.DateOffset(months=24), ds.max(), freq="ME")

    def pan_g(v, msk, cost_wk):
        w_ = wk[msk]
        keys = pd.Series(v[msk]).groupby(w_).sum()
        w = keys.to_numpy() - cost_wk
        if len(w) < 8:
            return None
        dp = dd_profile(w)
        k_ = DDT / max(dp["maxdd"], 1e-9)
        return dict(wkpos=100 * float((w > 0).mean()), weekly_dd=float(w.mean()) * k_,
                    top5=dp["dd_mean_top5"])

    def gate(v, cv, base, cb, scale):
        """scale: multiply v by this so its NOMINAL exposure matches base's (W88 sec 5)."""
        c = dict(m=0, w=0, d=0, a=0, n=0)
        for e in ends:
            msk = np.asarray((ds > e - pd.DateOffset(months=24)) & (ds <= e))
            if msk.sum() < 300:
                continue
            a_ = pan_g(v * scale, msk, cv * scale); b_ = pan_g(base, msk, cb)
            if a_ is None or b_ is None:
                continue
            c["n"] += 1
            x1 = a_["weekly_dd"] > b_["weekly_dd"]; x2 = a_["wkpos"] > b_["wkpos"]
            x3 = a_["top5"] < b_["top5"]
            c["m"] += x1; c["w"] += x2; c["d"] += x3; c["a"] += (x1 and x2 and x3)
        nn = max(c["n"], 1)
        return {k2: 100 * v2 / nn for k2, v2 in c.items() if k2 != "n"} | {"n": c["n"]}

    cP1 = ROWS["P1"]["cost"] * ROWS["P1"]["per_wk"]
    P_("    PRECONDITION - oracle battery (W85 rule: a gate that cannot pass a strictly-better")
    P_("    object issues no verdicts):")
    orc = {"P1 + $200/session": P1d + 200.0, "P1 + $500/session": P1d + 500.0,
           "P1 losses halved": np.where(P1d < 0, P1d * .5, P1d),
           "P1 losses x0.75": np.where(P1d < 0, P1d * .75, P1d)}
    okall = True
    for k, v in orc.items():
        g = gate(v, cP1, P1d, cP1, 1.0)
        P_(f"      {k:<22} ALL-THREE {g['a']:>5.0f} %")
        okall &= g["a"] >= 75
    P_(f"      -> gate is {'USABLE' if okall else 'BROKEN - NO VERDICTS ISSUED'}")
    if okall:
        P_("")
        P_(f"{'basket':<16}{'n':>4}{'money':>9}{'wk+%':>8}{'top5DD':>9}{'ALL THREE':>12}"
           f"   (exposure-matched to P1's 1 nominal unit)")
        grows = []
        for nb, nx in [(1, 1), (1, 2), (2, 3), (1, 3), (2, 1), (1, 0), (0, 1)]:
            v = nb * BMd + nx * X9d
            cw = LINES["candidate-specific WORKING"](nb, nx)
            sc = 1.0 / max(nb + nx, 1)
            g = gate(v, cw, P1d, cP1, sc)
            nm = f"{nb} BMOM:{nx} X9a" if nb and nx else ("BMOM alone" if nb else "X9a alone")
            P_(f"{nm:<16}{g['n']:>4}{g['m']:>8.0f}%{g['w']:>7.0f}%{g['d']:>8.0f}%"
               f"{g['a']:>11.0f}%")
            grows.append(dict(basket=nm, nb=nb, nx=nx, scale=sc, **g))
        pd.DataFrame(grows).to_csv(os.path.join(OUT, "gate_candcost.csv"), index=False)

    # =========================================================== PHASE 5: matched income
    P_("")
    P_("=" * 118)
    P_("=== PHASE 5: MATCHED INCOME IN CONSISTENT UNITS  (W88's table mixed two of them)")
    P_("=" * 118)
    P_("    W88 quoted P1 at '6.2 contracts' = 4.89 UNITS x 1.27 mean-size-while-holding, and")
    P_("    the basket at '3 contracts' = a NOMINAL ORDER COUNT. Those are different units.")
    P_("    Here every row is scaled to the same annual income and reported three ways.")
    P_("")
    twP1 = float(posu["P1"][inw].mean()); pkP1 = float(posu["P1"][inw].max())
    ddP1u = panel(P1d, PERIODS["full"], cP1)["maxdd"]
    annP1u = panel(P1d, t12, cP1)["ann"]
    P_(f"{'target':<10}{'object':<16}{'scale':>8}{'PEAK ctr':>10}{'time-wtd':>10}"
       f"{'max DD':>12}{'worst wk':>11}")
    mrows = []
    for tgt in (150_000, 175_000, 300_000):
        s = tgt / annP1u
        fp = panel(P1d, PERIODS["full"], cP1)
        P_(f"{tgt:<10,}{'P1':<16}{s:>8.2f}{s*pkP1:>10.1f}{s*twP1:>10.3f}"
           f"{s*fp['maxdd']:>12,.0f}{s*fp['worst']:>11,.0f}")
        mrows.append(dict(target=tgt, obj="P1", scale=s, peak=s * pkP1, tw=s * twP1,
                          maxdd=s * fp["maxdd"], worst=s * fp["worst"]))
        for nb, nx in [(1, 1), (1, 2), (2, 3)]:
            v = nb * BMd + nx * X9d
            cw = LINES["candidate-specific WORKING"](nb, nx)
            a = panel(v, t12, cw); f_ = panel(v, PERIODS["full"], cw)
            s2_ = tgt / a["ann"]
            tot = nb * posu["BMOM"] + nx * posu["X9a"]
            nm = f"{nb} BMOM:{nx} X9a"
            P_(f"{'':<10}{nm:<16}{s2_:>8.2f}{s2_*tot[inw].max():>10.1f}"
               f"{s2_*tot[inw].mean():>10.3f}{s2_*f_['maxdd']:>12,.0f}"
               f"{s2_*f_['worst']:>11,.0f}")
            mrows.append(dict(target=tgt, obj=nm, scale=s2_, peak=s2_ * tot[inw].max(),
                              tw=s2_ * tot[inw].mean(), maxdd=s2_ * f_["maxdd"],
                              worst=s2_ * f_["worst"]))
        P_("")
    pd.DataFrame(mrows).to_csv(os.path.join(OUT, "matched_income.csv"), index=False)
    P_("    scale is a CONTINUOUS multiplier and only integer rungs are executable; the")
    P_("    executable rungs are the ladder in PHASE 3. This table exists to compare RISK at")
    P_("    equal income, which is the owner's stated objective, not to propose a size.")

    P_(f"\n[done {_time.time()-t0:.0f}s]")
    out.close()


if __name__ == "__main__":
    main()
