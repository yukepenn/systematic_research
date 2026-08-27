"""RECENT-REGIME PANEL - separate RECENT HISTORICAL evidence from PROSPECTIVE FORWARD evidence.

Directive s2. TOMORROW_PRODUCTION_CANDIDATE said "recent-regime evidence: there is none", which is
wrong in SCOPE. There is substantial recent HISTORICAL evidence; it is simply DISCOVERY_CONSUMED /
BURNED rather than clean prospective confirmation. Those are different objects and both are real.

    RECENT != FORWARD.
    BURNED CURRENT-REGIME EVIDENCE IS STILL EVIDENCE.
    It is just not clean prospective confirmation.

Windows are FIXED STANDARD lengths declared here, not chosen after seeing results (s2: "Do NOT
optimize a new recent window"). Nothing sealed is read: everything ends at the 2026-07-31 cutoff.
"""
from __future__ import annotations

import os

import numpy as np
import pandas as pd

ROOT = (r"D:\OneDrive - Washington University in St. Louis\TradingResearch"
        r"\systematic_research")
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "out")
os.makedirs(OUT, exist_ok=True)
K_FROZEN = 20245.0 / 22931.0          # frozen research scaling, per s29
WINDOWS = [13, 26, 52, 104]           # fixed standard windows, declared before results
_fh = open(os.path.join(OUT, "panel.txt"), "w", encoding="utf-8")


def P(*a):
    print(*a, flush=True)
    print(*a, file=_fh)


def stats(x, k=K_FROZEN):
    x = np.asarray(x, float) * k
    n = len(x)
    if n < 2:
        return dict(n=n, mean=np.nan, pos=np.nan, t=np.nan, total=np.nan)
    sd = x.std(ddof=1)
    return dict(n=n, mean=x.mean(), pos=100 * np.mean(x > 0),
                t=(x.mean() / (sd / np.sqrt(n))) if sd > 0 else np.nan, total=x.sum())


def main():
    P("=" * 100)
    P("=== RECENT-REGIME PANEL - recent HISTORICAL evidence, which is BURNED, not FORWARD")
    P("=== Fixed standard windows declared before results. Nothing sealed is read.")
    P("=" * 100)

    # ---------------------------------------------------------------- P1 weekly
    d = pd.read_csv(os.path.join(ROOT, "runs/RR_W003_X9A_CONTRACT/out/weekly_p1_x9a.csv"))
    d = d.rename(columns={d.columns[0]: "week"})
    d["week"] = pd.to_datetime(d["week"])
    d = d.sort_values("week").reset_index(drop=True)

    # ---------------------------------------------------------------- XM weekly, from the ledger
    X = pd.read_csv(os.path.join(ROOT, "runs/RR_W001_ACTION_VALUE_LEDGER/out/ledger_xm.csv"))
    X["session_date"] = pd.to_datetime(X["session_date"])
    X["week"] = X["session_date"] + pd.to_timedelta(6 - X["session_date"].dt.weekday, unit="D")
    xw = X.groupby("week")["net_research"].sum()
    # reindex onto P1's weekly axis so a quiet XM week is a real ZERO, not a missing row
    xm = xw.reindex(d["week"], fill_value=0.0).values
    d["xm"] = xm
    P(f"\n    P1 weekly rows {len(d)}   {d['week'].min().date()} -> {d['week'].max().date()}")
    P(f"    XM trades {len(X):,}, active weeks {int((xw != 0).sum())} of {len(d)} "
      f"({100*(xw != 0).sum()/len(d):.1f} %)")
    P("    NOTE: XM's silent weeks are counted as $0, not dropped. Dropping them would inflate")
    P("    both its mean and its positive-week rate by conditioning on having traded.")

    P("")
    P("=" * 100)
    P("=== PANEL A - RECENT HISTORICAL (BURNED / DISCOVERY_CONSUMED). Real evidence, not clean.")
    P("=" * 100)
    P(f"    {'object':<10}{'window':>10}{'n':>5}{'mean $/wk':>12}{'total $':>12}"
      f"{'pos wks':>10}{'t':>8}")
    P("    " + "-" * 68)
    rows = []
    for name, col in (("P1/PCT", "p1"), ("XM", "xm"), ("P1+XM", None)):
        v = (d["p1"] + d["xm"]).values if col is None else d[col].values
        for w in WINDOWS + [len(d)]:
            s = stats(v[-w:])
            lab = "FULL" if w >= len(d) else f"last {w}w"
            P(f"    {name:<10}{lab:>10}{s['n']:>5}{s['mean']:>12,.0f}{s['total']:>12,.0f}"
              f"{s['pos']:>9.1f}%{s['t']:>8.2f}")
            rows.append(dict(object=name, window=lab, **s))
        P("    " + "-" * 68)
    pd.DataFrame(rows).to_csv(os.path.join(OUT, "recent_panel.csv"), index=False)

    # ---------------------------------------------------------------- correlation
    P("")
    P("=" * 100)
    P("=== TRAILING CORRELATION and CONDITIONAL BEHAVIOUR")
    P("=" * 100)
    for w in WINDOWS + [len(d)]:
        a, b = d["p1"].values[-w:], d["xm"].values[-w:]
        lab = "FULL" if w >= len(d) else f"last {w}w"
        r = np.corrcoef(a, b)[0, 1] if np.std(a) > 0 and np.std(b) > 0 else np.nan
        lose = a < 0
        cond = (b[lose] * K_FROZEN).mean() if lose.sum() > 1 else np.nan
        P(f"    {lab:>10}   rho(P1,XM) {r:+.3f}    "
          f"mean XM when P1 loses ${cond:>9,.0f}   (P1 losing weeks {int(lose.sum())})")

    # ---------------------------------------------------------------- concentration
    P("")
    P("=" * 100)
    P("=== CONCENTRATION - how much of the recent result lives in a few weeks")
    P("=" * 100)
    for name, col in (("P1/PCT", "p1"), ("XM", "xm")):
        for w in (26, 52, len(d)):
            v = np.sort(d[col].values[-w:])[::-1] * K_FROZEN
            tot = v.sum()
            lab = "FULL" if w >= len(d) else f"last {w}w"
            if abs(tot) < 1e-9:
                continue
            P(f"    {name:<8}{lab:>8}   top-1 week {100*v[0]/tot:>6.1f} %   "
              f"top-5 {100*v[:5].sum()/tot:>6.1f} %   of net ${tot:>9,.0f}")

    P("")
    P("=" * 100)
    P("=== PANEL B - PROSPECTIVE / POST-FREEZE")
    P("=" * 100)
    P("    NONE YET. The >= 2026-08-01 seal holds ~19 sessions against a 60-session CPA trigger.")
    P("    This is the only CLEAN PROSPECTIVE evidence and it is calendar-gated, not analysable.")
    P("")
    P("    Panel A is BURNED: every window above sits inside the discovery-consumed record and was")
    P("    available while the objects were being built. It is evidence about the recent regime.")
    P("    It is NOT confirmation, and it cannot be upgraded into confirmation by any analysis.")
    _fh.close()


if __name__ == "__main__":
    main()
