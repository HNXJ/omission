# beta
from src.analysis.io.loader import DataLoader
from src.analysis.io.logger import log
from src.f027_identity_coding.analysis import analyze_omission_identity
from src.f027_identity_coding.plot import plot_identity_decoding

def run_f027():
    """
    Main execution entry for Figure 27.
    """
    log.progress("Starting Analysis f027: Omission Identity Coding")
    loader = DataLoader()
    
    sessions = ["230629", "230630", "230714", "230719"]
    areas = ["V1", "V4", "PFC", "FEF"]
    
    times, results = analyze_omission_identity(loader, sessions, areas)
    if results:
        plot_identity_decoding(times, results)
    
    log.progress("Analysis f027 complete.")

if __name__ == "__main__":
    run_f027()
