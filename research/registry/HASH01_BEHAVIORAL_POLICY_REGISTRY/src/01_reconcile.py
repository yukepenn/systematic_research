#!/usr/bin/env python3
"""
HASH01_BEHAVIORAL_POLICY_REGISTRY / 01_reconcile.py

Bookkeeping/audit task (campaign directive sec22-27). NOT alpha research, and NOT a
claim that the registry gap documented in REGISTRY_GAP_NOTE.md (2026-08-07) is resolved.
Per sec25/sec66: "Statistical tools cannot restore lost preregistration."

Purpose: an honest trial-count reconciliation across
  - research/registry/tested_configs.csv           (contemporaneous registry, seq 1-90
                                                       Wave1/1b, then seq 230-498 post-gap-note)
  - research/registry/tested_configs_backfill.csv   (reconstructed registry, seq 91-229,
                                                       every row reconstructed=yes)
  - research/system_master/TESTING_LEDGER.csv       (a THIRD, separate registry -- family-level,
                                                       no seq numbers -- covers 2026-08-09/10 work
                                                       that was never logged into tested_configs.csv)

plus a distinct-architecture-vs-numeric-parameter-sweep classification of every DISTINCT
"experiment" value, and a check of whether post-gap-note work (seq > 229, and the
TESTING_LEDGER.csv families) restored the runs/<run_id>/spec.yaml-committed-before-results
convention that the gap note's own "Rule for any resumed work" required.

Does not modify tested_configs.csv, tested_configs_backfill.csv, or REGISTRY_GAP_NOTE.md.
"""
import csv
import json
import os
import subprocess
from collections import Counter, defaultdict

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
TESTED_CONFIGS = os.path.join(REPO_ROOT, "research", "registry", "tested_configs.csv")
BACKFILL = os.path.join(REPO_ROOT, "research", "registry", "tested_configs_backfill.csv")
TESTING_LEDGER = os.path.join(REPO_ROOT, "research", "system_master", "TESTING_LEDGER.csv")
OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "out")


# --------------------------------------------------------------------------------------
# 1. Load tested_configs.csv (schema-aware: header applies cleanly through seq ~319;
#    seq 320+ (SMV2B onward) uses a looser 8-14 column schema documented inline).
# --------------------------------------------------------------------------------------
def load_tested_configs():
    with open(TESTED_CONFIGS, newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))
    header = rows[0]
    assert header == [
        "seq", "date", "experiment", "run_id", "strategy", "timeframe",
        "params", "window", "cost_model", "purpose", "info_risk", "status",
    ]
    data = [r for r in rows[1:] if r and r[0].strip()]
    return header, data


def expand_seq_token(tok):
    """'6-33' -> [6,7,...,33] (a whole grid logged as one row = many trials).
    '230' -> [230]. '392a' -> ['392a'] (sub-id, kept as-is, not counted as a bare int)."""
    tok = tok.strip()
    if tok.isdigit():
        return [int(tok)]
    if "-" in tok:
        a, b = tok.split("-", 1)
        if a.isdigit() and b.isdigit():
            return list(range(int(a), int(b) + 1))
    return [tok]


def tc_experiment_and_run(row):
    """Schema-aware (experiment, run_id) extraction, keyed off the seq VALUE (not row
    length -- a few seq>=320 rows contain unescaped commas inside an unquoted params
    field, e.g. seq 366/367's "9 cells q{6,12,26}xN{390,780,1950}", which inflates their
    field count to look like the 12-column schema by accident. seq<320 is confirmed
    clean 12-column for every row in this file; seq>=320 (incl. letter-suffixed ids
    like '392a') is always the shifted schema: seq,family,run_id,params,window,result,status,date.
    12-column rows: standard header order (experiment=row[2], run_id=row[3])."""
    seq_tok = row[0].strip()
    is_pre_320 = seq_tok.split("-")[0].isdigit() and int(seq_tok.split("-")[0]) < 320
    if is_pre_320:
        return row[2], row[3]
    else:
        return row[1], row[2]


def analyze_tested_configs(header, data):
    seq_idx = header.index("seq")
    date_idx = header.index("date")
    expanded = []  # (seq_token, row)
    for row in data:
        for tok in expand_seq_token(row[seq_idx]):
            expanded.append((tok, row))

    int_tokens = [t for t, _ in expanded if isinstance(t, int)]
    str_tokens = sorted(set(t for t, _ in expanded if isinstance(t, str)))
    c = Counter(int_tokens)
    present_ints = set(c.keys())

    # seq buckets
    wave1_1b = sorted(x for x in present_ints if 0 <= x <= 90)          # contemporaneous, Wave1/1b
    gap_91_229 = sorted(x for x in present_ints if 91 <= x <= 229)      # should be EMPTY (backfill's turf)
    post_gap = sorted(x for x in present_ints if x >= 230)              # post-gap-note (2026-08-07 onward)

    missing_1_498 = sorted(set(range(1, 499)) - present_ints)

    return {
        "n_data_rows": len(data),
        "n_expanded_trial_slots": len(expanded),
        "n_distinct_int_seq": len(present_ints),
        "letter_suffixed_seq_ids": str_tokens,
        "seq_min": min(present_ints), "seq_max": max(present_ints),
        "wave1_1b_seq_present": wave1_1b,
        "gap_91_229_seq_present_should_be_empty": gap_91_229,
        "post_gap_note_seq_present": post_gap,
        "missing_seq_in_1_498": missing_1_498,
        "expanded_rows": expanded,
        "date_idx": date_idx,
    }


# --------------------------------------------------------------------------------------
# 2. Load tested_configs_backfill.csv
# --------------------------------------------------------------------------------------
def load_backfill():
    with open(BACKFILL, newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))
    header = rows[0]
    assert header == [
        "seq", "date", "experiment", "run_id", "strategy", "instrument", "params",
        "slip", "window", "cost_model", "purpose", "counts_as_trial", "reconstructed", "evidence",
    ]
    data = rows[1:]  # NOTE: keep blank-seq rows (parity gates) -- they are real data rows
    return header, data


def analyze_backfill(header, data):
    seq_idx = header.index("seq")
    counts_idx = header.index("counts_as_trial")
    recon_idx = header.index("reconstructed")
    with_seq = [r for r in data if r and r[seq_idx].strip()]
    blank_seq = [r for r in data if r and not r[seq_idx].strip()]
    seqs = [int(r[seq_idx]) for r in with_seq]
    distinct_seq = sorted(set(seqs))
    recon_flags = Counter(r[recon_idx].strip() for r in data if r)
    counts_yes = sorted(set(int(r[seq_idx]) for r in with_seq if r[counts_idx].strip().startswith("yes")))
    counts_no_rows = sum(1 for r in with_seq if not r[counts_idx].strip().startswith("yes"))
    parity_gate_rows = len(blank_seq)  # counts_as_trial = "no (parity gate)", seq intentionally blank
    return {
        "n_raw_rows_total": len(data),          # matches gap note's "296"
        "n_rows_with_seq": len(with_seq),
        "n_rows_blank_seq_parity_gates": parity_gate_rows,
        "seq_min": min(distinct_seq), "seq_max": max(distinct_seq),
        "n_distinct_seq": len(distinct_seq),
        "distinct_seq_all_91_to_229_present": distinct_seq == list(range(91, 230)),
        "reconstructed_flag_counts": dict(recon_flags),
        "n_seq_counted_as_trial_R1": len(counts_yes),   # = gap note's "139"
        "n_rows_not_counted_as_trial": counts_no_rows,  # stress reruns + parity gates
    }


# --------------------------------------------------------------------------------------
# 3. Overlap check between the two files
# --------------------------------------------------------------------------------------
def seq_overlap(tc_analysis, bf_analysis):
    tc_seqs = set()
    for tok, _row in tc_analysis["expanded_rows"]:
        if isinstance(tok, int):
            tc_seqs.add(tok)
    bf_seqs = set(range(bf_analysis["seq_min"], bf_analysis["seq_max"] + 1))
    return sorted(tc_seqs & bf_seqs)


# --------------------------------------------------------------------------------------
# 4. TESTING_LEDGER.csv -- a THIRD, separate registry (system_master campaign,
#    2026-08-09/10). Family-level, no seq numbers. Confirmed by grep that NONE of its
#    family names (AUCTION0x, EQV0x, GRID0x, PERT01, EXEC01, PLACEBO01, ...) appear
#    anywhere in tested_configs.csv or tested_configs_backfill.csv.
# --------------------------------------------------------------------------------------
def load_testing_ledger():
    if not os.path.isfile(TESTING_LEDGER):
        return None, []
    with open(TESTING_LEDGER, newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))
    header = rows[0]
    data = [r for r in rows[1:] if r and r[0].strip()]
    return header, data


def check_no_conflation(tc_analysis, bf_data, bf_header, ledger_data, ledger_header):
    """Verify TESTING_LEDGER family names do not appear as 'experiment' values in either
    tested_configs.csv or tested_configs_backfill.csv (would indicate double-logging)."""
    if not ledger_data:
        return {"checked": False}
    fam_idx = ledger_header.index("family")
    ledger_families = set(r[fam_idx] for r in ledger_data)

    tc_exps = set()
    for tok, row in tc_analysis["expanded_rows"]:
        exp, _run = tc_experiment_and_run(row)
        tc_exps.add(exp)

    bf_exp_idx = bf_header.index("experiment")
    bf_exps = set(r[bf_exp_idx] for r in bf_data if r)

    overlap_tc = ledger_families & tc_exps
    overlap_bf = ledger_families & bf_exps
    return {
        "checked": True,
        "n_ledger_families": len(ledger_families),
        "overlap_with_tested_configs_experiment_names": sorted(overlap_tc),
        "overlap_with_backfill_experiment_names": sorted(overlap_bf),
    }


# --------------------------------------------------------------------------------------
# 5. Preregistration-discipline check for post-gap-note work, via git history:
#    for each runs/<id>/ directory, does spec.yaml's first-add commit strictly PRECEDE
#    (by commit, not just by file mtime) the first commit that adds any non-spec.yaml
#    file in that same directory? That is the only git-verifiable proxy for "spec
#    committed before results were read" the gap note's own remediation rule asks for.
# --------------------------------------------------------------------------------------
def git_log_added_files(relpath):
    out = subprocess.run(
        ["git", "log", "--diff-filter=A", "--name-only",
         "--format=COMMIT|%H|%ad", "--date=iso-strict", "--", relpath + "/"],
        capture_output=True, text=True, cwd=REPO_ROOT,
    ).stdout
    entries = []
    cur = None
    for line in out.splitlines():
        if line.startswith("COMMIT|"):
            if cur:
                entries.append(cur)
            _, h, d = line.split("|", 2)
            cur = [h, d, []]
        elif line.strip():
            cur[2].append(line.strip())
    if cur:
        entries.append(cur)
    return entries  # newest -> oldest


def preregistration_audit():
    runs_dir = os.path.join(REPO_ROOT, "runs")
    if not os.path.isdir(runs_dir):
        return {"checked": False}
    dirs = sorted(d for d in os.listdir(runs_dir) if os.path.isdir(os.path.join(runs_dir, d)))
    per_dir = {}
    for d in dirs:
        entries = git_log_added_files(f"runs/{d}")
        if not entries:
            per_dir[d] = {"category": "NO_GIT_HISTORY"}
            continue
        spec_commit = None
        nonspec_commit = None
        for h, dt, files in reversed(entries):  # oldest -> newest
            has_spec = any(f.endswith("spec.yaml") for f in files)
            has_nonspec = any(not f.endswith("spec.yaml") for f in files)
            if has_spec and spec_commit is None:
                spec_commit = (h, dt)
            if has_nonspec and nonspec_commit is None:
                nonspec_commit = (h, dt)
        if spec_commit is None:
            per_dir[d] = {"category": "NO_SPEC_EVER"}
        elif nonspec_commit is None:
            per_dir[d] = {"category": "SPEC_ONLY_NO_RESULTS_DETECTED", "spec_commit": spec_commit}
        elif spec_commit[0] == nonspec_commit[0]:
            per_dir[d] = {"category": "SAME_COMMIT_spec_and_results", "commit": spec_commit}
        elif spec_commit[1] < nonspec_commit[1]:
            per_dir[d] = {
                "category": "SPEC_BEFORE_RESULTS_genuine_prereg",
                "spec_commit": spec_commit, "results_commit": nonspec_commit,
            }
        else:
            per_dir[d] = {
                "category": "SPEC_AFTER_RESULTS_backfilled",
                "spec_commit": spec_commit, "results_commit": nonspec_commit,
            }
    cat_counts = Counter(v["category"] for v in per_dir.values())
    return {"checked": True, "per_dir": per_dir, "category_counts": dict(cat_counts)}


# --------------------------------------------------------------------------------------
# 6. Experiment-level classification: (a) pure numeric-parameter sweep of the SAME
#    finite controller vs (b) genuinely distinct architecture/mechanism/data-source
#    decision vs (N) not an architecture-search trial at all (infrastructure, audit,
#    diagnostic, validation gate, holdout-consumption event) vs (U) mixed/unclassifiable
#    as filed (the registry's own "experiment" label bundles rows from more than one
#    of the above and would need sub-splitting before dedup could safely apply).
#
#    Basis: each row's own purpose/hypothesis_class/description text (read in full,
#    not guessed) plus repo context (CLAUDE.md frozen baseline; GRID01's own
#    already-established convention that VolMult grid density/spacing is a pure
#    numeric axis of the SAME Solar member architecture).
# --------------------------------------------------------------------------------------

# tested_configs.csv / backfill: experiment(family)-level classification
TC_CLASSIFICATION = {
    # ---- Wave 0 infra / validation / null-control (NOT architecture-search trials) ----
    "PARITY": ("N", "UI/MCP parity gate, not a trial (gap note's own rule: parity gates are not trials)"),
    "SW00": ("N", "determinism + baseline + cost-stress + fill-resolution + parallel-submission infra checks on the SAME frozen baseline config"),
    "SW01": ("N", "ledger-export instrumentation, no strategy variant"),
    "SW01c": ("A", "same frozen baseline params evaluated on an additional data window (2022) + slip stress; no decision-rule change"),
    "SW01b": ("B", "SW01bRandomEntryV1 -- a genuinely different strategy class (random entry) used as a null-control architecture"),
    "SW02a": ("B", "introduces a timed forced-flatten exit mechanism (EndTime ladder) not present in the session-close baseline; the ladder of times within it is numeric, but the mechanism itself is new"),
    "W1_REF": ("N", "full-history reference rerun of the canonical config, not a swept variant"),
    "W1_S1": ("A", "TM x SM spatial grid -- pure numeric axes of the same Solar Wave member architecture"),
    "W1_S2": ("A", "same strategy run at different bar timeframes (2m/3m/5m) -- bar-period is a numeric aggregation axis, decision rule unchanged"),
    "W1_S3": ("A", "Slowdown x WWS temporal grid -- pure numeric axes"),
    "W1_S4": ("B", "EntrySignalType {0,1,2,3} -- a categorical/qualitative mode switch in the vendor indicator's own decision rule, not a continuous numeric knob"),
    "W1b": ("A", "dense SM grid (1m and 3m) -- pure numeric plateau-mapping sweep"),
    "W1C": ("A", "backfill: tf x sm grid, wave1c Tier-2 confirmation -- pure numeric grid, same architecture as W1_S1/W1b"),
    "H011": ("B", "backfill: stop-order vs market-order execution mechanics -- a genuinely different fill/execution mechanism, not a numeric parameter"),
    "W2": ("U", "backfill: BUNDLES multiple genuinely different hypotheses under one experiment label -- 'fixed-threshold wide sweep' and 'H-012 sigma-estimator robustness' are numeric (a); 'H-006 adaptive threshold', 'H-007 split exit/reversal', 'H-008 anchor definition', 'H-006 x H-008 combo' are each distinct decision-rule mechanisms (b); plus non-trial parity gates. Needs sub-splitting by purpose column before any dedup pass, not a single dedup unit as filed."),
    "W3": ("U", "backfill: BUNDLES 'wave-index conditioning', 'H-014 price vs volatility', 'ES portability' (different instrument = data-source decision), 'C2 Type-3 re-entry (adaptive/fixed core)', 'C4 Type-2+Type-3' -- almost entirely (b)-type distinct mechanism/data-source decisions, plus non-trial parity gates. Needs sub-splitting."),
    # ---- Program B candidates (post-gap-note, seq230-232) ----
    "B01": ("B", "python_vector_orb_fade and python_vector_gapfade -- two genuinely distinct mechanisms (opening-range-breakout fade, gap fade), not parameter variants of Solar Wave or of each other"),
    # ---- Portability / operational variants (seq233-284) ----
    "PORT01": ("B", "same Solar-Wave-family construction ported to YM/RTY/CL -- a different INSTRUMENT/data-source decision per the task's own category (b), not a numeric sweep"),
    "DM01": ("A", "day-margin time-filter window sweep (1800-1640) on the already-adopted SolarWaveOpenV3 -- numeric operational-window axis"),
    "C01T1_EXPOSURE": ("B", "vol-surprise-tercile exposure overlay -- a new regime-conditioning decision layer, not a numeric knob on the existing controller"),
    "C01T1_ML": ("B", "logistic-regression meta-label overlay -- a genuinely new ML-based decision mechanism"),
    # ---- SYSTEM_MASTER V1 (seq285-319) ----
    "SM03_DISASTER_STOP": ("B", "introduces a close-basis disaster-stop layer not present in the frozen system; the m-multiplier grid within it is incidental numeric variation"),
    "SM03B_DISASTER_STOP_INTRABAR": ("B", "same as SM03 but intrabar-extreme trigger -- a different trigger MECHANISM (extreme vs close basis), not a reparameterization of SM03"),
    "SM04_CONSENSUS_SHAPE": ("B", "different vote-to-target mapping functions (U1/U2/U3/D1) -- distinct decision-mapping mechanisms"),
    "SM07_TRENDDAY_UPWEIGHT": ("B", "new frozen-on-history gap/IB trend-day classifier conditioning the existing target -- new conditioning mechanism"),
    "SM08_HTF_TILT": ("B", "new HTF-agreement-based exposure tilt mechanism (first adoption of an HTF conditioning layer)"),
    "SM10_VOLTRANSITION_ENGINE": ("B", "standalone daily engine (compression-state classifier -> directional hold) -- a wholly new, independent architecture, not a variant of Solar/BMOM"),
    "SM11_HOLDOUT_READ": ("N", "single preregistered holdout-consumption READ of already-frozen candidates, not itself a new architecture or a parameter sweep"),
    "SM14_ONELOT_DAYMARGIN": ("B", "new discretization mechanism collapsing the continuous multi-lot target to sign+hysteresis 1-lot trading; the (a,b) hysteresis-threshold grid within it is incidental numeric variation"),
    # ---- SolarWaveMasterV2 continuous-evolution program ----
    "SMV2A_DD_RECONCILE": ("N", "drawdown-reconciliation diagnostic, not a strategy variant"),
    "SMV2B": ("A", "BMOM fill-timing variants (signal-close / next-open / +1t / +2t slip) -- execution/cost-model axis of the same B-MOM decision logic, decision rule itself unchanged"),
    "SMV2C": ("A", "portfolio blend-weight sweep across Solar/BMOM/B1 sleeves (P0-P3) -- numeric allocation axis of the same multi-engine construction"),
    "SMV2E": ("U", "s0-s100 is a pure numeric short-scale multiplier (a); c1_htfup_short* vs c2_counterHTF_* are two DIFFERENT conditioning mechanisms (asymmetric-iff-HTF-up vs symmetric counter-HTF) (b) -- needs sub-splitting"),
    "SMV2E-ext": ("A", "plateau-neighbor extension of the c1 (HTF-up-conditional) mechanism's own numeric ladder -- same mechanism as SMV2E's c1 arm"),
    "SMV2F_LEVERAGE_ROBUST": ("N", "leverage/robustness diagnostic pass, per RunID naming (not present as CSV rows; see LEVERAGE_ROBUSTNESS.md)"),
    "SMV2G": ("B", "8 DIFFERENT HTF/trend feature constructions (SMA20/SMA100/EMA50/Donchian50mid/ret50/ret100/SMA50slope5/dualSMA50_200) -- distinct feature-mechanism decisions, not a numeric sweep of one formula"),
    "SMV2H": ("U", "one-contract construction program: introduces a NEW discretization mechanism (hysteresis one-lot mapping) with several genuinely different variants (A_dominant BMOM-first routing, B_sign, C_hyst thresholds, E_conflictflat, G_router_htf) (b) each a distinct routing/conflict-resolution rule, plus SM14_ref_oldM31 as a reference rerun (N) -- needs sub-splitting by variant letter"),
    "SMV2H2": ("A", "plateau-confirmation reruns of the A_dominant mechanism's own s5/s7/s9 numeric ladder -- same mechanism as SMV2H's A_dominant arm"),
    "SMV2I": ("U", "C-P1 CDaR/EDaR/Ulcer blend-weight sweep (a); C-P3 leverage-multiplier grid (a); C-P4 drought-tilt mechanism + its own placebo battery (b, new conditioning mechanism); C-P7 windfall event-study (N, diagnostic pretest not itself a candidate) -- needs sub-splitting"),
    "SMV2J": ("B", "Variance-Ratio and Efficiency-Ratio state-harness constructions -- new feature/mechanism, not a numeric sweep of an existing one"),
    "SMV2K": ("B", "Engine-3 failed-break-fade / small-gap-fade / overnight-drift -- three genuinely distinct trading mechanisms"),
    "SMV2M": ("B", "SolarWaveSMMaster_v2 -- the consolidated multi-engine architecture integration point itself, a foundational build milestone, not a sweep"),
    "SMV2N": ("B", "windfall give-back/trim POLICY -- a new decision mechanism (plus its own placebo/chronology validation, N)"),
    "SMV2O": ("B", "Kalman innovation-whiteness and BOCPD regime-age -- two distinct new state-estimation mechanisms/data representations"),
    "SMV2P": ("B", "Engine-3 value-area-rotation / multiday-false-break / month-end-flow -- three distinct trading mechanisms"),
    "SMV2Q": ("N", "diagnostics bundle, not a strategy variant"),
    "SMV2R": ("U", "bundles a numeric vol-memory-window sweep (a) with T2T3 new signal-LAYER addition and cohort-membership ablation (b, both architecture decisions) and a clamp audit (N, diagnostic) -- needs sub-splitting"),
    "SMV2S": ("A", "HTFgated_dominant threshold sweep (thr3/5/7) -- numeric threshold axis of the already-introduced HTF-gated dominant-routing mechanism"),
    "SMV2T": ("B", "NoFAST_R2_confirm -- ablation test removing a component ('FAST') from the architecture, a structural not numeric change"),
    "SMV2U": ("B", "different clock/bar-construction conventions (1m/5m bar-matched vs time-matched) -- a construction-mechanism decision, not a numeric knob"),
    "SMV2V": ("B", "ER150 damper -- new damping POLICY mechanism (plus its own placebo/chronology validation, N)"),
    "SMV2W": ("B", "5m clock R2 -- same clock-construction-mechanism family as SMV2U"),
    "SMV2X": ("B", "Engine-3 shock-continuation / macro-drift (FOMC/CPI) / opex-unclamp-breakout -- three distinct trading mechanisms"),
    "SMV2Y": ("N", "weekly viability diagnostics measuring existing state features (sigma460/ER150/flip-rate/VR) -- measurement, not a new architecture"),
    "SMV2Z": ("A", "viability-gating POLICY threshold sweep (s050/070/085) -- numeric threshold axis of one fixed gating mechanism"),
    "SMV2AA": ("A", "portfolio mix-shift -- numeric weight axis"),
    "SMV2AB": ("B", "Engine-3 slate-4 constructions -- distinct trading mechanisms"),
    "SMV2AC": ("B", "level-1 joint logistic ML overlay -- new ML-based decision mechanism"),
    "SMV2AD": ("U", "VolMult ceiling numeric sweep (a) bundled with 'extended cohort add/replace' (b, a cohort-membership architecture decision) and an old-regime screen (N, validation) -- needs sub-splitting"),
    "SMV2AE": ("A", "1-minute rescale of the existing ensemble -- same decision rule at a different bar resolution, a numeric/portability axis"),
    "SMV2AF": ("N", "gate battery (dev-bootstrap / LOYO-chronology / old-regime / diversification / overall-verdict) -- a promotion-gate validation pass on an already-built candidate, not itself a new architecture or sweep"),
    "SMV2AG": ("B", "adaptive clamp -- a new clamp MECHANISM (adaptive vs the existing fixed clamp), a structural not numeric change"),
    "SMV2AH": ("B", "day circuit-breaker -- a new risk-control mechanism (threshold_calibration and circuit_breaker_sweep_16cell are numeric sweeps within it)"),
    "SMV2AI": ("B", "ATR-blend construction -- a new volatility-scale construction mechanism (replace_blend_sweep_4arm is a numeric blend-weight sweep within it)"),
    "SMV2AJ": ("N", "gate battery (dev-bootstrap / LOYO / old-regime-dual / right-tail / portfolio / weight-robustness / overall-verdict) for the ATR-blend candidate -- validation, not a new architecture"),
    "SMV2AK": ("B", "volume-bar construction -- a new bar-construction/data-representation decision (distinct from time bars), not a numeric knob"),
    # ---- W16-W19 / R-series / S-series / SA0 -- infra, audits, forensics, red-team ----
    "W16-V1": ("N", "flatten-time audit (NQ/MNQ) -- forensic verification, not a strategy variant"),
    "W16-V1b": ("N", "origin-of-1639 forensic investigation"),
    "W16-V2": ("N", "overshoot-ratio trailing measurement -- diagnostic"),
    "W16-V3": ("N", "repo exposure status check -- infra"),
    "W16-V4a": ("N", "commission/margin verification -- infra"),
    "W17-V1R1": ("N", "flatten audit -- forensic"),
    "W17-V1R2": ("N", "MNQ flatten root-cause -- forensic"),
    "W17-V1h-V1e": ("N", "margin-window exposure audit -- forensic"),
    "W17-V1R3": ("N", "C4 rebuild v2 -- infra fix, not a strategy variant"),
    "W17B-C3": ("N", "C4 watchdog v4 -- infra"),
    "W17-V4": ("N", "friction-share ledger -- accounting/diagnostic"),
    "W17-V1d": ("N", "late-entry census -- diagnostic"),
    "W17-V1f": ("N", "event-day margin leverage -- diagnostic"),
    "W17-O1": ("N", "primary-objective build -- infra (utility-function module build)"),
    "W17-DIAG": ("N", "warmup start-state sensitivity -- diagnostic"),
    "W18R1-M1": ("B", "intraday vol-seasonality D4 construction -- a new conditioning mechanism"),
    "W18R2-M5": ("B", "ATR-blend cross-instrument replication -- new construction ported cross-instrument"),
    "W18-E1": ("N", "holdout-consumption determination -- protocol/governance decision, not a trial"),
    "W18-F": ("N", "warmup convergence measurement -- diagnostic"),
    "W18E-C4": ("N", "Product-A C4 propagation check -- forensic"),
    "W18R1-RT": ("N", "M1 red-team review -- adversarial audit, not a new trial"),
    "W18R2-RT": ("N", "M5 red-team review -- adversarial audit"),
    "W18-STAND": ("N", "stub-concentration caution note -- diagnostic"),
    "W18-O1R": ("N", "O1 blind repair -- infra fix"),
    "W19-R4": ("N", "seal-audit standing check -- governance"),
    "W19-D7": ("B", "2026 regime diagnostic construction -- but closed advisory, borderline; classified N since no candidate was constructed (diagnostic-only per its own TESTING_LEDGER row)"),
    "W19-R3": ("N", "O1 blind-review agreement -- governance/adjudication"),
    "W19-D7RT": ("N", "D7 red-team review -- adversarial audit"),
    "W19R1": ("B", "w19r1 selectivity run -- a new selectivity-filter construction"),
    "W19R1RT": ("N", "w19r1 red-team review -- adversarial audit"),
    "S0": ("N", "time-of-day autopsy -- diagnostic"),
    "S2-ARMA": ("B", "ARMA-based selectivity-timing construction -- new mechanism"),
    "S2RT": ("N", "red-team review of S2 -- adversarial audit"),
    "S2-R2": ("N", "S2 adjudication -- governance decision, not a new trial"),
    "P4-CHURN": ("N", "churn-selectivity autopsy -- diagnostic"),
    "D-WINNER": ("N", "winner autopsy -- diagnostic"),
    "E3-S5": ("B", "Engine-3 slate-5 cross-market construction -- new mechanism/data-source (cross-market)"),
    "X1X2": ("N", "execution-friction audit -- forensic"),
    "V1R4": ("N", "NT8 parity verification -- infra, not a trial"),
    "V1R4-P2": ("N", "warmup forensics -- diagnostic"),
    "V1R4-P3": ("N", "defect-3 BMOM-flatten bugfix -- infra fix"),
    "V1R4-P4": ("N", "full-history chunked certification -- infra/verification"),
    "R1-A": ("N", "P0 tradestate-ledger autopsy -- diagnostic"),
    "R1-B": ("B", "adaptive-exit giveback overlay -- new exit-mechanism construction"),
    "R2": ("B", "entry-confirmation giveback construction -- new entry mechanism"),
    "R2V1": ("N", "confirm2 formal adjudication -- governance decision on R2's own construction"),
    "SA0": ("N", "system-structure failure-mode science -- diagnostic/taxonomy, not a trial"),
    "SA0-ADDENDUM": ("N", "current edge-health monitoring -- diagnostic"),
    "R3": ("N", "seltime state diagnostic -- diagnostic"),
    "R2B": ("B", "pullback-reclaim adaptive-entry construction -- new entry mechanism"),
    "R4": ("N", "slope/impulse residual-information diagnostic -- feature-information test, no candidate constructed"),
    "R5": ("N", "microstructure OHLCV-proxy diagnostic -- feature-information test, no candidate constructed"),
    "R6": ("N", "Engine-3 audit, no candidate constructed -- diagnostic"),
    "PA0-PA1": ("N", "Product-A structural decomposition -- diagnostic/specification, not a trial"),
    "SYN": ("N", "2026-08-09 final synthesis writeup -- not a trial"),
    # Defensive: seq366/367 rows contain unescaped commas inside an unquoted params
    # field ("9 cells q{6,12,26}xN{390,780,1950}") that can fool naive column-count
    # schema detection into extracting this token as if it were the family name. It is
    # in fact part of SMV2J's own B-H1_variance_ratio sub-experiment (row untouched in
    # source; belt-and-suspenders entry in case a future parse ever mis-splits it again).
    "B-H1_variance_ratio": ("B", "same as SMV2J: Variance-Ratio state-harness construction -- new feature/mechanism"),
}

# TESTING_LEDGER.csv family-level classification (research/system_master/, 2026-08-09/10,
# NEVER logged into tested_configs.csv -- confirmed by grep, zero name overlap).
LEDGER_CLASSIFICATION = {
    "W5_PROTECTED_CONFIRMATION": ("U", "protected-pool confirmation batch spanning 3 different families (AUCTION01 D4 replication, AUCTION02 rate-limiter policy, FLOW01 PRE_EXIT) -- needs sub-splitting, not one dedup unit"),
    "U6B_ADVERSARIAL_REVIEW": ("N", "independent adversarial review verdict on an existing candidate, not a new construction"),
    "U6B_CAPITAL_FRONTIER_INTRADAY_DD": ("N", "diagnostic capital-frontier measurement of an existing candidate"),
    "U6B_FORWARD_READINESS": ("N", "diagnostic uncertainty-quantification panel"),
    "EVIDENCE01_REPORT_TRACEABILITY": ("N", "audit re-deriving headline numbers from source, infra/verification"),
    "O2_NUMERIC_PROVENANCE_AUDIT": ("N", "audit correcting stale numbers in canonical docs, infra"),
    "AUCTION02_ACTION_RELEVANCE": ("B", "NQ_VOLUME_AT_PRICE-based rate-limiter policy -- new data source + new decision mechanism"),
    "DOM01_COLLECTOR": ("N", "forward L2-data collector build, infra, never run"),
    "U0_UNIFIED_STATE": ("N", "shared causal state table build, infra"),
    "U2_DATA_AUDIT": ("N", "data-availability audit, not a trial"),
    "H0_PRODUCT_A_HEALTH": ("N", "current-health diagnostic panel on the existing incumbent"),
    "U1_SESSION_HETEROGENEITY": ("N", "diagnostic on existing incumbent, no candidate constructed"),
    "U3_HOLD_EXPOSURE_CONTINUATION": ("N", "diagnostic, no candidate constructed"),
    "U4_SHORT_MECHANISM": ("N", "diagnostic (giveback_ratio checkpoint measurement), no candidate constructed here (feeds U4B)"),
    "U5_SOFT_WEIGHTING": ("N", "diagnostic, confound found pre-construction, no candidate"),
    "U6_PRODUCT_A_PATH_DEPENDENCE": ("N", "diagnostic, no candidate constructed"),
    "U7_2026_TIMING_REGIME": ("N", "diagnostic, explains an anomaly, no candidate"),
    "WAVE1_SYNTHESIS": ("N", "EVI-ranking synthesis note, not a trial"),
    "U4B_SHORT_DECAY_DERISK": ("B", "signal-gated short early-flatten construction -- new exit-conditioning mechanism"),
    "WAVE2_EVI": ("N", "synthesis note, not a trial"),
    "SHADOW01_SETUP_COMPATIBILITY": ("N", "diagnostic feature test, no construction attempted"),
    "U1B_SESSION_HOLD_POLICY": ("B", "session/hold POLICY construction (2 legs) -- new decision mechanism"),
    "U6B_PRODUCT_A_SCALE_RATE": ("B", "bounded continuous scale-rate multiplier -- new sizing mechanism"),
    "U8_PATH_ORGANIZATION": ("B", "new organization-level feature class construction"),
    "U9_TRUE_MICROSTRUCTURE": ("N", "infrastructure/design pass (frozen prequential design), no candidate computed"),
    "U8B_ORGANIZATION_TRANSITION": ("B", "organization-transition feature construction -- new mechanism"),
    "U9B_MICROSTRUCTURE_ALPHA": ("B", "genuine order-flow/BBO-tick data source -- first true microstructure test, new data source"),
    "LEV01_VOLATILITY_ASYMMETRY": ("N", "diagnostic market-structure test, confound caught, no candidate constructed"),
    "SKEW01_RETURN_SKEWNESS": ("B", "new skewness-feature construction (though ultimately closed weak)"),
    "LEV02_TRAILING_REGIME": ("N", "diagnostic regime-signal test, clean null, no candidate"),
    "PORT01_AB_PORTFOLIO_SYNTHESIS": ("N", "portfolio-level quantification of an already-known correlation fact, non-alpha by its own label"),
    "EXP01_MARGINAL_EXPOSURE_SHAPE": ("N", "diagnostic shape-measurement, reassuring null, no candidate"),
    "WAVE4_TRUTH_AUDIT": ("N", "repo-truth verification audit, infra"),
    "SPEC01_SESSION_LEAK_AUDIT": ("N", "specification-defect audit, resolved not-a-defect"),
    "PRICE01_PRODUCT_A_GENUINE_MNQ": ("B", "genuine-MNQ dual-truth repricing -- a distinct pricing/data-source decision vs the NQ-proxy substrate used throughout the rest of the campaign"),
    "COMBO01_MULTIMODAL_SYNERGY": ("B", "AUCTION x FLOW interaction construction -- new combined-mechanism test"),
    "FLOW01_AGGRESSIVE_PARTICIPATION": ("B", "NQ_BIDASK_TICKS order-flow features at in-position checkpoints -- new data source"),
    "AUCTION01_VALUE_STATE": ("B", "NQ_VOLUME_AT_PRICE causal running POC/value-share state -- new data source (first genuinely new information class this campaign)"),
    "VAR01_VARIANCE_SIGNATURE": ("B", "multi-scale realized-variance feature construction -- new feature/mechanism"),
    "REL01_CONDITIONAL_CROSSMARKET": ("N", "scoping-only literature pass, no construction attempted"),
    "SOFT01_CONTINUOUS_WEIGHTING_AUDIT": ("N", "resolved by reference to an existing construction (U6B), no new construction"),
    "ADD01_PARTICIPATION_EXPANSION": ("B", "reachable-M enumeration + EntryLevel participation-expansion construction -- new mechanism"),
    "WIN01_WINNER_EXIT_RELAXATION": ("B", "exit-hysteresis relaxation construction (2 products x multiple cells) -- new exit mechanism"),
    "ICT0102_EVENT_SEQUENCE": ("B", "PDH/PDL sweep/rejection/MSS structural-event features -- new mechanism/feature class"),
    "MOM01_INTRADAY_MOMENTUM": ("B", "literature-based intraday-momentum feature test -- new feature/mechanism (though null result)"),
    "O2_OWNER_UTILITY_READJUDICATION": ("N", "utility-function readjudication of EXISTING candidates on real P&L -- adjudication, not a new construction"),
    "DATA02_MICROSTRUCTURE_INVENTORY": ("N", "read-only data inventory, infra"),
    "WAVE4_FRONTIER_O2_GAMMA_AUDIT": ("N", "cross-family audit/synthesis, infra"),
    "AUCTION03_MECHANISM_DECOMPOSITION": ("B", "bounded M1-M5 mechanism slate on Auction substrate -- distinct decomposition mechanisms, though not promoted"),
    "DOM01_DEPLOY_NT8_FEASIBILITY": ("N", "deployment-feasibility check, infra"),
    "EQV01_BEHAVIORAL_CANONICALIZATION": ("N", "specification/representation-equivalence audit -- explicitly not alpha, per its own status field"),
    "GRID01_SOLAR_RESOLUTION_CONVERGENCE": ("A", "VolMult grid density/spacing (G7/G13/G25/G49) -- pure numeric axis of the SAME Solar member architecture, explicitly diagnostic zero-alpha-budget per its own status"),
    "GRID02_ENDPOINT_PERTURBATION": ("A", "VolMult grid endpoint sweep [5,29]/[6,30]/[7,31] -- pure numeric axis, same architecture as GRID01"),
    "PERT01_STRUCTURAL_INVARIANCE": ("A", "one-at-a-time numeric perturbation of VolPeriod/BAND_DAYS/TiltSma -- pure numeric axes of the existing architecture, explicitly diagnostic"),
    "EXEC01_PRODUCT_A_DOLLAR_ATTRIBUTION": ("N", "execution-forensics dollar reconciliation, not a strategy variant"),
    "EQV02_FULL_HISTORY_ARRAY_EQUALITY": ("N", "specification/representation-equivalence audit -- explicitly not alpha"),
    "AUCTION04_CLEAN_CAUSAL_SUBSTRATE": ("B", "rebuilt causal Auction substrate + re-run of the M1-M5 mechanism slate -- data-integrity replication of a (b)-type family"),
    "EQV03_PNL_EQUALITY": ("N", "specification/representation-equivalence audit -- explicitly not alpha"),
    "PLACEBO01_COMPONENT_CAUSALITY": ("N", "causal placebo/falsification battery on EXISTING components (B-MOM, HTF, hysteresis, sizing) -- diagnostic falsification test, not a new construction"),
}


def classify(header_experiments, mapping, source_label):
    out = []
    for exp in header_experiments:
        cat, note = mapping.get(exp, ("U", "not classified by this script -- read the row before dedup"))
        out.append({"source": source_label, "experiment": exp, "category": cat, "note": note})
    return out


CATEGORY_LABEL = {
    "A": "parameter_sweep_same_architecture",
    "B": "distinct_architecture_mechanism_or_datasource",
    "N": "not_an_architecture_search_trial (infra/diagnostic/audit/validation/governance)",
    "U": "mixed_or_unclassifiable_as_filed (needs sub-splitting before any dedup)",
}


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    tc_header, tc_data = load_tested_configs()
    tc = analyze_tested_configs(tc_header, tc_data)

    bf_header, bf_data = load_backfill()
    bf = analyze_backfill(bf_header, bf_data)

    ledger_header, ledger_data = load_testing_ledger()

    overlap = seq_overlap(tc, bf)
    conflation_check = check_no_conflation(tc, bf_data, bf_header, ledger_data, ledger_header)

    prereg = preregistration_audit()

    # -------- trial-count bounds, extended to today --------
    # Gap note basis (2026-08-07): lower = 90 (Wave1/1b contemporaneous) + 139
    # (backfill distinct-param reconstructed) = 229. Upper = 383 (every ledger row incl reruns).
    wave1_1b_contemporaneous = 90  # reused from gap note; Wave1+1b seq set = {0,1,2..90}, 90 is
                                    # the note's own count treating seq=1's 18 infra rows and
                                    # seq=0's 5 null-control rows as NOT independently countable
                                    # trials (consistent with "parity gates are not trials" and
                                    # info_risk=none rows being explicitly non-trials).
    backfill_distinct_param = bf["n_seq_counted_as_trial_R1"]          # 139
    backfill_all_ledger_rows = bf["n_raw_rows_total"]                  # 296 (gap note's 383-90-... check below)

    # Post-gap-note bucket (seq >= 230 in tested_configs.csv): count DISTINCT seq slots
    # (ranges already expanded) as the lower-bound analogue of "distinct parameter sets",
    # and total expanded trial-slots (incl every range-expanded member) as the upper-bound
    # analogue of "every ledger row including reruns" -- consistent with how Wave1/1b's
    # own ranges (e.g. "6-33") were already counted as 28 distinct trials, not 1.
    post_gap_int_seq = tc["post_gap_note_seq_present"]
    post_gap_letter_ids = [t for t in tc["letter_suffixed_seq_ids"]]
    post_gap_lower = len(post_gap_int_seq) + len(post_gap_letter_ids)
    # upper bound for post-gap-note: same as lower here, since (unlike Wave1c-3's backfill)
    # tested_configs.csv logs slip-stress reruns as their OWN seq additions only where they
    # were assigned one (e.g. B01/PORT01 slip variants share one seq w/ the base -- already
    # reflected by range expansion); no separate "counts_as_trial" flag exists post-320 to
    # further discount, so lower==upper for this bucket under the same-methodology extension.
    post_gap_upper = post_gap_lower

    lower_bound_today = wave1_1b_contemporaneous + backfill_distinct_param + post_gap_lower
    upper_bound_today = wave1_1b_contemporaneous + 383 - 229 + post_gap_upper  # 383 already included 90+? see note
    # NOTE on upper bound arithmetic: the gap note's own upper bound (383) already = wave1/1b (90)
    # + backfill ALL ledger rows (296) - 3 blank-seq parity gates (not counted even in the upper
    # bound, since "parity gates are not trials at all" per the note's own R1 rule) = 90+293=383.
    upper_bound_today = wave1_1b_contemporaneous + (bf["n_raw_rows_total"] - bf["n_rows_blank_seq_parity_gates"]) + post_gap_upper

    # TESTING_LEDGER.csv families are NOT counted in either bound: it uses n_candidate_constructions
    # / n_parameter_cells / n_promotion_attempts, a fundamentally different unit of account (family-
    # level, not row-level trial slots), and was never reconciled against the tested_configs.csv R1
    # rule. Reported separately, not folded into the tested_configs.csv-based bound.
    ledger_family_count = len(set(r[ledger_header.index("family")] for r in ledger_data)) if ledger_data else 0
    ledger_param_cells_sum = sum(int(r[ledger_header.index("n_parameter_cells")]) for r in ledger_data) if ledger_data else 0
    ledger_candidate_constructions_sum = sum(int(r[ledger_header.index("n_candidate_constructions")]) for r in ledger_data) if ledger_data else 0

    # -------- experiment classification --------
    tc_exp_names = []
    seen = set()
    for tok, row in tc["expanded_rows"]:
        exp, _run = tc_experiment_and_run(row)
        if exp not in seen:
            seen.add(exp)
            tc_exp_names.append(exp)
    bf_exp_names = sorted(set(r[bf_header.index("experiment")] for r in bf_data if r))
    ledger_exp_names = sorted(set(r[ledger_header.index("family")] for r in ledger_data)) if ledger_data else []

    tc_classified = classify(tc_exp_names, TC_CLASSIFICATION, "tested_configs.csv")
    bf_classified = classify(bf_exp_names, TC_CLASSIFICATION, "tested_configs_backfill.csv")
    ledger_classified = classify(ledger_exp_names, LEDGER_CLASSIFICATION, "TESTING_LEDGER.csv")

    all_classified = tc_classified + bf_classified + ledger_classified
    cat_counts = Counter(r["category"] for r in all_classified)
    unclassified = [r for r in all_classified if r["note"].startswith("not classified")]

    # -------- assemble output --------
    summary = {
        "generated_by": "research/registry/HASH01_BEHAVIORAL_POLICY_REGISTRY/src/01_reconcile.py",
        "purpose": "bookkeeping/audit reconciliation, not alpha research; does not resolve the "
                   "governance gap documented in REGISTRY_GAP_NOTE.md (2026-08-07); "
                   "REGISTRY_GAP_NOTE.md itself is unmodified",
        "q1_seq_overlap": {
            "overlap_set_tested_configs_vs_backfill": overlap,
            "is_empty": len(overlap) == 0,
            "tested_configs_gap_91_229_present_rows": tc["gap_91_229_seq_present_should_be_empty"],
            "backfill_seq_range": [bf["seq_min"], bf["seq_max"]],
            "interpretation": (
                "EMPTY overlap confirmed. tested_configs.csv contains seq {0,1}x infra-placeholders, "
                "then 2-90 (Wave1/1b, one seq per trial), then a clean GAP at 91-229 (zero rows), "
                "then resumes at 230 through 498 (with skips at 392/407-409 and letter-suffixed "
                "sub-ids 392a/392b/423b/437b/437c). tested_configs_backfill.csv fills exactly and "
                "only that 91-229 gap (139 distinct seq, all reconstructed=yes). No double-counting risk."
            ),
        },
        "q1b_third_registry_no_conflation": conflation_check,
        "q2_categorization": {
            "contemporaneous_wave1_1b": {
                "seq_range": "0-90 (per tested_configs.csv; 0/1 are shared infra placeholders, "
                              "2-90 one seq per trial)",
                "n_rows_in_file": sum(1 for tok, row in tc["expanded_rows"] if isinstance(tok, int) and tok <= 90),
                "governance_status": "genuinely contemporaneous per campaign convention in force through Wave 1b "
                                      "(commit 9a2fff3); reused from gap note, not re-derived",
            },
            "reconstructed_backfill": {
                "seq_range": "91-229",
                "n_distinct_seq": bf["n_distinct_seq"],
                "n_raw_rows": bf["n_raw_rows_total"],
                "governance_status": "reconstructed=yes on ALL rows; preregistration guarantee explicitly "
                                      "NOT restored for this bucket per REGISTRY_GAP_NOTE.md -- reused verbatim, not re-derived",
            },
            "post_gap_note": {
                "seq_range": "230-498 (tested_configs.csv) + TESTING_LEDGER.csv families (no seq numbers)",
                "n_distinct_seq_or_letter_id_tested_configs": post_gap_lower,
                "n_distinct_families_testing_ledger": ledger_family_count,
                "governance_status": "MIXED, see preregistration_audit below -- NOT a uniform pass",
            },
        },
        "q3_trial_count_bounds_today": {
            "methodology": "same as gap note (lower = contemporaneous + reconstructed-distinct-param; "
                            "upper = every ledger row incl. reruns, excluding non-trial parity gates), "
                            "extended to include the post-gap-note tested_configs.csv bucket "
                            "(seq 230-498). TESTING_LEDGER.csv reported SEPARATELY (different unit of "
                            "account, family-level not row-level; never reconciled to the R1 rule).",
            "wave1_1b_contemporaneous": wave1_1b_contemporaneous,
            "backfill_distinct_param_R1": backfill_distinct_param,
            "backfill_all_rows_minus_parity_gates": bf["n_raw_rows_total"] - bf["n_rows_blank_seq_parity_gates"],
            "post_gap_note_tested_configs_lower": post_gap_lower,
            "post_gap_note_tested_configs_upper": post_gap_upper,
            "lower_bound_TODAY": lower_bound_today,
            "upper_bound_TODAY": upper_bound_today,
            "previously_published_bracket_2026_08_07": [229, 383],
            "testing_ledger_separate_accounting": {
                "n_families": ledger_family_count,
                "sum_n_parameter_cells": ledger_param_cells_sum,
                "sum_n_candidate_constructions": ledger_candidate_constructions_sum,
                "note": "NOT folded into lower/upper bound above -- different unit of account "
                        "(family-level summary stats self-reported by each family's own agent, not "
                        "individually-numbered per-config rows); would need its own row-level ledger "
                        "before it can be combined with the tested_configs.csv R1 rule.",
            },
        },
        "preregistration_audit_post_gap_note": {
            "method": "for every runs/<id>/ directory, compare the git commit that FIRST ADDS "
                      "spec.yaml against the git commit that FIRST ADDS any other file in that "
                      "directory. 'genuine preregistration' requires the spec commit to strictly "
                      "PREDATE the results commit -- the only git-verifiable proxy for 'spec "
                      "committed before results are read'.",
            "category_counts": prereg.get("category_counts"),
            "interpretation": (
                "MIXED, not a clean restoration. Roughly 60% of runs/ dirs with git history "
                "(SPEC_BEFORE_RESULTS_genuine_prereg) DO show a verifiably-separate preregistration "
                "commit preceding the results commit -- spanning 2026-08-06 (SW00) through "
                "2026-08-09 (WIN01, U9B, etc.), including the immediate post-gap-note recovery "
                "(B01C_ORB_FAIL, PORT01_SWEEPS, DM01, SM03-SM14: spec explicitly 'frozen before any "
                "result read' in separate earlier commits, confirming the campaign DID follow its "
                "own gap-note remediation rule for that stretch). But a material fraction "
                "(SAME_COMMIT_spec_and_results, ~24% of dirs, plus NO_SPEC_EVER dirs) shows spec.yaml "
                "(where one exists at all) and REPORT.md/src/out all landing in ONE commit -- e.g. "
                "AUCTION01_VALUE_STATE, AUCTION02, ADD01, FLOW01, VAR01, REL01, GAMMA00, O2, PRICE01, "
                "COMBO01, all dated 2026-08-09/10. The research/system_master/{GRID01,GRID02,PERT01,"
                "EQV01,EQV02,EQV03,PLACEBO01}/ directories (outside runs/ entirely) show the SAME "
                "same-commit pattern for src+out+REPORT.md, and EXEC01/AUCTION03 have NO spec.yaml at "
                "all. So: the LATEST wave of work (2026-08-09/10, essentially all of TESTING_LEDGER.csv "
                "plus the tail of runs/) does NOT carry a git-verifiable preregistration guarantee, "
                "despite prose language inside several REPORT.md files asserting 'preregistered' or "
                "'frozen before any result read' -- that assertion is not independently checkable "
                "against commit history the way the 2026-08-07/08 recovery period's spec.yaml-first "
                "commits are."
            ),
            "conclusion_answers_task_q3": (
                "NO, not uniformly. Post-gap-note work does NOT all inherit a clean pass. The "
                "2026-08-07/08 stretch (roughly seq 230-319, B01 through SM14) genuinely restored "
                "spec-before-results discipline and should NOT inherit the Wave1c-3 governance-failure "
                "caveat. The 2026-08-09/10 stretch (SMV2* tail, W16-19/R-series audits, and essentially "
                "all of TESTING_LEDGER.csv incl. AUCTION0x/EQV0x/GRID0x/PERT01/EXEC01/PLACEBO01) shows "
                "same-commit or absent spec artifacts and should carry a caveat of its own -- better "
                "documented and contemporaneously logged than Waves 1c-3 (no reconstruction-after-the-"
                "fact was needed; REPORT.md/out/ were written the same day as the work), but not "
                "git-verifiably preregistered either."
            ),
            "per_dir_detail_note": "full per-directory categorization retained in reconciliation.json "
                                    "under preregistration_audit_post_gap_note.per_dir",
            "per_dir": prereg.get("per_dir"),
        },
        "q4_experiment_classification": {
            "category_definitions": CATEGORY_LABEL,
            "category_counts": dict(cat_counts),
            "n_distinct_experiments_classified": len(all_classified),
            "unclassifiable_count": len(unclassified),
            "rows": all_classified,
        },
    }

    with open(os.path.join(OUT_DIR, "reconciliation.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, default=str)

    with open(os.path.join(OUT_DIR, "reconciliation.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["source", "experiment", "category", "category_label", "note"])
        for r in all_classified:
            w.writerow([r["source"], r["experiment"], r["category"], CATEGORY_LABEL[r["category"]], r["note"]])

    print("=== Q1: seq overlap ===")
    print("overlap set:", overlap, "(empty=" + str(len(overlap) == 0) + ")")
    print()
    print("=== Q3: trial count bounds TODAY ===")
    print("lower:", lower_bound_today, " upper:", upper_bound_today,
          " (2026-08-07 bracket was 229-383)")
    print()
    print("=== Preregistration category counts (post-gap-note runs/ dirs) ===")
    print(prereg.get("category_counts"))
    print()
    print("=== Q4: experiment classification counts ===")
    print(dict(cat_counts))
    print()
    print("Wrote:", os.path.join(OUT_DIR, "reconciliation.json"))
    print("Wrote:", os.path.join(OUT_DIR, "reconciliation.csv"))


if __name__ == "__main__":
    main()
