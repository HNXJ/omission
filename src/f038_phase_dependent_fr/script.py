# beta
from src.analysis.io.loader import DataLoader
from src.analysis.io.logger import log
from src.f038_phase_dependent_fr.analysis import analyze_phase_dependent_fr
from src.f038_phase_dependent_fr.plot import plot_phase_dependent_fr

def run_f038():
    """
    Main execution entry for Figure 38: PDFR.
    """
    log.progress("Starting Analysis f038: Phase-Dependent Firing Rate")
    loader = DataLoader()
    output_dir = loader.get_output_dir("f038_phase_dependent_fr")
    
    areas = ["V1", "V4", "PFC", "FEF"]
    results = analyze_phase_dependent_fr(loader, areas)
    
    if results:
        plot_phase_dependent_fr(results, output_dir)
        
    log.progress("Analysis f038 complete.")

if __name__ == "__main__":
    run_f038()
