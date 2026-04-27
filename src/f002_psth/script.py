from src.analysis.io.loader import DataLoader
from src.analysis.io.logger import log
from src.f002_psth.analysis import analyze_area_psths
from src.f002_psth.plot import plot_area_psths

def run_f002():
    log.progress("Starting Analysis f002: PSTH Suite")
    loader = DataLoader()
    output_dir = loader.get_output_dir("f002_psth")
    
    areas = loader.CANONICAL_AREAS
    results = analyze_area_psths(loader, areas)
    if results:
        plot_area_psths(results, output_dir=str(output_dir))
        
        # Export summary stats for the manifest
        import json
        summary_stats = {area: results[area]['stats'] for area in results}
        # Add N units
        for area in summary_stats:
            summary_stats[area]['n_units'] = results[area]['n_units']
            
        with open(output_dir / "stats.json", "w") as f:
            json.dump(summary_stats, f, indent=2)
            print(f"[progress] Exported stats.json to {output_dir}")
    log.progress("Analysis f002 complete.")

if __name__ == "__main__":
    run_f002()
