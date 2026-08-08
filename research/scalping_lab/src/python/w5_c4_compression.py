"""W5-C4 — FSS-6 compression->expansion + FSS-7 velocity/low-retracement.
Frozen spec: research/scalping_lab/specs/W5_programs_wave.md section C4 (frozen before
readout, 2026-08-08). Thresholds are frozen; nothing here was tuned.

House conventions (w31_snapback.py / w4a_fss1.py): 37 L2 discovery sessions,
sechilo+grid1s merge (grid LEFT JOIN sechilo on time, ffill mid_last, fill hi/lo with
mid_last, drop leading NaN), 1s clock, RTH = [09:30, 16:00) ET from tag date,
quote-alive = trailing 60s (bid_upd+ask_upd) sum > 0, sequential episode simulation,
conservative same-second-both-crossed -> adverse barrier rule, session (day-clustered)
bootstrap CIs, seed 20260808, 1000 reps. C1=2.872t RT, C2=4.872t.

Frozen-spec interpretation notes (documented in w5c4_report.md):
- FSS-6 compression window = trailing 120 seconds ENDING AT t-1 (rolling 120 on
  mid_high/mid_low, shift 1, full window required). Including t would make a boundary
  break impossible (mid_last[t] <= mid_high[t] <= window max), so shift-1 is forced.
  Compression: range = max(mid_high) - min(mid_low) <= 8t over that window.
- FSS-6 trigger (long): ret10 = mid_last[t] - mid_last[t-10] >= +6t AND
  mid_last[t] > comp_high (strict break). Short symmetric (ret10 <= -6t AND
  mid_last[t] < comp_low). Entry = market at mid_last[t] at the trigger second
  (delay 0, house convention). Long/short triggers are mutually exclusive by
  construction (ret10 cannot be both >= +6 and <= -6).
- FSS-7 move start = first second of the current same-sign ret20 regime, i.e. the
  second after the most recent second where ret20 (= mid_last[t]-mid_last[t-20])
  was of opposite sign, zero, or NaN ("last second where 20s ret sign flipped").
- FSS-7 (long): running extreme E(t) = max(mid_last[ms..t]); base = mid_last[ms];
  displacement = E - base (require > 0); retrace = E - mid_last[t];
  trigger: ret20 >= +12t AND retrace/displacement <= 0.25. Short symmetric.
  All signals on mid_last; mid_high/mid_low reserved for barrier evaluation (house).
- Sequential PER FAMILY: one timeline per (family, bracket) — long and short share
  it; an open episode blocks all entries; cooldown 60s applies to both dirs.
- Unconditional surface baseline = canonical census excursion_surface.csv
  (artifacts/census/, 30s RTH decision clock, same 37 sessions, same brackets);
  its rows for (24,8)/(32,10) are echoed into this run's artifacts.
"""
import glob, os
import numpy as np, pandas as pd
from numba import njit

BRK = [(24.0, 8.0), (32.0, 10.0)]
CAP = 300
COOL = 60
C1, C2 = 2.872, 4.872
SEED = 20260808
REPS = 1000

# FSS-6 frozen thresholds
F6_WIN = 120          # compression window (s)
F6_RNG = 8.0          # max range (ticks)
F6_RETW = 10          # expansion ret window (s)
F6_RETT = 6.0         # expansion |ret| threshold (ticks)
# FSS-7 frozen thresholds
F7_RETW = 20          # velocity ret window (s)
F7_RETT = 12.0        # velocity threshold (ticks)
F7_RMAX = 0.25        # max retracement ratio


@njit(cache=True)
def fss7_trigs(ml, ret20, thr, rmax):
    """Regime-tracked FSS-7 triggers. Regime = maximal run of strictly-positive
    (long) / strictly-negative (short) ret20; zero or NaN ret20 resets both."""
    n = ml.shape[0]
    trigL = np.zeros(n, np.bool_)
    trigS = np.zeros(n, np.bool_)
    pos_on = False; Epos = 0.0; Bpos = 0.0
    neg_on = False; Eneg = 0.0; Bneg = 0.0
    for t in range(n):
        r = ret20[t]
        if np.isnan(r):
            pos_on = False; neg_on = False
            continue
        if r > 0.0:
            if not pos_on:
                pos_on = True; Epos = ml[t]; Bpos = ml[t]
            elif ml[t] > Epos:
                Epos = ml[t]
            if r >= thr:
                disp = Epos - Bpos
                if disp > 0.0 and (Epos - ml[t]) <= rmax * disp:
                    trigL[t] = True
        else:
            pos_on = False
        if r < 0.0:
            if not neg_on:
                neg_on = True; Eneg = ml[t]; Bneg = ml[t]
            elif ml[t] < Eneg:
                Eneg = ml[t]
            if r <= -thr:
                disp = Bneg - Eneg
                if disp > 0.0 and (ml[t] - Eneg) <= rmax * disp:
                    trigS[t] = True
        else:
            neg_on = False
    return trigL, trigS


@njit(cache=True)
def simulate(ml, hi, lo, dec, trigL, trigS, A, B, cap, cool):
    """One sequential pass per (family, bracket): long+short share the timeline.
    Entry at ml[t] on the trigger second; barriers evaluated from t+1 (market
    entry, house convention); same-second both crossed -> adverse; cap -> MTM.
    Returns per-episode: index, dir (+1/-1), outcome (1 tgt/2 adv/3 cap), gross."""
    n = ml.shape[0]
    e_idx = np.empty(n, np.int64); e_dir = np.empty(n, np.int8)
    e_out = np.empty(n, np.int8); e_g = np.empty(n, np.float64)
    m = 0; t = 0
    while t < n - 1:
        if dec[t] and (trigL[t] or trigS[t]):
            dv = 1.0 if trigL[t] else -1.0
            entry = ml[t]
            end = t + cap
            if end > n - 1: end = n - 1
            res = 0; i = t + 1
            while i <= end:
                up = hi[i] - entry; dn = entry - lo[i]
                if dv > 0.0:
                    th = up >= A; ah = dn >= B
                else:
                    th = dn >= A; ah = up >= B
                if th and ah: res = 2; break
                if ah: res = 2; break
                if th: res = 1; break
                i += 1
            if res == 1:
                g = A
            elif res == 2:
                g = -B
            else:
                res = 3; g = (ml[end] - entry) * dv; i = end
            e_idx[m] = t; e_dir[m] = 1 if dv > 0.0 else -1
            e_out[m] = res; e_g[m] = g; m += 1
            t = i + cool
        else:
            t += 1
    return e_idx[:m], e_dir[:m], e_out[:m], e_g[:m]


SH = "research/scalping_lab/substrate/sechilo/NQ"
GR = "research/scalping_lab/substrate/grid1s/NQ"
OUTD = "research/scalping_lab/artifacts/w5_c4"
CENSUS = "research/scalping_lab/artifacts/census/excursion_surface.csv"
os.makedirs(OUTD, exist_ok=True)

rows = []
sessions = sorted(os.path.basename(p)[:-8] for p in glob.glob(os.path.join(SH, "s*.parquet")))
print(f"W5-C4 FSS-6/FSS-7 | sessions={len(sessions)} | seed={SEED} | "
      f"brackets={[(int(a),int(b)) for a,b in BRK]} | cap={CAP}s cool={COOL}s")
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
    dec = ((tod >= 9 * 3600 + 1800) & (tod < 16 * 3600) & (upd60 > 0)).astype(np.bool_)
    mls = pd.Series(ml)

    # --- FSS-6 triggers ---
    comp_hi = pd.Series(hi).rolling(F6_WIN, min_periods=F6_WIN).max().shift(1).values
    comp_lo = pd.Series(lo).rolling(F6_WIN, min_periods=F6_WIN).min().shift(1).values
    comp_rng = comp_hi - comp_lo
    ret10 = mls.diff(F6_RETW).values
    ok = ~(np.isnan(comp_rng) | np.isnan(ret10))
    f6L = ok & (comp_rng <= F6_RNG) & (ret10 >= F6_RETT) & (ml > comp_hi)
    f6S = ok & (comp_rng <= F6_RNG) & (ret10 <= -F6_RETT) & (ml < comp_lo)
    f6L = f6L.astype(np.bool_); f6S = f6S.astype(np.bool_)

    # --- FSS-7 triggers ---
    ret20 = mls.diff(F7_RETW).values
    f7L, f7S = fss7_trigs(ml, ret20, F7_RETT, F7_RMAX)

    trigmap = {"FSS6": (f6L, f6S), "FSS7": (f7L, f7S)}
    for fam, (tL, tS) in trigmap.items():
        ntrigL = int((tL & dec).sum()); ntrigS = int((tS & dec).sum())
        for (A, B) in BRK:
            ei, ed, eo, eg = simulate(ml, hi, lo, dec, tL, tS, A, B, CAP, COOL)
            for dname, dv in (("long", 1), ("short", -1)):
                msk = ed == dv
                rows.append(dict(session=tag, family=fam, A=int(A), B=int(B),
                                 dir=dname,
                                 n_trig=ntrigL if dv == 1 else ntrigS,
                                 n=int(msk.sum()),
                                 n_tgt=int(((eo == 1) & msk).sum()),
                                 n_adv=int(((eo == 2) & msk).sum()),
                                 n_cap=int(((eo == 3) & msk).sum()),
                                 gross_sum=float(eg[msk].sum())))
    print(tag, "done", flush=True)

R = pd.DataFrame(rows)
R.to_csv(os.path.join(OUTD, "w5c4_by_session.csv"), index=False)
NSESS = len(sessions)

# --- unconditional surface baseline (canonical census; echoed into artifacts) ---
U = pd.read_csv(CENSUS)
U = U[U.A.isin([24, 32]) & U.B.isin([8, 10])].reset_index(drop=True)
U.to_csv(os.path.join(OUTD, "w5c4_baseline_echo.csv"), index=False)
print("\n=== unconditional surface baseline (census excursion_surface.csv, echoed) ===")
print(U.to_string(index=False))
ULOOK = {(int(r.A), int(r.B), r["dir"]): (float(r.p_target), float(r.be_c1), float(r.gap_c1))
         for _, r in U.iterrows()}


def boot_ci(per, wts, reps=REPS):
    """Session bootstrap: resample sessions (day-clustered), episode-count weighted."""
    rng = np.random.default_rng(SEED)
    idx = np.arange(len(per))
    boots = np.empty(reps)
    for r in range(reps):
        b = rng.choice(idx, len(idx), replace=True)
        boots[r] = np.average(per[b], weights=wts[b])
    return float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))


prows = []
for fam in ("FSS6", "FSS7"):
    for (A, B) in BRK:
        for dname in ("long", "short"):
            gsel = R[(R.family == fam) & (R.A == int(A)) & (R.B == int(B)) & (R.dir == dname)]
            n_trig = int(gsel.n_trig.sum())
            ge = gsel[gsel.n > 0]
            n = int(ge.n.sum())
            p_unc, be1, gap_unc = ULOOK[(int(A), int(B), dname)]
            base = dict(family=fam, A=int(A), B=int(B), dir=dname, sessions=NSESS,
                        n_trig=n_trig, p_uncond=p_unc, be_c1=be1, gap_c1_uncond=gap_unc)
            if n == 0:
                prows.append(dict(**base, unique_days=0, episodes=0, epi_per_day=np.nan,
                                  p_tgt=np.nan, n_tgt=0, n_adv=0, n_cap=0,
                                  gross_per_trade=np.nan, net_c1=np.nan, ci_lo_c1=np.nan,
                                  ci_hi_c1=np.nan, net_c2=np.nan, ci_lo_c2=np.nan,
                                  ci_hi_c2=np.nan, lift_pp=np.nan, gap_c1_family=np.nan,
                                  passes=False))
                continue
            ud = int(ge.session.nunique())
            ntgt = int(ge.n_tgt.sum()); nadv = int(ge.n_adv.sum()); ncap = int(ge.n_cap.sum())
            gpt = float(ge.gross_sum.sum()) / n
            net1 = gpt - C1; net2 = gpt - C2
            per = (ge.gross_sum / ge.n - C1).values.astype(float)
            wts = ge.n.values.astype(float)
            lo_, hi_ = boot_ci(per, wts)
            ptgt = ntgt / max(1, ntgt + nadv)
            prows.append(dict(**base, unique_days=ud, episodes=n, epi_per_day=n / ud,
                              p_tgt=ptgt, n_tgt=ntgt, n_adv=nadv, n_cap=ncap,
                              gross_per_trade=gpt, net_c1=net1, ci_lo_c1=lo_, ci_hi_c1=hi_,
                              net_c2=net2, ci_lo_c2=lo_ - (C2 - C1), ci_hi_c2=hi_ - (C2 - C1),
                              lift_pp=100 * (ptgt - p_unc), gap_c1_family=be1 - ptgt,
                              passes=bool((net1 > 0) and (lo_ > -0.5))))
P = pd.DataFrame(prows)
P.to_csv(os.path.join(OUTD, "w5c4_pooled.csv"), index=False)

print("\n=== W5-C4 pooled — sequential per (family, bracket), 60s cooldown, cap 300s ===")
print(f"{'fam':>5} {'A':>3} {'B':>3} {'dir':>5} | {'trig':>6} {'epi':>5} {'e/d':>6} {'days':>4} | "
      f"{'P(tgt)':>7} {'cap':>4} {'P_unc':>7} {'lift_pp':>7} | {'netC1':>7} {'CI_lo':>7} {'CI_hi':>7} | "
      f"{'netC2':>7} | {'BE_C1':>6} {'gapF':>7} {'PASS':>4}")
for _, r in P.iterrows():
    if r.episodes == 0:
        print(f"{r.family:>5} {r.A:>3} {r.B:>3} {r['dir']:>5} | {r.n_trig:>6} {0:>5}  (no episodes)")
        continue
    print(f"{r.family:>5} {r.A:>3} {r.B:>3} {r['dir']:>5} | {r.n_trig:>6} {r.episodes:>5} "
          f"{r.epi_per_day:>6.2f} {r.unique_days:>4} | {r.p_tgt:>7.4f} {r.n_cap:>4} "
          f"{r.p_uncond:>7.4f} {r.lift_pp:>+7.2f} | {r.net_c1:>+7.3f} {r.ci_lo_c1:>+7.3f} "
          f"{r.ci_hi_c1:>+7.3f} | {r.net_c2:>+7.3f} | {r.be_c1:>6.4f} {r.gap_c1_family:>+7.4f} "
          f"{'PASS' if r.passes else 'fail':>4}")
print("(P_unc/BE_C1 from canonical census surface; lift_pp = 100*(P(tgt)-P_unc); "
      "gapF = BE_C1 - P(tgt), positive = still below break-even; "
      "PASS = net_c1>0 AND CI_lo_c1>-0.5t; CI_C2 = CI_C1 - 2.000t exactly)")

npass = int(P.passes.sum())
print(f"\npassing configs (frozen rule): {npass} / {len(P)}")
for fam in ("FSS6", "FSS7"):
    sub = P[P.family == fam]
    print(f"family {fam}: {int(sub.passes.sum())}/{len(sub)} cells pass; "
          f"net_c1 range [{sub.net_c1.min():+.3f}, {sub.net_c1.max():+.3f}] t; "
          f"max CI_hi_c1 {sub.ci_hi_c1.max():+.3f} t; episodes total {int(sub.episodes.sum())}")
print("\nW5C4 DONE")
