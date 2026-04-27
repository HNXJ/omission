# beta
import os
from src.analysis.io.loader import DataLoader
from src.f037_selectivity_index.analysis import analyze_selectivity_index
from src.f037_selectivity_index.plot import plot_selectivity_index

def main():
    loader = DataLoader()
    areas = ["V1", "V2", "V4", "PFC"]
    
    print(f"""[f037] Starting SSI Analysis...""")
    results = analyze_selectivity_index(loader, areas)
    
    print(f"""[f037] Generating Plot...""")
    plotter = plot_selectivity_index(results)
    
    output_dir = loader.get_output_dir("f037-selectivity-index")
    plotter.save(output_dir, "f037_selectivity_index")
    print(f"""[f037] Exported to {output_dir}""")

if __name__ == "__main__":
    main()
