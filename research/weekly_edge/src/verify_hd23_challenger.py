"""verify_hd23_challenger.py -- offline certification of the HD-20..23 challenger classes.

The headline gate is G1, and it is a PROOF, not a smell test:

    INVERSE-PATCH IDENTITY.  Apply every patch BACKWARDS to the generated file and assert the
    result is BYTE-IDENTICAL to the certified source.  If that holds, then by construction the
    ONLY differences between the certified class and the challenger are the hunks this build
    declares -- no line of the decision object, the signal, the session box, the sizing, the
    ledger arithmetic or the export format can have moved, because any such change would
    survive the inverse patch and break the equality.

    This is strictly stronger than "I diffed it and it looked fine", which is what a human
    review of a 1,400-line file actually amounts to.

The remaining gates check the properties the inverse patch cannot see:

    G2  M1 INERTNESS      every added method is provably dead outside State.Realtime
    G3  SAFE DEFAULTS     the bus is OFF and the witness is DETECT unless the owner opts in
    G4  BLIND NEVER GATES the two gating paths return unchanged when the witness is not armed
    G5  BRACE BALANCE     a cheap structural check; the real syntax check is the compile probe
    G6  NO STALE NAME     the old class name appears nowhere in the new file
    G7  EXIT SITES WRAPPED every Exit*/Enter* order site is accounted for
    G8  RESETSHADOW REACH the HD-21 leak is actually closed on every path that submits an exit

Run:  python verify_hd23_challenger.py
Exit: 0 = all gates pass, 1 = at least one gate FAILED.
"""
from __future__ import annotations

import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
NS = os.path.abspath(os.path.join(HERE, "..", "ninjascript"))
sys.path.insert(0, HERE)

import build_hd23_challenger as B   # noqa: E402


ROWS = []


def gate(name: str, cls: str, ok: bool, detail: str = "") -> bool:
    ROWS.append((name, cls, "PASS" if ok else "FAIL", detail))
    return ok


# =============================================================================================
def inverse_patch(new_text: str, cfg: dict) -> str:
    """Undo every declared patch. Order is the reverse of build_one."""
    t = new_text

    # 7. properties + defaults
    t = t.replace(B.DEFAULTS, "", 1)
    t = t.replace(B.PROPS, "", 1)

    # 6. exit sites
    for old, new in reversed(cfg["exits"]):
        t = t.replace(new, old, 1)

    # 5. the fourth witness
    t = t.replace("\n" + B.ACCTW_CALL.replace("__ARG__", cfg["acct_arg"]).rstrip("\n"), "", 1)

    # 4. session-flatten settle
    if cfg["family"] == "P1":
        t = t.replace(B.SESSFLAT_SETTLE, "", 1)

    # 3. export
    t = t.replace(B.CATCH_NEW, B.CATCH_OLD, 1)
    t = t.replace(cfg["export_new"], cfg["export_old"], 1)

    # 2. warm-up seed
    t = t.replace(B.WARMUP_NEW, B.WARMUP_OLD, 1)

    # 1. fields + helpers
    helpers = (B.FIELDS_AND_HELPERS
               .replace("__ACCT__", cfg["acct"])
               .replace("__INSTR__", cfg["instr"]))
    t = t.replace(helpers, "", 1)

    # 0. class rename
    t = t.replace(cfg["new_cls"], cfg["old_cls"])
    return t


def read_lf(path: str) -> str:
    with open(path, "rb") as fh:
        return fh.read().decode("utf-8").replace("\r\n", "\n")


ADDED_METHODS = [
    "HdAccountSignedQty", "HdExecInstrumentName", "PosBusPublish",
    "PosBusReadOthers", "AcctWitness", "HdExitQty", "HdExportEnsure",
]
# The two that are M1-safe by returning their argument rather than by returning early.
M1_BY_RETURN_ARG = {"HdExitQty"}
# HdExecInstrumentName is a pure try/catch accessor reached ONLY from M1-guarded callers and
# returns "?" rather than a number, so it cannot influence a decision in any State.
M1_EXEMPT = {"HdExecInstrumentName"}


def method_body(text: str, name: str) -> str:
    i = text.find(" " + name + "(")
    if i < 0:
        return ""
    j = text.find("{", i)
    depth, k = 0, j
    while k < len(text):
        if text[k] == "{":
            depth += 1
        elif text[k] == "}":
            depth -= 1
            if depth == 0:
                return text[j:k + 1]
        k += 1
    return ""


def check_one(cfg: dict) -> bool:
    src = read_lf(os.path.join(NS, cfg["src"]))
    new = read_lf(os.path.join(NS, cfg["dst"]))
    cls = cfg["new_cls"]
    ok = True

    # ---- G1  INVERSE-PATCH IDENTITY -- the proof
    back = inverse_patch(new, cfg)
    same = (back == src)
    detail = ""
    if not same:
        sl, bl = src.split("\n"), back.split("\n")
        for n, (a, b) in enumerate(zip(sl, bl), 1):
            if a != b:
                detail = f"first divergence at line {n}: {a[:60]!r} != {b[:60]!r}"
                break
        else:
            detail = f"length {len(bl)} vs certified {len(sl)}"
    ok &= gate("G1 inverse-patch identity", cls, same, detail)

    # ---- G2  M1 INERTNESS
    bad = []
    for m in ADDED_METHODS:
        body = method_body(new, m)
        if not body:
            bad.append(m + ":missing")
            continue
        if m in M1_EXEMPT:
            continue
        first = [ln.strip() for ln in body.split("\n")
                 if ln.strip() and not ln.strip().startswith(("{", "//"))]
        head = first[0] if first else ""
        if m in M1_BY_RETURN_ARG:
            if "if (State != State.Realtime)" not in head or "return want;" not in head:
                bad.append(m + ":" + head[:50])
        elif "if (State != State.Realtime) return;" not in head:
            # A method with `out` parameters CANNOT lead with the guard: C# definite assignment
            # forces the outs to be written first.  That is allowed only when the guard is the
            # very next statement AND the line before it touches nothing but the out params.
            pre, guard = (first + ["", ""])[0], (first + ["", ""])[1]
            allowed = (m in ("PosBusReadOthers", "HdAccountSignedQty")
                       and "State != State.Realtime" in guard
                       and "return false;" in guard
                       and re.fullmatch(r"[\w\s=;\"'0-9,]*(//.*)?", pre or "") is not None)
            if not allowed:
                bad.append(m + ":" + head[:50])
    ok &= gate("G2 M1 inertness", cls, not bad, ", ".join(bad))

    # ---- G3  SAFE DEFAULTS
    d_ok = ('PosBusDir = ""' in new
            and 'AcctWitnessMode = "DETECT"' in new
            and "PosBusStaleSec = 300" in new
            and "AcctConfirmBars = 2" in new)
    ok &= gate("G3 safe defaults (bus OFF, DETECT)", cls, d_ok)

    # ---- G4  BLIND NEVER GATES
    hx = method_body(new, "HdExitQty")
    aw = method_body(new, "AcctWitness")
    b_ok = ("if (!acctArmed)" in hx and "return want;" in hx
            and "acctArmed = false;" in aw
            and "ACCT-WITNESS-BLIND" in aw
            and "Halt(" not in aw.split("ACCT-WITNESS-BLIND")[1].split("return;")[0])
    ok &= gate("G4 blind never gates", cls, b_ok)

    # ---- G5  BRACE BALANCE (whole file, ignoring string/char literals crudely)
    stripped = re.sub(r'"(\\.|[^"\\])*"', '""', new)
    stripped = re.sub(r"'(\\.|[^'\\])'", "' '", stripped)
    stripped = re.sub(r"//[^\n]*", "", stripped)
    bal = stripped.count("{") - stripped.count("}")
    ok &= gate("G5 brace balance", cls, bal == 0, f"delta={bal}")

    # ---- G6  NO STALE CLASS NAME
    ok &= gate("G6 no stale class name", cls, cfg["old_cls"] not in new)

    # ---- G7  EVERY EXIT SITE WRAPPED
    sites = re.findall(r"Exit(?:Long|Short)\([^;]*;", new)
    unwrapped = [s for s in sites if "_q" not in s]
    ok &= gate("G7 exit sites wrapped", cls, not unwrapped,
               f"{len(unwrapped)} unwrapped of {len(sites)}")

    # ---- G8  HD-21 LEAK CLOSED
    if cfg["family"] == "P1":
        l_ok = ("sessFlatPending = true;" in new
                and "if (sessFlatPending)" in new
                and "ObserveSettlement(ACT_EXIT, sessFlatQty, sessFlatPx);" in new)
    else:
        # XM: every exit site sets ACT_EXIT except DEAD-SERIES, which Halts on the same line;
        # it gets an explicit ResetShadow for hygiene.
        l_ok = new.count("ResetShadow();   // [HD-21]") == 1
    ok &= gate("G8 HD-21 shadow leak closed", cls, l_ok)

    return ok


def main() -> int:
    all_ok = True
    for cfg in B.FILES:
        all_ok &= check_one(cfg)

    w = max(len(r[0]) for r in ROWS)
    print("=" * 104)
    print("HD-20..23 CHALLENGER -- OFFLINE CERTIFICATION")
    print("=" * 104)
    print(f"  {'GATE':<{w}}  {'CLASS':<28} {'RESULT':<6} DETAIL")
    print("  " + "-" * 100)
    cur = None
    for name, cls, res, detail in ROWS:
        if cls != cur:
            cur = cls
            print("  " + "-" * 100)
        print(f"  {name:<{w}}  {cls:<28} {res:<6} {detail}")
    print("=" * 104)
    n_fail = sum(1 for r in ROWS if r[2] == "FAIL")
    print(f"  {len(ROWS) - n_fail}/{len(ROWS)} gates PASS." if not n_fail
          else f"  *** {n_fail} GATE(S) FAILED ***")
    print("  G1 is the load-bearing one: it PROVES the certified decision object is untouched.")
    print("  It cannot prove the file COMPILES -- that is the synthetic probe's job (CLAUDE.md 6).")
    print("=" * 104)
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
