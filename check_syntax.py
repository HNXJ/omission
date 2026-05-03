import os
import sys
import py_compile
from pathlib import Path

def run_syntax_audit():
    """
    Performs a comprehensive, repo-wide syntax audit.
    Enforces compile-before-run doctrine for all active control plane files.
    """
    root = Path(__file__).parent
    targets = [
        root / "src",
        root / "dashboard" / "sync_manifest.py",
        root / "check_syntax.py"
    ]
    
    total_checked = 0
    errors = 0
    
    print(f"[action] Starting Repo-Wide Syntax Audit...")
    
    for target in targets:
        if not target.exists():
            continue
            
        if target.is_file():
            files = [target]
        else:
            files = target.rglob("*.py")
            
        for py_file in files:
            if "__pycache__" in str(py_file):
                continue
            
            total_checked += 1
            try:
                py_compile.compile(str(py_file), doraise=True)
            except py_compile.PyCompileError as e:
                print(f"[error] SYNTAX FAIL: {py_file.relative_to(root)}")
                print(f"        {e.msg}")
                errors += 1
            except Exception as e:
                print(f"[warning] UNEXPECTED FAIL: {py_file.relative_to(root)} - {e}")
                errors += 1

    print(f"--------------------------------------------------")
    if errors == 0:
        print(f"[success] Audit Complete. {total_checked} files passed.")
        sys.exit(0)
    else:
        print(f"[failed] Audit Failed. {errors} errors found in {total_checked} files.")
        sys.exit(1)

if __name__ == "__main__":
    run_syntax_audit()
