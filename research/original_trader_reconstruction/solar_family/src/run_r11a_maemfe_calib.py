"""R11-A: calibrate a Python MAE/MFE/ETD oracle against NT8's own serialized trades.

Directive v4.0 P1 / section 5. Oracle = runs/OTR_R6_NT8_PARITY/out/layerA_nt8_raw.json,
which carries NT8's MaeCurrency / MfeCurrency / EtdCurrency for 90 real Strategy Analyzer
trades. Accept a definition ONLY at 90/90 exact.

Also answers, as a by-product, whether our parquet bar substrate reproduces NT8's
HIGH/LOW (MAE/MFE depend on them; net PnL does not).
"""
import json
import os
import sys

import numpy as np
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
OUT = os.path.join(ROOT, "runs", "OTR_R11_INVERSE", "out")
os.makedirs(OUT, exist_ok=True)
POINT_VALUE = 20.0


def load_bars(lo="2022-12-20", hi="2023-01-20"):
    df = pd.read_parquet(os.path.join(ROOT, "research", "scalping_lab", "substrate",
                                      "minute", "NQ", "nq1m_2005_202605.parquet"))
    df["time"] = pd.to_datetime(df["time"])
    seg = df[(df["time"] >= lo) & (df["time"] <= hi)].reset_index(drop=True)
    return seg


def main():
    raw = json.load(open(os.path.join(ROOT, "runs", "OTR_R6_NT8_PARITY", "out",
                                      "layerA_nt8_raw.json")))
    tr = raw["trades"]
    bars = load_bars()
    t = bars["time"].values.astype("datetime64[m]")
    o, h, l, c = (bars[k].values for k in ("open", "high", "low", "close"))
    idx = {str(x): i for i, x in enumerate(t)}

    # ---- variant definitions ---------------------------------------------------
    # bar-range variants: which bars contribute to the excursion scan.
    # `tail` = extra prices folded in for the exit bar (NT8 has no intrabar path
    # without Tick Replay, so on the exit bar it can only know discrete prices).
    RANGES = {
        "incl_entry_incl_exit": (lambda a, b: (a, b + 1), ()),
        "excl_entry_incl_exit": (lambda a, b: (a + 1, b + 1), ()),
        "incl_entry_excl_exit": (lambda a, b: (a, b), ()),
        "exclexitbar_plus_exitpx": (lambda a, b: (a, b), ("xpx",)),
        "exclexitbar_plus_exitopen": (lambda a, b: (a, b), ("xopen",)),
        "exclexitbar_plus_both": (lambda a, b: (a, b), ("xpx", "xopen")),
    }
    # price-basis variants: bar extremes vs closes
    BASES = {"hilo": (h, l), "close": (c, c)}

    results = {}
    detail_best = None
    for rname, (rfn, tail) in RANGES.items():
        for bname, (hi_arr, lo_arr) in BASES.items():
            okm = okf = oke = n_used = 0
            worst = []
            for x in tr:
                et, xt = x["entry"]["time"][:16], x["exit"]["time"][:16]
                ei, xi = idx.get(et), idx.get(xt)
                if ei is None or xi is None:
                    continue
                n_used += 1
                a, b = rfn(ei, xi)
                a = max(a, 0); b = min(b, len(t))
                if b <= a:
                    a, b = ei, ei + 1
                dirn = 1 if x["entry"]["market_position"] == "Long" else -1
                epx = x["entry"]["price"]
                extra = []
                if "xpx" in tail:
                    extra.append(x["exit"]["price"])
                if "xopen" in tail and xi < len(t):
                    extra.append(float(o[xi]))
                hi_v = max([float(np.max(hi_arr[a:b]))] + extra)
                lo_v = min([float(np.min(lo_arr[a:b]))] + extra)
                if dirn > 0:
                    mae = max(0.0, epx - lo_v)
                    mfe = max(0.0, hi_v - epx)
                else:
                    mae = max(0.0, hi_v - epx)
                    mfe = max(0.0, epx - lo_v)
                mae_c, mfe_c = mae * POINT_VALUE, mfe * POINT_VALUE
                etd_c = mfe_c - x["ProfitCurrency"]
                dm = abs(mae_c - x["MaeCurrency"]); df_ = abs(mfe_c - x["MfeCurrency"])
                okm += dm < 1e-6; okf += df_ < 1e-6
                oke += abs(etd_c - mfe_c + x["ProfitCurrency"]) < 1e-6
                if dm > 1e-6 or df_ > 1e-6:
                    worst.append((x["TradeNumber"], et, xt, dirn, mae_c,
                                  x["MaeCurrency"], mfe_c, x["MfeCurrency"]))
            key = f"{rname}|{bname}"
            results[key] = dict(n=n_used, mae_exact=okm, mfe_exact=okf,
                                mae_pct=round(100 * okm / max(n_used, 1), 2),
                                mfe_pct=round(100 * okf / max(n_used, 1), 2))
            print(f"{key:34} n={n_used:3d}  MAE {okm:3d}/{n_used} ({100*okm/max(n_used,1):6.2f}%)"
                  f"  MFE {okf:3d}/{n_used} ({100*okf/max(n_used,1):6.2f}%)")
            if okm == n_used and okf == n_used and n_used:
                detail_best = key
            if worst and len(worst) <= 6:
                for w in worst:
                    print(f"     miss #{w[0]} {w[1]}->{w[2]} dir{w[3]:+d} "
                          f"MAE py={w[4]:.1f} nt={w[5]:.1f}  MFE py={w[6]:.1f} nt={w[7]:.1f}")

    # ---- UNIFIED RULE ----------------------------------------------------------
    # NT8 has no intrabar path without Tick Replay. It can only have seen the bars whose
    # CLOSE the position survived, plus the fill price itself. So:
    #   scan bars [entry_bar .. last_bar_held_through_close] with full High/Low,
    #   then fold in the exit fill price.
    # last_bar_held_through_close = exit_bar-1 for a next-bar-OPEN fill (the decision was
    # taken at the previous close), and exit_bar for an AT-CLOSE fill (session close).
    print("\n=== UNIFIED RULE (fill-type aware) ===")
    okm = okf = 0
    miss = []
    for x in tr:
        et, xt = x["entry"]["time"][:16], x["exit"]["time"][:16]
        ei, xi = idx[et], idx[xt]
        xpx = x["exit"]["price"]
        at_close = abs(xpx - float(c[xi])) < 1e-9 and abs(xpx - float(o[xi])) > 1e-9
        b = xi + 1 if at_close else xi
        b = max(b, ei + 1)
        hi_v = max(float(np.max(h[ei:b])), xpx)
        lo_v = min(float(np.min(l[ei:b])), xpx)
        dirn = 1 if x["entry"]["market_position"] == "Long" else -1
        epx = x["entry"]["price"]
        mae = (epx - lo_v) if dirn > 0 else (hi_v - epx)
        mfe = (hi_v - epx) if dirn > 0 else (epx - lo_v)
        mae_c, mfe_c = max(0.0, mae) * POINT_VALUE, max(0.0, mfe) * POINT_VALUE
        okm += abs(mae_c - x["MaeCurrency"]) < 1e-6
        okf += abs(mfe_c - x["MfeCurrency"]) < 1e-6
        if abs(mae_c - x["MaeCurrency"]) > 1e-6 or abs(mfe_c - x["MfeCurrency"]) > 1e-6:
            miss.append((x["TradeNumber"], et, xt, at_close, mae_c, x["MaeCurrency"],
                         mfe_c, x["MfeCurrency"]))
    print(f"  MAE {okm}/{len(tr)}   MFE {okf}/{len(tr)}")
    for m in miss[:8]:
        print(f"     miss #{m[0]} {m[1]}->{m[2]} at_close={m[3]} "
              f"MAE py={m[4]:.1f} nt={m[5]:.1f}  MFE py={m[6]:.1f} nt={m[7]:.1f}")
    results["UNIFIED_fill_type_aware"] = dict(n=len(tr), mae_exact=okm, mfe_exact=okf)
    if okm == len(tr) and okf == len(tr):
        detail_best = "UNIFIED_fill_type_aware"

    # ---- ETD identity ---------------------------------------------------------
    etd_ok = sum(abs((x["MfeCurrency"] - x["ProfitCurrency"]) -
                     x.get("EtdCurrency", x["MfeCurrency"] - x["ProfitCurrency"])) < 1e-6
                 for x in tr)
    print(f"\nETD identity (ETD == MFE - ProfitCurrency): {etd_ok}/{len(tr)}")

    # ---- evening-exit separability of the two day-grouping rules ---------------
    ev = sum(1 for x in tr if 18 <= int(x["exit"]["time"][11:13]) <= 23)
    print(f"trades exiting 18:00-23:59 (the only case where CAL vs SESS grouping differ): {ev}")

    json.dump(dict(variants=results, winner=detail_best, etd_identity_exact=etd_ok,
                   n_trades=len(tr), evening_exits=ev),
              open(os.path.join(OUT, "mae_mfe_calibration.json"), "w"), indent=2)
    print(f"\nWINNER: {detail_best}")


if __name__ == "__main__":
    main()
