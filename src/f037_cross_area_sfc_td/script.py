# beta
from src.analysis.io.loader import DataLoader
from src.analysis.io.logger import log
from src.f037_cross_area_sfc_td.analysis import analyze
from src.f037_cross_area_sfc_td.plot import plot

def run_f037():
    """
    Main execution entry for Figure 37: TD SFC.
    """
    log.progress("Starting Analysis f037: Top-Down SFC (PFC->V1)")
    loader = DataLoader()
    output_dir = loader.get_output_dir("f037_cross_area_sfc_td")
    
    res = analyze(loader, "PFC", "V1")
    if res:
        plot(res, output_dir)
        
    log.progress("Analysis f037 complete.")

if __name__ == "__main__":
    run_f037()
