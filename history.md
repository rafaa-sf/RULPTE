# History

Newest first. One entry per version.

## 0.1 — 2026-10-17 — Data and plots

- Notebook loads the FD001 train and test files, checks columns, row counts,
  engine counts and missing values, and asserts that the RUL file holds 100
  values.
- Labels every training row with `RUL = last cycle of that engine - cycle`,
  the standard C-MAPSS convention, and keeps all 20631 rows.
- Drops the seven sensors that never move (five distinct values or fewer,
  which includes the one that toggles between two adjacent readings) and
  keeps 14.
- Two figures: four selected engines with raw trace plus a 15-cycle rolling
  mean, and the fleet trend against RUL in four small panels with an
  interquartile band.

## Planned

- 0.2 — Baseline RUL model, scored by RMSE on the test engines.
- 1.0 — First release: reproducible from a clean clone using the README.
