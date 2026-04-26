from src.analysis.io.loader import DataLoader
from src.analysis.io.logger import log
from src.f030_putative_cell_type.analysis import analyze_putative_cell_types
from src.f030_putative_cell_type.plot import plot_putative_cell_types

def run_f030():
    log.progress("Starting Analysis f030: Putative Cell Type Analysis")
    loader = DataLoader()
    output_dir = loader.get_output_dir("f030_putative_cell_type")
    
    areas = loader.CANONICAL_AREAS
    results = analyze_putative_cell_types(areas)
    
    if results:
        plot_putative_cell_types(results, output_dir=str(output_dir))
        log.progress("Analysis f030 complete.")
    else:
        log.error("Analysis f030 failed: No results generated.")

if __name__ == "__main__":
    run_f030()
