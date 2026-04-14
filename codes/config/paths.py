import os
from pathlib import Path

# Base directories
# Base directories
PROJECT_ROOT = Path(os.environ.get("OMISSION_PROJECT_ROOT", r"D:\drive\omission")).resolve()

# NWB Data usually sits in a specific 'analysis/nwb' path on the workstation
DATA_DIR = Path(os.environ.get("OMISSION_DATA_DIR", r"D:\analysis\nwb")).resolve()
if not DATA_DIR.exists():
    DATA_DIR = (PROJECT_ROOT / "data").resolve()

OUTPUT_DIR = Path(os.environ.get("OMISSION_OUTPUT_DIR", PROJECT_ROOT / "outputs")).resolve()

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
