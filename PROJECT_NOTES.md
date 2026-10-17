# Project: Remaining Useful Life Prediction for Turbofan Engines (RUPLTE)

## Goal
Portfolio project on NASA C-MAPSS (sub-dataset FD001 only), in Python.
Milestone 1: load data, plot degradation curves.
Milestone 2: simple baseline regression on remaining useful life (RUL),
scored with RMSE.
Milestone 1.5: make it shippable from GitHub (see below).
Out of scope: FD002-FD004, deep learning, web apps, dashboards.

## Data
- Run download_data.py; it puts FD001 files in the data/ folder
- Files have no header and are space-separated
- Columns in order: engine id, cycle, 3 operating settings, 21 sensors
- Name the columns: unit, cycle, setting_1..3, sensor_1..21

## Allowed files
One notebook, README.md, history.md, requirements.txt, download_data.py,
LICENSE, .gitignore, and the data folder. No other files.

## Rules for the AI
- Work only on the task given; do not start later milestones
- Keep code short and simple, with a one-line markdown heading per cell
- Never print whole tables; at most 5 rows plus shape and summary
- Read only this file at the start, not the whole notebook
- Do not write interpretation text; I write the conclusions myself
- If something contradicts the dataset readme, stop and tell me
- Ask before installing any library beyond pandas, matplotlib,
  scikit-learn
- The project must run from a clean download using README.md only

## Status
- Done: Milestone 1, data and plots. Notebook loads FD001, checks it,
  builds train RUL, drops the 7 flat sensors, plots 4 engines and the
  fleet trend. Reviewed, all majors fixed, 7 code cells run clean.
- Also done: README.md (marked work in progress), history.md (0.1),
  MIT LICENSE, git repository initialised with no commit yet.
- Findings: base Python 3.14 had Jupyter but no pandas; user site now
  has pandas 3.0.6 / numpy 2.5.3 / matplotlib 3.11.2. Notebook stores
  zero outputs. .venv hides itself via its own .gitignore; data/ and
  .tmp/ still need a project .gitignore (Milestone 1.5).
- Next: user accepts Milestone 1, then Milestone 1.5 file work, then
  Milestone 2 baseline model.