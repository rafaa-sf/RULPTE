# Everything explained, in plain words

No maths background needed. Every word you meet in this project is explained
below, in the order you will meet it.

---

## 1. The one-sentence version

A jet engine has little measuring sticks inside it. NASA wrote down what those
sticks said, second by second, until each engine broke. This project reads
those notes and learns to guess **how many flights an engine has left**.

That guess has a name: **RUL**, short for *Remaining Useful Life*.

---

## 2. The words, one line each

| Word | What it means here |
| --- | --- |
| **Turbofan engine** | The big fan engine under an aeroplane wing. The NASA data comes from a simulation of one. |
| **Sensor** | A small gauge that reports one number: how hot, how fast, how much pressure. This engine has 21 of them that matter. |
| **Cycle** | One run of the engine, start to stop. Think of it as one flight. |
| **Run-to-failure** | The engine was not stopped early. It was run until it broke, so we know exactly when the end came. |
| **Unit** | One engine, with a number. `unit 7` is the seventh engine. This data has 100 of them. |
| **RUL** | Remaining Useful Life. How many cycles are left before this engine breaks. 0 means "it breaks now". |
| **Feature** | Something we measure and give to the model, for example the value of sensor 11 at this cycle. |
| **Model** | A formula that turns features into a guess. It is fitted to data, not written by hand. |
| **Training** | Letting the model look at engines whose end we know, so it can learn. |
| **Holdout** | Engines we hide from training, then test the model on. Like an exam with questions the student never saw. |
| **Baseline** | The simplest honest guess, used as a yardstick. If a real model cannot beat the baseline, it is worthless. |
| **RMSE** | Root Mean Squared Error. The typical size of a mistake, in cycles. RMSE 20 means "off by about 20 flights". Lower is better. |
| **Leakage** | Cheating by accident: letting the model see the answer, or the future. It makes results look great and be wrong. |

---

## 3. Where everything lives

```
RULPTE/
├── README.md           how to install and run, step by step
├── GUIDE.md            this file: what everything does and why
├── history.md          what changed in each version
├── rul_prediction.ipynb        the notebook: the whole analysis, read top to bottom
├── download_data.py    fetches the NASA files into data/
├── requirements.txt    the pinned Python libraries the notebook needs
├── LICENSE             MIT, so anyone may reuse this
├── figures/            one plot, shown at the top of the README
└── data/               the NASA files (downloaded, not stored in git)
    ├── train_FD00*.txt   engines run to failure, so we know the answers
    ├── test_FD00*.txt    engines stopped early, the quiz
    ├── RUL_FD00*.txt     the correct answers for each quiz
    └── readme.txt        NASA's own description of the files (not fetched by the script)
```

Why the data is not in git: it is 5.5 MB of NASA's work, downloaded in one
command, and storing it twice would only bloat the repository.

---

## 4. The data files, in plain words

**`train_FD001.txt`** — 20631 rows, 100 engines, one operating condition. Each row
is one engine at one cycle: its number, how old it is, three settings, and 21
sensor readings. Every engine starts at cycle 1 and ends at its last cycle, which
is the cycle it failed on. That is what lets us build the answer key.

**`test_FD001.txt`** — same layout, 13096 rows, 100 engines. Each engine stops
part-way through its life; the file does not say what happens next.

**`RUL_FD001.txt`** — 100 numbers: for each test engine, how many cycles were
actually left when the recording stopped. This is the answer key for the quiz.

**FD002, FD003, FD004** — the same three files for the other subsets. FD003 is
FD001 with a second fault mode; FD002 and FD004 have six operating conditions, so
the settings columns stop being constant and the sensor readings move with the
conditions. FD002 has 260 training engines and 259 test engines; FD004 has 249
and 248. The notebook scores FD001 and FD002: the easy textbook case and the hard
one.

**`readme.txt`** — NASA's notes. Its "26 sensor slots" line trips people up: the
file has 26 columns in total, of which 21 are sensors. Both statements are true.

---

## 5. The notebook, section by section

The notebook is read top to bottom, like a recipe. Each part answers one
question.

| Section | The question it answers |
| --- | --- |
| **Sensor guide** | What is each of the 21 sensors measuring, in what unit, and does FD001 keep it? The table at the top of the notebook, taken from the paper that introduced the dataset. |
| **Introduction** | What is this notebook about? The question it answers, the data it uses, and what it scores at the end. |
| **Imports and paths** | Which tools are needed, and where are the files? Loads `pandas` (tables), `numpy` (numbers), `matplotlib` (pictures), and points at `data/`. |
| **Load data** | Reads the three text files into tables and names the columns: `unit`, `cycle`, `setting_1..3`, `sensor_1..21`. |
| **Sanity check** | Are these really the files we think? Prints the shapes, the types, and counts empty cells. A wrong file that looks plausible is the most expensive mistake in this field, so the check is loud on purpose. |
| **Train RUL** | Builds the answer key: for each engine, find its last cycle, then RUL = last cycle − this cycle. The final cycle gets 0, a fresh engine gets its whole life. |
| **Sensor variability** | Which sensors are useless? A sensor that never changes cannot tell a healthy engine from a dying one, so anything with 5 or fewer distinct values is dropped. Seven go: `sensor_1, 5, 6, 10, 16, 18, 19`. Fourteen stay. |
| **Degradation by engine** | Do the surviving sensors really drift as an engine ages? Figure 1 shows four engines of different lengths, one panel per strong sensor. |
| **Fleet trend** | Does the drift hold across all 100 engines, not just the four? Figure 2 averages the fleet as the remaining flights count down. |
| **Model input** | Turns the table into the model's exam paper: one row per cycle, 14 sensors as features, RUL as the target, 20 engines held back for testing. |
| **Baseline model** | Can a straight line through the sensors beat the dumb guess? Turns the 14 sensors into 42 numbers, fits them on the visible engines of both subsets, and scores the hidden fifth: FD001 44.8 against 71.0, FD002 41.0 against 69.8. |
| **Score on the real test set** | How does it do on the official quiz? One prediction per test engine, from its last recorded cycle: FD001 28.3 against 51.8, FD002 33.5 against 59.8, with the like-for-like numbers beside them. |
| **How sure is it?** | How wide is the band around a prediction? A nominal 80% interval, sized on held-out engines cut at an arbitrary cycle: ±45.9 cycles on FD001, ±49.8 on FD002, covering 85% and 84% of the real answers. |
| **Where the model fails** | Which mistakes does a single number hide? Figure 3 plots guess against truth and error against truth, so the mid-life optimism is visible. |
| **How stable is that number?** | Is the score one lucky draw? Five folds, five repeats, a fresh random cut each time: 41.5 ± 2.2 cycles on FD001, 41.0 ± 2.4 on FD002, and the error split by how much life is left. |
| **What to do with the number** | A life estimate is only useful if it changes what someone does: the pessimistic end of the interval becomes GROUND, INSPECT, PLAN or MONITOR, and the 259 FD002 test engines are counted into those bands. |
| **Conclusions** | What did we learn? Fourteen sensors carry the signal, the baseline beats the average guess on both subsets, and it is optimistic by about 11 cycles. |

Nothing is written to disk. The notebook reads the data and draws pictures.

---

## 6. What the three pictures show

**Figure 1 — one engine's life, four sensors.** Each panel is one sensor. The
faint scribble is the raw record, which is noisy, like a heart-rate trace. The
bold line is a 15-cycle rolling mean: each point is the average of the 15 cycles
around it, which smooths the noise away and leaves the direction. The grey line
is the average of all engines still running. Because the four engines are
different ages, each trace is tagged with its name and length, e.g. `e69`, 362
cycles. Two sensors climb as the engine dies, two fall — both are informative,
which is why the colour marks the sensor and the dash pattern marks the engine.

**Figure 2 — the whole fleet at once.** Running life is on the x-axis, reversed,
so "now" is on the right and failure is at 0 on the far right. Each point is the
average of a 10-cycle slice of RUL, and the shaded band is the middle half of
the engines (the interquartile range): narrow band, engines agree; wide band,
they disagree. The plot stops at RUL 240 because past that point fewer than 20
engines are still alive, so an "average" would be a rumour, not a measurement.
The panel says so rather than hiding it.

**Figure 3 — where the model fails.** FD002's 259 test engines, one point each.
The left panel puts the guess against the truth; the dashed diagonal is perfect
prediction, and most points sit above it, which is the model's optimism. The
right panel shows only the mistake, with a band at ±RMSE so you can see which
errors are ordinary and which are large — and the orange line marks how far the
whole cloud sits above zero, and where that is worst.

---

## 7. The model, in plain words

The notebook also fits a model, which is just a formula with dials that get
turned until its guesses line up with engines whose end we already know.

**What it sees.** One row per cycle: the 14 live sensors turned into 42 numbers
— the reading now, its average over the last 20 cycles, and how much it moved
across those 20 cycles — plus the RUL of that cycle as the answer to learn.
Nothing else: no engine name, no date, nothing from the future.

**A hard extra rule.** Engines in FD002 and FD004 fly in six different operating
conditions and the sensors read differently in each, so a raw 550 that means
"fine on a hot day" can mean "worn out on a cold one". Each sensor is therefore
rescaled inside its own condition before the model ever sees it.

**How we know it is not cheating.** One engine in five is hidden before the first
dial is turned, and it stays hidden until the guesses are made. A model tested on
the engines it learned from is like a student sitting the exam they already saw —
it proves nothing.

**The yardstick.** "Every engine has about the fleet average left" is the dumbest
possible guess and is scored the same way. Our model has to beat it to mean
anything. On the hidden engines it scores **44.8** on FD001 (average guess 71.0)
and **41.0** on FD002 (69.8), so the sensors do carry real information.

**A fair comparison.** Those numbers average every cycle of the hidden engines,
young ones with 300 cycles left included; the real quiz has one row per engine,
near the end of life. Restricted to the quiz's life range: **27.6** against 54.1
on FD001, **32.6** against 56.5 on FD002. Compare like with like.

**The real quiz.** The official test sets are engines we never used, each recorded
only up to some point in its life. The model predicts once per engine from its
last recorded cycle: **28.3** against 51.8 on FD001's 100 engines, and **33.5**
against 59.8 on FD002's 259. FD002 is the headline because it is harder: six
conditions and 260 training engines.

**Why the sensors are expanded at all.** The plain 14 readings are the simpler
model, so the extra 28 numbers have to pay for themselves. The choice was not made
on the quiz — that would be marking your own homework. It was made on a harder
test: cut every hidden engine at a random point in its life, exactly as the quiz
does, and score that. There the 42 numbers win by about one cycle, **38.6 against
39.6** on FD001 and **39.4 against 39.9** on FD002 — a small, honest gain, inside
the spread. The quiz is a single draw of engines; the random-cut test never
touches it.

**How sure is it?** A single number hides how much to trust it, so each prediction
carries a band: a nominal 80% interval, ±45.9 cycles on FD001 and ±49.8 on FD002,
sized from engines cut at an arbitrary cycle rather than from the answers.
Measured on the real answers it covers 85% on FD001 and 84% on FD002 — wider than promised, which is
the safe direction, because the model's mistakes are lopsided rather than spread
evenly. The width rests on 20 engines and 25 draws, so it is coarse by a few
cycles.

**How stable is it?** The 35-ish number is one draw of engines, so the notebook
repeats the whole exercise five times with different engines held back and
different cut points: 41.5 ± 2.2 on FD001, 41.0 ± 2.4 on FD002. The official quiz
beats both, because it scores each engine once at its last cycle instead of across
its whole life. Two models whose scores differ by a cycle or two are not
different; the band around the number is as real as the number.

**What the number is for.** A life estimate only earns its keep if it changes
what someone does next, so the last section reads the pessimistic end of the
interval and turns it into an action: 5 cycles or fewer means ground the engine,
up to 20 inspect it before the next flight, up to 60 book the maintenance
window, more than that and there is nothing to do yet. On FD002's 259 test
engines that grounds 66, inspects 16, plans 60 and monitors the remaining 117.
`predict.py` applies the same four bands to any engine file you point it at, and
`python run.py --test` checks that the tool and the notebook still agree.


**Is it any good?** Against published work, no, not yet: deep sequence models
read the whole history and report about 12 cycles of error on FD001 against this
model's 28.3. That is the point of calling this a floor - it is the number any
cleverer model has to beat, produced by a formula you can read in ten lines.

**What it gets wrong.** On FD002 the model says 92.1 when the truth is 81.2 —
about 11 cycles too optimistic (about 18 on FD001). The lean is not flat: it is
nearly zero for a dying engine, peaks near +30 with 40 to 80 cycles left, and
turns negative beyond about 140, reaching −56 for the longest-lived engines. That
is why the third figure shows the error, not just the score. A model you cannot
see the mistakes of is a model you cannot improve.

---

## 9. How to run it

One command does everything — creates the environment, installs the libraries,
downloads the data, opens the notebook:

    python run.py

If you prefer to see each move, the same four steps by hand:

1. `python -m venv .venv` then `.venv\Scripts\activate`
2. `pip install -r requirements.txt notebook`
3. `python download_data.py`
4. `python -m notebook`, open `rul_prediction.ipynb`, **Run All**

`python run.py --check` runs the notebook without opening it and prints the two
RMSEs, which is how the project proves itself on a clean machine every time a
change is pushed.

The full walkthrough, with copy-paste commands and troubleshooting, is in
[README.md](README.md).

---

## 10. The three rules this project keeps

1. **Never let the model see the future.** Features come from a cycle; the
   answer comes from later cycles. Mixing them is leakage, and it is the number
   one way to publish a fake result.
2. **Never split by row when rows belong to the same engine.** Cycles of one
   engine are near-copies. The split is by engine, so the test is a real test.
3. **Always beat the dumb guess.** "Every engine has about 106 cycles left" is
   the yardstick. A model that cannot beat it is not a model, it is decoration.
