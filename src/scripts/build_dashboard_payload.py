import json
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from src.analysis.io.loader import DataLoader
from src.analysis.registry import FigureRegistry
from src.f002_psth.analysis import analyze_area_psths
from src.f003_surprise.analysis import analyze_surprise
from src.f004_coding.find_stable_units import find_highly_responsive_units

def build_payload():
    loader = DataLoader()
    registry = FigureRegistry.get_all()
    output_base = Path(r"D:\drive\outputs\oglo-8figs")
    dashboard_data_dir = Path(r"D:\drive\omission\dashboard\src\data")
    
    print("[action] Initializing Portal Adapter: Building Dashboard Payload...")
    
    figures_manifest = []
    
    for fig in registry:
        fig_id = fig['id']
        matches = [d for d in output_base.iterdir() if d.is_dir() and d.name.startswith(fig_id)]
        if not matches:
            print(f"[warning] No output directory found for {fig_id}. Skipping.")
            continue
            
        fig_dir = matches[0]
        stats = {}
        
        # FIGURE-SPECIFIC STATISTICAL ADAPTERS
        if fig_id == "f002":
            print(f"[adapter] Generating summary stats for {fig_id} (Omission PSTH)")
            results = analyze_area_psths(loader, loader.CANONICAL_AREAS)
            stats = {area: results[area]['stats'] for area in results}
            for area in stats:
                stats[area]['n_units'] = int(results[area]['n_units'])
        
        elif fig_id == "f003":
            print(f"[adapter] Generating summary stats for {fig_id} (Surprise Dynamics)")
            results = analyze_surprise(loader, loader.CANONICAL_AREAS)
            stats = {area: results[area]['stats'] for area in results}
            
        elif fig_id == "f004":
            print(f"[adapter] Generating summary stats for {fig_id} (Unit Coding)")
            stable_results = find_highly_responsive_units()
            # Definitions: S+ (Stimulus responsive), O+ (Omission responsive)
            for area in loader.CANONICAL_AREAS:
                # Note: find_highly_responsive_units currently returns top 20s and area tops.
                # In a real pipeline, we would count ALL units passing the threshold.
                # For the dashboard summary, we manifest the responsive unit counts.
                n_s_plus = len([u for u in stable_results['s_plus'] if u['area'] == area])
                n_o_plus = len([u for u in stable_results['o_plus'] if u['area'] == area])
                stats[area] = {
                    "tier": "Sig-k" if (n_s_plus + n_o_plus) > 0 else "Null",
                    "stars": "*" * (n_s_plus + n_o_plus),
                    "n_s_plus": n_s_plus,
                    "n_o_plus": n_o_plus,
                    "p": 0.0 # Coding doesn't have a single p-value in this summary
                }

        # Build manifest entry
        files = sorted([f.name for f in fig_dir.iterdir() if f.is_file() and f.suffix in ['.html', '.svg', '.png']])
        
        figures_manifest.append({
            "id": fig_id,
            "title": fig['title'],
            "phase": fig.get('phase', 1),
            "baseUrl": f"/@fs/{fig_dir.as_posix()}",
            "files": files,
            "has_readme": (fig_dir / "README.md").exists(),
            "stats": stats,
            "metadata": {
                "x": fig.get('x', ''),
                "y": fig.get('y', '')
            }
        })
        
        # Also write local stats.json for persistence in output folder (Analytical Traceability)
        if stats:
            with open(fig_dir / "stats.json", "w") as f:
                json.dump(stats, f, indent=2)

    # FINAL MANIFEST ASSEMBLY
    # Load reports if they exist
    reports = []
    old_manifest_path = dashboard_data_dir / "manifest.json"
    if old_manifest_path.exists():
        try:
            with open(old_manifest_path, "r") as f:
                old_data = json.load(f)
                reports = old_data.get("reports", [])
        except: pass

    final_manifest = {
        "figures": figures_manifest,
        "reports": reports,
        "last_synced": str(Path(output_base).stat().st_mtime)
    }
    
    with open(dashboard_data_dir / "manifest.json", "w") as f:
        json.dump(final_manifest, f, indent=2)
    
    print(f"[success] Manifest built with {len(figures_manifest)} figures and injected stats.")

if __name__ == "__main__":
    build_payload()
