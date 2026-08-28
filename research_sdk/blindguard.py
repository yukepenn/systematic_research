"""blindguard.py -- PHYSICAL AND LOGICAL ISOLATION OF A BLIND POOL.  ENGINEERING_ONLY / ZERO_ALPHA.

A blind pool is an IRREVERSIBLE asset. It is destroyed not by a decision to spend it but by an
accident: a glob that matched one extra file, a QA pass that touched price paths, a "quick sanity
check" on the whole export directory. This module makes those accidents fail loudly.

TWO INDEPENDENT MECHANISMS, because a single one is a single point of failure:

  1. assert_no_blind_contamination(inputs, blind_manifest)
        a BLOCKING intersection assertion the development runner calls before it reads anything.

  2. BLIND_SPEND_AUTHORIZED artifact
        the blind runner refuses to execute until an authorization file exists that names the
        development adjudication, the measured effect size, the power against THAT effect, and an
        explicit human decision. Passing every development gate is NECESSARY AND NOT SUFFICIENT --
        a pool that cannot adjudicate the claim must not be spent on it.

The second mechanism exists because the failure mode is not carelessness, it is momentum: every
gate passed, so the next step feels automatic. It is not automatic.
"""
from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone

import pandas as pd


class BlindPoolViolation(AssertionError):
    """Raised when blind data is about to be read without authorization. Never caught."""


def load_manifest(path: str, col: str = "session_date") -> set:
    return set(pd.read_csv(path)[col].astype(str))


def normalized_sha256(path: str) -> str:
    """Line-ending independent content hash.

    A tamper-evidence hash that changes with a git checkout setting is a weak one: the BBO pool
    manifest hashed differently in the working tree (CRLF) than in the committed blob (LF) while
    the content was identical. Normalise, then hash.
    """
    b = open(path, "rb").read().replace(b"\r\n", b"\n")
    return hashlib.sha256(b).hexdigest()


def assert_no_blind_contamination(input_sessions, blind_manifest_path: str, *,
                                  label: str = "development runner") -> int:
    """BLOCKING. Abort if any input session is in the blind manifest."""
    blind = load_manifest(blind_manifest_path)
    got = {str(s) for s in input_sessions}
    bad = sorted(got & blind)
    if bad:
        raise BlindPoolViolation(
            f"{label}: {len(bad)} BLIND session(s) present in the input set -- {bad[:5]}"
            f"{' ...' if len(bad) > 5 else ''}. The blind pool is irreversible; aborting.")
    return len(got)


def assert_disjoint(dev_manifest_path: str, blind_manifest_path: str) -> None:
    d, b = load_manifest(dev_manifest_path), load_manifest(blind_manifest_path)
    inter = sorted(d & b)
    if inter:
        raise BlindPoolViolation(f"development and blind manifests intersect on {inter}")
    if not d or not b:
        raise BlindPoolViolation("a manifest is empty -- refusing to certify isolation")


def write_authorization(path: str, *, development_run: str, mu_dev: float, se_blind: float,
                        power_vs_zero: float, power_vs_null: float, min_power: float,
                        decision: str, rationale: str, blind_manifest_path: str) -> dict:
    """Write BLIND_SPEND_AUTHORIZED. Only a decision of 'AUTHORIZED' unlocks the blind runner."""
    if decision not in ("AUTHORIZED", "WITHHELD"):
        raise BlindPoolViolation(f"decision must be AUTHORIZED or WITHHELD, got {decision!r}")
    if decision == "AUTHORIZED" and power_vs_zero < min_power:
        raise BlindPoolViolation(
            f"cannot authorize: power to reject a collapse to zero is {power_vs_zero:.3f} < the "
            f"PREDECLARED minimum {min_power:.3f}. A pool that cannot adjudicate the claim must "
            f"not be spent on it.")
    rec = {"artifact": "BLIND_SPEND_AUTHORIZED", "decision": decision,
           "written_utc": datetime.now(timezone.utc).isoformat(),
           "development_run": development_run, "mu_dev_per_session": mu_dev,
           "se_blind_per_session": se_blind, "power_vs_zero": power_vs_zero,
           "power_vs_economically_null": power_vs_null, "min_power_required": min_power,
           "rationale": rationale,
           "blind_manifest": os.path.basename(blind_manifest_path),
           "blind_manifest_sha256_normalized": normalized_sha256(blind_manifest_path)}
    with open(path, "wb") as fh:
        fh.write(json.dumps(rec, indent=2).encode("utf-8"))
    return rec


def require_authorization(auth_path: str, blind_manifest_path: str) -> dict:
    """BLOCKING. The blind runner calls this FIRST and aborts unless authorization exists."""
    if not os.path.exists(auth_path):
        raise BlindPoolViolation(
            f"BLIND_SPEND_AUTHORIZED not found at {auth_path}. The blind pool may not be read. "
            f"Passing every development gate is NECESSARY AND NOT SUFFICIENT.")
    rec = json.loads(open(auth_path, "r", encoding="utf-8").read())
    if rec.get("decision") != "AUTHORIZED":
        raise BlindPoolViolation(f"authorization decision is {rec.get('decision')!r}, not AUTHORIZED")
    got = normalized_sha256(blind_manifest_path)
    if rec.get("blind_manifest_sha256_normalized") != got:
        raise BlindPoolViolation(
            f"blind manifest CHANGED since authorization: authorized "
            f"{rec.get('blind_manifest_sha256_normalized')}, found {got}. Session substitution "
            f"after a decision is exactly what a frozen manifest exists to prevent.")
    return rec
