"""Checks that predict.py reproduces the notebook's published numbers."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import predict  # noqa: E402  (needs the path line above)


@pytest.fixture(scope="module")
def fd001():
    return predict.fit("FD001")


@pytest.fixture(scope="module")
def fd002():
    return predict.fit("FD002")


def test_feature_matrix_has_42_columns():
    frame = predict.load_subset("FD001")[0]
    assert predict.features(frame).shape == (len(frame), 42)


def test_fd001_score_matches_notebook(fd001):
    assert fd001["rmse"] == pytest.approx(35.6, abs=0.2)


def test_fd002_score_matches_notebook(fd002):
    assert fd002["rmse"] == pytest.approx(35.0, abs=0.2)


@pytest.mark.parametrize("p10, expected",
                         [(3, "GROUND"), (12, "INSPECT"), (40, "PLAN"), (90, "MONITOR")])
def test_action_policy(p10, expected):
    assert predict.action(p10) == expected
