"""G2_F1_COND01_20260829 — conditioner diagnostic on ORB01's FROZEN action set.

Preregistered spec: runs/G2_F1_COND01_20260829/spec.yaml (FROZEN).
Ambiguity resolutions: out/spec_resolutions.txt (written before any affected number).
Ledger trials: A_NR7 = G00017, B_RV3 = G00018. Gate table PRINTED BY THIS PROGRAM.

No parameter search occurs in this file: NR7's 7, RV's 21(+1 close), terciles, t >= 2.0,
300 family reps and seed 0 are spec/resolution constants. Trades are consumed READ-ONLY.
No VIX read. No data_esnq read. No sealed read.
"""
from __future__ import annotations

import json
import math
import os
import sys
from datetime import date

import numpy as np
import pandas as pd

REPO = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, REPO)

from research_sdk.seal_guard import assert_presealed, truncate_presealed
from research_sdk.session_boundary import assert_not_locked_forward

RUN_DIR = os.path.join(REPO, "runs", "G2_F1_COND01_20260829")
OUT = os.path.join(RUN_DIR, "out")

TRADES_CSV = os.path.join(REPO, r"runs\G2_F1_ORB01_20260829\out\trades.csv")
MODERN_PARQUET = os.path.join(REPO, r"runs\SM1M_SUBSTRATE\out\nq_1m_2022_2026.parquet")

GATE_FIRST, GATE_LAST = date(2022, 1, 1), date(2026, 7, 31)
RTH_LO, RTH_HI = 9 * 60 + 31, 16 * 60  # stamps 09:31..16:00 (END-stamped (09:30,16:00])
N_NR = 7          # NR7: prior session narrowest of trailing 7 (frozen)
N_RV_RETS = 21    # 21 close-to-close returns from 22 trailing closes (frozen)
N_REPS = 300      # CF replications (spec >= 300)
SEED = 0


def welch_t(a: np.ndarray, b: np.ndarray) -> tuple[float, float, float]:
    """(contrast a-b, Welch SE, t). With one trade per session (asserted in main),
    the session-clustered contrast t reduces exactly to this."""
    na, nb = len(a), len(b)
    ma, mb = float(np.mean(a)), float(np.mean(b))
    va = float(np.var(a, ddof=1))
    vb = float(np.var(b, ddof=1))
    se = math.sqrt(va / na + vb / nb)
    c = ma - mb
    return c, se, (c / se if se > 0 else float("inf") * np.sign(c or 1))


def main() -> None:
    print("data_esnq NOT read by this run (no ES leg in spec) — ALLOWLIST_DEV_44 not exercised.")
    print("NO VIX read of any kind (governance ruling: realized vol only).")

    # ---------------- frozen action set (READ-ONLY) ----------------
    trades = pd.read_csv(TRADES_CSV)
    assert list(trades.columns) == ["session_id", "entry_ts", "direction",
                                    "entry_px", "exit_px", "gross_pts", "net_usd"]
    assert_presealed(trades, "session_id", "COND01:trades")  # frozen set itself certified pre-seal
    assert trades["session_id"].is_unique, "expected exactly one trade per session (ORB01 guarantee)"
    tsess = pd.to_datetime(trades["session_id"]).dt.date.to_numpy()
    assert tsess.min() >= GATE_FIRST and tsess.max() <= GATE_LAST
    net = trades["net_usd"].to_numpy(dtype=float)
    is_long = (trades["direction"] == "long").to_numpy()
    n_trades = len(trades)
    print(f"frozen action set: {n_trades} trades, one per session, "
          f"{tsess.min()} .. {tsess.max()}, total net ${net.sum():,.2f} at $25.01/RT")

    # ---------------- conditioner substrate (seal-guarded) ----------------
    df = pd.read_parquet(MODERN_PARQUET, columns=["time", "high", "low", "close"])
    df, n_dropped = truncate_presealed(df, "time", "COND01:modern")
    assert_presealed(df, "time", "COND01:modern:post-truncate")
    print(f"seal_guard PASS [COND01:modern]: {n_dropped} sealed row(s) mechanically dropped, "
          f"frame certified pre-seal")
    assert_not_locked_forward(GATE_LAST)
    t = df["time"]
    df["session"] = t.dt.date.where(t.dt.hour < 18, (t + pd.Timedelta(days=1)).dt.date)
    df = df[(df["session"] >= GATE_FIRST) & (df["session"] <= GATE_LAST)]
    mod = df["time"].dt.hour * 60 + df["time"].dt.minute
    df = df[(mod >= RTH_LO) & (mod <= RTH_HI)]  # RTH 09:30-16:00 => stamps 09:31..16:00 (R3)
    df = df.sort_values("time", kind="stable")

    g = df.groupby("session", sort=True)
    ser = pd.DataFrame({"range": g["high"].max() - g["low"].min(),
                        "close": g["close"].last()})
    sess_arr = np.array(ser.index.to_list())          # ascending session dates
    ranges = ser["range"].to_numpy(dtype=float)
    closes = ser["close"].to_numpy(dtype=float)
    print(f"conditioner series: {len(ser)} sessions with RTH(09:30-16:00) bars, "
          f"{sess_arr[0]} .. {sess_arr[-1]}")

    # ---------------- causal states per trade session ----------------
    idx = np.searchsorted(sess_arr, tsess)            # position of trade session in series
    in_series = (idx < len(sess_arr))
    in_series &= np.array([idx[i] < len(sess_arr) and sess_arr[idx[i]] == tsess[i]
                           for i in range(n_trades)])
    print(f"trade sessions present in conditioner series: {int(in_series.sum())}/{n_trades}")

    nr7_def = in_series & (idx >= N_NR)
    nr7_state = np.zeros(n_trades, dtype=bool)
    for i in np.flatnonzero(nr7_def):
        j = idx[i]
        r1 = ranges[j - 1]                            # prior session
        others = ranges[j - N_NR: j - 1]              # the 6 before it
        nr7_state[i] = r1 < others.min()              # STRICT narrowest (R4)

    rv_def = in_series & (idx >= N_RV_RETS + 1)
    rv = np.full(n_trades, np.nan)
    for i in np.flatnonzero(rv_def):
        j = idx[i]
        c = closes[j - (N_RV_RETS + 1): j]            # 22 trailing closes strictly before t
        r = np.diff(np.log(c))                        # 21 close-to-close log returns
        rv[i] = float(np.std(r, ddof=1))

    q33, q66 = np.quantile(rv[rv_def], [1.0 / 3.0, 2.0 / 3.0])
    terc = np.full(n_trades, "", dtype=object)
    terc[rv_def & (rv <= q33)] = "bottom"
    terc[rv_def & (rv >= q66)] = "top"
    terc[rv_def & (rv > q33) & (rv < q66)] = "middle"

    n_excl_a = int(n_trades - nr7_def.sum())
    n_excl_b = int(n_trades - rv_def.sum())

    # ---------------- real contrasts ----------------
    a_in = nr7_def & nr7_state
    a_out = nr7_def & ~nr7_state
    cA, seA, tA = welch_t(net[a_in], net[a_out])
    mA_in = float(np.mean(net[a_in]))

    b_top = rv_def & (terc == "top")
    b_bot = rv_def & (terc == "bottom")
    b_mid = rv_def & (terc == "middle")
    cB, seB, tB = welch_t(net[b_top], net[b_bot])
    mB_top = float(np.mean(net[b_top]))

    # ---------------- CF shared family null (one draw per rep across BOTH conditioners) ----------------
    rng = np.random.default_rng(SEED)
    nA_in = int(a_in.sum())
    nB_top, nB_bot = int(b_top.sum()), int(b_bot.sum())
    A_pop = np.flatnonzero(nr7_def)
    B_pop = np.flatnonzero(rv_def)
    fam = np.empty(N_REPS)
    for rep in range(N_REPS):
        u = rng.random(n_trades)                      # THE one shared draw for this rep
        oa = A_pop[np.argsort(u[A_pop], kind="stable")]
        pin = oa[:nA_in]
        pout = oa[nA_in:]
        _, _, ta_ = welch_t(net[pin], net[pout])
        ob = B_pop[np.argsort(u[B_pop], kind="stable")]
        pbot = ob[:nB_bot]                            # count-matched bottom = smallest u
        ptop = ob[len(ob) - nB_top:]                  # count-matched top = largest u
        _, _, tb_ = welch_t(net[ptop], net[pbot])
        fam[rep] = max(abs(ta_), abs(tb_))
    fam_p95 = float(np.percentile(fam, 95))
    cfA = abs(tA) > fam_p95
    cfB = abs(tB) > fam_p95

    # ---------------- gates ----------------
    ca = (cA > 0) and (tA >= 2.0) and (mA_in > 0)
    cb = (cB > 0) and (tB >= 2.0) and (mB_top > 0)
    verd_a = "SURVIVED-DISCOVERY" if (ca and cfA) else "NULL"
    verd_b = "SURVIVED-DISCOVERY" if (cb and cfB) else "NULL"

    mdeA = 2.0 * seA
    mdeB = 2.0 * seB

    # ---------------- contrast tables csv ----------------
    def grp(name: str, group: str, m: np.ndarray) -> dict:
        sel = net[m]
        return dict(conditioner=name, group=group, n=int(m.sum()),
                    n_long=int((m & is_long).sum()), n_short=int((m & ~is_long).sum()),
                    mean_net=round(float(np.mean(sel)), 2) if m.any() else float("nan"),
                    sd_net=round(float(np.std(sel, ddof=1)), 2) if m.sum() > 1 else float("nan"),
                    total_net=round(float(np.sum(sel)), 2))

    rows = [
        grp("A_NR7", "in_state", a_in), grp("A_NR7", "out_of_state", a_out),
        dict(conditioner="A_NR7", group="CONTRAST(in-out)", n=int(nr7_def.sum()),
             n_long=None, n_short=None, mean_net=round(cA, 2), sd_net=round(seA, 2),
             total_net=round(tA, 4)),
        grp("B_RV3", "top", b_top), grp("B_RV3", "middle", b_mid), grp("B_RV3", "bottom", b_bot),
        dict(conditioner="B_RV3", group="CONTRAST(top-bottom)", n=int(nB_top + nB_bot),
             n_long=None, n_short=None, mean_net=round(cB, 2), sd_net=round(seB, 2),
             total_net=round(tB, 4)),
    ]
    ct = pd.DataFrame(rows)
    ct.to_csv(os.path.join(OUT, "contrast_tables.csv"), index=False)

    # ---------------- gate table (printed by program) ----------------
    L = []
    A = L.append
    A("G2_F1_COND01_20260829 — GATE TABLE (printed by program; ledger trials G00017 A_NR7, G00018 B_RV3)")
    A("conditioner diagnostic on ORB01's FROZEN action set (runs regardless of ORB01's NULL verdict);")
    A("conditioners add ZERO trades; matched control = the unconditional set itself; NO VIX read (realized vol only)")
    A(f"window sessions {GATE_FIRST} .. {GATE_LAST} | frozen trades {n_trades} (one per session) | "
      f"conditioner-series sessions {len(ser)}")
    A("evidence status: DISCOVERY_CONSUMED (window includes the burned 2026-05-31..07-31 span; no sealed reads)")
    A("")
    A(f"populations: A_NR7 defined {int(nr7_def.sum())} trades (excluded {n_excl_a} warm-up), "
      f"in-state {nA_in} / out {int(a_out.sum())};")
    A(f"             B_RV3 defined {int(rv_def.sum())} trades (excluded {n_excl_b} warm-up), "
      f"top {nB_top} / middle {int(b_mid.sum())} / bottom {nB_bot}; "
      f"RV tercile breakpoints q33={q33:.6f} q66={q66:.6f} (21-ret c2c log sd, unannualized)")
    A("")
    A(f"{'GATE':<6}{'SPEC':<62}{'OBSERVED':<70}{'PASS-FAIL'}")
    A(f"{'CA':<6}{'NR7 contrast > 0, t >= 2.0, in-state mean > 0 @ $25.01':<62}"
      f"{f'contrast ${cA:,.2f}/trade (t = {tA:.3f}), in-state mean ${mA_in:,.2f} ({nA_in} tr)':<70}"
      f"{'PASS' if ca else 'FAIL'}")
    A(f"{'CB':<6}{'RV top-vs-bottom contrast > 0, t >= 2.0, top mean > 0':<62}"
      f"{f'contrast ${cB:,.2f}/trade (t = {tB:.3f}), top mean ${mB_top:,.2f} ({nB_top} tr)':<70}"
      f"{'PASS' if cb else 'FAIL'}")
    A(f"{'CF-A':<6}{'family max-|t| null p95 (300 shared count-matched reps)':<62}"
      f"{f'|t_A| = {abs(tA):.3f} vs family p95 = {fam_p95:.3f}':<70}"
      f"{'PASS' if cfA else 'FAIL'}")
    A(f"{'CF-B':<6}{'family max-|t| null p95 (300 shared count-matched reps)':<62}"
      f"{f'|t_B| = {abs(tB):.3f} vs family p95 = {fam_p95:.3f}':<70}"
      f"{'PASS' if cfB else 'FAIL'}")
    A("")
    A(f"CF null detail: {N_REPS} reps, seed {SEED}, ONE shared U(0,1) draw per rep across both "
      f"conditioners (dependence preserved); count-matched to observed state counts; nets never permuted; "
      f"family max-|t| distribution: p50={float(np.percentile(fam, 50)):.3f} "
      f"p95={fam_p95:.3f} max={float(fam.max()):.3f}")
    A(f"group means: NR7 in ${mA_in:,.2f} (n={nA_in}) vs out ${float(np.mean(net[a_out])):,.2f} "
      f"(n={int(a_out.sum())}); RV top ${mB_top:,.2f} (n={nB_top}) vs middle "
      f"${float(np.mean(net[b_mid])):,.2f} (n={int(b_mid.sum())}) vs bottom "
      f"${float(np.mean(net[b_bot])):,.2f} (n={nB_bot})")
    A(f"expected-sign check (non-gate): spec expects HIGH vol better; observed top-bottom contrast "
      f"{'matches' if cB > 0 else 'CONTRADICTS'} the expected sign")
    A("")
    A(f"MDE (printed before verdicts, non-gate): contrast needed for t=2.0 — "
      f"A_NR7 ${mdeA:,.2f}/trade (observed ${cA:,.2f}); B_RV3 ${mdeB:,.2f}/trade (observed ${cB:,.2f})")
    A(f"VERDICT A_NR7 (G00017): {verd_a}" + ("" if verd_a != "NULL" else " — closed at formulation"))
    A(f"VERDICT B_RV3 (G00018): {verd_b}" + ("" if verd_b != "NULL" else " — closed at formulation"))
    table = "\n".join(L)
    print(table)
    with open(os.path.join(OUT, "gate_table.txt"), "wb") as f:
        f.write(table.encode("utf-8"))

    # ---------------- ledger (LIST of 2) ----------------
    common = dict(window="2022-01-01..2026-07-31 sessions (ORB01 frozen action set, $25.01/RT nets)",
                  n_frozen_trades=n_trades, cf_family_p95_abs_t=round(fam_p95, 4),
                  cf_n_reps=N_REPS, cf_seed=SEED, evidence_status="DISCOVERY_CONSUMED")
    ledger = [
        {"trial_id": "G00017",
         "metrics": {**common, "conditioner": "A_NR7",
                     "n_defined": int(nr7_def.sum()), "n_excluded_warmup": n_excl_a,
                     "n_in_state": nA_in, "n_out_state": int(a_out.sum()),
                     "in_state_mean_net": round(mA_in, 2),
                     "out_state_mean_net": round(float(np.mean(net[a_out])), 2),
                     "contrast_usd_per_trade": round(cA, 2), "welch_se": round(seA, 2),
                     "t_session_clustered": round(tA, 4),
                     "mde_contrast_t2": round(mdeA, 2),
                     "gates": {"CA": bool(ca), "CF": bool(cfA)}},
         "result": verd_a,
         "note": ("Prior-session NR7 (strict narrowest of trailing 7, RTH 09:30-16:00) on ORB01's frozen "
                  "action set; card MC-20. Session-clustered t = Welch (one trade/session). "
                  "Resolutions in out/spec_resolutions.txt.")},
        {"trial_id": "G00018",
         "metrics": {**common, "conditioner": "B_RV3",
                     "n_defined": int(rv_def.sum()), "n_excluded_warmup": n_excl_b,
                     "n_top": nB_top, "n_middle": int(b_mid.sum()), "n_bottom": nB_bot,
                     "rv_q33": round(float(q33), 6), "rv_q66": round(float(q66), 6),
                     "top_mean_net": round(mB_top, 2),
                     "middle_mean_net": round(float(np.mean(net[b_mid])), 2),
                     "bottom_mean_net": round(float(np.mean(net[b_bot])), 2),
                     "contrast_top_minus_bottom_usd": round(cB, 2), "welch_se": round(seB, 2),
                     "t_session_clustered": round(tB, 4),
                     "mde_contrast_t2": round(mdeB, 2),
                     "expected_sign_high_vol_better": bool(cB > 0),
                     "gates": {"CB": bool(cb), "CF": bool(cfB)}},
         "result": verd_b,
         "note": ("Trailing 21-session realized vol (close-to-close, causal) terciles, top-vs-bottom, on "
                  "ORB01's frozen action set; card MC-22 RESTRUCTURED (realized vol only — NO VIX read; "
                  "pristine VX window untouched). Resolutions in out/spec_resolutions.txt.")},
    ]
    with open(os.path.join(OUT, "ledger_result_pending.json"), "wb") as f:
        f.write(json.dumps(ledger, indent=2).encode("utf-8"))
    print("\noutputs written: gate_table.txt, contrast_tables.csv, ledger_result_pending.json")


if __name__ == "__main__":
    main()
