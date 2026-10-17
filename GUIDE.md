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
├── requirements.txt    the three Python libraries the notebook needs
├── LICENSE             MIT, so anyone may reuse this
├── figures/            one plot, shown at the top of the README
└── data/               the NASA files (downloaded, not stored in git)
    ├── train_FD001.txt   engines run to failure, so we know the answers
    ├── test_FD001.txt    engines stopped early, the quiz
    ├── RUL_FD001.txt     the correct answers for the quiz
    └── readme.txt        NASA's own description of the files (not fetched by the script)
```

Why the data is not in git: it is 5.5 MB of NASA's work, downloaded in one
command, and storing it twice would only bloat the repository.

---

## 4. The data files, in plain words

**`train_FD001.txt`** — 20631 rows. Each row is one engine at one cycle: its
number, how old it is, three settings, and 21 sensor readings. Every engine here
starts at cycle 1 and ends at its last cycle, which is the cycle it failed on.
That is what lets us build the answer key.

**`test_FD001.txt`** — same layout, 13096 rows, 100 engines. Each engine stops
part-way through its life; the file does not say what happens next.

**`RUL_FD001.txt`** — 100 numbers: for each test engine, how many cycles were
actually left when the recording stopped. This is the answer key for the quiz.

**`readme.txt`** — NASA's notes. Its "26 sensor slots" line trips people up: the
file has 26 columns in total, of which 21 are sensors. Both statements are true.

---

## 5. The notebook, section by section

The notebook is read top to bottom, like a recipe. Each part answers one
question.

| Section | The question it answers |
| --- | --- |
| **Introduction** | What is this notebook about? The question it answers, the data it uses, and what it scores at the end. |
| **Imports and paths** | Which tools are needed, and where are the files? Loads `pandas` (tables), `numpy` (numbers), `matplotlib` (pictures), and points at `data/`. |
| **Load data** | Reads the three text files into tables and names the columns: `unit`, `cycle`, `setting_1..3`, `sensor_1..21`. |
| **Sanity check** | Are these really the files we think? Prints the shapes, the types, and counts empty cells. A wrong file that looks plausible is the most expensive mistake in this field, so the check is loud on purpose. |
| **Train RUL** | Builds the answer key: for each engine, find its last cycle, then RUL = last cycle − this cycle. The final cycle gets 0, a fresh engine gets its whole life. |
| **Sensor variability** | Which sensors are useless? A sensor that never changes cannot tell a healthy engine from a dying one, so anything with 5 or fewer distinct values is dropped. Seven go: `sensor_1, 5, 6, 10, 16, 18, 19`. Fourteen stay. |
| **Degradation by engine** | Do the surviving sensors really drift as an engine ages? Figure 1 shows four engines of different lengths, one panel per strong sensor. |
| **Fleet trend** | Does the drift hold across all 100 engines, not just the four? Figure 2 averages the fleet as RUL counts down. |
| **Model input** | Turns the table into the model's exam paper: one row per cycle, 14 sensors as features, RUL as the target, 20 engines held back for testing. |
| **Baseline model** | Can a straight line through the sensors beat the dumb guess? Fits plain least squares on the 14 sensors of the 80 visible engines and scores it on the 20 hidden ones: 46.3 against 71.0. |
| **Score on the real test set** | How does it do on the official quiz? One prediction per test engine, from its last recorded cycle: 30.2 against 51.8, with the like-for-like 27.9 against 54.1 beside it. |
| **Where the model fails** | Which mistakes does a single number hide? Figure 3 plots guess against truth and error against truth, so the 18.8-cycle optimism is visible. |
| **Conclusions** | What did we learn? Fourteen sensors carry the signal, the baseline beats the average guess, and the model is optimistic by about 19 cycles. |

Nothing is written to disk. The notebook reads the data and draws pictures.

---

## 6. What the two pictures show

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

**Figure 3 — where the model fails.** The same 100 test engines, one point each.
The left panel puts the guess against the truth; the dashed diagonal is perfect
prediction, and most points sit above it, which is the 19-cycle optimism. The
right panel shows only the mistake, with a band at ±RMSE so you can see which
errors are ordinary and which are large.

---

## 7. The model, in plain words

The notebook also fits a model, which is just a formula with dials that get
turned until its guesses line up with engines whose end we already know.

**What it sees.** One row per cycle: the 14 live sensors, and the RUL of that
cycle as the answer to learn. That is the whole input. No engine name, no date,
nothing from the future.

**How we know it is not cheating.** 20 of the 100 engines are hidden before the
first dial is turned, and they stay hidden until the guesses are made. A model
tested on the same engines it learned from is like a student sitting the exam
they already saw — it proves nothing.

**The yardstick.** "Every engine has about 106 cycles left" is the dumbest
possible guess, and it is scored the same way. Our model has to beat it to mean
anything. On the 20 hidden engines the model scores **46.3** cycles of RMSE
against **71.0**, so the sensors do carry real information.

**A fair comparison.** Those two numbers are not the same test. The 46.3 averages
every single cycle of the hidden engines, including young ones with 300 cycles
left; the real quiz has one row per engine, near the end of life. Restrict the
hidden engines to the same life range and the model scores **27.9** against
**54.1**. Compare like with like or the second number flatters the model.

**The real quiz.** The official test set is 100 different engines, each recorded
only up to some point in its life. The model predicts once per engine, from its
last recorded cycle, and the answers are in `RUL_FD001.txt`. Score:
**30.2** cycles, against **51.8** for the average guess.

**What it gets wrong.** The model leans high: on average it says 94.3 cycles
when the truth is 75.5, about 19 cycles too optimistic. The lean is not flat:
it peaks in mid-life, about +40 cycles with roughly 70 left, and shrinks to
about +8 close to failure and +3 early in life. That is why the third figure
shows the error, not just the score. A model you cannot see the mistakes of is
a model you cannot improve.

## 8. What RMSE means, with a picture in your head

Suppose five engines have 10, 20, 30, 40 and 50 cycles left and the model says
30 for all of them. The mistakes are −20, −10, 0, +10, +20. Square them so
minus signs cannot cancel: 400, 100, 0, 100, 400. Average: 200. Square root:
about 14. So the model is "off by about 14 cycles". That is the number this
project will quote, and it is the same unit NASA uses, so it can be compared
with published results.

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
