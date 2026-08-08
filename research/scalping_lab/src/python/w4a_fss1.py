"""W4-A FSS-1: impulse -> shallow pullback -> rebreak (Zone F).
Frozen spec: research/scalping_lab/specs/W4_alpha_wave1.md section W4-A (committed
before readout). Sequential episode simulation, conservative same-second-both-crossed
-> adverse barrier rule, session (day-clustered) bootstrap CIs, seed 20260808, 1000 reps.

Frozen-spec interpretation notes (documented in w4a_report.md):
- Impulse detect on decision seconds only (RTH & quote-alive): ret_w = mid(t)-mid(t-w)
  >= I AND ret_w >= 0.5*TV_w (identical to ret/TV >= 0.5 since TV >= |ret| > 0 there).
- IH = running max of mid from impulse second, tracked up to 30s; pullback starts at the
  first second with depth d = IH - mid in [3t, 0.5*I]; d > 0.6*I cancels the setup and
  the cancel is enforced in BOTH the tracking window and the rebreak window; IH is
  frozen at pullback start (a new high after that IS the rebreak).
- Rebreak: mid > IH (strict) within 60s of pullback start -> MARKET entry at that
  second's mid (delay 0, house convention). Entries only on decision seconds; a
  crossing on a dead second kills the setup (no chase).
- PASSIVE: limit L = IH - 0.4*I armed from pullback start; fills checked from the NEXT
  second (order placed at the pullback-detection second's close -- no same-second
  lookahead fill); strict trade-through mid_low < L - 1t; within a second the fill
  check precedes the rebreak/cancel checks (price passes through the resting limit on
  the way down); fills only on decision seconds; barrier evaluation INCLUDES the fill
  second (conservative). Entry price = L. Cost C1p = 1.872t.
- PASSIVE STRESS (C2p_lite): identical fill logic, entry price shifted 1 tick adverse
  (entry = L + 1t in direction space), brackets measured from the shifted entry,
  friction 1.872t -> the 1t stress is applied 'via price' for ~2.872t total.
- Shorts simulated in sign-flipped space: y = -mid, y_hi = -mid_low, y_lo = -mid_high.
"""
import glob, os
import numpy as np, pandas as pd
from numba import njit

WS = [30, 15]                      # w=30 primary, w=15 neighbor
ILIST = [12, 8, 16]                # I=12 primary, 8/16 neighbors (full w x I grid run)
BRK = [(24.0, 8.0), (32.0, 10.0)]
CAP = 300
COOL = 30
TRACK = 30                         # IH tracking / pullback window (s)
REWIN = 60                         # rebreak window from pullback start (s)
DMIN = 3.0                         # minimum pullback depth (ticks)
C1, C2 = 2.872, 4.872              # market-market RT costs
C1P = 1.872                        # passive entry / market exit RT cost
SEED = 20260808

@njit(cache=True)
def simulate(y, yhi, ylo, dec, trig, I, A, B, passive, stress):
    """One sequential pass. Returns per-episode outcome (1 tgt/2 adv/3 cap), gross
    ticks, plus counters: impulses detected, valid pullbacks."""
    n = y.shape[0]
    e_out = np.empty(n, np.int8); e_g = np.empty(n, np.float64)
    m = 0; n_imp = 0; n_pb = 0
    dmax = 0.5 * I; dcan = 0.6 * I
    t = 0
    while t < n - 1:
        if not (dec[t] and trig[t]):
            t += 1
            continue
        n_imp += 1
        # --- phase 1: track impulse high, find pullback start within TRACK s ---
        IH = y[t]
        end_tr = t + TRACK
        if end_tr > n - 1: end_tr = n - 1
        tp = -1
        nxt = end_tr + 1
        tau = t + 1
        while tau <= end_tr:
            if y[tau] > IH: IH = y[tau]
            d = IH - y[tau]
            if d > dcan:                     # too deep -> cancel
                nxt = tau + 1
                break
            if DMIN <= d <= dmax:            # shallow pullback begins
                tp = tau
                break
            tau += 1
        if tp < 0:
            t = nxt
            continue
        n_pb += 1
        # --- phase 2: rebreak (market) or limit fill (passive) within REWIN s ---
        end_pb = tp + REWIN
        if end_pb > n - 1: end_pb = n - 1
        L = IH - 0.4 * I
        te = -1; entry = 0.0
        nxt = end_pb + 1
        u = tp + 1
        while u <= end_pb:
            if passive == 1:
                if ylo[u] < L - 1.0:         # strict trade-through -> fill at L
                    if dec[u]:
                        te = u
                        entry = L + 1.0 if stress == 1 else L
                    nxt = u + 1
                    break
                if y[u] > IH or IH - y[u] > dcan:   # rebreak w/o fill, or too deep
                    nxt = u + 1
                    break
            else:
                if y[u] > IH:                # rebreak -> market entry this second
                    if dec[u]:
                        te = u; entry = y[u]
                    nxt = u + 1
                    break
                if IH - y[u] > dcan:         # too deep -> cancel
                    nxt = u + 1
                    break
            u += 1
        if te < 0:
            t = nxt
            continue
        # --- barrier resolution (same-second both crossed -> adverse) ---
        start = te if passive == 1 else te + 1   # passive: fill second included
        end = te + CAP
        if end > n - 1: end = n - 1
        res = 0; i = start
        while i <= end:
            up = yhi[i] - entry; dn = entry - ylo[i]
            th = up >= A; ah = dn >= B
            if th and ah: res = 2; break
            if ah: res = 2; break
            if th: res = 1; break
            i += 1
        if res == 1:
            g = A
        elif res == 2:
            g = -B
        else:
            res = 3; g = y[end] - entry; i = end
        e_out[m] = res; e_g[m] = g; m += 1
        t = i + COOL
    return e_out[:m], e_g[:m], n_imp, n_pb

SH = "research/scalping_lab/substrate/sechilo/NQ"
GR = "research/scalping_lab/substrate/grid1s/NQ"
OUTD = "research/scalping_lab/artifacts/w4_fss1"
os.makedirs(OUTD, exist_ok=True)

VARIANTS = (("market", 0, 0), ("passive", 1, 0), ("passive_stress", 1, 1))

rows = []
sessions = sorted(os.path.basename(p)[:-8] for p in glob.glob(os.path.join(SH, "s*.parquet")))
print(f"W4-A FSS-1 | sessions={len(sessions)} | seed={SEED}")
for tag in sessions:
    d0 = pd.to_datetime(tag[1:], format="%Y%m%d")
    g = pd.read_parquet(os.path.join(GR, tag + ".parquet"))
    s = pd.read_parquet(os.path.join(SH, tag + ".parquet"))
    g["time"] = pd.to_datetime(g["time"]); s["time"] = pd.to_datetime(s["time"])
    f = g.merge(s, on="time", how="left")
    f["mid_last"] = f["mid_last"].ffill()
    f = f[f["mid_last"].notna()].reset_index(drop=True)
    f["mid_high"] = f["mid_high"].fillna(f["mid_last"])
    f["mid_low"] = f["mid_low"].fillna(f["mid_last"])
    ml = f["mid_last"].values.astype(np.float64)
    hi = f["mid_high"].values.astype(np.float64)
    lo = f["mid_low"].values.astype(np.float64)
    tod = (f["time"] - d0).dt.total_seconds().values
    upd60 = pd.Series((f["bid_upd"] + f["ask_upd"]).values).rolling(60, min_periods=1).sum().values
    dec = ((tod >= 9*3600+1800) & (tod < 16*3600) & (upd60 > 0)).astype(np.bool_)
    mls = pd.Series(ml)
    adm = mls.diff().abs()
    for w in WS:
        retw = mls.diff(w).values
        tvw = adm.rolling(w).sum().values
        for dname, dv in (("long", 1.0), ("short", -1.0)):
            y = ml * dv
            yhi = hi if dv > 0 else -lo
            ylo = lo if dv > 0 else -hi
            rsy = retw * dv
            for I in ILIST:
                trig = (rsy >= I) & (rsy >= 0.5 * tvw)
                trig = np.where(np.isnan(rsy) | np.isnan(tvw), False, trig).astype(np.bool_)
                for (A, B) in BRK:
                    for vname, pas, stz in VARIANTS:
                        eo, eg, nimp, npb = simulate(y, yhi, ylo, dec, trig,
                                                     float(I), A, B, pas, stz)
                        rows.append(dict(session=tag, variant=vname, w=w, I=I, dir=dname,
                                         A=int(A), B=int(B), n_imp=nimp, n_pb=npb,
                                         n=len(eo), n_tgt=int((eo == 1).sum()),
                                         n_adv=int((eo == 2).sum()),
                                         n_cap=int((eo == 3).sum()),
                                         gross_sum=float(eg.sum())))
    print(tag, "done", flush=True)

R = pd.DataFrame(rows)
R.to_csv(os.path.join(OUTD, "w4a_by_session.csv"), index=False)
NSESS = len(sessions)

def boot_ci(per, wts, reps=1000):
    """Session bootstrap: resample sessions (day-clustered), episode-count weighted."""
    rng = np.random.default_rng(SEED)
    idx = np.arange(len(per))
    boots = np.empty(reps)
    for r in range(reps):
        b = rng.choice(idx, len(idx), replace=True)
        boots[r] = np.average(per[b], weights=wts[b])
    return float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))

prows = []
for vname, cost_main, cost_sec in (("market", C1, C2),
                                   ("passive", C1P, C1P + 1.0),
                                   ("passive_stress", C1P, np.nan)):
    for w in WS:
        for I in ILIST:
            for dname in ("long", "short"):
                for (A, B) in BRK:
                    gsel = R[(R.variant == vname) & (R.w == w) & (R.I == I) &
                             (R.dir == dname) & (R.A == int(A)) & (R.B == int(B))]
                    n_imp = int(gsel.n_imp.sum()); n_pb = int(gsel.n_pb.sum())
                    ge = gsel[gsel.n > 0]
                    n = int(ge.n.sum())
                    base = dict(variant=vname, w=w, I=I, dir=dname, A=int(A), B=int(B),
                                sessions=NSESS, n_imp=n_imp, n_pb=n_pb)
                    if n == 0:
                        prows.append(dict(**base, unique_days=0, episodes=0,
                                          epi_per_day=np.nan, entry_rate=np.nan,
                                          p_tgt=np.nan, n_tgt=0, n_adv=0, n_cap=0,
                                          gross_per_trade=np.nan, net_main=np.nan,
                                          ci_lo=np.nan, ci_hi=np.nan, net_sec=np.nan,
                                          passes=False))
                        continue
                    ud = int(ge.session.nunique())
                    ntgt = int(ge.n_tgt.sum()); nadv = int(ge.n_adv.sum())
                    ncap = int(ge.n_cap.sum())
                    gpt = float(ge.gross_sum.sum()) / n
                    netm = gpt - cost_main
                    nets = gpt - cost_sec if np.isfinite(cost_sec) else np.nan
                    per = (ge.gross_sum / ge.n - cost_main).values.astype(float)
                    wts = ge.n.values.astype(float)
                    lo_, hi_ = boot_ci(per, wts)
                    prows.append(dict(**base, unique_days=ud, episodes=n,
                                      epi_per_day=n / ud,
                                      entry_rate=n / n_pb if n_pb else np.nan,
                                      p_tgt=ntgt / max(1, ntgt + nadv),
                                      n_tgt=ntgt, n_adv=nadv, n_cap=ncap,
                                      gross_per_trade=gpt, net_main=netm,
                                      ci_lo=lo_, ci_hi=hi_, net_sec=nets,
                                      passes=bool((netm > 0) and (lo_ > -0.5))))
P = pd.DataFrame(prows)
P.to_csv(os.path.join(OUTD, "w4a_pooled.csv"), index=False)

def show(vname, cmain_lbl, csec_lbl):
    print(f"\n=== W4-A pooled — {vname} (net_main uses {cmain_lbl}; net_sec {csec_lbl}) ===")
    print(f"{'w':>3} {'I':>3} {'dir':>5} {'A':>3} {'B':>3} | {'imp':>5} {'pb':>5} {'epi':>5} "
          f"{'e/d':>5} {'days':>4} {'fill%':>6} | {'P(tgt)':>7} {'cap':>4} | "
          f"{'net':>7} {'CI_lo':>7} {'CI_hi':>7} | {'net_sec':>7} {'PASS':>4}")
    for _, r in P[P.variant == vname].iterrows():
        star = " *" if (r.w == 30 and r.I == 12) else ""
        if r.episodes == 0:
            print(f"{r.w:>3} {r.I:>3} {r['dir']:>5} {r.A:>3} {r.B:>3} | {r.n_imp:>5} "
                  f"{r.n_pb:>5} {0:>5}  (no episodes){star}")
            continue
        print(f"{r.w:>3} {r.I:>3} {r['dir']:>5} {r.A:>3} {r.B:>3} | {r.n_imp:>5} {r.n_pb:>5} "
              f"{r.episodes:>5} {r.epi_per_day:>5.2f} {r.unique_days:>4} {100*r.entry_rate:>6.1f} | "
              f"{r.p_tgt:>7.4f} {r.n_cap:>4} | {r.net_main:>+7.3f} {r.ci_lo:>+7.3f} "
              f"{r.ci_hi:>+7.3f} | " +
              (f"{r.net_sec:>+7.3f}" if np.isfinite(r.net_sec) else f"{'--':>7}") +
              f" {'PASS' if r.passes else 'fail':>4}{star}")
    print("(* = primary w=30, I=12; fill% = entries/valid-pullbacks; "
          "PASS = net_main>0 AND CI_lo>-0.5t)")

show("market", "C1=2.872t", "C2=4.872t")
show("passive", "C1p=1.872t", "flat 2.872t")
show("passive_stress", "C1p=1.872t on 1t-adverse-shifted entry (C2p_lite ~2.872t)", "n/a")

print("\n=== plateau view: net_main across (w,I) grid, per variant/dir/bracket ===")
for vname in ("market", "passive"):
    for dname in ("long", "short"):
        for (A, B) in BRK:
            cells = []
            for w in WS:
                for I in ILIST:
                    r = P[(P.variant == vname) & (P.w == w) & (P.I == I) &
                          (P.dir == dname) & (P.A == int(A)) & (P.B == int(B))].iloc[0]
                    v = f"{r.net_main:+.2f}" if np.isfinite(r.net_main) else "n/a"
                    cells.append(f"w{w}I{I}:{v}{'P' if r.passes else ''}")
            print(f"{vname:>7} {dname:>5} +{int(A)}/-{int(B)}: " + "  ".join(cells))

npass = int(P[P.variant != "passive_stress"].passes.sum())
print(f"\npassing configs (market+passive, frozen rule): {npass} / "
      f"{len(P[P.variant != 'passive_stress'])}")
print("\nW4A DONE")
