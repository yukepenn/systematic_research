#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
G2_F10_MC50_MACRONIGHT_20260906 — MC-50 macro-night falsifier (Stage 2-5).

Implements runs/G2_F10_MC50_MACRONIGHT_20260906/spec.yaml EXACTLY.

Frozen primary (verbatim from the W2 skeptic):
  "NQ 18:00->08:29 net return on NFP/CPI nights at $35/RT + $5.25 ON tax vs matched
   same-weekday non-release nights, eras split 2017/2023, circular-shift shared draw,
   NQ 1-min pre-burn (~450 events — adequate)."

Definitions (END-stamped 1-min bars, exchange-session ET, sessions 18:00 -> 17:00):
  * A release DAY d defines the release NIGHT as 18:00 ET on calendar day d-1 -> 08:29 ET on d.
  * Entry price  = close of the bar stamped (d-1) 18:01 ET; if that bar is absent, the first
    available bar stamped in ((d-1) 18:00, (d-1) 18:30]. No bar in that window -> night dropped
    (counted in the exclusions table).
  * Exit price   = close of the bar stamped d 08:29 ET exactly. Absent -> night dropped (counted).
  * Gross $ = (exit - entry) points x $20 x 1 contract, long side.
  * Net   $ = Gross $ - $40.25  (ALL_IN floor: $35.00/RT + $5.25 overnight tax), charged
    against the long (event) side. Controls are the untraded counterfactual drift and are
    compared at their GROSS mean, per the frozen primary ("net return on NFP/CPI nights ...
    vs matched same-weekday non-release nights").
  * Primary statistic D_net = mean over release nights of (net_i - ctrl_gross_mean(era_i, wd_i)),
    where the control mean is over ALL same-weekday non-release eligible nights of the same era.
    D_gross = D_net + 40.25 (the same statistic before the cost floor).

Null (G2): 401 circular shifts of the release-night LABEL series along the chronologically
ordered calendar of eligible nights; offsets drawn once with a fixed seed and SHARED across
the pooled / NFP-only / CPI-only variants. Two-sided p is quantile-based:
    p = min(1, 2 * min( (1+#{D_k >= D})/(K+1), (1+#{D_k <= D})/(K+1) ))
which is invariant to the constant -$40.25 offset (asserted in-program: p from the net series
equals p from the gross series — the required second, independent computation of the same
probability event).

Eras: 2006..2016 / 2017..2022 / 2023..2026-05.  Seed: 20260906.  K = 401 shifts.
"""

import os
import sys
import numpy as np
import pandas as pd

# ---------------------------------------------------------------- paths / constants
HERE = os.path.dirname(os.path.abspath(__file__))
RUN_DIR = os.path.dirname(HERE)
REPO = os.path.abspath(os.path.join(RUN_DIR, os.pardir, os.pardir))

NQ_PARQUET = os.path.join(REPO, "research", "scalping_lab", "substrate", "minute", "NQ",
                          "nq1m_2005_202605.parquet")
NFP_CSV = os.path.join(REPO, "runs", "GENESIS_H2_CALENDAR_20260828", "out",
                       "calendar_artifacts", "daytype_sessions_NFP_DAY.csv")
CPI_CSV = os.path.join(REPO, "runs", "GENESIS_H2_CALENDAR_20260828", "out",
                       "calendar_artifacts", "daytype_sessions_CPI_DAY.csv")
OUT_DIR = os.path.join(RUN_DIR, "out")
os.makedirs(OUT_DIR, exist_ok=True)

DEV_END = pd.Timestamp("2026-05-29 23:59:59")
POP_START = pd.Timestamp("2006-01-01").date()
POP_END = pd.Timestamp("2026-05-29").date()
POINT_VALUE = 20.0
COST_ALL_IN = 40.25            # $35.00/RT + $5.25 overnight friction tax, BASIS: ALL_IN floor
N_SHIFTS = 401
SEED = 20260906
ENTRY_TOL_END = pd.Timedelta(minutes=30)   # entry bar accepted in ((d-1) 18:00, (d-1) 18:30]

ERAS = [("2006-2016", 2006, 2016), ("2017-2022", 2017, 2022), ("2023-2026-05", 2023, 2026)]


def era_of(d):
    y = d.year
    for name, lo, hi in ERAS:
        if lo <= y <= hi:
            return name
    return None


def two_sided_p(obs, null):
    """Quantile-based two-sided permutation p (obs included in the reference set)."""
    null = np.asarray(null, dtype=float)
    k = len(null)
    p_hi = (1 + np.sum(null >= obs)) / (k + 1)
    p_lo = (1 + np.sum(null <= obs)) / (k + 1)
    return min(1.0, 2.0 * min(p_hi, p_lo))


def main():
    lines = []          # captured report prints

    def say(s=""):
        print(s)
        lines.append(s)

    # ------------------------------------------------------------ load substrate
    df = pd.read_parquet(NQ_PARQUET, columns=["time", "close"])
    t = pd.to_datetime(df["time"])
    close = df["close"].to_numpy()

    # ---- G0: seal --------------------------------------------------------------
    max_ts = t.max()
    assert max_ts <= DEV_END, f"G0 SEAL VIOLATION: substrate max {max_ts} > {DEV_END}"
    g0_obs = f"max substrate timestamp = {max_ts}"
    g0_pass = True

    # ------------------------------------------------------------ anchor-bar maps
    hh = t.dt.hour.to_numpy()
    mm = t.dt.minute.to_numpy()
    dates = t.dt.date.to_numpy()

    # exit map: close of the bar stamped exactly 08:29 on date d
    m_exit = (hh == 8) & (mm == 29)
    exit_map = dict(zip(dates[m_exit], close[m_exit]))
    exit_ts_map = dict(zip(dates[m_exit], t.to_numpy()[m_exit]))

    # entry map: first bar stamped in (18:00, 18:30] on evening date e
    m_ent = (hh == 18) & (mm >= 1) & (mm <= 30)
    ent_idx = np.flatnonzero(m_ent)
    entry_map, entry_ts_map = {}, {}
    for i in ent_idx:                       # ascending time order -> first hit wins
        e = dates[i]
        if e not in entry_map:
            entry_map[e] = close[i]
            entry_ts_map[e] = t.iloc[i]

    # ------------------------------------------------------------ release calendars
    nfp = pd.read_csv(NFP_CSV)["session_date"]
    cpi = pd.read_csv(CPI_CSV)["session_date"]
    nfp_dates = set(pd.to_datetime(nfp).dt.date)
    cpi_dates = set(pd.to_datetime(cpi).dt.date)
    nfp_in = {d for d in nfp_dates if POP_START <= d <= POP_END}
    cpi_in = {d for d in cpi_dates if POP_START <= d <= POP_END}
    rel_in = nfp_in | cpi_in
    overlap = nfp_in & cpi_in

    # ------------------------------------------------------------ eligible-night calendar
    # Candidate nights: every date d with an 08:29 bar, or a release date in range; each needs
    # entry (evening d-1) and exit (morning d) present to be ELIGIBLE.
    candidates = sorted({d for d in exit_map} | rel_in)
    candidates = [d for d in candidates if POP_START <= d <= POP_END]

    rows = []
    excl = {"entry_bar_missing": 0, "exit_bar_missing": 0, "both_missing": 0}
    excl_rel = {"entry_bar_missing": [], "exit_bar_missing": [], "both_missing": []}
    late_entry_events = []
    for d in candidates:
        e = d - pd.Timedelta(days=1)
        e = e.date() if hasattr(e, "date") else e
        has_ent = e in entry_map
        has_ext = d in exit_map
        is_rel = d in rel_in
        if not (has_ent and has_ext):
            key = ("both_missing" if not has_ent and not has_ext
                   else "entry_bar_missing" if not has_ent else "exit_bar_missing")
            excl[key] += 1
            if is_rel:
                excl_rel[key].append(d)
            continue
        entry_px, exit_px = entry_map[e], exit_map[d]
        entry_ts = entry_ts_map[e]
        if is_rel and not (entry_ts.hour == 18 and entry_ts.minute == 1):
            late_entry_events.append((d, str(entry_ts)))
        gross_pts = exit_px - entry_px
        gross_usd = gross_pts * POINT_VALUE
        rows.append({
            "date": d, "weekday": pd.Timestamp(d).day_name(), "era": era_of(pd.Timestamp(d)),
            "is_nfp": d in nfp_in, "is_cpi": d in cpi_in, "is_release": is_rel,
            "entry_ts": str(entry_ts), "entry_px": entry_px,
            "exit_ts": str(pd.Timestamp(exit_ts_map[d])), "exit_px": exit_px,
            "gross_pts": gross_pts, "gross_usd": gross_usd,
            "net_usd": gross_usd - COST_ALL_IN,
        })

    nights = pd.DataFrame(rows).sort_values("date").reset_index(drop=True)
    assert nights["era"].notna().all()
    n_elig = len(nights)
    n_rel = int(nights["is_release"].sum())
    n_nfp = int(nights["is_nfp"].sum())
    n_cpi = int(nights["is_cpi"].sum())
    n_overlap_elig = int((nights["is_nfp"] & nights["is_cpi"]).sum())

    # ------------------------------------------------------------ statistic machinery
    # cell = era x weekday; controls = eligible non-release nights in the cell (GROSS mean).
    cell_key = (nights["era"] + "|" + nights["weekday"]).to_numpy()
    cells, cell_idx = np.unique(cell_key, return_inverse=True)
    n_cells = len(cells)
    gross = nights["gross_usd"].to_numpy()
    net = nights["net_usd"].to_numpy()
    cell_sum = np.bincount(cell_idx, weights=gross, minlength=n_cells)
    cell_cnt = np.bincount(cell_idx, minlength=n_cells).astype(float)

    def diff_stat(ev_mask, ctrl_excl_mask, values):
        """mean over ev of (values_i - gross control mean of cell_i);
        controls = eligible nights NOT in ctrl_excl_mask, per cell."""
        if ev_mask.sum() == 0:
            return np.nan
        ex_sum = np.bincount(cell_idx[ctrl_excl_mask], weights=gross[ctrl_excl_mask],
                             minlength=n_cells)
        ex_cnt = np.bincount(cell_idx[ctrl_excl_mask], minlength=n_cells).astype(float)
        c_cnt = cell_cnt - ex_cnt
        with np.errstate(invalid="ignore", divide="ignore"):
            c_mean = (cell_sum - ex_sum) / c_cnt
        cm = c_mean[cell_idx[ev_mask]]
        if np.isnan(cm).any():
            return np.nan
        return float(np.mean(values[ev_mask] - cm))

    rel_mask = nights["is_release"].to_numpy()
    nfp_mask = nights["is_nfp"].to_numpy()
    cpi_mask = nights["is_cpi"].to_numpy()

    # observed, NET (primary) and GROSS (G4 decomposition); identity D_gross = D_net + 40.25
    D_net = {"pooled": diff_stat(rel_mask, rel_mask, net),
             "nfp": diff_stat(nfp_mask, rel_mask, net),
             "cpi": diff_stat(cpi_mask, rel_mask, net)}
    D_gross = {"pooled": diff_stat(rel_mask, rel_mask, gross),
               "nfp": diff_stat(nfp_mask, rel_mask, gross),
               "cpi": diff_stat(cpi_mask, rel_mask, gross)}
    for k in D_net:
        assert abs(D_gross[k] - (D_net[k] + COST_ALL_IN)) < 1e-9, "gross/net identity broken"

    # second computation of the pooled difference (independent code path: per-cell weighted form)
    d2_terms = []
    for c in range(n_cells):
        in_cell = cell_idx == c
        ev = in_cell & rel_mask
        ct = in_cell & ~rel_mask
        if ev.sum() == 0:
            continue
        assert ct.sum() > 0
        d2_terms += list(net[ev] - gross[ct].mean())
    D_net_check = float(np.mean(d2_terms))
    assert abs(D_net_check - D_net["pooled"]) < 1e-9, \
        f"cross-check FAIL: {D_net_check} vs {D_net['pooled']}"

    # ------------------------------------------------------------ G2 null: 401 shared shifts
    rng = np.random.default_rng(SEED)
    offsets = rng.choice(np.arange(1, n_elig), size=N_SHIFTS, replace=False)
    null_net = {"pooled": [], "nfp": [], "cpi": []}
    null_gross = {"pooled": [], "nfp": [], "cpi": []}
    for k in offsets:
        s_nfp = np.roll(nfp_mask, k)          # SHARED offset across variants: same roll
        s_cpi = np.roll(cpi_mask, k)          # applied to both label series
        s_rel = s_nfp | s_cpi
        for name, m in (("pooled", s_rel), ("nfp", s_nfp), ("cpi", s_cpi)):
            null_net[name].append(diff_stat(m, s_rel, np.where(m, gross - COST_ALL_IN, gross)))
            null_gross[name].append(diff_stat(m, s_rel, gross))

    p_net = {k: two_sided_p(D_net[k], null_net[k]) for k in D_net}
    p_gross = {k: two_sided_p(D_gross[k], null_gross[k]) for k in D_gross}
    # REQUIRED second computation of the probability event: the quantile-based p must be
    # invariant to the constant -$40.25 (net vs gross series give the same p).
    for k in p_net:
        assert abs(p_net[k] - p_gross[k]) < 1e-12, f"p invariance broken for {k}"
    sd_null = float(np.std(null_net["pooled"], ddof=1))

    g2_pass = p_net["pooled"] <= 0.05

    # ------------------------------------------------------------ G3 eras
    era_rows = []
    era_signs = []
    for name, lo, hi in ERAS:
        em = (nights["era"] == name).to_numpy()
        ev = rel_mask & em
        d_era_net = diff_stat(ev, rel_mask, net)     # controls restricted to same era via cells
        d_era_gross = d_era_net + COST_ALL_IN
        ctrl_m = em & ~rel_mask
        era_rows.append({
            "era": name, "n_release": int(ev.sum()),
            "n_nfp": int((nfp_mask & em).sum()), "n_cpi": int((cpi_mask & em).sum()),
            "n_controls": int(ctrl_m.sum()),
            "release_gross_mean_usd": round(float(gross[ev].mean()), 2) if ev.sum() else np.nan,
            "release_net_mean_usd": round(float(net[ev].mean()), 2) if ev.sum() else np.nan,
            "control_gross_mean_usd": round(float(gross[ctrl_m].mean()), 2),
            "diff_net_usd": round(d_era_net, 2), "diff_gross_usd": round(d_era_gross, 2),
        })
        era_signs.append(np.sign(d_era_net))
    pooled_sign = np.sign(D_net["pooled"])
    n_agree = int(sum(1 for s in era_signs if s == pooled_sign))
    g3_pass = n_agree >= 2

    # ------------------------------------------------------------ G4 decomposition
    rel_gross_mean = float(gross[rel_mask].mean())
    rel_net_mean = float(net[rel_mask].mean())
    ctrl_gross_pool = float(gross[~rel_mask].mean())
    gross_passes = (D_gross["pooled"] > 0) and (p_gross["pooled"] <= 0.05)
    net_fails = D_net["pooled"] <= 0
    cost_killed = gross_passes and net_fails

    # ------------------------------------------------------------ G5 power (on any FAIL)
    any_fail = (not g2_pass) or (not g3_pass)
    mde80 = (1.959964 + 0.841621) * sd_null          # (z_.975 + z_.80) * sd(null)
    underpowered = mde80 > 3.0 * abs(D_net["pooled"])          # literal spec formula
    # Cost-invariant reading (CAP01 rule: a gate must test what the output MEANS): |D_net|
    # embeds the constant -$40.25 floor; the information effect is the departure of the
    # difference from the null center, which equals D_gross (null gross diffs center ~0).
    null_net_mean = float(np.mean(null_net["pooled"]))
    departure = D_net["pooled"] - null_net_mean
    underpowered_departure = mde80 > 3.0 * abs(departure)

    # ------------------------------------------------------------ outputs: night table
    ev_tab = nights[rel_mask].copy()
    ev_tab["type"] = np.where(ev_tab["is_nfp"] & ev_tab["is_cpi"], "NFP+CPI",
                              np.where(ev_tab["is_nfp"], "NFP", "CPI"))
    ctrl_means = {}
    for c in range(n_cells):
        m = (cell_idx == c) & ~rel_mask
        ctrl_means[cells[c]] = gross[m].mean() if m.sum() else np.nan
    ev_tab["control_era_mean_gross_usd"] = [round(ctrl_means[k], 2)
                                            for k in cell_key[rel_mask]]
    ev_tab = ev_tab[["date", "type", "weekday", "era", "entry_ts", "entry_px", "exit_ts",
                     "exit_px", "gross_pts", "gross_usd", "net_usd",
                     "control_era_mean_gross_usd"]]
    ev_tab.to_csv(os.path.join(OUT_DIR, "night_table.csv"), index=False)
    pd.DataFrame(era_rows).to_csv(os.path.join(OUT_DIR, "era_table.csv"), index=False)
    nights.to_csv(os.path.join(OUT_DIR, "eligible_nights.csv"), index=False)

    # ------------------------------------------------------------ prints
    say("=" * 100)
    say("G2_F10_MC50_MACRONIGHT_20260906 — MC-50 macro-night falsifier  (seed=%d, K=%d shifts)"
        % (SEED, N_SHIFTS))
    say("=" * 100)
    say()
    g1_sentence = (
        "G1 SEMANTIC: The population is every NQ overnight session 18:00 ET (prior evening) -> "
        "08:29 ET with both anchor bars present, session dates 2006-01-01..2026-05-29 "
        f"({n_elig} eligible nights); events are the {n_rel} NFP/CPI release nights "
        f"({n_nfp} NFP, {n_cpi} CPI, {n_overlap_elig} tagged both, counted once); controls are "
        "ALL same-weekday non-release nights in the same era. The event tested is the mean NET "
        "point P&L per night of 1 long NQ contract ($20/pt) after the $40.25 ALL_IN floor on "
        "release nights, minus the matched same-weekday same-era control GROSS mean — i.e. "
        "whether holding long into the release pays more than the ordinary night drift by more "
        "than the cost floor.")
    say(g1_sentence)
    say()
    say(f"Realized N: {n_rel} release nights (vs ~450 expected by the frozen primary). "
        f"NFP={n_nfp}, CPI={n_cpi}, overlap counted once={n_overlap_elig}.")
    say(f"Calendar files in range: NFP {len(nfp_in)}, CPI {len(cpi_in)}, union {len(rel_in)}, "
        f"overlap {len(overlap)}.")
    say()
    say("EXCLUSIONS (release nights dropped, both-bars rule):")
    say(f"{'reason':<24}{'n_release_dropped':>18}   dates")
    tot_drop = 0
    for k in ("entry_bar_missing", "exit_bar_missing", "both_missing"):
        ds = excl_rel[k]
        tot_drop += len(ds)
        say(f"{k:<24}{len(ds):>18}   {', '.join(str(x) for x in ds) if ds else '-'}")
    say(f"{'TOTAL':<24}{tot_drop:>18}")
    say(f"(all-night exclusions incl. controls: entry {excl['entry_bar_missing']}, "
        f"exit {excl['exit_bar_missing']}, both {excl['both_missing']}; "
        f"release entries filled by a later-than-18:01 bar within (18:00,18:30]: "
        f"{len(late_entry_events)})")
    say()
    say("POOLED / DECOMPOSITION (NET diff = event net mean - matched control gross mean; "
        "GROSS diff = +$40.25):")
    say(f"{'variant':<10}{'N_ev':>6}{'D_net $/night':>16}{'D_gross $/night':>17}"
        f"{'p (two-sided)':>15}")
    for k, lbl in (("pooled", "POOLED"), ("nfp", "NFP-only"), ("cpi", "CPI-only")):
        n_ev = {"pooled": n_rel, "nfp": n_nfp, "cpi": n_cpi}[k]
        say(f"{lbl:<10}{n_ev:>6}{D_net[k]:>16.2f}{D_gross[k]:>17.2f}{p_net[k]:>15.4f}")
    say("(NFP-only / CPI-only are decomposition prints, not separate chances.)")
    say()
    say("ERA TABLE:")
    say(pd.DataFrame(era_rows).to_string(index=False))
    say()
    say(f"G4 decomposition: release gross mean {rel_gross_mean:+.2f} $/night, net mean "
        f"{rel_net_mean:+.2f} $/night; pooled control gross mean {ctrl_gross_pool:+.2f}; "
        f"D_gross {D_gross['pooled']:+.2f} (p={p_gross['pooled']:.4f}), "
        f"D_net {D_net['pooled']:+.2f}.")
    if cost_killed:
        say("G4 verdict: cost-killed at the $40.25 floor")
    say()
    say(f"Null sd (pooled, 401 shared circular shifts): {sd_null:.2f} $/night; null mean of "
        f"the NET stat: {null_net_mean:+.2f} (= ~-$40.25 as expected); "
        f"MDE @80% power = {mde80:.2f} $/night.")
    say(f"G5 literal comparison (spec formula, |observed| = |D_net|): MDE {mde80:.2f} vs "
        f"3x|D_net| = {3*abs(D_net['pooled']):.2f} -> "
        f"{'UNDERPOWERED_STILL' if underpowered else 'not underpowered by the literal formula'}.")
    say(f"G5 cost-invariant caveat: |D_net| embeds the constant -$40.25 floor; the observed "
        f"INFORMATION departure from the null center is {departure:+.2f} $/night, and MDE "
        f"{mde80:.2f} > 3x|departure| = {3*abs(departure):.2f} -> the 'no gross information' "
        f"sub-claim is UNDERPOWERED_STILL and closes nothing on its own."
        if underpowered_departure else
        f"G5 cost-invariant check: departure {departure:+.2f}, 3x|departure| = "
        f"{3*abs(departure):.2f} >= MDE {mde80:.2f} -> adequately powered on both readings.")
    say()

    # ------------------------------------------------------------ gate table
    gt = []
    gt.append(("G0_seal", "max substrate date <= 2026-05-29 (hard assert)", g0_obs,
               "PASS" if g0_pass else "FAIL"))
    gt.append(("G1_semantic", "one printed sentence: population + event",
               "printed above (population, event, cost basis named)", "PASS"))
    gt.append(("G2_primary",
               "pooled two-sided p <= 0.05 vs 401 shared circular shifts of the label series",
               f"D_net={D_net['pooled']:+.2f} $/night, p={p_net['pooled']:.4f} "
               f"(p invariant net/gross: asserted)",
               "PASS" if g2_pass else "FAIL"))
    gt.append(("G3_era_stability",
               "sign of pooled difference agrees in >= 2 of 3 eras "
               "(2006..2016 / 2017..2022 / 2023..2026-05)",
               f"pooled sign {'+' if pooled_sign>0 else '-'}; era D_net signs "
               f"{['+' if s>0 else '-' for s in era_signs]}; agree={n_agree}/3",
               "PASS" if g3_pass else "FAIL"))
    g4_obs = (f"D_gross={D_gross['pooled']:+.2f} (p={p_gross['pooled']:.4f}), "
              f"D_net={D_net['pooled']:+.2f}; gross_passes={gross_passes}, "
              f"net_fails={net_fails}" + ("; COST-KILLED at the $40.25 floor" if cost_killed
                                          else ""))
    gt.append(("G4_gross_decomposition", "gross vs net printed; cost-killed branch evaluated",
               g4_obs, "PRINTED"))
    if any_fail:
        g5_obs = (f"MDE@80%={mde80:.2f} $/night; literal 3x|D_net|={3*abs(D_net['pooled']):.2f}"
                  + (" -> UNDERPOWERED_STILL; this FAIL closes nothing on its own"
                     if underpowered else " -> not underpowered by the literal formula")
                  + f"; cost-invariant 3x|departure|={3*abs(departure):.2f}"
                  + (" -> no-information sub-claim UNDERPOWERED_STILL, closes nothing on its own"
                     if underpowered_departure else " -> adequately powered"))
    else:
        g5_obs = "no gate failed; MDE print not triggered (power stat: MDE@80%%=%.2f)" % mde80
    gt.append(("G5_power", "MDE at 80% power printed on any FAIL; UNDERPOWERED_STILL if "
               "MDE > 3x|observed|", g5_obs, "PRINTED"))

    w = (22, 88, 96, 10)
    sep = "-" * (sum(w) + 6)
    gtl = ["GATE TABLE (program-printed)", sep,
           f"{'GATE':<{w[0]}}| {'SPEC':<{w[1]}}| {'OBSERVED':<{w[2]}}| PASS-FAIL", sep]
    for g, s, o, v in gt:
        gtl.append(f"{g:<{w[0]}}| {s:<{w[1]}}| {o:<{w[2]}}| {v}")
    gtl.append(sep)
    verdict = "PASS (G2+G3)" if (g2_pass and g3_pass) else \
              ("REGIME_LOCAL (G2 pass, G3 fail)" if g2_pass else "FAIL")
    gtl.append(f"VERDICT: {verdict}   | evidence status of every number: DISCOVERY_CONSUMED")
    gate_txt = "\n".join(gtl)
    say(gate_txt)

    with open(os.path.join(OUT_DIR, "gate_table.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    # machine-readable summary for the report writer
    import json
    summary = {
        "n_eligible_nights": n_elig, "n_release": n_rel, "n_nfp": n_nfp, "n_cpi": n_cpi,
        "n_overlap": n_overlap_elig,
        "D_net": {k: round(v, 4) for k, v in D_net.items()},
        "D_gross": {k: round(v, 4) for k, v in D_gross.items()},
        "p": {k: round(v, 6) for k, v in p_net.items()},
        "era_rows": era_rows, "sd_null": round(sd_null, 4), "mde80": round(mde80, 4),
        "underpowered_literal": bool(underpowered),
        "underpowered_departure": bool(underpowered_departure),
        "departure": round(departure, 4), "null_net_mean": round(null_net_mean, 4),
        "cost_killed": bool(cost_killed),
        "gross_passes": bool(gross_passes), "net_fails": bool(net_fails),
        "g2_pass": bool(g2_pass), "g3_pass": bool(g3_pass), "verdict": verdict,
        "rel_gross_mean": round(rel_gross_mean, 4), "rel_net_mean": round(rel_net_mean, 4),
        "ctrl_gross_mean_pooled": round(ctrl_gross_pool, 4),
        "exclusions_release": {k: [str(x) for x in v] for k, v in excl_rel.items()},
        "exclusions_all_nights": excl, "late_entry_events": late_entry_events,
        "seed": SEED, "n_shifts": N_SHIFTS,
    }
    with open(os.path.join(OUT_DIR, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, default=str)
    return summary


if __name__ == "__main__":
    main()
