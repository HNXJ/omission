# core
from src.analysis.io.loader import DataLoader
from src.analysis.io.logger import log
from src.f044_laminar_pac.analysis import analyze_laminar_pac
from src.f044_laminar_pac.plot import plot_laminar_pac

def run_f044():
    """
    Main entry point for Figure 44: Laminar PAC.
    """
    log.progress("Starting Analysis f044: Laminar PAC")
    loader = DataLoader()
    output_dir = loader.get_output_dir("f044-laminar-pac")
    
    # Analyze first available session/probe
    session = "230629" # Default session from mapping
    probe = 0
    
    results = analyze_laminar_pac(loader, session, probe)
    
    if results:
        plot_laminar_pac(results, str(output_dir))
        
    log.progress("Analysis f044 complete.")

if __name__ == "__main__":
    run_f044()
