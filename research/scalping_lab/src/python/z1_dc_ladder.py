"""W1-1 Z1: mid-price DC ladder, frozen theta grid. Event-level mid from sync+asof quotes.
Outputs r(theta), cycles/day, flip-to-flip economics, post-flip excursion probabilities."""
import glob, os
import numpy as np, pandas as pd
from numba import njit

TH = [5, 10, 20, 40, 80, 160]          # ticks, frozen
EXC = [(4,2),(6,2),(6,3),(8,4)]        # frozen A/B grid

@njit(cache=True)
def dc_segments(mid, theta):
    """Returns segment amplitudes (ticks) and flip indices. mid in ticks."""
    n = mid.shape[0]
    amps = np.empty(n, np.float64); flips = np.empty(n, np.int64); dirs = np.empty(n, np.int8)
    k = 0
    ext = mid[0]; prev_ext = np.nan; up = True   # start assuming up-trend; first segment dropped
    started = False
    for i in range(1, n):
        p = mid[i]
        if up:
            if p > ext: ext = p
            elif ext - p >= theta:
                if started and not np.isnan(prev_ext):
                    amps[k] = abs(ext - prev_ext); flips[k] = i; dirs[k] = 1; k += 1
                prev_ext = ext; ext = p; up = False; started = True
        else:
            if p < ext: ext = p
            elif p - ext >= theta:
                if started and not np.isnan(prev_ext):
                    amps[k] = abs(ext - prev_ext); flips[k] = i; dirs[k] = -1; k += 1
                prev_ext = ext; ext = p; up = True; started = True
    return amps[:k], flips[:k], dirs[:k]

@njit(cache=True)
def excursion(mid, starts, dirs, A, B, cap):
    """P(+A ticks in dir before -B against), forward scan capped at `cap` events."""
    hit = 0; tot = 0
    for s in range(starts.shape[0]):
        i0 = starts[s]; d = dirs[s]; p0 = mid[i0]
        end = min(i0 + cap, mid.shape[0])
        for i in range(i0+1, end):
            m = (mid[i] - p0) * d
            if m >= A: hit += 1; tot += 1; break
            if m <= -B: tot += 1; break
    return hit, tot

rows_r, rows_exc, day_net = [], [], {t: {} for t in TH}
files = sorted(glob.glob("research/scalping_lab/substrate/raw/NQ/s*.parquet"))
files = [f for f in files if "_rth" not in f]
for pq in files:
    tag = os.path.basename(pq)[:-8]
    df = pd.read_parquet(pq)
    if (df["bip"]==1).sum() == 0: continue
    df["time"] = pd.to_datetime(df["time"])
    B_ = df[df.bip==1][["time","price"]].rename(columns={"price":"bid"})
    A_ = df[df.bip==2][["time","price"]].rename(columns={"price":"ask"})
    Q = pd.merge_asof(B_.sort_values("time"), A_.sort_values("time"), on="time").dropna()
    mid = ((Q["bid"].values + Q["ask"].values) / 2.0) / 0.25   # ticks
    hrs = (Q["time"].iloc[-1] - Q["time"].iloc[0]).total_seconds()/3600
    for th in TH:
        amps, flips, dirs = dc_segments(mid, float(th))
        if len(amps) < 3: continue
        r = float(amps.mean()/th)
        # flip-to-flip capture per cycle (ticks): amp - 2*theta
        cap_t = amps - 2.0*th
        gross = float(cap_t.mean())
        net_c1 = gross - 2.872
        rows_r.append(dict(session=tag, theta=th, n_cycles=len(amps), cyc_per_day=len(amps)/(hrs/23),
                           r=round(r,4), gross_pc=round(gross,3), net_c1_pc=round(net_c1,3)))
        day_net[th][tag] = net_c1 * len(amps)
        # post-flip excursion (state = just flipped, direction = new trend)
        for (Aq,Bq) in EXC:
            h, t = excursion(mid, flips, dirs.astype(np.int64), float(Aq), float(Bq), 200000)
            if t > 0:
                rows_exc.append(dict(session=tag, theta=th, A=Aq, Bneg=Bq, p=round(h/t,4), n=t))
    # unconditional excursion baseline (theta-independent): every 2000th quote event
    st = np.arange(1000, len(mid)-1000, 2000).astype(np.int64)
    d1 = np.ones(len(st), np.int64)
    for (Aq,Bq) in EXC:
        h_u, t_u = excursion(mid, st, d1, float(Aq), float(Bq), 200000)
        h_d, t_d = excursion(mid, st, -d1, float(Aq), float(Bq), 200000)
        rows_exc.append(dict(session=tag, theta=0, A=Aq, Bneg=Bq, p=round((h_u+h_d)/(t_u+t_d),4), n=t_u+t_d))
    print(tag, "done", flush=True)

R = pd.DataFrame(rows_r); E = pd.DataFrame(rows_exc)
R.to_csv("research/scalping_lab/artifacts/z1/z1_r_curve_by_session.csv", index=False)
E.to_csv("research/scalping_lab/artifacts/z1/z1_excursion.csv", index=False)

print("\n=== Z1 r(theta) aggregate (37 L2 discovery sessions) ===")
agg = R.groupby("theta").apply(lambda g: pd.Series(dict(
    sessions=len(g), cyc_day=g["cyc_per_day"].mean(), r_mean=g["r"].mean(),
    r_p10=g["r"].quantile(.1), r_p90=g["r"].quantile(.9),
    gross_pc=g["gross_pc"].mean(), net_c1_pc=g["net_c1_pc"].mean()))).round(3)
print(agg.to_string())
# day-clustered bootstrap on net/cycle
rng = np.random.default_rng(20260807)
print("\nnet_c1/cycle day-clustered 95% CI:")
for th in TH:
    g = R[R["theta"]==th]
    if not len(g): continue
    vals = g.set_index("session").apply(lambda row: row["net_c1_pc"], axis=1).values
    boots = [np.mean(rng.choice(vals, len(vals), replace=True)) for _ in range(1000)]
    print(f"  theta={th}: mean {np.mean(vals):+.3f} ticks, CI [{np.percentile(boots,2.5):+.3f}, {np.percentile(boots,97.5):+.3f}]")
print("\n=== excursion: unconditional baseline vs post-flip (pooled) ===")
for (Aq,Bq) in EXC:
    base = E[(E.theta==0)&(E.A==Aq)&(E.Bneg==Bq)]
    null = Bq/(Aq+Bq)
    bp = np.average(base["p"], weights=base["n"])
    print(f"  +{Aq}/-{Bq}: null {null:.3f} | uncond {bp:.3f} | post-flip by theta: " +
        " ".join(f"{th}t={np.average(E[(E.theta==th)&(E.A==Aq)&(E.Bneg==Bq)]['p'], weights=E[(E.theta==th)&(E.A==Aq)&(E.Bneg==Bq)]['n']):.3f}" for th in TH if len(E[(E.theta==th)&(E.A==Aq)&(E.Bneg==Bq)])))
