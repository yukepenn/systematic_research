# SPEC_HASHES — SHA-256 of every frozen file this bundle depends on

Computed 2026-08-09, before any protected-pool value was loaded. Reproduce with:
`python3 -c "import hashlib; print(hashlib.sha256(open('<path>','rb').read()).hexdigest())"`
for any row below, and compare against the hash here — any mismatch means the file changed after
freezing and the bundle must be re-frozen before the pool may be opened.

| SHA-256 | file |
|---|---|
| `b068475384142cbf71fc78bd2f51e0ac530f06eb449d30b255141cf725fee3f3` | runs/AUCTION01_VALUE_STATE/spec.yaml |
| `7b4eb3bb62d699bb6ac0687b83b363824f4a3150ef4a27c67e93800d71a505f8` | runs/AUCTION01_VALUE_STATE/src/02_build_poc_substrate.py |
| `0c276c2daf1b7d6c7aeea87a3a056513db7892d4694114880d296b796e68dce1` | runs/AUCTION01_VALUE_STATE/src/03_diagnostics.py |
| `e46f7baa39a4d0d64f38bd05c9b4fdcbbe8a701a33baa5a20841ea86b0a2a752` | runs/AUCTION02_ACTION_RELEVANCE/spec.yaml |
| `4d609caf7b2a10a1ad3d05a3bf6c4bbbaf75cf3257a56755cf1e1285d0bff94c` | runs/AUCTION02_ACTION_RELEVANCE/src/01_build_action_substrate.py |
| `83703e3baf7e92226260c8072f800a12a914909ed5faa6554e2a9d3f3cfe1b30` | runs/AUCTION02_ACTION_RELEVANCE/src/02_step1_diagnostics.py |
| `a8111a809ddeee4a1719ae5bb3c10b21e2fbd7d29c92ae26ca19a5a986d01ded` | runs/AUCTION02_ACTION_RELEVANCE/src/03_step2_redundancy_check.py |
| `92ca10e73e64cb2f00b5f89bc7e3f7b6ec97bbf392fc58aa3a960ad614859a62` | runs/AUCTION02_ACTION_RELEVANCE/src/04_step4_combination_sandbox.py |
| `ac978ef6f2fcbdd7dd0d9d62b343f62852793d8743ca0a7140668e89a06eeb05` | runs/AUCTION02_ACTION_RELEVANCE/src/stats_lib_auction02.py |
| `72ddb38382e941bb02be39d135080e76e7f8b5cd849ee6bdd78ab76b66a1b535` | runs/FLOW01_AGGRESSIVE_PARTICIPATION/spec.yaml |
| `7dbbe2bbb8e6afe6d457d23757e196b5db60c66a11a44917c48d9d2ba81626ce` | runs/FLOW01_AGGRESSIVE_PARTICIPATION/src/01_build_checkpoint_features.py |
| `5cfd72257670cc9c43e5cff6a7a1d89be4be04ddcf52333040389cd6821c3a03` | runs/FLOW01_AGGRESSIVE_PARTICIPATION/src/02_analysis.py |
| `867d2581ba5ba1900970457e870a8d708f21e039c56b0eb6f99322b10707454d` | runs/W5_PROTECTED_CONFIRMATION/MASTER_PREREGISTRATION.md |
| `bf7dc3031f2380cb9ecfbffa07b4ef0f536f14271afde4337e901d40de23a73d` | runs/W5_PROTECTED_CONFIRMATION/PRIMARY_ENDPOINTS.md |
| `daced649bc1d6d66ab08ec2c21867e31ff8060617aed24d83689945b6e2a3776` | runs/W5_PROTECTED_CONFIRMATION/MULTIPLE_TESTING_PLAN.md |
| `2f9f9dcf67a6d172c6b43080b544c56164c4e3c538e8218d7227cdbcbc0b9e68` | runs/W5_PROTECTED_CONFIRMATION/FAILURE_RULES.md |

`ELIGIBLE_SESSION_MANIFEST_METADATA_ONLY.csv`'s own hash is intentionally **not** included here —
it is metadata built by directory-listing the pool's file existence (per sec18's explicit
allowance), not a hypothesis/threshold/code artifact, and it is expected to be the last file
generated before the freezing commit. Its content is auditable directly (dates, file counts, no
outcome values) rather than hash-pinned.

**Freezing commit**: this file, once all rows above are confirmed unchanged, is committed to git
together with the rest of the bundle. That commit's hash is the audit anchor per
`FAILURE_RULES.md`'s sign-off clause.
