#!/usr/bin/env python3
"""Set up and start RULPTE from nothing.

One command does the whole zero-to-results path: create `.venv`, install the
pinned libraries plus the notebook viewer, download the NASA data, then open
the notebook. Safe to run again: each step is skipped when it is already done.

    python run.py           set up, then open the notebook
    python run.py --check   set up, run the notebook headless, check the scores
    python run.py --test    set up, then run the test suite against the notebook
    python run.py --dry-run print the commands without running them
"""
import argparse
import os
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent
VENV = ROOT / ".venv"
DATA = ROOT / "data"
NOTEBOOK = "rul_prediction.ipynb"
DATA_FILES = tuple(f"{kind}_{s}.txt" for s in ("FD001", "FD002", "FD003", "FD004")
                   for kind in ("train", "test", "RUL"))
MIN_PYTHON = (3, 12)
EXPECTED = ("FD001 test RMSE: 28.3 cycles", "FD001 held-out RMSE: 44.8 cycles",
            "FD002 test RMSE: 33.5 cycles", "FD002 held-out RMSE: 41.0 cycles",
            "FD001 80% interval: ±45.9 cycles", "FD002 80% interval: ±49.8 cycles",
            "FD002 coverage on the test engines: 84%",
            "FD001 repeated grouped CV: 41.5 ± 2.2 cycles",
            "FD002 repeated grouped CV: 41.0 ± 2.4 cycles")


def venv_python():
    """The interpreter inside .venv, if it exists."""
    for candidate in (VENV / "Scripts" / "python.exe", VENV / "bin" / "python"):
        if candidate.is_file():
            return candidate
    return None


def missing_scores(text):
    """The expected score lines that did not appear in the executed notebook."""
    return [line for line in EXPECTED if line not in text]


def step(message):
    print(f"\n== {message}", flush=True)


def run(command, dry_run, capture=True):
    printable = " ".join(str(part) for part in command)
    print(f"   {printable}", flush=True)
    if dry_run:
        return ""
    if not capture:
        subprocess.run([str(part) for part in command], cwd=ROOT, check=True)
        return ""
    result = subprocess.run(
        [str(part) for part in command],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        print(result.stdout[-2000:])
        print(result.stderr[-2000:])
        sys.exit(f"\nFailed: {printable}")
    return result.stdout


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true",
                        help="run the notebook headless and print the scores, without opening a browser")
    parser.add_argument("--test", action="store_true",
                        help="run the test suite, which checks the tool against the notebook")
    parser.add_argument("--dry-run", action="store_true",
                        help="print the commands without running them")
    args = parser.parse_args()

    if sys.version_info < MIN_PYTHON:
        sys.exit(
            f"Python {MIN_PYTHON[0]}.{MIN_PYTHON[1]} or newer is required; "
            f"this is {sys.version.split()[0]} from {sys.executable}"
        )

    python = venv_python()
    if python is None:
        step(f"Creating the virtual environment in {VENV.name}")
        run([sys.executable, "-m", "venv", str(VENV)], args.dry_run)
        python = venv_python()
        if python is None and not args.dry_run:
            sys.exit("The virtual environment was not created. Is the 'venv' module available?")
        python = python or (VENV / ("Scripts/python.exe" if os.name == "nt" else "bin/python"))
    else:
        print(f"Virtual environment: {VENV}")

    step("Installing the libraries the notebook imports")
    run([python, "-m", "pip", "install", "--upgrade", "pip"], args.dry_run)
    run([python, "-m", "pip", "install", "-r", ROOT / "requirements.txt"], args.dry_run)

    step("Installing the notebook viewer")
    viewer = ["notebook"] + (["nbconvert"] if args.check else [])
    run([python, "-m", "pip", "install", *viewer], args.dry_run)

    if args.test:
        step("Installing pytest")
        run([python, "-m", "pip", "install", "pytest"], args.dry_run)

    if all((DATA / name).is_file() for name in DATA_FILES):
        print(f"Data: already in {DATA.name}/, skipping the download")
    else:
        step("Downloading the NASA data (about 15 MB, unpacked to 6 MB)")
        run([python, ROOT / "download_data.py"], args.dry_run)

    if args.check:
        step("Running the notebook headless")
        output = run([python, "-m", "nbconvert", "--to", "notebook", "--execute",
                      "--stdout", NOTEBOOK], args.dry_run)
        print()
        if args.dry_run:
            print("   (dry run: the notebook was not executed)")
            return
        missing = missing_scores(output)
        for expected in EXPECTED:
            print(f"   {'MISS' if expected in missing else 'ok  '} {expected}")
        if missing:
            sys.exit("\nThe notebook did not print the expected score.")
        print("\nAll cells ran and the scores match.")
        return

    if args.test:
        step("Training the saved model")
        run([python, "predict.py", "train"], args.dry_run)
        step("Running the tests")
        # no:cacheprovider keeps pytest from writing .pytest_cache, which some
        # locked-down machines refuse
        run([python, "-m", "pytest", "tests", "-q", "-p", "no:cacheprovider"],
            args.dry_run, capture=False)
        return

    step("Opening the notebook in your browser")
    run([python, "-m", "notebook", NOTEBOOK], args.dry_run, capture=False)


if __name__ == "__main__":
    main()
