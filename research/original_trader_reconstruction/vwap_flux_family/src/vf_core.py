"""vf_core: clean-room VWAP Flux cloud (directive v3.0 §14-§18).

Two lifecycle models (VF-ANCHOR incumbent / VF-BLOCK falsification control),
three rail formulas, two price inputs, anchor-age diagnostics. No vendor code.
Rail formula and lifecycle are decided by morphology/unit tests, never PnL.
"""
import numpy as np

DEFAULT_PCTS = (5.0, 25.0, 50.0, 75.0, 95.0)   # trader's Min..Max order
PUBLIC_PCTS = (0.0, 30.0, 50.0, 70.0, 100.0)   # vendor public defaults


def rails_from_population(vals, pcts, formula):
    """vals: sorted (ascending) population of layer VWAPs. Returns len(pcts) rails."""
    v = np.asarray(sorted(vals), float)
    n = len(v)
    out = np.empty(len(pcts))
    for j, p in enumerate(pcts):
        q = p / 100.0
        if formula == "percentile_linear":       # numpy 'linear' convention
            h = q * (n - 1)
            lo = int(np.floor(h)); hi = min(lo + 1, n - 1)
            out[j] = v[lo] + (h - lo) * (v[hi] - v[lo])
        elif formula == "nearest_rank":
            k = max(1, int(np.ceil(q * n))) - 1
            out[j] = v[min(k, n - 1)]
        elif formula == "minmax":                # position within [min,max] span
            out[j] = v[0] + q * (v[-1] - v[0])
        else:
            raise ValueError(formula)
    return out


def vf_levels(time_arr, price, volume, period_min=60, amount=5,
              pcts=DEFAULT_PCTS, lifecycle="anchor", formula="percentile_linear",
              with_meta=False):
    """Compute the 5 rails per bar.

    lifecycle='anchor': every period start a NEW accumulator; all retained
        accumulators keep updating each bar (incumbent).
    lifecycle='block': only the CURRENT period's accumulator updates; completed
        periods freeze (falsification control).
    Layer birth = period boundary on the wall clock (epoch-aligned), matching
    the hourly-anchor convention certified in VF4 for period=60.
    with_meta: also return per-bar anchor ages (bars) aligned to the SORTED
        population order (age-order diagnostics, §18) — metadata only.
    """
    n = len(price)
    t = time_arr.astype("datetime64[s]").astype("int64")
    period_id = t // (period_min * 60)
    lv = np.full((n, len(pcts)), np.nan)
    meta_age = np.full((n, amount), -1, dtype=np.int64) if with_meta else None
    layers = []          # [pv, v, birth_bar]
    cur_pid = None
    for i in range(n):
        pid = period_id[i]
        if pid != cur_pid:
            cur_pid = pid
            layers.append([0.0, 0.0, i])
            if len(layers) > amount:
                layers.pop(0)
        pv_add = price[i] * volume[i]
        if lifecycle == "anchor":
            for a in layers:
                a[0] += pv_add
                a[1] += volume[i]
        else:  # block
            layers[-1][0] += pv_add
            layers[-1][1] += volume[i]
        if len(layers) == amount and all(a[1] > 0 for a in layers):
            vals = [(a[0] / a[1], i - a[2]) for a in layers]
            vals.sort()
            lv[i] = rails_from_population([x[0] for x in vals], pcts, formula)
            if with_meta:
                meta_age[i] = [x[1] for x in vals]
    return (lv, meta_age) if with_meta else lv


def age_concordance(meta_age):
    """§18 diagnostic: Kendall-style concordance between sorted-value order and
    age order per bar (1 = oldest lowest ... , -1 = oldest highest)."""
    n, m = meta_age.shape
    out = np.full(n, np.nan)
    idx = np.arange(m)
    for i in range(n):
        a = meta_age[i]
        if a[0] < 0:
            continue
        conc = 0; tot = 0
        for j in range(m):
            for k in range(j + 1, m):
                if a[j] != a[k]:
                    conc += 1 if (a[j] > a[k]) else -1
                    tot += 1
        out[i] = conc / tot if tot else np.nan
    return out


# ------------------------- deterministic unit tests -------------------------
def _tests():
    # §16 adversarial population: percentile vs minmax must separate sharply
    pop = [100, 101, 102, 103, 140]
    pl = rails_from_population(pop, (75.0,), "percentile_linear")[0]
    nr = rails_from_population(pop, (75.0,), "nearest_rank")[0]
    mm = rails_from_population(pop, (75.0,), "minmax")[0]
    assert abs(pl - 103.0) < 1e-9, pl        # linear: h=3.0 -> exactly v[3]
    assert nr == 103.0, nr                    # ceil(0.75*5)=4 -> v[3]
    assert abs(mm - 130.0) < 1e-9, mm         # 100+0.75*40
    # median
    assert rails_from_population(pop, (50.0,), "percentile_linear")[0] == 102.0
    assert abs(rails_from_population(pop, (50.0,), "minmax")[0] - 120.0) < 1e-9
    # extremes agree across formulas
    for f in ("percentile_linear", "nearest_rank", "minmax"):
        r = rails_from_population(pop, (0.0, 100.0), f)
        assert r[0] == 100.0 and r[1] == 140.0, (f, r)
    # trader pcts on 5 layers, percentile_linear: 95% -> h=3.8 between v[3],v[4]
    r = rails_from_population(pop, DEFAULT_PCTS, "percentile_linear")
    assert abs(r[4] - (103 + 0.8 * 37)) < 1e-9

    # lifecycle separation on synthetic data: constant price then jump
    tmins = np.arange(0, 300, 1)
    tarr = np.array([np.datetime64("2026-01-05T00:00:00") + np.timedelta64(int(m), "m") for m in tmins])
    px = np.where(tmins < 150, 100.0, 200.0)
    vol = np.ones_like(px)
    la = vf_levels(tarr, px, vol, 60, 5, lifecycle="anchor")
    lb = vf_levels(tarr, px, vol, 60, 5, lifecycle="block")
    # at the last bar: anchor layers all contain post-jump prices -> all rails > 100
    assert la[-1, 0] > 100.0
    # block: the two oldest retained blocks are frozen pre-jump -> min rail == 100
    assert abs(lb[-1, 0] - 100.0) < 1e-9
    # anchor rails move every bar after the jump; block moves only current layer
    d_anchor = np.nanmean(np.abs(np.diff(la[200:, 0])))
    d_block = np.nanmean(np.abs(np.diff(lb[200:, 0])))
    assert d_anchor > 0 and d_block == 0.0

    # age concordance metadata sane
    _, ma = vf_levels(tarr, px, vol, 60, 5, lifecycle="anchor", with_meta=True)
    ac = age_concordance(ma)
    assert np.isfinite(ac[-1])
    print("[vf_core] all unit tests PASS")


if __name__ == "__main__":
    _tests()
