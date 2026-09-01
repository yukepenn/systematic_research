# 🔴 THE BLIND POOLS ARE FROZEN BY NAME, NOT BY CONTENT — and the substrate moved

**2026-09-01.** Found by an adversarial data prosecution, then re-verified independently by the
orchestrator from the filesystem and from source. **No blind-pool bytes were read.** Everything
below is metadata — names, sizes, mtimes — which `research_sdk/data_census.py` establishes cannot
consume a seal.

---

## §1 THE MECHANISM

`research_sdk/blindguard.py` freezes a pool by taking a **normalised sha256 of the manifest CSV**:

```python
def normalized_sha256(path):
    b = open(path, "rb").read().replace(b"\r\n", b"\n")   # <- the MANIFEST file
    return hashlib.sha256(b).hexdigest()
```

`require_authorization` re-checks *that* hash. It therefore guards against **session
substitution** — someone quietly swapping which sessions are in the pool — which is a real threat
and is correctly guarded.

> **It is structurally blind to the underlying `.ncd` bytes changing.** The manifest is a **list of
> session names**. Nothing in the repo hashes, sizes or timestamps the data those names point at.

**Every protected pool in this repo uses this mechanism.** None is content-frozen.

## §2 🔴 AND THE SUBSTRATE DID MOVE — 48 to 92 minutes after the freeze

`BBO_BLIND_POOL_MANIFEST.csv` — 19 NQ full-BBO sessions — was committed at
**2026-08-28 08:23:40 ET** (`17bbb2d`). Measured from the filesystem today:

| | |
|---|---|
| sessions whose backing files were rewritten **after** that instant | 🔴 **15 of 19** |
| bytes rewritten | **588,524,279** |
| window | **2026-08-28 09:11:08 → 09:55:34 ET** |

**And it is not random churn. It is precisely a quote backfill:**

```
session 2025-09-04, contract NQ 09-25
  Ask   total= 24  rewritten_after_freeze= 24
  Bid   total= 24  rewritten_after_freeze= 24
  Last  total= 23  rewritten_after_freeze=  0     <- untouched
```

**Every Bid file. Every Ask file. Not one `Last` file.** The same 48/71 pattern appears on all
15 sessions.

**The four untouched blind sessions still carry 23 Bid / 23 Ask hourly chunks. The 15 rewritten
ones now carry 24 / 24 — one more hour of quote data each.**

Meanwhile the manifest still records, for **all nineteen**:

```
bid_coverage = 0.739     ask_coverage = 0.739     old_quote_class = PARTIAL
```

> 🔴 **The pool's DEFINING PROPERTY is quote coverage, and quote coverage is exactly what was
> backfilled after the freeze.** The manifest hash verifies. The guard reports the pool intact.
> By its own contract it is telling the truth — it was never built to see this.

## §3 THE HONEST LIMIT ON THIS FINDING

**An mtime change proves a file was WRITTEN. It does not prove its content DIFFERS.** NT8 may have
rewritten identical bytes.

**I cannot settle that without reading blind-pool data, and I will not.**

> **That is the defect, stated exactly.** The freeze mechanism makes the question **permanently
> unanswerable**. What *is* proven is that the null hypothesis — *"nothing touched the blind
> substrate after the freeze"* — is **falsified for 3 of 3 pools that could be measured**, and
> that the file-count change (23 → 24 quote chunks) is evidence of *added data*, not merely of
> rewritten identical data.

## §4 SCOPE

| pool | n | mechanism | substrate rewritten after freeze? |
|---|---:|---|---|
| **BBO_BLIND_POOL** | 19 | name list + manifest sha256 | 🔴 **15 of 19** (verified here) |
| **ESNQ_BLIND_15 / EFFECTIVE_14** | 15 | name list + parent/child sha256 | 🔴 **13 of 15** |
| **MICRO_BLIND_CONFIRMATION_POOL** | 141 | name list, **no hash sidecar found** | 🔴 **37 of 141** |
| W5 PROTECTED 168-pool | 168 | name list + per-file sha256 on the date `.txt`s | **UNKNOWN** — not re-measured; identical mechanism, identical exposure |
| GLOBAL VIRGIN ≥ 2026-08-01 | ongoing | **DATE RULE**, enforced by `research_sdk/seal_guard.py` | **n/a — a rule cannot go stale.** ✅ This one is sound. |

**Wider context: the NT8 store is not a static archive.** 12,825 of 48,334 pre-seal-dated `.ncd`
files have an mtime later than 2026-08-28, and 27 files were written after 2026-09-01 00:00Z.
NT8 backfills continuously, and **the live book keeps the store hot.**

⚠️ `runs/ESNQ_V1_20260828/INCIDENT_BLIND_EXPORT_20260828.md` §5 asserts *"Blind manifest
**unmutated**: 15 sessions, `f4a8090e…3c8a`"*. **That is true, and it is the wrong invariant to
have checked** — the rewrite it did not look for was happening in the same hour.

## §5 THE FIX — free, metadata-only, and it cannot restore the existing pools

Extend every manifest with a per-session **content fingerprint** over the backing `.ncd` set —
`(n_files, total_bytes, max_mtime)` at minimum, or a sha256 over the file *metadata* tuple — and
have `blindguard.require_authorization` verify it alongside the manifest hash. **No `.ncd` content
is read, so no seal is consumed.**

🔴 **Retro-fitting it now cannot restore the three existing pools.** Their pre-backfill state is
gone; there is no baseline to compare against. **The correct treatment of those pools is a
downgrade, not a repair:**

> **BBO_BLIND_POOL, ESNQ_BLIND_EFFECTIVE_14 and MICRO_BLIND_CONFIRMATION_POOL can no longer be
> claimed as content-frozen blind pools.** They remain valid as *session-substitution-guarded*
> populations, which is what the guard actually delivers. **Any result that rests on their
> blindness must state this limitation, and no new one-shot confirmation should be spent against
> them until they are re-frozen with content fingerprints.**

This does not touch the **`GENESIS_H1` pristine one-shot window** or the **≥ 2026-08-01 virgin
seal**, both of which are date rules and are unaffected.

## §6 WHY THIS MATTERS BEYOND THE POOLS

The repo has now recorded the same shape three times in one day:

1. `ListStrategies` returned an incomplete set and a confident audit was built on it.
2. The export-handle collision was declared cleared because **one** leg recovered.
3. A blind pool is declared intact because **the manifest** is intact.

**Each time, a guard reported truthfully on the thing it measured, and the thing it measured was
not the thing that mattered.** The general rule this earns:

> **State what a guard CANNOT see, in the guard's own docstring, next to what it can.**
> `blindguard.normalized_sha256` should say — and now says nothing about — *"this hashes the
> manifest, not the data; it detects session substitution and cannot detect substrate change."*
