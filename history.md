# History

Newest first. One entry per version.

## 1.5 — 2026-10-17 — Remove the look-ahead

- Review found a forward leak: the 20-cycle mean was centred, so every row used
  the next ten cycles — information a running engine does not have. It is now the
  trailing mean, and the per-condition normalisation is fitted on the training
  engines only, never on the held-out ones.
- Every number moved, because the old ones were optimistic. FD001 test 35.6 →
  28.3 cycles, FD002 35.0 → 33.5; intervals ±45.9 / ±49.8 covering 85% and 84%;
  cross-validation 41.5 ± 2.2 / 41.0 ± 2.4.
- The honesty of the middle: the 42 features buy only about one cycle over the 14
  raw sensors (38.6 against 39.6 random-cut), and the model's optimism now runs
  from +2 near failure to about +30 in mid-life, turning negative past 140.

## 1.4 — 2026-10-17 — From number to decision

- The notebook ends by turning the pessimistic end of the interval into an
  action: GROUND, INSPECT, PLAN or MONITOR, with the 259 FD002 test engines
  counted into those four bands.
- `predict.py` is the tool: `train` writes a 9 kB `model.npz`, `predict` answers
  for any C-MAPSS file, `score` reproduces the published numbers.
- Four pytest checks keep the tool and the notebook in agreement, and CI now
  runs both `run.py --check` and `run.py --test` on every push.

## 1.3 — 2026-10-17 — How stable, and how it compares

- Repeated grouped cross-validation (5 folds by engine, 5 repeats, a fresh random
  cut each time) puts the model at 38.9 ± 2.4 cycles on FD001 and 38.5 ± 1.8
  on FD002, so the 35.6 / 35.0 test scores sit within one spread: differences of
  a couple of cycles are noise, not progress.
- Error by true life is now printed: worst on the engines with the longest to
  live (54.1 cycles at 150+ on FD001), best close to failure (24.2 at 0-50).
- README and GUIDE place the result against published work with one citation
  (attention-LSTM, 12.33 on FD001) and say plainly that this is a floor, not
  parity.

## 1.2 — 2026-10-17 — Hard subset, real features

- The data layer now spans all four subsets: FD001 and FD003 fly in one operating
  condition, FD002 and FD004 in six, and every sensor is standardised inside its
  own condition before it reaches the model.
- Each cycle becomes 42 features — the 14 live sensors at their current value,
  their 20-cycle average and their 20-cycle change — instead of 14 raw readings.
- The headline is FD002, the hard subset: 35.0 cycles RMSE on its 259 test
  engines against 59.8 for always guessing the average. FD001 scores 35.6 against
  51.8. FD001 was 30.2 under the old 14-feature model; the features were chosen
  on held-out engines cut at random cycles (35.8 against 39.6 on FD001, 37.7
  against 39.8 on FD002), never on the test score, so that 30.2 was one
  favourable draw of 100 engines rather than a better model.
- Every prediction now carries a nominal 80% interval, calibrated on held-out
  engines cut early: ±42.7 cycles on FD001, ±48.4 on FD002, covering 71% and 83%
  of the official answers. The shortfall is printed, not tuned away.
- All three figures share one design language: colour means drift direction, grey
  is context, and the dash pattern identifies the engine.

## 1.1 — 2026-10-17 — One command from clone to results

- `run.py` replaces the five hand-typed steps: it creates `.venv`, installs the
  pinned libraries plus the notebook viewer, downloads the data on first run,
  and opens the notebook. Every step is skipped when it is already done.
- `python run.py --check` runs the notebook headless and fails if the expected
  scores stop appearing, so the README's promise is testable.
- GitHub Actions runs exactly that on a clean runner for every push, from a
  `Python 3.12` image with no libraries preinstalled.
- The README quick start is three lines now; the step-by-step route stays below
  it for readers who want to see each move.

## 1.0 — 2026-10-17 — First release

- The notebook is `rul_prediction.ipynb`: it opens with a "Before you start"
  cell, closes with the author's introduction and conclusions, and ships with
  its outputs saved, so the three figures are visible before running anything.
- Shippable from a clean clone: `requirements.txt` pins pandas 3.0.6,
  numpy 2.5.4 and matplotlib 3.11.2, `download_data.py` fetches the data, and
  the README walks from the GitHub page to a finished run with a Results table,
  a troubleshooting section and the NASA data credit.
- Scores unchanged from 0.2 and restated in one table: 30.2 against 51.8 on the
  official test engines, 46.3 against 71.0 held out, 27.9 against 54.1 like for
  like.
- A reviewer followed the README in a clean clone; the gaps it found are fixed.

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

- 1.2 — Optional: a model that corrects the mid-life optimism, and the same
  study on FD002 (six operating conditions) to show what the baseline loses.
