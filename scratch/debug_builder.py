import sys
from pathlib import Path

REPO_ROOT = Path("D:/drive/omission")
output_bases = [
    REPO_ROOT / "outputs" / "oglo-8figs",
    REPO_ROOT.parent / "outputs" / "oglo-8figs"
]

fig_id = "f007"

for base in output_bases:
    print(f"Checking base: {base}")
    if not base.exists():
        print(f"Base does not exist: {base}")
        continue
    matches = [d for d in base.iterdir() if d.is_dir() and d.name.startswith(fig_id)]
    print(f"Matches for {fig_id}: {matches}")
