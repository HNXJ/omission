
from pathlib import Path

files_to_clean = [
    'omission/codes/scripts/dev/layer-mapping-omission.py',
    'omission/codes/scripts/dev/vflip2-mapping.py'
]

deprecation_notice = """# Local-only
# This script is deprecated and is retained for reference only.

raise NotImplementedError("Deprecated script retained for reference only")
"""

for file_path in files_to_clean:
    with open(file_path, 'w') as f:
        f.write(deprecation_notice)
    print(f"Cleaned {file_path}")

print("Finished cleaning dev scripts.")
