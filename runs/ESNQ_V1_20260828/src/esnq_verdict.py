"""ESNQ_V1 gate table, frozen uncertainty, blind-spend admissibility, verdict."""
from __future__ import annotations

import json
import os
import sys

import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(RUN))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "research_sdk"))
import blindguard as BG                                                 # noqa: E402
import blind_spend_power as BSP                                         # noqa: E402
import esnq_batch as B                                                  # noqa: E402

OUT = os.path.join(RUN, "out")
_fh = open(os.path.join(OUT, "esnq_verdict.txt"), "w", encoding="utf-8")


def P(*a):
    print(*a, flush=True)
    print(*a, file=_fh)


d = pd.read_parquet(os.path.join(OUT, "feat_batch.parquet"))
sess = sorted(BG.load_manifest(os.path.join(RUN, "manifests", "ESNQ_DEV_44.csv")))
BG.assert_no_blind_contamination(sess, os.path.join(RUN, "manifests",
                                                    "ESNQ_BLIND_EFFECTIVE_14.csv"))
feats = B.FEATURES
adm = d[d["wait_ok"] & d[feats].notna().all(axis=1)
        & d["long_gross"].notna() & d["short_gross"].notna()].sort_values("t").reset_index(drop=True)
X = np.nan_to_num(adm[feats].values.astype(float), posinf=0, neginf=0)
y = (adm["long_gross"].values + (-adm["short_gross"].values)) / 2.0
ss = adm["session"].values
order = [s for s in sess if s in set(ss)]
folds = B.chrono_folds(order)
mk = lambda: Ridge(alpha=B.RIDGE_ALPHA)                                  # noqa: E731

ix, pr = B.oof(X, y, ss, folds, mk)
sub = adm.iloc[ix]
net, act = B.policy_pnl(pr, sub, 0.0)
sn = pd.Series(net).groupby(sub["session"].values).sum()
sn = sn.reindex([s for s in order if s in sn.index])
mu = float(sn.mean())

P("=" * 112)
P("=== ESNQ_V1 DEVELOPMENT GATE TABLE  (frozen in SPEC/A1 before any result)")
P("=" * 112)
n5, _ = B.policy_pnl(pr, sub, 0.5)
s5 = float(pd.Series(n5).groupby(sub["session"].values).sum().sum())
n10, _ = B.policy_pnl(pr, sub, 1.0)
s10 = float(pd.Series(n10).groupby(sub["session"].values).sum().sum())
pos = sn[sn > 0]
top5 = float(pos.nlargest(5).sum() / pos.sum()) if len(pos) else float("nan")
qs = [float(x.sum()) for x in np.array_split(sn.values, 4)]

# --- X8 declared secondary control: NQ-only information set, identical folds/sample
nqf = ["nq_spread_tk", "nq_rvol_30s", "tod"]
Xn = np.nan_to_num(adm[nqf].values.astype(float), posinf=0, neginf=0)
ixn, prn = B.oof(Xn, y, ss, folds, mk)
nn, an = B.policy_pnl(prn, adm.iloc[ixn], 0.0)
snn = pd.Series(nn).groupby(ss[ixn]).sum()
mu_nq = float(snn.mean())

# numpy bools are NOT `is True` / `is False`. The first version of this table silently dropped
# X1 from the blocking-failure list for exactly that reason. Cast every verdict to a python bool.
_b = lambda v: None if v is None else bool(v)                            # noqa: E731
G = [("X1  joint after-cost OOF net > 0", f"${sn.sum():,.2f}", _b(sn.sum() > 0)),
     ("X2  > 95th pctile refitted session-block null", "NOT RUN - see below", None),
     ("X3  beats activity-matched placebo", "NOT RUN - see below", None),
     ("X4  beats same-trigger mirror", f"${-sn.sum():,.2f} for the mirror", None),
     ("X5  STRESS +0.5tk net > 0", f"${s5:,.2f}", _b(s5 > 0)),
     ("X6  top-5 sessions <= 50% of positive net", f"{100*top5:.1f} %", _b(top5 <= 0.50)),
     ("X7  net > 0 in >= 3 of 4 quartiles", f"{sum(q>0 for q in qs)} of 4",
      _b(sum(q > 0 for q in qs) >= 3)),
     ("X8  NQ-only control (diagnostic, not a gate)", f"${mu_nq:,.2f}/session", None),
     ("X9  ES-pairing mechanism null", "NOT RUN - see below", None)]
P(f"    {'GATE':<48} {'OBSERVED':>26}   VERDICT")
for nm, ob, ok in G:
    v = "PASS" if ok is True else ("*** FAIL ***" if ok is False else "n/a")
    P(f"    {nm:<48} {ob:>26}   {v}")
blocking_fail = [nm for nm, _, ok in G if ok is False]
P("")
P("    X2/X3/X9 NOT RUN, and the reason is not budget:")
P("      X1 FAILS. A refitted null, an activity placebo and a cross-market mechanism null all ask")
P("      'is this POSITIVE result real / genuinely cross-market?'. There is no positive result to")
P("      attribute. Running them on a losing object would answer a question nobody asked, and a")
P("      null percentile for a negative strategy cannot rescue it. The object closes on X1.")

P("")
P("=" * 112)
P("=== FROZEN UNCERTAINTY (A3-4): circular block bootstrap on the session nets")
P("=" * 112)
bs = BSP.mu_claim_block_bootstrap(sn.values)
for k in ("n_sessions", "block_length", "B", "seed", "percentile", "mu_hat_dev",
          "bootstrap_mean_of_means", "bootstrap_sd", "lower_bound_raw", "mu_claim",
          "distinct_replicate_values"):
    P(f"    {k:<28} {bs[k]}")
lo95 = float(np.percentile(
    [np.mean(np.random.default_rng(BSP.BOOT_SEED + i).choice(sn.values, len(sn)))
     for i in range(2000)], 5))
P(f"    (diagnostic only) IID session bootstrap 5th pctile  ${lo95:,.2f}")

P("")
P("=" * 112)
P("=== BLIND-SPEND ADMISSIBILITY  (A2 s7 + A3 s2/s4)")
P("=" * 112)
au = BSP.authorize(bs["mu_hat_dev"], 0.0, gates_pass=not blocking_fail,
                   mechanism_null_pass=False, causality_pass=True, parity_pass=True,
                   stress_pass=s5 > 0)
P(f"    EFFECTIVE blind n            {BSP.N_BLIND}")
P(f"    sigma_blind (frozen)         ${BSP.SIGMA_PROXY:,.2f}/session")
P(f"    SE_blind                     ${BSP.se_blind():,.2f}/session")
P(f"    MDE(80% power)               ${(1.6448536269514722+0.8416212335729143)*BSP.se_blind():,.2f}/session")
P(f"    mu_hat_dev                   ${bs['mu_hat_dev']:,.2f}/session")
P(f"    mu_claim (10th pctile, frozen)  ${bs['mu_claim']:,.2f}/session")
P(f"    blind power at mu_claim      {BSP.power_vs_zero(bs['mu_claim']):.3f}   required >= 0.80")
P("")
for k, v in au["conditions"].items():
    P(f"    {k:<32} {v}")
P(f"    >>> DECISION: {au['decision']}   ({au['status']})")

verdict = ("NO CANDIDATE" if blocking_fail else
           ("DEVELOPMENT-SUPPORTED / BLIND-SPEND-ADMISSIBLE" if au["decision"] == "AUTHORIZED"
            else "DEVELOPMENT-SUPPORTED / BLIND-UNDERPOWERED"))
P("")
P("=" * 112)
P(f"=== VERDICT: {verdict}")
P("=" * 112)
P(f"    blocking gate failures: {blocking_fail if blocking_fail else 'none'}")
P("    ESNQ_V1 is CLOSED at its exact tested scope. No 30s/15s/120s rescue, no feature addition,")
P("    no subset, no GBM, no nonlinear model, no event/TOD/volatility filter, no ES-only variant,")
P("    no alternative pairing null, no threshold relaxation. A genuinely different future")
P("    cross-market formulation requires a FRESH EVI adjudication and fresh preregistration.")
json.dump({"verdict": verdict, "blocking_failures": blocking_fail,
           "gates": [{"gate": n, "observed": o, "pass": (None if ok is None else bool(ok))} for n, o, ok in G],
           "mu_hat_dev": bs["mu_hat_dev"], "mu_claim": bs["mu_claim"],
           "blind_power_at_mu_claim": BSP.power_vs_zero(bs["mu_claim"]),
           "blind_effective_n": int(BSP.N_BLIND), "blind_decision": au["decision"],
           "bootstrap": {k: (float(v) if isinstance(v,(int,float,np.floating)) else v) for k,v in bs.items()}, "total_net": float(sn.sum()), "net_per_session": mu,
           "stress_05": s5, "stress_10": s10, "nq_only_control_per_session": mu_nq},
          open(os.path.join(OUT, "esnq_verdict.json"), "w", encoding="utf-8"), indent=2)
_fh.close()
