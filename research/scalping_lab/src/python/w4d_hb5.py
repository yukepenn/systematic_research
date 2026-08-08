"""W4-D — H-B5 spike continuation vs reversal (classification -> at most one frozen rule).
Spec: specs/W4_alpha_wave1.md section W4-D (frozen before readout). Seed 20260808.

Spike: |mid_last(t) - mid_last(t-10)| >= 16t on RTH quote-alive seconds; episode
collapse 60s (first second wins). From spike second: CONT = further +12t in spike
direction before -8t against within 300s (per-second hi/lo scan, conservative
same-second-both-crossed -> adverse); REV = mirror; NEITHER otherwise.
Univariate conditioner cells; FROZEN trigger: any cell |P(CONT)-pooled| >= 10pp with
n >= 100 and >= 15 sessions -> exactly ONE trade readout (largest |dev| cell):
enter spike-end+10s in favored direction, bracket (24,8), cap 300s, cooldown 60s.
"""
import glob, os
import numpy as np, pandas as pd
from numba import njit

SPIKE_K = 10
SPIKE_T = 16.0
COLLAPSE = 60
CAP = 300
CONT_A, CONT_B = 12.0, 8.0     # +12 in spike dir before -8 against
RET_WIN = 10                   # first-10s retracement window
RET_SPLIT = 0.25
TRADE_DELAY = 10
TRADE_A, TRADE_B = 24.0, 8.0
TRADE_COOL = 60
C1, C2 = 2.872, 4.872
SEED = 20260808
NBOOT = 1000
BLOCKS = [("0930_1030", 9*3600+1800, 10*3600+1800), ("1030_1200", 10*3600+1800, 12*3600),
          ("1200_1400", 12*3600, 14*3600), ("1400_1600", 14*3600, 16*3600)]

SH = "research/scalping_lab/substrate/sechilo/NQ"
GR = "research/scalping_lab/substrate/grid1s/NQ"
CAL = "research/04_complementary_family/c01_announcement_calendar.csv"
OUTD = "research/scalping_lab/artifacts/w4_hb5"
os.makedirs(OUTD, exist_ok=True)


@njit(cache=True)
def barrier_class(hi, lo, t0, ref, d, A, B, cap):
    """1 = target-first, 2 = adverse-first (conservative same-second), 3 = cap/no-resolve."""
    n = hi.shape[0]
    end = min(t0 + cap, n - 1)
    for i in range(t0 + 1, end + 1):
        up = hi[i] - ref
        dn = ref - lo[i]
        if d == 1:
            t_hit = up >= A; a_hit = dn >= B
        else:
            t_hit = dn >= A; a_hit = up >= B
        if t_hit and a_hit:
            return 2
        if a_hit:
            return 2
        if t_hit:
            return 1
    return 3


@njit(cache=True)
def trade_barrier(ml, hi, lo, te, entry, d, A, B, cap):
    """Returns (outcome 1 tgt/2 adv/3 cap, gross ticks, resolve index)."""
    n = ml.shape[0]
    end = min(te + cap, n - 1)
    for i in range(te + 1, end + 1):
        up = hi[i] - entry
        dn = entry - lo[i]
        if d == 1:
            t_hit = up >= A; a_hit = dn >= B
        else:
            t_hit = dn >= A; a_hit = up >= B
        if t_hit and a_hit:
            return 2, -B, i
        if a_hit:
            return 2, -B, i
        if t_hit:
            return 1, A, i
    return 3, (ml[end] - entry) * d, end


def block_of(tod):
    for name, a, b in BLOCKS:
        if a <= tod < b:
            return name
    return "other"


# ---- calendar (inspected: columns date,event,time_et,source; time_et = HH:MM ET) ----
cal = pd.read_csv(CAL)
cal["date"] = pd.to_datetime(cal["date"])
hm = cal["time_et"].str.split(":", expand=True).astype(int)
cal["ev_sec"] = hm[0] * 3600 + hm[1] * 60
cal_by_date = cal.groupby("date")["ev_sec"].apply(list).to_dict()
print(f"calendar loaded: {len(cal)} rows, events={sorted(cal['event'].unique())}, "
      f"usable time_et for all rows: {cal['ev_sec'].notna().all()}")

sessions = sorted(os.path.basename(p)[:-8] for p in glob.glob(os.path.join(SH, "s*.parquet")))
epi_rows = []
arrays = {}   # session -> (ml, hi, lo) for the (at most one) trade readout

for tag in sessions:
    d = pd.to_datetime(tag[1:], format="%Y%m%d")
    g = pd.read_parquet(os.path.join(GR, tag + ".parquet"))
    s = pd.read_parquet(os.path.join(SH, tag + ".parquet"))
    g["time"] = pd.to_datetime(g["time"]); s["time"] = pd.to_datetime(s["time"])
    f = g.merge(s, on="time", how="left")
    f["mid_last"] = f["mid_last"].ffill()
    f = f[f["mid_last"].notna()].reset_index(drop=True)
    f["mid_high"] = f["mid_high"].fillna(f["mid_last"])
    f["mid_low"] = f["mid_low"].fillna(f["mid_last"])
    ml = f["mid_last"].values; hi = f["mid_high"].values; lo = f["mid_low"].values
    n = len(f)
    tod = (f["time"] - d).dt.total_seconds().values
    upd60 = pd.Series((f["bid_upd"] + f["ask_upd"]).values).rolling(60, min_periods=1).sum().values
    dec = (tod >= 9 * 3600 + 1800) & (tod < 16 * 3600) & (upd60 > 0)
    spread = f["spread_t"].values
    arrays[tag] = (ml, hi, lo)

    d10 = pd.Series(ml).diff(SPIKE_K).values
    spike = dec & ~np.isnan(d10) & (np.abs(d10) >= SPIKE_T)
    ev_secs = cal_by_date.get(d, [])

    last_acc = -10**9
    for t0 in np.where(spike)[0]:
        if t0 < last_acc + COLLAPSE:
            continue
        last_acc = t0
        sgn = 1 if d10[t0] > 0 else -1
        cont = barrier_class(hi, lo, t0, ml[t0], sgn, CONT_A, CONT_B, CAP)
        rev = barrier_class(hi, lo, t0, ml[t0], -sgn, CONT_A, CONT_B, CAP)
        if cont == 1:
            out = "CONT"
        elif rev == 1:
            out = "REV"
        else:
            out = "NEITHER"
        # (1) scheduled-news proximity +-5 min
        near = any(abs(tod[t0] - es) <= 300 for es in ev_secs)
        # (2) pre-trend alignment: sign(mid(t-10) - mid(t-310)) vs spike sign
        if t0 - (SPIKE_K + 300) >= 0:
            pre = ml[t0 - SPIKE_K] - ml[t0 - SPIKE_K - 300]
            if pre * sgn > 0:
                ptr = "aligned"
            elif pre * sgn < 0:
                ptr = "opposite"
            else:
                ptr = "zero"
        else:
            ptr = "na"
        # (3) spread at spike second
        spc = "sp<=2" if spread[t0] <= 2.0 else "sp>2"
        # (4) first-10s retracement fraction from spike-end extreme
        e10 = min(t0 + RET_WIN, n - 1)
        if e10 >= t0 + 1:
            if sgn == 1:
                retr = max(0.0, hi[t0] - lo[t0 + 1:e10 + 1].min())
            else:
                retr = max(0.0, hi[t0 + 1:e10 + 1].max() - lo[t0])
            frac = retr / SPIKE_T
            rc = "ret<=0.25" if frac <= RET_SPLIT else "ret>0.25"
        else:
            frac = np.nan; rc = "na"
        epi_rows.append(dict(session=tag, t0=int(t0), tod=float(tod[t0]), dir=int(sgn),
                             d10=float(d10[t0]), outcome=out, cont_res=int(cont),
                             rev_res=int(rev), near_news=bool(near), pretrend=ptr,
                             spread_cell=spc, spread_t=float(spread[t0]),
                             ret_frac=float(frac) if not np.isnan(frac) else np.nan,
                             ret_cell=rc, block=block_of(tod[t0])))
    print(tag, "done", flush=True)

E = pd.DataFrame(epi_rows)
E.to_csv(os.path.join(OUTD, "w4d_episodes.csv"), index=False)
n_sess = len(sessions)
N = len(E)
print(f"\n=== W4-D H-B5 spike episodes: {N} episodes, {E['session'].nunique()} unique sessions "
      f"of {n_sess}, {N / n_sess:.2f} episodes/day ===")
print("by direction:", E["dir"].value_counts().to_dict())

# ---- pooled classification ----
pool = E["outcome"].value_counts()
pP = {k: pool.get(k, 0) / N for k in ("CONT", "REV", "NEITHER")}
print(f"\npooled: P(CONT)={pP['CONT']:.4f}  P(REV)={pP['REV']:.4f}  P(NEITHER)={pP['NEITHER']:.4f}  (n={N})")
nei = E[E.outcome == "NEITHER"]
both_adv = int(((nei.cont_res == 2) & (nei.rev_res == 2)).sum())
print(f"NEITHER breakdown: both-adverse(whipsaw)={both_adv}, cap-unresolved={len(nei) - both_adv}")

# day-clustered CI on pooled P(CONT)
rng = np.random.default_rng(SEED)
per = E.groupby("session")["outcome"].agg(cont=lambda x: (x == "CONT").sum(), tot="size")
sess_list = per.index.to_numpy()
cv = per["cont"].values.astype(float); tv = per["tot"].values.astype(float)
boots = []
for _ in range(NBOOT):
    b = rng.choice(len(sess_list), len(sess_list), replace=True)
    boots.append(cv[b].sum() / tv[b].sum())
print(f"pooled P(CONT) day-clustered 95% CI: [{np.percentile(boots, 2.5):.4f}, {np.percentile(boots, 97.5):.4f}]")

# long/short pooled split
for dv, nm in ((1, "up-spike"), (-1, "dn-spike")):
    g = E[E.dir == dv]
    if len(g):
        vc = g["outcome"].value_counts()
        print(f"  {nm}: n={len(g)} P(CONT)={vc.get('CONT', 0)/len(g):.4f} "
              f"P(REV)={vc.get('REV', 0)/len(g):.4f} P(NEITHER)={vc.get('NEITHER', 0)/len(g):.4f}")

# ---- conditioner cells (univariate) ----
def cells_of(col):
    for val, g in E.groupby(col, dropna=False):
        yield f"{col}={val}", g

cell_rows = []
print(f"\n=== conditioner cells: P(CONT) vs pooled {pP['CONT']:.4f} "
      f"(trigger: |dev| >= 0.10, n >= 100, sessions >= 15) ===")
print(f"{'cell':<28} {'n':>5} {'sess':>4} {'P(CONT)':>8} {'P(REV)':>7} {'P(NEI)':>7} {'dev':>7} {'trig':>5}")
for col in ("near_news", "pretrend", "spread_cell", "ret_cell", "block"):
    for name, g in cells_of(col):
        ncell = len(g); ns = g["session"].nunique()
        pc = (g.outcome == "CONT").mean(); prv = (g.outcome == "REV").mean()
        pn = (g.outcome == "NEITHER").mean()
        dev = pc - pP["CONT"]
        trig = (abs(dev) >= 0.10) and (ncell >= 100) and (ns >= 15)
        cell_rows.append(dict(conditioner=col, cell=name, n=ncell, sessions=ns,
                              p_cont=round(pc, 4), p_rev=round(prv, 4), p_neither=round(pn, 4),
                              dev=round(dev, 4), qualifies=trig))
        print(f"{name:<28} {ncell:>5} {ns:>4} {pc:>8.4f} {prv:>7.4f} {pn:>7.4f} {dev:>+7.4f} {str(trig):>5}")
CL = pd.DataFrame(cell_rows)
CL.to_csv(os.path.join(OUTD, "w4d_cells.csv"), index=False)

# news conditioner evaluability note
nn = E[E.near_news]
print(f"\nnews conditioner: calendar usable=YES; near-news episodes={len(nn)} "
      f"(NFP/CPI 08:30 is pre-RTH so only FOMC 14:00 can overlap RTH spikes)")

# ---- frozen rule trigger ----
qual = CL[CL.qualifies].copy()
if len(qual) == 0:
    print("\nFROZEN TRIGGER: no cell qualifies (|dev| >= 10pp with n >= 100 and >= 15 sessions).")
    print("NO trade readout — classification tables are the deliverable.")
else:
    qual["absdev"] = qual["dev"].abs()
    top = qual.sort_values("absdev", ascending=False).iloc[0]   # frozen tie-break: largest |dev|
    col = top["conditioner"]; val = top["cell"].split("=", 1)[1]
    # rebuild the cell membership mask
    Ecol = E[col].astype(str)
    mask = Ecol == val
    favored = "CONT" if top["dev"] > 0 else "REV"
    print(f"\nFROZEN TRIGGER FIRED: cell {top['cell']} (n={top['n']}, sessions={top['sessions']}, "
          f"dev={top['dev']:+.4f}) -> ONE trade readout, favored={favored}")
    print(f"rule: enter spike-end+{TRADE_DELAY}s, dir = {'spike dir' if favored == 'CONT' else 'anti-spike'}, "
          f"bracket ({TRADE_A:.0f},{TRADE_B:.0f}), cap {CAP}s, cooldown {TRADE_COOL}s")
    tr_rows = []
    for tag in sessions:
        ml, hi, lo = arrays[tag]
        sub = E[(E.session == tag) & mask.values].sort_values("t0")
        last_end = -10**9
        for _, r in sub.iterrows():
            te = int(r.t0) + TRADE_DELAY
            if te >= len(ml) - 1:
                continue
            if te < last_end + TRADE_COOL:
                continue
            dtr = int(r.dir) if favored == "CONT" else -int(r.dir)
            outc, gross, ridx = trade_barrier(ml, hi, lo, te, ml[te], dtr,
                                              TRADE_A, TRADE_B, CAP)
            last_end = ridx
            tr_rows.append(dict(session=tag, t0=int(r.t0), te=te, dir=dtr, outcome=int(outc),
                                gross=float(gross)))
    T = pd.DataFrame(tr_rows)
    T.to_csv(os.path.join(OUTD, "w4d_trade_readout.csv"), index=False)

    def readout(name, TT):
        if len(TT) == 0:
            print(f"  {name}: 0 trades")
            return
        nt = len(TT); days = TT["session"].nunique()
        n_tgt = int((TT.outcome == 1).sum()); n_adv = int((TT.outcome == 2).sum())
        n_cap = int((TT.outcome == 3).sum())
        ptgt = n_tgt / max(1, n_tgt + n_adv)
        gm = TT.gross.mean()
        net1 = gm - C1; net2 = gm - C2
        per = TT.groupby("session")["gross"].agg(["mean", "size"])
        pm = per["mean"].values - C1; pw = per["size"].values.astype(float)
        rb = np.random.default_rng(SEED)
        bts = []
        for _ in range(NBOOT):
            b = rb.choice(len(pm), len(pm), replace=True)
            bts.append(np.average(pm[b], weights=pw[b]))
        lo95, hi95 = np.percentile(bts, 2.5), np.percentile(bts, 97.5)
        print(f"  {name}: trades={nt} trades/day={nt / n_sess:.3f} unique_days={days} "
              f"tgt/adv/cap={n_tgt}/{n_adv}/{n_cap} P(tgt-first)={ptgt:.4f}")
        print(f"      netC1={net1:+.3f}t  CI95=[{lo95:+.3f}, {hi95:+.3f}]  netC2={net2:+.3f}t  "
              f"gross={gm:+.3f}t")

    print(f"\n=== TRADE READOUT (cell {top['cell']}, favored {favored}) ===")
    readout("ALL   ", T)
    readout("LONG  ", T[T.dir == 1])
    readout("SHORT ", T[T.dir == -1])

print("\nW4D DONE")
