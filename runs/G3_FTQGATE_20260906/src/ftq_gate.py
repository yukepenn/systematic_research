"""G3_FTQGATE_20260906 -- corr-regime-gated flight-to-quality (ledger G00076, GENESIS3_EVENT).

Spec: runs/G3_FTQGATE_20260906/spec.yaml. FROZEN OBJECT (echoed verbatim as constants below):
  * EVENT day d: ES daily point-return <= -1.5 x trailing-60-session sigma (sigma causal,
    excludes day d: shift(1); min_valid 50/60, the family precedent from G3_EVENT_GC E2).
  * REGIME at d (causal, lagged one day): sign of the trailing-60-session ES-ZB daily
    point-return correlation computed over the window ENDING AT d-1 (data through d-1 only).
    NEG = corr < 0, POS = corr > 0 (corr == 0.0 exactly -> excluded, count printed).
  * 2x2: {event} x {NEG, POS} -> ZB forward close-to-close POINT returns at horizons
    h in {1, 3, 5} = {next day, days +1..+3, +1..+5}, computed on the merged ES-ZB session
    axis (inner join by date; ~99% of sessions shared).
  * SINGLE PRIMARY (the CLAIM): at h=3, NEG-cell mean minus NEG-regime UNCONDITIONAL control
    (all eligible days in the regime, the matched-control law) > 0, AND the interaction
    (NEG delta minus POS delta) > 0.  h=1 and h=5 are printed as secondary/descriptive.
  * NULL 1 (p): circular shift of the EVENT FLAG over the merged day axis, ONE SHARED offset
    draw per iteration across the whole family, min shift 30, 2000 draws; regime series and
    outcomes held fixed -> event clustering preserved exactly. One-sided p (claim directional).
  * NULL 2 (CI, "event-clustered block bootstrap"): circular block bootstrap of the merged day
    axis with block length 60 sessions (chosen to SPAN 2008-style event clusters; measured
    cluster spans printed and compared), 2000 draws, (event, regime, fwd-outcome) tuples move
    together inside a block; percentile 95% CI of each delta and of the interaction; also a
    bootstrap p = fraction of draws with statistic <= 0 (the SECOND, independent computation
    of every headline p).
  * GATES G1..G5 per spec; decision rule mechanical: G2+G3 PASS -> TAIL-ENGINE CANDIDATE;
    either fails -> closed at scope (SS28). DISCOVERY evidence status.

DELEV01: everything in POINTS (self-financing per-contract ret_points; never % on any
back-adjusted level). SEAL asserted < 2026-08-01 on both inputs.
"""
from __future__ import annotations

import json
import os

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.dirname(HERE)
OUT = os.path.join(RUN, "out")
SEAL = pd.Timestamp("2026-08-01")
RNG = np.random.default_rng(20260906)

# ---- preregistered constants (echo of spec.yaml; printed in the gate-table footer) ----
EVENT_Z = -1.5
SIG_WIN, SIG_MIN = 60, 50
CORR_WIN, CORR_MIN = 60, 50           # regime corr window; min valid pairs (same 50/60 tolerance)
HORIZONS = [1, 3, 5]
H_PRIMARY = 3
N_SHIFT, MIN_SHIFT = 2000, 30
N_BB, L_BLOCK = 2000, 60
CLUSTER_GAP = 5                       # event days <= 5 sessions apart form one cluster (reporting)
ZB_PV, ZB_TICK_PTS = 1000.0, 0.03125  # $/point, tick in points -> $31.25/tick
COMMISSION = 4.36
COST_1T = COMMISSION + 1 * ZB_TICK_PTS * ZB_PV      # 35.61
COST_2T = COMMISSION + 2 * ZB_TICK_PTS * ZB_PV      # 66.86

_fh = open(os.path.join(OUT, "gate_table.txt"), "w", encoding="utf-8")


def P(*a):
    print(*a, flush=True)
    print(*a, file=_fh)


def fwd_sum(r, h):
    """sum of r[i+1..i+h]; NaN if any component NaN or out of range."""
    s = pd.Series(r)
    out = s.shift(-1).rolling(h, min_periods=h).sum().shift(-(h - 1))
    return out.values


def main():
    # ================================================================ LOAD + SEAL
    es = pd.read_parquet(os.path.join(OUT, "es_daily.parquet"))
    zb = pd.read_parquet(os.path.join(OUT, "zb_daily.parquet"))
    assert es["date"].max() < SEAL, "SEAL VIOLATION (ES)"
    assert zb["date"].max() < SEAL, "SEAL VIOLATION (ZB)"
    manifest = json.load(open(os.path.join(OUT, "inputs_manifest.json"), encoding="utf-8"))

    j = pd.merge(es[["date", "ret_points", "close", "clean_daily"]],
                 zb[["date", "ret_points", "clean_daily"]],
                 on="date", suffixes=("_es", "_zb")).sort_values("date").reset_index(drop=True)
    n = len(j)
    dates = j["date"]
    r_es = j["ret_points_es"].where(j["clean_daily_es"]).values      # POINTS, gap-nulled
    r_zb = j["ret_points_zb"].where(j["clean_daily_zb"]).values      # POINTS, gap-nulled

    # ================================================================ EVENT (causal sigma)
    sig60 = pd.Series(r_es).shift(1).rolling(SIG_WIN, min_periods=SIG_MIN).std().values
    z_es = r_es / sig60
    event = (z_es <= EVENT_Z) & np.isfinite(z_es)

    # ================================================================ REGIME (corr through d-1)
    x, y = r_es.copy(), r_zb.copy()
    valid = np.isfinite(x) & np.isfinite(y)
    xv = np.where(valid, x, 0.0)
    yv = np.where(valid, y, 0.0)

    def rsum(a, w):
        return pd.Series(a).rolling(w, min_periods=1).sum().values

    cnt = rsum(valid.astype(float), CORR_WIN)
    sx, sy = rsum(xv, CORR_WIN), rsum(yv, CORR_WIN)
    sxx, syy = rsum(xv * xv, CORR_WIN), rsum(yv * yv, CORR_WIN)
    sxy = rsum(xv * yv, CORR_WIN)
    with np.errstate(invalid="ignore", divide="ignore"):
        cov = sxy / cnt - (sx / cnt) * (sy / cnt)
        vx = sxx / cnt - (sx / cnt) ** 2
        vy = syy / cnt - (sy / cnt) ** 2
        corr_now = cov / np.sqrt(vx * vy)
    corr_now = np.where(cnt >= CORR_MIN, corr_now, np.nan)
    corr_lag = pd.Series(corr_now).shift(1).values                   # data through d-1 ONLY
    reg_neg = corr_lag < 0
    reg_pos = corr_lag > 0
    n_zero = int(np.sum(corr_lag == 0.0))

    # ---- independent regime-lag verification (recompute at sample days from truncated data)
    idx_candidates = np.where(np.isfinite(corr_lag))[0]
    samp = RNG.choice(idx_candidates, size=min(25, len(idx_candidates)), replace=False)
    lag_err = 0.0
    for i in samp:
        w0 = max(0, i - CORR_WIN)
        xs, ys = x[w0:i], y[w0:i]                                    # rows strictly BEFORE day i
        m = np.isfinite(xs) & np.isfinite(ys)
        if m.sum() >= CORR_MIN:
            c = float(np.corrcoef(xs[m], ys[m])[0, 1])
            lag_err = max(lag_err, abs(c - corr_lag[i]))
    lag_ok = lag_err < 1e-9

    # ================================================================ OUTCOMES + ELIGIBILITY
    FWD = {h: fwd_sum(r_zb, h) for h in HORIZONS}
    regime_defined = reg_neg | reg_pos
    event_defined = np.isfinite(z_es)
    ELIG = {h: regime_defined & event_defined & np.isfinite(FWD[h]) for h in HORIZONS}

    # ================================================================ CLUSTERS (reporting)
    ev_idx = np.where(event)[0]
    clusters = []
    if len(ev_idx):
        start = prev = ev_idx[0]
        for i in ev_idx[1:]:
            if i - prev <= CLUSTER_GAP:
                prev = i
            else:
                clusters.append((start, prev))
                start = prev = i
        clusters.append((start, prev))
    spans = np.array([b - a + 1 for a, b in clusters]) if clusters else np.array([1])
    p95_span = float(np.percentile(spans, 95))
    max_span = int(spans.max())

    # ================================================================ HEADER + MDE (FIRST)
    P("=" * 118)
    P("=== G3_FTQGATE_20260906 -- corr-regime-gated flight-to-quality (G00076, GENESIS3_EVENT)")
    P("=" * 118)
    P(f"merged ES-ZB axis: {n:,} sessions {dates.min().date()} -> {dates.max().date()}   "
      f"(ES {manifest['es']['rows']:,} d, ZB {manifest['zb']['rows']:,} d, both identity-gated "
      f"causal roll)")
    P(f"event: ES ret_pts <= {EVENT_Z} x trailing-{SIG_WIN} sigma (causal)   "
      f"events = {int(event.sum())}   (spec expectation ~150-250)")
    P(f"regime: sign of trailing-{CORR_WIN} ES-ZB corr THROUGH d-1   "
      f"NEG days = {int(reg_neg.sum()):,}   POS days = {int(reg_pos.sum()):,}   "
      f"undefined = {int((~regime_defined).sum()):,}   corr==0 exactly: {n_zero}")
    ev_neg_n = int((event & reg_neg).sum())
    ev_pos_n = int((event & reg_pos).sum())
    P(f"event split: NEG-regime {ev_neg_n}   POS-regime {ev_pos_n}   "
      f"(events outside defined regime: {int((event & ~regime_defined).sum())})")
    P(f"event clusters (gap <= {CLUSTER_GAP} sessions): {len(clusters)} clusters, "
      f"span P95 {p95_span:.0f} max {max_span} sessions; block length {L_BLOCK} "
      f"{'SPANS' if L_BLOCK >= max_span else '*** DOES NOT SPAN ***'} the widest cluster")
    P("")
    P("G1 -- MDE TABLE (printed BEFORE any observed cell mean; 80% power, alpha .05 two-sided)")
    P(f"{'regime':<8}{'h':>3}{'n_event':>9}{'n_days':>8}{'n_clust':>9}{'sd_fwd(pts)':>13}"
      f"{'MDE(pts)':>10}{'MDE_clust(pts)':>15}")
    n_clust_reg = {"NEG": len([1 for a, b in clusters if reg_neg[a]]),
                   "POS": len([1 for a, b in clusters if reg_pos[a]])}
    for regname, regmask in (("NEG", reg_neg), ("POS", reg_pos)):
        for h in HORIZONS:
            el = ELIG[h] & regmask
            nev = int((el & event).sum())
            nd = int(el.sum())
            sd = float(np.nanstd(FWD[h][el])) if nd else np.nan
            nc = max(1, n_clust_reg[regname])
            mde = 2.80 * sd * np.sqrt(1 / max(nev, 1) + 1 / max(nd, 1))
            mde_c = 2.80 * sd * np.sqrt(1 / nc + 1 / max(nd, 1))
            P(f"{regname:<8}{h:>3}{nev:>9}{nd:>8}{nc:>9}{sd:>13.3f}{mde:>10.3f}{mde_c:>15.3f}")
    P("")

    # ================================================================ STATISTICS
    def stats_for(ev_mask):
        """(neg_delta, pos_delta, interaction, cell means...) per horizon for a given event mask.
        Controls (own-regime unconditional means) are FIXED from the observed eligibility."""
        out = {}
        for h in HORIZONS:
            f = FWD[h]
            elN, elP = ELIG[h] & reg_neg, ELIG[h] & reg_pos
            uncN = float(np.nanmean(f[elN]))
            uncP = float(np.nanmean(f[elP]))
            mN = f[elN & ev_mask]
            mP = f[elP & ev_mask]
            nN, nP = int(np.isfinite(mN).sum()), int(np.isfinite(mP).sum())
            cN = float(np.nanmean(mN)) if nN else np.nan
            cP = float(np.nanmean(mP)) if nP else np.nan
            dN, dP = cN - uncN, cP - uncP
            out[h] = dict(cell_neg=cN, cell_pos=cP, unc_neg=uncN, unc_pos=uncP,
                          n_neg=nN, n_pos=nP, d_neg=dN, d_pos=dP, inter=dN - dP)
        return out

    obs = stats_for(event)

    # non-event means (transparency; control law uses UNCONDITIONAL)
    nonev = {}
    for h in HORIZONS:
        f = FWD[h]
        nonev[h] = (float(np.nanmean(f[ELIG[h] & reg_neg & ~event])),
                    float(np.nanmean(f[ELIG[h] & reg_pos & ~event])))

    # ---------------- NULL 1: shared-draw circular shift of the event flag
    u = RNG.random(N_SHIFT)
    offsets = (MIN_SHIFT + np.floor(u * (n - 2 * MIN_SHIFT))).astype(int)
    keys = [(h, k) for h in HORIZONS for k in ("d_neg", "d_pos", "inter")]
    null_shift = {k: np.full(N_SHIFT, np.nan) for k in keys}
    pos0 = np.where(event)[0]
    for it in range(N_SHIFT):
        sh = np.zeros(n, dtype=bool)
        sh[(pos0 + offsets[it]) % n] = True
        st = stats_for(sh)
        for h in HORIZONS:
            for k in ("d_neg", "d_pos", "inter"):
                null_shift[(h, k)][it] = st[h][k]

    def p_shift(h, k):
        d = null_shift[(h, k)]
        d = d[np.isfinite(d)]
        o = obs[h][k]
        return float((np.sum(d >= o) + 1) / (len(d) + 1))            # one-sided, claim positive

    # ---------------- NULL 2: event-clustered circular block bootstrap (CI + second p)
    nb = int(np.ceil(n / L_BLOCK)) + 1
    ub = RNG.random((N_BB, nb))
    starts = np.floor(ub * n).astype(int)
    bidx = (starts[:, :, None] + np.arange(L_BLOCK)[None, None, :]) % n
    bidx = bidx.reshape(N_BB, -1)[:, :n]                             # (N_BB, n) resampled days
    boot = {k: np.full(N_BB, np.nan) for k in keys}
    for it in range(N_BB):
        ix = bidx[it]
        ev_b, rn_b, rp_b = event[ix], reg_neg[ix], reg_pos[ix]
        for h in HORIZONS:
            f_b = FWD[h][ix]
            el_b = np.isfinite(f_b) & np.isfinite(z_es[ix]) & (rn_b | rp_b)
            elN, elP = el_b & rn_b, el_b & rp_b
            mN, mP = f_b[elN & ev_b], f_b[elP & ev_b]
            if not len(mN) or not len(mP):
                continue
            dN = float(np.nanmean(mN)) - float(np.nanmean(f_b[elN]))
            dP = float(np.nanmean(mP)) - float(np.nanmean(f_b[elP]))
            boot[(h, "d_neg")][it], boot[(h, "d_pos")][it] = dN, dP
            boot[(h, "inter")][it] = dN - dP

    def ci(h, k):
        d = boot[(h, k)]
        d = d[np.isfinite(d)]
        return (float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5)),
                float((np.sum(d <= 0) + 1) / (len(d) + 1)), len(d))

    # ================================================================ 2x2 TABLE
    P("2x2 TABLE  (ZB forward close-to-close POINT sums; delta = event-cell mean minus "
      "OWN-REGIME UNCONDITIONAL control)")
    hdr = (f"{'h':>3} {'regime':<7}{'n_ev':>6}{'cell(pts)':>11}{'uncond(pts)':>12}"
           f"{'nonev(pts)':>11}{'delta(pts)':>11}{'CI95_lo':>9}{'CI95_hi':>9}"
           f"{'p_shift':>9}{'p_boot':>8}")
    P(hdr)
    rows_csv = []
    for h in HORIZONS:
        o = obs[h]
        for regname in ("NEG", "POS"):
            k = "d_neg" if regname == "NEG" else "d_pos"
            lo, hi, pbb, nbd = ci(h, k)
            cell = o["cell_neg"] if regname == "NEG" else o["cell_pos"]
            unc = o["unc_neg"] if regname == "NEG" else o["unc_pos"]
            nev = o["n_neg"] if regname == "NEG" else o["n_pos"]
            ne = nonev[h][0] if regname == "NEG" else nonev[h][1]
            ps = p_shift(h, k)
            tag = " <- PRIMARY" if (h == H_PRIMARY and regname == "NEG") else ""
            P(f"{h:>3} {regname:<7}{nev:>6}{cell:>11.4f}{unc:>12.4f}{ne:>11.4f}"
              f"{o[k]:>11.4f}{lo:>9.4f}{hi:>9.4f}{ps:>9.4f}{pbb:>8.4f}{tag}")
            rows_csv.append(dict(horizon=h, regime=regname, n_event=nev, cell_mean_pts=cell,
                                 uncond_ctrl_pts=unc, nonevent_mean_pts=ne, delta_pts=o[k],
                                 ci95_lo=lo, ci95_hi=hi, p_shift=ps, p_boot=pbb,
                                 n_boot_valid=nbd, primary=(h == H_PRIMARY and regname == "NEG")))
        lo, hi, pbb, nbd = ci(h, "inter")
        ps = p_shift(h, "inter")
        tag = " <- PRIMARY" if h == H_PRIMARY else ""
        P(f"{h:>3} {'INTER':<7}{'':>6}{'':>11}{'':>12}{'':>11}{o['inter']:>11.4f}"
          f"{lo:>9.4f}{hi:>9.4f}{ps:>9.4f}{pbb:>8.4f}{tag}")
        rows_csv.append(dict(horizon=h, regime="INTERACTION", n_event=ev_neg_n + ev_pos_n,
                             cell_mean_pts=np.nan, uncond_ctrl_pts=np.nan,
                             nonevent_mean_pts=np.nan, delta_pts=o["inter"], ci95_lo=lo,
                             ci95_hi=hi, p_shift=ps, p_boot=pbb, n_boot_valid=nbd,
                             primary=(h == H_PRIMARY)))
    P("")

    # ---------------- POS-cell honesty: year composition + 2022 sub-cell
    yr = dates.dt.year.values
    P("G4 HONESTY -- regime composition by year (share of defined-regime days that are POS) and "
      "POS-cell events:")
    for yy in range(2009, 2027):
        m = (yr == yy) & regime_defined
        if m.sum() == 0:
            continue
        pos_share = float(reg_pos[m].mean())
        nev_p = int((event & reg_pos & (yr == yy)).sum())
        nev_n = int((event & reg_neg & (yr == yy)).sum())
        P(f"    {yy}: POS share {pos_share:5.1%}   events NEG/POS {nev_n:>3}/{nev_p:>3}")
    m22 = event & reg_pos & (yr == 2022) & ELIG[H_PRIMARY]
    f3 = FWD[H_PRIMARY]
    P(f"    2022 POS-cell (decisive modern cell), h={H_PRIMARY}: n={int(m22.sum())}, "
      f"mean {float(np.nanmean(f3[m22])) if m22.sum() else float('nan'):+.4f} pts "
      f"vs 2022 POS uncond "
      f"{float(np.nanmean(f3[reg_pos & (yr == 2022) & ELIG[H_PRIMARY]])):+.4f} pts")
    o3 = obs[H_PRIMARY]
    loP, hiP, pbbP, _ = ci(H_PRIMARY, "d_pos")
    pos_pays = (o3["d_pos"] > 0) and (loP > 0)
    P(f"    POS-cell 'also pays' reclassify check (h={H_PRIMARY}): delta {o3['d_pos']:+.4f}, "
      f"CI [{loP:+.4f}, {hiP:+.4f}] -> {'PAYS (reclassify to unconditional FTQ)' if pos_pays else 'does not pay'}")
    P("")

    # ---------------- G5 cost (trivial at 1-5d; printed anyway)
    dneg_usd = o3["d_neg"] * ZB_PV
    P(f"G5 COST -- ZB tick $31.25, commission ${COMMISSION}/ctRT: 1-tick ${COST_1T:.2f} | "
      f"2-tick ${COST_2T:.2f} per round trip")
    P(f"    NEG-cell h={H_PRIMARY} delta = {o3['d_neg']:+.4f} pts x ${ZB_PV:.0f}/pt = "
      f"${dneg_usd:+,.2f} per contract per event -> cost coverage "
      f"{abs(dneg_usd) / COST_2T:.1f}x conservative" )
    P("")

    # ================================================================ GATES
    loI, hiI, pbbI, nbdI = ci(H_PRIMARY, "inter")
    loN, hiN, pbbN, nbdN = ci(H_PRIMARY, "d_neg")
    psI, psN = p_shift(H_PRIMARY, "inter"), p_shift(H_PRIMARY, "d_neg")
    g1 = True                                                        # MDE printed above, first
    g2 = (o3["inter"] > 0) and (loI > 0)
    g3 = (o3["d_neg"] > 0) and (loN > 0)
    g4 = True                                                        # POS cell + control printed
    g5 = True                                                        # cost band printed
    seal_ok = (es["date"].max() < SEAL) and (zb["date"].max() < SEAL)
    id_ok = (manifest["es"]["identity_gate_maxerr"] < 1e-9
             and manifest["zb"]["identity_gate_maxerr"] < 1e-9)
    roll_ok = bool(manifest["es"]["roll_causal"]) and bool(manifest["zb"]["roll_causal"])

    gates = [
        ("G0a_SEAL", "max ES and ZB session < 2026-08-01",
         f"ES {es['date'].max().date()}, ZB {zb['date'].max().date()}", seal_ok),
        ("G0b_IDENTITY", "ret_points == roll.economic_returns, err < 1e-9 (both roots)",
         f"ES {manifest['es']['identity_gate_maxerr']:.1e}, "
         f"ZB {manifest['zb']['identity_gate_maxerr']:.1e}", id_ok),
        ("G0c_ROLL_CAUSAL", "every roll info_cutoff < decision_date (both roots)",
         f"ES {manifest['es']['roll_causal']}, ZB {manifest['zb']['roll_causal']}", roll_ok),
        ("G0d_REGIME_LAG", "regime at d == corr recomputed from data STRICTLY before d "
         f"(independent check, {len(samp)} sample days)", f"max err {lag_err:.1e}", lag_ok),
        ("G0e_POINTS_ONLY", "all math in points on per-contract self-financing returns (DELEV01)",
         "no % column formed anywhere", True),
        ("G1_MDE_first", "MDE table printed BEFORE observed cells; ~150-250 events expected",
         f"printed first; {int(event.sum())} events (NEG {ev_neg_n} / POS {ev_pos_n})", g1),
        ("G2_interaction", f"h={H_PRIMARY} interaction (NEG delta - POS delta) > 0, "
         "clustered CI excludes 0",
         f"{o3['inter']:+.4f} pts, CI [{loI:+.4f}, {hiI:+.4f}], p_shift {psI:.4f}, "
         f"p_boot {pbbI:.4f}", g2),
        ("G3_neg_cell", f"h={H_PRIMARY} NEG-regime delta vs own-regime uncond control > 0, "
         "CI excludes 0",
         f"{o3['d_neg']:+.4f} pts, CI [{loN:+.4f}, {hiN:+.4f}], p_shift {psN:.4f}, "
         f"p_boot {pbbN:.4f}", g3),
        ("G4_pos_cell_honesty", "POS cell printed with its own-regime control + year table + "
         "2022 sub-cell; 'also pays' check applied",
         f"printed; POS delta {o3['d_pos']:+.4f}, CI [{loP:+.4f}, {hiP:+.4f}], "
         f"{'PAYS' if pos_pays else 'does not pay'}", g4),
        ("G5_cost", "cost band printed ({1,2}-tick RT on ZB)",
         f"${COST_1T:.2f} / ${COST_2T:.2f}; NEG h3 delta ${dneg_usd:+,.2f}/ct/event", g5),
        ("G6_P_MEANING", "IN WORDS: p_shift = one-sided fraction of 2000 shared-offset circular "
         "shifts of the EVENT FLAG whose statistic >= observed (regime+outcomes fixed)",
         "second, independent computation: p_boot from the block bootstrap (printed per cell)",
         True),
        ("G7_CLUSTER_SPAN", f"block length {L_BLOCK} >= max measured event-cluster span",
         f"{len(clusters)} clusters, span P95 {p95_span:.0f}, max {max_span}",
         L_BLOCK >= max_span),
    ]
    P("GATE TABLE  (printed by program)")
    P(f"{'GATE':<22}{'SPEC':<90}{'OBSERVED':<72}{'PASS-FAIL'}")
    all_pass = True
    for g, s, o_, p in gates:
        all_pass &= bool(p)
        P(f"{g:<22}{s:<90}{o_:<72}{'PASS' if p else '*** FAIL ***'}")
    P("")
    prereg = dict(event_z=EVENT_Z, sig_win=SIG_WIN, sig_min=SIG_MIN, corr_win=CORR_WIN,
                  corr_min=CORR_MIN, horizons=HORIZONS, h_primary=H_PRIMARY, n_shift=N_SHIFT,
                  min_shift=MIN_SHIFT, n_bb=N_BB, l_block=L_BLOCK, cluster_gap=CLUSTER_GAP,
                  zb_pv=ZB_PV, commission=COMMISSION, seed=20260906)
    P("PREREG CONSTANTS ECHO: " + json.dumps(prereg))
    P("")

    decision = "FTQGATE01 TAIL-ENGINE CANDIDATE" if (g2 and g3) else "CLOSED AT SCOPE (SS28)"
    if g2 and g3 and pos_pays:
        decision += " -- RECLASSIFY: unconditional FTQ (POS cell also pays; simpler object)"
    P(f"DECISION RULE (mechanical): G2 {'PASS' if g2 else 'FAIL'} + G3 "
      f"{'PASS' if g3 else 'FAIL'} -> {decision}")
    P(f"ALL GATES: {'PASS' if all_pass else '*** AT LEAST ONE FAIL ***'}   "
      f"EVIDENCE STATUS: DISCOVERY (2009..2026-07, burned/discovery window; no forward claim)")
    P("=" * 118)

    # ================================================================ CSV OUTPUTS
    pd.DataFrame(rows_csv).to_csv(os.path.join(OUT, "twobytwo.csv"), index=False)
    reg_series = pd.DataFrame(dict(
        date=dates, es_ret_pts=r_es, zb_ret_pts=r_zb, es_sig60=sig60, es_z=z_es,
        event=event.astype(int), corr_lag1=corr_lag,
        regime=np.where(reg_neg, "NEG", np.where(reg_pos, "POS", "UNDEF"))))
    reg_series.to_csv(os.path.join(OUT, "regime_series.csv"), index=False)

    json.dump(dict(
        decision=decision, g2=bool(g2), g3=bool(g3), pos_pays=bool(pos_pays),
        all_gates_pass=bool(all_pass),
        n_sessions=n, n_events=int(event.sum()), ev_neg=ev_neg_n, ev_pos=ev_pos_n,
        n_clusters=len(clusters), max_cluster_span=max_span,
        primary=dict(h=H_PRIMARY,
                     d_neg=o3["d_neg"], d_neg_ci=[loN, hiN], p_neg_shift=psN, p_neg_boot=pbbN,
                     d_pos=o3["d_pos"], d_pos_ci=[loP, hiP],
                     inter=o3["inter"], inter_ci=[loI, hiI], p_inter_shift=psI,
                     p_inter_boot=pbbI),
        gates=[dict(gate=g, spec=s, observed=o_, ok=bool(p)) for g, s, o_, p in gates]),
        open(os.path.join(OUT, "verdicts.json"), "w", encoding="utf-8"), indent=2)
    _fh.close()


if __name__ == "__main__":
    main()
