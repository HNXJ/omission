import json
import sys
from pathlib import Path

# Resolve Repo Root
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(REPO_ROOT))

from src.analysis.io.loader import DataLoader
from src.analysis.registry import FigureRegistry
from src.f002_psth.analysis import analyze_area_psths
from src.f003_surprise.analysis import analyze_surprise
from src.f004_coding.find_stable_units import find_highly_responsive_units, compute_area_coding_stats

def build_payload():
    loader = DataLoader()
    registry = FigureRegistry.get_all()
    
    # Repo-relative paths
    output_base = REPO_ROOT.parent / "outputs" / "oglo-8figs" # External to repo but relative to root's parent
    # Fallback to local outputs if external doesn't exist
    if not output_base.exists():
        output_base = REPO_ROOT / "outputs" / "oglo-8figs"
        output_base.mkdir(parents=True, exist_ok=True)
        
    dashboard_data_dir = REPO_ROOT / "dashboard" / "src" / "data"
    dashboard_data_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"[action] Initializing Portal Adapter at {REPO_ROOT}...")
    
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
            area_coding_stats = compute_area_coding_stats()
            # Canonical Payload: explicit counts for S+ and O+
            for area in loader.CANONICAL_AREAS:
                a_res = area_coding_stats.get(area, {})
                stats[area] = {
                    "tier": "Sig-k" if (a_res.get('n_s_plus', 0) + a_res.get('n_o_plus', 0)) > 0 else "Null",
                    "n_stable": a_res.get('n_stable', 0),
                    "n_s_plus": a_res.get('n_s_plus', 0),
                    "n_s_minus": a_res.get('n_s_minus', 0),
                    "n_o_plus": a_res.get('n_o_plus', 0),
                    "n_o_minus": a_res.get('n_o_minus', 0),
                    "test": a_res.get('test', ''),
                    "threshold": a_res.get('threshold', 0)
                }

        # Multi-Condition Stats Injection (Standard vs Omission)
        # If the figure supports it, we nest stats by condition
        if fig_id in ["f002", "f003", "f004"]:
            # For f004, AAAB stats = Stimulus counts, AXAB stats = Omission counts
            if fig_id == "f004":
                stats = {
                    "aaab": {a: {"n": stats[a]["n_s_plus"], "label": "S+"} for a in stats},
                    "axab": {a: {"n": stats[a]["n_o_plus"], "label": "O+"} for a in stats},
                    "both": stats
                }
            elif fig_id == "f002":
                # f002 PSTH compares AXAB to AAAB directly, so the stats are already a comparison
                # We'll keep them in 'both' and 'axab'
                stats = {"both": stats, "axab": stats, "aaab": {}}
            elif fig_id == "f003":
                stats = {"both": stats, "axab": stats, "aaab": {}}

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
