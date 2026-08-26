"""WE_W38 (spec preregistered): a SHORT-SPECIFIC quality score, and the regime alternative.

The short sleeve has only ever been graded with the LONG side's feature signs (a mirror).
This wave lets the data choose both the features and their signs on the short entries
themselves (Q1), and preregisters the competing explanation - that the short side's problem
is a drift tax concentrated in particular hours, needing a restriction not a score (Q2).

Feature screen and hour restriction are derived on SEL (2022-07 -> 2024-07) ONLY; every
quoted number comes from EVAL (2024-07 -> 2026-08). Scores use trailing-entry quantiles.
"""
from __future__ import annotations

import os
import sys
import time as _time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_we_w01 as W1                                                  # noqa: E402
from run_we_w01 import ROOT, PV, COMM_RT, STRESS_RT, sm14_1m             # noqa: E402
from run_we_w03 import cd_signals                                        # noqa: E402
from run_we_w17 import load_deep                                         # noqa: E402
from run_we_w19 import MEMBERS, QS, weekly, sharpe                       # noqa: E402
from run_we_w26 import fills_daily                                       # noqa: E402
from run_we_w35 import fills_qexit                                       # noqa: E402
from run_we_w37 import causal_score                                      # noqa: E402
from we_quality import build_context                                     # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W38_SHORTQ", "out")
os.makedirs(OUT, exist_ok=True)
A = np.datetime64("2022-07-01")
SPLIT = np.datetime64("2024-07-01")
B = np.datetime64("2026-08-01")
RNG = np.random.default_rng(20260838)
MINHIST = 100
WIN = 250


# --------------------------------------------------------------------------- fills
def sfills(D, dir_arr, size_at_entry=None, halt=1300.0, target=1000.0, block=None):
    """Signed fills (long or short) with per-entry size and an optional new-entry block."""
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
        if want != 0 and p == 0 and block is not None and block[i]:
            want = 0
        if want != p:
            if p != 0:
                pnl = p * u * (o[i] - epx) * PV - COMM_RT * u
                trades.append(dict(d=p, u=u, et=str(t[eti]), xt=str(t[i]), pnl=pnl))
                spnl += pnl
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
            trades.append(dict(d=p, u=u, et=str(t[eti]), xt=str(t[i]), pnl=pnl))
            p = 0; u = 0
    return trades


# --------------------------------------------------------------------------- signal
def targets(D):
    """sm14_1m targets per member set, cached (keyed on bar count + a close checksum)."""
    key = f"{D['n']}_{int(abs(D['c']).sum())}"
    TG = {}
    for k, v in MEMBERS.items():
        f = os.path.join(OUT, f"tg_{k}_{key}.npy")
        if os.path.exists(f):
            TG[k] = np.load(f)
            continue
        TG[k] = sm14_1m(D, 460, return_targets=True, volmults=v)
        np.save(f, TG[k])
        print(f"   targets {k} built", flush=True)
    return TG


def vote(TG, D, X, side):
    """Identical construction to we_quality.long_vote / short_vote, with cached targets."""
    vs = []
    for mem in MEMBERS:
        tg = TG[mem]
        for q in QS:
            okv = np.ones(D["n"], bool) if q is None else ((X["norm"] <= 0) | (X["ratio"] >= q))
            for dg in (True, False):
                a = okv & (X["dL"] if side > 0 else X["dS"]) if dg else okv
                hit = (tg > 0) if side > 0 else (tg < 0)
                vs.append(np.where(hit & a, 1, 0).astype(np.int8))
    return np.vstack(vs).mean(axis=0)


# --------------------------------------------------------------------------- features
def extra_features(D, X):
    """The 11 candidates beyond the five the long score already uses. All lagged."""
    n = D["n"]
    c, o, h, l, v = D["c"], D["o"], D["h"], D["l"], D["v"]
    idx = np.arange(n)
    _, cd = cd_signals(D)
    volnorm = pd.Series(v).rolling(240, min_periods=30).mean().values
    lag = lambda a: np.concatenate([[a[0]], a[:-1]])                     # noqa: E731
    atr_l = X["atr_l"]
    F = {}
    F["delta_signed"] = lag(cd / np.maximum(volnorm, 1e-9))
    atr_med = pd.Series(atr_l).rolling(6900, min_periods=1000).mean().values
    F["atr_rel"] = atr_l / np.maximum(atr_med, 1e-9)
    F["ratio"] = X["ratio"]
    rng_ = X["ratio"] * X["norm"]                                        # realised range i-1
    F["sess_extension"] = rng_ / np.maximum(atr_l, 1e-9)
    c_l = lag(c)
    F["mom60"] = (c_l - np.concatenate([[c[0]] * 61, c[:-61]])) / np.maximum(atr_l, 1e-9)
    gap = np.zeros(n); bso = np.zeros(n); prng = np.zeros(n)
    sess_rng = np.zeros(D["n_sess"])
    prev_c = np.nan
    for s in range(D["n_sess"]):
        m = idx[D["sid"] == s]
        sess_rng[s] = h[m].max() - l[m].min()
        g = (o[m[0]] - prev_c) if not np.isnan(prev_c) else 0.0
        gap[m] = g / max(atr_l[m[0]], 1e-9)
        bso[m] = np.arange(len(m))
        prev_c = c[m[-1]]
    prm = pd.Series(sess_rng).rolling(20, min_periods=5).mean().shift(1).values
    prev_rel = np.concatenate([[1.0], sess_rng[:-1] / np.maximum(prm[1:], 1e-9)])
    prev_rel = np.nan_to_num(prev_rel, nan=1.0)
    prng = prev_rel[D["sid"]]
    F["gap_prev_close"] = gap
    F["bars_since_open"] = bso
    F["prev_range_rel"] = prng
    mins = ((D["t"] - D["t"].astype("datetime64[D]")).astype("timedelta64[s]")
            .astype(np.int64) // 60)
    ang = 2 * np.pi * mins / 1440.0
    F["hour_sin"] = np.sin(ang)
    F["hour_cos"] = np.cos(ang)
    upb = (np.diff(c, prepend=c[0]) > 0).astype(float)
    F["upvol_share"] = lag(pd.Series(upb).rolling(60, min_periods=20).mean().values)
    for k in F:
        F[k] = np.nan_to_num(F[k], nan=0.0, posinf=0.0, neginf=0.0)
    return F


def pool(X, F):
    P = {k: X[k] for k in ("dist_open", "dist_vwap", "prev_ret", "runlen", "delta_mag")}
    P.update(F)
    return P


# --------------------------------------------------------------------------- screen
def screen(P, ent_i, pnl, tmin=2.0):
    """SEL-only screen: each feature at BOTH signs; admit on |t| and both-half consistency."""
    half = len(ent_i) // 2
    rows = []
    for name, arr in P.items():
        vals = arr[ent_i].astype(float)
        for sgn in (+1, -1):
            sv = sgn * vals
            thr = np.nanquantile(sv, 2 / 3)
            fav = sv >= thr
            if fav.sum() < 40 or (~fav).sum() < 40:
                continue
            a, b = pnl[fav], pnl[~fav]
            se = np.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b))
            eff = a.mean() - b.mean()
            t = eff / se if se > 0 else 0.0
            h1 = np.zeros(len(ent_i), bool); h1[:half] = True
            e1 = e2 = np.nan
            for msk, tag in ((h1, 1), (~h1, 2)):
                fa, re = fav & msk, (~fav) & msk
                if fa.sum() >= 15 and re.sum() >= 15:
                    e = pnl[fa].mean() - pnl[re].mean()
                    if tag == 1:
                        e1 = e
                    else:
                        e2 = e
            ok = (t >= tmin) and (e1 > 0) and (e2 > 0)
            rows.append(dict(feature=name, sign=sgn, n_fav=int(fav.sum()),
                             eff=round(float(eff), 2), t=round(float(t), 2),
                             eff_h1=round(float(e1), 2) if e1 == e1 else None,
                             eff_h2=round(float(e2), 2) if e2 == e2 else None,
                             admit=bool(ok)))
    df = pd.DataFrame(rows).sort_values("t", ascending=False)
    adm = df[df["admit"]]
    best = {}
    for _, r in adm.iterrows():
        if r["feature"] not in best or r["t"] > best[r["feature"]]["t"]:
            best[r["feature"]] = r
    return df, [(r["feature"], int(r["sign"])) for r in best.values()]


def causal_short_score(P, ent_i, feats, window=WIN, q=2 / 3):
    """Score each entry from the quantiles of the PRIOR `window` entries only."""
    vals = {k: (s * P[k][ent_i].astype(float)) for k, s in feats}
    n_ent = len(ent_i)
    sc_ent = np.full(n_ent, np.nan)
    for j in range(n_ent):
        if j < MINHIST:
            continue
        lo = max(0, j - window)
        s = 0
        for k, _ in feats:
            hist = vals[k][lo:j]
            s += vals[k][j] >= np.nanquantile(hist, q)
        sc_ent[j] = s
    return sc_ent


# --------------------------------------------------------------------------- main
def main():
    t0 = _time.time()
    D = load_deep("2022-01-01", "2026-07-31 17:00")
    W1.DEV_END = pd.Timestamp("2026-07-31").date()
    n, tarr = D["n"], D["t"]
    print(f"bars {n:,} sessions {D['n_sess']:,} [{_time.time()-t0:.0f}s]", flush=True)
    X = build_context(D)
    TG = targets(D)
    wkmap = {s: D["wk"][s] for s in range(D["n_sess"])}

    def wk_of(ts):
        i = int(min(np.searchsorted(tarr, ts), n - 1))
        return wkmap[int(D["sid"][i])]

    def nsess(a, b):
        m = (tarr >= a) & (tarr < b)
        return len(np.unique(D["sid"][m]))
    NS_EVAL, NS_FULL = nsess(SPLIT, B), nsess(A, B)

    out = open(os.path.join(OUT, "shortq.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out)

    # ---------------- B1 harness check: reproduce W37's long P2 -------------------
    P_("=== B1 HARNESS CHECK (must reproduce W37 long P2: 13.50 pts/session, Sharpe 0.291) ===")
    posL = (vote(TG, D, X, +1) >= 0.5).astype(np.int8)
    baseL = fills_daily(D, posL, halt=1300, target=1000)
    baseL_in = [x for x in baseL if A <= np.datetime64(x["et"]) < B]
    entL = np.array([int(min(np.searchsorted(tarr, np.datetime64(x["et"])), n - 1))
                     for x in baseL_in])
    holdsL = np.array([(np.datetime64(x["xt"]) - np.datetime64(x["et"]))
                       / np.timedelta64(1, "m") for x in baseL_in])
    scL, _ = causal_score(X, entL, window=WIN)
    szL = np.where(scL >= 3, 2, 1).astype(np.int8)
    medh = []; runm = []
    for j in range(len(entL)):
        runm.append(holdsL[j])
        medh.append(float(np.median(runm[-250:])) if j >= MINHIST else 0.0)
    cutb = int(np.median([m for m in medh if m > 0]))
    P2 = fills_qexit(D, posL, szL, scL, cut_bars=cutb)
    dP2 = weekly(P2, wk_of, A, B); sP2, _, _ = sharpe(dP2)
    pP2 = np.array([x["pnl"] for x in P2 if A <= np.datetime64(x["et"]) < B])
    ptsP2 = pP2.sum() / PV / NS_FULL
    ok = abs(ptsP2 - 13.50) < 0.6 and abs(sP2 - 0.291) < 0.03
    P_(f"   cut bars derived = {cutb} (W37: 23) | pts/session {ptsP2:.2f} | Sharpe {sP2:.3f}"
       f"  -> {'PASS' if ok else 'FAIL - RUN VOID'}")
    if not ok:
        out.close(); return

    # ---------------- short base --------------------------------------------------
    posS = -(vote(TG, D, X, -1) >= 0.5).astype(np.int8)
    S0 = sfills(D, posS)
    chk = fills_daily(D, posS, halt=1300, target=1000)
    same = (len(chk) == len(S0) and
            abs(sum(x["pnl"] for x in chk) - sum(x["pnl"] for x in S0)) < 1e-6)
    P_(f"   sfills vs fills_daily on the short base: {'IDENTICAL' if same else 'MISMATCH'}")
    if not same:
        P_("   -> fill-layer mismatch, run VOID"); out.close(); return

    rows = []
    hdr = (f"{'arm':<32}{'n':>6}{'avgSz':>7}{'pts/ses':>9}{'$/tr':>8}{'wkMean':>9}{'wk+%':>7}"
           f"{'worst':>10}{'sharpe':>7}{'wk/|wst|':>9}{'stress':>8}")

    def rep(nm, trl, a, b, ns, ref=None, quiet=False):
        d = weekly(trl, wk_of, a, b)
        s, _, wp = sharpe(d)
        v = np.array(list(d.values())) if d else np.array([0.0])
        p = np.array([x["pnl"] for x in trl if a <= np.datetime64(x["et"]) < b])
        u = np.array([x.get("u", 1) for x in trl if a <= np.datetime64(x["et"]) < b])
        if len(p) == 0:
            p = np.array([0.0]); u = np.array([1])
        eff = v.mean() / abs(v.min()) if v.min() < 0 else float("inf")
        st = float((v - STRESS_RT * len(p) / max(len(v), 1)).mean())
        tag = ""
        r = dict(arm=nm, n=len(p), avg_size=round(float(u.mean()), 2),
                 pts=round(float(p.sum() / PV / ns), 2), per_trade=round(float(p.mean()), 1),
                 wk=round(float(v.mean())), pos=round(wp, 1), worst=round(float(v.min())),
                 sharpe=round(s, 3), eff=round(float(eff), 3), stress=round(st))
        if ref is not None:
            okk = (r["pts"] > ref["pts"] and r["eff"] >= ref["eff"]
                   and r["worst"] >= ref["worst"] * 1.02 and st > 0)
            tag = "  ADOPT?" if okk else "  reject"
            r["passes"] = okk
        if not quiet:
            P_(f"{nm:<32}{len(p):>6}{u.mean():>7.2f}{p.sum()/PV/ns:>9.2f}{p.mean():>8.1f}"
               f"{v.mean():>9,.0f}{wp:>7.1f}{v.min():>10,.0f}{s:>7.3f}{eff:>9.3f}"
               f"{st:>8,.0f}{tag}")
        rows.append(r)
        return r

    # ---------------- SEL screen ---------------------------------------------------
    F = extra_features(D, X)
    P = pool(X, F)
    S0_sel = [x for x in S0 if A <= np.datetime64(x["et"]) < SPLIT]
    ent_sel = np.array([int(min(np.searchsorted(tarr, np.datetime64(x["et"])), n - 1))
                        for x in S0_sel])
    pnl_sel = np.array([x["pnl"] for x in S0_sel])
    P_(f"\n=== SEL SCREEN ({len(ent_sel)} short entries 2022-07 -> 2024-07, "
       f"{len(P)} candidates x 2 signs) ===")
    df_scr, feats = screen(P, ent_sel, pnl_sel)
    df_scr.to_csv(os.path.join(OUT, "screen.csv"), index=False)
    P_(df_scr.head(14).to_string(index=False))
    P_(f"\n   ADMITTED (max-t sign per feature): {feats}")
    K = len(feats)
    kmaj = K // 2 + 1
    P_(f"   K = {K} features -> majority rule k >= {kmaj} (derived, not chosen)")

    # hour buckets, SEL only
    hrs = ((tarr - tarr.astype("datetime64[D]")).astype("timedelta64[s]")
           .astype(np.int64) // 3600)
    hs = hrs[ent_sel]
    bad = []
    P_("\n   SEL hour buckets (ET), short base:")
    line = []
    for hh in range(24):
        m = hs == hh
        if m.sum() >= 30:
            mu = pnl_sel[m].mean()
            line.append(f"{hh:02d}h n={m.sum():>4} ${mu:>7.1f}")
            if mu < 0:
                bad.append(hh)
    for j in range(0, len(line), 4):
        P_("     " + " | ".join(line[j:j + 4]))
    P_(f"   blocked hours (SEL mean < 0, n>=30): {bad}")
    blk = np.isin(hrs, bad) if bad else np.zeros(n, bool)

    # ---------------- scores on all entries ---------------------------------------
    S0_all = [x for x in S0 if A <= np.datetime64(x["et"]) < B]
    ent_all = np.array([int(min(np.searchsorted(tarr, np.datetime64(x["et"])), n - 1))
                        for x in S0_all])
    P_(f"\n   scoring {len(ent_all)} short entries causally (trailing {WIN}) "
       f"[{_time.time()-t0:.0f}s]")
    sc_ent = causal_short_score(P, ent_all, feats)
    sc_arr = np.zeros(n)
    okm = ~np.isnan(sc_ent)
    sc_arr[ent_all[okm]] = sc_ent[okm]
    sz_arr = np.where(sc_arr >= kmaj, 2, 1).astype(np.int8)

    mir = [("dist_open", -1), ("prev_ret", +1), ("runlen", -1),
           ("dist_vwap", -1), ("delta_mag", +1)]
    sc_m = causal_short_score(P, ent_all, mir)
    scm_arr = np.zeros(n)
    okm2 = ~np.isnan(sc_m)
    scm_arr[ent_all[okm2]] = sc_m[okm2]
    szm_arr = np.where(scm_arr >= 3, 2, 1).astype(np.int8)

    arms = {
        "S0 base short": (posS, None, None),
        "S1 mirror score": (posS, szm_arr, None),
        "S2 short-specific score": (posS, sz_arr, None),
        "S3 hour restriction": (posS, None, blk),
        "S4 S2 + S3": (posS, sz_arr, blk),
    }
    for wname, (a, b, ns) in (("EVAL (honest)", (SPLIT, B, NS_EVAL)),
                              ("FULL (selection-contaminated)", (A, B, NS_FULL))):
        P_(f"\n=== SHORT ARMS on {wname} ===")
        P_(hdr)
        ref = None
        for nm, (dr, sz, bk) in arms.items():
            trl = sfills(D, dr, size_at_entry=sz, block=bk)
            r = rep(f"{nm} [{wname.split()[0]}]", trl, a, b, ns, ref=ref)
            if ref is None:
                ref = r

    # ---------------- null on the best passing short arm --------------------------
    ev = [r for r in rows if r["arm"].endswith("[EVAL]")]
    base_ev = ev[0]
    cand = [r for r in ev[1:] if r.get("passes")]
    best = max(cand, key=lambda r: r["eff"]) if cand else None
    if best is None:
        P_("\n=== NO SHORT ARM PASSES ON EVAL -> preregistered falsifier fires ===")
    else:
        P_(f"\n=== NULL (binding) on {best['arm']}: 100 circular shifts ===")
        use_sz = sz_arr if "S2" in best["arm"] or "S4" in best["arm"] else (
            szm_arr if "S1" in best["arm"] else None)
        use_bk = blk if "S3" in best["arm"] or "S4" in best["arm"] else None
        nulls = []
        for j in range(100):
            off = int(RNG.integers(20_000, n - 20_000))
            szn = np.roll(use_sz, off) if use_sz is not None else None
            bkn = np.roll(use_bk, off) if use_bk is not None else None
            trl = sfills(D, posS, size_at_entry=szn, block=bkn)
            d = weekly(trl, wk_of, SPLIT, B)
            v = np.array(list(d.values()))
            nulls.append(v.mean() / abs(v.min()) if v.min() < 0 else 9.9)
            if (j + 1) % 25 == 0:
                print(f"   nulls {j+1}/100 [{_time.time()-t0:.0f}s]", flush=True)
        nulls = np.array(nulls)
        pct = 100.0 * (nulls < best["eff"]).mean()
        verdict = "EVIDENCE" if pct >= 95 else ("weak" if pct >= 80 else "NOT EVIDENCE")
        P_(f"   real wk/|worst| {best['eff']:.3f} | null mean {nulls.mean():.3f} | "
           f"p95 {np.percentile(nulls,95):.3f} | percentile {pct:.1f} | "
           f"p {(nulls>=best['eff']).mean():.3f} -> {verdict}")
        rows.append(dict(arm="NULL " + best["arm"], pts=None, sharpe=None,
                         eff=round(float(nulls.mean()), 3), worst=None,
                         stress=None, n=100, pos=round(pct, 1)))

    # ---------------- C1 combined portfolio ---------------------------------------
    P_("\n=== C1 COMBINED PORTFOLIO (long P2 + short arm), EVAL window ===")
    P_(hdr)
    rep("C1a long P2 alone [EVAL]", P2, SPLIT, B, NS_EVAL)
    show = ["S0 base short"] + ([best["arm"].replace(" [EVAL]", "")] if best else [])
    for nm in show:
        dr, sz, bk = arms[nm]
        trl = sfills(D, dr, size_at_entry=sz, block=bk)
        rep(f"C1 P2 + {nm.split()[0]} [EVAL]", P2 + trl, SPLIT, B, NS_EVAL)

    pd.DataFrame(rows).to_csv(os.path.join(OUT, "summary.csv"), index=False)
    out.close()
    print(f"done [{_time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
