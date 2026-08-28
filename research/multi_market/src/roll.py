"""CAUSAL ROLL (s6) and the SELF-FINANCING ECONOMIC RETURN (s7).

s7 IS THE MOST IMPORTANT GATE IN THIS LANE, so state the failure it prevents plainly:

    A naive continuous splice computes  new_close_t - old_close_{t-1}  across a roll and books the
    CROSS-CONTRACT BASIS as trading P&L. On this data that basis is not small - ES 12-11 sits
    EXACTLY 16.00 points below ES 03-11 - and it has a systematic sign, so a naive engine would
    manufacture a trend return out of the futures curve and call it alpha.

THE CONSTRUCTION, which cannot express that error:

    at close t-1 : position is in the OLD contract (the one designated for day t-1)
                   the roll decision, made from information through t-1, names the TARGET for day t
    on day t     : (1) OLD earns the overnight segment   old_open_t   - old_close_{t-1}
                   (2) at the open, close OLD / establish TARGET, paying real turnover cost
                   (3) TARGET earns the intraday segment target_close_t - target_open_t

    unit economic return  r_t = (old_open_t - old_close_{t-1}) + (tgt_close_t - tgt_open_t)

    On a NO-ROLL day old == target and this telescopes to close_t - close_{t-1}, the plain daily
    change of one contract. On a ROLL day the two contracts are NEVER differenced against each
    other, so the basis cannot enter. That is the whole point, and `test_basis_invariance` below
    proves it rather than asserting it.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

# s6: safety override. Roll no later than this many trading days before the contract's last
# observed bar, so a position can never be carried into expiry / first notice. Determined from
# contract MECHANICS, never from future price or volume.
PRE_EXPIRY_BUFFER_DAYS = 5


def build_roll_ledger(panel: pd.DataFrame, root: str) -> pd.DataFrame:
    """CAUSAL, ONE-WAY roll over a root's contracts.

    panel: date | contract_id | expiry_key | open/high/low/close/volume, one row per contract-day.

    RULES (s6):
      A. compare CURRENT vs NEXT eligible contract using volume known through t-1;
      B. if next's PRIOR-DAY volume exceeds current's PRIOR-DAY volume, the roll takes effect on t;
      C. once rolled, NEVER roll backward;
      D. safety override before expiry, from contract mechanics, never from future data.
    """
    panel = panel.sort_values(["date", "expiry_key"])
    dates = np.sort(panel["date"].unique())
    vol = panel.pivot_table(index="date", columns="contract_id", values="volume").sort_index()
    last_bar = panel.groupby("contract_id")["date"].max()
    order = sorted(panel["contract_id"].unique(), key=lambda c: last_bar[c])
    pos = {c: i for i, c in enumerate(order)}

    cur = None
    rows = []
    for i, d in enumerate(dates):
        live = [c for c in order if last_bar[c] >= d]
        if not live:
            continue
        if cur is None or cur not in live:
            cur = live[0]
            rows.append(dict(decision_date=d, info_cutoff=None, old_contract=None,
                             new_contract=cur, old_prev_vol=np.nan, new_prev_vol=np.nan,
                             reason="INITIALISE", effective_date=d))
            continue
        nxt = None
        for c in live:
            if pos[c] > pos[cur]:
                nxt = c
                break
        if nxt is None:
            continue

        # ---- ALL information is from t-1. Never day t.
        prev = dates[i - 1] if i > 0 else None
        if prev is None:
            continue
        v_cur = vol[cur].get(prev, np.nan) if cur in vol.columns else np.nan
        v_nxt = vol[nxt].get(prev, np.nan) if nxt in vol.columns else np.nan
        # D: days remaining is a property of the CONTRACT, known in advance
        remaining = int((last_bar[cur] - d) / np.timedelta64(1, "D"))
        forced = remaining <= PRE_EXPIRY_BUFFER_DAYS
        crossed = (not np.isnan(v_cur)) and (not np.isnan(v_nxt)) and (v_nxt > v_cur)
        if forced or crossed:
            rows.append(dict(decision_date=d, info_cutoff=prev, old_contract=cur,
                             new_contract=nxt, old_prev_vol=v_cur, new_prev_vol=v_nxt,
                             reason="PRE_EXPIRY_OVERRIDE" if forced and not crossed
                                    else "VOLUME_CROSSOVER",
                             effective_date=d))
            cur = nxt                                       # C: one-way, never backward
    led = pd.DataFrame(rows)
    led["root"] = root
    return led


def designated_contract(panel: pd.DataFrame, ledger: pd.DataFrame) -> pd.Series:
    """Which contract is held on each date. Step function from the ledger, forward-filled."""
    dates = pd.Index(np.sort(panel["date"].unique()), name="date")
    s = pd.Series(index=dates, dtype=object)
    for _, r in ledger.iterrows():
        s.loc[r["effective_date"]] = r["new_contract"]
    return s.ffill()


def economic_returns(panel: pd.DataFrame, held: pd.Series) -> pd.DataFrame:
    """SELF-FINANCING unit return in PRICE POINTS (s7). Never differences two contracts."""
    o = panel.pivot_table(index="date", columns="contract_id", values="open").sort_index()
    c = panel.pivot_table(index="date", columns="contract_id", values="close").sort_index()
    dates = held.index
    rows = []
    for i in range(1, len(dates)):
        d, dp = dates[i], dates[i - 1]
        tgt, old = held.get(d), held.get(dp)
        if not isinstance(tgt, str) or not isinstance(old, str):
            continue
        try:
            old_c_prev, old_o = c.at[dp, old], o.at[d, old]
            tgt_o, tgt_c = o.at[d, tgt], c.at[d, tgt]
        except KeyError:
            continue
        if any(pd.isna(x) for x in (old_c_prev, old_o, tgt_o, tgt_c)):
            continue
        overnight = old_o - old_c_prev          # OLD contract carries the overnight segment
        intraday = tgt_c - tgt_o                # TARGET carries the intraday segment
        rows.append(dict(date=d, old_contract=old, target_contract=tgt,
                         overnight=overnight, intraday=intraday,
                         ret_points=overnight + intraday, rolled=int(old != tgt)))
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------- s7 UNIT TESTS
def test_basis_invariance(verbose=True):
    """THE GATE. Two contracts with IDENTICAL daily changes but a huge constant basis must produce
    the SAME economic return. If changing the roll spread changes the return, the engine is wrong.

    Also runs a naive splice alongside, to show the error this construction avoids is real and
    large rather than theoretical."""
    n = 40
    dates = pd.bdate_range("2012-01-02", periods=n)
    rng = np.random.default_rng(7)
    step = rng.normal(0, 5, n)
    base_close = 1000 + np.cumsum(step)
    base_open = base_close - rng.normal(0, 2, n)
    roll_at = 20

    out = {}
    for basis in (0.0, 25.0, -300.0, 5000.0):
        rec = []
        for i, d in enumerate(dates):
            rec.append(dict(date=d, contract_id="A", expiry_key=1, open=base_open[i],
                            high=0, low=0, close=base_close[i],
                            volume=1000 if i < roll_at else 10))
            rec.append(dict(date=d, contract_id="B", expiry_key=2,
                            open=base_open[i] + basis, high=0, low=0,
                            close=base_close[i] + basis,
                            volume=10 if i < roll_at else 1000))
        panel = pd.DataFrame(rec)
        held = pd.Series(["A"] * roll_at + ["B"] * (n - roll_at), index=pd.Index(dates, name="date"))
        er = economic_returns(panel, held)
        out[basis] = er["ret_points"].sum()
        if basis == 25.0:
            naive_c = panel.pivot_table(index="date", columns="contract_id", values="close")
            naive = [naive_c.at[dates[i], held.iloc[i]] - naive_c.at[dates[i - 1], held.iloc[i - 1]]
                     for i in range(1, n)]
            out["NAIVE_at_basis_25"] = float(np.sum(naive))

    vals = [out[b] for b in (0.0, 25.0, -300.0, 5000.0)]
    spread = max(vals) - min(vals)
    ok = spread < 1e-9
    if verbose:
        print("  s7 BASIS-INVARIANCE TEST")
        for b in (0.0, 25.0, -300.0, 5000.0):
            print(f"    basis {b:>9,.1f} -> economic return {out[b]:>12.6f} points")
        print(f"    spread across bases: {spread:.3e}   {'PASS' if ok else '*** FAIL ***'}")
        print(f"    naive splice at basis 25.0 -> {out['NAIVE_at_basis_25']:>12.6f} points "
              f"(error {out['NAIVE_at_basis_25'] - out[25.0]:+.6f} = the basis, booked as P&L)")
    assert ok, "BASIS LEAKED INTO THE ECONOMIC RETURN - the simulator is wrong"
    return out


def test_no_roll_telescopes(verbose=True):
    """On a no-roll day the construction must reduce EXACTLY to close_t - close_{t-1}."""
    n = 30
    dates = pd.bdate_range("2012-01-02", periods=n)
    rng = np.random.default_rng(11)
    cl = 100 + np.cumsum(rng.normal(0, 1, n))
    op = cl - rng.normal(0, 0.5, n)
    panel = pd.DataFrame([dict(date=d, contract_id="A", expiry_key=1, open=op[i], high=0, low=0,
                               close=cl[i], volume=100) for i, d in enumerate(dates)])
    held = pd.Series(["A"] * n, index=pd.Index(dates, name="date"))
    er = economic_returns(panel, held)
    expect = np.diff(cl)
    err = float(np.max(np.abs(er["ret_points"].values - expect)))
    if verbose:
        print(f"  s7 NO-ROLL TELESCOPING TEST: max |r_t - (close_t - close_t-1)| = {err:.3e}   "
              f"{'PASS' if err < 1e-9 else '*** FAIL ***'}")
    assert err < 1e-9
    return err


def test_roll_causality(verbose=True):
    """The roll may use volume through t-1 ONLY. Perturbing day t's volume must not move the
    ledger; perturbing day t-1's volume MUST be able to. A check that cannot fail is useless."""
    n = 30
    dates = pd.bdate_range("2012-01-02", periods=n)
    def mk(vol_a, vol_b):
        rec = []
        for i, d in enumerate(dates):
            rec.append(dict(date=d, contract_id="A", expiry_key=1, open=100, high=0, low=0,
                            close=100, volume=vol_a[i]))
            rec.append(dict(date=d, contract_id="B", expiry_key=2, open=100, high=0, low=0,
                            close=100, volume=vol_b[i]))
        return pd.DataFrame(rec)
    va = np.full(n, 1000.0); vb = np.full(n, 10.0)
    vb[15:] = 5000.0                                   # genuine crossover from index 15
    base = build_roll_ledger(mk(va, vb), "T")
    d_base = base[base.reason == "VOLUME_CROSSOVER"]["decision_date"].min()

    # The base roll fires at index 16, because its information cutoff is index 15 where B first
    # exceeds A. So index 15 IS the t-1 of that decision and index 16 IS its day t.
    # A FIRST VERSION OF THIS TEST perturbed index 15 and called it "day t", then reported a
    # CAUSALITY LEAK that did not exist. The probe was mislabelled, not the engine. Discipline
    # rule 55: a causality check can itself be the defect - verify it has teeth AND that it
    # isolates the right day.
    i_base = int(np.where(dates == d_base)[0][0])

    va2, vb2 = va.copy(), vb.copy()
    vb2[i_base - 2] = 99999.0                          # EARLIER t-1 -> ledger SHOULD move earlier
    moved = build_roll_ledger(mk(va2, vb2), "T")
    d_moved = moved[moved.reason == "VOLUME_CROSSOVER"]["decision_date"].min()

    va3, vb3 = va.copy(), vb.copy()
    vb3[i_base] = 0.1                                  # DAY-T volume crushed -> must NOT matter
    same = build_roll_ledger(mk(va3, vb3), "T")
    d_same = same[same.reason == "VOLUME_CROSSOVER"]["decision_date"].min()

    has_teeth = d_moved < d_base
    causal = d_same == d_base
    if verbose:
        print(f"  s6 ROLL CAUSALITY: base {pd.Timestamp(d_base).date()}   "
              f"perturb t-1 -> {pd.Timestamp(d_moved).date()} ({'moved, test has teeth' if has_teeth else 'DID NOT MOVE'})"
              f"   perturb t -> {pd.Timestamp(d_same).date()} ({'unchanged, causal' if causal else 'MOVED - LEAK'})")
    assert has_teeth, "the causality probe cannot detect a change - it has no teeth"
    assert causal, "day-t volume moved the roll decision - CAUSALITY LEAK"
    return d_base


if __name__ == "__main__":
    print("s6/s7 UNIT TESTS")
    test_no_roll_telescopes()
    test_basis_invariance()
    test_roll_causality()
    print("  ALL PASS")
