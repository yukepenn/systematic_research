# AGENTS.md

Read [`CLAUDE.md`](CLAUDE.md) first. It is the operating contract.

- **Active campaign:** #7 `WEEKLY_EDGE` (`research/weekly_edge/`).
- **Current research state:** `research/weekly_edge/CURRENT_BASELINE.md`.
- **Current executable state:** `research/operational/EXECUTION_MANIFEST.md`.
- 🔴 **THERE IS A LIVE REAL-MONEY BOOK** since 2026-09-01: account `2047681`, the M_11 pair
  executing on MNQ at `MnqPerNq = 3`. **Read `research/operational/CURRENT_LIVE_TRUTH.md` before
  touching anything.**
- **Bootstrap = README + CLAUDE + CURRENT_LIVE_TRUTH + CURRENT_BASELINE.** Nothing else by default.
- **Do not read `research/archive/` or `runs/` recursively** to orient yourself.
- **Never place, modify or cancel an order. Never enable, disable, resize or start a strategy** —
  including on `2047681`, and including when the owner asks; enabling is an owner action performed
  in the NT8 UI. The agent may **read** the live account freely.
- ⛔ **Never send strategy source through the CrossTrade MCP** — `CompileNinjaScript` /
  `WriteNinjaScriptFile` / `ReadNinjaScriptFile` on our own classes are banned (CLAUDE.md §1).
- Spec committed before results. No force-push. No history rewrites.
- Data ≥ 2026-08-01 is sealed.
