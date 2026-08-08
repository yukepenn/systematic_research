"""W5-C1 CLEAN/deep entry — frozen spec research/scalping_lab/specs/W5_programs_wave.md
section C1 (Amendment 6, frozen before readout 2026-08-08). Seed 20260808.

Mechanical distinction from killed W3-1 (raw immediate fade): (a) interaction gate
depth x efficiency x flow, (b) recovery-confirmation entry (NOT entry at trigger).

Frozen rule (LONG; SHORT symmetric via sign-flipped space):
  trigger at second t (decision second = RTH & quote-alive):
      ret30 = mid(t) - mid(t-30)  <= -D            (D=12 primary, 16 neighbor)
      eff60 = |mid(t)-mid(t-60)| / sum_{trailing 60}|1s dmid|  >= 0.12
      sflow10 = trailing-10s sum of sflow          <= 0
  entry NOT at trigger: WAIT for recovery tick = first second u in (t, t+60] with
      mid_last(u) >= trailing-30s low(u) + 2t
      else cancel at t+60. Enter at the recovery-tick second's mid_last (market).

  Frozen-text ambiguity, resolved and documented (w5c1_report.md): the spec does not
  name the series for "trailing-30s low". Both readings are run:
    lowsrc="close": rolling 30s min of mid_last (incl. current second)  [PRIMARY —
        the wick-based reading makes the recovery gate a no-op (~100% entry rate,
        ~1.3s mean lag), which contradicts the spec's stated mechanical distinction
        from killed W3-1; close-based makes the confirmation real]
    lowsrc="wick":  rolling 30s min of mid_low                          [sensitivity]
  Brackets (A,B) in {(20,6),(24,8),(32,10)} ticks; cap 300s; cooldown 30s; sequential.

House conventions (w31_snapback / w4a_fss1):
  - grid1s LEFT JOIN sechilo on time, ffill mid_last, fill hi/lo with mid_last,
    drop leading NaN.
  - decision seconds: tod in [9:30, 16:00) ET AND trailing-60s (bid_upd+ask_upd)>0.
  - recovery crossing on a dead second kills the setup (no chase), as in W4-A.
  - market entry: barrier evaluation starts the second AFTER entry; same second both
    barriers crossed -> adverse. Cap exit at mid_last(t_entry+300).
  - costs C1=2.872t, C2=4.872t RT; session (day-clustered) bootstrap, 1000 reps,
    seed 20260808, resample sessions, episode-count weighted.
"""
import glob, os
import numpy as np, pandas as pd
from numba import njit

DS = [12, 16]                        # D=12 primary, 16 frozen neighbor
BRK = [(20.0, 6.0), (24.0, 8.0), (32.0, 10.0)]
CAP = 300
COOL = 30
RWIN = 60                            # recovery window after trigger (s)
RECT = 2.0                           # recovery ticks above trailing-30s low
EFFMIN = 0.12
C1, C2 = 2.872, 4.872
SEED = 20260808

@njit(cache=True)
def simulate(y, yhi, ylo, low30, dec, trig, A, B, cap, cool, rwin, rect):
    """Sequential episode machine in direction-flipped space (long space).
    Returns per-episode (outcome 1 tgt/2 adv/3 cap, gross ticks, entry idx, lag s)
    plus counters: triggers processed, recoveries entered, cancels (window expired),
    dead-second kills."""
    n = y.shape[0]
    e_out = np.empty(n, np.int8); e_g = np.empty(n, np.float64)
    e_te = np.empty(n, np.int64); e_lag = np.empty(n, np.int64)
    m = 0; n_trig = 0; n_dead = 0; n_exp = 0
    t = 0
    while t < n - 1:
        if not (dec[t] and trig[t]):
            t += 1
            continue
        n_trig += 1
        # --- wait for recovery tick within rwin s of trigger ---
        end_r = t + rwin
        if end_r > n - 1: end_r = n - 1
        te = -1
        nxt = end_r + 1
        u = t + 1
        while u <= end_r:
            if y[u] >= low30[u] + rect:      # recovery crossing
                if dec[u]:
                    te = u
                else:
                    n_dead += 1              # dead second -> kill setup
                nxt = u + 1
                break
            u += 1
        if te < 0:
            if u > end_r:
                n_exp += 1                   # window expired, no recovery
            t = nxt
            continue
        entry = y[te]
        # --- barrier resolution: starts second AFTER entry; both crossed -> adverse ---
        end = te + cap
        if end > n - 1: end = n - 1
        res = 0; i = te + 1
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
        e_out[m] = res; e_g[m] = g; e_te[m] = te; e_lag[m] = te - t; m += 1
        t = i + cool
    return e_out[:m], e_g[:m], e_te[:m], e_lag[:m], n_trig, n_dead, n_exp

SH = "research/scalping_lab/substrate/sechilo/NQ"
GR = "research/scalping_lab/substrate/grid1s/NQ"
OUTD = "research/scalping_lab/artifacts/w5_c1"
os.makedirs(OUTD, exist_ok=True)

rows = []
sessions = sorted(os.path.basename(p)[:-8] for p in glob.glob(os.path.join(SH, "s*.parquet")))
print(f"W5-C1 CLEAN/deep entry | sessions={len(sessions)} | seed={SEED}")
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
    ret30 = mls.diff(30).values
    ret60 = mls.diff(60).values
    tv60 = mls.diff().abs().rolling(60).sum().values
    with np.errstate(divide="ignore", invalid="ignore"):
        eff60 = np.abs(ret60) / tv60
    effok = np.where(np.isnan(eff60), False, eff60 >= EFFMIN)
    sflow10 = pd.Series(f["sflow"].values.astype(np.float64)).rolling(10).sum().values
    for dname, dv in (("long", 1.0), ("short", -1.0)):
        y = ml * dv
        yhi = hi if dv > 0 else -lo
        ylo = lo if dv > 0 else -hi
        low30_close = pd.Series(y).rolling(30, min_periods=1).min().values
        low30_wick = pd.Series(ylo).rolling(30, min_periods=1).min().values
        rety30 = ret30 * dv
        sfy = sflow10 * dv
        for D in DS:
            trig = (rety30 <= -D) & effok & (sfy <= 0)
            trig = np.where(np.isnan(rety30) | np.isnan(sflow10), False, trig).astype(np.bool_)
            for lowsrc, low30 in (("close", low30_close), ("wick", low30_wick)):
                for (A, B) in BRK:
                    eo, eg, ete, elag, ntr, ndead, nexp = simulate(
                        y, yhi, ylo, low30, dec, trig, A, B, CAP, COOL, RWIN, RECT)
                    rows.append(dict(session=tag, lowsrc=lowsrc, D=D, dir=dname,
                                     A=int(A), B=int(B),
                                     n_trig=ntr, n_dead=ndead, n_exp=nexp, n=len(eo),
                                     n_tgt=int((eo == 1).sum()), n_adv=int((eo == 2).sum()),
                                     n_cap=int((eo == 3).sum()), gross_sum=float(eg.sum()),
                                     lag_sum=int(elag.sum())))
    print(tag, "done", flush=True)

R = pd.DataFrame(rows)
R.to_csv(os.path.join(OUTD, "w5c1_by_session.csv"), index=False)
NSESS = len(sessions)

CEN = pd.read_csv("research/scalping_lab/artifacts/census/excursion_surface.csv")

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
for lowsrc in ("close", "wick"):
    for D in DS:
        for dname in ("long", "short"):
            for (A, B) in BRK:
                gsel = R[(R.lowsrc == lowsrc) & (R.D == D) & (R.dir == dname) &
                         (R.A == int(A)) & (R.B == int(B))]
                n_trig = int(gsel.n_trig.sum()); n_dead = int(gsel.n_dead.sum())
                n_exp = int(gsel.n_exp.sum())
                ge = gsel[gsel.n > 0]
                n = int(ge.n.sum())
                cen = CEN[(CEN.A == int(A)) & (CEN.B == int(B)) & (CEN.dir == dname)].iloc[0]
                base = dict(lowsrc=lowsrc, D=D, dir=dname, A=int(A), B=int(B),
                            sessions=NSESS,
                            n_trig=n_trig, n_dead=n_dead, n_exp=n_exp,
                            census_p=float(cen.p_target), census_gap_c1=float(cen.gap_c1),
                            be_c1=(B + C1) / (A + B), be_c2=(B + C2) / (A + B))
                if n == 0:
                    prows.append(dict(**base, unique_days=0, episodes=0, epi_per_day=np.nan,
                                      entry_rate=np.nan, mean_lag=np.nan, p_tgt=np.nan,
                                      n_tgt=0, n_adv=0, n_cap=0, lift_pp=np.nan,
                                      gross_per_trade=np.nan, net_c1=np.nan, ci_lo=np.nan,
                                      ci_hi=np.nan, net_c2=np.nan, passes=False))
                    continue
                ud = int(ge.session.nunique())
                ntgt = int(ge.n_tgt.sum()); nadv = int(ge.n_adv.sum()); ncap = int(ge.n_cap.sum())
                gpt = float(ge.gross_sum.sum()) / n
                p_tgt = ntgt / max(1, ntgt + nadv)
                net1 = gpt - C1; net2 = gpt - C2
                per = (ge.gross_sum / ge.n - C1).values.astype(float)
                wts = ge.n.values.astype(float)
                lo_, hi_ = boot_ci(per, wts)
                prows.append(dict(**base, unique_days=ud, episodes=n, epi_per_day=n / ud,
                                  entry_rate=n / n_trig if n_trig else np.nan,
                                  mean_lag=float(ge.lag_sum.sum()) / n,
                                  p_tgt=p_tgt, n_tgt=ntgt, n_adv=nadv, n_cap=ncap,
                                  lift_pp=100 * (p_tgt - float(cen.p_target)),
                                  gross_per_trade=gpt, net_c1=net1, ci_lo=lo_, ci_hi=hi_,
                                  net_c2=net2, passes=bool((net1 > 0) and (lo_ > -0.5))))
P = pd.DataFrame(prows)
P.to_csv(os.path.join(OUTD, "w5c1_pooled.csv"), index=False)

for lowsrc, lbl in (("close", "PRIMARY reading: low = rolling 30s min of mid_last"),
                    ("wick", "SENSITIVITY reading: low = rolling 30s min of mid_low")):
    print(f"\n=== W5-C1 pooled — lowsrc={lowsrc} ({lbl}) ===")
    print("(sequential, market entry at recovery tick; net C1=2.872t, C2=4.872t)")
    print(f"{'D':>3} {'dir':>5} {'A':>3} {'B':>3} | {'trig':>5} {'exp':>5} {'dead':>4} "
          f"{'epi':>5} {'e/d':>6} {'days':>4} {'lag':>5} | {'P(tgt)':>7} {'census':>7} "
          f"{'lift_pp':>7} {'BE_C1':>6} | {'netC1':>7} {'CI_lo':>7} {'CI_hi':>7} | "
          f"{'netC2':>7} {'PASS':>4}")
    for _, r in P[P.lowsrc == lowsrc].iterrows():
        star = " *" if r.D == 12 else ""
        if r.episodes == 0:
            print(f"{r.D:>3} {r['dir']:>5} {r.A:>3} {r.B:>3} | {r.n_trig:>5} {r.n_exp:>5} "
                  f"{r.n_dead:>4} {0:>5}  (no episodes){star}")
            continue
        print(f"{r.D:>3} {r['dir']:>5} {r.A:>3} {r.B:>3} | {r.n_trig:>5} {r.n_exp:>5} "
              f"{r.n_dead:>4} {r.episodes:>5} {r.epi_per_day:>6.2f} {r.unique_days:>4} "
              f"{r.mean_lag:>5.1f} | {r.p_tgt:>7.4f} {r.census_p:>7.4f} {r.lift_pp:>+7.2f} "
              f"{r.be_c1:>6.4f} | {r.net_c1:>+7.3f} {r.ci_lo:>+7.3f} {r.ci_hi:>+7.3f} | "
              f"{r.net_c2:>+7.3f} {'PASS' if r.passes else 'fail':>4}{star}")
print("\n(* = primary D=12; D=16 = frozen robustness neighbor, reported never selected on)")
print("(trig = triggers processed; exp = recovery window expired, no entry; dead = "
      "recovery on dead second, killed; lag = mean seconds trigger->recovery entry; "
      "lift_pp = P(tgt) - unconditional census p_target, in percentage points; "
      "PASS = net_C1>0 AND CI_lo>-0.5t)")

print("\n=== long+short combined per (lowsrc, D, bracket) — diagnostic only ===")
for lowsrc in ("close", "wick"):
    for D in DS:
        for (A, B) in BRK:
            gsel = R[(R.lowsrc == lowsrc) & (R.D == D) & (R.A == int(A)) & (R.B == int(B))]
            n = int(gsel.n.sum())
            if n == 0: continue
            gpt = float(gsel.gross_sum.sum()) / n
            gs = gsel.groupby("session").agg(gross_sum=("gross_sum", "sum"), n=("n", "sum"))
            gs = gs[gs.n > 0]
            per = (gs.gross_sum / gs.n - C1).values.astype(float)
            wts = gs.n.values.astype(float)
            lo_, hi_ = boot_ci(per, wts)
            ntgt = int(gsel.n_tgt.sum()); nadv = int(gsel.n_adv.sum())
            print(f"  {lowsrc:>5} D={D:>2} +{int(A)}/-{int(B)}: epi={n:>5} "
                  f"P(tgt)={ntgt/max(1,ntgt+nadv):.4f} netC1={gpt-C1:+.3f}t "
                  f"CI=[{lo_:+.3f},{hi_:+.3f}] netC2={gpt-C2:+.3f}t")

for lowsrc in ("close", "wick"):
    sub = P[P.lowsrc == lowsrc]
    print(f"\npassing configs lowsrc={lowsrc} (frozen rule net_C1>0 AND CI_lo>-0.5t): "
          f"{int(sub.passes.sum())} / {len(sub)}")
print("\nW5C1 DONE")
