from pathlib import Path
# core
from src.analysis.io.loader import DataLoader
from src.f002_psth.plot import plot_design_summary

def run_f002():
    loader = DataLoader()
    output_dir = loader.get_output_dir("f002_psth")
    plot_design_summary(output_dir=output_dir)

if __name__ == "__main__":
    run_f002()
