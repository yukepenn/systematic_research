# Vendor-binary remediation plan — P0 governance track

_2026-08-07, POST_CAMPAIGN_AUDIT_01. Status: **CONTAINED AT TIP, NOT ERASED FROM HISTORY.**
History erasure is **HUMAN ACTION REQUIRED** — the constitution forbids autonomous history
rewrites, and this document deliberately does not perform one._

## 1. Incident summary

The licensed RenkoKings vendor package was committed to this repository in `35901db`
(2026-08-06) and pushed to a **public** GitHub repository (`yukepenn/systematic_research`),
violating the constitution's *never redistribute vendor binaries* boundary. Affected paths:

| path | nature |
|---|---|
| `SolarWaveRK/RenkoKings_SolarWaveRK_NT8.dll` | licensed vendor assembly, 4.5 MB |
| `SolarWaveRK/RenkoKings_SolarWaveRK_NT8.cs` | NT8 auto-generated wrapper stub (no vendor logic, still vendor-named) |
| `SolarWaveRK/Info.xml` | vendor package manifest |
| `SolarWaveRK/AdditionalReferences.txt` | vendor package metadata |
| `SolarWaveRK/templates/Indicator/RenkoKings_SolarWaveRK/*.xml` | two vendor display templates |

## 2. Timeline (all times UTC, 2026)

| when | event |
|---|---|
| 08-06 23:46 | repository created public |
| 08-06 ~22:16 local | `35901db` commits the vendor directory |
| 08-07 ~12:15 | first audit discovers the exposure; repository set **private** |
| 08-07 (later) | repository found **PUBLIC again** (re-opened, presumably for the external GitHub-render audit that produced Constitution v2; `pushedAt` 2026-08-07T12:49Z) |
| 08-07 (this audit) | repository set **private** again via `gh repo edit` — verified `visibility: PRIVATE` |
| 08-07 (this audit) | discovery that the vendor files were **still tracked at HEAD** (never removed from the tree — every push re-published them, and the README §6b disclosure understated this as "remains in git history") |
| 08-07 (this audit) | `git rm --cached` of all six vendor paths + `.gitignore` guard, commit `1f169ae` on `post_campaign_audit`. Files remain on disk (user's licensed installation copy) and remain reachable in history |

At first remediation: 0 forks, 0 stars. Total public exposure: two windows, roughly
12.5 h + ~10 h. Any clone taken during either window contains the blob.

## 3. What has been done (autonomous, within constitution)

1. Repository visibility set **PRIVATE** (constitution step 1; reversible; explicitly directed).
2. Vendor paths **untracked at tip** on `post_campaign_audit` (`1f169ae`) — a normal forward
   commit, not a history rewrite. Pushing this branch no longer publishes the files.
3. `.gitignore` guard added: `SolarWaveRK/`, `*.dll`, `*.zip`, `*.7z`.
4. No vendor file was read, inspected, decompiled, or modified. The working-tree copies are
   untouched.

## 3b. Second-red-team disclosure: containment is LOCAL-ONLY until pushed

The remote (`origin/research-campaign`, tip `e5079e1`) still **tracks the full
vendor package in its tree** — not merely in history. Any authorized clone of the
remote checks the vendor files out. The untracking commit `1f169ae` exists only on
the local `post_campaign_audit` branch. Mitigation: repository visibility is
PRIVATE (re-verified by the red team). Pushing `post_campaign_audit` puts a
vendor-free tip on the remote but does not change `research-campaign`'s tip; that
branch's remediation is bundled into the HUMAN ACTION list below.

## 4. What remains — HUMAN ACTION REQUIRED

The blob is still **reachable in git history** of every branch (`research-campaign`,
`post_campaign_audit`, `origin/research-campaign`) because `35901db` is an ancestor of all of
them. Erasure requires, in order:

1. **Decide** to rewrite history (owner decision; constitution forbids autonomous execution).
2. Preserve a private archival bundle: `git bundle create <safe-location>/pre-rewrite.bundle --all`.
3. Run `git filter-repo --invert-paths --path SolarWaveRK/` on a fresh clone
   (filter-repo, not filter-branch; BFG is the fallback).
4. Force-push all rewritten refs (`research-campaign`, `post_campaign_audit`, `main` if present).
5. Ask GitHub Support to run garbage collection and drop cached views / unreachable objects
   (dangling blobs remain fetchable by SHA until GC).
6. Re-clone or clean every local working copy (old clones recontaminate on push).
7. Note: commit SHAs change; this document's SHA references become historical names.
8. Keep the repository **private permanently**, or at minimum until steps 3–6 are complete;
   if it must be public again, that decision must follow the rewrite, not precede it.

## 5. Prevention now in force

- `.gitignore` blocks the vendor directory and all `*.dll`/`*.zip`/`*.7z`.
- Audit-branch policy: never `git add .`; stage only explicitly named files (constitution §14).
- Recommended (human, optional): a pre-push hook rejecting any blob > 1 MB or matching
  vendor patterns; not installed autonomously because hooks are untracked local state.

## 6. Interaction with the research program

The research itself is **vendor-independent**: every published campaign figure was produced by
the vendor-free `SolarWaveOpen*` strategies, and RE01/RE02 established exact behavioural parity.
The vendor package is needed only for the two legacy parity gates (`SolarWaveRKReplicaV0`,
ledger exporters). Erasing it from history destroys no research evidence.
