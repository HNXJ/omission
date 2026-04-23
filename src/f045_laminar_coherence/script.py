# core
from src.analysis.io.loader import DataLoader
from src.analysis.io.logger import log
from src.f045_laminar_coherence.analysis import analyze_laminar_coherence
from src.f045_laminar_coherence.plot import plot_laminar_coherence

def run_f045():
    """
    Main entry point for Figure 45: Laminar Coherence.
    """
    log.progress("Starting Analysis f045: Laminar Coherence")
    loader = DataLoader()
    output_dir = loader.get_output_dir("f045-laminar-coherence")
    
    session = "230629"
    probe = 0
    
    results = analyze_laminar_coherence(loader, session, probe)
    
    if results:
        plot_laminar_coherence(results, str(output_dir))
        
    log.progress("Analysis f045 complete.")

if __name__ == "__main__":
    run_f045()
