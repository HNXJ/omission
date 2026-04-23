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
    fig = plot_selectivity_index(results)
    
    export_path = os.path.join("Export_Staging", "f037_selectivity_index.html")
    fig.write_html(export_path)
    print(f"""[f037] Exported to {export_path}""")

if __name__ == "__main__":
    main()
