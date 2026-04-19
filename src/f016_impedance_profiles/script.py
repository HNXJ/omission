from pathlib import Path
# beta
from src.analysis.io.loader import DataLoader
from src.f016_impedance_profiles.analysis import analyze_impedance
from src.f016_impedance_profiles.plot import plot_impedance

def run_f016():
    loader = DataLoader()
    output_dir = loader.get_output_dir("f016_impedance_profiles")
    results = analyze_impedance(loader, session="230629", probe=0)
    if results:
        plot_impedance(results, output_dir=output_dir)

if __name__ == "__main__":
    run_f016()
