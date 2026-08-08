"""W6-T3 ES-led lag trade rule (FSS-10 family, KPI A) — sequential episode sim.
Spec: specs/W6_fss10_redteam.md (frozen, committed 58a97a3 before this run). Seed 20260808.

Frozen rule (T3): on the 1s RTH quote-alive clock, enter NQ in the ES direction when
  es_z_ret60 - nq_z_ret60 >= theta (theta=1.0 primary, 1.5 neighbor)
  AND |es_z_ret60| >= 0.5, ES direction = sign(es_ret60).
Long when ES direction up, short when down (the symmetric construction — both
directions from the single inequality). Sequential sim, brackets (24,8),(32,10),
cap 300s, cooldown 60s, entry at the trigger second's NQ mid_last.
Same-second-both-crossed -> adverse (house conservative barrier convention).

JOIN (frozen): merge ES sechilo onto NQ per-second frame on time; ffill es_mid_last
with staleness limit 5s (last ES second-row older than 5s -> ES features NaN at that
decision second, excluded); es hi/lo not ffilled (unused here — barriers are NQ).
Z-NORM (frozen): z_ret60 = ret60 / rolling-600s std of 1s dmid, per instrument,
trailing, min 300s history.
Sessions: intersection of NQ-L2-usable (quote-alive) and ES availability;
s20250902 excluded (NQ quote-dead RTH). es_s20260519 kept (truncated ES afternoon,
caveat: no ES-fresh seconds after ~14:43:27 -> no triggers there).
"""
import glob, os
import numpy as np, pandas as pd
from numba import njit

THETAS = [1.0, 1.5]          # 1.0 primary; 1.5 frozen neighbor
BRK = [(24, 8), (32, 10)]
CAP = 300
COOL = 60
C1, C2 = 2.872, 4.872
ZGATE = 0.5
SEED = 20260808
NBOOT = 1000

SH = "research/scalping_lab/substrate/sechilo/NQ"
ESH = "research/scalping_lab/substrate/sechilo/ES"
GR = "research/scalping_lab/substrate/grid1s/NQ"
OUTD = "research/scalping_lab/artifacts/w6_fss10"
CENSUS = "research/scalping_lab/artifacts/census/excursion_surface.csv"
os.makedirs(OUTD, exist_ok=True)

EXCLUDE = {"s20250902"}      # NQ quote-dead in RTH (frozen session list rule)


@njit(cache=True)
def simulate(ml, hi, lo, dirsig, A, B, cap, cool):
    """One sequential book: dirsig[t] in {+1,-1,0} = trigger direction at t (0=none).
    Enter at ml[t] (trigger second's NQ mid_last), resolve from t+1 on hi/lo barriers
    or cap. Same-second both-crossed -> adverse. Cooldown after resolution.
    Returns entry_idx, dir, outcome (1 tgt/2 adv/3 cap), gross ticks."""
    n = ml.shape[0]
    e_idx = np.empty(n, np.int64); e_dir = np.empty(n, np.int8)
    e_out = np.empty(n, np.int8); e_gross = np.empty(n, np.float64)
    m = 0; t = 0
    while t < n - 1:
        d = dirsig[t]
        if d != 0:
            entry = ml[t]
            res = 0; i = t + 1
            end = min(t + cap, n - 1)
            while i <= end:
                up = hi[i] - entry; dn = entry - lo[i]
                if d == 1:
                    t_hit = up >= A; a_hit = dn >= B
                else:
                    t_hit = dn >= A; a_hit = up >= B
                if t_hit and a_hit: res = 2; break
                if a_hit: res = 2; break
                if t_hit: res = 1; break
                i += 1
            if res == 1: g = float(A)
            elif res == 2: g = -float(B)
            else:
                res = 3; g = (ml[end] - entry) * d; i = end
            e_idx[m] = t; e_dir[m] = d; e_out[m] = res; e_gross[m] = g; m += 1
            t = i + cool
        else:
            t += 1
    return e_idx[:m], e_dir[:m], e_out[:m], e_gross[:m]


nq_tags = {os.path.basename(p)[:-8] for p in glob.glob(os.path.join(SH, "s*.parquet"))}
es_tags = {os.path.basename(p)[:-8].replace("es_", "")
           for p in glob.glob(os.path.join(ESH, "es_s*.parquet"))}
sessions = sorted((nq_tags & es_tags) - EXCLUDE)
print(f"analysis sessions: {len(sessions)} (NQ sechilo {len(nq_tags)} & ES {len(es_tags)} "
      f"minus excluded {sorted(EXCLUDE)})")
print(sessions)

sess_rows, epi_rows = [], []
for tag in sessions:
    d = pd.to_datetime(tag[1:], format="%Y%m%d")
    g = pd.read_parquet(os.path.join(GR, tag + ".parquet"))
    s = pd.read_parquet(os.path.join(SH, tag + ".parquet"))
    e = pd.read_parquet(os.path.join(ESH, "es_" + tag + ".parquet"))
    g["time"] = pd.to_datetime(g["time"]); s["time"] = pd.to_datetime(s["time"])
    e["time"] = pd.to_datetime(e["time"])
    f = g.merge(s, on="time", how="left")
    f["mid_last"] = f["mid_last"].ffill()
    f = f[f["mid_last"].notna()].reset_index(drop=True)
    f["mid_high"] = f["mid_high"].fillna(f["mid_last"])
    f["mid_low"] = f["mid_low"].fillna(f["mid_last"])
    # frame must be a contiguous 1s grid for ffill(limit)=staleness-in-seconds
    step = f["time"].diff().dt.total_seconds().values[1:]
    assert (step == 1).all(), f"{tag}: non-contiguous 1s grid"
    f = f.merge(e[["time", "mid_last"]].rename(columns={"mid_last": "es_raw"}),
                on="time", how="left")

    ml = f["mid_last"].values; hi = f["mid_high"].values; lo = f["mid_low"].values
    n = len(f)
    tod = (f["time"] - d).dt.total_seconds().values
    rth = (tod >= 9 * 3600 + 1800) & (tod < 16 * 3600)
    upd60 = pd.Series((f["bid_upd"] + f["ask_upd"]).values).rolling(60, min_periods=1).sum().values
    alive = upd60 > 0

    # --- ES features on the joined frame (frozen join + z-norm) ---
    es_mid = f["es_raw"].ffill(limit=5)               # staleness limit 5s (1s grid)
    es_dmid = es_mid.diff()
    es_sd = es_dmid.rolling(600, min_periods=300).std()
    es_ret60 = (es_mid - es_mid.shift(60)).values
    es_z = (es_ret60 / np.where(es_sd.values > 0, es_sd.values, np.nan))

    # --- NQ features, same construction ---
    mls = pd.Series(ml)
    nq_dmid = mls.diff()
    nq_sd = nq_dmid.rolling(600, min_periods=300).std()
    nq_ret60 = (mls - mls.shift(60)).values
    nq_z = (nq_ret60 / np.where(nq_sd.values > 0, nq_sd.values, np.nan))

    es_ok = ~np.isnan(es_z)                           # ES-feature-NaN secs excluded
    dec = rth & alive & es_ok & ~np.isnan(nq_z)
    gap = es_z - nq_z
    esdir = np.where(es_ret60 > 0, 1, np.where(es_ret60 < 0, -1, 0)).astype(np.int8)

    n_dec = int(dec.sum())
    n_rth_alive = int((rth & alive).sum())
    for theta in THETAS:
        trig = dec & (gap >= theta) & (np.abs(es_z) >= ZGATE)
        dirsig = np.where(trig, esdir, 0).astype(np.int8)
        n_trig = int((dirsig != 0).sum())
        for (A, B) in BRK:
            ei, ed, eo, eg = simulate(ml, hi, lo, dirsig, float(A), float(B), CAP, COOL)
            for dname, dv in (("long", 1), ("short", -1)):
                mset = ed == dv
                sess_rows.append(dict(
                    session=tag, theta=theta, A=A, B=B, dir=dname,
                    n=int(mset.sum()),
                    n_tgt=int((eo[mset] == 1).sum()), n_adv=int((eo[mset] == 2).sum()),
                    n_cap=int((eo[mset] == 3).sum()),
                    gross_sum=float(eg[mset].sum()),
                    n_trig_secs=n_trig, n_dec_secs=n_dec, n_rth_alive=n_rth_alive))
            for j in range(len(ei)):
                t0 = ei[j]
                epi_rows.append(dict(
                    session=tag, theta=theta, A=A, B=B,
                    dir="long" if ed[j] == 1 else "short",
                    t=int(t0), tod=float(tod[t0]), outcome=int(eo[j]),
                    gross=float(eg[j]), es_z=float(es_z[t0]), nq_z=float(nq_z[t0]),
                    gap=float(gap[t0])))
    print(tag, f"done  dec_secs={n_dec} rth_alive={n_rth_alive}", flush=True)

R = pd.DataFrame(sess_rows)
R.to_csv(os.path.join(OUTD, "t3_by_session.csv"), index=False)
E = pd.DataFrame(epi_rows)
E.to_csv(os.path.join(OUTD, "t3_episodes.csv"), index=False)
NSESS = len(sessions)

# --- unconditional census baseline (frozen comparison target) ---
census = pd.read_csv(CENSUS)
base = {(int(r.A), int(r.B), r["dir"]): float(r.p_target) for _, r in census.iterrows()}
print("\ncensus baselines used:",
      {k: v for k, v in base.items() if k[0] in (24, 32)})

brng = np.random.default_rng(SEED)
sum_rows = []
print(f"\n=== W6-T3 ES-led lag rule — pooled ({NSESS} sessions, seed {SEED}, "
      f"{NBOOT} session-bootstrap reps, day-clustered) ===")
hdr = (f"{'th':>4} {'A':>3} {'B':>3} {'dir':>5} | {'epi':>5} {'e/d':>6} {'days':>4} "
       f"{'P(tgt)':>7} {'[CI]':>17} {'base':>6} {'lift_pp':>7} | "
       f"{'netC1':>7} {'CI_lo':>7} {'CI_hi':>7} | {'netC2':>7} | {'pass':>4}")
print(hdr)
for theta in THETAS:
    for (A, B) in BRK:
        for dname in ("long", "short", "both"):
            if dname == "both":
                gsel = R[(R.theta == theta) & (R.A == A) & (R.B == B)]
                g0 = gsel.groupby("session")[["n", "n_tgt", "n_adv", "n_cap", "gross_sum"]].sum().reset_index()
            else:
                g0 = R[(R.theta == theta) & (R.A == A) & (R.B == B) & (R.dir == dname)].copy()
            g0 = g0[g0.n > 0]
            epi = int(g0.n.sum())
            if dname == "both":
                nl = R[(R.theta == theta) & (R.A == A) & (R.B == B) & (R.dir == "long")].n.sum()
                ns = R[(R.theta == theta) & (R.A == A) & (R.B == B) & (R.dir == "short")].n.sum()
                bl = ((base[(A, B, "long")] * nl + base[(A, B, "short")] * ns) / max(1, nl + ns))
            else:
                bl = base[(A, B, dname)]
            if epi == 0:
                print(f"{theta:>4} {A:>3} {B:>3} {dname:>5} | {0:>5} {'-':>6} {0:>4} "
                      f"{'-':>7} {'-':>17} {bl:>6.4f} {'-':>7} | {'-':>7} {'-':>7} {'-':>7} "
                      f"| {'-':>7} | {'-':>4}")
                sum_rows.append(dict(theta=theta, A=A, B=B, dir=dname, episodes=0,
                                     epi_per_day=0.0, unique_days=0, baseline=bl))
                continue
            days = int(g0.session.nunique())
            resolved = int((g0.n_tgt + g0.n_adv).sum())
            ptgt = g0.n_tgt.sum() / max(1, resolved)
            net1 = g0.gross_sum.sum() / epi - C1
            net2 = g0.gross_sum.sum() / epi - C2
            per = (g0.gross_sum / g0.n - C1).values
            w = g0.n.values
            tgt_a = g0.n_tgt.values.astype(float)
            res_a = (g0.n_tgt + g0.n_adv).values.astype(float)
            idx = np.arange(len(per))
            b_net, b_p = [], []
            for _ in range(NBOOT):
                b = brng.choice(idx, len(idx), replace=True)
                b_net.append(np.average(per[b], weights=w[b]))
                rs = res_a[b].sum()
                if rs > 0: b_p.append(tgt_a[b].sum() / rs)
            if len(idx) >= 2:
                ci_lo, ci_hi = np.percentile(b_net, 2.5), np.percentile(b_net, 97.5)
                p_lo, p_hi = np.percentile(b_p, 2.5), np.percentile(b_p, 97.5)
            else:
                ci_lo = ci_hi = p_lo = p_hi = np.nan
            lift = (ptgt - bl) * 100
            ok = (net1 > 0) and (ci_lo > -0.5)
            print(f"{theta:>4} {A:>3} {B:>3} {dname:>5} | {epi:>5} {epi/NSESS:>6.2f} {days:>4} "
                  f"{ptgt:>7.4f} [{p_lo:>7.4f},{p_hi:>7.4f}] {bl:>6.4f} {lift:>+7.2f} | "
                  f"{net1:>+7.3f} {ci_lo:>+7.3f} {ci_hi:>+7.3f} | {net2:>+7.3f} | "
                  f"{'PASS' if ok else 'FAIL':>4}")
            sum_rows.append(dict(theta=theta, A=A, B=B, dir=dname, episodes=epi,
                                 epi_per_day=round(epi / NSESS, 3), unique_days=days,
                                 n_tgt=int(g0.n_tgt.sum()), n_adv=int(g0.n_adv.sum()),
                                 n_cap=int(g0.n_cap.sum()),
                                 p_tgt=round(ptgt, 4), p_ci_lo=round(p_lo, 4),
                                 p_ci_hi=round(p_hi, 4), baseline=round(bl, 4),
                                 lift_pp=round(lift, 2),
                                 net_c1=round(net1, 3), ci_lo=round(ci_lo, 3),
                                 ci_hi=round(ci_hi, 3), net_c2=round(net2, 3),
                                 pass_c1=bool(ok)))
SO = pd.DataFrame(sum_rows)
SO.to_csv(os.path.join(OUTD, "t3_summary.csv"), index=False)

print("\n=== diagnostics ===")
for theta in THETAS:
    gt = R[(R.theta == theta) & (R.A == 24) & (R.B == 8)].groupby("session").first()
    print(f"theta={theta}: trigger-secs/day mean={gt.n_trig_secs.mean():.1f} "
          f"median={gt.n_trig_secs.median():.0f} max={gt.n_trig_secs.max()} "
          f"(dec-secs/day mean={gt.n_dec_secs.mean():.0f}, "
          f"rth-alive/day mean={gt.n_rth_alive.mean():.0f})")
if len(E):
    for theta in THETAS:
        for dname in ("long", "short"):
            ee = E[(E.theta == theta) & (E.A == 24) & (E.dir == dname)]
            if not len(ee): continue
            h = ee.tod / 3600
            print(f"theta={theta} {dname} (24/8): entries tod p25/p50/p75 = "
                  f"{h.quantile(.25):.2f}/{h.quantile(.5):.2f}/{h.quantile(.75):.2f} ET-h, "
                  f"median gap={ee.gap.median():.2f}, median |es_z|={ee.es_z.abs().median():.2f}, "
                  f"median nq_z={ee.nq_z.median():.2f}")
    # per-outcome mean gross sanity
    print("outcome counts (all cells): "
          f"tgt={int((E.outcome==1).sum())} adv={int((E.outcome==2).sum())} "
          f"cap={int((E.outcome==3).sum())}; cap mean gross="
          f"{E[E.outcome==3].gross.mean():+.3f}t")
print("\nW6-T3 DONE")
