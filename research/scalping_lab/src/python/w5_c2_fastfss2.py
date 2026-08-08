"""W5-C2 fast FSS-2 breakout-acceptance on 15s/30s completed bars.
Frozen spec: research/scalping_lab/specs/W5_programs_wave.md section C2 (committed
before readout). Sequential episode simulation, conservative same-second-both-crossed
-> adverse barrier rule, session (day-clustered) bootstrap CIs, seed 20260808, 1000 reps.
Mechanical distinction from killed 1-min S2a: 4-8x faster clock (15s/30s bars),
acceptance-close grammar (no pullback-bar requirement).

Frozen-spec interpretation notes (documented in w5c2_report.md):
- Bars: wall-clock-aligned K-second bars (K=15,30) from the merged 1s frame; bar id =
  floor(seconds-from-tag-date / K), so bars align to :00/:15/:30/:45. O = first-second
  mid_last, H = max(mid_high), L = min(mid_low), C = last-second mid_last. Only
  COMPLETED bars (exactly K seconds present) are eligible as breakout or acceptance
  bars; the 1s grid is complete so only edge bars can be partial.
- LONG breakout bar j: C[j] > max(H[j-20..j-1]) (strict, prior 20 bars, full history
  required) AND bar range > 0 (zero-range bars skipped) AND close-location
  (C-L)/(H-L) >= 0.7 AND the bar's CLOSE second is a decision second (RTH & quote-
  alive). SHORT symmetric (simulated in sign-flipped space: y=-mid, yhi=-mid_low,
  ylo=-mid_high; flipped-bar Hf=-L, Lf=-H, Cf=-C makes the code identical).
- Acceptance configs: acc=1 -> next 1 completed bar closes above the broken level
  (strict); acc=2 -> next 2 completed bars BOTH close above the level. Each acceptance
  bar's close second must also be a decision second, else the setup cancels.
- Acceptance-phase high AH = max(mid-bar high) over the acceptance bars only (not the
  breakout bar). Entry trigger: 1s mid >= AH + 1t (the +1t buffer supplies the
  crossing strictness), scanned STRICTLY AFTER the last acceptance bar's close second
  (from tc+1), within 120s (u <= tc+120) else cancel. Market entry at that second's
  mid, delay 0 (house convention); a crossing on a dead (non-decision) second kills
  the setup (no chase, per W4-A house pattern).
- Barriers evaluated from te+1 (market entry); same-second both-crossed -> adverse.
  Cap 300s -> mark-to-mid gross. Cooldown 60s after episode resolution.
- One trade per breakout + sequential: a 1s busy pointer advances past every consumed
  setup (acceptance-fail second+1, entry-window end+1, dead-cross second+1, or
  resolve+cooldown); breakout bars whose close second precedes the pointer are skipped.
"""
import glob, os
import numpy as np, pandas as pd
from numba import njit

KS = [15, 30]                      # bar clocks (seconds)
ACCS = [1, 2]                      # acceptance configs: 1-bar and 2-bar
BRK = [(24.0, 8.0), (32.0, 10.0)]
LOOK = 20                          # prior-bar lookback for the broken level
CLMIN = 0.7                        # close-location minimum
CAP = 300
COOL = 60
EWIN = 120                         # entry window (s) after acceptance close
C1, C2 = 2.872, 4.872
SEED = 20260808

@njit(cache=True)
def simulate(y, yhi, ylo, dec, bC, bH, bLvl, bTrig, bCloseIdx, bLen, K,
             nacc, A, B, cap, cool, ewin):
    """One sequential pass over bars (flipped space for shorts).
    Returns per-episode outcome (1 tgt/2 adv/3 cap), gross ticks, entry 1s index,
    plus counters: breakouts considered, acceptances completed, dead-second-cross
    kills, no-cross cancels."""
    nb = bC.shape[0]; n = y.shape[0]
    e_out = np.empty(nb, np.int8); e_g = np.empty(nb, np.float64)
    e_idx = np.empty(nb, np.int64)
    m = 0; n_brk = 0; n_acc = 0; n_dead = 0; n_nox = 0
    ptr = 0
    j = 0
    while j < nb:
        if (not bTrig[j]) or bCloseIdx[j] < ptr:
            j += 1
            continue
        n_brk += 1
        # --- acceptance phase: next nacc completed bars all close above level ---
        ok = True
        AH = -1.0e18
        tc = -1
        fail_ptr = -1
        for a in range(1, nacc + 1):
            jb = j + a
            if jb >= nb:
                ok = False
                break
            if bLen[jb] != K or (not dec[bCloseIdx[jb]]) or not (bC[jb] > bLvl[j]):
                ok = False
                fail_ptr = bCloseIdx[jb] + 1
                break
            if bH[jb] > AH:
                AH = bH[jb]
            tc = bCloseIdx[jb]
        if not ok:
            if fail_ptr > ptr:
                ptr = fail_ptr
            j += 1
            continue
        n_acc += 1
        # --- entry: 1s mid crosses AH + 1t strictly after acceptance close ---
        lvl = AH + 1.0
        te = -1
        end_w = tc + ewin
        if end_w > n - 1:
            end_w = n - 1
        u = tc + 1
        dead = False
        while u <= end_w:
            if y[u] >= lvl:
                if dec[u]:
                    te = u
                else:
                    dead = True          # crossing on dead second kills the setup
                break
            u += 1
        if te < 0:
            if dead:
                n_dead += 1
                ptr = u + 1
            else:
                n_nox += 1
                ptr = end_w + 1
            j += 1
            continue
        entry = y[te]
        # --- barrier resolution (same-second both crossed -> adverse) ---
        res = 0
        i = te + 1
        end = te + cap
        if end > n - 1:
            end = n - 1
        while i <= end:
            up = yhi[i] - entry; dn = entry - ylo[i]
            th = up >= A; ah = dn >= B
            if th and ah:
                res = 2; break
            if ah:
                res = 2; break
            if th:
                res = 1; break
            i += 1
        if res == 1:
            g = A
        elif res == 2:
            g = -B
        else:
            res = 3; g = y[end] - entry; i = end
        e_out[m] = res; e_g[m] = g; e_idx[m] = te; m += 1
        ptr = i + cool
        j += 1
    return e_out[:m], e_g[:m], e_idx[:m], n_brk, n_acc, n_dead, n_nox

SH = "research/scalping_lab/substrate/sechilo/NQ"
GR = "research/scalping_lab/substrate/grid1s/NQ"
OUTD = "research/scalping_lab/artifacts/w5_c2"
os.makedirs(OUTD, exist_ok=True)

rows = []
sessions = sorted(os.path.basename(p)[:-8] for p in glob.glob(os.path.join(SH, "s*.parquet")))
print(f"W5-C2 fast FSS-2 | sessions={len(sessions)} | seed={SEED} | "
      f"clocks={KS} acc={ACCS} brackets={[(int(a),int(b)) for a,b in BRK]} | "
      f"lookback={LOOK} bars, CL>={CLMIN}, entry window={EWIN}s, cap={CAP}s, cool={COOL}s")
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
    tod = (f["time"] - d0).dt.total_seconds().values.astype(np.int64)
    upd60 = pd.Series((f["bid_upd"] + f["ask_upd"]).values).rolling(60, min_periods=1).sum().values
    dec = ((tod >= 9*3600+1800) & (tod < 16*3600) & (upd60 > 0)).astype(np.bool_)
    for K in KS:
        bid = tod // K                                # wall-clock-aligned bar id
        # contiguous-run bar boundaries (grid is complete; ids are non-decreasing)
        change = np.empty(len(bid), np.bool_); change[0] = True
        change[1:] = bid[1:] != bid[:-1]
        starts = np.flatnonzero(change)
        ends = np.append(starts[1:] - 1, len(bid) - 1)
        nb = len(starts)
        bLen = (ends - starts + 1).astype(np.int64)
        bCloseIdx = ends.astype(np.int64)
        bHr = np.array([hi[starts[b]:ends[b]+1].max() for b in range(nb)])
        bLr = np.array([lo[starts[b]:ends[b]+1].min() for b in range(nb)])
        bCr = ml[ends]
        for dname, dv in (("long", 1.0), ("short", -1.0)):
            if dv > 0:
                y, yhi, ylo = ml, hi, lo
                bH, bL, bC = bHr, bLr, bCr
            else:
                y, yhi, ylo = -ml, -lo, -hi
                bH, bL, bC = -bLr, -bHr, -bCr
            bLvl = pd.Series(bH).shift(1).rolling(LOOK, min_periods=LOOK).max().values
            brange = bH - bL
            with np.errstate(invalid="ignore", divide="ignore"):
                clv = np.where(brange > 0, (bC - bL) / brange, np.nan)
            bTrig = ((bC > bLvl) & (brange > 0) & (clv >= CLMIN)
                     & (bLen == K) & dec[bCloseIdx])
            bTrig = np.where(np.isnan(bLvl), False, bTrig).astype(np.bool_)
            bLvl_f = np.where(np.isnan(bLvl), -1.0e18, bLvl)
            n_trig = int(bTrig.sum())
            for nacc in ACCS:
                for (A, B) in BRK:
                    eo, eg, ei, nbrk, naccd, ndead, nnox = simulate(
                        y, yhi, ylo, dec, bC, bH, bLvl_f, bTrig, bCloseIdx, bLen,
                        K, nacc, A, B, CAP, COOL, EWIN)
                    rows.append(dict(session=tag, K=K, acc=nacc, dir=dname,
                                     A=int(A), B=int(B), n_trig=n_trig,
                                     n_brk=nbrk, n_acc=naccd, n_dead=ndead,
                                     n_nox=nnox, n=len(eo),
                                     n_tgt=int((eo == 1).sum()),
                                     n_adv=int((eo == 2).sum()),
                                     n_cap=int((eo == 3).sum()),
                                     gross_sum=float(eg.sum())))
    print(tag, "done", flush=True)

R = pd.DataFrame(rows)
R.to_csv(os.path.join(OUTD, "w5c2_by_session.csv"), index=False)
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
for K in KS:
    for nacc in ACCS:
        for dname in ("long", "short"):
            for (A, B) in BRK:
                gsel = R[(R.K == K) & (R.acc == nacc) & (R.dir == dname) &
                         (R.A == int(A)) & (R.B == int(B))]
                base = dict(K=K, acc=nacc, dir=dname, A=int(A), B=int(B),
                            sessions=NSESS,
                            n_trig=int(gsel.n_trig.sum()), n_brk=int(gsel.n_brk.sum()),
                            n_acc=int(gsel.n_acc.sum()), n_dead=int(gsel.n_dead.sum()),
                            n_nox=int(gsel.n_nox.sum()))
                ge = gsel[gsel.n > 0]
                n = int(ge.n.sum())
                if n == 0:
                    prows.append(dict(**base, unique_days=0, episodes=0,
                                      epi_per_day=np.nan, p_tgt=np.nan, n_tgt=0,
                                      n_adv=0, n_cap=0, gross_per_trade=np.nan,
                                      net_c1=np.nan, ci_lo_c1=np.nan, ci_hi_c1=np.nan,
                                      net_c2=np.nan, ci_lo_c2=np.nan, ci_hi_c2=np.nan,
                                      passes=False))
                    continue
                ud = int(ge.session.nunique())
                ntgt = int(ge.n_tgt.sum()); nadv = int(ge.n_adv.sum())
                ncap = int(ge.n_cap.sum())
                gpt = float(ge.gross_sum.sum()) / n
                net1 = gpt - C1; net2 = gpt - C2
                per = (ge.gross_sum / ge.n - C1).values.astype(float)
                wts = ge.n.values.astype(float)
                lo1, hi1 = boot_ci(per, wts)
                # C2 = C1 + 2.000 exactly -> C2 CI is the C1 CI shifted by -2t
                prows.append(dict(**base, unique_days=ud, episodes=n,
                                  epi_per_day=n / ud, p_tgt=ntgt / max(1, ntgt + nadv),
                                  n_tgt=ntgt, n_adv=nadv, n_cap=ncap,
                                  gross_per_trade=gpt, net_c1=net1,
                                  ci_lo_c1=lo1, ci_hi_c1=hi1, net_c2=net2,
                                  ci_lo_c2=lo1 - (C2 - C1), ci_hi_c2=hi1 - (C2 - C1),
                                  passes=bool((net1 > 0) and (lo1 > -0.5))))
P = pd.DataFrame(prows)
P.to_csv(os.path.join(OUTD, "w5c2_pooled.csv"), index=False)

print("\n=== W5-C2 pooled — per (clock, acceptance, dir, bracket); costs C1=2.872t, "
      "C2=4.872t; CI = day-clustered session bootstrap (1000 reps, seed 20260808) ===")
print(f"{'K':>3} {'acc':>3} {'dir':>5} {'A':>3} {'B':>3} | {'trig':>5} {'brk':>5} "
      f"{'accd':>5} {'epi':>4} {'e/d':>5} {'days':>4} | {'P(tgt)':>7} {'BE_C1':>6} "
      f"{'cap':>3} | {'netC1':>7} {'CI_lo':>7} {'CI_hi':>7} | {'netC2':>7} {'PASS':>4}")
for _, r in P.iterrows():
    be1 = (r.B + C1) / (r.A + r.B)
    if r.episodes == 0:
        print(f"{r.K:>3} {r.acc:>3} {r['dir']:>5} {r.A:>3} {r.B:>3} | {r.n_trig:>5} "
              f"{r.n_brk:>5} {r.n_acc:>5} {0:>4}  (no episodes)")
        continue
    print(f"{r.K:>3} {r.acc:>3} {r['dir']:>5} {r.A:>3} {r.B:>3} | {r.n_trig:>5} "
          f"{r.n_brk:>5} {r.n_acc:>5} {r.episodes:>4} {r.epi_per_day:>5.2f} "
          f"{r.unique_days:>4} | {r.p_tgt:>7.4f} {be1:>6.4f} {r.n_cap:>3} | "
          f"{r.net_c1:>+7.3f} {r.ci_lo_c1:>+7.3f} {r.ci_hi_c1:>+7.3f} | "
          f"{r.net_c2:>+7.3f} {'PASS' if r.passes else 'fail':>4}")
print("(trig = raw trigger bars; brk = breakouts considered by the sequential sim; "
      "accd = acceptances completed; BE_C1 = P(tgt) needed to break even at C1; "
      "PASS = net_c1>0 AND CI_lo>-0.5t)")

print("\n=== funnel: entry-phase attrition per config ===")
for _, r in P.iterrows():
    er = r.episodes / r.n_acc if r.n_acc else np.nan
    print(f"  K={r.K:>2} acc={r.acc} {r['dir']:>5} +{r.A}/-{r.B}: brk={r.n_brk:>4} "
          f"-> accepted={r.n_acc:>4} -> entered={r.episodes:>4} "
          f"(entry rate {100*er if np.isfinite(er) else float('nan'):.1f}%; "
          f"no-cross={r.n_nox}, dead-cross={r.n_dead})")

print("\n=== plateau view: net_c1 across (K, acc) grid, per dir/bracket ===")
for dname in ("long", "short"):
    for (A, B) in BRK:
        cells = []
        for K in KS:
            for nacc in ACCS:
                r = P[(P.K == K) & (P.acc == nacc) & (P.dir == dname) &
                      (P.A == int(A)) & (P.B == int(B))].iloc[0]
                v = f"{r.net_c1:+.2f}" if np.isfinite(r.net_c1) else "n/a"
                cells.append(f"K{K}a{nacc}:{v}{'P' if r.passes else ''}")
        print(f"{dname:>5} +{int(A)}/-{int(B)}: " + "  ".join(cells))

npass = int(P.passes.sum())
print(f"\npassing configs (frozen rule net_c1>0 AND CI_lo>-0.5t): {npass} / {len(P)}")
print("\nW5C2 DONE")
