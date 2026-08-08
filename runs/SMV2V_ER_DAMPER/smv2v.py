"""SMV2V_ER_DAMPER -- seq 393 (policy cells), 394 (placebo + chronology).
Frozen spec: runs/SMV2V_ER_DAMPER/spec.yaml.

Hypothesis (SMV2R sub_385 JOB B, ER150_top|HTF row): ER150-top-tercile agreement
days are followed by LOWER next-session Solar/E10 PnL (-$206/sd, t_NW=-3.27,
HTF-controlled). This run tests a ONE-SHOT bounded policy: on session t+1 after
an ER150 "agreement day" t, scale the SOLAR leg of the champion daily curve by
s in {0.65, 0.75, 0.85}; BMOM leg untouched; recombine to the champion basis.

State construction -- REUSED from SMV2R sub385 where the spec says to reuse it
(the ER150 formula and the tercile digitize machinery), FRESHLY BUILT where the
spec explicitly requires something sub385 did not do:
  - ER150[t] = |close[t]-close[t-150]| / max(sum_{t-149..t}|diff|, 1e-9), on the
    3-minute bar series, bar-index based (session-boundary agnostic), IDENTICAL
    formula to sub385_majobs.py. (REUSED, verbatim.)
  - tercile classification: np.digitize(er, [q33, q67]) -> 0/1/2, top tercile =
    index 2. (REUSED, verbatim digitize logic.) sub385 computed q33/q67 ONCE
    over the FULL fixed dev sample (in-sample, non-causal). This spec instead
    requires "expanding top tercile ranks, >=12mo burn-in" -- an EXPLICIT,
    spec-directed change from sub385's fixed-sample tercile to a causal
    expanding-sample tercile (recomputed at each session's close bar from ALL
    bar-level ER150 values observed through that bar). This is not a silent
    deviation: the spec text itself overrides sub385's fixed-tercile choice.
  - "agreement day": sub385's agree_fn for ER150 was membership in the top
    tercile ALONE (no sign check). This spec's hypothesis text explicitly adds
    a second, new condition: "sign of (close_t - close_{t-150 bars}) equals
    sign of ensemble position at session close". This combined AND condition
    is NEW (not in sub385 at all -- sub385 never checked ER sign-agreement,
    only MA states did that). Built fresh per the spec's literal wording.
  - "ensemble position at session close": SM01/SM06 substrate's vote_pos (raw
    member vote sum, -13..13) is used as "the ensemble position" per spec's
    "vote states from the SM01 substrate" data line (distinct from sub385's
    cache_incumbent-derived bar_pos, which used a specific incumbent's
    rounded/clamped E10 target execution). By construction (see
    sm01_solarsim.member_trades: every member is flattened AT the session's
    last bar, so pos[t]=0 for all members at last_of_sess), vote_pos is
    IDENTICALLY 0 at every literal last-of-session bar -- "position at session
    close" cannot mean the literal final print (it is degenerate/always flat).
    OPERATIONAL CHOICE (documented, not silent): "position at session close"
    = vote_pos at the bar immediately BEFORE the session's last bar (the last
    non-flattened reading, i.e. what was actually held into the close print
    before being closed out). "close_t" and ER150[t] themselves are unaffected
    by the flatten mechanic (pure price data) and are evaluated at the
    session's literal last bar as usual.
  - Undefined ER (bar index < 150) or degenerate sign (price_dir==0 or
    pos_dir==0, i.e. flat position or unchanged price) => NOT an agreement day
    (there is no directional claim to agree on). This differs from sub385's
    "undefined MA state = AGREE (no gating)" convention -- for ER, "undefined"
    cannot sensibly default to agreement since ER agreement is a top-tercile
    MEMBERSHIP test, not a sign-match-only test; a flat/undefined bar simply
    fails membership. Documented, not silent.

Policy: scaled[u] = agree[u-1] (single-day window, session t+1 only; no
multi-day window, so SMV2N's "retrigger extends the window" union logic does
not apply here -- consecutive trigger days each independently flag their own
immediate next day). Recombine: policy_twin = s*leg_solar (on scaled days,
else leg_solar) + leg_bmom (untouched every day).

Gates -- identical battery to SMV2N (runs/SMV2N_WINDFALL_POLICY/smv2n.py):
  1: CDaR_0.95 AND TUW improve (strictly lower) vs unscaled champion twin.
  2: both improvements > placebo median + 2*IQR (200 seeds 1..200, same
     scaled-day COUNT, non-overlapping with each other and with the real
     scaled days, drawn from the burn-in-eligible region). Single-day windows
     (unlike SMV2N's multi-day contiguous runs) so placement is a simple
     without-replacement draw of day-indices, no run-length matching needed.
  3: LOYO >=4/5 (years 2022..2026, dSharpe sign) + leave-2022-out keeps sign.
  4: RTC >= 0.97 on champion (unscaled twin) top-decile days (k=ceil(0.10*n)).
  5: net retention (policy net / unscaled net) >= 0.97.
  6: old-regime (SM06 substrate, 2006-2021) same-direction check: build the
     IDENTICAL agreement-flag construction (own expanding tercile, own 12mo
     burn-in from 2006-01-05) on the E10-only curve (e10_daily_hist.csv, the
     same object class as SM01's e10_daily_py.csv -- pure SOLAR/E10 ensemble
     PnL, matching what the ORIGINAL sub385 JOB B hypothesis coefficient was
     computed on) and require the sign of the agreement -> next-session E10
     PnL relationship not to REVERSE relative to the dev-side sign (computed
     the same way, on e10_daily_py.csv). Flat (~0) acceptable; only a clearly
     POSITIVE old-regime coefficient (reversal of the dev's established
     negative relationship) fails.

House bootstrap (supplementary, non-gating context only): moving block
bootstrap of the policy-vs-unscaled daily net delta, block=5, n_boot=10000,
seed=20260808 -- this is sm_metrics.block_bootstrap_delta's exact default
signature; used here for one extra confidence read per cell, reported in
REPORT.md, NOT a gate.

HARD: no data >= 2026-08-01 is ever used for policy/dev objects; dev sessions
<= 2026-05-31 only for all gates 1-5 and the dev-side sign in gate 6. Gate 6's
old-regime substrate (2006-2021) is a separate, already-frozen historical
object (SM06_SOLAR_HISTORY), used for structure/sign confirmation only, never
for tuning.
"""
import os
import sys

import numpy as np
import pandas as pd

REPO = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
RUN = os.path.join(REPO, "runs", "SMV2V_ER_DAMPER")
OUT = os.path.join(RUN, "out")
os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, os.path.join(REPO, "src", "analytics"))
from smv2_common import dd_battery  # noqa: E402
from sm_metrics import block_bootstrap_delta  # noqa: E402

DEV_END = pd.Timestamp("2026-05-31")
CELLS = [0.65, 0.75, 0.85]
CENTER = 0.75
N_PLACEBO = 200
BURN_DAYS = 365
ER_WIN = 150
HOUSE_SEED = 20260808
HOUSE_BLOCK = 5
HOUSE_NBOOT = 10000


def sgn(v):
    return 0 if v == 0 else (1 if v > 0 else -1)


def cdar95(net):
    """dd_battery 'CDaR5'-exact (SMV2N-identical light implementation, used in the
    hot placebo/gate loops -- dd_battery itself is reserved for the one-shot
    STEP 0 repro check to avoid its resample() overhead on 600+ calls)."""
    dd = dd_of(net)
    ddpos = np.sort(dd[dd > 0])[::-1]
    k = max(1, int(0.05 * len(dd)))
    return float(ddpos[:k].mean()) if len(ddpos) else 0.0


def tuw_longest(net):
    """dd_battery 'longest_TUW_days'-exact."""
    dd = dd_of(net)
    uw = dd > 1e-9
    tuw = cur = 0
    for u in uw:
        cur = cur + 1 if u else 0
        tuw = max(tuw, cur)
    return int(tuw)


def sharpe(net):
    net = np.asarray(net, dtype=float)
    sd = net.std(ddof=1)
    return float(net.mean() / sd * np.sqrt(252)) if sd > 0 else np.nan


def dd_of(net):
    eq = np.cumsum(np.asarray(net, dtype=float))
    return np.maximum.accumulate(eq) - eq


# ================================================================== STEP 0
# repro gate: leg curves reconcile to the champion twin, and the champion
# twin dev battery reproduces runs/SMV2M_MASTER_BUILD/out/twin_battery.csv

leg = pd.read_csv(os.path.join(REPO, "runs", "SMV2Q_DIAGNOSTICS", "out", "leg_daily.csv"),
                  index_col=0, parse_dates=True)
assert leg.index.max() <= DEV_END, "VIRGIN guard: leg curve extends past dev cutoff"
cal = leg.index
n = len(cal)
leg_solar = leg["leg_solar"].to_numpy()
leg_bmom = leg["leg_bmom"].to_numpy()
twin = leg["twin"].to_numpy()
recon_err = float(np.max(np.abs((leg_solar + leg_bmom) - twin)))

tb = pd.read_csv(os.path.join(REPO, "runs", "SMV2M_MASTER_BUILD", "out", "twin_battery.csv")
                 ).set_index("label").loc["MASTER_TWIN_dev"]
b_twin = dd_battery(cal, twin, label="twin_dev_repro")
repro = {
    "leg_recon_max_abs_err": recon_err,
    "n_days_expected": int(tb["n_days"]), "n_days_got": n,
    "net_expected": float(tb["net"]), "net_got": float(twin.sum()),
    "sharpe_expected": float(tb["sharpe"]), "sharpe_got": b_twin["sharpe"],
    "cdar95_expected": float(tb["CDaR5"]), "cdar95_got": b_twin["CDaR5"],
    "tuw_expected": int(tb["longest_TUW_days"]), "tuw_got": b_twin["longest_TUW_days"],
    "maxdd_expected": float(tb["maxDD_eod"]), "maxdd_got": b_twin["maxDD_eod"],
}
repro["pass"] = bool(
    repro["leg_recon_max_abs_err"] <= 1e-6
    and repro["n_days_expected"] == repro["n_days_got"]
    and abs(repro["net_expected"] - repro["net_got"]) <= 1e-6
    and abs(repro["sharpe_expected"] - repro["sharpe_got"]) <= 1e-9
    and abs(repro["cdar95_expected"] - repro["cdar95_got"]) <= 1e-6
    and repro["tuw_expected"] == repro["tuw_got"]
    and abs(repro["maxdd_expected"] - repro["maxdd_got"]) <= 1e-6)
pd.DataFrame([repro]).to_csv(os.path.join(OUT, "repro_check.csv"), index=False)
print("REPRO:", repro, flush=True)
if not repro["pass"]:
    print("REPRO FAILED -- BLOCKED", flush=True)
    sys.exit(2)


# ================================================================== state builder

def build_agree_table(vote_parquet_path, dev_end, first_date_floor=None):
    """Per-session agreement table from a vote_state_3m-style substrate parquet.
    Returns DataFrame indexed by session date with columns:
      close_t, er_t, st_er (-1/0/1/2), pos_close, price_dir, pos_dir,
      burn_ok, agree (bool).
    ER150 formula and digitize tercile logic verbatim from SMV2R sub385_majobs.py
    (agree_fn / STATES['ER150']); tercile population is EXPANDING (bar-level,
    from bar ER_WIN through the evaluation bar, inclusive) per this spec's
    explicit override of sub385's fixed-sample tercile.
    """
    v = pd.read_parquet(vote_parquet_path)
    v["sess_date"] = pd.to_datetime(v["sess_date"])
    if dev_end is not None:
        v = v[v["sess_date"] <= dev_end].reset_index(drop=True)
    else:
        v = v.reset_index(drop=True)
    close = v["close"].to_numpy()
    vote_pos = v["vote_pos"].to_numpy()
    sess_date = v["sess_date"].to_numpy()
    m = len(v)

    dabs = np.abs(np.diff(close, prepend=close[0]))
    dabs[0] = 0
    csum = np.cumsum(dabs)
    er = np.full(m, np.nan)
    er[ER_WIN:] = np.abs(close[ER_WIN:] - close[:-ER_WIN]) / np.maximum(
        csum[ER_WIN:] - csum[:-ER_WIN], 1e-9)

    # "session close" bar = the LAST bar of each CALENDAR sess_date (not the raw
    # is_last_of_sess flag, which is per sess_id and NOT 1:1 with calendar dates
    # in the pre-2012 old-regime substrate: early closes are keyed on >=17:00
    # gaps -- sm01_solarsim.resample_3m docstring -- which can split one calendar
    # date across >1 sess_id, each carrying its own is_last_of_sess bar. Grouping
    # by calendar sess_date and taking the chronologically-last bar coalesces any
    # such split and matches exactly how e10_daily_py.csv / e10_daily_hist.csv
    # aggregate daily net (keyed by sess_date, sm01_solarsim.e10_sim). Verified
    # a no-op vs is_last_of_sess on the modern (SM01, 2022-2026) substrate.
    idx_df = pd.DataFrame({"sess_date": sess_date, "idx": np.arange(m)})
    last_by_date = idx_df.groupby("sess_date")["idx"].max().sort_index()
    last_idx = last_by_date.to_numpy()
    n_sess = len(last_idx)
    sess_dates_u = pd.to_datetime(last_by_date.index.to_numpy())

    st_er = np.full(n_sess, -1, dtype=int)
    q33_a = np.full(n_sess, np.nan)
    q67_a = np.full(n_sess, np.nan)
    for i, t in enumerate(last_idx):
        if t < ER_WIN:
            continue
        pool = er[ER_WIN:t + 1]
        q33, q67 = np.percentile(pool, [100.0 / 3.0, 200.0 / 3.0])
        q33_a[i] = q33
        q67_a[i] = q67
        e_t = er[t]
        st_er[i] = 2 if e_t >= q67 else (0 if e_t < q33 else 1)

    prev_idx = np.clip(last_idx - 1, 0, None)
    pos_close = np.where(last_idx > 0, vote_pos[prev_idx], 0)
    close_t = close[last_idx]
    have_lag = last_idx >= ER_WIN
    lag_idx = np.clip(last_idx - ER_WIN, 0, None)
    close_t150 = np.where(have_lag, close[lag_idx], np.nan)

    tab = pd.DataFrame({
        "sess": sess_dates_u,
        "close_t": close_t,
        "close_t150": close_t150,
        "er_t": er[last_idx],
        "q33": q33_a, "q67": q67_a,
        "st_er": st_er,
        "pos_close": pos_close,
    })
    tab["price_dir"] = np.sign(tab["close_t"] - tab["close_t150"]).fillna(0).astype(int)
    tab["pos_dir"] = np.sign(tab["pos_close"]).astype(int)
    floor_date = first_date_floor if first_date_floor is not None else tab["sess"].iloc[0]
    tab["burn_ok"] = (tab["sess"] - floor_date).dt.days >= BURN_DAYS
    tab["agree"] = (tab["burn_ok"] & (tab["st_er"] == 2)
                    & (tab["price_dir"] != 0) & (tab["pos_dir"] != 0)
                    & (tab["price_dir"] == tab["pos_dir"]))
    return tab.set_index("sess")


print("building dev state table (SM01 substrate)...", flush=True)
dev_tab = build_agree_table(
    os.path.join(REPO, "runs", "SM01_SUBSTRATE", "out", "vote_state_3m.parquet"), DEV_END)

assert list(dev_tab.index) == list(cal), "session calendar mismatch: SM01 substrate vs SMV2Q leg curve"

dev_tab.reset_index().to_csv(os.path.join(OUT, "state_dev.csv"), index=False)
n_agree = int(dev_tab["agree"].sum())
n_burn_ok = int(dev_tab["burn_ok"].sum())
print(f"dev sessions={len(dev_tab)} burn_ok={n_burn_ok} agree_days={n_agree}", flush=True)

# scaled[u] = agree at session u-1 (single-day window, session t+1 only)
agree_arr = dev_tab["agree"].to_numpy()
scaled = np.zeros(n, dtype=bool)
scaled[1:] = agree_arr[:-1]
n_scaled = int(scaled.sum())
first_burn_idx = int(np.where(dev_tab["burn_ok"].to_numpy())[0][0]) if n_burn_ok else n
lo = first_burn_idx + 1  # earliest index a real/placebo scaled day can occupy
print(f"n_scaled_days={n_scaled} lo={lo}", flush=True)


# ================================================================== policy cells

cdar_un = cdar95(twin)
tuw_un = tuw_longest(twin)
sh_un = sharpe(twin)
net_un = float(twin.sum())
k_dec = int(np.ceil(0.10 * n))
top_idx = np.argsort(twin)[::-1][:k_dec]
top_min = float(twin[top_idx].min())
assert (twin[top_idx] > 0).all(), "champion top-decile day contains a non-positive (non-up) day"

daily = pd.DataFrame({"sess": cal, "leg_solar": leg_solar, "leg_bmom": leg_bmom,
                      "twin_unscaled": twin, "scaled": scaled})
cell_curves = {}
house_boot = {}
for s in CELLS:
    scale_vec = np.where(scaled, s, 1.0)
    pol_solar = leg_solar * scale_vec
    pol_twin = pol_solar + leg_bmom
    cell_curves[s] = pol_twin
    daily[f"twin_s{s:.2f}"] = pol_twin
    hb = block_bootstrap_delta(pol_twin, twin, block=HOUSE_BLOCK, n_boot=HOUSE_NBOOT, seed=HOUSE_SEED)
    house_boot[s] = hb
daily.to_csv(os.path.join(OUT, "policy_daily.csv"), index=False)


# ================================================================== placebo battery (seq 394a)

occupied_base = scaled.copy()
feasible_pool = np.array([i for i in range(lo, n) if not occupied_base[i]])
pl_rows = []
for seed in range(1, N_PLACEBO + 1):
    rng = np.random.default_rng(seed)
    ok = len(feasible_pool) >= n_scaled
    mask = np.zeros(n, dtype=bool)
    if ok and n_scaled > 0:
        idx = rng.choice(feasible_pool, size=n_scaled, replace=False)
        mask[idx] = True
    row = {"seed": seed, "feasible": ok, "n_scaled_days": n_scaled}
    for s in CELLS:
        if ok:
            pl_solar = leg_solar * np.where(mask, s, 1.0)
            pl_twin = pl_solar + leg_bmom
            row[f"dcdar_s{s:.2f}"] = cdar_un - cdar95(pl_twin)
            row[f"dtuw_s{s:.2f}"] = tuw_un - tuw_longest(pl_twin)
        else:
            row[f"dcdar_s{s:.2f}"] = np.nan
            row[f"dtuw_s{s:.2f}"] = np.nan
    pl_rows.append(row)
plc = pd.DataFrame(pl_rows)
plc.to_csv(os.path.join(OUT, "placebo.csv"), index=False)
n_feas = int(plc["feasible"].sum())
print(f"placebo: feasible={n_feas}/{N_PLACEBO}", flush=True)


# ================================================================== chronology (seq 394b)

years = np.array([d.year for d in cal])
yr_list = sorted(set(years.tolist()))
chron_rows = []
loyo_gate = {}
for s in CELLS:
    pol = cell_curves[s]
    dsh_full = sharpe(pol) - sh_un
    sign_full = sgn(dsh_full)
    chron_rows.append({"s": s, "scope": "full", "sharpe_unscaled": sh_un,
                       "sharpe_policy": sharpe(pol), "dsharpe": dsh_full,
                       "sign": sign_full, "n_days": n})
    agree_cnt = 0
    sign_loyo_2022 = None
    for y in yr_list:
        m = years != y
        dsh = sharpe(pol[m]) - sharpe(twin[m])
        chron_rows.append({"s": s, "scope": f"loyo_{y}", "sharpe_unscaled": sharpe(twin[m]),
                           "sharpe_policy": sharpe(pol[m]), "dsharpe": dsh,
                           "sign": sgn(dsh), "n_days": int(m.sum())})
        if sgn(dsh) == sign_full:
            agree_cnt += 1
        if y == 2022:
            sign_loyo_2022 = sgn(dsh)
    for y in yr_list:
        m = years == y
        dsh = sharpe(pol[m]) - sharpe(twin[m])
        chron_rows.append({"s": s, "scope": f"year_{y}", "sharpe_unscaled": sharpe(twin[m]),
                           "sharpe_policy": sharpe(pol[m]), "dsharpe": dsh,
                           "sign": sgn(dsh), "n_days": int(m.sum())})
    loyo_gate[s] = {"agree": agree_cnt, "n_years": len(yr_list),
                    "loyo2022_keeps_sign": bool(sign_loyo_2022 == sign_full),
                    "pass": bool(agree_cnt >= 4 and sign_loyo_2022 == sign_full)}
pd.DataFrame(chron_rows).to_csv(os.path.join(OUT, "chronology.csv"), index=False)


# ================================================================== gate 6: old-regime sign check

print("building old-regime state table (SM06 substrate, 2006-2021)...", flush=True)
hist_tab = build_agree_table(
    os.path.join(REPO, "runs", "SM06_SOLAR_HISTORY", "out", "vote_state_3m_hist.parquet"), None)
hist_e10 = pd.read_csv(os.path.join(REPO, "runs", "SM06_SOLAR_HISTORY", "out", "e10_daily_hist.csv"))
hist_e10["sess"] = pd.to_datetime(hist_e10["sess"])
assert list(hist_tab.index) == list(hist_e10["sess"]), "session calendar mismatch: SM06 substrate vs e10_daily_hist"
hist_tab.reset_index().to_csv(os.path.join(OUT, "state_oldregime.csv"), index=False)

dev_e10 = pd.read_csv(os.path.join(REPO, "runs", "SM01_SUBSTRATE", "out", "e10_daily_py.csv"))
dev_e10["sess"] = pd.to_datetime(dev_e10["sess"])
dev_e10 = dev_e10[dev_e10["sess"] <= DEV_END].reset_index(drop=True)
assert list(dev_e10["sess"]) == list(cal), "session calendar mismatch: e10_daily_py vs leg curve"


def nw_ols_dummy(y, dummy, lag=5):
    """y ~ const + beta*dummy ; Newey-West t on beta. X columns: [1, dummy]."""
    X = np.column_stack([np.ones(len(y)), dummy.astype(float)])
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    u = y - X @ beta
    XtX_inv = np.linalg.inv(X.T @ X)
    Xu = X * u[:, None]
    S = Xu.T @ Xu
    for L in range(1, lag + 1):
        w = 1 - L / (lag + 1)
        G = Xu[:-L].T @ Xu[L:]
        S += w * (G + G.T)
    V = XtX_inv @ S @ XtX_inv
    t = beta / np.sqrt(np.maximum(np.diag(V), 1e-300))
    return float(beta[1]), float(t[1])


def relationship_sign(agree_bool_series, e10_daily_df, burn_ok_series):
    d = e10_daily_df.set_index("sess")["net"]
    df = pd.DataFrame({"agree": agree_bool_series, "burn_ok": burn_ok_series})
    df["next_net"] = d.reindex(df.index).shift(-1)
    df = df[df["burn_ok"]].dropna()
    beta, t = nw_ols_dummy(df["next_net"].to_numpy(), df["agree"].to_numpy(), lag=5)
    mean_agree = float(df.loc[df["agree"], "next_net"].mean()) if df["agree"].any() else np.nan
    mean_nonagree = float(df.loc[~df["agree"], "next_net"].mean()) if (~df["agree"]).any() else np.nan
    return {"n_days": len(df), "n_agree": int(df["agree"].sum()),
            "coef_beta": beta, "t_NW": t, "sign": sgn(beta),
            "mean_next_net_agree": mean_agree, "mean_next_net_nonagree": mean_nonagree}


dev_rel = relationship_sign(dev_tab["agree"], dev_e10, dev_tab["burn_ok"])
hist_rel = relationship_sign(hist_tab["agree"], hist_e10, hist_tab["burn_ok"])
gate6_reversed = bool(dev_rel["sign"] != 0 and hist_rel["sign"] == -dev_rel["sign"])
gate6_pass = not gate6_reversed
oldregime_row = {
    "dev_n_days": dev_rel["n_days"], "dev_n_agree": dev_rel["n_agree"],
    "dev_coef_beta": dev_rel["coef_beta"], "dev_t_NW": dev_rel["t_NW"], "dev_sign": dev_rel["sign"],
    "dev_mean_next_net_agree": dev_rel["mean_next_net_agree"],
    "dev_mean_next_net_nonagree": dev_rel["mean_next_net_nonagree"],
    "oldregime_n_days": hist_rel["n_days"], "oldregime_n_agree": hist_rel["n_agree"],
    "oldregime_coef_beta": hist_rel["coef_beta"], "oldregime_t_NW": hist_rel["t_NW"],
    "oldregime_sign": hist_rel["sign"],
    "oldregime_mean_next_net_agree": hist_rel["mean_next_net_agree"],
    "oldregime_mean_next_net_nonagree": hist_rel["mean_next_net_nonagree"],
    "reversed": gate6_reversed, "gate6_pass": gate6_pass,
}
pd.DataFrame([oldregime_row]).to_csv(os.path.join(OUT, "oldregime.csv"), index=False)
print("GATE6:", oldregime_row, flush=True)


# ================================================================== cells.csv + gate roll-up

cells_rows = []
for s in CELLS:
    pol = cell_curves[s]
    cd = cdar95(pol)
    tu = tuw_longest(pol)
    net_p = float(pol.sum())
    dcdar = cdar_un - cd
    dtuw = tuw_un - tu
    rtc = float(pol[top_idx].sum() / twin[top_idx].sum())
    ret = net_p / net_un

    pc = plc[plc["feasible"]]
    med_c = float(pc[f"dcdar_s{s:.2f}"].median())
    iqr_c = float(pc[f"dcdar_s{s:.2f}"].quantile(0.75) - pc[f"dcdar_s{s:.2f}"].quantile(0.25))
    med_t = float(pc[f"dtuw_s{s:.2f}"].median())
    iqr_t = float(pc[f"dtuw_s{s:.2f}"].quantile(0.75) - pc[f"dtuw_s{s:.2f}"].quantile(0.25))
    thr_c = med_c + 2.0 * iqr_c
    thr_t = med_t + 2.0 * iqr_t

    g1_c = bool(cd < cdar_un)
    g1_t = bool(tu < tuw_un)
    g2_c = bool(dcdar > thr_c)
    g2_t = bool(dtuw > thr_t)
    g3 = loyo_gate[s]["pass"]
    g4 = bool(rtc >= 0.97)
    g5 = bool(ret >= 0.97)
    g6 = gate6_pass  # gate 6 is not cell-specific (state/relationship construction is shared)
    hb = house_boot[s]
    cells_rows.append({
        "s": s, "n_days": n, "n_scaled_days": n_scaled,
        "net_unscaled": net_un, "net_policy": net_p, "net_retention": ret,
        "cdar95_unscaled": cdar_un, "cdar95_policy": cd, "dcdar": dcdar,
        "tuw_unscaled": tuw_un, "tuw_policy": tu, "dtuw": dtuw,
        "maxdd_unscaled": float(dd_of(twin).max()), "maxdd_policy": float(dd_of(pol).max()),
        "sharpe_unscaled": sh_un, "sharpe_policy": sharpe(pol), "dsharpe_full": sharpe(pol) - sh_un,
        "rtc": rtc, "rtc_k_days": k_dec, "rtc_topdecile_min_pnl": top_min,
        "placebo_n_feasible": n_feas,
        "placebo_dcdar_median": med_c, "placebo_dcdar_iqr": iqr_c, "placebo_dcdar_thresh": thr_c,
        "placebo_dtuw_median": med_t, "placebo_dtuw_iqr": iqr_t, "placebo_dtuw_thresh": thr_t,
        "loyo_agree_count": loyo_gate[s]["agree"], "loyo_n_years": loyo_gate[s]["n_years"],
        "loyo2022_keeps_sign": loyo_gate[s]["loyo2022_keeps_sign"],
        "gate1_cdar_improve": g1_c, "gate1_tuw_improve": g1_t,
        "gate2_cdar_gt_placebo": g2_c, "gate2_tuw_gt_placebo": g2_t,
        "gate3_loyo": g3, "gate4_rtc": g4, "gate5_retention": g5, "gate6_oldregime": g6,
        "all_gates_pass": bool(g1_c and g1_t and g2_c and g2_t and g3 and g4 and g5 and g6),
        "house_boot_delta_mean": hb["delta"], "house_boot_p_leq_0": hb["p_leq_0"],
        "house_boot_ci_lo": hb["ci_lo"], "house_boot_ci_hi": hb["ci_hi"],
    })
cells = pd.DataFrame(cells_rows)
cells.to_csv(os.path.join(OUT, "cells.csv"), index=False)

center = cells[cells["s"] == CENTER].iloc[0]
verdict = "SURVIVES" if center["all_gates_pass"] else "KILLED"
print(cells.T.to_string())
print("\nVERDICT (center s=0.75):", verdict)
print("ALL-CELLS pass:", cells["all_gates_pass"].tolist())
