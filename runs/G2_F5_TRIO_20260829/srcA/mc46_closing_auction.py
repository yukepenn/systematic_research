"""G2_F5_TRIO_20260829 sub-run A — MC-46 closing-auction break test (trial G00029).

Frozen primary (spec.yaml A_MC46_closing_auction) executed exactly, per
outA/spec_resolutions.txt R1-R10. Gate table PRINTED BY THIS PROGRAM; MDE and event
counts printed BEFORE verdicts. Substrate law: POINTS only. Seal: every load passes
research_sdk.seal_guard.assert_presealed. No parameter search. K=1000, seed 20260829.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import time as _time
from datetime import date, datetime, timezone

import numpy as np
import pandas as pd

REPO = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, REPO)
from research_sdk.seal_guard import assert_presealed  # noqa: E402

SUBSTRATE = os.path.join(REPO, r"research\scalping_lab\substrate\minute\NQ\nq1m_2005_202605.parquet")
OUT = os.path.join(REPO, r"runs\G2_F5_TRIO_20260829\outA")
SEED = 20260829
K = 1000
START = date(2006, 1, 1)
END = date(2026, 5, 31)

# grid: stamps 09:30..16:00 -> closes[391]; returns/volume positions 0..389 = stamps 09:31..16:00
N_RET = 390


def grid_idx(hh: int, mm: int) -> int:
    """Return-grid index of END-stamp hh:mm (09:31 -> 0 ... 16:00 -> 389)."""
    return (hh - 9) * 60 + (mm - 31)


ANCHORS = {
    "15:50": {"pre": (grid_idx(15, 31), grid_idx(15, 40)), "post": (grid_idx(15, 51), grid_idx(16, 0))},
    "15:40": {"pre": (grid_idx(15, 21), grid_idx(15, 30)), "post": (grid_idx(15, 41), grid_idx(15, 50))},
    "15:45": {"pre": (grid_idx(15, 26), grid_idx(15, 35)), "post": (grid_idx(15, 46), grid_idx(15, 55))},
}


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_sessions():
    """Return (session_ids, R[N,390] returns pts, V[N,390] volume, C1550[N], C1600[N], C0930[N], C1000[N])."""
    df = pd.read_parquet(SUBSTRATE)
    df["ts"] = pd.to_datetime(df["time"])
    assert_presealed(df, "ts", "MC46 load nq1m_2005_202605")  # hard rule 4
    df = df[(df["ts"] >= pd.Timestamp("2005-12-31")) & (df["ts"] <= pd.Timestamp("2026-06-01"))]

    # session_id: 18:00->17:00 ET; RTH stamps (<=17:00) carry the session's own date
    t = df["ts"]
    sess = np.where(t.dt.time > pd.Timestamp("17:00").time(), (t + pd.Timedelta(days=1)).dt.date, t.dt.date)
    df = df.assign(sess=sess)
    df = df[(df["sess"] >= START) & (df["sess"] <= END)]

    minute_of = (t.dt.hour * 60 + t.dt.minute).reindex(df.index)
    df = df.assign(minute=minute_of)

    m0930, m0931, m1556, m1600 = 9 * 60 + 30, 9 * 60 + 31, 15 * 60 + 56, 16 * 60
    rth = df[(df["minute"] >= m0931) & (df["minute"] <= m1600)]
    counts = rth.groupby("sess").size()
    late = rth[(rth["minute"] >= m1556)].groupby("sess").size()
    has_seed = df[df["minute"] <= m0930].groupby("sess").size()
    qual = counts[(counts >= 300)].index.intersection(late.index).intersection(has_seed.index)
    qual = np.array(sorted(qual))
    n = len(qual)

    sess_pos = {s: i for i, s in enumerate(qual)}
    C = np.full((n, N_RET + 1), np.nan)  # closes at stamps 09:30..16:00
    V = np.zeros((n, N_RET))

    dfq = df[df["sess"].isin(sess_pos)].sort_values("ts")
    # seed close: last close at/before 09:30 per session
    seeds = dfq[dfq["minute"] <= m0930].groupby("sess")["close"].last()
    for s, v in seeds.items():
        C[sess_pos[s], 0] = v
    inwin = dfq[(dfq["minute"] >= m0931) & (dfq["minute"] <= m1600)]
    rows = inwin["sess"].map(sess_pos).to_numpy()
    cols = inwin["minute"].to_numpy() - m0931 + 1  # close-grid col (1..390)
    C[rows, cols] = inwin["close"].to_numpy()
    V[rows, cols - 1] = inwin["volume"].to_numpy()

    # forward-fill closes along the grid
    for j in range(1, N_RET + 1):
        m = np.isnan(C[:, j])
        C[m, j] = C[m, j - 1]
    assert not np.isnan(C).any(), "unseeded session slipped through qualification"
    R = np.diff(C, axis=1)  # POINTS
    return qual, R, V, C[:, grid_idx(15, 50) + 1], C[:, N_RET], C[:, 0], C[:, grid_idx(10, 0) + 1]


def stats_for(Rw_pre, Rw_post, Vw_pre, Vw_post):
    """Cross-session aggregate (mean|ret|, mean vol, lag1 autocorr) for pre & post window
    matrices [N,10]; returns dict of (pre, post, n_ac_pre, n_ac_post)."""
    out = {}
    out["absret"] = (np.abs(Rw_pre).mean(axis=1).mean(), np.abs(Rw_post).mean(axis=1).mean())
    out["volume"] = (Vw_pre.mean(axis=1).mean(), Vw_post.mean(axis=1).mean())

    def ac(W):
        a, b = W[:, :-1], W[:, 1:]
        am = a - a.mean(axis=1, keepdims=True)
        bm = b - b.mean(axis=1, keepdims=True)
        den = np.sqrt((am**2).sum(axis=1) * (bm**2).sum(axis=1))
        ok = den > 0
        r = np.full(len(W), np.nan)
        r[ok] = (am[ok] * bm[ok]).sum(axis=1) / den[ok]
        return np.nanmean(r), int(ok.sum())

    ac_pre, n_pre = ac(Rw_pre)
    ac_post, n_post = ac(Rw_post)
    out["autocorr"] = (ac_pre, ac_post)
    out["_ac_n"] = (n_pre, n_post)
    return out


def window(M, lohi):
    lo, hi = lohi
    return M[:, lo : hi + 1]


def main():
    t0 = _time.time()
    lines = []

    def P(s=""):
        print(s)
        lines.append(s)

    P("=" * 100)
    P("G2_F5_TRIO_20260829 / sub-run A — MC-46 CLOSING-AUCTION BREAK TEST (trial G00029)")
    P("printed by srcA/mc46_closing_auction.py — GATE/SPEC/OBSERVED/PASS-FAIL assembled by program only")
    P(f"substrate: {SUBSTRATE}")
    P(f"substrate sha256: {sha256_file(SUBSTRATE)}")
    P(f"python {sys.version.split()[0]}  numpy {np.__version__}  pandas {pd.__version__}")
    P(f"seed={SEED}  K={K}  range {START}..{END}  evidence status: DISCOVERY_CONSUMED")
    P("=" * 100)

    sess, R, V, c1550, c1600, c0930, c1000 = load_sessions()
    n = len(sess)
    eras = {"2006-15": sess <= date(2015, 12, 31), "2016-26": sess >= date(2016, 1, 1)}

    # ---- observed effects at all three anchors --------------------------------------
    obs = {}
    for name, w in ANCHORS.items():
        st = stats_for(window(R, w["pre"]), window(R, w["post"]), window(V, w["pre"]), window(V, w["post"]))
        obs[name] = st

    # ---- shared circular-shift null at the 15:50 construction -----------------------
    rng = np.random.default_rng(SEED)
    w = ANCHORS["15:50"]
    pre_idx = np.arange(w["pre"][0], w["pre"][1] + 1)
    post_idx = np.arange(w["post"][0], w["post"][1] + 1)
    null_eff = {"absret": np.empty(K), "volume": np.empty(K), "autocorr": np.empty(K)}
    rowsel = np.arange(n)[:, None]
    for k in range(K):
        o = rng.integers(1, N_RET, size=n)  # ONE offset per session, shared across stats
        pi = (pre_idx[None, :] + o[:, None]) % N_RET
        qi = (post_idx[None, :] + o[:, None]) % N_RET
        st = stats_for(R[rowsel, pi], R[rowsel, qi], V[rowsel, pi], V[rowsel, qi])
        for s in ("absret", "volume", "autocorr"):
            null_eff[s][k] = abs(st[s][1] - st[s][0])
    p95 = {s: float(np.percentile(null_eff[s], 95)) for s in null_eff}

    # ---- MDE / event counts BEFORE verdicts (hard rule 7) ---------------------------
    P()
    P("EVENT COUNTS AND MDE — PRINTED BEFORE ANY VERDICT")
    P(f"  qualifying sessions (full sample) : {n}")
    for e, m in eras.items():
        P(f"  qualifying sessions {e}        : {int(m.sum())}")
    a5 = obs["15:50"]
    P(f"  autocorr valid sessions 15:50 pre/post : {a5['_ac_n'][0]}/{a5['_ac_n'][1]}")
    P("  MDE (= shared circular-shift null p95 of |post-pre|, one-sided 5%):")
    P(f"    mean|1-min ret|  : {p95['absret']:.6f} pts")
    P(f"    mean volume      : {p95['volume']:.3f} contracts/min")
    P(f"    lag-1 autocorr   : {p95['autocorr']:.6f}")

    # ---- gate table -----------------------------------------------------------------
    stat_label = {"absret": "S1 mean|1-min ret| (pts)", "volume": "S2 mean volume", "autocorr": "S3 lag-1 autocorr"}
    P()
    P("OBSERVED WINDOW AGGREGATES (per-session value, cross-session mean; POINTS / contracts)")
    P(f"  {'anchor':7s} {'statistic':26s} {'pre':>14s} {'post':>14s} {'effect=|d|':>12s}")
    eff = {}
    for name in ("15:50", "15:40", "15:45"):
        for s in ("absret", "volume", "autocorr"):
            pre, post = obs[name][s]
            eff[(name, s)] = abs(post - pre)
            P(f"  {name:7s} {stat_label[s]:26s} {pre:14.6f} {post:14.6f} {eff[(name, s)]:12.6f}")

    P()
    P("GATE TABLE — frozen clause: effect(15:50) > effect(15:40) AND > effect(15:45) AND > null p95")
    hdr = f"  {'GATE':26s} {'SPEC (must exceed)':>44s} {'OBSERVED eff(15:50)':>20s} {'VERDICT':>9s}"
    P(hdr)
    P("  " + "-" * (len(hdr) - 2))
    passes = {}
    for s in ("absret", "volume", "autocorr"):
        e50, e40, e45 = eff[("15:50", s)], eff[("15:40", s)], eff[("15:45", s)]
        ok = (e50 > e40) and (e50 > e45) and (e50 > p95[s])
        passes[s] = ok
        spec = f"p40={e40:.6f} p45={e45:.6f} null95={p95[s]:.6f}"
        P(f"  {stat_label[s]:26s} {spec:>44s} {e50:20.6f} {'PASS' if ok else 'FAIL':>9s}")
        for cl, okc in (("> placebo 15:40", e50 > e40), ("> placebo 15:45", e50 > e45), ("> null p95", e50 > p95[s])):
            P(f"      clause {cl:16s}: {'PASS' if okc else 'FAIL'}")
    n_pass = sum(passes.values())
    break_exists = n_pass >= 1
    P("  " + "-" * (len(hdr) - 2))
    P(f"  ANCHOR-SPECIFIC BREAK AT 15:50 (>=1 of 3 per R6): {'EXISTS — PASS' if break_exists else 'ABSENT — FAIL'}"
      f"  ({n_pass}/3 statistics pass)")
    P("  NOTE (R6/R9): 3 statistics at per-stat p95 -> family alpha <=~0.14 under independence;")
    marginal = [s for s in passes if passes[s] and eff[("15:50", s)] < 1.5 * p95[s]]
    P(f"  marginal passes (effect < 1.5x null p95): {marginal if marginal else 'none'}")
    P("  R9 caveat: the close ramp is convex, so later anchors mechanically favor larger pre/post")
    P("  differences; placebo construction executed exactly as frozen.")

    # ---- conditional reversion table ------------------------------------------------
    rev_lines = []
    if break_exists:
        D = c1600 - c1550  # dislocation, points
        # next qualifying session within 7 calendar days
        nxt = np.full(n, -1)
        for i in range(n - 1):
            if (sess[i + 1] - sess[i]).days <= 7:
                nxt[i] = i + 1
        ok = nxt >= 0
        H1 = np.full(n, np.nan)
        H2 = np.full(n, np.nan)
        H1[ok] = c0930[nxt[ok]] - c1600[ok]
        H2[ok] = c1000[nxt[ok]] - c0930[nxt[ok]]

        def RP(s=""):
            P(s)
            rev_lines.append(s)

        RP()
        RP("REVERSION TABLE (diagnostic; runs because the anchor-specific break exists; no gate, no policy)")
        RP("dislocation D = close16:00 - close15:50 (pts); H1 = overnight to next 09:30; H2 = next 09:30->10:00")
        RP(f"sessions dropped for missing next session (gap>7d/end of sample): {int((~ok).sum())}")
        for e, m in eras.items():
            me = m & ok
            d, h1, h2 = D[me], H1[me], H2[me]
            q = np.quantile(d, np.linspace(0, 1, 11))
            q[0], q[-1] = -np.inf, np.inf
            RP(f"  era {e} (N={int(me.sum())}):  OLS slope H1~D = "
               f"{np.polyfit(d, h1, 1)[0]:+.4f} pts/pt")
            RP(f"    {'decile':>6s} {'N':>5s} {'mean D':>10s} {'mean H1':>10s} {'mean H2':>10s}")
            for dec in range(10):
                sel = (d >= q[dec]) & (d < q[dec + 1])
                RP(f"    {dec + 1:6d} {int(sel.sum()):5d} {d[sel].mean():10.3f} {h1[sel].mean():10.3f} {h2[sel].mean():10.3f}")
        RP("evidence status: DISCOVERY_CONSUMED — in-sample diagnostic, no forward claim, no tradability claim.")
    else:
        P()
        P("REVERSION TABLE: NOT RUN — spec runs it ONLY on an anchor-specific break; the break gate FAILED.")

    P()
    P(f"wall_s {int(_time.time() - t0)}")

    with open(os.path.join(OUT, "A_gate_table.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    if rev_lines:
        with open(os.path.join(OUT, "reversion_table.txt"), "w", encoding="utf-8") as f:
            f.write("\n".join(rev_lines) + "\n")

    frag = {
        "kind": "RESULT",
        "trial_id": "G00029",
        "result": "PASS" if break_exists else "FAIL",
        "selected": False,
        "metrics": {
            "n_sessions": int(n),
            "n_sessions_2006_15": int(eras["2006-15"].sum()),
            "n_sessions_2016_26": int(eras["2016-26"].sum()),
            "eff_1550_absret_pts": eff[("15:50", "absret")],
            "eff_1540_absret_pts": eff[("15:40", "absret")],
            "eff_1545_absret_pts": eff[("15:45", "absret")],
            "null_p95_absret_pts": p95["absret"],
            "eff_1550_volume": eff[("15:50", "volume")],
            "eff_1540_volume": eff[("15:40", "volume")],
            "eff_1545_volume": eff[("15:45", "volume")],
            "null_p95_volume": p95["volume"],
            "eff_1550_autocorr": eff[("15:50", "autocorr")],
            "eff_1540_autocorr": eff[("15:40", "autocorr")],
            "eff_1545_autocorr": eff[("15:45", "autocorr")],
            "null_p95_autocorr": p95["autocorr"],
            "stats_passing": int(n_pass),
            "K": K,
            "seed": SEED,
            "wall_s": int(_time.time() - t0),
        },
        "note": ("MC-46 anchor-specific 15:50 break test, frozen construction (spec_resolutions R1-R7); "
                 + ("break EXISTS; reversion table written (diagnostic, DISCOVERY_CONSUMED, no policy)."
                    if break_exists else "break ABSENT; reversion table not run per spec.")
                 + " Shared circular-shift null, one offset/session/replication across all 3 statistics."),
        "ts_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "hash": None, "prev_hash": None, "seq": None,
        "pending": "orchestrator must chain hash/prev_hash/seq on append",
    }
    with open(os.path.join(OUT, "ledger_result_pending.json"), "w", encoding="utf-8") as f:
        json.dump(frag, f, indent=1, sort_keys=True)
    print("wrote outA/A_gate_table.txt, outA/ledger_result_pending.json"
          + (", outA/reversion_table.txt" if rev_lines else ""))


if __name__ == "__main__":
    main()
