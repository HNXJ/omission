
from pathlib import Path

deprecated_dir = Path('omission/codes/scripts/deprecated/')
deprecation_notice = """# Deprecated
# This script is deprecated and is retained for reference only.

raise NotImplementedError("Deprecated script retained for reference only")
"""

for file_path in deprecated_dir.glob('*.py'):
    with open(file_path, 'w') as f:
        f.write(deprecation_notice)
    print(f"Cleaned {file_path}")

print("Finished cleaning deprecated scripts.")
