import os
import json
import sys
from pathlib import Path

# Add project root to path for registry import
sys.path.append(str(Path(__file__).parent.parent))
from src.analysis.registry import FigureRegistry

def sync():
    outputs_dir = Path(r'D:\drive\outputs\oglo-8figs')
    manifest_path = Path(r'D:\drive\omission\dashboard\src\data\manifest.json')
    
    if not outputs_dir.exists():
        print(f"Error: {outputs_dir} does not exist.")
        return

    figures = []
    
    # Use registry as the source of truth
    registry_items = FigureRegistry.get_all()
    
    for fig in registry_items:
        # Search for folders that start with this ID
        matches = [d for d in outputs_dir.iterdir() if d.is_dir() and d.name.startswith(fig['id'])]
        if not matches:
            continue
            
        # Pick the best match (e.g. f002-psth over f002-task-timeline if needed)
        # For now, pick the first one
        d = matches[0]
        
        # Files in folder
        files = sorted([f.name for f in d.iterdir() if f.is_file() and f.suffix in ['.html', '.svg', '.png']])
        has_readme = (d / "README.md").exists()
        
        # Load stats if present
        stats = {}
        stats_file = d / "stats.json"
        if stats_file.exists():
            try:
                with open(stats_file, "r") as f:
                    stats = json.load(f)
            except:
                pass
        
        figures.append({
            "id": fig['id'],
            "title": fig['title'],
            "phase": fig.get('phase', 1),
            "baseUrl": f"/@fs/{d.as_posix()}",
            "files": files,
            "has_readme": has_readme,
            "stats": stats,
            "metadata": {
                "x": fig.get('x', ''),
                "y": fig.get('y', '')
            }
        })
        
    # Maintain the existing "reports" section if manifest exists
    reports = []
    if manifest_path.exists():
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                old_data = json.load(f)
                reports = old_data.get("reports", [])
        except:
            pass
            
    manifest_data = {
        "figures": figures,
        "reports": reports,
        "last_synced": Path(outputs_dir).stat().st_mtime
    }
    
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, indent=2)
        
    print(f"Manifest synced with {len(figures)} figures from Registry.")

if __name__ == "__main__":
    sync()
