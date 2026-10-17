# History

Newest first. One entry per version.

## 0.2 — 2026-10-17 — Baseline RUL model

- Adds features (the 14 live sensors) and labels, and splits by engine: 20 of
  the 100 units are hidden before the first coefficient is fitted.
- Plain least squares on the fitting engines only: RMSE 46.3 cycles on the
  held-out engines against 71.0 for always guessing the average.
- Official test score, one prediction per test engine at its last recorded
  cycle: RMSE 30.2 cycles against 51.8 for the average guess, printed next to
  a like-for-like held-out number (27.9 vs 54.1) so the two are not confused.
- Third figure plots those 100 predictions against the truth and the error
  against true life, so the model's 18.8-cycle optimism is visible rather
  than buried.

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

- 1.0 — First release: reproducible from a clean clone using the README.
