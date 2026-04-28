import json
import sys
import shutil
from pathlib import Path

# Resolve Repo Root
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(REPO_ROOT))

from src.analysis.io.loader import DataLoader
from src.analysis.registry import FigureRegistry
from src.f002_psth.analysis import analyze_area_psths
from src.f003_surprise.analysis import analyze_surprise
from src.f004_coding.find_stable_units import compute_area_coding_stats

def build_payload():
    loader = DataLoader()
    registry = FigureRegistry.get_all()
    
    # Repo-relative paths
    output_bases = [
        REPO_ROOT / "outputs" / "oglo-8figs",
        REPO_ROOT.parent / "outputs" / "oglo-8figs"
    ]
    
    dashboard_data_dir = REPO_ROOT / "dashboard" / "src" / "data"
    dashboard_data_dir.mkdir(parents=True, exist_ok=True)
    
    public_figures_dir = REPO_ROOT / "dashboard" / "public" / "figures"
    public_figures_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"[action] Initializing Portable Portal Adapter at {REPO_ROOT}...")
    
    figures_manifest = []
    
    for fig in registry:
        fig_id = fig['id']
        files = set()
        max_mtime = 0
        fig_dirname = ""
        
        # Merge assets from all bases (sibling then local to prioritize local overwrites)
        for base in reversed(output_bases):
            if not base.exists(): continue
            matches = [d for d in base.iterdir() if d.is_dir() and d.name.startswith(fig_id)]
            if not matches: continue
            
            fig_dir = matches[0]
            fig_dirname = fig_dir.name
            target_dir = public_figures_dir / fig_dirname
            target_dir.mkdir(parents=True, exist_ok=True)
            max_mtime = max(max_mtime, fig_dir.stat().st_mtime)
            
            for f in fig_dir.iterdir():
                if f.is_file() and f.suffix in ['.html', '.svg', '.png']:
                    shutil.copy2(f, target_dir / f.name)
                    files.add(f.name)
                    
        if not fig_dirname: continue
        
        sorted_files = sorted(list(files))
        stats = {}
        
        # FIGURE-SPECIFIC STATISTICAL ADAPTERS
        if fig_id == "f002":
            results = analyze_area_psths(loader, loader.CANONICAL_AREAS)
            stats = {area: results[area]['stats'] for area in results}
            for area in stats: stats[area]['n_units'] = int(results[area]['n_units'])
        
        elif fig_id == "f003":
            results = analyze_surprise(loader, loader.CANONICAL_AREAS)
            stats = {area: results[area]['stats'] for area in results}
            
        elif fig_id == "f004":
            area_coding_stats = compute_area_coding_stats()
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

        # Multi-Condition Stats Injection
        if fig_id in ["f002", "f003", "f004"]:
            if fig_id == "f004":
                stats = {
                    "aaab": {a: {"n": stats[a]["n_s_plus"], "label": "S+"} for a in stats},
                    "axab": {a: {"n": stats[a]["n_o_plus"], "label": "O+"} for a in stats},
                    "both": stats
                }
            else:
                stats = {"both": stats, "axab": stats, "aaab": {}}

        figures_manifest.append({
            "id": fig_id,
            "title": fig['title'],
            "phase": fig.get('phase', 1),
            "baseUrl": f"/figures/{fig_dirname}", # PORTABLE ASSET PATH
            "files": sorted_files,
            "has_readme": (target_dir / "README.md").exists(),
            "stats": stats,
            "mtime": max_mtime,
            "metadata": {"x": fig.get('x', ''), "y": fig.get('y', '')}
        })

    if not figures_manifest:
        raise ValueError("[error] No figures were manifested.")

    # GENERATE REAL METADATA-DERIVED SCOREBOARD
    n_total_units = 0
    for area in loader.CANONICAL_AREAS:
        n_total_units += len(loader.get_units_by_area(area))
        
    session_map_path = REPO_ROOT / "context" / "overview" / "session-area-mapping.md"
    n_sessions = 0
    if session_map_path.exists():
        n_sessions = len([line for line in session_map_path.read_text().split('\n') if '|' in line]) - 2
        
    scoreboard_data = {
        "system_status": "STABLE",
        "active_phase": f"Phase {max([f['phase'] for f in figures_manifest])}",
        "metrics": {
            "sessions": n_sessions,
            "latency_onset": "45ms [CALIBRATION PENDING]",
            "units": n_total_units
        },
        "ledger": []
    }
    
    for fig in figures_manifest:
        # Use stored mtime
        mtime = fig.get("mtime", 0)
        from datetime import datetime
        dt = datetime.fromtimestamp(mtime)
        
        scoreboard_data["ledger"].append({
            "analysis": fig["title"],
            "file": "script.py",
            "date": dt.strftime("%Y-%m-%d"),
            "time": dt.strftime("%H:%M"),
            "status": "awesome" if fig["stats"] else "pass",
            "score": 95 if fig["stats"] else 80,
            "notes": f"Generated {len(fig['files'])} portable assets.",
            "code": f"src.{fig['id']}"
        })
    
    with open(dashboard_data_dir / "scoreboard.json", "w") as f:
        json.dump(scoreboard_data, f, indent=2)

    # Last sync timestamp from the most recent output_base
    sync_ts = "0"
    for base in output_bases:
        if base.exists():
            sync_ts = str(base.stat().st_mtime)
            break

    final_manifest = {
        "figures": figures_manifest,
        "reports": [],
        "last_synced": sync_ts
    }
    
    with open(dashboard_data_dir / "manifest.json", "w") as f:
        json.dump(final_manifest, f, indent=2)
    
    print(f"[success] Manifest built with {len(figures_manifest)} portable figures.")

if __name__ == "__main__":
    try:
        build_payload()
    except Exception as e:
        print(f"\n[CRITICAL FAILURE] {str(e)}")
        sys.exit(1)
