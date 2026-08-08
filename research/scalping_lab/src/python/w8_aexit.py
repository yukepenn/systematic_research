"""W8-3 — A-EXIT: patient execution on Solar's time-triggered exits (DR-E R1, Arm A+B).

Spec: research/scalping_lab/specs/W8_programs_final.md (frozen, cf7041f), section W8-3.

Frozen mechanics as implemented (documented interpretations):
- Fills are MINUTE-stamped (all seconds == :00). The fill minute's :00 second is taken as
  the fill's reference second T (= the timestamp itself). For the E10 v2 flatten this means
  the counterfactual template anchors at the fill's own minute (30/31 exits are stamped
  16:45 = the END stamp of the 16:44-flatten 3-min bar; 1 is stamped 16:42), not at the
  spec's literal example anchor 16:44:00 — the mechanics are identical, shifted to the
  actual fill minute.
- Baseline: market cross at T using grid1s bid/ask at second T (sell -> bid, buy -> ask).
  grid1s bid/ask are PRICES (points); the per-second state is the LAST quote within the
  second, forward-filled (causal end-of-second state, per build_grid1s.py).
- Arm A (time-triggered 16:42-16:45 flatten exits, actions Sell/BuyToCover):
  patient limit posted at post = T - W, W in {30, 60, 120} s, at the opposite touch AT THE
  POSTING SECOND (sell -> ask(post), buy -> bid(post)) from grid1s.
  Deadline D = T + 59 s (the fill minute's :59 second; spec: "before 16:44:59").
- Arm B (signal entries outside 16:42-16:45, actions Buy/SellShort, names S/L):
  marketable-limit posted at post = T at the opposite touch (buy -> bid(T),
  sell -> ask(T)); patience W in {5, 30, 60} s; deadline D = T + W.
- Fill condition (house trade-through convention): filled iff sechilo mid (TICKS =
  price * 4) crosses THROUGH the limit by >= 1 tick strictly before the deadline second:
  scan seconds [post + 1, D - 1] inclusive (posting second excluded because grid1s state
  is end-of-second; deadline second excluded because that is the forced-cross second);
  sell limit L: filled iff any sechilo mid_high >= L*4 + 1;
  buy  limit L: filled iff any sechilo mid_low  <= L*4 - 1.
  Sechilo is sparse (only seconds with quote events); absent seconds cannot fill.
- Unfilled -> forced cross at the deadline second's touch: sell -> bid(D), buy -> ask(D).
- Saving per order in NQ ticks (positive = patient better than baseline):
  sell: (realized - baseline) / 0.25 ; buy: (baseline - baseline_side_realized) ->
  (baseline - realized) / 0.25.
- Multiple fills in the same minute + same order_action = ONE order (qty summed, MNQ units).
- Session tag = END date (18:00 prior ET day -> 17:00 tag day); fills with hour >= 18 map
  to the next calendar day's tag.
- Dollarization: prices are NQ index levels but the traded units are MNQ (qty in MNQ
  contracts); 1 NQ tick = 0.25 pts = $0.50 per MNQ contract.
- Day-clustered bootstrap: resample sessions with replacement, 1000 reps, seed 20260808,
  percentile CI [2.5, 97.5] on the pooled per-order mean saving.
- HARD GUARD: no fill row with time >= 2026-06-01 is ever used; substrate sessions all
  end 2026-05-20.

Outputs (research/scalping_lab/artifacts/w8_aexit/):
  stdout.txt, w8aexit_orders.csv, w8aexit_summary.csv, w8aexit_report.md (report written
  separately from this run's numbers).
"""
import glob
import os
import sys

import numpy as np
import pandas as pd

ROOT = "D:/OneDrive - Washington University in St. Louis/TradingResearch/systematic_research"
FILLS = os.path.join(ROOT, "runs/E10MASTER_V2/out/e10m_v2_fills.csv")
SECHILO = os.path.join(ROOT, "research/scalping_lab/substrate/sechilo/NQ")
GRID1S = os.path.join(ROOT, "research/scalping_lab/substrate/grid1s/NQ")
ART = os.path.join(ROOT, "research/scalping_lab/artifacts/w8_aexit")
os.makedirs(ART, exist_ok=True)

SEED = 20260808
REPS = 1000
TICK = 0.25              # NQ points per tick
MNQ_TICK_USD = 0.50      # $ per tick per MNQ contract
CUTOFF = pd.Timestamp("2026-06-01")
ARM_W = {"A": [30, 60, 120], "B": [5, 30, 60]}


class Tee:
    def __init__(self, path):
        self.f = open(path, "w", encoding="utf-8")
        self.stdout = sys.stdout

    def write(self, s):
        self.f.write(s)
        self.stdout.write(s)

    def flush(self):
        self.f.flush()
        self.stdout.flush()


def load_orders():
    f = pd.read_csv(FILLS, skiprows=1)
    f["time"] = pd.to_datetime(f["time"])
    n_raw = len(f)
    f = f[f["time"] < CUTOFF].copy()
    print(f"FACT: fills rows raw={n_raw}, kept after < {CUTOFF.date()} truncation={len(f)}")
    assert (f["time"] < CUTOFF).all()
    assert (f["time"].dt.second == 0).all(), "fills must be minute-stamped"
    h17 = f[f["time"].dt.hour == 17]
    assert (h17["time"].dt.strftime("%H:%M") == "17:00").all(), "fills inside 17:00-17:59 halt"
    print(f"FACT: fills stamped exactly 17:00 (session-close boundary, map to same-day tag): {len(h17)}")
    tag = f["time"].dt.normalize() + pd.to_timedelta((f["time"].dt.hour >= 18).astype(int), unit="D")
    f["sess"] = tag.dt.strftime("s%Y%m%d")

    sech = {os.path.basename(p)[:-8] for p in glob.glob(os.path.join(SECHILO, "s*.parquet"))}
    grid = {os.path.basename(p)[:-8] for p in glob.glob(os.path.join(GRID1S, "s*.parquet"))}
    sessions = sorted(sech & grid)
    assert max(sessions) < "s20260601", "substrate session beyond cutoff"
    print(f"FACT: substrate sessions sechilo={len(sech)} grid1s={len(grid)} intersection={len(sessions)}")

    sub = f[f["sess"].isin(sessions)].copy()
    print(f"FACT: fills on substrate sessions={len(sub)} across {sub['sess'].nunique()} sessions")
    hm = sub["time"].dt.strftime("%H:%M")
    in_win = (hm >= "16:42") & (hm <= "16:45")

    a_fills = sub[in_win & sub["order_action"].isin(["Sell", "BuyToCover"])]
    b_fills = sub[~in_win & sub["order_action"].isin(["Buy", "SellShort"])]
    excl_win_entries = sub[in_win & sub["order_action"].isin(["Buy", "SellShort"])]
    print(f"FACT: Arm A exit fills (16:42-16:45, Sell/BuyToCover): {len(a_fills)} "
          f"on {a_fills['sess'].nunique()} sessions; stamp minutes: "
          f"{dict(a_fills['time'].dt.strftime('%H:%M').value_counts())}")
    print(f"FACT: Arm B entry fills (non-window Buy/SellShort): {len(b_fills)} "
          f"on {b_fills['sess'].nunique()} sessions; names: "
          f"{dict(b_fills['name'].value_counts())}")
    print(f"FACT: window-time Buy/SellShort fills excluded from both arms: {len(excl_win_entries)}")

    def group(df, arm):
        g = (df.groupby(["sess", "time", "order_action"], as_index=False)
               .agg(qty=("qty", "sum"), n_fills=("qty", "size"),
                    names=("name", lambda s: "+".join(sorted(set(s))))))
        g["arm"] = arm
        g["side"] = np.where(g["order_action"].isin(["Sell", "SellShort"]), "sell", "buy")
        return g

    a = group(a_fills, "A")
    b = group(b_fills, "B")
    n_multi = int((a["n_fills"] > 1).sum() + (b["n_fills"] > 1).sum())
    print(f"FACT: orders after same-minute/same-action grouping: ArmA={len(a)}, ArmB={len(b)}; "
          f"multi-fill minutes merged: {n_multi}")
    return sessions, a, b


class Session:
    """Per-session substrate access. grid: exact-second (asof fallback) bid/ask PRICES;
    sechilo: sparse per-second mid hi/lo in TICKS."""

    def __init__(self, tag):
        g = pd.read_parquet(os.path.join(GRID1S, tag + ".parquet"),
                            columns=["time", "bid", "ask"])
        self.gt = g["time"].values.astype("datetime64[s]").astype(np.int64)
        self.gbid = g["bid"].values
        self.gask = g["ask"].values
        s = pd.read_parquet(os.path.join(SECHILO, tag + ".parquet"),
                            columns=["time", "mid_high", "mid_low"])
        self.st = s["time"].values.astype("datetime64[s]").astype(np.int64)
        self.shi = s["mid_high"].values
        self.slo = s["mid_low"].values

    def quote_at(self, tsec):
        """(bid, ask) at epoch-second tsec: exact second if on grid, else last prior
        second (asof). None if before grid start or NaN."""
        i = np.searchsorted(self.gt, tsec, side="right") - 1
        if i < 0:
            return None
        b, a = self.gbid[i], self.gask[i]
        if np.isnan(b) or np.isnan(a):
            return None
        return float(b), float(a), bool(self.gt[i] != tsec)

    def cross_through(self, lo_sec, hi_sec, limit_ticks, side):
        """First epoch-second in [lo_sec, hi_sec] where sechilo mid trades through the
        limit by >= 1 tick. Returns epoch-second or None."""
        i0 = np.searchsorted(self.st, lo_sec, side="left")
        i1 = np.searchsorted(self.st, hi_sec, side="right")
        if i0 >= i1:
            return None
        if side == "sell":
            hit = self.shi[i0:i1] >= limit_ticks + 1.0
        else:
            hit = self.slo[i0:i1] <= limit_ticks - 1.0
        idx = np.nonzero(hit)[0]
        if len(idx) == 0:
            return None
        return int(self.st[i0 + idx[0]])


def simulate(orders, sessions_needed):
    cache = {}
    rows = []
    dropped = []
    for _, o in orders.iterrows():
        tag = o["sess"]
        if tag not in cache:
            cache[tag] = Session(tag)
        S = cache[tag]
        T = int(pd.Timestamp(o["time"]).value // 10**9)
        side = o["side"]
        for W in ARM_W[o["arm"]]:
            if o["arm"] == "A":
                post, deadline = T - W, T + 59
            else:
                post, deadline = T, T + W
            q_base = S.quote_at(T)
            q_post = S.quote_at(post)
            q_dead = S.quote_at(deadline)
            if q_base is None or q_post is None or q_dead is None:
                dropped.append((o["arm"], W, tag, str(o["time"]), "missing quote state"))
                continue
            baseline = q_base[0] if side == "sell" else q_base[1]
            limit = q_post[1] if side == "sell" else q_post[0]
            limit_ticks = limit / TICK
            fill_sec = S.cross_through(post + 1, deadline - 1, limit_ticks, side)
            if fill_sec is not None:
                realized = limit
                filled = True
            else:
                realized = q_dead[0] if side == "sell" else q_dead[1]
                filled = False
            saving = ((realized - baseline) if side == "sell" else (baseline - realized)) / TICK
            rows.append(dict(
                arm=o["arm"], W=W, sess=tag, time=str(o["time"]), side=side,
                action=o["order_action"], names=o["names"], qty_mnq=int(o["qty"]),
                post=str(pd.Timestamp(post, unit="s")), deadline=str(pd.Timestamp(deadline, unit="s")),
                baseline_px=baseline, limit_px=limit, filled=filled,
                fill_sec=(str(pd.Timestamp(fill_sec, unit="s")) if fill_sec else ""),
                realized_px=realized, saving_t=saving,
                saving_usd=saving * int(o["qty"]) * MNQ_TICK_USD,
                asof_base=q_base[2], asof_post=q_post[2], asof_dead=q_dead[2],
            ))
    return pd.DataFrame(rows), dropped


def cluster_ci(df, col="saving_t", seed=SEED, reps=REPS):
    """Day-clustered bootstrap CI on the pooled per-order mean of `col`."""
    rng = np.random.default_rng(seed)
    sess = df["sess"].unique()
    groups = {s: df.loc[df["sess"] == s, col].values for s in sess}
    means = np.empty(reps)
    for r in range(reps):
        pick = rng.choice(sess, size=len(sess), replace=True)
        pooled = np.concatenate([groups[s] for s in pick])
        means[r] = pooled.mean()
    return float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))


def summarize(res):
    out = []
    for (arm, W), d in res.groupby(["arm", "W"]):
        miss = d[~d["filled"]]
        lo, hi = cluster_ci(d)
        qs = np.percentile(d["saving_t"], [5, 25, 50, 75, 95])
        out.append(dict(
            arm=arm, W=W, n_orders=len(d), n_sessions=d["sess"].nunique(),
            n_filled=int(d["filled"].sum()), fill_rate=float(d["filled"].mean()),
            mean_saving_t=float(d["saving_t"].mean()),
            ci_lo=lo, ci_hi=hi,
            qtyw_mean_saving_t=float(np.average(d["saving_t"], weights=d["qty_mnq"])),
            total_saving_usd=float(d["saving_usd"].sum()),
            n_miss=len(miss),
            miss_mean_saving_t=(float(miss["saving_t"].mean()) if len(miss) else np.nan),
            miss_qtyw_saving_t=(float(np.average(miss["saving_t"], weights=miss["qty_mnq"]))
                                if len(miss) else np.nan),
            miss_total_usd=float(miss["saving_usd"].sum()),
            q05=qs[0], q25=qs[1], q50=qs[2], q75=qs[3], q95=qs[4],
        ))
    return pd.DataFrame(out)


def worked_example(res, label, arm, W, want_filled):
    d = res[(res["arm"] == arm) & (res["W"] == W) & (res["filled"] == want_filled)]
    if not len(d):
        print(f"[{label}] no {'filled' if want_filled else 'unfilled'} order for Arm {arm} W={W}")
        return
    r = d.iloc[0]
    lt = r["limit_px"] / TICK
    print(f"\n[{label}] Arm {arm}, W={W}s — {r['sess']}  fill stamp {r['time']}  "
          f"side={r['side']} ({r['action']}, names={r['names']}, qty={r['qty_mnq']} MNQ)")
    print(f"  reference second T   = {r['time']} (fill minute's :00 second — minute-stamp convention)")
    print(f"  posted at            = {r['post']}   deadline = {r['deadline']}")
    print(f"  baseline (cross @T)  = {'bid' if r['side']=='sell' else 'ask'}(T) = {r['baseline_px']:.2f}")
    print(f"  patient limit        = {'ask' if r['side']=='sell' else 'bid'}(post) = {r['limit_px']:.2f}"
          f"  ({lt:.0f} sechilo ticks; needs mid {'>=' if r['side']=='sell' else '<='} "
          f"{lt + (1 if r['side']=='sell' else -1):.0f}t to fill)")
    if r["filled"]:
        print(f"  FILLED: sechilo mid traded through at {r['fill_sec']} -> realized = limit = {r['realized_px']:.2f}")
    else:
        print(f"  NOT FILLED by {r['deadline']} -> forced cross at deadline "
              f"{'bid' if r['side']=='sell' else 'ask'} = {r['realized_px']:.2f}")
    print(f"  saving = ({'realized-baseline' if r['side']=='sell' else 'baseline-realized'})/0.25 "
          f"= {r['saving_t']:+.1f} NQ ticks  (${r['saving_usd']:+.2f} at qty x $0.50/MNQ-tick)")


def main():
    sys.stdout = Tee(os.path.join(ART, "stdout.txt"))
    print("W8-3 A-EXIT patient execution study — seed", SEED, "| reps", REPS)
    print("Convention: fills are minute-stamped; the fill minute's :00 second is the reference second T.")
    sessions, a, b = load_orders()
    orders = pd.concat([a, b], ignore_index=True)
    res, dropped = simulate(orders, sessions)
    print(f"FACT: simulated order-W rows: {len(res)}; dropped for missing quote state: {len(dropped)}")
    for d in dropped:
        print("  DROPPED:", d)
    n_asof = int(res[["asof_base", "asof_post", "asof_dead"]].any(axis=1).sum())
    print(f"FACT: rows using asof (non-exact-second grid state) at any leg: {n_asof}")

    res.to_csv(os.path.join(ART, "w8aexit_orders.csv"), index=False)
    summ = summarize(res)
    summ.to_csv(os.path.join(ART, "w8aexit_summary.csv"), index=False)

    pd.set_option("display.width", 250)
    print("\n=== SUMMARY (per arm per W) — saving in NQ ticks per order, + = patient better ===")
    print(summ.to_string(index=False, float_format=lambda x: f"{x:.3f}"))

    print("\n=== Arm A per-order detail (all Ws) ===")
    cols = ["W", "sess", "time", "side", "qty_mnq", "baseline_px", "limit_px", "filled",
            "fill_sec", "realized_px", "saving_t"]
    print(res[res["arm"] == "A"][cols].to_string(index=False))

    print("\n=== Arm B side split (secondary, in-sample characterization) ===")
    for (W, side), d in res[res["arm"] == "B"].groupby(["W", "side"]):
        lo, hi = cluster_ci(d)
        print(f"  W={W:>3} {side:>4}: n={len(d):>3} fill_rate={d['filled'].mean():.3f} "
              f"mean={d['saving_t'].mean():+.3f}t CI[{lo:+.3f},{hi:+.3f}]")

    print("\n=== 3 fully worked examples ===")
    worked_example(res, "EX1", "A", 60, True)
    worked_example(res, "EX2", "A", 60, False)
    worked_example(res, "EX3", "B", 30, False)

    print("\n=== FROZEN VERDICT RULE: adopt-for-ops iff Arm A saving CI_lo > 0; close passive track if <= 0 ===")
    for _, r in summ[summ["arm"] == "A"].iterrows():
        verdict = "ADOPT-FOR-OPS (CI_lo > 0)" if r["ci_lo"] > 0 else "CI_lo <= 0 -> close passive track"
        print(f"  Arm A W={int(r['W']):>3}: mean={r['mean_saving_t']:+.3f}t "
              f"CI[{r['ci_lo']:+.3f}, {r['ci_hi']:+.3f}] -> {verdict}")
    print("\nDONE")


if __name__ == "__main__":
    main()
