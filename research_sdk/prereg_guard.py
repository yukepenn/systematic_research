"""
Preregistration guard.

Enforces the campaign's post-structural-invariance governance rule (master directive
sec6-7, sec170): for every new inference-bearing run, the spec/manifest/candidate
definition must be committed to git BEFORE the outcome-producing code runs, in a
commit that is a strict ancestor of the commit that later lands the results. No
same-commit spec+result landings for alpha-bearing work.

Two modes:

  PROSPECTIVE (default) -- call this BEFORE running an alpha experiment. Checks the
  live working tree: spec is committed and unmodified, HEAD descends from the spec
  commit, and the result files do not exist yet. Refuses the run if any check fails.

  AUDIT -- call this AFTER the fact, pointing at a historical spec_commit and the
  commit that (should have) landed results. Answers a purely git-forensic question:
  were the result files absent from the repo tree at spec_commit? This is the same
  question HASH01/REGISTRY_GAP_NOTE.md answered by hand for ~74 run directories;
  audit mode makes that check mechanical and reusable so the registry can be
  rescanned without repeating manual archaeology (sec96, sec171).

Run classes (sec8): ENGINEERING_ONLY and ZERO_ALPHA_BUDGET runs may bypass the gate
entirely -- infrastructure work carries no selection risk. Every other class must
pass.

CLI:
    python research_sdk/prereg_guard.py check \
        --run-class BOUNDED_SELECTION \
        --spec-commit <sha> --spec path/to/spec.md [path/to/manifest.csv ...] \
        --result out/results.json [out/results.csv ...]

    python research_sdk/prereg_guard.py audit \
        --spec-commit <sha> --spec path/to/spec.md \
        --result out/results.json [--result-commit <sha>]

Exit code 0 = gate passes (run may proceed / historical record is clean).
Exit code 1 = gate fails (refuse the run / same-commit violation found).
"""

from __future__ import annotations

import argparse
import hashlib
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

RUN_CLASSES = (
    "ENGINEERING_ONLY",
    "AUDIT",
    "DIAGNOSTIC",
    "EXPLORATORY_DISCOVERY",
    "BOUNDED_SELECTION",
    "PROTECTED_CONFIRMATION",
    "LOCKED_FORWARD_MONITOR",
    "PROMOTION_CERTIFICATION",
)

BYPASS_CLASSES = ("ENGINEERING_ONLY", "ZERO_ALPHA_BUDGET")


class GitError(RuntimeError):
    pass


def _git(repo_root: Path, *args: str) -> str:
    proc = subprocess.run(
        ["git", *args],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        raise GitError(f"git {' '.join(args)} failed: {proc.stderr.strip()}")
    return proc.stdout


def _git_ok(repo_root: Path, *args: str) -> bool:
    proc = subprocess.run(["git", *args], cwd=str(repo_root), capture_output=True, text=True)
    return proc.returncode == 0


@dataclass
class GuardCheck:
    name: str
    passed: bool
    detail: str


@dataclass
class GuardResult:
    mode: str
    run_class: str | None
    bypassed: bool
    checks: list[GuardCheck] = field(default_factory=list)

    @property
    def overall_pass(self) -> bool:
        if self.bypassed:
            return True
        return all(c.passed for c in self.checks)

    def report(self) -> str:
        lines = [f"[prereg_guard:{self.mode}] run_class={self.run_class}"]
        if self.bypassed:
            lines.append(f"  BYPASSED (run_class in {BYPASS_CLASSES}) -- gate not evaluated")
        for c in self.checks:
            mark = "PASS" if c.passed else "FAIL"
            lines.append(f"  [{mark}] {c.name}: {c.detail}")
        lines.append(f"OVERALL: {'PASS -- may proceed' if self.overall_pass else 'FAIL -- refuse'}")
        return "\n".join(lines)


def _commit_exists(repo_root: Path, commit: str) -> bool:
    return _git_ok(repo_root, "cat-file", "-e", f"{commit}^{{commit}}")


def _path_in_tree_at(repo_root: Path, commit: str, path: str) -> bool:
    return _git_ok(repo_root, "cat-file", "-e", f"{commit}:{path}")


def _is_ancestor(repo_root: Path, ancestor: str, descendant: str) -> bool:
    return _git_ok(repo_root, "merge-base", "--is-ancestor", ancestor, descendant)


def _working_tree_matches_head(repo_root: Path, path: str) -> bool:
    """True if the file has no uncommitted modifications relative to HEAD."""
    proc = subprocess.run(
        ["git", "diff", "--quiet", "HEAD", "--", path],
        cwd=str(repo_root),
        capture_output=True,
    )
    return proc.returncode == 0


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_prospective(
    repo_root: Path,
    run_class: str,
    spec_commit: str,
    spec_paths: list[str],
    result_paths: list[str],
    candidate_manifest: str | None = None,
    candidate_manifest_sha256: str | None = None,
) -> GuardResult:
    result = GuardResult(mode="prospective", run_class=run_class, bypassed=run_class in BYPASS_CLASSES)
    if result.bypassed:
        return result

    if run_class not in RUN_CLASSES:
        result.checks.append(GuardCheck("run_class_valid", False, f"'{run_class}' not in {RUN_CLASSES}"))
        return result
    result.checks.append(GuardCheck("run_class_valid", True, run_class))

    if not _commit_exists(repo_root, spec_commit):
        result.checks.append(GuardCheck("spec_commit_exists", False, f"{spec_commit} not found in repo"))
        return result
    result.checks.append(GuardCheck("spec_commit_exists", True, spec_commit))

    for p in spec_paths:
        committed = _path_in_tree_at(repo_root, spec_commit, p)
        result.checks.append(GuardCheck(f"spec_committed:{p}", committed,
                                         "present in spec_commit tree" if committed else "MISSING from spec_commit tree"))
        clean = _working_tree_matches_head(repo_root, p)
        result.checks.append(GuardCheck(f"spec_unmodified_on_disk:{p}", clean,
                                         "no uncommitted local changes" if clean else "working tree has uncommitted edits to spec"))

    head_descends = _is_ancestor(repo_root, spec_commit, "HEAD")
    result.checks.append(GuardCheck("head_descends_from_spec_commit", head_descends,
                                     "HEAD is a descendant of spec_commit" if head_descends
                                     else "HEAD does NOT descend from spec_commit -- wrong branch/detached history?"))

    for p in result_paths:
        exists = (repo_root / p).exists()
        result.checks.append(GuardCheck(f"result_not_yet_produced:{p}", not exists,
                                         "does not exist yet (good)" if not exists
                                         else "ALREADY EXISTS -- results predate/duplicate this prereg"))

    if candidate_manifest is not None:
        mpath = repo_root / candidate_manifest
        if not mpath.exists():
            result.checks.append(GuardCheck("candidate_manifest_frozen", False, f"{candidate_manifest} not found"))
        elif candidate_manifest_sha256 is not None:
            actual = _sha256(mpath)
            match = actual == candidate_manifest_sha256
            result.checks.append(GuardCheck("candidate_manifest_frozen", match,
                                             f"sha256 {'matches' if match else 'MISMATCH'} frozen hash ({actual[:12]}...)"))
        else:
            result.checks.append(GuardCheck("candidate_manifest_frozen", True,
                                             f"{candidate_manifest} exists (no hash pinned to compare)"))

    return result


def check_audit(
    repo_root: Path,
    spec_commit: str,
    spec_paths: list[str],
    result_paths: list[str],
    result_commit: str = "HEAD",
) -> GuardResult:
    result = GuardResult(mode="audit", run_class=None, bypassed=False)

    if not _commit_exists(repo_root, spec_commit):
        result.checks.append(GuardCheck("spec_commit_exists", False, f"{spec_commit} not found in repo"))
        return result
    result.checks.append(GuardCheck("spec_commit_exists", True, spec_commit))

    for p in spec_paths:
        committed = _path_in_tree_at(repo_root, spec_commit, p)
        result.checks.append(GuardCheck(f"spec_present_at_spec_commit:{p}", committed,
                                         "present" if committed else "MISSING at spec_commit"))

    ancestry_ok = _is_ancestor(repo_root, spec_commit, result_commit)
    result.checks.append(GuardCheck("spec_commit_precedes_result_commit", ancestry_ok,
                                     f"spec_commit is ancestor of {result_commit}" if ancestry_ok
                                     else f"spec_commit does NOT precede {result_commit}"))

    for p in result_paths:
        absent_at_spec = not _path_in_tree_at(repo_root, spec_commit, p)
        result.checks.append(GuardCheck(f"result_absent_at_spec_commit:{p}", absent_at_spec,
                                         "absent at spec_commit -- landed later (clean)" if absent_at_spec
                                         else "SAME-COMMIT VIOLATION -- result already present at spec_commit"))
        present_at_result = _path_in_tree_at(repo_root, result_commit, p)
        result.checks.append(GuardCheck(f"result_present_at_result_commit:{p}", present_at_result,
                                         "present" if present_at_result else f"MISSING at {result_commit}"))

    return result


def _selftest(repo_root: Path) -> int:
    """Demonstrates the guard against two real commits from this campaign's own
    history: a genuine prereg-before-result pass, and a known same-commit case
    (documented narratively in research/registry/REGISTRY_GAP_NOTE.md; this
    reproduces that finding mechanically for one example instead of by hand)."""
    print("=== SELF-TEST 1: SIMPLE01 completion pass (expected PASS) ===")
    r1 = check_audit(
        repo_root,
        spec_commit="6ffe82d",
        spec_paths=["research/system_master/SIMPLE01_MINIMUM_SYSTEM/out/03_SPEC_completion_pass_preregistration.md"],
        result_paths=["research/system_master/SIMPLE01_MINIMUM_SYSTEM/out/completion_pass_results.json"],
        result_commit="e5e03bf",
    )
    print(r1.report())
    print()
    print("=== SELF-TEST 2: AUCTION04 (expected FAIL -- known same-commit landing) ===")
    r2 = check_audit(
        repo_root,
        spec_commit="fcaae6c",
        spec_paths=["runs/AUCTION04_CLEAN_CAUSAL_SUBSTRATE/spec.yaml"],
        result_paths=["runs/AUCTION04_CLEAN_CAUSAL_SUBSTRATE/out/m5_clean_action_value.json"],
        result_commit="fcaae6c",
    )
    print(r2.report())
    print()

    ok = r1.overall_pass and not r2.overall_pass
    print(f"SELF-TEST {'PASSED' if ok else 'FAILED'} "
          f"(expected check1=PASS check2=FAIL; got check1={r1.overall_pass} check2={r2.overall_pass})")
    return 0 if ok else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--repo-root", default=".", help="repo root (default: cwd)")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_check = sub.add_parser("check", help="prospective gate -- run before starting an alpha experiment")
    p_check.add_argument("--run-class", required=True, choices=RUN_CLASSES + ("ZERO_ALPHA_BUDGET",))
    p_check.add_argument("--spec-commit", required=True)
    p_check.add_argument("--spec", nargs="+", required=True, dest="spec_paths")
    p_check.add_argument("--result", nargs="+", default=[], dest="result_paths")
    p_check.add_argument("--candidate-manifest")
    p_check.add_argument("--candidate-manifest-sha256")

    p_audit = sub.add_parser("audit", help="retrospective git-forensic check on a historical spec/result pair")
    p_audit.add_argument("--spec-commit", required=True)
    p_audit.add_argument("--spec", nargs="+", required=True, dest="spec_paths")
    p_audit.add_argument("--result", nargs="+", default=[], dest="result_paths")
    p_audit.add_argument("--result-commit", default="HEAD")

    sub.add_parser("selftest", help="run the two built-in historical self-tests")

    args = parser.parse_args()
    repo_root = Path(args.repo_root).resolve()

    if args.cmd == "selftest":
        return _selftest(repo_root)
    elif args.cmd == "check":
        res = check_prospective(
            repo_root, args.run_class, args.spec_commit, args.spec_paths, args.result_paths,
            candidate_manifest=args.candidate_manifest,
            candidate_manifest_sha256=args.candidate_manifest_sha256,
        )
    else:
        res = check_audit(repo_root, args.spec_commit, args.spec_paths, args.result_paths, args.result_commit)

    print(res.report())
    return 0 if res.overall_pass else 1


if __name__ == "__main__":
    sys.exit(main())
