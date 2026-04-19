# beta
from src.analysis.io.loader import DataLoader
from src.analysis.io.logger import log
from src.f032_directed_flow.analysis import analyze_directed_flow
from src.f032_directed_flow.plot import plot_directed_flow

def run_f032():
    """
    Main execution entry for Figure 32.
    """
    log.progress("Starting Analysis f032: Directed Flow")
    loader = DataLoader()
    output_dir = loader.get_output_dir("f032_directed_flow")
    
    areas = ["V1", "V4", "PFC", "FEF"]
    mat = analyze_directed_flow(loader, areas)
    
    if mat is not None:
        plot_directed_flow(mat, areas, output_dir)
        
    log.progress("Analysis f032 complete.")

if __name__ == "__main__":
    run_f032()
