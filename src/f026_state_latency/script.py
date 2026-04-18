# beta
from src.analysis.io.loader import DataLoader
from src.analysis.io.logger import log
from src.f026_state_latency.analysis import analyze_area_latencies
from src.f026_state_latency.plot import plot_divergence_latency

def run_f026():
    """
    Main execution entry for Figure 26.
    """
    log.progress("Starting Analysis f026: State Divergence Latency")
    loader = DataLoader()
    
    # Representative sessions
    sessions = ["230629", "230630", "230714", "230719"]
    areas = ["V1", "V4", "PFC", "FEF"]
    
    results = analyze_area_latencies(loader, sessions, areas)
    if results:
        plot_divergence_latency(results)
    
    log.progress("Analysis f026 complete.")

if __name__ == "__main__":
    run_f026()
