"""audit_defect_classes.py -- BOUNDED repo-wide scan for the three silent-failure CLASSES that
were survived on 2026-08-28. Not a general code review.

    0A  integer overflow in time arithmetic      (bbo_v1.py:119)
    0C  numpy.datetime64 vs pandas.Timestamp keys (carry00 run 1)
    0D  import-time destructive file handles      (bbo_v1.py, void_audit.py)

The 0A scan is not purely textual: for every `np.arange(...) * <scale>` it finds, it EXECUTES the
expression's shape on this interpreter and reports whether the product actually overflows here.
A grep tells you where to look; running it tells you whether it is broken.

Run: python research_sdk/audit_defect_classes.py
"""
from __future__ import annotations

import ast
import io
import os
import re
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
SKIP = {".git", "__pycache__", "archive", ".ipynb_checkpoints"}
TIME_SCALES = {1_000, 1_000_000, 1_000_000_000, 10 ** 9, 10 ** 6, 10 ** 3}
SCALE_NAMES = {"NS", "NS_PER_S", "NANOS", "NANO", "US", "MS", "SEC_NS", "NSEC"}


def py_files():
    for p in ROOT.rglob("*.py"):
        if any(s in p.parts for s in SKIP):
            continue
        yield p


def literal_scale(node, consts):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return int(node.value)
    if isinstance(node, ast.Name) and node.id in consts:
        return consts[node.id]
    if isinstance(node, ast.Name) and node.id in SCALE_NAMES:
        return 1_000_000_000
    return None


def module_int_consts(tree):
    out = {}
    for n in tree.body:
        if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name):
            try:
                v = ast.literal_eval(n.value)
                if isinstance(v, int):
                    out[n.targets[0].id] = v
            except Exception:                                           # noqa: BLE001
                pass
    return out


def scan_0a(path, src, tree):
    """np.arange / np.array / np.zeros-family integer arrays multiplied by a time scale."""
    consts = module_int_consts(tree)
    hits = []
    for node in ast.walk(tree):
        if not (isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mult)):
            continue
        for a, b in ((node.left, node.right), (node.right, node.left)):
            if not (isinstance(a, ast.Call) and isinstance(a.func, ast.Attribute)):
                continue
            if a.func.attr not in ("arange", "array", "linspace"):
                continue
            scale = literal_scale(b, consts)
            if scale is None or abs(scale) < 1_000:
                continue
            has_dtype = any(k.arg == "dtype" for k in a.keywords)
            seg = ast.get_source_segment(src, node) or ""
            # EXECUTE it: does this expression actually overflow on this interpreter?
            overflows, detail = False, ""
            try:
                arr = eval(compile(ast.Expression(a), "<a>", "eval"),                # noqa: S307
                           {"np": np, "numpy": np}, dict(consts))
                if np.issubdtype(np.asarray(arr).dtype, np.integer):
                    a64 = np.asarray(arr).astype(np.int64)
                    prod = np.asarray(arr) * type(np.asarray(arr).flat[0])(scale) \
                        if np.asarray(arr).size else np.asarray(arr)
                    ref = a64 * np.int64(scale)
                    overflows = not np.array_equal(np.asarray(prod).astype(np.int64), ref)
                    detail = (f"dtype={np.asarray(arr).dtype} "
                              f"{'OVERFLOWS HERE' if overflows else 'ok here'}")
            except Exception as e:                                      # noqa: BLE001
                detail = f"not statically evaluable ({type(e).__name__})"
            hits.append(dict(file=str(path.relative_to(ROOT)).replace("\\", "/"),
                             line=node.lineno, expr=seg[:88], scale=scale,
                             explicit_dtype=has_dtype, overflows=overflows, detail=detail))
            break
    return hits


NP_UNIQUE_RE = re.compile(r"\[[\"'](\w+)[\"']\]\s*\.unique\(\)")
GROUPBY_RE = re.compile(r"\.groupby\(\s*[\"'](\w+)[\"']")


DATEISH = re.compile(r"^(date|.*_date|dt|time|.*_time|ts|.*_ts|week|.*_week|day|.*_day|"
                     r"session_date|sess_date|effective_from|decision_ts)$", re.I)


def scan_0c(path, src):
    """Files where a column is both .unique()'d and .groupby()'d.

    The datetime64-vs-Timestamp hazard bites ONLY on DATETIME columns: `.unique()` on an int64 or
    object column returns numpy.int64 / str, both of which hash equal to their Python counterparts,
    so a groupby key matches. Only np.datetime64 vs pd.Timestamp fails to hash equal. Columns are
    therefore split into DATE-LIKE (real risk) and other (reported, not counted).
    """
    u = set(NP_UNIQUE_RE.findall(src))
    g = set(GROUPBY_RE.findall(src))
    both = sorted(u & g)
    if not both:
        return []
    dateish = [c for c in both if DATEISH.match(c)]
    guarded = ("keysafe" in src or "assert_resolves" in src
               or "date-key type mismatch" in src or "pd.Timestamp(x) for x in" in src)
    return [dict(file=str(path.relative_to(ROOT)).replace("\\", "/"),
                 columns=",".join(both), dateish=",".join(dateish),
                 at_risk=bool(dateish) and not guarded, guarded=guarded)]


def importable_names(files):
    """module basename -> path, for cross-referencing who imports whom."""
    return {p.stem: p for p in files}


def imported_modules(src):
    out = set()
    try:
        tree = ast.parse(src)
    except Exception:                                                   # noqa: BLE001
        return out
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            for a in n.names:
                out.add(a.name.split(".")[0])
        elif isinstance(n, ast.ImportFrom) and n.module:
            out.add(n.module.split(".")[0])
    return out


def _import_time_nodes(body):
    """Yield only nodes that actually EXECUTE on import.

    Function and class bodies do not run on import, and neither does `if __name__ == "__main__"`.
    Flagging those would drown the real signal in hundreds of harmless in-function writes -- which
    is exactly what the first version of this scanner did (638 false positives).
    """
    for node in body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        if isinstance(node, ast.If):
            t = node.test
            if (isinstance(t, ast.Compare) and isinstance(t.left, ast.Name)
                    and t.left.id == "__name__"):
                continue
            yield from _import_time_nodes(node.body)
            yield from _import_time_nodes(node.orelse)
            continue
        yield node


def scan_0d(path, src, tree):
    """IMPORT-TIME open(..., 'w'/'a') -- truncates evidence merely on import."""
    hits = []
    for node in _import_time_nodes(tree.body):
        for sub in ast.walk(node):
            if (isinstance(sub, ast.Call) and isinstance(sub.func, ast.Name)
                    and sub.func.id == "open"):
                mode = ""
                if len(sub.args) > 1 and isinstance(sub.args[1], ast.Constant):
                    mode = str(sub.args[1].value)
                for k in sub.keywords:
                    if k.arg == "mode" and isinstance(k.value, ast.Constant):
                        mode = str(k.value.value)
                if any(m in mode for m in ("w", "a", "+")):
                    hits.append(dict(file=str(path.relative_to(ROOT)).replace("\\", "/"),
                                     line=sub.lineno, mode=mode))
    return hits


def main():
    a, c, d = [], [], []
    n = 0
    files = list(py_files())
    srcs = {}
    for p in files:
        try:
            srcs[p] = p.read_text(encoding="utf-8", errors="replace")
        except Exception:                                               # noqa: BLE001
            pass
    # who imports whom -- a flat script whose module-level write is its PURPOSE is not a hazard;
    # the hazard is a module that is IMPORTED by something else and truncates on import.
    all_imported = set()
    for src in srcs.values():
        all_imported |= imported_modules(src)
    for p in files:
        src = srcs.get(p)
        if src is None:
            continue
        try:
            tree = ast.parse(src)
        except Exception:                                               # noqa: BLE001
            continue
        n += 1
        a += scan_0a(p, src, tree)
        c += scan_0c(p, src)
        for h in scan_0d(p, src, tree):
            h["is_imported"] = p.stem in all_imported
            d.append(h)

    print("=" * 108)
    print(f"=== DEFECT-CLASS AUDIT over {n} python files   (numpy {np.__version__}, "
          f"default int dtype {np.array([1]).dtype})")
    print("=" * 108)

    print("\n=== 0A  INTEGER OVERFLOW IN TIME ARITHMETIC")
    print("    numpy array constructor multiplied by a >=1e3 time scale")
    if not a:
        print("    (no sites)")
    bad = [h for h in a if h["overflows"]]
    for h in sorted(a, key=lambda x: (not x["overflows"], x["file"])):
        flag = "*** OVERFLOWS ***" if h["overflows"] else ("ok" if h["explicit_dtype"] else "check")
        print(f"    {flag:<18} {h['file']}:{h['line']}")
        print(f"        {h['expr']}")
        print(f"        scale={h['scale']:,}  explicit dtype={h['explicit_dtype']}  {h['detail']}")
    print(f"\n    >>> SITES {len(a)}   ACTUALLY OVERFLOWING ON THIS INTERPRETER: {len(bad)}")

    print("\n=== 0C  datetime64 vs Timestamp KEY MISMATCH RISK")
    print("    files that both .unique() and .groupby() the same column")
    if not c:
        print("    (no sites)")
    risk = [h for h in c if h["at_risk"]]
    for h in sorted(c, key=lambda x: (not x["at_risk"], x["file"])):
        tag = ("*** AT RISK ***" if h["at_risk"]
               else ("guarded" if h["guarded"] else "not date-like"))
        extra = f"   DATE-LIKE: {h['dateish']}" if h["dateish"] else ""
        print(f"    {tag:<18} {h['file']}")
        print(f"        columns: {h['columns']}{extra}")
    print(f"\n    >>> SITES {len(c)}   AT RISK (date-like column AND unguarded): {len(risk)}")
    print("    Non-date-like columns are NOT this class: numpy.int64 and str hash equal to their")
    print("    Python counterparts, so a groupby key matches. Only np.datetime64 vs pd.Timestamp")
    print("    fails to hash equal, which is what silently emptied CARRY00's first run.")

    print("\n=== 0D  IMPORT-TIME DESTRUCTIVE FILE HANDLES")
    print("    module-level open(..., 'w'/'a') -- truncates evidence on mere import")
    haz = [h for h in d if h["is_imported"]]
    if not haz:
        print("    (no module that another module imports truncates on import)")
    for h in haz:
        print(f"    *** IMPORTED ELSEWHERE  {h['file']}:{h['line']}  mode={h['mode']!r}")
    print(f"\n    >>> module-level write sites {len(d)}   "
          f"OF WHICH IMPORTED ELSEWHERE: {len(haz)}")
    print("    A flat script whose module-level write IS its purpose is not a hazard. The hazard")
    print("    is a module another module imports, which truncates evidence on import -- which is")
    print("    exactly how void_audit.txt was zeroed after a successful run.")

    print("\n" + "=" * 108)
    print(f"=== BLAST RADIUS: 0A actually-overflowing {len(bad)} · "
          f"0C at-risk {len(risk)} · 0D imported-and-destructive {len(haz)}")
    print("=" * 108)
    return bad, c, d


if __name__ == "__main__":
    main()
