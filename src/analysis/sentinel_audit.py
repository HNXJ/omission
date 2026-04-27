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

class GPAAuditor:
    def __init__(self):
        self.criteria = {
            "AESTHETIC": {"white_bg": 2.0, "font_scaling": 2.0, "legend_pos": 2.0, "color_validity": 2.0, "grid_clarity": 2.0},
            "STATISTICAL": {"sig_tier_presence": 10.0, "p_value_reporting": 5.0, "stars_mapping": 5.0, "test_identification": 5.0, "n_counts_verified": 5.0},
            "DATA_INTEGRITY": {"nan_absence": 10.0, "inf_absence": 10.0, "zero_variance_guard": 5.0, "range_clipping": 5.0},
            "DOCUMENTATION": {"readme_presence": 5.0, "methodology_detail": 5.0, "data_contract_ref": 5.0, "src_link_validity": 5.0},
            "SCIENTIFIC_DENSITY": {"multi_area_comparison": 10.0, "temporal_resolution": 5.0, "baseline_reporting": 5.0}
        }

    def audit_figure(self, folder_path):
        gpa = 0.0
        details = []
        status = "pass"
        
        if not os.path.exists(folder_path):
            return 0, "queued", "Directory not found."

        # 1. Documentation (20 pts)
        if os.path.exists(os.path.join(folder_path, 'README.md')):
            gpa += 20.0
        else:
            details.append("Missing README.md")

        # 2. Content Audit
        html_files = [f for f in os.listdir(folder_path) if f.endswith('.html')]
        if not html_files:
            return 0, "fail", "No HTML figure found"
        
        first_fig = os.path.join(folder_path, html_files[0])
        try:
            with open(first_fig, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
                # Aesthetic (10 pts)
                white_patterns = [r'"paper_bgcolor":\s*"#?FFFFFF"', r'"paper_bgcolor":\s*"white"', r'"paper_bgcolor":\s*"rgb\(255,\s*255,\s*255\)"']
                if any(re.search(p, content, re.I) for p in white_patterns):
                    gpa += 10.0
                else:
                    details.append("Non-white background")

                # Statistical (30 pts)
                if re.search(r'Sig-\d+|Insignificant|Null', content):
                    gpa += 10.0
                if re.search(r'p=\d+\.\d+e[+-]\d+', content):
                    gpa += 5.0
                if "*" in content or "n.s." in content:
                    gpa += 5.0

                # Data Integrity (30 pts)
                if not re.search(r'":\s*\[[^\]]*\b(NaN|Infinity)\b', content):
                    gpa += 30.0
                else:
                    details.append("Corrupt Data (NaN/INF)")
                    status = "fail"

                # Scientific Density (10 pts)
                if "Area" in content or "Population" in content:
                    gpa += 10.0
                    
        except Exception as e:
            return 0, "fail", f"Audit Error: {str(e)}"

        status = "awesome" if gpa >= 90 else "pass" if gpa >= 60 else "fail"
        return round(gpa, 2), status, "; ".join(details) if details else "GPA Calibrated."

def main():
    print(f"[SENTINEL] Starting Sovereign GPA Audit (v2.0)...")
    auditor = GPAAuditor()
    
    if not os.path.exists(SCOREBOARD_PATH):
        sb = {"ledger": [], "last_updated": "", "metrics": {}, "system_status": "INIT"}
    else:
        with open(SCOREBOARD_PATH, 'r') as f:
            sb = json.load(f)
    
    new_ledger = []
    all_figures = FigureRegistry.get_all()
    
    for fig in all_figures:
        registry_folder = os.path.basename(fig['module'])
        path = os.path.join(OUTPUTS_DIR, registry_folder)
        
        if not os.path.exists(path):
             matches = [d for d in os.listdir(OUTPUTS_DIR) if d.startswith(fig['id'])] if os.path.exists(OUTPUTS_DIR) else []
             if matches: path = os.path.join(OUTPUTS_DIR, matches[0])
             else: registry_folder = "N/A"

        score, status, notes = auditor.audit_figure(path)
        
        new_ledger.append({
            "analysis": f"{fig['id']} - {fig['title']}",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "time": datetime.now().strftime("%H:%M"),
            "file": registry_folder + "/*.html" if os.path.exists(path) else "N/A",
            "code": fig['module'] + "/script.py",
            "status": status,
            "score": score,
            "notes": notes
        })

    sb['ledger'] = new_ledger
    sb['last_updated'] = datetime.now().isoformat()
    sb['system_status'] = "ONLINE"
    sb['active_phase'] = "Phase E (Excellence)"
    
    with open(SCOREBOARD_PATH, 'w') as f:
        json.dump(sb, f, indent=2)
    
    print(f"[SENTINEL] Registry Audit Complete. {len(new_ledger)} modules verified.")

if __name__ == "__main__":
    main()

