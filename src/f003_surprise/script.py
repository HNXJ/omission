from src.analysis.io.loader import DataLoader
from src.analysis.io.logger import log
from src.f003_surprise.analysis import analyze_surprise
from src.f003_surprise.plot import plot_surprise

def run_f003():
    log.progress("Starting Analysis f003: Surprise Index")
    loader = DataLoader()
    output_dir = loader.get_output_dir("f003_surprise")
    
    areas = loader.CANONICAL_AREAS
    results = analyze_surprise(loader, areas)
    if results:
        plot_surprise(results, output_dir=str(output_dir))
        
        # Export summary stats for the manifest
        import json
        summary_stats = {area: results[area]['stats'] for area in results}
        with open(output_dir / "stats.json", "w") as f:
            json.dump(summary_stats, f, indent=2)
            print(f"[progress] Exported stats.json to {output_dir}")
    log.progress("Analysis f003 complete.")

if __name__ == "__main__":
    run_f003()
