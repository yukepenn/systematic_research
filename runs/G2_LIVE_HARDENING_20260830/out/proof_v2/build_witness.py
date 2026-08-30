"""RE-PROVER witness: is the COMPILED assembly the post-fix build?

The connection-loss revert removed two property assignments whose semantics are
realtime-only, so no backtest can distinguish the two builds behaviourally. The
witness therefore has to be taken at the assembly level.

A C# `X = value;` on a property compiles to `call instance void ...::set_X(...)`,
which puts the member name `set_X` in the assembly's #Strings metadata heap.
Removing the only assignment site removes the MemberRef and its name.

Control: the sibling properties the hardened files STILL declare must be PRESENT,
otherwise the search is not sensitive and an ABSENT result means nothing.

Prints a GATE / SPEC / OBSERVED / VERDICT table. Never assembled by hand.
"""
import hashlib
import os
import re
import sys

CUSTOM = r"C:\Users\Yuke Zhang\Documents\NinjaTrader 8\bin\Custom"
DLL = os.path.join(CUSTOM, "NinjaTrader.Custom.dll")
STRAT = os.path.join(CUSTOM, "Strategies")

HARDENED = ["WeeklyEdgeP1PCT_v2.cs", "WeeklyEdgeXMConflict_v3.cs"]
CERTIFIED = {
    "WeeklyEdgeP1PCT_v1.cs":
        "ee4c765bc5cab23096f4009943ef6a79e03c3d2d7c671a2285f6cec2676e87b2",
    "WeeklyEdgeXMConflict_v2.cs":
        "2ec00dd4d0a11b999b649dcf358b63f92bc09f4edf1d2cec77c076b64c910dde",
}
HARD_EXPECT = {
    "WeeklyEdgeP1PCT_v2.cs":
        "a815da3b8d7a22cae9359af8ece069db3bc5362ee202cf8dfe5b16da2caeafb9",
    "WeeklyEdgeXMConflict_v3.cs":
        "3b8da2e60b2b799321eadace0e2e35f2741a67f6745162ff7ea13b31274419f0",
}

REMOVED = ["ConnectionLossHandling", "NumberRestartAttempts"]
KEPT = ["RealtimeErrorHandling", "DisconnectDelaySeconds", "StartBehavior"]


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def code_sites(path, names):
    """assignment/reference sites in real code (comments stripped), and comment-only mentions"""
    lines = open(path, encoding="utf-8", errors="replace").read().split("\n")
    pat = re.compile(r"\b(" + "|".join(names) + r")\b")
    code, comment = [], []
    for i, l in enumerate(lines, 1):
        s = l.strip()
        if s.startswith("//"):
            if pat.search(s):
                comment.append(i)
            continue
        if pat.search(s.split("//")[0]):
            code.append((i, s))
    return code, comment


def main():
    out = []
    P = out.append
    P("=" * 112)
    P("RE-PROVER BUILD WITNESS - is the compiled assembly the post-fix (reverted) build?")
    P("=" * 112)

    blob = open(DLL, "rb").read()
    P("")
    P("assembly : %s" % DLL)
    P("bytes    : %d   mtime(utc): %s" % (len(blob), __import__("datetime").datetime.
      utcfromtimestamp(os.path.getmtime(DLL)).isoformat() + "Z"))
    P("")

    gates = []

    # --- source-level: zero declarations remain ---
    for f in HARDENED:
        code, comment = code_sites(os.path.join(STRAT, f), REMOVED)
        gates.append(("S1 %s" % f[:26],
                      "0 non-comment sites for %s" % "/".join(REMOVED),
                      "%d code site(s); %d comment mention(s) at %s"
                      % (len(code), len(comment), comment),
                      len(code) == 0))

    # --- source-level: hardened digests match what the fixer recorded ---
    for f, want in HARD_EXPECT.items():
        got = sha(os.path.join(STRAT, f))
        gates.append(("S2 %s" % f[:26], "sha256 == fixer's post-revert digest",
                      "%s..%s" % (got[:8], got[-4:]), got == want))

    # --- certified sources untouched ---
    for f, want in CERTIFIED.items():
        got = sha(os.path.join(STRAT, f))
        gates.append(("S3 %s" % f[:26], "certified sha256 UNCHANGED",
                      "%s..%s" % (got[:8], got[-4:]), got == want))

    # --- assembly-level: sensitivity control MUST be present ---
    for n in KEPT:
        present = ("set_" + n).encode("ascii") in blob
        gates.append(("A1 control set_%s" % n[:22],
                      "PRESENT (still declared -> search is sensitive)",
                      "PRESENT" if present else "ABSENT", present))

    # --- assembly-level: the removed setters must be gone ---
    for n in REMOVED:
        present = ("set_" + n).encode("ascii") in blob
        gates.append(("A2 removed set_%s" % n[:22],
                      "ABSENT (no assignment site anywhere in the assembly)",
                      "PRESENT" if present else "ABSENT", not present))

    # --- assembly-level: both hardened types are actually in the assembly ---
    for t in ["WeeklyEdgeP1PCT_v2", "WeeklyEdgeXMConflict_v3",
              "WeeklyEdgeP1PCT_v1", "WeeklyEdgeXMConflict_v2"]:
        present = t.encode("ascii") in blob
        gates.append(("A3 type %s" % t[:22], "PRESENT in NinjaTrader.Custom.dll",
                      "PRESENT" if present else "ABSENT", present))

    P("%-32s %-52s %-22s %s" % ("GATE", "SPEC", "OBSERVED", "VERDICT"))
    P("-" * 112)
    for g, s, o, ok in gates:
        P("%-32s %-52s %-22s %s" % (g, s, o, "PASS" if ok else "FAIL"))
    P("-" * 112)
    ok = all(g[3] for g in gates)
    P("BUILD WITNESS: %s" % ("PASS - the on-disk compiled assembly is the POST-FIX build"
                            if ok else "FAIL"))
    txt = "\n".join(out)
    print(txt)
    here = os.path.dirname(os.path.abspath(__file__))
    open(os.path.join(here, "BUILD_WITNESS.txt"), "w", encoding="utf-8").write(txt + "\n")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
