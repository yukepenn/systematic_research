"""End-to-end check that panel.py + common.py work together on the REAL panel.

Not a result. It (a) re-verifies the 2022-01-01 wall on the written parquet, (b) confirms the
helpers run on real data, and (c) records the EPISODE STRUCTURE the next agent must plan for,
because the wave brief's stated prior about episode counts does not survive contact with the
panel.

    python runs/G3_VOLSHORT01_20260831/src/discovery/smoke_test.py
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, HERE)
import common as C                                                        # noqa: E402

PANEL = os.path.join(ROOT, "runs", "G3_VOLSHORT01_20260831", "out", "discovery",
                     "panel_pre2022.parquet")
WALL = pd.Timestamp("2022-01-01")
_LOG: list[str] = []


def P(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    _LOG.append(s)


def main() -> int:
    d = pd.read_parquet(PANEL)
    P("=" * 92)
    P("G3_VOLSHORT01 smoke test -- panel + common, end to end")
    P("=" * 92)

    P("\n[A] wall re-verified on the written artefact")
    mx = d["session_date"].max()
    ok = mx < WALL
    P(f"  rows={len(d):,}  span {d['session_date'].min().date()} .. {mx.date()}  "
      f"max < 2022-01-01 = {ok}  -> {'PASS' if ok else 'FAIL'}")
    assert ok
    for c in [c for c in d.columns if c.endswith("_asof")] + ["prev_session_date"]:
        v = pd.to_datetime(d[c]).dropna()
        assert len(v) == 0 or v.max() < WALL, c
    P("  every *_asof and prev_session_date column also < wall  -> PASS")

    f = d[d["session_quality"] == "FULL"].reset_index(drop=True)
    P(f"  FULL sessions usable for return work: {len(f):,}")

    P("\n[B] episode structure of a causal rolling-252 tercile high state")
    P("  THE BRIEF SAID: '~600 raw high-VIX sessions cluster into perhaps 8-14 independent")
    P("  episodes.' On this panel, at gap_days=10, that is NOT what happens. Plan for this.")
    P(f"\n  {'index':<6s} {'high_sess':>9s} {'K@10':>5s} {'K@21':>5s} {'K@42':>5s} "
      f"{'K@63':>5s} {'rho_bar':>8s} {'K_eff@10':>9s} {'top5share':>10s} {'singletons':>10s}")
    for col in ("vix", "vxn"):
        g = f[f[col].notna()].reset_index(drop=True)
        g["st"] = C.causal_tercile(g[col], window=252)
        hi = (g["st"] == 2).values
        sp = np.where(hi, -g["rth_ret_pts"], np.nan)
        ids = C.episode_ids(hi, g["session_date"], gap_days=10)
        rho = C.icc_rho(sp, ids)
        et = C.episode_table(hi, g["session_date"], values=sp)
        Ks = [len(C.episodes(hi, g["session_date"], gap_days=gd)) for gd in (10, 21, 42, 63)]
        top5 = 100 * et["n_sessions"].nlargest(5).sum() / et["n_sessions"].sum()
        P(f"  {col:<6s} {int(hi.sum()):>9,} {Ks[0]:>5d} {Ks[1]:>5d} {Ks[2]:>5d} {Ks[3]:>5d} "
          f"{rho:>8.4f} {C.k_eff(Ks[0], rho):>9.2f} {top5:>9.1f}% "
          f"{int((et['n_sessions'] <= 2).sum()):>10d}")

    g = f[f["vix"].notna()].reset_index(drop=True)
    g["st"] = C.causal_tercile(g["vix"], window=252)
    hi = (g["st"] == 2).values
    et = C.episode_table(hi, g["session_date"],
                         values=np.where(hi, -g["rth_ret_pts"], np.nan))
    P(f"\n  VIX high-state episode SIZE distribution (K={len(et)}): "
      f"min={int(et['n_sessions'].min())} p25={et['n_sessions'].quantile(.25):.0f} "
      f"median={et['n_sessions'].median():.0f} p75={et['n_sessions'].quantile(.75):.0f} "
      f"max={int(et['n_sessions'].max())}")
    P("  -> the count is dominated by a few huge blocks. K is NOT the effective sample size;")
    P("     report K, rho_bar and K_eff together, and never quote K alone.")
    P("\n  five largest VIX high-state episodes (short-leg pts, DISCOVERY_CONTAMINATED):")
    for _, r in et.nlargest(5, "n_sessions").iterrows():
        P(f"    {str(r['start'].date())} .. {str(r['end'].date())}  "
          f"{int(r['n_sessions']):>4d} sessions  short-leg sum {r['sum']:>10,.1f} pts")

    P("\n  an ABSOLUTE threshold clusters more, but still not into 8-14:")
    for thr in (20, 25, 30):
        ab = (g["vix"] > thr).values
        P(f"    VIX>{thr}: {int(ab.sum()):>5,} sessions -> "
          f"K@10={len(C.episodes(ab, g['session_date'], 10)):>3d}  "
          f"K@21={len(C.episodes(ab, g['session_date'], 21)):>3d}")

    P("\n[C] three_arms runs on the real panel (structure check only -- NOT a result)")
    g2 = g.dropna(subset=["st", "rth_ret_pts"]).reset_index(drop=True)
    tab = C.three_arms(g2, "st", high_state=2, low_state=0)
    P("  " + C.format_arms(tab).replace("\n", "\n  "))
    P("\n  Reported here ONLY to prove the plumbing. Adjudicating these numbers is the next")
    P("  agent's job, and requires the rate-matched random-short placebo and the episode")
    P("  bootstrap, neither of which is run here.")

    out = os.path.join(ROOT, "runs", "G3_VOLSHORT01_20260831", "out", "discovery",
                       "smoke_test.txt")
    with open(out, "w", encoding="utf-8") as fh:
        fh.write("\n".join(_LOG) + "\n")
    P(f"\n  WROTE {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
