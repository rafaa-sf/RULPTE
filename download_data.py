"""Download the NASA C-MAPSS turbofan FD001 files into the data/ folder.

Standard library only (no extra installs). Run from the project folder:

    python download_data.py            # download if files are missing
    python download_data.py --force    # download again even if present
"""
import io
import shutil
import sys
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

# Mirror of NASA's Prognostics Data Repository entry "Turbofan Engine
# Degradation Simulation Data Set" (the "6." file, not the newer "17." one).
URL = (
    "https://phm-datasets.s3.amazonaws.com/NASA/"
    "6.+Turbofan+Engine+Degradation+Simulation+Data+Set.zip"
)
DATA_DIR = Path(__file__).resolve().parent / "data"
REQUIRED = ["train_FD001.txt", "test_FD001.txt", "RUL_FD001.txt"]
OPTIONAL = ["readme.txt"]
# file -> (expected rows, expected engines); None = not checked
EXPECTED = {
    "train_FD001.txt": (20631, 100),
    "test_FD001.txt": (13096, 100),
    "RUL_FD001.txt": (100, None),
}

MANUAL_HELP = f"""
Automatic download failed. Download it by hand instead:
  1. Search for "NASA Prognostics Data Repository" and open the
     "Turbofan Engine Degradation Simulation Data Set" entry.
  2. Download the zip and unzip it.
  3. Copy these files into: {DATA_DIR}
     {', '.join(REQUIRED)}
"""


def download(url, dest):
    """Stream the file to disk, printing progress in MB."""
    req = urllib.request.Request(url, headers={"User-Agent": "cmapss-rul-project"})
    with urllib.request.urlopen(req, timeout=60) as resp, open(dest, "wb") as out:
        total = int(resp.headers.get("Content-Length") or 0)
        done = 0
        while True:
            chunk = resp.read(1024 * 256)
            if not chunk:
                break
            out.write(chunk)
            done += len(chunk)
            size = f" / {total / 1e6:.1f}" if total else ""
            print(f"\rDownloaded {done / 1e6:.1f}{size} MB", end="", flush=True)
    print()


def _scan(source, wanted, data_dir, found, depth=0):
    """Look through a zip (and zips nested inside it) for the wanted files."""
    with zipfile.ZipFile(source) as zf:
        for info in zf.infolist():
            base = Path(info.filename).name  # basename only: no path tricks
            low = base.lower()
            if low in wanted:
                target = wanted[low]
                with zf.open(info) as src, open(data_dir / target, "wb") as dst:
                    shutil.copyfileobj(src, dst)
                found.add(target)
            elif low.endswith(".zip") and depth < 3:
                # NASA's zip contains another zip (CMAPSSData.zip): open it too
                with zf.open(info) as inner:
                    _scan(io.BytesIO(inner.read()), wanted, data_dir, found, depth + 1)


def extract_needed(zip_path, data_dir):
    """Copy only the wanted files out of the zip, ignoring folder structure."""
    wanted = {n.lower(): n for n in REQUIRED + OPTIONAL}
    data_dir.mkdir(parents=True, exist_ok=True)
    found = set()
    _scan(zip_path, wanted, data_dir, found)
    return found


def check(data_dir):
    """Compare row and engine counts with the known FD001 sizes. Warn only."""
    for name, (rows, engines) in EXPECTED.items():
        lines = [l for l in (data_dir / name).read_text().splitlines() if l.strip()]
        got_engines = len({l.split()[0] for l in lines}) if engines else None
        ok = len(lines) == rows and (engines is None or got_engines == engines)
        note = "OK" if ok else f"WARNING: expected {rows} rows / {engines} engines"
        extra = f", {got_engines} engines" if engines else ""
        print(f"  {name}: {len(lines)} rows{extra} -> {note}")


def main():
    force = "--force" in sys.argv
    if not force and all((DATA_DIR / n).exists() for n in REQUIRED):
        print(f"Data already in {DATA_DIR}. Use --force to download again.")
        check(DATA_DIR)
        return 0

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    zip_path = DATA_DIR / "_download.zip"
    try:
        print("Downloading C-MAPSS dataset...")
        download(URL, zip_path)
        found = extract_needed(zip_path, DATA_DIR)
    except (urllib.error.URLError, TimeoutError, zipfile.BadZipFile, OSError) as exc:
        print(f"Error: {exc}")
        print(MANUAL_HELP)
        return 1
    finally:
        zip_path.unlink(missing_ok=True)

    missing = [n for n in REQUIRED if n not in found]
    if missing:
        print(f"Error: not found in the zip: {', '.join(missing)}")
        print(MANUAL_HELP)
        return 1

    print(f"Saved to {DATA_DIR}. Sanity check:")
    check(DATA_DIR)
    return 0


if __name__ == "__main__":
    sys.exit(main())
