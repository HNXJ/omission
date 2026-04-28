import sys
import os
from pathlib import Path

# Resolve Repo Root
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(REPO_ROOT))

from src.analysis.io.loader import DataLoader
from src.f007_sfc.analysis import analyze_circular_sfc
from src.f007_sfc.plot import plot_circular_sfc
from pathlib import Path
import os

def run_f007():
    loader = DataLoader()
    REPO_ROOT = Path(__file__).resolve().parent.parent.parent
    output_dir = REPO_ROOT / "outputs" / "oglo-8figs" / "f007-sfc"
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Analyze Circular SFC (Phase-locking at spike times)
    results = analyze_circular_sfc(loader, loader.CANONICAL_AREAS)
    
    # 2. Plot Circular Histograms
    plot_circular_sfc(results, str(output_dir))
    
    print(f"[success] Figure f007 (SFC Circular) manifested in {output_dir}")

if __name__ == "__main__":
    run_f007()
