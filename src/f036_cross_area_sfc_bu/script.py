# beta
from src.analysis.io.loader import DataLoader
from src.analysis.io.logger import log
from src.f036_cross_area_sfc_bu.analysis import analyze_cross_area_sfc
from src.f036_cross_area_sfc_bu.plot import plot_cross_area_sfc

def run_f036():
    """
    Main execution entry for Figure 36: BU SFC.
    """
    log.progress("Starting Analysis f036: Bottom-Up SFC (V1->V4)")
    loader = DataLoader()
    output_dir = loader.get_output_dir("f036_cross_area_sfc_bu")
    
    res = analyze_cross_area_sfc(loader, "V1", "V4")
    if res:
        plot_cross_area_sfc(res, output_dir)
        
    log.progress("Analysis f036 complete.")

if __name__ == "__main__":
    run_f036()
