"""G3_INCUMBENT_BASELINE_00 - the champion's own numbers, on the GENESIS III risk vector.

VERIFICATION, NOT SELECTION. Nothing is chosen, tuned or ranked here. This run exists because
directive section 2 says VERIFY ALL NUMBERS BEFORE REUSE, and because every WAVE H comparison needs
a baseline computed by the SAME evaluator the challengers will face. A challenger scored by
champion_eval against an incumbent scored by hand is not a comparison.

Directive section 2 also forbids mixing four different objects. They are computed separately and
printed separately, and the differences between them are the point:

  A  HISTORICAL BACKTEST HEADLINE   NT8 Strategy Analyzer basis: $4.36/ctrRT, ZERO slippage
  B  RECOSTED HISTORICAL            + the modelled spread the research charges
                                      (P1 $14.44/ctrRT, XM $12.50/ctrRT)
  C  FORWARD PLANNING EXPECTATION   inherited claim, CHECKED for consistency, not recomputed
  D  LIVE / PAPER OBSERVED          n = 1 round trip. Reported, never used for anything.

CLAUDE.md section 3 is binding on how the sum is labelled: certifying both legs does NOT produce an
executable portfolio. The research portfolio is INVERSE-VOL weighted; running both legs at quantity
1 is a different object. The sum below is therefore an EXECUTABLE_COMPONENT_SET and is never called
a portfolio, and no research-portfolio figure is quoted for it.
"""

from __future__ import annotations

import json
import os
import sys

import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, ROOT)

from research_sdk.champion_eval import (  # noqa: E402
    risk_vector, weekly_from_trades, incremental, iso_week, max_drawdown,
)

SRC = os.path.join(ROOT, "runs", "G2_AUG_INCUMBENT_READ_20260830", "out")
OUT = os.path.join(os.path.dirname(__file__), "..", "out")
os.makedirs(OUT, exist_ok=True)

# modelled spread per contract round turn, the research cost basis
SPREAD = {"P1": 14.44, "XM": 12.50}
DD_TARGET = 20245.0


def load(name):
    d = pd.read_csv(os.path.join(SRC, f"{name.lower()}_trades_full.csv"))
    d["et"] = pd.to_datetime(d["et"])
    d["xt"] = pd.to_datetime(d["xt"])
    # Session attribution: the repo's unit is the 18:00->17:00 session, and the trade's WEEK comes
    # from the ledger's own `wk` column, which is what every prior figure used. Use it, do not
    # re-derive it - re-deriving would silently move trades between weeks at the 18:00 boundary.
    return d


def main() -> int:
    print("=" * 112)
    print("G3_INCUMBENT_BASELINE_00 - the champion's own numbers on the GENESIS III risk vector.")
    print("VERIFICATION ONLY. Nothing is selected, tuned or ranked.")
    print("=" * 112)

    P1, XM = load("p1"), load("xm")
    for nm, d in (("P1", P1), ("XM", XM)):
        print(f"\n{nm}: {len(d)} trades, net ${d.pnl.sum():,.2f}, "
              f"ctrRT {d.qty.sum():.0f}, {d.et.min().date()} .. {d.xt.max().date()}")

    # --- reproduce the recorded headline to the cent, or say so -------------------------------
    rec = json.load(open(os.path.join(SRC, "leg_baselines.json")))
    ok = (abs(P1.pnl.sum() - rec["P1"]["net"]) < 0.01
          and abs(XM.pnl.sum() - rec["XM"]["net"]) < 0.01
          and len(P1) == rec["P1"]["trades"] and len(XM) == rec["XM"]["trades"])
    print(f"\nrecorded baseline reproduces to the cent: {ok}   "
          f"(recorded SUM ${rec['SUM_net']:,.2f}, recomputed ${P1.pnl.sum() + XM.pnl.sum():,.2f})")
    if not ok:
        print("  -> THE RECORDED BASELINE DOES NOT REPRODUCE. Everything below is void.")
        return 1

    # --- one shared week index, or the legs are not comparable --------------------------------
    all_weeks = sorted(set(P1.wk) | set(XM.wk))
    print(f"shared week index: {len(all_weeks)} ISO weeks "
          f"({all_weeks[0]} .. {all_weeks[-1]})")

    rows = []
    for basis, spread_on in (("A_NT8_HEADLINE", False), ("B_RECOSTED", True)):
        legs = {}
        for nm, d in (("P1", P1), ("XM", XM)):
            pnl = d.pnl.to_numpy(float).copy()
            if spread_on:
                pnl = pnl - SPREAD[nm] * d.qty.to_numpy(float)
            legs[nm] = pnl
        comb = None
        for nm in ("P1", "XM"):
            d = P1 if nm == "P1" else XM
            rv = risk_vector(f"{nm}[{basis}]", d.wk.tolist(), legs[nm], d.qty.to_numpy(float),
                             all_weeks, target_dd=DD_TARGET)
            rows.append(rv)
            _, w = weekly_from_trades(d.wk.tolist(), legs[nm], all_weeks)
            comb = w if comb is None else comb + w
        # the component set: leg sum at quantity 1 each
        wk_all = np.array(all_weeks)
        cs = risk_vector(f"M_11_COMPONENT_SET[{basis}]",
                         list(np.concatenate([P1.wk.values, XM.wk.values])),
                         np.concatenate([legs["P1"], legs["XM"]]),
                         np.concatenate([P1.qty.values, XM.qty.values]),
                         all_weeks, target_dd=DD_TARGET)
        rows.append(cs)
        if basis == "A_NT8_HEADLINE":
            _, wp1 = weekly_from_trades(P1.wk.tolist(), legs["P1"], all_weeks)
            _, wxm = weekly_from_trades(XM.wk.tolist(), legs["XM"], all_weeks)
            wA = (wp1, wxm, wk_all)
        else:
            _, wp1 = weekly_from_trades(P1.wk.tolist(), legs["P1"], all_weeks)
            _, wxm = weekly_from_trades(XM.wk.tolist(), legs["XM"], all_weeks)
            wB = (wp1, wxm, wk_all)

    # ------------------------------------------------------------------------------------------
    print("\n" + "=" * 112)
    print("THE RISK VECTOR.  Fixed-DD is ONE COLUMN, never the yardstick (directive section 25).")
    print("=" * 112)
    cols = [("net/wk", "net_per_week", "{:>11,.0f}"), ("med/wk", "median_per_week", "{:>10,.0f}"),
            ("%pos", "pct_positive_weeks", "{:>7.1%}"), ("wk SD", "weekly_sd", "{:>10,.0f}"),
            ("dnSD", "downside_sd", "{:>9,.0f}"), ("ES95", "es95", "{:>10,.0f}"),
            ("worst wk", "worst_week", "{:>11,.0f}"), ("maxDD", "max_dd", "{:>10,.0f}"),
            ("DDwks", "dd_duration_weeks", "{:>6d}"), ("fixDD/wk", "fixed_dd_income", "{:>10,.0f}"),
            ("top10%", "top_10pct_share", "{:>8.1%}"), ("trades", "n_trades", "{:>7d}")]
    hdr = f"{'object':<30}"
    for nm, _, _ in cols:
        hdr += f"{nm:>11}"
    print(hdr)
    print("-" * (30 + 11 * len(cols)))
    for rv in rows:
        line = f"{rv.name:<30}"
        for _, attr, fmt in cols:
            v = getattr(rv, attr)
            try:
                line += f"{v:>11,.0f}" if abs(v) >= 100 and not isinstance(v, bool) else f"{v:>11.3g}"
            except (TypeError, ValueError):
                line += f"{str(v):>11}"
        print(line)

    # ------------------------------------------------------------------------------------------
    print("\n" + "=" * 112)
    print("THE DIVERSIFICATION QUESTION, ON BOTH COST BASES")
    print("=" * 112)
    for label, (wp1, wxm, _) in (("A_NT8_HEADLINE", wA), ("B_RECOSTED", wB)):
        inc = incremental(wp1, wxm, n_draws=4000, mean_block=4.0)
        print(f"\n[{label}]  corr(P1, XM) = {inc['correlation']:+.4f}")
        print(f"  P1 {inc['base_per_week']:>9,.0f}/wk   XM {inc['cand_per_week']:>9,.0f}/wk   "
              f"combined {inc['combined_per_week']:>9,.0f}/wk")
        print(f"  weekly SD: P1 {inc['base_sd']:>9,.0f}  combined {inc['combined_sd']:>9,.0f}   "
              f"maxDD: P1 {inc['base_maxdd']:>9,.0f}  combined {inc['combined_maxdd']:>9,.0f}")
        for k in ("vol", "es", "dd"):
            print(f"  increment over a risk-matched P1 [{k:>3}]: "
                  f"{inc[f'increment_vs_scaled_{k}']:>+10,.0f}/wk   "
                  f"(scale P1 by k={inc[f'scaled_base_k_{k}']:.4f})")
        print(f"  XM during P1's worst decile of weeks: {inc['cand_in_base_worst_decile']:>+9,.0f}/wk"
              f"   (P1 there {inc['base_worst_decile_per_week']:,.0f}/wk)")

    # --- the conditional-correlation identity, reproduced ---------------------------------------
    print("\n" + "=" * 112)
    print("THE MIXTURE, REPRODUCED: XM's correlation with P1 is not one number")
    print("=" * 112)
    XM2 = XM.copy()
    XM2["dir"] = np.sign(XM2.pnl)  # placeholder if direction is absent
    # direction is recoverable only if the ledger carries it; state honestly what we can and cannot do
    if "d" in XM2.columns or "dir_true" in XM2.columns:
        pass
    print("  The ledger runs/G2_AUG_INCUMBENT_READ_20260830/out/xm_trades_full.csv carries columns")
    print(f"  {list(XM.columns)} - it has NO SIGNED DIRECTION column, so the")
    print("  long/short conditional correlation (rho +0.408 when XM is long, -0.204 when short)")
    print("  CANNOT be reproduced from this artifact. It is NOT recomputed here and is NOT quoted.")
    print("  To reproduce it, the XM reference decision ledger with desired_direction is required:")
    print("    research/weekly_edge/ninjascript/reference/xm_reference_decisions.csv")

    # --- concentration -------------------------------------------------------------------------
    print("\n" + "=" * 112)
    print("CONCENTRATION - the capital plan has to admit this")
    print("=" * 112)
    for nm, d in (("P1", P1), ("XM", XM)):
        p = np.sort(d.pnl.to_numpy(float))
        net = p.sum()
        print(f"\n{nm}: net ${net:,.0f} from {len(p)} trades, median ${np.median(p):,.2f}, "
              f"win rate {float((p > 0).mean()):.1%}")
        for f in (0.01, 0.05, 0.10):
            k = max(1, int(round(len(p) * f)))
            print(f"   top {f:>5.0%} = {k:>4d} trades = ${p[-k:].sum():>12,.0f} = "
                  f"{p[-k:].sum() / net:>7.1%} of net   |   the other {len(p) - k:>4d} sum "
                  f"${p[:-k].sum():>12,.0f}")

    out = {rv.name: rv.as_dict() for rv in rows}
    with open(os.path.join(OUT, "baseline_risk_vectors.json"), "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1, default=str)
    print(f"\nwrote {os.path.join(OUT, 'baseline_risk_vectors.json')}")

    print("\n" + "=" * 112)
    print("LABELS THAT TRAVEL WITH THESE NUMBERS")
    print("=" * 112)
    print("  A_NT8_HEADLINE is Strategy Analyzer with ZERO slippage and the template commission.")
    print("    It is NOT a forward expectation and must never be quoted as one.")
    print("  B_RECOSTED adds the modelled spread the research charges. It is still IN-SAMPLE and")
    print("    still POST-SELECTION.")
    print("  M_11_COMPONENT_SET is two individually certified legs at quantity 1. It is NOT the")
    print("    research portfolio, which is inverse-vol weighted. No research-portfolio figure may")
    print("    be quoted for it (CLAUDE.md section 3).")
    print("  Evidence status of every number above: DISCOVERY_CONSUMED / IN-SAMPLE.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
