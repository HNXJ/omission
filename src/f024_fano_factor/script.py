# beta
from src.analysis.io.loader import DataLoader
from src.analysis.io.logger import log
from src.f024_fano_factor.analysis import analyze_fano_factor
from src.f024_fano_factor.plot import plot_fano_factor

def run_f024():
    """
    Main execution entry for Figure 24.
    """
    log.progress("Starting Analysis f024: Fano Factor")
    loader = DataLoader()
    
    sessions = ["230629", "230630", "230714", "230719"]
    areas = ["V1", "V4", "PFC", "FEF"]
    
    results = analyze_fano_factor(loader, sessions, areas, condition="AXAB")
    if results:
        plot_fano_factor(results)
    
    log.progress("Analysis f024 complete.")

if __name__ == "__main__":
    run_f024()
