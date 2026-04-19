from pathlib import Path
# core
from src.analysis.io.loader import DataLoader
from src.f001_theory.plot import plot_theory_schematic

def run_f001():
    loader = DataLoader()
    output_dir = loader.get_output_dir("f001_theory")
    plot_theory_schematic(output_dir=output_dir)

if __name__ == "__main__":
    run_f001()
