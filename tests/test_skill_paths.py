import os
import re
from pathlib import Path

def test_skill_paths():
    repo_root = Path(r"D:\drive\omission")
    skills_dir = repo_root / ".gemini" / "skills"
    
    if not skills_dir.exists():
        print("No skills directory found.")
        return

    failed = False
    
    # Regex to find standard markdown file links like [name](file:///D:/drive/omission/path/to/file)
    link_pattern = re.compile(r'\[.*?\]\(file:///(.*?)\)')
    
    for skill_dir in skills_dir.iterdir():
        if not skill_dir.is_dir():
            continue
            
        skill_file = skill_dir / "SKILL.md"
        if not skill_file.exists():
            continue
            
        with open(skill_file, "r", encoding="utf-8") as f:
            content = f.read()
            
        links = link_pattern.findall(content)
        for link in links:
            # Handle Windows paths by replacing forward slashes with backslashes
            if "D:/drive/omission" in link:
                normalized_path = Path(link.replace("D:/drive/omission", "D:\\drive\\omission"))
                if not normalized_path.exists():
                    print(f"FAIL: {skill_dir.name} references non-existent path: {normalized_path}")
                    failed = True

    if failed:
        print("Test failed: Some skills reference non-existent paths.")
        exit(1)
    else:
        print("Success: All referenced paths in active skills exist.")
        exit(0)

if __name__ == "__main__":
    test_skill_paths()
