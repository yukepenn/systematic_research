"""Row-identity comparator: hardened vs certified NT8 backtest trade lists.

PASS requires 100% row identity on (entry time, exit time, qty, entry px, exit px, P&L).
Prints a GATE / SPEC / OBSERVED / PASS-FAIL table from the program.
"""
import json
import sys
import csv


FIELDS = [
    ("entry_time", lambda t: t["entry"]["time"]),
    ("exit_time", lambda t: t["exit"]["time"]),
    ("qty", lambda t: t["Quantity"]),
    ("entry_px", lambda t: t["entry"]["price"]),
    ("exit_px", lambda t: t["exit"]["price"]),
    ("pnl", lambda t: t["ProfitCurrency"]),
]

EXTRA = [
    ("entry_name", lambda t: t["entry"]["name"]),
    ("exit_name", lambda t: t["exit"]["name"]),
    ("entry_action", lambda t: t["entry"]["order_action"]),
    ("exit_action", lambda t: t["exit"]["order_action"]),
    ("entry_mp", lambda t: t["entry"]["market_position"]),
    ("commission", lambda t: t["Commission"]),
    ("mae_cur", lambda t: t["MaeCurrency"]),
    ("mfe_cur", lambda t: t["MfeCurrency"]),
]


def row(t, fields):
    return tuple(f(t) for _, f in fields)


def load(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)["result"]


def dump_csv(trades, path, fields):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["trade_no"] + [n for n, _ in fields])
        for t in trades:
            w.writerow([t["TradeNumber"]] + list(row(t, fields)))


def main(cert_path, hard_path, label, outprefix):
    c = load(cert_path)
    h = load(hard_path)
    ct, ht = c["trades"], h["trades"]

    allf = FIELDS + EXTRA
    dump_csv(ct, outprefix + "_cert.csv", allf)
    dump_csv(ht, outprefix + "_hard.csv", allf)

    lines = []
    P = lines.append
    P("=" * 96)
    P("ROW-IDENTITY PROOF  %s" % label)
    P("  certified : %s   (%s)" % (c["strategy_full_name"], cert_path))
    P("  hardened  : %s   (%s)" % (h["strategy_full_name"], hard_path))
    P("  instrument=%s  from=%s  to=%s" % (c["instrument"], c["from"], c["to"]))
    P("=" * 96)

    n_c, n_h = len(ct), len(ht)
    n = min(n_c, n_h)

    # core 6-field comparison
    core_mm = []
    for i in range(n):
        a, b = row(ct[i], FIELDS), row(ht[i], FIELDS)
        if a != b:
            core_mm.append((i, a, b))
    # full comparison incl. names / mae / mfe
    full_mm = []
    for i in range(n):
        a, b = row(ct[i], allf), row(ht[i], allf)
        if a != b:
            full_mm.append((i, a, b))

    sum_c = sum(t["ProfitCurrency"] for t in ct)
    sum_h = sum(t["ProfitCurrency"] for t in ht)
    com_c = sum(t["Commission"] for t in ct)
    com_h = sum(t["Commission"] for t in ht)
    qty_c = sum(t["Quantity"] for t in ct)
    qty_h = sum(t["Quantity"] for t in ht)

    gates = [
        ("G1 trade count", "hardened == certified", "%d vs %d" % (n_h, n_c), n_h == n_c),
        ("G2 core row identity", "0 mismatched rows on (entry_t,exit_t,qty,entry_px,exit_px,pnl)",
         "%d mismatched of %d" % (len(core_mm), n), len(core_mm) == 0 and n_h == n_c),
        ("G3 extended row identity", "0 mismatched rows incl. signal names, commission, MAE, MFE",
         "%d mismatched of %d" % (len(full_mm), n), len(full_mm) == 0 and n_h == n_c),
        ("G4 closed-trade net", "identical to the cent", "%.2f vs %.2f" % (sum_h, sum_c),
         round(sum_h, 2) == round(sum_c, 2)),
        ("G5 total commission", "identical", "%.2f vs %.2f" % (com_h, com_c),
         round(com_h, 2) == round(com_c, 2)),
        ("G6 total quantity", "identical", "%d vs %d" % (qty_h, qty_c), qty_h == qty_c),
        ("G7 engine NetProfit", "identical (incl. open trade)",
         "%.2f vs %.2f" % (h["performance"]["all"]["NetProfit"], c["performance"]["all"]["NetProfit"]),
         round(h["performance"]["all"]["NetProfit"], 6) == round(c["performance"]["all"]["NetProfit"], 6)),
        ("G8 engine TradesCount", "identical",
         "%d vs %d" % (h["performance"]["all"]["TradesCount"], c["performance"]["all"]["TradesCount"]),
         h["performance"]["all"]["TradesCount"] == c["performance"]["all"]["TradesCount"]),
        ("G9 bars loaded", "identical bar set",
         "%s vs %s" % (_bars(h), _bars(c)), _bars(h) == _bars(c)),
        ("G10 equity curve", "identical point-for-point",
         _eq(h, c), _eqok(h, c)),
    ]

    P("")
    P("%-26s %-58s %-26s %s" % ("GATE", "SPEC", "OBSERVED", "VERDICT"))
    P("-" * 120)
    for g, s, o, ok in gates:
        P("%-26s %-58s %-26s %s" % (g, s, o, "PASS" if ok else "FAIL"))
    P("-" * 120)
    overall = all(ok for _, _, _, ok in gates)
    P("OVERALL: %s   (100%% row identity required)" % ("PASS" if overall else "FAIL"))
    P("")

    if core_mm or full_mm:
        P("OFFENDING ROWS (first 40, core fields):")
        P("  idx | field | certified | hardened")
        names = [nm for nm, _ in allf]
        for i, a, b in (core_mm or full_mm)[:40]:
            for j, nm in enumerate(names[:len(a)]):
                if a[j] != b[j]:
                    P("  %5d | %-13s | %-24s | %s" % (i, nm, a[j], b[j]))
        with open(outprefix + "_mismatches.csv", "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow(["idx", "field", "certified", "hardened"])
            names = [nm for nm, _ in allf]
            for i, a, b in (full_mm or core_mm):
                for j, nm in enumerate(names[:len(a)]):
                    if a[j] != b[j]:
                        w.writerow([i, nm, a[j], b[j]])
    else:
        P("OFFENDING ROWS: none. All %d rows byte-identical across all %d compared fields."
          % (n, len(allf)))

    txt = "\n".join(lines)
    print(txt)
    with open(outprefix + "_ROWIDENTITY.txt", "w", encoding="utf-8") as fh:
        fh.write(txt + "\n")
    return 0 if overall else 1


def _bars(r):
    for t in r["trace"]:
        if t.startswith("loaded "):
            return t
    return "?"


def _eq(h, c):
    a, b = h["equity_curve"], c["equity_curve"]
    if len(a) != len(b):
        return "len %d vs %d" % (len(a), len(b))
    d = sum(1 for x, y in zip(a, b) if x["t"] != y["t"] or abs(x["equity"] - y["equity"]) > 1e-6)
    return "%d/%d points differ" % (d, len(a))


def _eqok(h, c):
    a, b = h["equity_curve"], c["equity_curve"]
    return len(a) == len(b) and all(
        x["t"] == y["t"] and abs(x["equity"] - y["equity"]) <= 1e-6 for x, y in zip(a, b))


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
