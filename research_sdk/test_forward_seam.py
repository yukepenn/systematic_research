# -*- coding: utf-8 -*-
"""The SEAM test: every value shadow_runner can EMIT must be one the ledger ACCEPTS.

WHY THIS EXISTS (CLEANSET 4, 2026-09-01)
----------------------------------------
`shadow_runner.exec_costs()` returns `data_quality="COSTS_MODELLED"` whenever the broker
reports $0.00 commission -- which is every execution this broker produces -- and hands it
straight to `shadow_ledger.append_outcome(data_quality=...)`. That enum did not contain
`COSTS_MODELLED`, so append_outcome raised and the row spilled.

Both sides were tested. The runner's selftest (10/10) asserts exec_costs returns exactly
that tuple. The ledger's selftest (11/11) asserts the enum rejects unknown values. Both
passed. NOBODY TESTED THE JOIN, and the join is where the forward-evidence chain lives.

The chain has zero rows, so it never fired. It would have fired on the first outcome after
SHADOW_START = 2026-09-01 18:00 ET, and the failure mode is the worst kind: rows land in
spillover.jsonl, which is BY DESIGN "recorded, never lost" -- so the ledger would have
accumulated decisions with no outcomes, forever, while every component reported healthy.

    python research_sdk/test_forward_seam.py
"""
import ast
import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import shadow_ledger as SL      # noqa: E402
import shadow_runner as SR      # noqa: E402


def _string_literals(fn_source):
    """Every string literal a function can return, via AST -- not grep."""
    tree = ast.parse(fn_source)
    out = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            out.add(node.value)
    return out


def test_every_emitted_quality_is_accepted():
    """AST-extract exec_costs' literals; each must be in the ledger's QUALITY enum."""
    src = io.open(os.path.join(HERE, "shadow_runner.py"), encoding="utf-8").read()
    tree = ast.parse(src)
    fn = next(n for n in ast.walk(tree)
              if isinstance(n, ast.FunctionDef) and n.name == "exec_costs")
    emitted = {c.value for c in ast.walk(fn)
               if isinstance(c, ast.Constant) and isinstance(c.value, str)}
    # keep only the ones that look like quality tokens (UPPER_SNAKE), not dict keys
    emitted = {e for e in emitted if e.isupper() and e.replace("_", "").isalpha()}
    assert emitted, "found no quality literals in exec_costs -- test is not looking at the right function"
    unaccepted = emitted - set(SL.QUALITY)
    assert not unaccepted, (
        "shadow_runner.exec_costs can emit %s, which shadow_ledger.QUALITY rejects.\n"
        "  Every such row raises LedgerError and spills SILENTLY into spillover.jsonl.\n"
        "  QUALITY = %s" % (sorted(unaccepted), list(SL.QUALITY)))


def test_the_actual_zero_commission_path_round_trips():
    """The real call the broker's $0.00 executions take, end to end into a live chain."""
    import tempfile
    costs, dq = SR.exec_costs({"Commission": 0.0, "Fee": 0.0, "Quantity": 2})
    assert dq == "COSTS_MODELLED", dq
    assert abs(costs - 4.36) < 1e-9, costs

    d = tempfile.mkdtemp()
    dec = os.path.join(d, "_seam_decisions.csv")
    out = os.path.join(d, "_seam_outcomes.csv")
    start = "2026-09-01T18:00:00-04:00"

    row = SL.append_decision(
        dec, shadow_start=start, ts_decision="2026-09-01T19:00:00-04:00",
        strategy_id="SIM:TEST:L", source_hash="h", config_hash="c",
        data_cutoff="2026-09-01T19:00:00-04:00", input_dataset_version="v",
        input_source_hashes="s", action="LONG", intended_qty=2,
        expected_costs="nt8_template", quality_status="OK", blocked_reason="")

    # THE JOIN. Before the fix this raised LedgerError and the outcome was lost.
    SL.append_outcome(out, decision_path=dec, decision_seq=row["seq"],
                      ts_outcome="2026-09-01T19:05:00-04:00",
                      entry_fill=100.0, exit_fill=101.0, gross_pnl="", costs=costs,
                      net_pnl="", data_quality=dq, note="seam test")

    SL.verify(dec, "decision")
    SL.verify(out, "outcome")
    for p in (dec, out):
        os.remove(p)


def test_modelled_costs_stay_distinguishable_from_measured():
    """The whole point of the token: a modelled cost must never read as a measured one."""
    observed, dq_ok = SR.exec_costs({"Commission": 2.18, "Fee": 0.0, "Quantity": 1})
    assert dq_ok == "OK" and observed == 2.18, (observed, dq_ok)
    _, dq_mod = SR.exec_costs({"Commission": 0.0, "Fee": 0.0, "Quantity": 1})
    assert dq_mod != dq_ok, "modelled and measured costs must not share a quality token"


def test_ledger_still_rejects_genuinely_unknown_quality():
    """Widening the enum must not have disabled it."""
    import tempfile
    d = tempfile.mkdtemp()
    p = os.path.join(d, "_seam_reject.csv")
    try:
        SL.append_decision(p, shadow_start="2026-09-01T18:00:00-04:00",
                           ts_decision="2026-09-01T19:00:00-04:00",
                           strategy_id="x", source_hash="h", config_hash="c",
                           data_cutoff="d", input_dataset_version="v",
                           input_source_hashes="s", action="LONG", intended_qty=1,
                           expected_costs="e", quality_status="NOT_A_REAL_STATUS",
                           blocked_reason="")
    except SL.LedgerError:
        return
    finally:
        if os.path.exists(p):
            os.remove(p)
    raise AssertionError("the QUALITY enum no longer rejects unknown values")


if __name__ == "__main__":
    fails = 0
    for name, fn in sorted(globals().items()):
        if not name.startswith("test_"):
            continue
        try:
            fn()
            print("  PASS  %s" % name)
        except Exception as ex:
            fails += 1
            print("  FAIL  %s\n        %s" % (name, str(ex).splitlines()[0][:120]))
    print("\n%d failed" % fails)
    sys.exit(1 if fails else 0)
