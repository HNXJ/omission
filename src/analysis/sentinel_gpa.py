import os
import json
import re
import numpy as np
from datetime import datetime
import sys

# Ensure src is in path
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from src.analysis.registry import FigureRegistry

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
OUTPUTS_DIR = os.path.join(REPO_ROOT, '../outputs/oglo-8figs')
SCOREBOARD_PATH = os.path.join(REPO_ROOT, 'dashboard/src/data/scoreboard.json')

class GPAAuditor:
    def __init__(self):
        self.criteria = {
            "AESTHETIC": {
                "white_bg": 2.0, "font_scaling": 2.0, "legend_pos": 2.0, 
                "color_validity": 2.0, "grid_clarity": 2.0
            },
            "STATISTICAL": {
                "sig_tier_presence": 10.0, "p_value_reporting": 5.0,
                "stars_mapping": 5.0, "test_identification": 5.0,
                "n_counts_verified": 5.0
            },
            "DATA_INTEGRITY": {
                "nan_absence": 10.0, "inf_absence": 10.0, 
                "zero_variance_guard": 5.0, "range_clipping": 5.0
            },
            "DOCUMENTATION": {
                "readme_presence": 5.0, "methodology_detail": 5.0,
                "data_contract_ref": 5.0, "src_link_validity": 5.0
            },
            "SCIENTIFIC_DENSITY": {
                "multi_area_comparison": 10.0, "temporal_resolution": 5.0,
                "baseline_reporting": 5.0
            }
        }
        self.total_weight = sum(sum(cat.values()) for cat in self.criteria.values())

    def audit_html(self, content):
        score = 0.0
        details = []

        # 1. Aesthetics
        if re.search(r'"paper_bgcolor":\s*"#?FFFFFF"|white|rgb\(255,\s*255,\s*255\)', content, re.I):
            score += self.criteria["AESTHETIC"]["white_bg"]
        
        # 2. Statistical (Look for the new S_k tier format)
        if re.search(r'Sig-\d+|Insignificant|Null', content):
            score += self.criteria["STATISTICAL"]["sig_tier_presence"]
            details.append("Significance Tier detected")
        if re.search(r'p=\d+\.\d+e[+-]\d+', content):
            score += self.criteria["STATISTICAL"]["p_value_reporting"]
        if "*" in content or "n.s." in content:
             score += self.criteria["STATISTICAL"]["stars_mapping"]

        # 3. Data Integrity
        if not re.search(r'":\s*\[[^\]]*\b(NaN|Infinity)\b', content):
            score += self.criteria["DATA_INTEGRITY"]["nan_absence"]
            score += self.criteria["DATA_INTEGRITY"]["inf_absence"]
        else:
            details.append("NaN/INF detected in trace data")

        return score, details

    def run_audit(self):
        print(f"[GPA] Starting Sovereign GPA Audit (v2.0)...")
        all_figs = FigureRegistry.get_all()
        ledger = []

        for fig in all_figs:
            folder_name = os.path.basename(fig['module'])
            path = os.path.join(OUTPUTS_DIR, folder_name)
            
            # Fallback to heuristic
            if not os.path.exists(path):
                matches = [d for d in os.listdir(OUTPUTS_DIR) if d.startswith(fig['id'])] if os.path.exists(OUTPUTS_DIR) else []
                if matches: path = os.path.join(OUTPUTS_DIR, matches[0])
            
            gpa = 0.0
            status = "queued"
            notes = "Analysis pending."
            
            if os.path.exists(path):
                # Base Docs Score
                if os.path.exists(os.path.join(path, 'README.md')):
                    gpa += 20.0 # Aggregate docs score
                
                htmls = [f for f in os.listdir(path) if f.endswith('.html')]
                if htmls:
                    with open(os.path.join(path, htmls[0]), 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        content_score, content_details = self.audit_html(content)
                        gpa += content_score
                        notes = "; ".join(content_details) if content_details else "Compliant."
                
                # Normalize to 100
                status = "awesome" if gpa >= 90 else "pass" if gpa >= 70 else "fail"
                
            ledger.append({
                "analysis": f"{fig['id']} - {fig['title']}",
                "status": status,
                "score": round(gpa, 2),
                "notes": notes,
                "date": datetime.now().strftime("%Y-%m-%d")
            })

        return ledger

if __name__ == "__main__":
    auditor = GPAAuditor()
    results = auditor.run_audit()
    print(json.dumps(results, indent=2))
