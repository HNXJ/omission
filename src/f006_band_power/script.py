from src.analysis.io.loader import DataLoader
from src.analysis.io.logger import log
from src.f006_band_power.analysis import analyze_band_dynamics
from src.f006_band_power.plot import plot_band_dynamics

def run_f006():
    log.progress("Starting Analysis f006: Band Power Dynamics")
    loader = DataLoader()
    output_dir = loader.get_output_dir("f006_band_power")
    
    areas = loader.CANONICAL_AREAS
    results = analyze_band_dynamics(areas)
    if results:
        plot_band_dynamics(results, output_dir=str(output_dir))
    log.progress("Analysis f006 complete.")

if __name__ == "__main__":
    run_f006()
