# -*- coding: utf-8 -*-
"""Apply the repo-live-truth audit edits, asserting every match.

Same discipline as the MX01 port transforms: an edit that does not match EXACTLY ONCE is
NOT applied silently -- it is reported and skipped for manual handling. A documentation
sweep that quietly mis-patches is worse than one that does nothing.

SKIPPED BY POLICY: the .cs header findings. Touching a file in bin/Custom/Strategies
triggers a NinjaTrader.Custom.dll recompile against a RUNNING REAL-MONEY BOOK. The status
correction is recorded in CURRENT_LIVE_TRUTH.md / EXECUTION_MANIFEST.md instead, and the
comment edit is deferred to a window when both legs are stopped and flat.
"""
import io
import json
import os
import sys

REPO = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
SYN = "audit_synth.json"

syn = json.load(io.open(SYN, encoding="utf-8"))
findings = syn["findings"]

SKIP_SUFFIX = (".cs",)          # never edit compiled sources while the book is live

applied, skipped, failed = [], [], []
# group by file so multiple edits to one file are applied against one in-memory copy
byfile = {}
for i, f in enumerate(findings):
    path = f["file"].split(":")[0].replace("/", os.sep)
    byfile.setdefault(path, []).append((i, f))

for path, items in sorted(byfile.items()):
    full = os.path.join(REPO, path)
    if path.endswith(SKIP_SUFFIX):
        for i, f in items:
            skipped.append((i, path, "POLICY: live compiled source, never edit while enabled"))
        continue
    if not os.path.exists(full):
        for i, f in items:
            failed.append((i, path, "FILE NOT FOUND"))
        continue

    with io.open(full, encoding="utf-8-sig", newline="") as fh:
        src = fh.read()
    eol = "\r\n" if "\r\n" in src else "\n"
    text = src.replace("\r\n", "\n")
    orig = text

    for i, f in items:
        old = f["quote"].replace("\r\n", "\n")
        new = f["suggested_fix"].replace("\r\n", "\n")
        n = text.count(old)
        if n == 1:
            text = text.replace(old, new, 1)
            applied.append((i, path, len(new) - len(old)))
        elif n == 0:
            failed.append((i, path, "NO MATCH (0x) -- quote head: %r" % old[:90]))
        else:
            failed.append((i, path, "AMBIGUOUS (%dx) -- quote head: %r" % (n, old[:90])))

    if text != orig:
        with io.open(full, "w", encoding="utf-8", newline="") as fh:
            fh.write(text.replace("\n", eol))

print("=" * 78)
print("APPLIED  %d" % len(applied))
for i, p, d in applied:
    print("   #%-2d %-62s %+6d" % (i, p, d))
print()
print("SKIPPED BY POLICY  %d" % len(skipped))
for i, p, why in skipped:
    print("   #%-2d %-62s %s" % (i, p, why))
print()
print("NEEDS MANUAL HANDLING  %d" % len(failed))
for i, p, why in failed:
    print("   #%-2d %-62s %s" % (i, p, why))
print("=" * 78)
print("files touched: %d" % len({p for _, p, _ in applied}))
