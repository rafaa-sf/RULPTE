# RULPTE — Remaining Useful Life Prediction for Turbofan Engines

A small, readable study of how turbofan engines degrade, using NASA's C-MAPSS
FD001 run-to-failure data. The notebook loads the raw sensor records, labels
each one with its remaining useful life (RUL), drops the sensors that never
move, and plots the degradation signal that a predictive model would learn
from.

This is the data-and-plots milestone. A baseline RUL model comes next.

> **Status: work in progress.** The notebook is finished, but two steps below
> are not ready yet: `requirements.txt` (step 3) and the notebook's first
> cell that repeats the download (step 5). Both land in the next milestone.
> Until then, install `pandas`, `numpy` and `matplotlib` by hand and skip the
> notebook's first cell.

## What you get

- A notebook that loads the data, checks it, and plots it, top to bottom in
  about two seconds (measured: 1.7 s for all seven code cells).
- Two figures: four engines followed from first flight to failure, and the
  fleet-wide trend as RUL counts down.
- No deep learning, no web app, no dashboard. Just the data and what it says.

## What you need

- Python 3.11 or newer (developed on 3.14)
- Git, to clone the repository
- About 15 MB of disk for the dataset, which is downloaded, not committed

## 1. Get the code

```bash
git clone https://github.com/rafaa-sf/RULPTE.git
cd RULPTE
```

## 2. Create a virtual environment

Windows (PowerShell or cmd):

```bash
python -m venv .venv
.venv\Scripts\activate
```

macOS / Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Your prompt should now start with `(.venv)`. Every command below runs inside
that environment.

## 3. Install the requirements

```bash
pip install -r requirements.txt
```

Three libraries: pandas, numpy and matplotlib, pinned to the versions the
notebook was verified with.

## 4. Download the data

```bash
python download_data.py
```

It fetches the NASA archive once, keeps only the FD001 files, deletes the
zip, and prints a sanity check. You should see:

```
  train_FD001.txt: 20631 rows, 100 engines -> OK
  test_FD001.txt: 13096 rows, 100 engines -> OK
  RUL_FD001.txt: 100 rows -> OK
```

The files land in `data/`, which git ignores. Use `python download_data.py --force`
to download again.

If the download is blocked (locked-down network, proxy), the script prints
manual instructions: open the NASA Prognostics Data Repository, download the
*Turbofan Engine Degradation Simulation Data Set* zip, unzip it, and copy
`train_FD001.txt`, `test_FD001.txt`, `RUL_FD001.txt` and `readme.txt` into
`data/`.

## 5. Open the notebook and run all cells

```bash
jupyter lab rulpte.ipynb
```

(Or `jupyter notebook rulpte.ipynb`, or open the file in VS Code.)

Make sure the notebook is using the environment from step 2 — the interpreter
whose path ends in `.venv`. Then **Kernel → Restart Kernel and Run All Cells**.

The notebook's first cell repeats the data-download step, in case you opened
the notebook before running step 4.

## What to expect

- Train data: 20631 rows, 100 engines, 26 columns — unit, cycle, three
  operating settings, 21 sensor channels. Test data: 13096 rows, same columns
  for 100 engines. `RUL_FD001.txt` holds the 100 true end-of-life values.
- Seven of the 21 sensors never move (or move in only two values), so the
  notebook drops them and keeps 14.
- Figure 1: four engines, 128 to 362 cycles long, rising and falling sensors.
  Each panel shows the raw signal faintly and a 15-cycle rolling mean in bold,
  so the trend clears the noise.
- Figure 2: the same sensors averaged over the fleet as RUL counts down, in
  2×2 panels. The band is the interquartile range across engines. The plot
  stops at RUL 240 because fewer than 20 engines are still running beyond that,
  and the panel says so.
- Nothing is written to disk. The notebook only reads the data and draws.

## Project layout

```
rulpte.ipynb      the notebook: load, check, label, plot
download_data.py  fetches the NASA archive into data/
requirements.txt  pinned dependencies
data/             downloaded data (git ignored)
history.md        version history, newest first
```

## Troubleshooting

**`ModuleNotFoundError: No module named 'pandas'`** — the notebook is running
on an interpreter that is not your virtual environment. Check with
`import sys; print(sys.executable)`; the path must end in `.venv`. Pick that
kernel, or `pip install -r requirements.txt` in the active environment.

**`python download_data.py` fails with a network error** — the NASA mirror was
unreachable. Retry, or use the manual download steps it prints.

**`Error: not found in the zip`** — a partial or wrong archive was downloaded.
Delete `data/` and run `python download_data.py --force`.

**The figures do not appear** — run the cells inside Jupyter, not from a plain
`python` script, and do not add `matplotlib.use("Agg")`. Restart the kernel and
run all cells again.

**A matplotlib cache permission error** — point the cache somewhere writable
before starting Jupyter:
`set MPLCONFIGDIR=%TEMP%\mplcache` (Windows) or
`export MPLCONFIGDIR=/tmp/mplcache` (macOS/Linux).

**`Permission denied` when writing `data/`** — the project is in a protected
folder. Move it somewhere under your home directory.

## Data credit

The data is NASA's C-MAPSS Turbofan Engine Degradation Simulation Data Set,
from the NASA Prognostics Center of Excellence at Ames Research Center.
Please cite it as:

> A. Saxena, K. Goebel (2008). *Turbofan Engine Degradation Simulation Data
> Set*, NASA Prognostics Data Repository, NASA Ames Research Center, Moffett
> Field, CA.

Only the FD001 subset is used here: one operating condition, one fault mode.
The data is downloaded at run time and is not redistributed in this
repository.

## History

See [history.md](history.md) for what changed in each version.
