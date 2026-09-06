"""XINST01 - cross-instrument P1/PCT port. Trials ES/RTY/YM/ZB.

Runs AFTER g0_validate.py has certified the bench reproduces NQ P1/PCT. Implements the
preregistered spec: percentile box transfer (STEP B), per-instrument run + eval battery +
program-printed gate table (STEP D), orthogonality vs P1 (STEP E). LEADS WITH WEEKLY-VOL.
"""
from __future__ import annotations

import os
import sys
import time as _t

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import xinst_bench as XB                                            # noqa: E402
if XB.REPO not in sys.path:
    sys.path.insert(0, XB.REPO)
from we_lab import spread_profile                                  # noqa: E402
import research_sdk.eval_battery as EB                             # noqa: E402

OUT = os.path.join(os.path.dirname(HERE), "out")
os.makedirs(OUT, exist_ok=True)
SEED = 20260906
Z_ALPHA = 2.2414027276      # one-sided, alpha = 0.0125 (Bonferroni 0.05/4)
Z_POWER = 0.8416212336      # 80% power

NQ_SUB = "runs/SM1M_SUBSTRATE/out/nq_1m_2022_2026.parquet"
INST = [
    dict(root="ES",  pv=50.0,   tick=0.25,      sub="runs/SM1M_ES_SUBSTRATE/out/es_1m_2022_2026.parquet",
         win_a="2022-07-01", spread_ticks=1, klass="equity-index"),
    dict(root="RTY", pv=50.0,   tick=0.10,      sub="runs/SM1M_RTY_SUBSTRATE/out/rty_1m_2022_2026.parquet",
         win_a="2022-07-01", spread_ticks=1, klass="equity-index"),
    dict(root="YM",  pv=5.0,    tick=1.0,       sub="runs/SM1M_YM_SUBSTRATE/out/ym_1m_2022_2026.parquet",
         win_a="2022-07-01", spread_ticks=1, klass="equity-index"),
    dict(root="ZB",  pv=1000.0, tick=1.0 / 32.0, sub="runs/SM1M_ZB_SUBSTRATE/out/zb_1m_2023_2026.parquet",
         win_a="2023-07-01", spread_ticks=1, klass="rates"),
]
WIN_B = "2026-08-01"


def moving_block_boot_p(x, L, B, rng):
    """One-sided p for mean>0 under a dependence-preserving null (moving-block bootstrap of the
    CENTERED series -> sampling distribution of the mean when the true mean is 0)."""
    x = np.asarray(x, float); n = len(x)
    m0 = x.mean()
    xc = x - m0
    nb = int(np.ceil(n / L))
    starts_pool = np.arange(0, n - L + 1)
    means = np.empty(B)
    for b in range(B):
        st = rng.choice(starts_pool, nb, replace=True)
        idx = (st[:, None] + np.arange(L)[None, :]).ravel()[:n]
        means[b] = xc[idx].mean()
    p = (1 + int(np.sum(means >= m0))) / (B + 1)
    return float(p), float(m0), means


def daily_by_date(D, session_net, sess_in):
    """P&L per calendar session-date. Sessions can share a date when a >60-min intraday data
    gap splits one trading day into two sessions, so aggregate by date (sum)."""
    sd = pd.to_datetime(D["sess_date"])[sess_in]
    return pd.Series(session_net, index=sd.date).groupby(level=0).sum()


def main():
    t0 = _t.time()
    rng = np.random.default_rng(SEED)
    log = []

    def P(*a):
        s = " ".join(str(x) for x in a)
        print(s, flush=True); log.append(s)

    prof = spread_profile()

    # ============================================================ NQ P1/PCT reference (STEP C)
    P("=" * 110)
    P("=== NQ P1/PCT reference (the STEP-C reproduction; used as weekly-vol reference and for")
    P("===   orthogonality). Its exact reproduction is certified in out/port_validation.txt.")
    P("=" * 110)
    Dnq, bnq = XB.load_substrate(NQ_SUB, "NQ")
    trnq, mnq = XB.build_p1pct(Dnq, PV=20.0, comm=4.36, halt_pts=XB.NQ_HALT_PTS,
                               tgt_pts=XB.NQ_TGT_PTS, smin_pts=None, smax_pts=None,
                               stopm_pts=None, win_a="2022-07-01", win_b=WIN_B)
    net_nq, ct_nq, rate_nq, ntr_nq = XB.net_series(
        Dnq, trnq, PV=20.0, tick=0.25, spread_model=("nq_profile", prof),
        sess_in=mnq["sess_in"], i_of=mnq["i_of"])
    w_nq, wk_nq = XB.weekly(Dnq, net_nq, mnq["sess_in"])
    pan_nq = XB.panel(w_nq)
    V_nq = XB.vol_scale(Dnq)
    P(f"  NQ P1/PCT: weekly ${pan_nq['weekly']:,.2f}  maxDD ${pan_nq['maxdd']:,.0f}  "
      f"t {pan_nq['t']:.3f}  weeks {pan_nq['nwk']}  spread ${rate_nq:.3f}/ctrRT")
    P(f"  NQ vol scale (mean|dClose|, in-session) = {V_nq:.5f} pts   [{_t.time()-t0:.0f}s]")
    nq_daily = daily_by_date(Dnq, net_nq, mnq["sess_in"])
    nq_wk_map = pd.Series(w_nq, index=wk_nq)

    # NQ box percentile reference (STEP B): where do 65 / 50 pts sit in NQ's session-range dist?
    nq_ranges = XB.session_ranges(Dnq, a="2022-07-01", b=WIN_B)
    pct_halt = XB.pctile_rank(nq_ranges, XB.NQ_HALT_PTS)
    pct_tgt = XB.pctile_rank(nq_ranges, XB.NQ_TGT_PTS)
    P(f"  NQ session point-range dist ({len(nq_ranges)} sessions): median {np.median(nq_ranges):.1f} pts")
    P(f"  TRANSFER PERCENTILES: halt 65pts -> {pct_halt:.2f}th pctile ; "
      f"target 50pts -> {pct_tgt:.2f}th pctile  (recorded BEFORE any port P&L)")

    inst_rows = []
    orth_rows = []
    gate_blocks = []

    for cfg in INST:
        root = cfg["root"]
        P("")
        P("#" * 110)
        P(f"### {root}  ({cfg['klass']})   PV={cfg['pv']}  tick={cfg['tick']:.5f}  "
          f"comm=$4.36  window {cfg['win_a']}..{WIN_B}")
        P("#" * 110)
        D, bnd = XB.load_substrate(cfg["sub"], root)
        P(f"  substrate: {bnd['n_bars']:,} bars / {bnd['n_sess']:,} sessions  "
          f"{bnd['first_sess']} -> {bnd['last_sess']}  dropped>=seal {bnd['n_dropped']}")
        P(f"  SEAL: max session {bnd['last_sess']} < 2026-08-01 ? {bnd['seal_ok']}")
        if not bnd["seal_ok"]:
            raise RuntimeError(f"SEAL VIOLATION on {root}")

        # ---- scale-invariant clamp transfer (volatility ratio) ------------------------------
        V = XB.vol_scale(D)
        ratio = V / V_nq
        smin = XB.NQ_SMIN_PTS * ratio
        smax = XB.NQ_SMAX_PTS * ratio
        stopm = XB.NQ_STOPM_PTS * ratio
        P(f"  vol scale {V:.5f} pts ; ratio to NQ {ratio:.5f}  ->  ratchet clamps (pts): "
          f"SMIN {smin:.4f}  SMAX {smax:.4f}  STOPM {stopm:.4f}")
        if root == "ZB":
            P(f"  ZB points basis: 1 pt = 32 ticks, $/tick = PV*tick = ${cfg['pv']*cfg['tick']:.4f} "
              f"(all range/box/RV math in POINTS/32nds, per DELEV01)")

        # ---- STEP B: box by percentile of THIS instrument's session-range dist --------------
        rngs = XB.session_ranges(D, a=cfg["win_a"], b=WIN_B)
        halt_pts = float(np.percentile(rngs, pct_halt))
        tgt_pts = float(np.percentile(rngs, pct_tgt))
        P(f"  session point-range dist ({len(rngs)} sess): median {np.median(rngs):.4f} pts ; "
          f"box @ percentiles -> HALT {halt_pts:.5f} pts (${halt_pts*cfg['pv']:,.0f}) / "
          f"TARGET {tgt_pts:.5f} pts (${tgt_pts*cfg['pv']:,.0f})  [recorded before P&L]")

        # ---- run the identical mechanism -----------------------------------------------------
        tr, meta = XB.build_p1pct(D, PV=cfg["pv"], comm=4.36, halt_pts=halt_pts, tgt_pts=tgt_pts,
                                  smin_pts=smin, smax_pts=smax, stopm_pts=stopm,
                                  win_a=cfg["win_a"], win_b=WIN_B)
        dv = cfg["pv"] * cfg["tick"]     # $/tick
        # primary at realistic spread (1 tick)
        net, ct, rate, ntr = XB.net_series(
            D, tr, PV=cfg["pv"], tick=cfg["tick"],
            spread_model=("flat_ticks", cfg["spread_ticks"], dv),
            sess_in=meta["sess_in"], i_of=meta["i_of"])
        w, wk = XB.weekly(D, net, meta["sess_in"])
        pan = XB.panel(w)
        n_in = len(meta["trin"])
        P(f"  ran: {ntr:,} trades ({n_in:,} in-window), {meta['n_entries']:,} entries, "
          f"size-2 {100*meta['size2_share']:.1f}% , $/tick ${dv:.4f} , spread(1tk) ${rate:.2f}/ctrRT"
          f"   [{_t.time()-t0:.0f}s]")

        # ---- G1: MDE FIRST (barrier), then observed ----------------------------------------
        sigma_w = float(np.std(w, ddof=1))
        mde = (Z_ALPHA + Z_POWER) * sigma_w / np.sqrt(len(w))
        P("")
        P(f"  G1 MDE (80% power, alpha 0.0125, weekly sd ${sigma_w:,.0f}, {len(w)} wk): "
          f"${mde:,.2f}/wk  <-- printed BEFORE the observed edge (barrier)")
        P(f"     OBSERVED native after-cost weekly net: ${pan['weekly']:,.2f}/wk "
          f"({'ABOVE' if pan['weekly'] > mde else 'BELOW'} MDE)")

        # ---- eval battery: native / weekly_vol / realized_vol / gross_exposure (vs P1) ------
        # align inst weekly with NQ P1 weekly on shared ISO weeks
        wk_s = pd.Series(w, index=wk)
        joined = pd.concat([wk_s.rename("inst"), nq_wk_map.rename("p1")], axis=1).dropna()
        res = EB.evaluate(joined["inst"].to_numpy(), joined["p1"].to_numpy(), n_placebo=0)
        wv_net = float(res["weekly_vol"])
        P("")
        P(f"  EVAL BATTERY (candidate {root} risk-matched to NQ P1/PCT, {len(joined)} shared wk):")
        for b in ("native", "weekly_vol", "realized_vol", "gross_exposure"):
            lead = "  <== PRIMARY" if b == "weekly_vol" else ""
            P(f"     {b:<16} ${res[b]:>12,.2f}/wk{lead}")

        # ---- G3: fixed-DD ONLY with its side-blind random-thinning placebo (T2 lesson) ------
        trin = meta["trin"]
        tp = np.array([x["pnl"] - rate * x["u"] for x in trin], float)   # per-trade net
        wk_of_trade = np.array([XB.pd_week_idx(x["et"]) for x in trin])
        codes, uniq = pd.factorize(pd.Index(wk_of_trade), sort=True)
        nper = len(uniq)
        nrm = max(1, int(round(0.10 * len(tp))))
        res_dd = EB.evaluate(joined["inst"].to_numpy(), joined["inst"].to_numpy(),
                             n_placebo=2000, base_for_placebo="fixed_dd",
                             ref_trades=tp, ref_periods=codes, n_trades_removed=nrm, seed=SEED)
        fixed_dd_income = float(res_dd["fixed_dd"])
        placebo_pct = res_dd.placebo_percentile
        # median placebo lift (side-blind thinning of THIS book)
        null = EB.random_thinning_placebo(tp, codes, nrm, "fixed_dd", n=2000, seed=SEED,
                                           n_periods=nper)
        base_income = tp.sum() / nper
        placebo_med = float(np.median(null))
        P("")
        P(f"  G3 fixed-DD (order statistic -> shown ONLY with placebo): self fixed-DD income "
          f"${base_income:,.2f}/wk ; side-blind 10%-thinning median ${placebo_med:,.2f}/wk "
          f"(lift {placebo_med-base_income:+,.2f})")
        placebo_ok = wv_net > 0
        P(f"     LEAD IS WEEKLY-VOL ${wv_net:,.2f}/wk. Edge survives at weekly-vol (not fixed-DD"
          f"-only)? {placebo_ok}")

        # ---- G2: Bonferroni vs dependence-preserving null ----------------------------------
        bp, m0, _ = moving_block_boot_p(w, L=4, B=20000, rng=rng)
        bonf = bp <= 0.0125
        P("")
        P(f"  G2 weekly mean ${pan['weekly']:,.2f}/wk ; analytic t {pan['t']:.3f} ; "
          f"moving-block-bootstrap (L=4, 20k) one-sided p = {bp:.5f}  "
          f"-> Bonferroni (p<=0.0125) {'PASS' if bonf else 'FAIL'}")

        # ---- G4: spread sensitivity band 0/1/2/3 ticks -------------------------------------
        band = {}
        for k in (0, 1, 2, 3):
            nk, _, rk, _ = XB.net_series(D, tr, PV=cfg["pv"], tick=cfg["tick"],
                                         spread_model=("flat_ticks", k, dv),
                                         sess_in=meta["sess_in"], i_of=meta["i_of"])
            wkk, _ = XB.weekly(D, nk, meta["sess_in"])
            wkk_s = pd.Series(wkk, index=wk)
            jj = pd.concat([wkk_s.rename("i"), nq_wk_map.rename("p")], axis=1).dropna()
            rr = EB.evaluate(jj["i"].to_numpy(), jj["p"].to_numpy(), n_placebo=0)
            band[k] = dict(native=float(wkk.mean()), wv=float(rr["weekly_vol"]), rate=rk)
        pos_through = max([k for k in (0, 1, 2, 3) if band[k]["wv"] > 0], default=-1)
        cost_robust = (f"positive weekly-vol through {pos_through}-tick"
                       if pos_through >= 1 else
                       ("0-tick only (COST-FRAGILE)" if pos_through == 0 else "negative at 0-tick"))
        P("")
        P(f"  G4 spread band (weekly-vol net $/wk):  " +
          "  ".join(f"{k}tk ${band[k]['wv']:,.0f}" for k in (0, 1, 2, 3)))
        P(f"     cost robustness: {cost_robust}")

        # ---- commission +-50% sensitivity (post-hoc: commission shifts each trade's P&L by
        #      (4.36-cm)*u; the 2nd-order box-trigger shift is negligible and ignored here) ----
        csens = {}
        for cm in (2.18, 4.36, 6.54):
            ncs = net + (4.36 - cm) * ct        # net already carries comm 4.36 + 1-tick spread
            wcs, wkcs = XB.weekly(D, ncs, meta["sess_in"])
            wcs_s = pd.Series(wcs, index=wkcs)
            jc = pd.concat([wcs_s.rename("i"), nq_wk_map.rename("p")], axis=1).dropna()
            csens[cm] = float(EB.evaluate(jc["i"].to_numpy(), jc["p"].to_numpy(),
                                          n_placebo=0)["weekly_vol"])
        P(f"  commission +-50% (weekly-vol $/wk): $2.18 ${csens[2.18]:,.0f}  "
          f"$4.36 ${csens[4.36]:,.0f}  $6.54 ${csens[6.54]:,.0f}")

        # ---- walk-forward: chronological halves --------------------------------------------
        half = len(w) // 2
        w1, w2 = w[:half], w[half:]
        def _tstat(x):
            return float(x.mean()) / max(x.std(ddof=1) / np.sqrt(len(x)), 1e-9)
        P("")
        P(f"  WALK-FORWARD (chronological halves): "
          f"H1 ${w1.mean():,.0f}/wk t {_tstat(w1):.2f} ({len(w1)}wk) | "
          f"H2 ${w2.mean():,.0f}/wk t {_tstat(w2):.2f} ({len(w2)}wk)")

        # ---- STEP E: orthogonality vs P1 ----------------------------------------------------
        inst_daily = daily_by_date(D, net, meta["sess_in"])
        jd = pd.concat([inst_daily.rename("inst"), nq_daily.rename("p1")], axis=1).dropna()
        corr_daily = float(jd["inst"].corr(jd["p1"])) if len(jd) > 2 else float("nan")
        # trade-day overlap: both traded (nonzero) same date
        both_trade = float(((jd["inst"] != 0) & (jd["p1"] != 0)).mean())
        # weekly corr + worst-decile (drawdown) overlap
        jw = pd.concat([pd.Series(w, index=wk).rename("inst"),
                        nq_wk_map.rename("p1")], axis=1).dropna()
        corr_wk = float(jw["inst"].corr(jw["p1"])) if len(jw) > 2 else float("nan")
        k = max(1, int(round(0.10 * len(jw))))
        inst_bot = set(jw["inst"].nsmallest(k).index)
        p1_bot = set(jw["p1"].nsmallest(k).index)
        dd_overlap = len(inst_bot & p1_bot) / max(len(inst_bot | p1_bot), 1)
        P("")
        P(f"  ORTHOGONALITY vs NQ P1 ({len(jd)} shared days, {len(jw)} shared wk): "
          f"daily rho {corr_daily:+.4f} ; weekly rho {corr_wk:+.4f} ; "
          f"both-traded-day share {100*both_trade:.1f}% ; worst-decile-wk overlap (Jaccard) "
          f"{dd_overlap:.3f}")

        # ---- verdict (lead with weekly-vol at the realistic 1-tick spread) ------------------
        info_supported = bool(bonf and wv_net > 0 and pos_through >= 1)
        if info_supported:
            verdict = "INFORMATION-SUPPORTED"
        elif pos_through == 0 and wv_net <= 0:
            verdict = "COST-FRAGILE"            # positive weekly-vol ONLY at 0-tick spread
        elif wv_net > 0 and not bonf:
            verdict = "CLOSED-BY-POWER"         # positive at realistic cost, underpowered
        elif pan["weekly"] <= 0 < fixed_dd_income and placebo_pct is not None and placebo_pct < 50:
            verdict = "FIXED-DD-ARTIFACT"       # edge only on the order-statistic basis
        else:
            verdict = "FAIL"                    # negative edge at realistic cost (ZB: sig. negative)
        P("")
        P(f"  ==> {root} VERDICT: {verdict}")

        # gate block for gate_table.txt
        gb = [f"{'='*100}",
              f"INSTRUMENT {root} - GATE / SPEC / OBSERVED / PASS-FAIL",
              f"{'='*100}",
              f"{'gate':<6}{'spec':<52}{'observed':>32}{'verdict':>10}",
              _grow("G0b", "max session < 2026-08-01 (seal)", bnd['last_sess'], bnd['seal_ok']),
              _grow("G1", "MDE(80%,a=.0125) printed before observed edge",
                    f"MDE ${mde:,.0f} vs obs ${pan['weekly']:,.0f}", pan['weekly'] > mde),
              _grow("G2", "weekly-vol net>0 & Bonferroni p<=0.0125 (dep null)",
                    f"wv ${wv_net:,.0f}, p {bp:.4f}", (wv_net > 0 and bonf)),
              _grow("G3", "edge at weekly-vol, not fixed-DD-only (T2)",
                    f"wv ${wv_net:,.0f} / self-DD ${base_income:,.0f}", placebo_ok),
              _grow("G4", "cost-robust: weekly-vol net>0 at >=1 tick spread",
                    cost_robust, pos_through >= 1),
              _grow("G5", "daily-PnL corr vs P1 printed", f"rho {corr_daily:+.3f}", True),
              f"G6  SEMANTIC: over {len(jw)} ISO weeks in {cfg['win_a']}..{WIN_B} on {root} 1-min",
              f"    (pre-seal, DISCOVERY_CONSUMED, in-sample), the after-cost weekly-vol-matched",
              f"    net (levered to NQ P1's weekly volatility) is ${wv_net:,.2f}/wk; the number is",
              f"    the mean weekly P&L of the ported P1/PCT mechanism, NOT a forward or live figure.",
              f"    ==> VERDICT {verdict}"]
        gate_blocks.append("\n".join(gb))

        inst_rows.append(dict(
            root=root, klass=cfg["klass"], pv=cfg["pv"], tick=cfg["tick"],
            win_a=cfg["win_a"], nwk=len(w), ntrades=ntr, ntrades_inwin=n_in,
            entries=meta["n_entries"], size2_share=meta["size2_share"],
            pct_halt=pct_halt, pct_tgt=pct_tgt, halt_pts=halt_pts, tgt_pts=tgt_pts,
            halt_usd=halt_pts * cfg["pv"], tgt_usd=tgt_pts * cfg["pv"],
            vol_scale=V, vol_ratio=ratio, smin=smin, smax=smax, stopm=stopm,
            spread_rate_1tk=rate, dollar_per_tick=dv,
            native_wk=pan["weekly"], weekly_vol_wk=wv_net,
            realized_vol_wk=float(res["realized_vol"]), gross_exp_wk=float(res["gross_exposure"]),
            fixed_dd_self=base_income, placebo_med=placebo_med, placebo_pct=placebo_pct,
            maxdd=pan["maxdd"], top5=pan["top5"], worst=pan["worst"], poswk=pan["poswk"],
            t_analytic=pan["t"], boot_p=bp, mde=mde,
            band0=band[0]["wv"], band1=band[1]["wv"], band2=band[2]["wv"], band3=band[3]["wv"],
            cost_robust=cost_robust, pos_through=pos_through,
            comm_lo=csens[2.18], comm_hi=csens[6.54],
            wf_h1=float(w1.mean()), wf_h1_t=_tstat(w1), wf_h2=float(w2.mean()), wf_h2_t=_tstat(w2),
            corr_daily=corr_daily, corr_wk=corr_wk, both_trade_share=both_trade,
            dd_overlap=dd_overlap, verdict=verdict))
        orth_rows.append(dict(root=root, shared_days=len(jd), shared_wk=len(jw),
                              corr_daily=corr_daily, corr_weekly=corr_wk,
                              both_traded_day_share=both_trade,
                              worst_decile_wk_overlap_jaccard=dd_overlap,
                              inst_weekly_vol=wv_net, verdict=verdict))

    # ============================================================ write deliverables
    pd.DataFrame(inst_rows).to_csv(os.path.join(OUT, "per_instrument.csv"), index=False)
    pd.DataFrame(orth_rows).to_csv(os.path.join(OUT, "orthogonality.csv"), index=False)
    with open(os.path.join(OUT, "gate_table.txt"), "w", encoding="utf-8") as f:
        f.write(f"XINST01 GATE TABLE - program-printed. NQ P1/PCT reproduced EXACTLY "
                f"(port_validation.txt).\nTransfer percentiles: halt {pct_halt:.2f}th / "
                f"target {pct_tgt:.2f}th of session point-range.\n\n")
        f.write("\n\n".join(gate_blocks) + "\n")
    with open(os.path.join(OUT, "run_log.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(log) + "\n")
    P("")
    P(f"[done {_t.time()-t0:.0f}s]  wrote per_instrument.csv, orthogonality.csv, gate_table.txt")


def _grow(g, spec, obs, ok):
    return f"{g:<6}{spec:<52}{str(obs)[:31]:>32}{('PASS' if ok else 'FAIL'):>10}"


# small helper referenced in main (week index for a trade timestamp)
def _pd_week_idx(ts):
    p = pd.Timestamp(ts)
    iso = p.isocalendar()
    return f"{iso[0]}-W{iso[1]:02d}"


XB.pd_week_idx = _pd_week_idx


if __name__ == "__main__":
    main()
