"""Drift guards: predict.py must keep reproducing the notebook and survive its own npz."""

import json
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import predict  # noqa: E402  (needs the path line above)

ACTIONS = ("GROUND", "INSPECT", "PLAN", "MONITOR")
BANDS = (5, 20, 60)  # predict.action's thresholds, in order
LINE = re.compile(r"^engine (\d+)\s+RUL (\d+)\s+p10 (\d+)\s+p90 (\d+)\s+(\w+)$")


def printed(text):
    """predict() stdout as (engine, rul, p10, p90, action); anything else is a failure."""
    lines = text.strip().splitlines()
    hits = [LINE.match(line) for line in lines]
    assert lines and all(hits), f"unparsed output: {text!r}"
    return [(int(u), int(r), int(lo), int(hi), a) for u, r, lo, hi, a in (hit.groups() for hit in hits)]


@pytest.fixture
def tmp_path():
    """pytest makes tmp_path dirs mode 0700, which this Windows sandbox cannot reopen;
    the default permissions keep the write below allowed. Cleaned up afterwards."""
    base = Path(tempfile.gettempdir()) / f"rulpte-test-{os.urandom(4).hex()}"
    base.mkdir()
    yield base
    shutil.rmtree(base, ignore_errors=True)


@pytest.fixture(scope="module")
def fd001():
    return predict.fit("FD001")


@pytest.fixture(scope="module")
def fd002():
    return predict.fit("FD002")


def test_fd001_reproduces_notebook(fd001):
    assert fd001["rmse"] == pytest.approx(28.3, abs=0.2)
    assert fd001["coverage"] == pytest.approx(0.85, abs=0.02)


def test_fd002_reproduces_notebook(fd002):
    """The six-condition subset is where the tool and the notebook drift apart unseen."""
    assert fd002["rmse"] == pytest.approx(33.5, abs=0.2)
    assert fd002["half"] == pytest.approx(49.8, abs=0.3)
    assert fd002["coverage"] == pytest.approx(0.84, abs=0.02)


def test_npz_round_trip_matches_memory(fd001, tmp_path, capsys, monkeypatch):
    """The saved model, loaded the way predict() loads it, must agree engine for engine."""
    path = predict.DATA / "test_FD001.txt"
    units, rul = predict.forecast(predict.read_frame(path), fd001)
    memory = {int(u): int(v) for u, v in zip(units, rul)}

    npz = tmp_path / "model.npz"
    np.savez_compressed(npz, **{f"FD001_{k}": v for k, v in fd001.items()})
    monkeypatch.setattr(predict, "MODEL", npz)  # no write into the project
    predict.predict("FD001", path)

    rows = printed(capsys.readouterr().out)
    assert len(rows) == len(memory)
    assert {u: r for u, r, *_ in rows} == memory  # condition mapping and maths survive the disk trip
    assert {a for *_, a in rows} <= set(ACTIONS)


def test_predict_covers_every_fd002_engine(capsys):
    if not predict.MODEL.is_file() or "FD002_coef" not in np.load(predict.MODEL).files:
        pytest.fail("model.npz lacks FD002: run `python predict.py train` first")
    path = predict.DATA / "test_FD002.txt"
    predict.predict("FD002", path)

    rows = printed(capsys.readouterr().out)
    assert len(rows) == predict.read_frame(path)["unit"].nunique()  # one line per engine, no cap
    assert {a for *_, a in rows} <= set(ACTIONS)


def test_action_bands_come_from_the_thresholds():
    for probe in [-1.0] + [b + d for b in BANDS for d in (-0.5, 0.15)]:
        expected = ACTIONS[sum(probe > b for b in BANDS)]  # one band up per threshold crossed
        assert predict.action(probe) == expected

def test_notebook_code_cells_compile():
    """A markdown cell saved as code stops Run All; this catches it before a push."""
    notebook = Path(__file__).resolve().parents[1] / "rul_prediction.ipynb"
    cells = json.loads(notebook.read_text(encoding="utf-8"))["cells"]
    for index, cell in enumerate(cells):
        if cell["cell_type"] != "code":
            continue
        source = "".join(cell["source"])
        try:
            compile(source, f"cell {index}", "exec")
        except SyntaxError as error:
            raise AssertionError(
                f"notebook cell {index} is code but does not compile: "
                f"line {error.lineno}: {error.msg}"
            ) from error
