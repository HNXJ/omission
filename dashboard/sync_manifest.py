import os
import json
from pathlib import Path

def sync():
    outputs_dir = Path(r'D:\drive\outputs\oglo-8figs')
    manifest_path = Path(r'D:\drive\omission\dashboard\src\data\manifest.json')
    
    if not outputs_dir.exists():
        print(f"Error: {outputs_dir} does not exist.")
        return

    figures = []
    
    # Sort directories by f-number
    dirs = sorted([d for d in outputs_dir.iterdir() if d.is_dir()])
    
    for d in dirs:
        folder_name = d.name
        # Expecting fxxx-name
        if not folder_name.startswith('f'):
            continue
            
        fig_id = folder_name
        title = folder_name.replace('-', ' ').title()
        
        # Files in folder
        files = sorted([f.name for f in d.iterdir() if f.is_file() and f.suffix in ['.html', '.svg', '.png']])
        has_readme = (d / "README.md").exists()
        
        figures.append({
            "id": fig_id,
            "title": title,
            "baseUrl": f"/@fs/{d.as_posix()}",
            "files": files,
            "has_readme": has_readme
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
        "reports": reports
    }
    
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, indent=2)
        
    print(f"Manifest synced with {len(figures)} figures.")

if __name__ == "__main__":
    sync()
