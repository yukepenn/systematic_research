# hunt_B_mine.py — exhaustive separator mining over true-context features (FAMILY B hunt).
import os, sys, itertools
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hunt_B_sim as H

OUT = H.OUT

def ema(x, n):
    a = 2.0 / (n + 1)
    out = np.empty_like(x)
    out[0] = x[0]
    for i in range(1, len(x)):
        out[i] = out[i-1] + a * (x[i] - out[i-1])
    return out

def build_matrix():
    bars = H.get_bars()
    ctx = H.make_ctx(bars)
    lab = H.load_labels().sort_values("entry_time").reset_index(drop=True)
    t = bars["time"]; c = bars["close"]; o = bars["open"]; hgh = bars["high"]; low = bars["low"]
    v = bars["volume"]; st = bars["signal_trade"]
    tidx = {str(x): i for i, x in enumerate(t)}
    lab["entry_i"] = [tidx[x] for x in lab["entry_time"]]

    # base run for exit times (true exits == base exits for taken trades)
    tr = H.run_gated(bars, ctx, lambda i, d, p: True)
    trd = pd.DataFrame(tr)
    trd = trd[pd.to_datetime(trd["entry_time"]) < "2023-01-21"].reset_index(drop=True)
    assert (trd["entry_time"].values == lab["entry_time"].values).all()
    lab["exit_i"] = trd["exit_i"].values
    lab["pnl"] = trd["pnl"].values
    lab["entry_px"] = trd["entry_px"].values

    emas = {n: ema(c, n) for n in (20, 60, 120, 240, 480, 960, 1440)}
    flip_bars = np.where(np.abs(st) == 1)[0]

    # true-context sequential stats
    take = lab[lab.label == "TAKE"].reset_index(drop=True)
    feats = []
    for k, r in lab.iterrows():
        i = r["entry_i"]; s = i - 1
        d = 1 if r["dir"] == "L" else -1
        sidx = ctx["sid"][s]
        so = ctx["sopen"][sidx]; sl = ctx["slast"][sidx]
        # true-stream prior trades THIS session (taken, entry before s)
        sess_end = str(t[sl].astype("datetime64[D]"))
        prior = take[(take.session_end_day == sess_end) & (take.entry_i <= s)]
        pnl_seq = prior["pnl"].tolist()
        dir_seq = prior["dir"].tolist()
        consec = 0
        for p in reversed(pnl_seq):
            if p < 0: consec += 1
            else: break
        consec_dir = 0
        for p, dd in zip(reversed(pnl_seq), reversed(dir_seq)):
            if dd == r["dir"]:
                if p < 0: consec_dir += 1
                else: break
        my = [p for p, dd in zip(pnl_seq, dir_seq) if dd == r["dir"]]
        opp = [p for p, dd in zip(pnl_seq, dir_seq) if dd != r["dir"]]
        # open position (true ctx): last prior trade with exit_i > s
        open_tr = prior[prior.exit_i > s]
        is_rev = len(open_tr) > 0
        open_pnl = 0.0; open_hold = 0.0
        if is_rev:
            q = open_tr.iloc[-1]
            pd_ = 1 if q["dir"] == "L" else -1
            open_pnl = pd_ * (c[s] - q["entry_px"]) * 20.0
            open_hold = s - q["entry_i"]
        nflip120 = int(((flip_bars >= s - 120) & (flip_bars < s)).sum())
        nflip240 = int(((flip_bars >= s - 240) & (flip_bars < s)).sum())
        shi = hgh[so:s+1].max(); slo = low[so:s+1].min()
        f = dict(
            entry_time=r["entry_time"], label=r["label"], cert=r["certainty"],
            sess=r["session_end_day"], dirn=d, is_rev=int(is_rev),
            mod=ctx["mod"][s], dow=ctx["dow"][s],
            bars_open=int(ctx["bars_since_open"][s]), bars_close=int(ctx["bars_to_close"][s]),
            gap_days=int(ctx["gap_days_sess"][sidx]), prev_len=int(ctx["prev_len_sess"][sidx]),
            ntr=len(pnl_seq), cum=sum(pnl_seq), cum_my=sum(my), cum_opp=sum(opp),
            consec=consec, consec_dir=consec_dir,
            last_pnl=pnl_seq[-1] if pnl_seq else 0.0,
            last_my=my[-1] if my else 0.0,
            last2_my=sum(my[-2:]) if len(my) >= 2 else (my[-1] if my else 0.0),
            open_pnl=open_pnl, open_hold=open_hold,
            nflip120=nflip120, nflip240=nflip240,
            vol=v[s],
            c_open=c[s]-o[so], c_prevc=c[s]-c[so-1] if so > 0 else 0.0,
            rangepos=(c[s]-slo)/max(shi-slo, 1e-9), sessrange=shi-slo,
        )
        for n, e in emas.items():
            f[f"c_ema{n}"] = c[s] - e[s]
            f[f"d_ema{n}"] = d * (c[s] - e[s])
        # would-be pnl of skipping? no. leg features:
        f["dc_open"] = d * f["c_open"]
        f["dcum"] = f["cum"]
        f["d_last_pnl"] = f["last_pnl"]
        feats.append(f)
    return pd.DataFrame(feats)


if __name__ == "__main__":
    M = build_matrix()
    M.to_csv(os.path.join(OUT, "hunt_B_matrix.csv"), index=False)
    hard = M[(M.cert == "HARD") | (M.sess.isin(H.HARD_SESS))].copy()
    # HARD labels = rows on hard sessions (all cent-certain) + hard-cert rows elsewhere
    y = (hard.label == "SKIP").astype(int).values
    print("hard rows:", len(hard), "skips:", y.sum())
    numcols = [cc for cc in hard.columns if hard[cc].dtype != object and cc not in ("dirn",)]
    results = []
    for col in numcols:
        x = hard[col].values.astype(float)
        for thr in np.unique(x):
            for op in ("<=", ">="):
                pred = (x <= thr) if op == "<=" else (x >= thr)
                tp = int((pred & (y == 1)).sum()); fp = int((pred & (y == 0)).sum())
                if tp == y.sum() and fp <= 2:
                    results.append((col, op, thr, tp, fp))
    print("single rules catching ALL hard skips with <=2 false positives:")
    for r in sorted(results, key=lambda z: z[4]):
        print("  ", r)
