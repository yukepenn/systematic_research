"""LANE A step 1 - THE LAST-ONLY DATA CONTRACT.  BLOCKING: no feature may be fitted until this
certifies.  Directive s4B.

THE PROBLEM MS01A LEFT BEHIND.  81.1 % of adjacent tick events share a millisecond timestamp, and
exchange sequence INSIDE one millisecond is not recoverable from this export. So any feature that
walks rows in file order inside an equal-timestamp bucket is reading an ARTIFACT OF THE EXPORT, not
the market. The classic tick rule is exactly such a feature: it signs a trade by comparing it to
the previous ROW, and inside a tied millisecond "previous row" is arbitrary.

THE SOLUTION, BY CONSTRUCTION rather than by hoping.  Collapse each DISTINCT TIMESTAMP into one
bucket using only order-invariant aggregates, then build every feature from the SEQUENCE OF
BUCKETS - which has a well-defined order because its timestamps are distinct by construction.

    bucket volume       sum(v)                 order-invariant
    bucket vwap         sum(p*v)/sum(v)        order-invariant
    bucket trades       count                  order-invariant
    bucket hi / lo      max(p) / min(p)        order-invariant
    bucket n_prices     nunique(p)             order-invariant

    signed flow         sign(vwap_t - vwap_{t-1}) * volume_t     <- prior DISTINCT timestamp,
                                                                    which is s4B clause 2

That satisfies s4B clause 2 by construction. This script then VERIFIES it empirically anyway,
because "it should be invariant" is an argument and the directive asks for a test.

NOTHING HERE READS THE 141-SESSION BLIND POOL. Discovery sessions only.
"""
from __future__ import annotations

import glob
import os
import re

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

ROOT = (r"D:\OneDrive - Washington University in St. Louis\TradingResearch"
        r"\systematic_research")
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(HERE, "out")
os.makedirs(OUT, exist_ok=True)
V2 = os.path.join(ROOT, "research/data_microstructure_v2/raw/NQ")
V1 = os.path.join(ROOT, "research/scalping_lab/substrate/raw/NQ")
BLIND = os.path.join(ROOT, "runs/MICRO_DISCOVERY_CONFIRMATION_SPLIT/out/"
                           "MICRO_BLIND_CONFIRMATION_POOL.csv")
SEED = 20260827
NTEST = 12
_fh = open(os.path.join(OUT, "contract.txt"), "w", encoding="utf-8")


def P(*a):
    print(*a, flush=True)
    print(*a, file=_fh)


def load_last(path):
    """Last events only (bip == 0), stable-sorted by time so the ORIGINAL FILE ORDER survives
    inside ties - the permutation test needs a real baseline to perturb."""
    t = pq.read_table(path, columns=["bip", "time", "price", "volume"])
    d = t.to_pandas()
    d = d[d["bip"] == 0].drop(columns=["bip"])
    return d.sort_values("time", kind="stable").reset_index(drop=True)


def buckets(d):
    """Collapse to DISTINCT-TIMESTAMP buckets using ORDER-INVARIANT aggregates only."""
    g = d.groupby("time", sort=True)
    pv = (d["price"] * d["volume"]).groupby(d["time"]).sum()
    v = g["volume"].sum()
    return pd.DataFrame({"vwap": pv / v, "vol": v, "trades": g.size(),
                         "hi": g["price"].max(), "lo": g["price"].min(),
                         "nprice": g["price"].nunique()}).reset_index()


def permute_within_ms(d, rng):
    """Randomly permute rows INSIDE each equal-timestamp group, leaving group order intact.
    This is the adversary s4B specifies: a feature that moves under it was reading export row
    order and calling it trade sequence."""
    k = rng.random(len(d))
    order = np.lexsort((k, d["time"].values.astype("int64")))
    return d.iloc[order].reset_index(drop=True)


def feat_bucket(d):
    """CERTIFIED CONSTRUCTION - everything derived from distinct-timestamp buckets."""
    b = buckets(d)
    w = b["vwap"].values
    v = b["vol"].values.astype(float)
    dv = np.sign(np.diff(w, prepend=w[0])) * v          # prior DISTINCT timestamp
    return dict(n_buckets=float(len(b)), tot_vol=float(v.sum()),
                n_trades=float(b["trades"].sum()),
                signed_flow=float(dv.sum()), abs_flow=float(np.abs(dv).sum()),
                displacement=float(w[-1] - w[0]),
                realized_vol=float(np.sqrt(np.sum(np.diff(w) ** 2))),
                rng_hi_lo=float(b["hi"].max() - b["lo"].min()),
                n_distinct_px=float(pd.unique(d["price"]).size),
                vol_concentration=float((v ** 2).sum() / (v.sum() ** 2)))


def feat_rowwise(d):
    """NAIVE CONSTRUCTION - the one the directive warns about. Walks rows in FILE ORDER, so its
    tick rule and its first/last prices are decided by export ordering inside tied milliseconds."""
    p = d["price"].values
    v = d["volume"].values.astype(float)
    s = np.sign(np.diff(p, prepend=p[0])) * v           # tick rule on ROWS, not timestamps
    return dict(rowwise_signed_flow=float(s.sum()), rowwise_abs_flow=float(np.abs(s).sum()),
                rowwise_displacement=float(p[-1] - p[0]),
                rowwise_realized_vol=float(np.sqrt(np.sum(np.diff(p) ** 2))),
                rowwise_uptick_frac=float(np.mean(np.diff(p, prepend=p[0]) > 0)))


def main():
    blind = set(pd.read_csv(BLIND)["session"])
    files = {}
    for dd, tag in ((V2, "v2"), (V1, "v1")):
        for f in sorted(glob.glob(os.path.join(dd, "s*.parquet"))):
            s = re.match(r"^s(\d{8})", os.path.basename(f)).group(0)
            if s in blind:
                continue                                  # never touch the blind pool
            files.setdefault(s, (f, tag))                 # v2 wins where both exist
    sess = sorted(files)
    P("=" * 100)
    P("=== LANE A step 1 - LAST-ONLY DATA CONTRACT.  BLOCKING GATE.")
    P("=== Discovery sessions only. The 141-session blind pool is NOT opened.")
    P("=" * 100)
    P(f"    discovery sessions available   {len(sess)}   "
      f"(v2 {sum(1 for s in sess if files[s][1] == 'v2')}, "
      f"v1 {sum(1 for s in sess if files[s][1] == 'v1')})")
    P(f"    blind sessions excluded        {len(blind)}")

    rng = np.random.default_rng(SEED)
    pick = [sess[i] for i in np.linspace(0, len(sess) - 1, NTEST).astype(int)]
    P("")
    P("=" * 100)
    P(f"=== WITHIN-MILLISECOND PERMUTATION-INVARIANCE TEST on {NTEST} sessions")
    P("=== Each feature computed on the natural order, then on a random permutation INSIDE each")
    P("=== tied-timestamp group. A feature that moves was reading export row order.")
    P("=" * 100)
    rows = []
    for s in pick:
        f, tag = files[s]
        d = load_last(f)
        nms = d["time"].nunique()
        tie = 1.0 - nms / len(d)
        a = {**feat_bucket(d), **feat_rowwise(d)}
        b = {**feat_bucket(permute_within_ms(d, rng)), **feat_rowwise(permute_within_ms(d, rng))}
        for kk in a:
            rows.append(dict(session=s, tag=tag, tie_frac=tie, feature=kk, base=a[kk],
                             perm=b[kk], abs_diff=abs(b[kk] - a[kk]),
                             rel_diff=abs(b[kk] - a[kk]) / max(abs(a[kk]), 1e-9)))
        P(f"    {s} [{tag}]  {len(d):>9,} Last events  {nms:>9,} distinct ms  "
          f"tie fraction {tie:6.1%}")
    r = pd.DataFrame(rows)
    r.to_csv(os.path.join(OUT, "permutation_test.csv"), index=False)

    P("")
    P(f"    {'feature':<24}{'max |abs diff|':>16}{'max rel diff':>15}{'moved':>12}   VERDICT")
    P("    " + "-" * 84)
    verdict = {}
    for kk, g in r.groupby("feature", sort=False):
        ok = bool(g["rel_diff"].max() <= 1e-12)
        verdict[kk] = ok
        P(f"    {kk:<24}{g['abs_diff'].max():>16,.4f}{g['rel_diff'].max():>15.3e}"
          f"{int((g['rel_diff'] > 1e-12).sum()):>6}/{len(g):<5}   "
          f"{'INVARIANT - ADMISSIBLE' if ok else '*** MOVES - DROP ***'}")

    P("")
    P("=" * 100)
    P("=== VERDICT")
    P("=" * 100)
    good = [k for k, o in verdict.items() if o]
    bad = [k for k, o in verdict.items() if not o]
    P(f"    ADMISSIBLE ({len(good)}): " + ", ".join(good))
    P(f"    REJECTED   ({len(bad)}): " + ", ".join(bad))
    P("")
    P("    The rejected list is the point. Those are the features a Last-only study would")
    P("    NATURALLY write - a tick-rule signed flow, an uptick fraction, a first-to-last")
    P("    displacement - and on THIS export they are partly a function of ROW ORDER INSIDE A")
    P("    MILLISECOND, which carries no exchange information. They are not repaired. They are")
    P("    replaced by the bucket construction, which is invariant BY CONSTRUCTION and is now")
    P("    also invariant BY MEASUREMENT.")
    pd.DataFrame(dict(feature=list(verdict), admissible=list(verdict.values()))).to_csv(
        os.path.join(OUT, "admissible_features.csv"), index=False)
    _fh.close()


if __name__ == "__main__":
    main()
