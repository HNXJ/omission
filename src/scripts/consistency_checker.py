import os
import re
import glob

def check_consistency():
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    skills_dir = os.path.join(repo_root, '.gemini', 'skills')
    
    errors = 0
    checked_files = 0
    
    # Find all SKILL.md
    for root, _, files in os.walk(skills_dir):
        for file in files:
            if file == "SKILL.md":
                checked_files += 1
                filepath = os.path.join(root, file)
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                # Look for file paths like src/... or context/...
                paths = re.findall(r'`(src/.*?|context/.*?)`', content)
                for path in paths:
                    full_path = os.path.join(repo_root, os.path.normpath(path))
                    if not os.path.exists(full_path):
                        print(f"Error: Referenced file not found: {path} in {filepath}")
                        errors += 1
                        
                # Look for skill cross-references like [skill-name]
                refs = re.findall(r'\[([^\]]+)\]\(.*?skill\.md\)', content, flags=re.IGNORECASE)
                for ref in refs:
                    ref_path = os.path.join(skills_dir, ref, 'SKILL.md')
                    if not os.path.exists(ref_path):
                        print(f"Error: Broken cross-skill link to {ref} in {filepath}")
                        errors += 1

    print(f"Checked {checked_files} skill files. Found {errors} errors.")
    if errors > 0:
        return False
    return True

if __name__ == "__main__":
    print("Running consistency checker...")
    check_consistency()