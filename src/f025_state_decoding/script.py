from pathlib import Path
# beta
from src.analysis.io.loader import DataLoader
from src.analysis.io.logger import log
from src.f025_state_decoding.analysis import analyze_state_decoding
from src.f025_state_decoding.plot import plot_state_decoding

def run_f025():
    """
    Main execution entry for Figure 25.
    """
    log.progress("Starting Analysis f025: State Decoding")
    loader = DataLoader()
    output_dir = loader.get_output_dir("f025_state_decoding")
    
    sessions = ["230629", "230630", "230714", "230719"]
    areas = ["V1", "V4", "PFC", "FEF"]
    
    times, results = analyze_state_decoding(loader, sessions, areas)
    if results:
        plot_state_decoding(times, results, output_dir=output_dir)
    
    log.progress("Analysis f025 complete.")

if __name__ == "__main__":
    run_f025()
