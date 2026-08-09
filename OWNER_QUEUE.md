# OWNER_QUEUE — things that require the owner, and never halt the program

Created 2026-08-09 per MEGA PROMPT V6 §16. One entry per blocked item, kept current.
Nothing here stops a wave: the entry records what is needed, why, what it blocks, what was
done instead, and how much would change if it were resolved. Items are not repeated in wave
reports and are not re-requested every wave.

---

## OQ-1 — Repository is PUBLIC, and remote retention of the vendor DLL is UNVERIFIED
**Opened** 2026-08-09 (Wave 17, V3-R5). **Status** OPEN. **Severity** the highest-consequence
item in this file, and it is a licensing/exposure question, not a research one.

**The facts, separated by evidence class.**
- DIRECT: `gh repo view` reports `github.com/yukepenn/systematic_research` is
  **`visibility: PUBLIC`, isPrivate: false, forks 0, stars 0** as of 2026-08-09. This status
  had never been stated anywhere in the repo before now. `README.md` §6b records that the
  repository was *set private* on 2026-08-07 ~12:15 UTC; it is public again today.
- DIRECT: `git rev-list --objects --all` on the local clone returns **zero** objects matching
  `RenkoKings_SolarWaveRK_NT8.dll` or any `.dll`, and the blob-adding commit `35901db` named
  in README §6b does not exist in local history.
- **CORRECTION TO WAVE 16, and the Wave-16 claim was mine**: Wave 16 concluded from that
  second bullet that "the vendor DLL is not reachable anywhere in the current public
  repository history" and that the remediation "already happened and is already live on the
  public remote." **That conclusion is overstated and is hereby downgraded.**
  `git rev-list --objects --all` enumerates objects reachable in the **local** clone. It
  cannot test what the GitHub **remote** still serves. GitHub retains unreachable objects and
  will serve them by direct SHA until a support-requested garbage collection — which is
  precisely the residual risk README §6b warned about. The honest finding is:
  **"not reachable via normal history traversal; REMOTE RETENTION UNVERIFIED."**

**What is needed from the owner.** (a) A decision on whether this repository should be public
at all, given it contains a licensed vendor's reverse-engineered indicator math. (b) If the
vendor blob's removal from the remote matters, a GitHub Support request to garbage-collect
unreachable objects — the only action that actually erases them.

**What was done instead.** Reported factually, corrected the README banner in place (append,
not rewrite), and took **no** irreversible action: no force-push, no history rewrite, no
visibility change. §16 forbids acting here and V6 §7 V3-R5 says "report only, never act."

**How much would change if resolved.** Nothing numerical. This is an exposure/licensing
question with zero effect on any research result.

---

## OQ-2 — Exact NinjaTrader Lifetime all-in commission for NQ and MNQ
**Opened** 2026-08-09 (Wave 16 V4a, still open in Wave 17). **Status** OPEN. **Severity** low
for rankings, moderate for absolute net.

**What is needed.** The exact all-in per-side (or per-round-turn) commission the Lifetime plan
charges on NQ and MNQ, including exchange and NFA components.

**Why.** Every backtest in this program codes a flat **$4.36 round turn for NQ and $1.30 for
MNQ** (verified DIRECTLY: NT8 reports `commission: 2.18` per side on NQ fills and the trade
lists reconcile to the cent). NinjaTrader's live `/pricing/commissions/` page confirms the
schedule is dated **2026-07-01 and updated quarterly**, but its instrument-filtered NQ/MNQ
table did not render through WebFetch, so the coded figure is neither confirmed nor
contradicted. A single static rate across 2022-2026 is in any case not the historical truth.

**What was done instead.** Per V6 §7 V4a: no rate was invented. A **sensitivity band** is
computed instead (V4 friction ledger, `runs/W17_C4_COMPLIANCE/V4_FRICTION.md`) reporting net
P&L, Sharpe and friction share across a multiple of the coded rate, plus the breakeven
multiple at which each object's net reaches zero.

**How much would change if resolved.** The point estimate of net P&L and friction share. No
ranking or verdict in the program depends on it — the band brackets it.

---

## OQ-3 — NinjaScript recompile (F5) after a strategy edit
**Opened** 2026-08-09. **Status** RESOLVED-IN-PRACTICE, kept for the record.

`WriteNinjaScriptFile` reported `compile_engine: "file_only"`, i.e. its reflection-based
recompile trigger was unavailable and it warned that an owner F5 would be required. In
practice NT8 8.1.8.1 picked up the newly written `.cs` files anyway: a subsequent
`RunStrategyBacktest` resolved
`NinjaTrader.NinjaScript.Strategies.SolarWaveOneContractNQ_v2` and ran it. **`file_only` is
therefore not by itself proof that a compile is blocked** — verify by resolving the class,
not by trusting the flag. Recorded because it changes how future waves should read that
response, and because the reverse (a stale type served after an edit) remains possible: the
self-check used here is that a freshly-added property/output must actually appear.
