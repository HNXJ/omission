# core
import os
import json
import re
from pathlib import Path

def generate_manifest():
    """
    Scans output and progress directories to generate a frontend manifest.
    Uses /@fs/ prefix for Vite local serving.
    """
    print(f"""[action] Starting manifest generation...""")
    
    output_root = Path("D:/drive/outputs/oglo-8figs")
    print(f"""[action] Setting output root to {output_root}...""")
    
    progress_root = Path("D:/drive/progress-report")
    print(f"""[action] Setting progress root to {progress_root}...""")
    
    manifest = {
        "figures": [],
        "reports": []
    }
    print(f"""[action] Initialized manifest structure...""")

    # Scan figures
    if output_root.exists():
        print(f"""[action] Scanning figures in {output_root}...""")
        for fig_dir in sorted(output_root.iterdir()):
            if fig_dir.is_dir():
                print(f"""[action] Processing figure directory: {fig_dir.name}...""")
                # Extract numeric ID for phase mapping
                fig_num_match = re.search(r'f(\d+)', fig_dir.name)
                fig_phase = 1
                if fig_num_match:
                    num = int(fig_num_match.group(1))
                    if num <= 4: fig_phase = 1
                    elif num <= 10: fig_phase = 2
                    elif num <= 20: fig_phase = 3
                    elif num <= 30: fig_phase = 4
                    else: fig_phase = 5
                
                fig_data = {
                    "id": fig_dir.name,
                    "title": fig_dir.name.replace("-", " ").title(),
                    "phase": fig_phase,
                    "baseUrl": f"/@fs/{fig_dir.as_posix()}",
                    "files": [f.name for f in fig_dir.glob("*.html")],
                    "has_readme": (fig_dir / "README.md").exists()
                }
                manifest["figures"].append(fig_data)
                print(f"""[action] Added figure data for {fig_dir.name}...""")

    # Scan reports
    if progress_root.exists():
        print(f"""[action] Scanning reports in {progress_root}...""")
        for report_file in sorted(progress_root.glob("*.md"), reverse=True):
            print(f"""[action] Processing report: {report_file.name}...""")
            report_data = {
                "id": report_file.stem,
                "title": report_file.stem.replace("progress-report-", ""),
                "url": f"/@fs/{report_file.as_posix()}"
            }
            manifest["reports"].append(report_data)
            print(f"""[action] Added report data for {report_file.name}...""")

    # Save manifest
    target_path = Path("dashboard/src/data/manifest.json")
    target_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(target_path, "w") as f:
        json.dump(manifest, f, indent=2)
        print(f"""[action] Wrote manifest to {target_path}...""")

if __name__ == "__main__":
    generate_manifest()
