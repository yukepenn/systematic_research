"""W5 A1 — Robust sizing FRONTIER for R5-E10 v2 (Program A; ledger-only).

Frozen spec: research/scalping_lab/specs/W5_programs_wave.md §A1.

Inputs : runs/E10MASTER_V2/out/daily_v1_v2.csv  (sess, net_v1, net_v2)
         daily P&L per 1-NQ-equivalent (engine traded +/-10 MNQ = 1 NQ).
         PRIMARY ledger = net_v2 (Flatten1644, live-operations default).
         net_v1 (frozen research champion) run as full sensitivity grid.
Contamination rule: minute-history dev window ends 2026-05-31 — the ledger is
TRUNCATED there on load; no row dated 2026-06-01 or later enters any statistic.

Method:
  * Stationary block bootstrap (Politis-Romano): mean block 10 days
    (geometric block-length distribution, restart prob p = 1/10, circular
    wrap), 2000 paths, path length = ledger length, seed 20260808.
  * Kelly machinery: mu = mean daily P&L per 1 NQ, sigma = std (ddof=1).
    Full-Kelly capital equivalent K = sigma^2 / mu  (the wealth at which
    holding exactly 1 NQ is full Kelly: n* = W*mu/sigma^2 = 1  =>  W = K).
    K is estimated ONCE from the empirical (unstressed) primary ledger and
    held fixed across scenarios: the operator sizes on the edge they
    BELIEVE (empirical), the scenarios vary the edge they GET.
  * Continuous-c idealization (scale-free): W_{t+1} = W_t * (1 + c*PnL_t/K).
  * MNQ-granular: contracts_t = max(round(10 * c * W_t / K), 0) MNQ
    (1 NQ = 10 MNQ; the spec's  c*W*mu/sigma^2 / (0.1*NQ_notional)  form with
    return-per-notional Kelly reduces algebraically to exactly this — the
    notional proxy cancels), wealth W_{t+1} = W_t + (contracts_t/10)*PnL_t,
    W0 in {25k, 50k, 100k}; W<=0 is ruin (contracts 0 thereafter).
  * Scenarios (each run over the full c grid): empirical; mu*0.75; mu*0.5
    (additive shift, variance unchanged); top-5 profit days removed; and
    BOTH combined variants (top-5 removed + 0.75 / + 0.5 haircut of the
    post-removal mean).
  * Reported per (scenario, c): annualized geometric growth (median across
    paths), median terminal wealth multiple, P(maxDD > 20/30/40%), time
    under water (median fraction of days below running peak, median longest
    underwater spell), and for granular runs P(ruin).

No NT8 / no orders / local python only.  Seed 20260808.
"""
from __future__ import annotations

import io
import os
import sys
from contextlib import redirect_stdout

import numpy as np
import pandas as pd

# ---------------------------------------------------------------- constants
ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
LEDGER_CSV = os.path.join(ROOT, "runs", "E10MASTER_V2", "out", "daily_v1_v2.csv")
ART_DIR = os.path.join(ROOT, "research", "scalping_lab", "artifacts", "w5_a1")

SEED = 20260808
N_PATHS = 2000
MEAN_BLOCK = 10.0          # stationary bootstrap mean block length (days)
RESTART_P = 1.0 / MEAN_BLOCK
C_GRID = [0.15, 0.25, 0.35, 0.5, 0.75, 1.0]
W0_GRID = [25_000.0, 50_000.0, 100_000.0]
DD_LEVELS = [0.20, 0.30, 0.40]
ANN_DAYS = 252
DEV_END = "2026-05-31"     # contamination ledger: sealed holdout starts 2026-06-01
EXTERNAL_K_ESTIMATE = 85_000.0
SAFE_DD_LEVEL = 0.40
SAFE_DD_PROB = 0.05


# ---------------------------------------------------------------- bootstrap
def stationary_bootstrap_indices(rng: np.random.Generator, n_obs: int,
                                 n_paths: int, path_len: int) -> np.ndarray:
    """Politis-Romano stationary bootstrap index matrix (n_paths x path_len).

    Geometric block lengths (restart prob RESTART_P), uniform random block
    starts, circular wrap modulo n_obs.
    """
    starts = rng.integers(0, n_obs, size=(n_paths, path_len))
    restart = rng.random(size=(n_paths, path_len)) < RESTART_P
    idx = np.empty((n_paths, path_len), dtype=np.int64)
    idx[:, 0] = starts[:, 0]
    for t in range(1, path_len):
        cont = (idx[:, t - 1] + 1) % n_obs
        idx[:, t] = np.where(restart[:, t], starts[:, t], cont)
    return idx


# ---------------------------------------------------------------- metrics
def _underwater_stats(uw: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Per-path (fraction of days underwater, longest underwater spell)."""
    n_paths, n_t = uw.shape
    frac = uw.mean(axis=1)
    t_arr = np.broadcast_to(np.arange(n_t), (n_paths, n_t))
    last_dry = np.maximum.accumulate(np.where(~uw, t_arr, -1), axis=1)
    spell = (t_arr - last_dry) * uw
    return frac, spell.max(axis=1)


def continuous_metrics(pnl_mat: np.ndarray, c: float, K: float) -> dict:
    """Scale-free multiplicative sim: W_{t+1} = W_t * (1 + c*PnL_t/K)."""
    r = c * pnl_mat / K
    ruined = (r <= -1.0).any(axis=1)
    # guard log1p; ruined paths are forced to worst-case metrics below
    logw = np.cumsum(np.log1p(np.clip(r, -0.999999, None)), axis=1)
    w = np.exp(logw)
    runmax = np.maximum.accumulate(np.maximum(w, 1.0), axis=1)  # peak incl. W0=1
    dd = 1.0 - w / runmax
    maxdd = dd.max(axis=1)
    maxdd[ruined] = 1.0
    n_t = pnl_mat.shape[1]
    term_mult = np.where(ruined, 0.0, np.exp(logw[:, -1]))
    ann_growth = np.where(ruined, -1.0,
                          np.expm1(logw[:, -1] * ANN_DAYS / n_t))
    uw_frac, uw_spell = _underwater_stats(dd > 1e-12)
    return dict(
        ann_geo_growth_med=float(np.median(ann_growth)),
        term_mult_med=float(np.median(term_mult)),
        p_dd20=float((maxdd > DD_LEVELS[0]).mean()),
        p_dd30=float((maxdd > DD_LEVELS[1]).mean()),
        p_dd40=float((maxdd > DD_LEVELS[2]).mean()),
        tuw_frac_med=float(np.median(uw_frac)),
        uw_spell_days_med=float(np.median(uw_spell)),
        p_ruin=float(ruined.mean()),
    )


def mnq_granular_metrics(pnl_mat: np.ndarray, c: float, K: float,
                         w0: float) -> dict:
    """Integer-MNQ sim: contracts_t = max(round(10*c*W_t/K), 0)."""
    n_paths, n_t = pnl_mat.shape
    w = np.full(n_paths, w0)
    ruined = np.zeros(n_paths, dtype=bool)
    runmax = np.full(n_paths, w0)
    maxdd = np.zeros(n_paths)
    uw_days = np.zeros(n_paths, dtype=np.int64)
    spell_cur = np.zeros(n_paths, dtype=np.int64)
    spell_max = np.zeros(n_paths, dtype=np.int64)
    ever_zero_contracts = np.zeros(n_paths, dtype=bool)
    for t in range(n_t):
        contracts = np.floor(10.0 * c * w / K + 0.5)
        contracts = np.where(ruined, 0.0, np.maximum(contracts, 0.0))
        ever_zero_contracts |= (contracts == 0.0) & ~ruined
        w = w + (contracts / 10.0) * pnl_mat[:, t]
        newly_ruined = (w <= 0.0) & ~ruined
        ruined |= newly_ruined
        w = np.where(ruined, 0.0, w)
        runmax = np.maximum(runmax, w)
        dd = 1.0 - w / runmax
        maxdd = np.maximum(maxdd, dd)
        uw = dd > 1e-12
        uw_days += uw
        spell_cur = np.where(uw, spell_cur + 1, 0)
        spell_max = np.maximum(spell_max, spell_cur)
    maxdd[ruined] = 1.0
    term_mult = w / w0
    with np.errstate(divide="ignore"):
        ann_growth = np.where(
            ruined, -1.0, np.expm1(np.log(np.maximum(term_mult, 1e-300))
                                   * ANN_DAYS / n_t))
    return dict(
        ann_geo_growth_med=float(np.median(ann_growth)),
        term_mult_med=float(np.median(term_mult)),
        p_dd20=float((maxdd > DD_LEVELS[0]).mean()),
        p_dd30=float((maxdd > DD_LEVELS[1]).mean()),
        p_dd40=float((maxdd > DD_LEVELS[2]).mean()),
        tuw_frac_med=float(np.median(uw_days / n_t)),
        uw_spell_days_med=float(np.median(spell_max)),
        p_ruin=float(ruined.mean()),
        p_ever_zero_contracts=float(ever_zero_contracts.mean()),
    )


# ---------------------------------------------------------------- scenarios
def build_scenarios(pnl: np.ndarray) -> dict[str, np.ndarray]:
    """Six stressed daily-P&L series per spec (haircuts are additive shifts:
    variance unchanged; combined haircuts are relative to the post-removal
    mean of the top-5-removed series)."""
    mu = pnl.mean()
    top5 = np.argsort(pnl)[-5:]
    tail = np.delete(pnl, top5)
    mu_tail = tail.mean()
    return {
        "empirical": pnl.copy(),
        "haircut_mu075": pnl - 0.25 * mu,
        "haircut_mu050": pnl - 0.50 * mu,
        "top5_removed": tail.copy(),
        "combined_top5_mu075": tail - 0.25 * mu_tail,
        "combined_top5_mu050": tail - 0.50 * mu_tail,
    }


# ---------------------------------------------------------------- driver
def run_ledger(name: str, pnl: np.ndarray, dates: pd.DatetimeIndex,
               K_fixed: float, rng: np.random.Generator):
    """Full frontier for one ledger. Returns (cont_rows, mnq_rows, meta)."""
    scenarios = build_scenarios(pnl)
    mu, sigma = pnl.mean(), pnl.std(ddof=1)
    top5_idx = np.argsort(pnl)[-5:]
    top5_tbl = sorted(
        [(str(dates[i].date()), float(pnl[i])) for i in top5_idx],
        key=lambda x: -x[1])
    mu_se = sigma / np.sqrt(len(pnl))
    meta = dict(ledger=name, n_days=len(pnl), first=str(dates[0].date()),
                last=str(dates[-1].date()), mu=mu, sigma=sigma,
                mu_se=mu_se, mu_t_stat=mu / mu_se,
                K_own=sigma * sigma / mu, K_used=K_fixed,
                sharpe_ann=mu / sigma * np.sqrt(ANN_DAYS),
                worst_day=float(pnl.min()), best_day=float(pnl.max()),
                top5_days=top5_tbl)
    cont_rows, mnq_rows = [], []
    for scen, series in scenarios.items():
        n_obs = len(series)
        idx = stationary_bootstrap_indices(rng, n_obs, N_PATHS, n_obs)
        pnl_mat = series[idx]
        scen_stats = dict(scen_mu=float(series.mean()),
                          scen_sigma=float(series.std(ddof=1)),
                          scen_n_days=n_obs)
        for c in C_GRID:
            m = continuous_metrics(pnl_mat, c, K_fixed)
            cont_rows.append(dict(ledger=name, scenario=scen, c=c,
                                  **scen_stats, **m))
            for w0 in W0_GRID:
                g = mnq_granular_metrics(pnl_mat, c, K_fixed, w0)
                mnq_rows.append(dict(ledger=name, scenario=scen, c=c,
                                     W0=int(w0), **scen_stats, **g))
    return cont_rows, mnq_rows, meta


def fmt_pct(x: float) -> str:
    return f"{100.0 * x:.1f}%"


def main() -> None:
    os.makedirs(ART_DIR, exist_ok=True)
    df = pd.read_csv(LEDGER_CSV, parse_dates=["sess"])
    n_raw = len(df)
    df = df[df["sess"] <= pd.Timestamp(DEV_END)].reset_index(drop=True)
    n_dev = len(df)
    print("=" * 78)
    print("W5 A1 — Robust sizing FRONTIER for R5-E10 v2 (seed %d)" % SEED)
    print("=" * 78)
    print(f"Ledger file: {LEDGER_CSV}")
    print(f"Rows in file: {n_raw}; rows after contamination truncation at "
          f"{DEV_END}: {n_dev} (sealed holdout 2026-06-01+ excluded)")
    dates = pd.DatetimeIndex(df["sess"])
    pnl_v2 = df["net_v2"].to_numpy(float)
    pnl_v1 = df["net_v1"].to_numpy(float)

    # Kelly capital from the PRIMARY empirical ledger (v2, live default)
    mu2, sd2 = pnl_v2.mean(), pnl_v2.std(ddof=1)
    K2 = sd2 * sd2 / mu2
    mu1, sd1 = pnl_v1.mean(), pnl_v1.std(ddof=1)
    K1 = sd1 * sd1 / mu1
    print("\n--- Kelly machinery (empirical, dev window) -------------------")
    print(f"v2 (PRIMARY, Flatten1644 live default): mu = ${mu2:,.2f}/day, "
          f"sigma = ${sd2:,.2f}/day, ann Sharpe = {mu2/sd2*np.sqrt(252):.3f}")
    print(f"v2 mu standard error = ${sd2/np.sqrt(len(pnl_v2)):,.2f}/day "
          f"(mu/se = {mu2/(sd2/np.sqrt(len(pnl_v2))):.2f}) — the edge "
          f"estimate itself is uncertain; this is why the haircut scenarios "
          f"are load-bearing")
    print(f"v2 full-Kelly capital K = sigma^2/mu = ${K2:,.0f}  "
          f"(1 NQ is full Kelly at this wealth)")
    print(f"v1 (frozen research champion, sensitivity): mu = ${mu1:,.2f}, "
          f"sigma = ${sd1:,.2f}, K = ${K1:,.0f}")
    print(f"External sanity estimate: ~${EXTERNAL_K_ESTIMATE:,.0f}; "
          f"v2 K / external = {K2/EXTERNAL_K_ESTIMATE:.2f}")

    rng = np.random.default_rng(SEED)
    cont_all, mnq_all, metas = [], [], []
    for name, series, K_fixed in [("v2", pnl_v2, K2), ("v1", pnl_v1, K1)]:
        c_rows, m_rows, meta = run_ledger(name, series, dates, K_fixed, rng)
        cont_all += c_rows
        mnq_all += m_rows
        metas.append(meta)
        print(f"\nledger {name}: n={meta['n_days']} days "
              f"[{meta['first']} .. {meta['last']}], worst day "
              f"${meta['worst_day']:,.0f}, top-5 profit days removed in tail "
              f"scenarios: {meta['top5_days']}")

    cont = pd.DataFrame(cont_all)
    mnq = pd.DataFrame(mnq_all)
    cont.to_csv(os.path.join(ART_DIR, "w5a1_frontier_continuous.csv"),
                index=False)
    mnq.to_csv(os.path.join(ART_DIR, "w5a1_frontier_mnq_granular.csv"),
               index=False)
    kelly = pd.DataFrame([{k: v for k, v in m.items() if k != "top5_days"}
                          for m in metas])
    kelly["external_estimate"] = EXTERNAL_K_ESTIMATE
    kelly.to_csv(os.path.join(ART_DIR, "w5a1_kelly_capital.csv"), index=False)

    # ---------------- frontier printout (primary ledger, continuous) ------
    print("\n--- FRONTIER (v2 primary, continuous-c idealization) ----------")
    print(f"{'scenario':<22}{'c':>6}{'geoAnn':>9}{'medTW':>8}"
          f"{'P(DD>20)':>10}{'P(DD>30)':>10}{'P(DD>40)':>10}"
          f"{'TUW':>7}{'maxUW_d':>9}")
    v2c = cont[cont.ledger == "v2"]
    for _, r in v2c.iterrows():
        print(f"{r['scenario']:<22}{r['c']:>6.2f}"
              f"{fmt_pct(r['ann_geo_growth_med']):>9}"
              f"{r['term_mult_med']:>8.2f}"
              f"{fmt_pct(r['p_dd20']):>10}{fmt_pct(r['p_dd30']):>10}"
              f"{fmt_pct(r['p_dd40']):>10}{fmt_pct(r['tuw_frac_med']):>7}"
              f"{r['uw_spell_days_med']:>9.0f}")

    # ---------------- safe-c determination --------------------------------
    print("\n--- Safe-c: P(maxDD > 40%) < 5% in EVERY scenario -------------")
    safe_rows = []
    for ledger_name, frame, label in [
            ("v2", cont, "continuous"),
            ("v1", cont, "continuous")]:
        sub = frame[frame.ledger == ledger_name]
        worst = sub.groupby("c")["p_dd40"].max()
        safe = worst[worst < SAFE_DD_PROB].index.tolist()
        safe_rows.append(dict(ledger=ledger_name, mode=label, W0="n/a",
                              safe_c=safe,
                              worst_p_dd40_by_c=worst.round(4).to_dict()))
        print(f"{ledger_name} {label:<11}: worst-scenario P(DD>40) by c = "
              f"{ {k: round(v,4) for k,v in worst.items()} }")
        print(f"    -> safe c set: {safe if safe else 'EMPTY'}")
    for ledger_name in ["v2", "v1"]:
        for w0 in W0_GRID:
            sub = mnq[(mnq.ledger == ledger_name) & (mnq.W0 == int(w0))]
            worst = sub.groupby("c")["p_dd40"].max()
            safe = worst[worst < SAFE_DD_PROB].index.tolist()
            safe_rows.append(dict(ledger=ledger_name, mode="mnq_granular",
                                  W0=int(w0), safe_c=safe,
                                  worst_p_dd40_by_c=worst.round(4).to_dict()))
            print(f"{ledger_name} MNQ W0=${w0/1000:.0f}k: worst P(DD>40) by "
                  f"c = { {k: round(v,4) for k,v in worst.items()} }")
            print(f"    -> safe c set: {safe if safe else 'EMPTY'}")
    pd.DataFrame(safe_rows).to_csv(
        os.path.join(ART_DIR, "w5a1_safe_c_sets.csv"), index=False)

    print("\nEXPLICIT: sizing creates NO alpha — it only rescales a fixed "
          "daily edge and its risk; every c on this frontier trades growth "
          "against drawdown, and no single c is 'the answer'.")
    print("Artifacts written to", ART_DIR)


if __name__ == "__main__":
    buf = io.StringIO()
    with redirect_stdout(buf):
        main()
    text = buf.getvalue()
    sys.stdout.write(text)
    with open(os.path.join(ART_DIR, "w5a1_stdout.txt"), "w",
              encoding="utf-8") as fh:
        fh.write(text)
