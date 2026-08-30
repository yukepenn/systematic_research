"""G2_AUG_INCUMBENT_READ — parse the two NT8 Strategy Analyzer jobs, print the August read
with its mandatory Jan-Jul parity cross-check. Executes the frozen spec; prints, never asserts
a verdict the spec did not preregister."""
import json, sys, os
import pandas as pd

RUN = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(RUN, "out")
os.makedirs(OUT, exist_ok=True)


def load(path):
    d = json.load(open(path, encoding="utf-8"))
    r = d["result"] if "result" in d else d
    rows = [dict(et=x["entry"]["time"], xt=(x.get("exit") or {}).get("time"),
                 qty=x["Quantity"], pnl=x["ProfitCurrency"], comm=x["Commission"])
            for x in r["trades"]]
    T = pd.DataFrame(rows)
    T["et"] = pd.to_datetime(T.et); T["xt"] = pd.to_datetime(T.xt)
    T["m"] = T.et.dt.strftime("%Y-%m")
    T["wk"] = T.et.dt.strftime("%G-W%V")
    return T, r


def main(p1_path, xm_path):
    P, rp = load(p1_path)
    X, rx = load(xm_path)
    lines = []
    def say(s=""):
        print(s); lines.append(s)

    say("G2_AUG_INCUMBENT_READ — NT8 Strategy Analyzer, certified .cs, NQ 09-26 1-min")
    say(f"P1 window {P.et.min()} .. {P.et.max()}  n={len(P)}")
    say(f"XM window {X.et.min()} .. {X.et.max()}  n={len(X)}")
    say("COST CONVENTION: NT8 template commission, ZERO modeled spread. Research adds "
        "$20.65/ctrRT (P1, measured) or $12.50 (XM, modeled). NOT the same quantity.")
    say()

    # --- mandatory parity cross-check on the consumed window (Jan-Jul 2026) ---
    pj = P[(P.m >= "2026-01") & (P.m <= "2026-07")]
    xj = X[(X.m >= "2026-01") & (X.m <= "2026-07")]
    say("PARITY CROSS-CHECK (2026 Jan-Jul, consumed window; Python figures are net of modeled "
        "spread, NT8 is not — the NT8 side should be HIGHER by roughly the spread):")
    say(f"  P1  NT8 gross-of-spread ${pj.pnl.sum():,.0f} on {len(pj)} trades "
        f"| Python net ${42481:,.0f} on 245 trades | spread they differ by ≈ "
        f"${14.44*pj.qty.sum():,.0f}")
    say(f"  XM  NT8 ${xj.pnl.sum():,.0f} on {len(xj)} trades | Python net ${39649:,.0f} on 54")
    say()

    say("MONTHLY (NT8 convention):")
    M = pd.DataFrame({"P1": P.groupby("m").pnl.sum(), "P1_n": P.groupby("m").size(),
                      "XM": X.groupby("m").pnl.sum(), "XM_n": X.groupby("m").size()}).fillna(0)
    M["COMBO"] = M.P1 + M.XM
    say(M.loc["2026-01":].round(0).to_string())
    say()

    for label, df in (("P1", P), ("XM", X)):
        A = df[df.m == "2026-08"]
        say(f"=== AUGUST 2026 — {label} ===")
        if len(A) == 0:
            say("  no trades"); continue
        say(f"  trades {len(A)} | ctrRT {A.qty.sum()} | net ${A.pnl.sum():,.0f} "
            f"| mean ${A.pnl.mean():,.0f} | win {(A.pnl>0).mean():.1%}")
        say(f"  best ${A.pnl.max():,.0f} | worst ${A.pnl.min():,.0f} | "
            f"top-1 share of net {A.pnl.max()/A.pnl.sum()*100:.0f}%" if A.pnl.sum() else "")
        A.to_csv(os.path.join(OUT, f"{label.lower()}_august_trades.csv"), index=False)
        say()

    PA, XA = P[P.m == "2026-08"], X[X.m == "2026-08"]
    say("=== AUGUST 2026 — COMBINED (M_11) ===")
    say(f"  NT8 convention net ${PA.pnl.sum()+XA.pnl.sum():,.0f} "
        f"({len(PA)}+{len(XA)} trades)")
    adj = 20.65*PA.qty.sum() + 12.50*XA.qty.sum()
    say(f"  research-convention estimate (subtract measured/modeled spread ${adj:,.0f}): "
        f"${PA.pnl.sum()+XA.pnl.sum()-adj:,.0f}")
    say()
    W = pd.DataFrame({"P1": PA.groupby("wk").pnl.sum(), "XM": XA.groupby("wk").pnl.sum()}).fillna(0)
    W["COMBO"] = W.P1 + W.XM
    say("August weekly (NT8 convention):")
    say(W.round(0).to_string())

    P.to_csv(os.path.join(OUT, "p1_trades_full.csv"), index=False)
    X.to_csv(os.path.join(OUT, "xm_trades_full.csv"), index=False)
    open(os.path.join(OUT, "august_read.txt"), "w", encoding="utf-8").write("\n".join(lines))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
