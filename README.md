# RULPTE — Remaining Useful Life Prediction for Turbofan Engines

A small, readable study of how turbofan engines degrade, using NASA's C-MAPSS
FD001 run-to-failure data: it labels every recorded cycle with its remaining
useful life (RUL) and fits a deliberately simple baseline that predicts how many
cycles an engine has left.

> **Test RMSE 30.2 cycles** on the 100 official test engines, against 51.8 for
> always guessing the fleet average. The caveat travels with the number: 46.3 /
> 71.0 is the held-out figure on all cycles, and 27.9 / 54.1 once those cycles
> are cut to the test's life range.

The baseline is plain least squares on the 14 live sensors, no deep learning, so
the numbers are a floor, not a ceiling.

New to the vocabulary? **[GUIDE.md](GUIDE.md)** explains every term, every file
and every figure in plain words, with no maths.

![Predicted RUL against true RUL for the 100 test engines, and the error against true life with the ±RMSE band](figures/figure-3.png)

*Figure 3 — the 100 official test engines: predictions against the truth, then
the error against true life, with the ±RMSE band and the model's slight
optimism.*

## Quick start (Windows, copy and paste)

```powershell
git clone https://github.com/rafaa-sf/RULPTE.git
cd RULPTE
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt notebook
python download_data.py
python -m notebook
```

Your browser opens a file list. Click **rul_prediction.ipynb**, then menu
**Kernel → Restart Kernel and Run All Cells**. The three figures appear under
their cells. `Ctrl+C` twice in the terminal stops the server.

The sections below explain each step of that block, for Windows, macOS and
Linux.

## What you get

- A notebook that loads the data, checks it, plots it and scores a baseline
  model, top to bottom in a few seconds.
- Three figures: four engines followed from first flight to failure, the
  fleet-wide trend as RUL counts down, and the test-engine errors shown at the
  top of this page.
- No deep learning, no web app, no dashboard, and no editor required beyond a
  browser. Just the data and what it says.

## Results

All figures are RMSE in cycles. Lower is better.

| What is scored | Model | Always guessing the average |
| --- | --- | --- |
| 20 held-out engines, every cycle | 46.3 | 71.0 |
| Same held-out engines, only cycles in the test's life range | 27.9 | 54.1 |
| Official test: one prediction per engine at its last recorded cycle | 30.2 | 51.8 |

Only the last row is the official score. The other two are the honest checks
around it: the first includes young engines with 300 cycles left, the second is
scored the way the test set is scored.

## What you need

- Python 3.12 or newer (developed on 3.14; the pinned numpy 2.5.4 needs 3.12)
- Git, to clone the repository
- A notebook viewer: **Jupyter Notebook**, installed in step 3. No VS Code, no
  PyCharm, no account.
- About 6 MB of disk for the dataset once unpacked (the download itself is a
  ~15 MB archive that is deleted afterwards), and it is not committed

## 1. Get the code

```bash
git clone https://github.com/rafaa-sf/RULPTE.git
cd RULPTE
```

## 2. Create a virtual environment

Windows (PowerShell or cmd):

```powershell
python -m venv .venv
.venv\Scripts\activate
```

macOS / Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Your prompt should now start with `(.venv)`. Every command below runs inside
that environment — including the notebook, which is why the figures and the
data libraries are guaranteed to be the same install.

If `python` is not recognised on Windows, use `py -3` instead of `python` in
both lines.

## 3. Install what the notebook needs

```powershell
pip install -r requirements.txt
pip install notebook
```

The first line installs the three libraries the notebook imports — pandas,
numpy and matplotlib — pinned to the versions it was verified with. The second
installs Jupyter Notebook, the browser-based viewer that runs the cells. It is
not pinned: any current version works.

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
`train_FD001.txt`, `test_FD001.txt` and `RUL_FD001.txt` into
`data/`.

## 5. Open the notebook and run all cells

Start the viewer from the project folder, with the environment still active:

```powershell
python -m notebook
```

Your browser opens at `http://localhost:8888/tree`. If it does not open by
itself, copy the full URL the terminal printed — it ends in `?token=...` — and
paste it into the browser. Keep that terminal window open: closing it stops
the server.

Then:

1. Click **rul_prediction.ipynb** in the file list.
2. Check the kernel name at the top right: it must be the one from your
   environment (it normally reads *Python 3 (ipykernel)*). If the notebook
   cannot import pandas later, this is the first thing to check.
3. Menu **Kernel → Restart Kernel and Run All Cells**.
4. Cell by cell instead: click a cell and press **Shift+Enter**.

Two ways to stop: `Ctrl+C` twice in the terminal, or close the browser tab and
stop the process.

`python -m notebook` works even when the `jupyter` command is not on your PATH,
which is the usual reason `jupyter notebook` fails on Windows.

The notebook reads `data/`, so run step 4 first. Everything after that is
read-only: it creates no files.

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
- The model: every cycle is one row, the 14 live sensors are the features, RUL
  is the target, and 20 of the 100 engines are held back and never seen while
  fitting. The three scores are in the results table above.
- Figure 3: the model leans about 19 cycles high, and it leans high at every
  age, worst with 40-80 cycles left.
- Nothing is written to disk. The notebook only reads the data and draws.

## Reading it without the code

A notebook shows its code, but you do not have to look at it.

**Hide the code in place.** In JupyterLab open menu **View → Collapse All Code**
(command palette: *Collapse All Code*). Every code cell folds down to its
output, so what is left on screen is the written explanations, the printed
numbers and the three figures. The cells still run: **Run → Run All Cells** or
**Kernel → Restart Kernel and Run All Cells** executes everything and the
figures reappear below the folded cells. **View → Expand All Code** brings the
code back.

**Or export a read-only page.** After running all cells once, this writes
`rul_prediction.html` with the text and the figures and no code at all:

```powershell
pip install nbconvert
python -m nbconvert --to html --no-input rul_prediction.ipynb
```

Open the file with a double click. It needs no server, no kernel and no
libraries, so it is also the version to send to someone who just wants to read
it. It is a snapshot: re-export after any change, and keep it out of git.

### Prefer an editor?

VS Code: install the *Jupyter* extension, open `rul_prediction.ipynb`, pick the
interpreter inside `.venv`, and press *Run All*. The steps above are the same
without any editor.

## Project layout

```
rul_prediction.ipynb      the notebook: load, check, label, plot, fit, score
download_data.py  fetches the NASA archive into data/
requirements.txt  pinned dependencies
GUIDE.md          plain-words explanation of every term, file and figure
LICENSE           MIT
figures/figure-3.png  the test-engine plot shown at the top of this page
data/             downloaded data (git ignored)
history.md        version history, newest first
```

## Troubleshooting

**`No module named notebook`** — the viewer is not installed in the
environment you are running from. Run `pip install notebook` with the same
`python` you used to start it. To be certain, start it as
`python -m notebook` and check `python -c "import sys; print(sys.executable)"`.

**`jupyter` is not recognised, or `jupyter notebook` opens nothing** — use
`python -m notebook` instead. The `jupyter` shortcut is often missing on
Windows while the module is present.

**`ModuleNotFoundError: No module named 'pandas'`** — the notebook is running
on an interpreter that is not your virtual environment. In the notebook run
`import sys; print(sys.executable)`; the path must end in `.venv`. Pick that
kernel, or `pip install pandas numpy matplotlib` in the active environment.

**The browser does not open** — copy the URL with the token from the terminal
into the browser by hand. If the port is taken, run
`python -m notebook --port 8889`.

**`python download_data.py` fails with a network error** — the NASA mirror was
unreachable. Retry, or use the manual download steps it prints.

**`Error: not found in the zip`** — a partial or wrong archive was downloaded.
Delete `data/` and run `python download_data.py --force`.

**The figures do not appear** — run the cells inside the notebook, not from a
plain `python` script, and do not add `matplotlib.use("Agg")`. Restart the
kernel and run all cells again.

**A matplotlib cache permission error** — point the cache somewhere writable
before starting the notebook:
`$env:MPLCONFIGDIR="$env:TEMP\mplcache"` (PowerShell) or
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
