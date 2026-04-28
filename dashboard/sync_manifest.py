import os
import json
import sys
import shutil
from pathlib import Path

# Resolve Repo Root
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(REPO_ROOT))
from src.analysis.registry import FigureRegistry

def sync():
    # Repo-relative paths
    outputs_dir = REPO_ROOT.parent / 'outputs' / 'oglo-8figs'
    if not outputs_dir.exists():
        outputs_dir = REPO_ROOT / 'outputs' / 'oglo-8figs'
        outputs_dir.mkdir(parents=True, exist_ok=True)
        
    public_figures_dir = REPO_ROOT / 'dashboard' / 'public' / 'figures'
    public_figures_dir.mkdir(parents=True, exist_ok=True)
    
    manifest_path = REPO_ROOT / 'dashboard' / 'src' / 'data' / 'manifest.json'
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    
    figures = []
    registry_items = FigureRegistry.get_all()
    
    for fig in registry_items:
        matches = [d for d in outputs_dir.iterdir() if d.is_dir() and d.name.startswith(fig['id'])]
        if not matches: continue
            
        d = matches[0]
        target_dir = public_figures_dir / d.name
        target_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy for portability
        files = []
        for f in d.iterdir():
            if f.is_file() and f.suffix in ['.html', '.svg', '.png']:
                shutil.copy2(f, target_dir / f.name)
                files.append(f.name)
        
        files.sort()
        stats = {}
        stats_file = d / "stats.json"
        if stats_file.exists():
            try:
                with open(stats_file, "r") as f: stats = json.load(f)
            except: pass
        
        figures.append({
            "id": fig['id'],
            "title": fig['title'],
            "phase": fig.get('phase', 1),
            "baseUrl": f"/figures/{d.name}", # PORTABLE ASSET PATH
            "files": files,
            "has_readme": (d / "README.md").exists(),
            "stats": stats,
            "metadata": {"x": fig.get('x', ''), "y": fig.get('y', '')}
        })
        
    manifest_data = {
        "figures": figures,
        "reports": [],
        "last_synced": str(outputs_dir.stat().st_mtime)
    }
    
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, indent=2)
        
    print(f"Manifest synced with {len(figures)} portable figures.")

if __name__ == "__main__":
    sync()
