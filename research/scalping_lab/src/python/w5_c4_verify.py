"""W5-C4 verification pass (independent code paths; output w5c4_verify.txt).
1. FSS-6 trigger re-derivation for ALL sessions via numpy sliding_window_view
   (independent of pandas rolling): exact match of trigger sets + event detail.
2. Compression funnel diagnostic: why FSS-6 (never/rarely) fires.
3. FSS-7 pure-Python re-simulation (independent trigger derivation via back-scan
   for the sign flip + slice extremes; independent sequential loop) for the two
   highest-episode sessions, both brackets, compared to w5c4_by_session.csv.
4. Pooled-CSV cross-foot: episodes/net_c1 recomputed from by-session CSV.
"""
import glob, os
import numpy as np, pandas as pd

SH = "research/scalping_lab/substrate/sechilo/NQ"
GR = "research/scalping_lab/substrate/grid1s/NQ"
OUTD = "research/scalping_lab/artifacts/w5_c4"
C1, C2 = 2.872, 4.872
CAP, COOL = 300, 60
BRK = [(24.0, 8.0), (32.0, 10.0)]

R = pd.read_csv(os.path.join(OUTD, "w5c4_by_session.csv"))
P = pd.read_csv(os.path.join(OUTD, "w5c4_pooled.csv"))


def load(tag):
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
    dec = (tod >= 9 * 3600 + 1800) & (tod < 16 * 3600) & (upd60 > 0)
    return f, ml, hi, lo, dec


sessions = sorted(os.path.basename(p)[:-8] for p in glob.glob(os.path.join(SH, "s*.parquet")))

# ---------- 1+2: FSS-6 independent trigger re-derivation + funnel ----------
print("=== [1] FSS-6 trigger re-derivation (sliding_window_view, all 37 sessions) ===")
tot = dict(dec=0, comp=0, comp_vel=0, trigL=0, trigS=0)
events = []
mismatch = 0
for tag in sessions:
    f, ml, hi, lo, dec = load(tag)
    n = len(ml)
    swv_hi = np.lib.stride_tricks.sliding_window_view(hi, 120).max(axis=1)
    swv_lo = np.lib.stride_tricks.sliding_window_view(lo, 120).min(axis=1)
    comp_hi = np.full(n, np.nan); comp_lo = np.full(n, np.nan)
    # window [t-120, t-1] -> swv index t-120; defined for t >= 120
    comp_hi[120:] = swv_hi[: n - 120]
    comp_lo[120:] = swv_lo[: n - 120]
    rng = comp_hi - comp_lo
    ret10 = np.full(n, np.nan); ret10[10:] = ml[10:] - ml[:-10]
    ok = ~(np.isnan(rng) | np.isnan(ret10))
    tL = ok & (rng <= 8.0) & (ret10 >= 6.0) & (ml > comp_hi)
    tS = ok & (rng <= 8.0) & (ret10 <= -6.0) & (ml < comp_lo)
    # main-run values (pandas rolling path)
    mls = pd.Series(ml)
    chp = pd.Series(hi).rolling(120, min_periods=120).max().shift(1).values
    clp = pd.Series(lo).rolling(120, min_periods=120).min().shift(1).values
    rp = chp - clp
    r10p = mls.diff(10).values
    okp = ~(np.isnan(rp) | np.isnan(r10p))
    tLp = okp & (rp <= 8.0) & (r10p >= 6.0) & (ml > chp)
    tSp = okp & (rp <= 8.0) & (r10p <= -6.0) & (ml < clp)
    if not (np.array_equal(tL, tLp) and np.array_equal(tS, tSp)):
        mismatch += 1
        print(f"  MISMATCH {tag}")
    comp = dec & ok & (rng <= 8.0)
    vel = comp & (np.abs(ret10) >= 6.0)
    tot["dec"] += int(dec.sum()); tot["comp"] += int(comp.sum())
    tot["comp_vel"] += int(vel.sum())
    tot["trigL"] += int((tL & dec).sum()); tot["trigS"] += int((tS & dec).sum())
    for t in np.where((tL | tS) & dec)[0]:
        events.append(dict(session=tag, time=str(f["time"].iloc[t]),
                           dir="long" if tL[t] else "short", mid=ml[t],
                           comp_hi=comp_hi[t], comp_lo=comp_lo[t], rng=rng[t],
                           ret10=ret10[t]))
print(f"sessions with trigger-set mismatch vs main run: {mismatch} / {len(sessions)}")
print(f"FUNNEL (RTH quote-alive seconds, all sessions): dec={tot['dec']}, "
      f"compression(range<=8t)={tot['comp']} ({100*tot['comp']/tot['dec']:.3f}%), "
      f"compression AND |ret10|>=6t={tot['comp_vel']}, "
      f"full trigger long={tot['trigL']} short={tot['trigS']}")
print("\nFSS-6 trigger events (all):")
for e in events:
    print(f"  {e['session']} {e['time']} {e['dir']:>5} mid={e['mid']:.1f} "
          f"comp=[{e['comp_lo']:.1f},{e['comp_hi']:.1f}] rng={e['rng']:.1f}t ret10={e['ret10']:+.1f}t")
csvL = int(R[(R.family == "FSS6") & (R.A == 24) & (R.dir == "long")].n_trig.sum())
csvS = int(R[(R.family == "FSS6") & (R.A == 24) & (R.dir == "short")].n_trig.sum())
print(f"cross-check vs by_session CSV n_trig: long {tot['trigL']} == {csvL}: "
      f"{tot['trigL'] == csvL} | short {tot['trigS']} == {csvS}: {tot['trigS'] == csvS}")

# ---------- 3: FSS-7 pure-Python re-simulation ----------
print("\n=== [3] FSS-7 pure-Python re-simulation (independent code path) ===")


def fss7_trig_indep(ml, ret20, t):
    """Independent: back-scan for last sign flip; slice extremes."""
    r = ret20[t]
    if np.isnan(r) or abs(r) < 12.0:
        return 0
    s = t
    if r > 0:
        while s >= 0 and not (np.isnan(ret20[s]) or ret20[s] <= 0.0):
            s -= 1
        ms = s + 1
        if ms > t: return 0
        E = ml[ms:t + 1].max(); base = ml[ms]
        disp = E - base
        return 1 if (disp > 0 and (E - ml[t]) <= 0.25 * disp) else 0
    else:
        while s >= 0 and not (np.isnan(ret20[s]) or ret20[s] >= 0.0):
            s -= 1
        ms = s + 1
        if ms > t: return 0
        E = ml[ms:t + 1].min(); base = ml[ms]
        disp = base - E
        return -1 if (disp > 0 and (ml[t] - E) <= 0.25 * disp) else 0


def resim(tag, A, B):
    f, ml, hi, lo, dec = load(tag)
    n = len(ml)
    ret20 = np.full(n, np.nan); ret20[20:] = ml[20:] - ml[:-20]
    out = {("long", k): 0 for k in ("n", "tgt", "adv", "cap")}
    out.update({("short", k): 0 for k in ("n", "tgt", "adv", "cap")})
    gsum = {"long": 0.0, "short": 0.0}
    t = 0
    while t < n - 1:
        dv = fss7_trig_indep(ml, ret20, t) if dec[t] else 0
        if dv == 0:
            t += 1
            continue
        entry = ml[t]; end = min(t + CAP, n - 1)
        res = 0; i = t + 1
        while i <= end:
            up = hi[i] - entry; dn = entry - lo[i]
            th = (up >= A) if dv == 1 else (dn >= A)
            ah = (dn >= B) if dv == 1 else (up >= B)
            if ah: res = 2; break        # adverse dominates (incl. both-crossed)
            if th: res = 1; break
            i += 1
        if res == 1: g = A
        elif res == 2: g = -B
        else: res = 3; g = (ml[end] - entry) * dv; i = end
        dname = "long" if dv == 1 else "short"
        out[(dname, "n")] += 1
        out[(dname, ("tgt", "adv", "cap")[res - 1])] += 1
        gsum[dname] += g
        t = i + COOL
    return out, gsum


heavy = (R[(R.family == "FSS7") & (R.A == 24)].groupby("session").n.sum()
         .sort_values(ascending=False).index[:2].tolist())
allmatch = True
for tag in heavy:
    for (A, B) in BRK:
        out, gsum = resim(tag, A, B)
        for dname in ("long", "short"):
            row = R[(R.session == tag) & (R.family == "FSS7") & (R.A == int(A)) &
                    (R.B == int(B)) & (R.dir == dname)].iloc[0]
            ok = (out[(dname, "n")] == row.n and out[(dname, "tgt")] == row.n_tgt and
                  out[(dname, "adv")] == row.n_adv and out[(dname, "cap")] == row.n_cap and
                  abs(gsum[dname] - row.gross_sum) < 1e-9)
            allmatch &= ok
            print(f"  {tag} FSS7 +{int(A)}/-{int(B)} {dname:>5}: resim n={out[(dname,'n')]} "
                  f"tgt={out[(dname,'tgt')]} adv={out[(dname,'adv')]} cap={out[(dname,'cap')]} "
                  f"gross={gsum[dname]:+.1f} | csv n={row.n} tgt={row.n_tgt} adv={row.n_adv} "
                  f"cap={row.n_cap} gross={row.gross_sum:+.1f} | MATCH={ok}")
print(f"FSS-7 independent re-simulation: ALL MATCH = {allmatch}")

# ---------- 4: pooled cross-foot ----------
print("\n=== [4] pooled CSV cross-foot from by-session CSV ===")
bad = 0
for _, r in P.iterrows():
    gsel = R[(R.family == r.family) & (R.A == r.A) & (R.B == r.B) & (R.dir == r["dir"])]
    ge = gsel[gsel.n > 0]
    n = int(ge.n.sum())
    if n == 0:
        continue
    net1 = float(ge.gross_sum.sum()) / n - C1
    ptgt = int(ge.n_tgt.sum()) / max(1, int(ge.n_tgt.sum()) + int(ge.n_adv.sum()))
    ok = (n == r.episodes and abs(net1 - r.net_c1) < 1e-9 and abs(ptgt - r.p_tgt) < 1e-9
          and int(ge.session.nunique()) == r.unique_days
          and abs((r.net_c1 - 2.0) - r.net_c2) < 1e-9)
    if not ok:
        bad += 1
        print(f"  CROSS-FOOT FAIL: {r.family} {r.A}/{r.B} {r['dir']}")
print(f"cross-foot failures: {bad} / {len(P)} rows")
print("\nVERIFY DONE")
