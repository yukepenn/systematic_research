"""W5-C3 FSS-3 failed-opposite-probe state machine (never tested).
Frozen spec: research/scalping_lab/specs/W5_programs_wave.md section C3 (committed
before this run). Sequential episode simulation, conservative same-second-both-crossed
-> adverse barrier rule, session (day-clustered) bootstrap CIs, seed 20260808, 1000 reps.
37 L2 discovery sessions (sechilo listing is canonical; never opens extra grid files).

Frozen-spec interpretation notes (documented in w5c3_report.md):
- All state-machine logic runs on mid_last (house convention, as W4-A); mid_high /
  mid_low are used ONLY for barrier resolution (conservative same-second
  both-crossed -> adverse). Shorts simulated in sign-flipped space:
  y = -mid, y_hi = -mid_low, y_lo = -mid_high.
- Context detect on decision seconds only (RTH & quote-alive): ret120 =
  mid(t) - mid(t-120) >= CTX (long; short symmetric). CTX in {16 primary, 12, 24}.
- Probe: from context detection t0, PH = running max of mid from t0; probe triggers
  at the FIRST second t1 in (t0, t0+30] with PH - mid(t1) >= P (P in {6 primary,
  4, 8}). PH is frozen at t1; probe-low L = mid(t1) (the probe low at set time);
  probe depth = PH - L (>= P). No probe within 30s -> resume scan at t0+31.
- Failure window: 30s from L being set, i.e. u in (t1, t1+30]. Checks per second on
  mid_last: (a) undercut: mid(u) < L - 2t (undercut by MORE than 2t) -> cancel the
  setup (the probe kept going: it did not fail); undercuts <= 2t are tolerated and
  do NOT update L or the recovery level. (b) recovery: mid(u) >= L + 0.5*(PH - L)
  -> the probe FAILED; entry LONG at that second's mid (market, delay 0, house
  convention). Entries only on decision seconds; a crossing on a dead second kills
  the setup (no chase). Neither within 30s -> setup expires, resume at t1+31.
  (a) and (b) cannot both hold in one second (single mid_last value), so ordering
  within a second is moot.
- One trade per probe holds by construction (single sequential pass; each probe
  yields at most one entry, then scan resumes past it).
- Barriers evaluated from te+1 (market entry); cap 300s -> exit at mid(te+300);
  cooldown 60s after episode resolution (trades only, house convention).
- Lift = pooled P(target) minus unconditional P(target-first) for the same
  (A, B, dir) from artifacts/census/excursion_surface.csv (frozen census).
"""
import glob, os
import numpy as np, pandas as pd
from numba import njit

CTX_LIST = [16, 12, 24]            # context ret120 threshold (t); 16 primary
PROBE_LIST = [6, 4, 8]             # probe counter-move threshold (t); 6 primary
BRK = [(24.0, 8.0), (32.0, 10.0)]
CTX_WIN = 120                      # context return window (s)
PROBE_WIN = 30                     # probe must trigger within 30s of context
FAIL_WIN = 30                      # recovery must occur within 30s of L being set
UNDERCUT_TOL = 2.0                 # undercut > 2t cancels
CAP = 300
COOL = 60
C1, C2 = 2.872, 4.872
SEED = 20260808

@njit(cache=True)
def simulate(y, yhi, ylo, dec, trig, P, A, B):
    """One sequential pass in direction space. Returns per-episode outcome
    (1 tgt / 2 adv / 3 cap), gross ticks, and state-machine counters."""
    n = y.shape[0]
    e_out = np.empty(n, np.int8); e_g = np.empty(n, np.float64)
    m = 0
    n_ctx = 0; n_probe = 0; n_cancel = 0; n_dead = 0; n_expire = 0
    t = 0
    while t < n - 1:
        if not (dec[t] and trig[t]):
            t += 1
            continue
        n_ctx += 1
        # --- phase 1: probe search within PROBE_WIN s of context detection ---
        PH = y[t]
        end_pr = t + PROBE_WIN
        if end_pr > n - 1: end_pr = n - 1
        t1 = -1
        tau = t + 1
        while tau <= end_pr:
            if y[tau] > PH: PH = y[tau]
            if PH - y[tau] >= P:
                t1 = tau
                break
            tau += 1
        if t1 < 0:                       # no probe -> skip past probe window
            t = end_pr + 1
            continue
        n_probe += 1
        L = y[t1]
        depth = PH - L                   # >= P by construction
        R = L + 0.5 * depth              # 50% recovery level
        # --- phase 2: failure window, FAIL_WIN s from L being set ---
        end_fw = t1 + FAIL_WIN
        if end_fw > n - 1: end_fw = n - 1
        te = -1
        nxt = end_fw + 1                 # default: setup expires
        expired = 1
        u = t1 + 1
        while u <= end_fw:
            if y[u] < L - UNDERCUT_TOL:  # undercut > 2t -> probe succeeded, cancel
                n_cancel += 1
                nxt = u + 1
                expired = 0
                break
            if y[u] >= R:                # >=50% recovery -> probe FAILED
                if dec[u]:
                    te = u
                else:
                    n_dead += 1          # crossing on dead second kills setup
                nxt = u + 1
                expired = 0
                break
            u += 1
        if te < 0:
            if expired == 1: n_expire += 1
            t = nxt
            continue
        entry = y[te]
        # --- barrier resolution (same-second both crossed -> adverse) ---
        end = te + CAP
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
        e_out[m] = res; e_g[m] = g; m += 1
        t = i + COOL
    return e_out[:m], e_g[:m], n_ctx, n_probe, n_cancel, n_dead, n_expire

SH = "research/scalping_lab/substrate/sechilo/NQ"
GR = "research/scalping_lab/substrate/grid1s/NQ"
OUTD = "research/scalping_lab/artifacts/w5_c3"
os.makedirs(OUTD, exist_ok=True)

rows = []
sessions = sorted(os.path.basename(p)[:-8] for p in glob.glob(os.path.join(SH, "s*.parquet")))
print(f"W5-C3 FSS-3 failed-opposite-probe | sessions={len(sessions)} | seed={SEED}")
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
    ret_ctx = mls.diff(CTX_WIN).values
    for dname, dv in (("long", 1.0), ("short", -1.0)):
        y = ml * dv
        yhi = hi if dv > 0 else -lo
        ylo = lo if dv > 0 else -hi
        rsy = ret_ctx * dv
        for CTX in CTX_LIST:
            trig = np.where(np.isnan(rsy), False, rsy >= CTX).astype(np.bool_)
            for P in PROBE_LIST:
                for (A, B) in BRK:
                    eo, eg, nctx, npr, ncan, ndead, nexp = simulate(
                        y, yhi, ylo, dec, trig, float(P), A, B)
                    rows.append(dict(session=tag, ctx=CTX, probe=P, dir=dname,
                                     A=int(A), B=int(B), n_ctx=nctx, n_probe=npr,
                                     n_cancel=ncan, n_dead=ndead, n_expire=nexp,
                                     n=len(eo), n_tgt=int((eo == 1).sum()),
                                     n_adv=int((eo == 2).sum()),
                                     n_cap=int((eo == 3).sum()),
                                     gross_sum=float(eg.sum())))
    print(tag, "done", flush=True)

R = pd.DataFrame(rows)
R.to_csv(os.path.join(OUTD, "w5c3_by_session.csv"), index=False)
NSESS = len(sessions)

SURF = pd.read_csv("research/scalping_lab/artifacts/census/excursion_surface.csv")
def uncond_p(A, B, dname):
    r = SURF[(SURF.A == int(A)) & (SURF.B == int(B)) & (SURF.dir == dname)]
    return float(r.p_target.iloc[0]) if len(r) else np.nan

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
for CTX in CTX_LIST:
    for P in PROBE_LIST:
        for dname in ("long", "short"):
            for (A, B) in BRK:
                gsel = R[(R.ctx == CTX) & (R.probe == P) & (R.dir == dname) &
                         (R.A == int(A)) & (R.B == int(B))]
                nctx = int(gsel.n_ctx.sum()); npr = int(gsel.n_probe.sum())
                ncan = int(gsel.n_cancel.sum()); ndead = int(gsel.n_dead.sum())
                nexp = int(gsel.n_expire.sum())
                ge = gsel[gsel.n > 0]
                n = int(ge.n.sum())
                pu = uncond_p(A, B, dname)
                base = dict(ctx=CTX, probe=P, dir=dname, A=int(A), B=int(B),
                            sessions=NSESS, n_ctx=nctx, n_probe=npr,
                            n_cancel=ncan, n_dead=ndead, n_expire=nexp)
                if n == 0:
                    prows.append(dict(**base, unique_days=0, episodes=0,
                                      epi_per_day=np.nan, entry_rate=np.nan,
                                      p_tgt=np.nan, n_tgt=0, n_adv=0, n_cap=0,
                                      gross_per_trade=np.nan, net_c1=np.nan,
                                      ci_lo=np.nan, ci_hi=np.nan, net_c2=np.nan,
                                      p_uncond=pu, lift_pp=np.nan, passes=False))
                    continue
                ud = int(ge.session.nunique())
                ntgt = int(ge.n_tgt.sum()); nadv = int(ge.n_adv.sum())
                ncap = int(ge.n_cap.sum())
                gpt = float(ge.gross_sum.sum()) / n
                net1 = gpt - C1; net2 = gpt - C2
                per = (ge.gross_sum / ge.n - C1).values.astype(float)
                wts = ge.n.values.astype(float)
                lo_, hi_ = boot_ci(per, wts)
                ptgt = ntgt / max(1, ntgt + nadv)
                prows.append(dict(**base, unique_days=ud, episodes=n,
                                  epi_per_day=n / ud,
                                  entry_rate=n / npr if npr else np.nan,
                                  p_tgt=ptgt, n_tgt=ntgt, n_adv=nadv, n_cap=ncap,
                                  gross_per_trade=gpt, net_c1=net1,
                                  ci_lo=lo_, ci_hi=hi_, net_c2=net2,
                                  p_uncond=pu,
                                  lift_pp=100.0 * (ptgt - pu),
                                  passes=bool((net1 > 0) and (lo_ > -0.5))))
P_ = pd.DataFrame(prows)
P_.to_csv(os.path.join(OUTD, "w5c3_pooled.csv"), index=False)

print("\n=== W5-C3 pooled (net C1=2.872t, net_c2 C2=4.872t; CI = session bootstrap "
      "2.5/97.5, seed 20260808, 1000 reps) ===")
print(f"{'ctx':>4} {'P':>3} {'dir':>5} {'A':>3} {'B':>3} | {'nctx':>6} {'probe':>6} "
      f"{'can':>5} {'dead':>4} {'exp':>5} | {'epi':>5} {'e/d':>5} {'days':>4} | "
      f"{'P(tgt)':>7} {'unc':>7} {'lift':>6} {'cap':>4} | "
      f"{'netC1':>7} {'CI_lo':>7} {'CI_hi':>7} | {'netC2':>7} {'PASS':>4}")
for _, r in P_.iterrows():
    star = " *" if (r.ctx == 16 and r.probe == 6) else ""
    if r.episodes == 0:
        print(f"{r.ctx:>4} {r.probe:>3} {r['dir']:>5} {r.A:>3} {r.B:>3} | {r.n_ctx:>6} "
              f"{r.n_probe:>6} {r.n_cancel:>5} {r.n_dead:>4} {r.n_expire:>5} | "
              f"{0:>5}  (no episodes){star}")
        continue
    print(f"{r.ctx:>4} {r.probe:>3} {r['dir']:>5} {r.A:>3} {r.B:>3} | {r.n_ctx:>6} "
          f"{r.n_probe:>6} {r.n_cancel:>5} {r.n_dead:>4} {r.n_expire:>5} | "
          f"{r.episodes:>5} {r.epi_per_day:>5.2f} {r.unique_days:>4} | "
          f"{r.p_tgt:>7.4f} {r.p_uncond:>7.4f} {r.lift_pp:>+6.2f} {r.n_cap:>4} | "
          f"{r.net_c1:>+7.3f} {r.ci_lo:>+7.3f} {r.ci_hi:>+7.3f} | "
          f"{r.net_c2:>+7.3f} {'PASS' if r.passes else 'fail':>4}{star}")
print("(* = primary ctx=16, P=6; lift in percentage points vs unconditional census "
      "P(target-first) same (A,B,dir); PASS = net_c1>0 AND CI_lo>-0.5t)")

print("\n=== plateau view: net_c1 across (ctx, P) grid, per dir/bracket ===")
for dname in ("long", "short"):
    for (A, B) in BRK:
        cells = []
        for CTX in CTX_LIST:
            for P in PROBE_LIST:
                r = P_[(P_.ctx == CTX) & (P_.probe == P) & (P_.dir == dname) &
                       (P_.A == int(A)) & (P_.B == int(B))].iloc[0]
                v = f"{r.net_c1:+.2f}" if np.isfinite(r.net_c1) else "n/a"
                cells.append(f"c{CTX}p{P}:{v}{'P' if r.passes else ''}")
        print(f"{dname:>5} +{int(A)}/-{int(B)}: " + "  ".join(cells))

npass = int(P_.passes.sum())
print(f"\npassing configs (frozen rule net_c1>0 AND CI_lo>-0.5t): {npass} / {len(P_)}")
print("\nW5C3 DONE")
