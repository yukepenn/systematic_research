# G3_ONDEALER_20260906  (ledger G00090, family GENESIS3_EVENT)
# Dealer-inventory overnight drift (European-open window). Frozen object per spec.yaml.
# Program-printed gate table; ALL cells reported; mechanical clauses only; POINTS basis.
#
# FROZEN MECHANICAL READINGS (stated here, before any result is computed):
#  R1. Substrate: runs/SM1M_ES_SUBSTRATE/out/es_1m_2022_2026.parquet, POINTS, bars END-stamped
#      ET (bar stamped 18:01 covers 18:00:00-18:01:00). Session = trade date: bars with
#      end-stamp minute-of-day > 17*60 belong to the NEXT day (CLOSEHOUR convention).
#  R2. 1-min return r_t = close_t - close_{t-1} WITHIN session only (first bar of each
#      session has no return; the 17:00->18:01 halt gap belongs to no minute). Returns after
#      intra-session missing bars telescope into the next bar and stay at its clock slot.
#  R3. Overnight grid 17:00->09:30 ET: bars whose OPEN time (end-stamp minus 1 min) lies in
#      [18:00, 09:30) ET. The 17:xx cell is structurally empty (CME halt; verified 0 bars).
#      K = 16 clock cells: open-hour 18,19,20,21,22,23,0,1,...,8 (full) + 09:00-09:29 partial.
#  R4. Stage-1 cell statistic: pooled per-minute mean mu_h = sum(r in cell h)/count(cell h).
#  R5. G2 null ("circular-shift null that PRESERVES the diurnal grid; shift whole sessions,
#      never minutes"): TWO constructions, both printed.
#      (a) LITERAL whole-session circular shift: session s's overnight return vector is
#          reassigned to calendar slot s+k, every return keeping its clock position. For a
#          full-sample pooled cell mean this is a PERMUTATION of the same multiset and is
#          IDENTICALLY INVARIANT (a mathematical identity). The program COMPUTES it for
#          k in {1,5,25,125,625} and prints max |null-obs| over all 16 cells, to record the
#          degeneracy as a measured fact rather than assert it.
#      (b) OPERATIVE powered null (the frozen reading G2 is decided on): grid-preserving
#          WHOLE-SESSION randomization at session granularity -- each session's ENTIRE
#          overnight vector is multiplied by eps_s in {-1,+1}, ONE shared draw per session
#          across all 16 cells per replicate (CLAUDE.md 'one shared draw per session across
#          a family'). No minute is ever moved; every |return| keeps its clock slot; the
#          diurnal vol grid and within-session cross-cell dependence are preserved exactly.
#          B=10,000, seed 20260906. Two-sided p_h = (1+#{|mu_h*|>=|mu_h|})/(B+1).
#          G2 clause: min_h p_h <= alpha_corr = 0.05/K_eff, K=16,
#          K_eff = K/(1+(K-1)*rho_bar) clamped to [1,K], rho_bar = mean pairwise corr of the
#          session-level cell-sum series X[s,h]. Second computation for any clearing cell:
#          session-cluster normal-approx z and circular session-block bootstrap CI (L=10,
#          B=2,000). p stated in words (CAP01 rule).
#  R6. Stage 2: price@02:00 = close of bar end-stamped 02:00; price@05:00 = close of bar
#      end-stamped 05:00; Euro-window W[s] = c(05:00) - c(02:00) (POINTS). Prior-RTH return
#      R[s-1] = c(16:00) - c(09:30) of the PREVIOUS session in the panel (causal: ends before
#      the 18:00 open of session s's overnight). DOWN: R<0; UP: R>0; R==0 excluded from
#      conditional cells, kept in the control. Control = ALL eligible sessions, same window
#      (spec: matched unconditional control). Eligible = W defined AND prior-session RTH
#      defined. BOTH directions (DOWN and UP cells) fully reported; the GATING cell is DOWN
#      (named by G3). EFFECT := mean(W|DOWN) - mean(W|all eligible).
#  R7. G3 null (here the whole-session circular shift has power and is used LITERALLY):
#      roll the prior-RTH-direction flag series by k whole sessions against the FIXED W
#      series, k = 1..N_e-1 FULLY ENUMERATED, same k shared by DOWN and UP cells
#      (dependence preserved). G3 clause: two-sided p = (1+#{|delta*|>=|delta_obs|})/N_e
#      <= 0.05 for the DOWN cell. Second computation: joint circular session-block bootstrap
#      CI of the delta (L=10, B=2,000).
#  R8. G4 ON cost floor (BASIS = MODELED ALL_IN, family convention: ticks PER SIDE + $4.36
#      Lifetime commission): ES tick 0.25 pt = $12.50, $50/pt.
#      1tk/side RT = $29.36 = 0.5872 pt; 2tk/side RT = $54.36 = 1.0872 pt -- the 2-tick rung
#      GATES (spec: thin overnight book). Tradable = the DOWN cell held 02:00->05:00, one
#      RT per conditioning day, direction = sign(mean_down).
#      G4 clause: |mean_down| - 1.0872 pt > 0 over the full (post-2022 = whole-substrate)
#      sample. Both rungs printed; |EFFECT| printed beside (spec words '|effect| vs the ON
#      cost floor').
#  R9. G5 chronology: era1 = sessions <= 2023-12-31 ('2022-23'), era2 >= 2024-01-01
#      ('2024-26'). G5 clause: sign(EFFECT_era1) == sign(EFFECT_era2) (the effect's sign,
#      per the spec sentence tying sign consistency to the effect). Cell-mean era signs
#      printed beside (not gating).
#  R10. G1: MDE printed per cell (all 16 hour cells + DOWN/UP conditional cells) BEFORE any
#      observed mean is printed. MDE_sig = 1.96*SE, MDE_80 = 2.8016*SE.
#  R11. Seal: assert max bar time < 2026-08-01 before anything else. DST note: the
#      02:00-05:00 band is FIXED ET CLOCK (spec); the European local open drifts inside it
#      on the ~2-3 US/EU DST-mismatch weeks per year -- disclosed, not modeled.

import io
import os
import hashlib
import numpy as np
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
RUN = os.path.join(ROOT, "runs", "G3_ONDEALER_20260906")
OUT = os.path.join(RUN, "out")
os.makedirs(OUT, exist_ok=True)

SEAL = pd.Timestamp("2026-08-01")
SEED = 20260906
B_FLIP = 10_000
B_BOOT = 2_000
BLOCK_L = 10

COMM = 4.36
TICK_USD = 12.50
PT_USD = 50.0
COST_PRIMARY_USD = 2 * TICK_USD + COMM      # 1 tick/side RT
COST_STRESS_USD = 4 * TICK_USD + COMM       # 2 ticks/side RT (GATES)
COST_PRIMARY_PTS = COST_PRIMARY_USD / PT_USD
COST_STRESS_PTS = COST_STRESS_USD / PT_USD

buf = io.StringIO()
def P(s=""):
    print(s)
    buf.write(s + "\n")

HR = "=" * 100
P(HR)
P("G3_ONDEALER_20260906  (ledger G00090, family GENESIS3_EVENT)   EVIDENCE STATUS: DISCOVERY")
P("Dealer-inventory overnight drift: Stage 1 = ES overnight clock-hour grid (17:00->09:30 ET);")
P("Stage 2 = prior-RTH-DOWN conditional Euro-window (02:00->05:00 ET) vs matched unconditional control.")
P("POINTS basis on the back-adjusted ES 1-min substrate. Frozen mechanical readings R1-R11 in src header.")
P(f"cost floor (BASIS=MODELED ALL_IN, comm ${COMM:.2f}/ctRT + spread PER SIDE): "
  f"PRIMARY 1tk/side ${COST_PRIMARY_USD:.2f} RT = {COST_PRIMARY_PTS:.4f} pt; "
  f"STRESS 2tk/side ${COST_STRESS_USD:.2f} RT = {COST_STRESS_PTS:.4f} pt  << the 2-tick rung GATES (thin ON book)")
P("")

# ------------------------------------------------------------------ load + seal
PATH = os.path.join(ROOT, "runs", "SM1M_ES_SUBSTRATE", "out", "es_1m_2022_2026.parquet")
sha = hashlib.sha256(open(PATH, "rb").read()).hexdigest()
df = pd.read_parquet(PATH, columns=["time", "close"])
tmax = df["time"].max()
assert tmax < SEAL, f"SEAL VIOLATION: max time {tmax}"
n_on_after = int((df["time"] >= SEAL).sum())
assert n_on_after == 0
P(f"[G0] substrate {os.path.relpath(PATH, ROOT)}")
P(f"     sha256 {sha}")
P(f"     bars {len(df):,}; span {df['time'].min()} .. {tmax}; bars >= 2026-08-01: {n_on_after}  SEAL OK")

mins = (df["time"].dt.hour * 60 + df["time"].dt.minute).to_numpy()
sess = (df["time"].dt.normalize() + pd.to_timedelta((mins > 17 * 60).astype(int), unit="D")).to_numpy()
df = df.assign(sess=sess, mins=mins)
open_mins = (mins - 1) % 1440
df["open_mins"] = open_mins
n17 = int(((open_mins >= 17 * 60) & (open_mins < 18 * 60)).sum())
assert n17 == 0, f"unexpected 17:xx-open bars: {n17}"
P(f"     sessions {df['sess'].nunique():,}; 17:xx-open bars {n17} (halt cell structurally empty, as frozen)")

# within-session 1-min returns (POINTS)
df["r"] = df.groupby("sess")["close"].diff()

# overnight bars: open time in [18:00, 09:30)
on_mask = (df["open_mins"] >= 18 * 60) | (df["open_mins"] < 9 * 60 + 30)
df["on"] = on_mask
# cell = open hour; partial cell 9 covers 09:00-09:29 opens
df["cell"] = np.where(on_mask, df["open_mins"] // 60, -1)

CELL_ORDER = [18, 19, 20, 21, 22, 23, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
CELL_LABEL = {h: (f"{h:02d}:00-{h:02d}:59" if h != 9 else "09:00-09:29") for h in CELL_ORDER}
K = len(CELL_ORDER)

onb = df[df["on"] & df["r"].notna()]
# session-level cell sums and counts
Xp = onb.pivot_table(index="sess", columns="cell", values="r", aggfunc="sum")
Np = onb.pivot_table(index="sess", columns="cell", values="r", aggfunc="size")
Xp = Xp.reindex(columns=CELL_ORDER)
Np = Np.reindex(columns=CELL_ORDER)
sessions = Xp.index
N_sess = len(sessions)
Xmat = Xp.to_numpy()                      # (N_sess, K) with NaN where no bars
Nmat = np.nan_to_num(Np.to_numpy(), nan=0.0)
M_h = Nmat.sum(axis=0)                    # bars per cell
n_sess_h = (~np.isnan(Xmat)).sum(axis=0)
X0 = np.nan_to_num(Xmat, nan=0.0)
short_sessions = int((Nmat.sum(axis=1) < 300).sum())
P(f"     overnight bars with return: {len(onb):,}; sessions in grid {N_sess:,}; "
  f"sessions with <300 ON bars: {short_sessions} (kept AS-IS; map artifact)")
P("     POINTS only: no percent column is formed anywhere in this program.")
P("")

# ------------------------------------------------------------------ G1: MDE FIRST
P("[G1] MDE FIRST (printed before any observed mean).  SE_h = sd_s(X[s,h])*sqrt(N_h)/M_h (session-cluster,")
P("     per-minute pts); MDE_sig = 1.96*SE, MDE_80 = 2.8016*SE (5% two-sided, 80% power).  Cell-total MDE = MDE*60.")
sd_h = np.array([np.nanstd(Xmat[:, j], ddof=1) for j in range(K)])
se_h = sd_h * np.sqrt(n_sess_h) / M_h
P("     cell         n_bars  n_sess   SE(pt/min)  MDE_sig(pt/min)  MDE_80(pt/min)  MDE_80(cell-hold pt)")
for j, h in enumerate(CELL_ORDER):
    hold = 60 if h != 9 else 30
    P(f"     {CELL_LABEL[h]:12s}{int(M_h[j]):8d}{int(n_sess_h[j]):8d}   {se_h[j]:9.6f}     {1.96*se_h[j]:9.6f}      "
      f"{2.8016*se_h[j]:9.6f}        {2.8016*se_h[j]*hold:8.4f}")

# stage-2 structures (counts + MDE before observed means)
stamps = df[df["mins"].isin([2 * 60, 5 * 60, 9 * 60 + 30, 16 * 60])]
piv = stamps.pivot_table(index="sess", columns="mins", values="close", aggfunc="last")
piv.columns = [f"c{c}" for c in piv.columns]
piv = piv.reindex(sessions)
piv["W"] = piv["c300"] - piv["c120"]                        # Euro-window 02:00->05:00
piv["rth"] = piv["c960"] - piv["c570"]                      # same-session RTH 09:30->16:00
piv["rth_prev"] = piv["rth"].shift(1)                       # prior session's RTH (causal)
elig = piv[piv["W"].notna() & piv["rth_prev"].notna()].copy()
N_e = len(elig)
W = elig["W"].to_numpy()
flag = np.sign(elig["rth_prev"].to_numpy())                  # -1 DOWN, +1 UP, 0 excluded
n_down = int((flag < 0).sum()); n_up = int((flag > 0).sum()); n_zero = int((flag == 0).sum())
sdW = W.std(ddof=1)
se_down = sdW * np.sqrt(1.0 / n_down)
se_delta = sdW * np.sqrt(max(1.0 / n_down - 1.0 / N_e, 0.0))
P("")
P(f"     Stage 2 population: eligible sessions (W defined AND prior-RTH defined) = {N_e}")
P(f"       excluded: {N_sess - N_e} of {N_sess} (missing 02:00/05:00 stamp or prior 09:30/16:00 stamp)")
P(f"       DOWN {n_down} / UP {n_up} / zero-RTH {n_zero} (zero excluded from conditional cells, kept in control)")
P(f"       sd(W) = {sdW:.4f} pt;  SE(mean_down) ~ {se_down:.4f} pt;  SE(EFFECT) ~ {se_delta:.4f} pt")
P(f"       MDE_sig(EFFECT) = {1.96*se_delta:.4f} pt (${1.96*se_delta*PT_USD:.2f});  "
  f"MDE_80(EFFECT) = {2.8016*se_delta:.4f} pt (${2.8016*se_delta*PT_USD:.2f})")
P(f"       cost rungs for scale: PRIMARY {COST_PRIMARY_PTS:.4f} pt / STRESS(GATING) {COST_STRESS_PTS:.4f} pt")
G1 = True
P("")

# ------------------------------------------------------------------ family K_eff
C = pd.DataFrame(Xmat, columns=[str(h) for h in CELL_ORDER]).corr()
iu = np.triu_indices(K, 1)
rho_bar = float(np.nanmean(C.to_numpy()[iu]))
k_eff_raw = K / (1 + (K - 1) * rho_bar)
K_eff = float(min(K, max(1.0, k_eff_raw)))
alpha_corr = 0.05 / K_eff
P(f"[family] K = {K} clock cells; mean pairwise corr of session cell-sums rho_bar = {rho_bar:+.4f} "
  f"({len(iu[0])} pairs)")
P(f"         K_eff = K/(1+(K-1)*rho_bar) = {k_eff_raw:.3f} -> clamped [1,{K}] = {K_eff:.3f}")
P(f"         K_eff-corrected two-sided alpha = 0.05/K_eff = {alpha_corr:.5f}")
P("")

# ------------------------------------------------------------------ Stage 1 observed grid
mu_h = X0.sum(axis=0) / M_h                                  # pooled pts/min
tot_h = X0.sum(axis=0)
mu_on = X0.sum() / M_h.sum()
t_h = mu_h / se_h
era1_mask = sessions <= pd.Timestamp("2023-12-31")
era2_mask = ~era1_mask
mu_h_e1 = np.nan_to_num(Xmat[era1_mask], nan=0.0).sum(axis=0) / Nmat[era1_mask].sum(axis=0)
mu_h_e2 = np.nan_to_num(Xmat[era2_mask], nan=0.0).sum(axis=0) / Nmat[era2_mask].sum(axis=0)

# ------------------------------------------------------------------ G2 nulls
# (a) literal whole-session circular shift -- computed, expected exactly invariant
lit_diffs = []
for k in (1, 5, 25, 125, 625):
    Tk = np.roll(X0, k, axis=0).sum(axis=0)
    Mk = np.roll(Nmat, k, axis=0).sum(axis=0)
    lit_diffs.append(np.max(np.abs(Tk / Mk - mu_h)))
lit_max = max(lit_diffs)

# (b) operative powered null: shared per-session sign flips
rng = np.random.default_rng(SEED)
X_on_sess = X0.sum(axis=1)                                   # session overnight sums
null_ge = np.zeros(K)
null_loc_ge = np.zeros(K)
loc_obs = mu_h - mu_on
CH = 2_000
done = 0
while done < B_FLIP:
    b = min(CH, B_FLIP - done)
    E = rng.integers(0, 2, size=(b, N_sess)).astype(np.float64) * 2 - 1
    nT = E @ X0                                              # (b, K)
    nmu = nT / M_h
    null_ge += (np.abs(nmu) >= np.abs(mu_h)).sum(axis=0)
    nmu_on = (E @ X_on_sess) / M_h.sum()
    null_loc_ge += (np.abs(nmu - nmu_on[:, None]) >= np.abs(loc_obs)).sum(axis=0)
    done += b
p_flip = (1 + null_ge) / (B_FLIP + 1)
p_loc = (1 + null_loc_ge) / (B_FLIP + 1)

# second computation: normal-approx cluster z -> two-sided p
from math import erf, sqrt
p_norm = np.array([2 * (1 - 0.5 * (1 + erf(abs(t) / sqrt(2)))) for t in t_h])

# session-block bootstrap CI per cell (circular, L=10, shared indices across cells)
nb = int(np.ceil(N_sess / BLOCK_L))
starts = rng.integers(0, N_sess, size=(B_BOOT, nb))
idx = (starts[:, :, None] + np.arange(BLOCK_L)[None, None, :]) % N_sess
idx = idx.reshape(B_BOOT, -1)[:, :N_sess]
boot_mu = np.empty((B_BOOT, K))
for b in range(B_BOOT):
    ii = idx[b]
    boot_mu[b] = X0[ii].sum(axis=0) / np.maximum(Nmat[ii].sum(axis=0), 1)
ci_lo = np.percentile(boot_mu, 2.5, axis=0)
ci_hi = np.percentile(boot_mu, 97.5, axis=0)

P("[Stage 1] ES overnight clock-hour grid (BANKED as the ES overnight structure map either way).")
P("     mu = pooled mean pts/min; loc = mu - overnight-wide mean; p_flip = two-sided grid-preserving")
P("     session-randomization p (R5b); p_norm = cluster normal-approx (second computation);")
P("     CI95 = circular session-block bootstrap of mu (L=10, B=2000).")
P(f"     overnight-wide per-minute mean = {mu_on:+.6f} pt/min")
P("     cell          n_bars   mu(pt/min)    total_pt   t_clu   p_flip   p_norm    loc(pt/min)  p_loc    CI95(pt/min)          e1_mu      e2_mu")
csv_rows = []
for j, h in enumerate(CELL_ORDER):
    P(f"     {CELL_LABEL[h]:12s}{int(M_h[j]):8d}   {mu_h[j]:+.6f}   {tot_h[j]:+9.2f}   {t_h[j]:+5.2f}   "
      f"{p_flip[j]:.4f}   {p_norm[j]:.4f}   {loc_obs[j]:+.6f}   {p_loc[j]:.4f}   "
      f"[{ci_lo[j]:+.6f},{ci_hi[j]:+.6f}]   {mu_h_e1[j]:+.6f}   {mu_h_e2[j]:+.6f}")
    csv_rows.append(dict(cell=CELL_LABEL[h], open_hour=h, n_bars=int(M_h[j]), n_sessions=int(n_sess_h[j]),
                         mean_pts_per_min=mu_h[j], total_pts=tot_h[j], se_ppm=se_h[j], t_cluster=t_h[j],
                         p_flip_2s=p_flip[j], p_norm_2s=p_norm[j], loc_ppm=loc_obs[j], p_loc_2s=p_loc[j],
                         ci95_lo_ppm=ci_lo[j], ci95_hi_ppm=ci_hi[j],
                         era1_ppm=mu_h_e1[j], era2_ppm=mu_h_e2[j]))
P("")
P(f"[G2] (a) LITERAL whole-session circular shift, k in (1,5,25,125,625): max |null mu - obs mu| over 16 cells")
P(f"         = {lit_max:.3e}  -> IDENTICALLY INVARIANT (permutation identity); DEGENERATE for a full-sample")
P(f"         pooled cell mean; recorded as measured. G2 is decided on the OPERATIVE null (R5b).")
best_j = int(np.argmin(p_flip))
G2 = bool(p_flip.min() <= alpha_corr)
clearing = [CELL_LABEL[CELL_ORDER[j]] for j in range(K) if p_flip[j] <= alpha_corr]
P(f"     (b) OPERATIVE null, B={B_FLIP:,}, seed {SEED}: min two-sided p over cells = {p_flip.min():.4f} "
  f"at {CELL_LABEL[CELL_ORDER[best_j]]}; bar = {alpha_corr:.5f}")
P(f"         cells clearing the K_eff-corrected bar: {clearing if clearing else 'NONE'}")
P(f"     IN WORDS: p_flip[h] is the probability, under random re-signing of WHOLE overnight sessions")
P(f"     (each session's entire overnight minute-vector x +/-1, one shared draw per session across all")
P(f"     16 clock cells), that cell h's pooled per-minute mean is at least as large in MAGNITUDE as")
P(f"     observed. Second computation p_norm agrees/disagrees per cell above.")
P(f"     -> G2 {'PASS' if G2 else 'FAIL'}")
P("")

# ------------------------------------------------------------------ Stage 2 observed
m_down = W[flag < 0].mean(); m_up = W[flag > 0].mean(); m_all = W.mean()
eff_down = m_down - m_all
eff_up = m_up - m_all
e1e = elig.index <= pd.Timestamp("2023-12-31")
e2e = ~e1e
def cellmeans(mask):
    Wm = W[mask]; fm = flag[mask]
    return (Wm[fm < 0].mean() if (fm < 0).any() else np.nan,
            Wm[fm > 0].mean() if (fm > 0).any() else np.nan,
            Wm.mean(), int((fm < 0).sum()), int((fm > 0).sum()), int(mask.sum()))
d1, u1, a1, nd1, nu1, na1 = cellmeans(e1e)
d2, u2, a2, nd2, nu2, na2 = cellmeans(e2e)
eff1 = d1 - a1
eff2 = d2 - a2

# G3 null: fully enumerated whole-session circular shift of the flag against fixed W
deltas_dn = np.empty(N_e - 1); deltas_up = np.empty(N_e - 1)
for i, k in enumerate(range(1, N_e)):
    fk = np.roll(flag, k)
    deltas_dn[i] = W[fk < 0].mean() - m_all
    deltas_up[i] = W[fk > 0].mean() - m_all
p_dn = (1 + np.sum(np.abs(deltas_dn) >= abs(eff_down))) / N_e
p_up = (1 + np.sum(np.abs(deltas_up) >= abs(eff_up))) / N_e
p_dn_1s_pos = (1 + np.sum(deltas_dn >= eff_down)) / N_e
p_dn_1s_neg = (1 + np.sum(deltas_dn <= eff_down)) / N_e

# second computation: joint circular block bootstrap of (flag, W)
nb2 = int(np.ceil(N_e / BLOCK_L))
st2 = rng.integers(0, N_e, size=(B_BOOT, nb2))
idx2 = (st2[:, :, None] + np.arange(BLOCK_L)[None, None, :]) % N_e
idx2 = idx2.reshape(B_BOOT, -1)[:, :N_e]
boot_eff = np.empty(B_BOOT)
for b in range(B_BOOT):
    ii = idx2[b]
    Wb = W[ii]; fb = flag[ii]
    boot_eff[b] = (Wb[fb < 0].mean() if (fb < 0).any() else np.nan) - Wb.mean()
eff_ci = np.nanpercentile(boot_eff, [2.5, 97.5])

P("[Stage 2] Euro-window (02:00->05:00 ET) conditional on prior-RTH direction -- BOTH directions reported.")
P(f"     cell        n      mean W (pt)    $/event     EFFECT vs control (pt)   p_shift_2s")
P(f"     DOWN     {n_down:5d}     {m_down:+9.4f}   {m_down*PT_USD:+9.2f}          {eff_down:+9.4f}            {p_dn:.4f}   << GATING")
P(f"     UP       {n_up:5d}     {m_up:+9.4f}   {m_up*PT_USD:+9.2f}          {eff_up:+9.4f}            {p_up:.4f}")
P(f"     CONTROL  {N_e:5d}     {m_all:+9.4f}   {m_all*PT_USD:+9.2f}          (all eligible days, same window)")
P(f"     one-sided shift pcts for DOWN effect: P(delta* >= obs) = {p_dn_1s_pos:.4f}; P(delta* <= obs) = {p_dn_1s_neg:.4f}")
P(f"     block-bootstrap CI95 of EFFECT (second computation): [{eff_ci[0]:+.4f}, {eff_ci[1]:+.4f}] pt")
P(f"     eras: 2022-23 DOWN {d1:+.4f} (n={nd1}) UP {u1:+.4f} (n={nu1}) ALL {a1:+.4f} (n={na1}) EFFECT {eff1:+.4f}")
P(f"           2024-26 DOWN {d2:+.4f} (n={nd2}) UP {u2:+.4f} (n={nu2}) ALL {a2:+.4f} (n={na2}) EFFECT {eff2:+.4f}")
P(f"     IN WORDS: p_shift is the probability, under circular shifts of the prior-RTH-direction flag by")
P(f"     k WHOLE SESSIONS (k=1..{N_e-1}, fully enumerated, shared k across DOWN/UP) against the fixed")
P(f"     Euro-window return series, that |mean(W|pseudo-DOWN) - mean(W|all)| is at least as large as observed.")
G3 = bool(p_dn <= 0.05)
P(f"     -> G3 (DOWN cell beats matched unconditional control; two-sided shift p <= 0.05): "
  f"{'PASS' if G3 else 'FAIL'}")
P("")

# ------------------------------------------------------------------ G4 cost floor
net_primary = abs(m_down) - COST_PRIMARY_PTS
net_stress = abs(m_down) - COST_STRESS_PTS
G4 = bool(net_stress > 0)
P("[G4] ON cost floor (tradable = DOWN cell, held 02:00->05:00, direction = sign(mean_down), 1 RT/event):")
P(f"     |mean_down| = {abs(m_down):.4f} pt (${abs(m_down)*PT_USD:.2f}/event) on n={n_down} events over "
  f"{(sessions.max()-sessions.min()).days/365.25:.2f} yr")
P(f"     PRIMARY 1tk/side: net {net_primary:+.4f} pt (${net_primary*PT_USD:+.2f}/event)")
P(f"     STRESS  2tk/side: net {net_stress:+.4f} pt (${net_stress*PT_USD:+.2f}/event)   << GATES")
P(f"     |EFFECT| beside (spec words): {abs(eff_down):.4f} pt vs rungs {COST_PRIMARY_PTS:.4f}/{COST_STRESS_PTS:.4f} pt")
P(f"     -> G4 (|mean_down| - 2tk rung > 0, post-2022 = full substrate): {'PASS' if G4 else 'FAIL'}")
P("")

# ------------------------------------------------------------------ G5 chronology
s1 = np.sign(eff1); s2 = np.sign(eff2)
G5 = bool(s1 == s2 and s1 != 0)
P("[G5] chronology: sign consistency of the EFFECT across era halves")
P(f"     2022-23 EFFECT {eff1:+.4f} pt (n_down {nd1}) | 2024-26 EFFECT {eff2:+.4f} pt (n_down {nd2})")
P(f"     cell-mean era signs beside (not gating): DOWN {np.sign(d1):+.0f}/{np.sign(d2):+.0f}, "
  f"UP {np.sign(u1):+.0f}/{np.sign(u2):+.0f}")
P(f"     -> G5 (sign(EFFECT_2022-23) == sign(EFFECT_2024-26), both nonzero): {'PASS' if G5 else 'FAIL'}")
P("")

# ------------------------------------------------------------------ final gate table
P(HR)
P(f"{'GATE':<16s}{'SPEC':<70s}{'PASS/FAIL':>12s}")
P("-" * 100)
def row(g, spec, obs, ok):
    P(f"{g:<16s}{spec:<70s}{'PASS' if ok else 'FAIL':>12s}")
    P(f"{'':16s}OBSERVED: {obs}")
row("G1_MDE_first", "MDE printed per cell BEFORE observed means",
    f"16 hour cells + stage-2 printed; MDE_80(EFFECT) = {2.8016*se_delta:.4f} pt", G1)
row("G2_hour_structure", "a cell clears grid-preserving shift null at K_eff-corrected 5%",
    f"min p_flip {p_flip.min():.4f} at {CELL_LABEL[CELL_ORDER[best_j]]} vs bar {alpha_corr:.5f}; "
    f"K={K}, K_eff={K_eff:.2f}; literal shift degenerate ({lit_max:.1e})", G2)
row("G3_conditional", "DOWN cell beats matched unconditional control (2-sided shift p<=0.05)",
    f"EFFECT {eff_down:+.4f} pt, p_shift {p_dn:.4f}; boot CI [{eff_ci[0]:+.4f},{eff_ci[1]:+.4f}]", G3)
row("G4_cost_floor", "{1,2}-tick ON band; 2-tick rung GATES; net-of-cost survival post-2022",
    f"|mean_down| {abs(m_down):.4f} pt; STRESS net {net_stress:+.4f} pt (${net_stress*PT_USD:+.2f}/event)", G4)
row("G5_chronology", "2022-23 vs 2024-26 sign consistency (EFFECT)",
    f"{eff1:+.4f} vs {eff2:+.4f} pt", G5)
P("-" * 100)
P(f"blocking set G2+G3+G4+G5: G2:{'PASS' if G2 else 'FAIL'}  G3:{'PASS' if G3 else 'FAIL'}  "
  f"G4:{'PASS' if G4 else 'FAIL'}  G5:{'PASS' if G5 else 'FAIL'}")
decision = ("ONDEALER01 CANDIDATE" if (G2 and G3 and G4 and G5)
            else "CLOSED AT SCOPE (S28 block) -- the overnight hour-grid is BANKED as the ES overnight structure map")
P(f"DECISION (mechanical): {decision}")
P("EVIDENCE STATUS: DISCOVERY (first read of this representation; consumed by this read).")
P(HR)

# ------------------------------------------------------------------ artifacts
pd.DataFrame(csv_rows).to_csv(os.path.join(OUT, "hour_grid.csv"), index=False)
cond_rows = [
    dict(cell="DOWN", n=n_down, mean_W_pts=m_down, effect_vs_control_pts=eff_down, p_shift_2s=p_dn,
         boot_ci_lo=eff_ci[0], boot_ci_hi=eff_ci[1],
         era1_mean=d1, era1_n=nd1, era2_mean=d2, era2_n=nd2, era1_effect=eff1, era2_effect=eff2),
    dict(cell="UP", n=n_up, mean_W_pts=m_up, effect_vs_control_pts=eff_up, p_shift_2s=p_up,
         boot_ci_lo=np.nan, boot_ci_hi=np.nan,
         era1_mean=u1, era1_n=nu1, era2_mean=u2, era2_n=nu2, era1_effect=u1 - a1, era2_effect=u2 - a2),
    dict(cell="CONTROL_ALL", n=N_e, mean_W_pts=m_all, effect_vs_control_pts=0.0, p_shift_2s=np.nan,
         boot_ci_lo=np.nan, boot_ci_hi=np.nan,
         era1_mean=a1, era1_n=na1, era2_mean=a2, era2_n=na2, era1_effect=0.0, era2_effect=0.0),
]
pd.DataFrame(cond_rows).to_csv(os.path.join(OUT, "conditional.csv"), index=False)
with open(os.path.join(OUT, "gate_table.txt"), "w", encoding="utf-8") as f:
    f.write(buf.getvalue())
print("\nWROTE out/gate_table.txt, out/hour_grid.csv, out/conditional.csv")
