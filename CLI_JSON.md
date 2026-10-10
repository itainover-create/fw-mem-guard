# CLI JSON contract — version 1

Starting with 0.3.5, `fw-memguard compare project.fwmg.json --json` emits one JSON
object with `schemaVersion: 1` on exit 0 (PASS) or 2 (budget exceeded). Exit 1
indicates an input/runtime error: stdout is empty, diagnostics are on stderr.
Do not parse stderr as JSON or treat a missing report as PASS.

Within schemaVersion 1, existing fields retain their names, types and meaning.
New optional fields may be added. Consumers must ignore unknown fields and reject
unknown schema versions. Removal, type changes or changes in meaning require a
new schemaVersion. Array ordering and JSON property ordering are not contractual.

The native engine's existing `schema_version: 1` remains present for compatibility;
it describes the engine protocol, not this CLI contract. Project `schema: 1/2`
and the editor's reduced export `format_version: 1/2` are separate formats.

## Required comparison fields

| Field | Type / meaning |
|---|---|
| `schemaVersion` | Integer, currently 1 |
| `schema_version` | Integer, native engine protocol, currently 1 |
| `status` | `pass` or `budget_exceeded` |
| `validation` | `configured_linker_profile`; CLI additionally validates both MAP/ELF pairs |
| `attribution` | `gnu_input_sections` or `not_available` |
| `baseline`, `current` | Objects with nonnegative integer `flash` and `ram` allocated bytes |
| `delta` | Signed integer `flash` and `ram`; current minus baseline |
| `violations` | Array; empty on PASS, nonempty on exit 2 |
| `budgetChecks` | Array of every validated aggregate and configured per-bank check |
| `attributionCoverage` | Object with `flash` and `ram` metrics below, or null when attribution is unavailable |

Budget rows contain `memory` (`flash`/`ram`), `metric` (`usage_bytes`/`growth_bytes`),
integer `actual` and nonnegative integer `limit`. Per-bank rows additionally contain
`region` (string). A violation is strictly `actual > limit`; equality passes.

Optional `section_delta` maps output-section names to signed integer size changes.
Sections can include ignored/nonallocated content, so their sum need not equal
Flash/RAM growth. Optional `banks` maps names to `memory`, `capacity`, `baseline`,
`current`, `delta` in bytes; values reconcile with aggregate totals. Optional
`contributors` contains `objects`, `archives` and `unattributed`; object/archive
rows have `name` and baseline/current/delta Flash/RAM pairs. Archive rows regroup
objects and must not be added to them.

## Attribution percentages

For each memory class, `attributionCoverage` contains:

- `baselineUnattributedPercent`, `currentUnattributedPercent`: residual bytes /
  allocated bytes × 100. Null for zero total allocation.
- `netGrowthBytes`: current allocation minus baseline allocation.
- `unattributedDeltaBytes`: current residual minus baseline residual.
- `unattributedNetGrowthPercent`: signed residual change / net growth × 100;
  null when net growth is zero or negative. This may be negative or above 100%
  when identified contributions offset residual changes. It is never clamped.
- `positiveGrowthBytes`: sum of positive object deltas plus positive residual change.
- `positiveUnattributedGrowthBytes`: max(0, residual change).
- `unattributedPositiveGrowthPercent`: positive residual change / positive growth
  × 100; null for zero positive growth. Archive regroupings are excluded.

For example: identified objects shrink 90 B while residuals grow 100 B. Net
growth is 10 B, the residual/net ratio is 1000%, and the positive-growth ratio is
100%. No growth has been counted twice. Zero residual *change* does not imply
complete attribution: baseline and current allocations may both contain many
unattributed bytes. Use the current-allocation percentage alongside growth.

Percentages are numbers without a percent sign and may contain decimals. Round
only for display. These metrics describe recognized byte ownership, not statistical
confidence, source-line causality, or peak heap/stack usage.

The full CLI report can contain local object and archive paths. The editor's
reduced sharing export continues to omit them. Neither output uploads itself.
