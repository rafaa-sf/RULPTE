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
├── rulpte.ipynb        the notebook: the whole analysis, read top to bottom
├── download_data.py    fetches the NASA files into data/
├── requirements.txt    the three Python libraries the notebook needs
├── LICENSE             MIT, so anyone may reuse this
└── data/               the NASA files (downloaded, not stored in git)
    ├── train_FD001.txt   engines run to failure, so we know the answers
    ├── test_FD001.txt    engines stopped early, the quiz
    ├── RUL_FD001.txt     the correct answers for the quiz
    └── readme.txt        NASA's own description of the files
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
| **Introduction** | What is this notebook about? Written by the author. |
| **Imports and paths** | Which tools are needed, and where are the files? Loads `pandas` (tables), `numpy` (numbers), `matplotlib` (pictures), and points at `data/`. |
| **Load data** | Reads the three text files into tables and names the columns: `unit`, `cycle`, `setting_1..3`, `sensor_1..21`. |
| **Sanity check** | Are these really the files we think? Prints the shapes, the types, and counts empty cells. A wrong file that looks plausible is the most expensive mistake in this field, so the check is loud on purpose. |
| **Train RUL** | Builds the answer key: for each engine, find its last cycle, then RUL = last cycle − this cycle. The final cycle gets 0, a fresh engine gets its whole life. |
| **Sensor variability** | Which sensors are useless? A sensor that never changes cannot tell a healthy engine from a dying one, so anything with 5 or fewer distinct values is dropped. Seven go: `sensor_1, 5, 6, 10, 16, 18, 19`. Fourteen stay. |
| **Degradation by engine** | Do the surviving sensors really drift as an engine ages? Figure 1 shows four engines of different lengths, one panel per strong sensor. |
| **Fleet trend** | Does the drift hold across all 100 engines, not just the four? Figure 2 averages the fleet as RUL counts down. |
| **Model input** | Turns the table into the model's exam paper: one row per cycle, 14 sensors as features, RUL as the target, 20 engines held back for testing. |
| **Conclusions** | What did we learn? Written by the author. |

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

---

## 7. What RMSE means, with a picture in your head

Suppose five engines have 10, 20, 30, 40 and 50 cycles left and the model says
30 for all of them. The mistakes are −20, −10, 0, +10, +20. Square them so
minus signs cannot cancel: 400, 100, 0, 100, 400. Average: 200. Square root:
about 14. So the model is "off by about 14 cycles". That is the number this
project will quote, and it is the same unit NASA uses, so it can be compared
with published results.

---

## 8. How to run it

1. `python -m venv .venv` then `.venv\Scripts\activate`
2. `pip install -r requirements.txt`
3. `python download_data.py`
4. `python -m notebook`, open `rulpte.ipynb`, **Run All**

The full walkthrough, with copy-paste commands and troubleshooting, is in
[README.md](README.md).

---

## 9. The three rules this project keeps

1. **Never let the model see the future.** Features come from a cycle; the
   answer comes from later cycles. Mixing them is leakage, and it is the number
   one way to publish a fake result.
2. **Never split by row when rows belong to the same engine.** Cycles of one
   engine are near-copies. The split is by engine, so the test is a real test.
3. **Always beat the dumb guess.** "Every engine has about 108 cycles left" is
   the yardstick. A model that cannot beat it is not a model, it is decoration.
