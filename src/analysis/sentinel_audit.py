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
        
        # Sort by size to pick the primary figure (not indices or small plots)
        html_files.sort(key=lambda x: os.path.getsize(os.path.join(folder_path, x)), reverse=True)
        first_fig = os.path.join(folder_path, html_files[0])
        try:
            with open(first_fig, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
                # Aesthetic (10 pts)
                white_patterns = [r'"paper_bgcolor":\s*"#?FFFFFF"', r'"paper_bgcolor":\s*"white"']
                if any(re.search(p, content, re.I) for p in white_patterns):
                    gpa += 10.0
                else:
                    details.append("Non-white background")

                # Statistical Proof (40 pts)
                # Tier detection (20) + P-value reporting (10) + Significance mapping (10)
                tier_match = re.search(r'Sig-\d+|Insignificant|Null', content)
                p_match = re.search(r'p=\d+\.\d+e[+-]\d+', content)
                stars_match = re.search(r'\*+|n\.s\.|Null', content)
                
                if tier_match: gpa += 20.0
                if p_match: gpa += 10.0
                if stars_match: gpa += 10.0
                
                if not tier_match:
                    details.append("Missing Statistical Tier")

                # Data Integrity (20 pts)
                if not re.search(r'":\s*\[[^\]]*\b(NaN|Infinity)\b', content):
                    gpa += 20.0
                else:
                    details.append("Corrupt Data (NaN/INF)")
                    status = "fail"

                # Scientific Density (10 pts)
                if any(term in content for term in ["Area", "Population", "Units", "Hierarchy"]):
                    gpa += 10.0
                else:
                    details.append("Low Scientific Density")
                    
        except Exception as e:
            return 0, "fail", f"Audit Error: {str(e)}"

        status = "awesome" if gpa >= 95 else "pass" if gpa >= 70 else "fail"
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
    
    print(f"\n{'='*100}")
    print(f"{'ANALYSIS':<30} | {'STATUS':<8} | {'SCORE':<6} | {'NOTES'}")
    print(f"{'-'*100}")
    for entry in new_ledger:
        print(f"{entry['analysis'][:30]:<30} | {entry['status']:<8} | {entry['score']:<6} | {entry['notes']}")
    print(f"{'='*100}\n")
    
    avg_gpa = sum(e['score'] for e in new_ledger) / len(new_ledger) if new_ledger else 0
    print(f"[SENTINEL] Registry Audit Complete. {len(new_ledger)} modules verified. Average GPA: {avg_gpa:.2f}")

if __name__ == "__main__":
    main()

