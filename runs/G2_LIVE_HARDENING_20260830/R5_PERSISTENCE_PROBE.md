# R5 — RESTART PERSISTENCE: disk probe (orchestrator, 2026-08-30 ~08:0x ET)

Evidence gathered without restarting NT8, while both strategies were running/enabled and the
account was flat. Feeds the R4 lane and the runbook's open question.

## What the disk shows

- `WeeklyEdgeP1PCT_v1` / `WeeklyEdgeXMConflict_v2` appear **nowhere** in
  `workspaces/*.xml`, `Config.xml` or `UI.xml`, even though both are `Realtime` and
  `isEnabled: true`. The only hits outside `bin/` and `db/` are backtest artifacts
  (`strategyanalyzerlogs/`), the reflection cache, and today's `log/`.
- No CrossTrade registry file was found on disk (only `cache/CrossTrade-v1.13-*.Reflection.dat`),
  so the add-on's deployment registry appears to be **in-memory**.

## What that does and does not prove

**Does NOT prove** the strategies are lost on restart: NT8 writes workspace state on save/exit,
and these were added ~1 h ago programmatically via `StrategiesGrid.StrategyAdd`, so absence now is
equally consistent with "not yet flushed".

**Does establish** that there is currently **no on-disk record** of the running configuration —
so an NT8 *crash* (as opposed to a clean exit) would leave nothing to restore from, on either the
NT8 side or the add-on side.

## A second, independent persistence path exists — and it is the add-on's, not NT8's

The CrossTrade tool contract states, for `StopStrategy(remove_from_registry)`:
*"If true, deployment is removed from the registry (**won't be replayed on reconnect**). If false,
the strategy is closed but the deployment record stays — set to false when intentionally pausing
across a reconnect cycle."*

⇒ **The add-on replays registered deployments on reconnect.** Both of ours are registered. This is
a real recovery mechanism for a *connection* drop. It is untested for an NT8 *process* restart, and
if the registry is in-memory it cannot survive one.

## The experiment that settles it (run while FLAT, market closed)

1. Confirm flat + note `current_strategy_id` for both deployments.
2. Exit NT8 cleanly; check whether `workspaces/*.xml` now contains the strategy names.
3. Restart NT8, reconnect, and call `ListDeployedStrategies` + `ListStrategies`.
4. Record: (a) do the strategies exist? (b) are they *enabled*? (c) new or same strategy ids?
   (d) did the add-on replay them or did NT8 restore them?
5. Write the answer into `research/operational/NT8_RUNBOOK.md`.

⚠️ Until this is answered, **"NT8 is running" is a load-bearing precondition of the paper book**,
and an unattended overnight restart is an unquantified risk. The safe operating rule meanwhile:
**be flat before any deliberate restart**, and verify both strategies after every restart.
