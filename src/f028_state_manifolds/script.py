# beta
from src.analysis.io.loader import DataLoader
from src.analysis.io.logger import log
from src.f028_state_manifolds.analysis import analyze_cross_area_manifolds
from src.f028_state_manifolds.plot import plot_manifold_coupling

def run_f028():
    """
    Main execution entry for Figure 28.
    """
    log.progress("Starting Analysis f028: Cross-Area State Manifolds")
    loader = DataLoader()
    
    sessions = ["230629", "230630", "230714", "230719"]
    areas = ["V1", "V4", "PFC", "FEF"]
    
    mat = analyze_cross_area_manifolds(loader, sessions, areas)
    if mat is not None:
        plot_manifold_coupling(mat, areas)
    
    log.progress("Analysis f028 complete.")

if __name__ == "__main__":
    run_f028()
