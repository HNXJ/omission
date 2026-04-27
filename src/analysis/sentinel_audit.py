import os
import json
import re
from datetime import datetime
import sys

# Ensure src is in path for registry import
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from src.analysis.registry import FigureRegistry

# SCORING CRITERIA
PENALTY_AESTHETIC = 20    # Background not #FFFFFF
PENALTY_INTEGRITY = 40    # NaN, INF, Noise, or Single-Session
PENALTY_LABELS = 20       # Missing Title, X/Y, or Legend
PENALTY_DOCS = 20         # Missing README or src ref

# Use relative paths from repo root
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
OUTPUTS_DIR = os.path.join(REPO_ROOT, '../outputs/oglo-8figs')
SCOREBOARD_PATH = os.path.join(REPO_ROOT, 'dashboard/src/data/scoreboard.json')

def audit_figure(folder_path):
    score = 100
    notes = []
    status = "pass"
    
    if not os.path.exists(folder_path):
        return 0, "queued", "Directory not found - Analysis likely not yet performed."

    # 1. Documentation Audit
    has_readme = os.path.exists(os.path.join(folder_path, 'README.md'))
    if not has_readme:
        score -= PENALTY_DOCS
        notes.append("Missing README.md")

    # 2. Content Audit (Analyze first HTML found)
    html_files = [f for f in os.listdir(folder_path) if f.endswith('.html')]
    if not html_files:
        return 0, "fail", "No HTML figure found"
    
    first_fig = os.path.join(folder_path, html_files[0])
    try:
        with open(first_fig, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
            # Aesthetic Check
            if '"paper_bgcolor":"white"' not in content and '"paper_bgcolor":"rgb(255,255,255)"' not in content:
                if '"paper_bgcolor"' in content:
                    score -= PENALTY_AESTHETIC
                    notes.append("Non-white background detected")

            # Label Check
            if '"title"' not in content or 'xaxis' not in content or 'yaxis' not in content:
                score -= PENALTY_LABELS
                notes.append("Missing Title or Axis labels")

            # Integrity Check
            if 'NaN' in content or 'Infinity' in content:
                score -= PENALTY_INTEGRITY
                notes.append("Corrupt Data (NaN/INF detected)")
                status = "fail"
    except Exception as e:
        return 0, "fail", f"Audit interrupted: {str(e)}"

    if score < 75:
        status = "fail"
    if score == 100:
        status = "awesome"
        
    return score, status, "; ".join(notes) if notes else "All Sentinel checks passed."

def main():
    print(f"[SENTINEL] Starting Registry-Driven Audit...")
    
    if not os.path.exists(SCOREBOARD_PATH):
        sb = {"ledger": [], "last_updated": "", "metrics": {}, "system_status": "INIT"}
    else:
        with open(SCOREBOARD_PATH, 'r') as f:
            sb = json.load(f)
    
    new_ledger = []
    all_figures = FigureRegistry.get_all()
    
    for fig in all_figures:
        # Find actual folder name (heuristic matching ID to folder starting with ID)
        folder_match = [d for d in os.listdir(OUTPUTS_DIR) if d.startswith(fig['id'])] if os.path.exists(OUTPUTS_DIR) else []
        
        if folder_match:
            folder_name = folder_match[0]
            path = os.path.join(OUTPUTS_DIR, folder_name)
            score, status, notes = audit_figure(path)
            file_ref = folder_name + "/*.html"
        else:
            score, status, notes = 0, "queued", "Analysis module registered but no output folder detected."
            file_ref = "N/A"
        
        new_ledger.append({
            "analysis": fig['id'] + " - " + fig['title'],
            "date": datetime.now().strftime("%Y-%m-%d"),
            "time": datetime.now().strftime("%H:%M"),
            "file": file_ref,
            "code": fig['module'] + "/script.py",
            "status": status,
            "score": score,
            "notes": notes
        })

    sb['ledger'] = new_ledger
    sb['last_updated'] = datetime.now().isoformat()
    sb['system_status'] = "ONLINE"
    sb['active_phase'] = "Phase D (Convergence)"
    
    with open(SCOREBOARD_PATH, 'w') as f:
        json.dump(sb, f, indent=2)
    
    print(f"[SENTINEL] Registry Audit Complete. {len(new_ledger)} modules verified.")

if __name__ == "__main__":
    main()

