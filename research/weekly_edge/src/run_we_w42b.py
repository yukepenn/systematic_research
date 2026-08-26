"""WE_W42 amendment 1 — LOOK-AHEAD CORRECTION, found in self-review of read 1.

Read 1's E2/E3 updated the running MAE/MFE with bar i's OWN high/low and then exited at bar
i's OPEN. That admits a fill at a price the trigger could not have been known at. It is the
same error as W03's gate and it had already produced headline numbers (E2 at Sharpe 0.465,
the highest in campaign history). Those arms are VOID.

The corrected construction is also the one that would actually be traded: a RESTING ORDER at a
level that is known before the bar trades.
  E2  a stop at epx - (winners' trailing median MAE) x ATR_at_entry, the level fixed at entry
  E3  a trailing stop at epx + MFE(through bar i-1) x (1 - winners' trailing median give-back)
Both fill AT the level, or at the open if the bar gaps through it. And after any stop-out,
RE-ENTRY IS BLOCKED until the vote target returns to zero - without that the object re-enters
on the very next bar and the stop is economically a no-op (read 1's trade count nearly doubled
for exactly this reason).

E1 was also degenerate in read 1: it could only exit EARLIER, never later, because `want` came
from a position array already zeroed at vote < 0.5. Here the position array itself is rebuilt
with entry at >= 0.5 and hold while >= the exit threshold.

Phase 1's diagnostic is unaffected and stands.
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
from run_we_w01 import ROOT, PV, COMM_RT, STRESS_RT                      # noqa: E402
from run_we_w17 import load_deep                                         # noqa: E402
from run_we_w19 import weekly                                            # noqa: E402
from run_we_w26 import fills_daily                                       # noqa: E402
from run_we_w35 import fills_qexit                                       # noqa: E402
from run_we_w37 import causal_score                                      # noqa: E402
from run_we_w38 import targets, vote                                     # noqa: E402
from run_we_w39 import WIN                                               # noqa: E402
from run_we_w42 import OUT, A, B, MINHIST                                # noqa: E402
from we_quality import build_context                                     # noqa: E402

RNG = np.random.default_rng(2026421)


def fills_rest(D, pos_arr, size_at_entry, score, halt=1300.0, target=1000.0,
               stop_atr=None, atr=None, trail_gb=None, cut_bars=None, cut_max_score=1,
               partial_thr=None, block_reentry=True):
    """Frozen entries; exits via signal at the open, then RESTING orders inside the bar.

    stop_atr[i]  : distance in ATR for a stop fixed at entry      (level known at entry)
    trail_gb[i]  : give-back fraction of the running MFE          (level known at bar start)
    partial_thr[i]: points at which one contract leaves on a limit (level known at entry)
    """
    t, o, c, h, l = D["t"], D["o"], D["c"], D["h"], D["l"]
    fb, lb, n = D["fb"], D["lb"], D["n"]
    trades = []
    u = 0; epx = 0.0; eti = -1; spnl = 0.0; stopped = False; blocked = False
    ent_sc = 0; mfe_prev = 0.0; took = False
    s_lvl = None; gb = None; p_lvl = None
    for i in range(n):
        if fb[i]:
            spnl = 0.0; stopped = False; blocked = False
        want = int(pos_arr[i - 1]) if i > 0 and not fb[i] else 0
        if stopped:
            want = 0
        if blocked:
            if want == 0:
                blocked = False
            else:
                want = 0
        if u > 0 and want > 0 and cut_bars is not None and ent_sc <= cut_max_score \
                and i - eti >= cut_bars:
            want = 0
        # --- 1. signal-driven fills at the OPEN ---------------------------------------
        if (want > 0) != (u > 0):
            if u > 0:
                pnl = u * (o[i] - epx) * PV - COMM_RT * u
                trades.append(dict(d=1, u=u, et=str(t[eti]), xt=str(t[i]), pnl=pnl))
                spnl += pnl
                if spnl <= -halt or (target is not None and spnl >= target):
                    stopped = True; want = 0
                u = 0
            if want > 0:
                u = int(size_at_entry[i]); epx, eti = o[i], i
                ent_sc = int(score[i]); mfe_prev = 0.0; took = False
                a0 = float(atr[i]) if atr is not None else 1.0
                s_lvl = (epx - float(stop_atr[i]) * a0) if (
                    stop_atr is not None and np.isfinite(stop_atr[i])) else None
                gb = float(trail_gb[i]) if (
                    trail_gb is not None and 0 < trail_gb[i] < 1) else None
                p_lvl = (epx + float(partial_thr[i])) if (
                    partial_thr is not None and np.isfinite(partial_thr[i])) else None
                if u < 1:
                    u = 0
        # --- 2. resting orders inside bar i, at levels known before it trades ---------
        if u > 0:
            if p_lvl is not None and u >= 2 and not took and h[i] >= p_lvl:
                px = max(o[i], p_lvl)
                pnl = (px - epx) * PV - COMM_RT
                trades.append(dict(d=1, u=1, et=str(t[eti]), xt=str(t[i]), pnl=pnl))
                spnl += pnl; u -= 1; took = True
            lvl = -np.inf
            if s_lvl is not None:
                lvl = max(lvl, s_lvl)
            if gb is not None and mfe_prev > 0:
                lvl = max(lvl, epx + mfe_prev * (1.0 - gb))
            if np.isfinite(lvl) and l[i] <= lvl:
                px = min(o[i], lvl)
                pnl = u * (px - epx) * PV - COMM_RT * u
                trades.append(dict(d=1, u=u, et=str(t[eti]), xt=str(t[i]), pnl=pnl))
                spnl += pnl; u = 0
                if block_reentry:
                    blocked = True
                if spnl <= -halt or (target is not None and spnl >= target):
                    stopped = True
            else:
                mfe_prev = max(mfe_prev, h[i] - epx)
        if lb[i] and u > 0:
            pnl = u * (c[i] - epx) * PV - COMM_RT * u
            trades.append(dict(d=1, u=u, et=str(t[eti]), xt=str(t[i]), pnl=pnl))
            u = 0
    return trades


def main():
    t0 = _time.time()
    D = load_deep("2022-01-01", "2026-07-31 17:00")
    W1.DEV_END = pd.Timestamp("2026-07-31").date()
    n, tarr = D["n"], D["t"]
    X = build_context(D)
    TG = targets(D)
    atr = np.maximum(X["atr_l"], 1e-9)
    wkmap = {s: D["wk"][s] for s in range(D["n_sess"])}

    def i_of(ts):
        return int(min(np.searchsorted(tarr, np.datetime64(ts)), n - 1))

    def wk_of(ts):
        return wkmap[int(D["sid"][i_of(ts)])]
    NS = len(np.unique(D["sid"][(tarr >= A) & (tarr < B)]))
    out = open(os.path.join(OUT, "exits_b.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out)

    vfrac = vote(TG, D, X, +1)
    posL = (vfrac >= 0.5).astype(np.int8)
    baseL = fills_daily(D, posL, halt=1300, target=1000)
    bl = [x for x in baseL if A <= np.datetime64(x["et"]) < B]
    entL = np.array([i_of(x["et"]) for x in bl])
    scQ0, _ = causal_score(X, entL, window=WIN)
    szQ0 = np.where(scQ0 >= 3, 2, 1).astype(np.int8)
    P1 = fills_qexit(D, posL, szQ0, scQ0)
    ref_pts = np.array([x["pnl"] for x in P1
                        if A <= np.datetime64(x["et"]) < B]).sum() / PV / NS
    same = fills_rest(D, posL, szQ0, scQ0)
    d1 = abs(sum(x["pnl"] for x in same) - sum(x["pnl"] for x in P1))
    P_(f"=== B1: P1 {ref_pts:.2f} pts/session (expect 14.72) | fills_rest with no exit rules "
       f"== fills_qexit: {'IDENTICAL' if d1 < 1e-6 and len(same) == len(P1) else 'MISMATCH'} "
       f"[{_time.time()-t0:.0f}s]")
    if abs(ref_pts - 14.72) >= 0.6 or d1 >= 1e-6:
        out.close(); return

    # trade paths, for the derived trailing thresholds (phase 1 of read 1, unchanged)
    tr = [x for x in P1 if A <= np.datetime64(x["et"]) < B]
    stop_atr = np.full(n, np.nan); gbv = np.full(n, np.nan); part = np.full(n, np.nan)
    w_mae, w_gb, w_mfe = [], [], []
    for j, x in enumerate(tr):
        e, xi = i_of(x["et"]), i_of(x["xt"])
        if xi <= e:
            xi = min(e + 1, n - 1)
        px = D["o"][e]
        mfe = float(D["h"][e:xi + 1].max() - px); mae = float(D["l"][e:xi + 1].min() - px)
        real = x["pnl"] / PV / x.get("u", 1)
        if j >= MINHIST:
            if w_mae:
                stop_atr[e] = float(np.median(w_mae[-250:]))
            if w_gb:
                gbv[e] = float(np.median(w_gb[-250:]))
            if w_mfe:
                part[e] = float(np.median(w_mfe[-250:]))
        if real > 0:
            w_mae.append(abs(mae) / float(atr[e]))
            if mfe > 1e-9:
                w_gb.append(max(0.02, min(0.98, (mfe - real) / mfe)))
            w_mfe.append(mfe)
    P_(f"   derived (trailing 250 winners): stop {np.nanmedian(stop_atr[entL]):.2f} ATR | "
       f"give-back {np.nanmedian(gbv[entL]):.3f} | partial {np.nanmedian(part[entL]):.1f} pts")

    keys = sorted(weekly(P1, wk_of, A, B))

    def wvec(trl):
        d = weekly(trl, wk_of, A, B)
        return np.array([d.get(x, 0.0) for x in keys])
    rows = []
    hdr = (f"{'arm':<36}{'n':>6}{'sz':>5}{'pts':>7}{'$/tr':>8}{'wk$':>8}{'wk+%':>6}"
           f"{'worst':>9}{'CVaR5':>9}{'shrp':>7}{'eff':>7}{'cvEff':>7}{'stress':>8}")

    def rep(nm, trl, ref=None):
        v = wvec(trl)
        pp = np.array([x["pnl"] for x in trl if A <= np.datetime64(x["et"]) < B])
        uu = np.array([x.get("u", 1) for x in trl if A <= np.datetime64(x["et"]) < B])
        if len(pp) == 0:
            pp, uu = np.array([0.0]), np.array([1])
        nw = max(1, int(np.ceil(0.05 * len(v))))
        cv = float(np.sort(v)[:nw].mean())
        s = float(v.mean() / v.std(ddof=1)) if v.std(ddof=1) > 0 else 0.0
        eff = float(v.mean() / abs(v.min())) if v.min() < 0 else 9.9
        cve = float(v.mean() / abs(cv)) if cv < 0 else 9.9
        st = float(v.mean() - STRESS_RT * len(pp) / len(v))
        r = dict(arm=nm, n=len(pp), avg_size=round(float(uu.mean()), 2),
                 pts=round(float(pp.sum() / PV / NS), 2), wk=round(float(v.mean())),
                 worst=round(float(v.min())), cvar5=round(cv), sharpe=round(s, 3),
                 eff=round(eff, 3), cveff=round(cve, 3), stress=round(st))
        tag = ""
        if ref is not None:
            r["passes"] = bool(eff > ref["eff"] and cve > ref["cveff"] and st > 0)
            tag = "  PASS" if r["passes"] else "  reject"
        P_(f"{nm:<36}{r['n']:>6}{r['avg_size']:>5.2f}{r['pts']:>7.2f}{pp.mean():>8.1f}"
           f"{r['wk']:>8,.0f}{100*(v>0).mean():>6.1f}{r['worst']:>9,.0f}{r['cvar5']:>9,.0f}"
           f"{r['sharpe']:>7.3f}{r['eff']:>7.3f}{r['cveff']:>7.3f}{r['stress']:>8,.0f}{tag}")
        rows.append(r); return r

    P_(f"\n=== CORRECTED ARMS: resting orders, re-entry blocked after a stop "
       f"[{_time.time()-t0:.0f}s] ===")
    P_(hdr)
    ref = rep("P1 incumbent (reference)", P1)
    rep("P2 incumbent + 23-bar cut", fills_rest(D, posL, szQ0, scQ0, cut_bars=23), ref)
    rep("E2 stop at winners' median MAE",
        fills_rest(D, posL, szQ0, scQ0, stop_atr=stop_atr, atr=atr), ref)
    rep("E2b same, re-entry ALLOWED (control)",
        fills_rest(D, posL, szQ0, scQ0, stop_atr=stop_atr, atr=atr, block_reentry=False), ref)
    rep("E3 trailing give-back stop",
        fills_rest(D, posL, szQ0, scQ0, trail_gb=gbv, atr=atr), ref)
    rep("E3b same, re-entry ALLOWED (control)",
        fills_rest(D, posL, szQ0, scQ0, trail_gb=gbv, atr=atr, block_reentry=False), ref)
    rep("E2+E3 both stops",
        fills_rest(D, posL, szQ0, scQ0, stop_atr=stop_atr, trail_gb=gbv, atr=atr), ref)
    rep("E4 stops on high-score entries only",
        fills_rest(D, posL, szQ0, scQ0, cut_bars=23,
                   stop_atr=np.where(scQ0 >= 3, stop_atr, np.nan), atr=atr), ref)
    rep("E5 partial at winners' median MFE",
        fills_rest(D, posL, szQ0, scQ0, partial_thr=part), ref)

    # E1, rebuilt properly: enter at >= 0.5, HOLD while >= the exit threshold
    P_(f"\n=== E1 rebuilt: entry at vote >= 0.50, HOLD while vote >= x "
       f"(read 1's version was degenerate) ===")
    P_(hdr)
    for ev in (0.25, 0.3125, 0.375, 0.4375):
        pa = np.zeros(n, np.int8); held = 0
        for i in range(n):
            if D["fb"][i]:
                held = 0
            if held == 0 and vfrac[i] >= 0.5:
                held = 1
            elif held == 1 and vfrac[i] < ev:
                held = 0
            pa[i] = held
        ent2 = np.array([i_of(x["et"]) for x in fills_daily(D, pa, halt=1300, target=1000)
                         if A <= np.datetime64(x["et"]) < B])
        sc2, _ = causal_score(X, ent2, window=WIN)
        rep(f"E1 hold while vote >= {ev:.4f}",
            fills_rest(D, pa, np.where(sc2 >= 3, 2, 1).astype(np.int8), sc2), ref)

    cand = [r for r in rows if r.get("passes")]
    if not cand:
        P_("\n=== NO CORRECTED EXIT MECHANISM CLEARS -> falsifier fires ===")
    else:
        best = max(cand, key=lambda r: r["eff"])
        P_(f"\n=== BINDING NULLS on {best['arm']} [{_time.time()-t0:.0f}s] ===")
        P_("    N2 = exit the same NUMBER of trades early, at randomly chosen bars-in-trade")
        base_eff = best["eff"]
        nl = []
        n_stopped = 0
        for j in range(100):
            rnd = np.full(n, np.nan)
            rnd[entL] = RNG.choice(np.array(w_mae[-250:]) if w_mae else [1.0],
                                   size=len(entL), replace=True)
            v = wvec(fills_rest(D, posL, szQ0, scQ0, stop_atr=rnd, atr=atr))
            nl.append(v.mean() / abs(v.min()) if v.min() < 0 else 9.9)
            if (j + 1) % 50 == 0:
                print(f"   nulls {j+1}/100 [{_time.time()-t0:.0f}s]", flush=True)
        nu = np.array(nl)
        pct = 100.0 * (nu < base_eff).mean()
        P_(f"   N2 randomised stop distance   real {base_eff:.3f} | null mean {nu.mean():.3f} "
           f"| p95 {np.percentile(nu,95):.3f} | pctile {pct:.1f} | "
           f"p {(nu>=base_eff).mean():.3f} -> "
           f"{'EVIDENCE' if pct>=95 else ('weak' if pct>=80 else 'NOT EVIDENCE')}")
    pd.DataFrame(rows).to_csv(os.path.join(OUT, "summary_b.csv"), index=False)
    out.close()
    print(f"done [{_time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
