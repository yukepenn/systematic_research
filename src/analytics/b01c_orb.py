"""B01c — DR05-H3: opening-range-breakout failure + value reacceptance fade.

Preregistered: runs/B01C_ORB_FAIL/spec.yaml (seq 230). ALL constants frozen in
DR-05.md. Read order enforced: event census printed and gated (n >= 150) BEFORE
any P&L is computed (guarded by --pnl flag so the census run cannot leak P&L).

Event definition (per closed 1-min bar, ET timestamps):
  OR window 09:30-10:00; OR high/low from those bars' highs/lows.
  Breakout:      first close > OR_high (up) or < OR_low (down) after 10:00.
  Failure:       a close back inside the OR within 15 minutes of the breakout close.
  Reacceptance:  the next 2 consecutive closes also inside (the failure close plus
                 one more, i.e. two consecutive inside closes ending the pattern).
  Veto:          at the reacceptance stamp, theta=179 DC direction == breakout
                 direction AND current segment overshoot >= 0.5*theta.
  Entry:         next bar OPEN, direction opposite the breakout.
  Stop:          10 ticks beyond the breakout extreme (highest high of the
                 breakout excursion for up-breakouts; lowest low for down).
  Target:        session VWAP (anchor 18:00 ET, cum (H+L+C)/3 * vol), evaluated
                 against the bar's range using the PRIOR closed bar's VWAP value.
  Time stop:     90 minutes after entry (bar close); safety flatten 16:55 close.
  <= 1 trade per side per session.

Usage:
    python src/analytics/b01c_orb.py            # census only (no P&L)
    python src/analytics/b01c_orb.py --pnl      # census + P&L + gates
"""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dc_overshoot import dc_segments  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BARS = os.path.join(ROOT, "runs", "B01A_BARS_1M", "nq_1m_2022_2026.csv")
OUT = os.path.join(ROOT, "research", "04_complementary_family")

TICK = 0.25
PV = 20.0
THETA_PTS = 179 * TICK
STOP_PTS = 10 * TICK
RT_COMM = 4.36
FAIL_WIN = 15      # minutes from breakout close
TIME_STOP = 90     # minutes from entry
MAX_HOLD_END = (16, 55)


def load():
    bars = pd.read_csv(BARS, parse_dates=["time"])
    bars["date"] = bars.time.dt.date
    # session id from the exporter's first_bar_of_session flag
    bars["sess"] = bars.first_bar_of_session.cumsum()
    tp = (bars.high + bars.low + bars.close) / 3.0
    pv_cum = (tp * bars.volume).groupby(bars.sess).cumsum()
    v_cum = bars.volume.groupby(bars.sess).cumsum()
    bars["vwap"] = pv_cum / v_cum.replace(0, np.nan)
    return bars


def dc_state(bars):
    """Per-bar theta=179 DC direction and running overshoot (points)."""
    seg = dc_segments(bars.close, 179, tick=TICK, start_up=False)
    dirn = np.zeros(len(bars))
    ovr = np.zeros(len(bars))
    c = bars.close.to_numpy()
    for r in seg.itertuples():
        a, e = int(r.i_flip), int(r.i_next)
        dirn[a:e] = r.dirn
        run = np.maximum.accumulate((c[a:e] - r.p_flip) * r.dirn)
        ovr[a:e] = run
    return dirn, ovr


def find_events(bars):
    dirn, ovr = dc_state(bars)
    ev = []
    hh, ll, cc, oo = (bars.high.to_numpy(), bars.low.to_numpy(),
                      bars.close.to_numpy(), bars.open.to_numpy())
    minutes = bars.time.dt.hour * 60 + bars.time.dt.minute
    for d, g in bars.groupby("date"):
        idx = g.index.to_numpy()
        m = minutes.loc[idx].to_numpy()
        orm = (m > 570) & (m <= 600)          # bars closing 09:31..10:00
        if orm.sum() < 25:
            continue                           # holiday/short session
        or_hi, or_lo = hh[idx[orm]].max(), ll[idx[orm]].min()
        post = idx[(m > 600) & (m <= 960)]     # 10:00 -> 16:00 close stamps
        done = {1: False, -1: False}
        k = 0
        while k < len(post):
            i = post[k]
            side = 1 if cc[i] > or_hi else (-1 if cc[i] < or_lo else 0)
            if side == 0 or done[side]:
                k += 1
                continue
            # breakout at bar i; look for failure close within FAIL_WIN minutes
            j = i + 1
            ext = hh[i] if side == 1 else ll[i]
            fail = -1
            while j < post[-1] and (j - i) <= FAIL_WIN:
                ext = max(ext, hh[j]) if side == 1 else min(ext, ll[j])
                inside = (cc[j] <= or_hi) if side == 1 else (cc[j] >= or_lo)
                if inside:
                    fail = j
                    break
                j += 1
            if fail < 0:
                done[side] = True             # sustained breakout; no re-arm
                k += 1
                continue
            # reacceptance: next close also inside
            r = fail + 1
            inside2 = r < post[-1] and ((cc[r] <= or_hi) if side == 1
                                        else (cc[r] >= or_lo))
            if not inside2:
                k = int(np.searchsorted(post, r))
                continue
            vetoed = (dirn[r] == side) and (ovr[r] >= 0.5 * THETA_PTS)
            ev.append(dict(date=d, i_break=i, i_reacc=r, side=side,
                           or_hi=or_hi, or_lo=or_lo, extreme=ext,
                           vetoed=bool(vetoed), year=pd.Timestamp(d).year))
            done[side] = True
            k = int(np.searchsorted(post, r + 1))
    return pd.DataFrame(ev)


def simulate(bars, events, slip_ticks=1):
    hh, ll, cc, oo = (bars.high.to_numpy(), bars.low.to_numpy(),
                      bars.close.to_numpy(), bars.open.to_numpy())
    vw = bars.vwap.to_numpy()
    tm = bars.time
    rows = []
    slip = slip_ticks * TICK
    for e in events.itertuples():
        if e.vetoed:
            continue
        i0 = e.i_reacc + 1
        if i0 >= len(bars):
            continue
        side = -e.side                          # fade the breakout
        entry = oo[i0] - side * 0 + (slip if side == 1 else -slip)
        stop = e.extreme + (STOP_PTS if e.side == 1 else -STOP_PTS)
        t_end = i0
        limit_t = tm.iloc[i0] + pd.Timedelta(minutes=TIME_STOP)
        exit_px, reason = None, None
        j = i0
        while j < len(bars) - 1:
            if tm.iloc[j] >= limit_t:
                exit_px, reason = cc[j], "time"
                break
            h_, l_ = hh[j], ll[j]
            hit_stop = (h_ >= stop) if side == -1 else (l_ <= stop)
            tgt = vw[j - 1]
            hit_tgt = (l_ <= tgt <= h_)
            if hit_stop and hit_tgt:
                exit_px, reason = stop, "stop"   # conservative: stop first
                break
            if hit_stop:
                exit_px, reason = stop, "stop"
                break
            if hit_tgt:
                exit_px, reason = tgt, "vwap"
                break
            if (tm.iloc[j].hour, tm.iloc[j].minute) >= MAX_HOLD_END:
                exit_px, reason = cc[j], "eod"
                break
            j += 1
        if exit_px is None:
            exit_px, reason = cc[j], "eof"
        exit_px = exit_px - (slip if side == 1 else -slip)
        pnl = side * (exit_px - entry) * PV - RT_COMM
        rows.append(dict(date=e.date, year=e.year, side=side, entry=entry,
                         exit=exit_px, reason=reason, pnl=round(pnl, 2),
                         bars_held=j - i0))
    return pd.DataFrame(rows)


def main():
    bars = load()
    ev = find_events(bars)
    n_total, n_veto = len(ev), int(ev.vetoed.sum()) if len(ev) else 0
    n_trade = n_total - n_veto
    print(f"CENSUS: events {n_total} | vetoed {n_veto} | tradable {n_trade}")
    if len(ev):
        print(ev.groupby("year").agg(events=("side", "size"),
                                     vetoed=("vetoed", "sum")).to_string())
    ev.to_csv(os.path.join(OUT, "b01c_event_census.csv"), index=False)
    if n_trade < 150:
        print("VERDICT: INCONCLUSIVE (n < 150) — per spec, stop before P&L.")
        return
    if "--pnl" not in sys.argv:
        print("Census gate passed (n >= 150). Re-run with --pnl to read P&L.")
        return
    for s in [0, 1, 2]:
        tr = simulate(bars, ev, slip_ticks=s)
        gp = tr.pnl[tr.pnl > 0].sum()
        gl = -tr.pnl[tr.pnl < 0].sum()
        pf = gp / gl if gl else np.inf
        yr = tr.groupby("year").pnl.sum()
        daily = tr.groupby("date").pnl.sum()
        top5 = daily.nlargest(5).sum()
        print(f"\nslip-{s}: n {len(tr)} net ${tr.pnl.sum():,.2f} PF {pf:.3f} "
              f"avg ${tr.pnl.mean():.2f} pos-years {(yr > 0).sum()}/{len(yr)} "
              f"net-ex-top5-days ${tr.pnl.sum() - top5:,.2f}")
        print("  yearly: " + "  ".join(f"{y}:{v:,.0f}" for y, v in yr.items()))
        print("  exits: " + str(tr.reason.value_counts().to_dict()))
        if s == 1:
            tr.to_csv(os.path.join(OUT, "b01c_trades_slip1.csv"), index=False)


if __name__ == "__main__":
    main()
