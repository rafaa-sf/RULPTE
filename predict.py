#!/usr/bin/env python3
"""C-MAPSS remaining-useful-life CLI: train, predict, score."""

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans

ROOT = Path(__file__).resolve().parent
DATA, MODEL = ROOT / "data", ROOT / "model.npz"
COLS = ["unit", "cycle"] + [f"setting_{i}" for i in range(1, 4)] + [f"sensor_{i}" for i in range(1, 22)]
SETTINGS, SENSORS = COLS[2:5], COLS[5:]
KEEP = ["sensor_2", "sensor_3", "sensor_4", "sensor_7", "sensor_8", "sensor_9", "sensor_11", "sensor_12",
        "sensor_13", "sensor_14", "sensor_15", "sensor_17", "sensor_20", "sensor_21"]
CONDITIONS = {"FD001": 1, "FD002": 6, "FD003": 1, "FD004": 6}
WIN, FLAT = 20, 1e-9
FEATURES = [f"{s}{suffix}" for s in KEEP for suffix in ("", f"_avg{WIN}", f"_d{WIN}")]

def action(p10):
    """Demonstration policy, not airworthiness guidance: the lower bound decides the response."""
    return "GROUND" if p10 <= 5 else "INSPECT" if p10 <= 20 else "PLAN" if p10 <= 60 else "MONITOR"

def read_frame(path):
    path = Path(path)
    if not path.is_file():
        sys.exit(f"no such file: {path}")
    return pd.read_csv(path, sep=r"\s+", header=None, names=COLS)

def load_subset(name):
    """Train/test frames z-scored inside their operating condition, plus the condition stats."""
    if name not in CONDITIONS:
        sys.exit(f"unknown subset {name}; choose from {', '.join(CONDITIONS)}")
    train, test = read_frame(DATA / f"train_{name}.txt"), read_frame(DATA / f"test_{name}.txt")
    rul = pd.read_csv(DATA / f"RUL_{name}.txt", header=None, names=["RUL"]).squeeze()

    km = KMeans(n_clusters=CONDITIONS[name], n_init=10, random_state=0).fit(train[SETTINGS].to_numpy(float))
    train["condition"], test["condition"] = km.labels_, km.predict(test[SETTINGS].to_numpy(float))
    mean = train.groupby("condition")[SENSORS].mean()
    std = train.groupby("condition")[SENSORS].std().mask(lambda s: s <= FLAT, 1.0)
    for frame in (train, test):  # train statistics only; labels 0..k-1 row them onto every reading
        labels = frame["condition"].to_numpy()
        frame[SENSORS] = (frame[SENSORS].to_numpy(float) - mean.to_numpy()[labels]) / std.to_numpy()[labels]

    train["RUL"] = train.groupby("unit")["cycle"].transform("max") - train["cycle"]
    return train, test, rul, {"centre": km.cluster_centers_, "cond_mean": mean.to_numpy(),
                              "cond_std": std.to_numpy()}

def features(frame):
    """Per engine, sorted by cycle: value, 20-cycle centred mean, 20-cycle change."""
    d = frame.sort_values(["unit", "cycle"])
    by = d.groupby("unit")[KEEP]
    avg = by.transform(lambda s: s.rolling(WIN, center=True, min_periods=1).mean())
    # early rows have no t-WIN reading, so they use the engine's first one: no NaN, no dropped rows
    change = d[KEEP] - by.shift(WIN).fillna(by.transform("first"))
    out = pd.concat([d[KEEP], avg.add_suffix(f"_avg{WIN}"), change.add_suffix(f"_d{WIN}")], axis=1)
    return out.loc[frame.index]  # caller's row order: masks keep lining up

def fit(name):
    """Least squares on four of five engines; the fifth supplies the 80% half-width."""
    frame, test, rul, norm = load_subset(name)
    X, y = features(frame).to_numpy(float), frame["RUL"].to_numpy(float)
    held_units = np.sort(frame["unit"].unique())[::5]
    held = frame["unit"].isin(held_units).to_numpy()
    mean, std = X[~held].mean(axis=0), X[~held].std(axis=0)
    A = np.column_stack([np.ones(len(X)), (X - mean) / std])
    coef = np.linalg.lstsq(A[~held], y[~held], rcond=None)[0]

    F = pd.DataFrame(X, columns=FEATURES).assign(unit=frame["unit"].to_numpy(), RUL=y)
    rng, error = np.random.default_rng(0), []
    for _ in range(25):  # 25 random cuts, one per held-out engine, the notebook's seed
        engines = [F[F["unit"] == u] for u in held_units]
        cut = pd.DataFrame([r.iloc[rng.integers(5, len(r))] for r in engines])
        B = np.column_stack([np.ones(len(cut)), (cut[FEATURES].to_numpy(float) - mean) / std])
        error += list(np.abs(np.clip(B @ coef, 0, None) - cut["RUL"].to_numpy(float)))
    half = float(np.quantile(error, 0.8))

    rows = test.groupby("unit")["cycle"].idxmax()  # last recorded cycle per engine
    truth = pd.Series(rul.to_numpy(float), index=range(1, len(rul) + 1)).loc[test.loc[rows, "unit"]].to_numpy(float)
    B = np.column_stack([np.ones(len(rows)), (features(test).loc[rows].to_numpy(float) - mean) / std])
    pred = np.clip(B @ coef, 0, None)
    return {"coef": coef, "mean": mean, "std": std, "half": half, "mean_y": float(y[~held].mean()),
            "rmse": float(np.sqrt(np.mean((pred - truth) ** 2))),
            "coverage": float(np.mean(np.abs(pred - truth) <= half)), "engines": frame.unit.nunique(), **norm}

def train():
    arrays = {}
    for name in ("FD001", "FD002"):
        model = fit(name)
        arrays.update({f"{name}_{key}": value for key, value in model.items()})
        print(f"trained {name}: 42 features, {model['engines']} engines, interval ±{model['half']:.1f} cycles")
    np.savez_compressed(MODEL, **arrays)

def predict(subset, path):
    if not MODEL.is_file():
        sys.exit(f"{MODEL.name} not found; run: python predict.py train")
    model = np.load(MODEL)
    if f"{subset}_coef" not in model:
        sys.exit(f"{subset} is not in {MODEL.name}; train it first")

    frame = read_frame(path)
    centres = model[f"{subset}_centre"]
    labels = np.argmin(((frame[SETTINGS].to_numpy(float)[:, None, :] - centres) ** 2).sum(axis=2), axis=1)
    frame[SENSORS] = ((frame[SENSORS].to_numpy(float) - model[f"{subset}_cond_mean"][labels]) /
                      model[f"{subset}_cond_std"][labels])  # same condition z-score as training

    rows = frame.groupby("unit")["cycle"].idxmax()
    X = features(frame).loc[rows].to_numpy(float)
    half = float(model[f"{subset}_half"])
    rul = np.clip(np.column_stack([np.ones(len(X)), (X - model[f"{subset}_mean"]) / model[f"{subset}_std"]])
                  @ model[f"{subset}_coef"], 0, None)
    units = frame.loc[rows, "unit"].to_numpy()
    for unit, value in list(zip(units, rul))[:100]:
        low = int(max(0.0, value - half))
        print(f"engine {unit}  RUL {int(value)}  p10 {low}  p90 {int(value + half)}  {action(low)}")
    if len(units) > 100:
        print(f"note: showing 100 of {len(units)} engines")

def score(subset):
    model = fit(subset)
    print(f"{subset} test RMSE: {model['rmse']:.1f} cycles")
    print(f"{subset} 80% interval: ±{model['half']:.1f} cycles")
    print(f"{subset} coverage on the test engines: {model['coverage']:.0%}")

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("train", help="fit FD001 and FD002, write model.npz")
    one = commands.add_parser("predict", help="RUL and action for every engine in a test file")
    one.add_argument("--subset", default="FD002", help="FD001 or FD002 (default FD002)")
    one.add_argument("--file", help="any C-MAPSS format test file")
    other = commands.add_parser("score", help="reproduced test RMSE, interval and coverage")
    other.add_argument("--subset", default="FD001", help="FD001 or FD002 (default FD001)")
    args = parser.parse_args()

    if args.command == "train":
        train()
    elif args.command == "predict":
        if not args.file:
            sys.exit("predict: --file is required")
        predict(args.subset, args.file)
    else:
        score(args.subset)

if __name__ == "__main__":
    main()
