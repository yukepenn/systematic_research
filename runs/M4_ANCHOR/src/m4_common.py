"""M4_ANCHOR — member-level state machine with anchor origin/confirmation as a free choice.

member_states_anchor / member_trades_anchor are near-verbatim copies of
sm01_solarsim.member_states / member_trades, generalized to a `mode` parameter. mode="CLOSE"
must reproduce the original bit-for-bit (verified by this run's parity assertion). Lessons
carried over from M3 (module-name collision, pend_pos not pos) are already applied here.
"""
import os, sys
import numpy as np, pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
import sm01_solarsim as sm

MODES = ("CLOSE", "HILO_RAW", "CLOSE_CONFIRMED")


def member_states_anchor(close, high, low, sigma, vol_mult, mode,
                          stop_mult_ticks=179.0, smin_ticks=40.0, smax_ticks=1200.0,
                          start_up=False):
    """mode="CLOSE": verbatim sm01_solarsim.member_states (anchor tracks close, reversal test on
    close). mode="HILO_RAW": anchor tracks running max(high)/min(low); reversal test uses the
    SAME intrabar series (low breaches while up, high breaches while down) -- H-008's replicated
    construction. mode="CLOSE_CONFIRMED": anchor origin is intrabar (max(high)/min(low), same as
    HILO_RAW) but the reversal test is CONFIRMED by close -- directive §6's "at most one blended
    form", no numeric weight anywhere.
    """
    assert mode in MODES
    n = close.size
    lo, hi = smin_ticks * sm.TICK, smax_ticks * sm.TICK
    fallback = stop_mult_ticks * sm.TICK

    def resolve_s(t):
        s = sigma[t]
        if not np.isfinite(s) or s <= 0:
            return fallback
        return min(max(vol_mult * s, lo), hi)

    is_up = np.zeros(n, dtype=bool)
    flip = np.zeros(n, dtype=np.int8)
    s_eff = np.empty(n)
    anchor_out = np.empty(n)

    up = bool(start_up)
    anchor = close[0]
    S = resolve_s(0)
    is_up[0] = up; s_eff[0] = S; anchor_out[0] = anchor

    for t in range(1, n):
        if mode == "CLOSE":
            origin_up, origin_dn = close[t], close[t]
            test_up, test_dn = close[t], close[t]
            reset_up, reset_dn = close[t], close[t]
        elif mode == "HILO_RAW":
            origin_up, origin_dn = high[t], low[t]
            test_up, test_dn = low[t], high[t]
            reset_up, reset_dn = low[t], high[t]
        else:  # CLOSE_CONFIRMED
            origin_up, origin_dn = high[t], low[t]
            test_up, test_dn = close[t], close[t]
            reset_up, reset_dn = close[t], close[t]

        if up:
            if origin_up >= anchor:
                anchor = origin_up
            elif test_up < anchor - S:
                up = False
                S = resolve_s(t)
                anchor = reset_up
                flip[t] = -1
        else:
            if origin_dn <= anchor:
                anchor = origin_dn
            elif test_dn > anchor + S:
                up = True
                S = resolve_s(t)
                anchor = reset_dn
                flip[t] = 1
        is_up[t] = up; s_eff[t] = S; anchor_out[t] = anchor
    return is_up, flip, s_eff, anchor_out


def member_trades_anchor(bars, is_up, flip, s_eff, anchor, mode, bars_required=20,
                          comm_side=sm.NQ_COMM_SIDE, point_value=sm.NQ_POINT_VALUE):
    """Verbatim sm01_solarsim.member_trades, EXCEPT the exit-check `xl`/`close[t]` comparison
    uses the SAME origin/test convention as member_states_anchor's mode, so the exit condition
    here is structurally consistent with whatever generated `flip`/`anchor`/`is_up`. For CLOSE
    this reduces exactly to the original. Returns (fills, pos, pend_pos) -- pend_pos is what
    downstream E10 aggregation actually consumes (see M3's REPORT.md for why this matters)."""
    n = len(bars)
    close = bars["close"].to_numpy(); open_ = bars["open"].to_numpy()
    high = bars["high"].to_numpy(); low = bars["low"].to_numpy()
    last_of_sess = bars["is_last_of_sess"].to_numpy()
    times = bars["time"].to_numpy()

    pos = np.zeros(n, dtype=np.int8)
    pend_pos = np.zeros(n, dtype=np.int8)
    fills = []
    p = 0
    pending = 0

    for t in range(n):
        if pending != 0:
            if pending == 1:
                px = sm._fill(open_[t], high[t], low[t], +1); p = 1
                fills.append((t, times[t], "Long", "Buy", px, p))
            elif pending == -1:
                px = sm._fill(open_[t], high[t], low[t], -1); p = -1
                fills.append((t, times[t], "Short", "SellShort", px, p))
            elif pending == -2:
                px = sm._fill(open_[t], high[t], low[t], -1); p = 0
                fills.append((t, times[t], "L-SolarExit", "Sell", px, p))
            elif pending == 2:
                px = sm._fill(open_[t], high[t], low[t], +1); p = 0
                fills.append((t, times[t], "S-SolarExit", "BuyToCover", px, p))
            pending = 0

        if t >= bars_required:
            if mode == "CLOSE":
                test_exit_up, test_exit_dn = close[t], close[t]
            elif mode == "HILO_RAW":
                test_exit_up, test_exit_dn = low[t], high[t]
            else:  # CLOSE_CONFIRMED
                test_exit_up, test_exit_dn = close[t], close[t]
            xl = anchor[t] - s_eff[t] if is_up[t] else anchor[t] + s_eff[t]
            test_val = test_exit_up if is_up[t] else test_exit_dn
            decided = False
            if p == 1 and test_val <= xl:
                pending = -2; decided = True
            elif p == -1 and test_val >= xl:
                pending = 2; decided = True
            if not decided and p == 0 and flip[t] != 0 and not last_of_sess[t]:
                pending = 1 if flip[t] > 0 else -1

        if last_of_sess[t] and p != 0:
            side = -1 if p == 1 else +1
            px = sm._fill(open_[t], high[t], low[t], side, at_close=close[t])
            fills.append((t, times[t], "Exit on session close",
                          "Sell" if p == 1 else "BuyToCover", px, 0))
            p = 0
            if pending in (-2, 2):
                pending = 0
        pos[t] = p
        if pending == 1:
            pend_pos[t] = 1
        elif pending == -1:
            pend_pos[t] = -1
        elif pending in (2, -2):
            pend_pos[t] = 0
        else:
            pend_pos[t] = p

    f = pd.DataFrame(fills, columns=["bar", "time", "name", "order_action", "price", "pos_after"])
    f["commission"] = comm_side
    return f, pos, pend_pos


def build_pend_anchor(bars, sigma, mode, vms=None):
    vms = vms or list(sm.VMS)
    close = bars["close"].to_numpy(); high = bars["high"].to_numpy(); low = bars["low"].to_numpy()
    PEND, FLIPS = [], []
    for vm in vms:
        is_up, flip, s_eff, anchor = member_states_anchor(close, high, low, sigma, float(vm), mode)
        fills, pos, pend = member_trades_anchor(bars, is_up, flip, s_eff, anchor, mode)
        PEND.append(pend); FLIPS.append(flip)
    return np.column_stack(PEND), np.column_stack(FLIPS)


def verify_parity(bars, sigma, vms=None):
    close = bars["close"].to_numpy(); high = bars["high"].to_numpy(); low = bars["low"].to_numpy()
    vms = vms or list(sm.VMS)
    all_ok = True
    detail = []
    for vm in vms:
        is_up0, flip0, s_eff0, anchor0 = sm.member_states(close, sigma, float(vm))
        _, pos0, pend0 = sm.member_trades(bars, is_up0, flip0, s_eff0, anchor0)
        is_up1, flip1, s_eff1, anchor1 = member_states_anchor(close, high, low, sigma, float(vm), "CLOSE")
        _, pos1, pend1 = member_trades_anchor(bars, is_up1, flip1, s_eff1, anchor1, "CLOSE")
        ok = bool(np.array_equal(pos0, pos1) and np.array_equal(pend0, pend1)
                  and np.array_equal(is_up0, is_up1) and np.array_equal(flip0, flip1)
                  and np.allclose(s_eff0, s_eff1) and np.allclose(anchor0, anchor1))
        detail.append({"vol_mult": vm, "PASS": ok})
        all_ok = all_ok and ok
    return all_ok, detail
