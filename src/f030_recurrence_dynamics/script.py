# beta
from src.analysis.io.loader import DataLoader
from src.analysis.io.logger import log
from src.f030_recurrence_dynamics.analysis import analyze_recurrence_dynamics
from src.f030_recurrence_dynamics.plot import plot_recurrence_dynamics

def run_f030():
    """
    Main execution entry for Figure 30.
    """
    log.progress("Starting Analysis f030: Recurrence & Feedback Dynamics")
    loader = DataLoader()
    
    sessions = ["230629", "230630", "230714", "230719"]
    areas = ["V1", "V4", "PFC", "FEF"]
    
    results = analyze_recurrence_dynamics(loader, sessions, areas)
    if results:
        plot_recurrence_dynamics(results)
    
    log.progress("Analysis f030 complete.")

if __name__ == "__main__":
    run_f030()
