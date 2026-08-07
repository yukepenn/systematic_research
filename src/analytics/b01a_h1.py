"""B01a — DR05-H1 overshoot / failed-flip calibration (RESEARCH_WAVE_B01).

Preregistered in research/04_complementary_family/B01_WAVE_SPEC.md and DR-05.md;
constants frozen there: theta = 179 ticks, failure = max overshoot < 0.25*theta
within 60 min of flip confirmation, re-cross margin 10 ticks. Instrumentation
(seq 0): a property of the price stream, not a strategy.

Definitions implemented exactly as written:
  * DC ledger: dc_overshoot.dc_segments on 1-min closes (methodological
    continuity with DC01), theta=179, start_up=False.
  * omega: overshoot from flip price to segment close-extreme until the opposite
    flip (dc_segments column), in ticks.
  * failure: max (close - p_flip)*dirn over the 60 BARS after confirmation
    < 0.25*theta (60 one-minute trading bars = 60 trading minutes).
  * unconditional continuation: (c[t0+60] - c[t0]) * dirn from flip confirmation.
  * failed-flip continuation: (c[t1+60] - c[t1]) * dirn where t1 = t0 + 60 (the
    failure stamp).
  * PASS (a): yearly mean omega in [0.5*theta, 1.5*theta] every calendar year.
  * PASS (b): median failed continuation <= unconditional median - 10 ticks,
    same sign of difference in >= 4 of 5 years, pooled one-sided
    Mann-Whitney/Wilcoxon p < 0.05.

Usage: python src/analytics/b01a_h1.py   (CWD = repo root)
Writes: research/04_complementary_family/b01a_h1_ledger.csv.gz
        research/04_complementary_family/b01a_h1_report.md
"""
import os
import sys

import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dc_overshoot import dc_segments  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BARS = os.path.join(ROOT, "runs", "B01A_BARS_1M", "nq_1m_2022_2026.csv")
OUT = os.path.join(ROOT, "research", "04_complementary_family")

THETA_TICKS = 179
TICK = 0.25
THETA_PTS = THETA_TICKS * TICK          # 44.75
FAIL_PTS = 0.25 * THETA_PTS             # 11.1875 (45 ticks per DR-05 rounding)
RECROSS_PTS = 10 * TICK                 # 2.50
WIN = 60                                 # bars (= trading minutes)
HORIZONS = [15, 30, 60, 120]


def main():
    bars = pd.read_csv(BARS, parse_dates=["time"])
    c = bars.close.to_numpy(float)
    times = bars.time.to_numpy()
    n = len(c)
    seg = dc_segments(bars.close, THETA_TICKS, tick=TICK, start_up=False)
    seg = seg.reset_index(drop=True)
    print(f"bars {n:,}  segments {len(seg):,}")

    t0 = seg.i_flip.to_numpy()
    dirn = seg.dirn.to_numpy(float)
    p_flip = seg.p_flip.to_numpy()

    # rolling forward extremes within the 60-bar observation window
    max_os60 = np.full(len(seg), np.nan)
    t_maxos = np.full(len(seg), -1)
    recross_bar = np.full(len(seg), -1)
    fwd = {h: np.full(len(seg), np.nan) for h in HORIZONS}
    cont_fail = np.full(len(seg), np.nan)
    for k in range(len(seg)):
        a = t0[k]
        b = min(a + WIN, n - 1)
        w = (c[a + 1:b + 1] - p_flip[k]) * dirn[k]
        if len(w):
            max_os60[k] = w.max()
            t_maxos[k] = int(np.argmax(w)) + 1
        # first close-basis re-cross of the flip price by >= 10 ticks (any time
        # before the segment's closing flip; H2's entry event)
        e = int(seg.i_next.iloc[k])
        wr = (c[a + 1:e + 1] - p_flip[k]) * dirn[k]
        hits = np.nonzero(wr <= -RECROSS_PTS)[0]
        if len(hits):
            recross_bar[k] = int(hits[0]) + 1
        for h in HORIZONS:
            if a + h < n:
                fwd[h][k] = (c[a + h] - c[a]) * dirn[k]
        t1 = a + WIN
        if t1 + WIN < n:
            cont_fail[k] = (c[t1 + WIN] - c[t1]) * dirn[k]

    led = seg.copy()
    led["time_flip"] = times[t0]
    led["year"] = pd.DatetimeIndex(led.time_flip).year
    hrs = pd.DatetimeIndex(led.time_flip).hour
    led["session_bucket"] = np.select(
        [(hrs >= 18) | (hrs < 2), (hrs >= 2) & (hrs < 8),
         (hrs >= 8) & (hrs < 12), (hrs >= 12) & (hrs < 14)],
        ["B1_asia", "B2_europe", "B3_us_open", "B4_midday"], "B5_close")
    led["omega_ticks"] = led.omega / TICK
    led["max_os60_ticks"] = max_os60 / TICK
    led["t_maxos_bar"] = t_maxos
    led["failed"] = max_os60 < FAIL_PTS
    led["recross_bar"] = recross_bar
    for h in HORIZONS:
        led[f"fwd{h}_ticks"] = fwd[h] / TICK
    led["cont_fail_ticks"] = cont_fail / TICK

    os.makedirs(OUT, exist_ok=True)
    led.to_csv(os.path.join(OUT, "b01a_h1_ledger.csv.gz"), index=False)

    # ---- arm (a): yearly mean overshoot in [0.5, 1.5] * theta
    a_tab = led.groupby("year").omega_ticks.agg(["count", "mean"])
    a_tab["in_band"] = a_tab["mean"].between(0.5 * THETA_TICKS, 1.5 * THETA_TICKS)
    a_pass = bool(a_tab.in_band.all())

    # ---- arm (b): failed vs unconditional continuation
    uncond = led.fwd60_ticks.dropna()
    fail = led.loc[led.failed, "cont_fail_ticks"].dropna()
    med_u, med_f = uncond.median(), fail.median()
    delta = med_f - med_u
    yearly = []
    for y, g in led.groupby("year"):
        mu = g.fwd60_ticks.dropna().median()
        mf = g.loc[g.failed, "cont_fail_ticks"].dropna().median()
        yearly.append(dict(year=y, n_flips=len(g), n_failed=int(g.failed.sum()),
                           med_uncond=round(mu, 2), med_failed=round(mf, 2),
                           diff=round(mf - mu, 2), worse=bool(mf < mu)))
    ytab = pd.DataFrame(yearly)
    sign_stable = int(ytab.worse.sum())
    stat, p = mannwhitneyu(fail, uncond, alternative="less")
    b_pass = bool((delta <= -10) and (sign_stable >= 4) and (p < 0.05))

    verdict = "PASS" if (a_pass and b_pass) else "FAIL"
    rep = []
    rep.append("# B01a — DR05-H1 calibration result\n")
    rep.append(f"_2026-08-07 · {len(seg):,} DC segments (theta=179 ticks) on "
               f"{n:,} one-minute closes 2022-01→2026-07 · driver "
               f"`src/analytics/b01a_h1.py` · constants frozen in DR-05.md._\n")
    rep.append(f"## VERDICT: **{verdict}**  (arm a: {'PASS' if a_pass else 'FAIL'}, "
               f"arm b: {'PASS' if b_pass else 'FAIL'})\n")
    rep.append("## Arm (a) — yearly mean overshoot, band [89.5, 268.5] ticks\n")
    rep.append(a_tab.round(2).to_markdown())
    rep.append("\n## Arm (b) — failed-flip continuation vs unconditional\n")
    rep.append(f"- failed flips: {len(fail):,} of {len(led):,} "
               f"({100 * led.failed.mean():.1f}%)")
    rep.append(f"- pooled median continuation: failed {med_f:.2f} ticks vs "
               f"unconditional {med_u:.2f} ticks → diff {delta:+.2f} "
               f"(requirement ≤ −10)")
    rep.append(f"- sign stability: worse in {sign_stable}/5 years (requirement ≥ 4)")
    rep.append(f"- one-sided Mann-Whitney p = {p:.2e} (requirement < 0.05)\n")
    rep.append(ytab.to_markdown(index=False))
    rep.append("\n## Ledger\n`b01a_h1_ledger.csv.gz` — per-flip omega, 60-min max "
               "overshoot, failure flag, re-cross bar (≥10-tick margin), forward "
               "returns at 15/30/60/120 min, year/side/session strata. Feeds "
               "DR05-H2 (B01b) if PASS; kills it unbuilt if FAIL.")
    with open(os.path.join(OUT, "b01a_h1_report.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(rep))
    print("\n".join(rep[:12]))
    print("wrote b01a_h1_ledger.csv.gz, b01a_h1_report.md")


if __name__ == "__main__":
    main()
