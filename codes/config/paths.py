import os
from pathlib import Path

# Base directories
PROJECT_ROOT = Path(os.environ.get("OMISSION_PROJECT_ROOT", Path(__file__).resolve().parent.parent.parent.parent))

DATA_DIR = Path(os.environ.get("OMISSION_DATA_DIR", PROJECT_ROOT / "data"))
OUTPUT_DIR = Path(os.environ.get("OMISSION_OUTPUT_DIR", PROJECT_ROOT / "outputs"))

# Data subdirectories
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
ARRAY_DATA_DIR = DATA_DIR / "arrays"
METADATA_DIR = DATA_DIR / "metadata"
BEHAVIORAL_DIR = DATA_DIR / "behavioral"

# Output subdirectories
FIGURES_DIR = OUTPUT_DIR / "figures"
REPORTS_DIR = OUTPUT_DIR / "reports"

def get_nwb_files():
    return list(DATA_DIR.rglob("*.nwb"))

def ensure_dirs():
    for d in [OUTPUT_DIR, FIGURES_DIR, REPORTS_DIR, PROCESSED_DATA_DIR]:
        d.mkdir(parents=True, exist_ok=True)
