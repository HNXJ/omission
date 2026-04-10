
import ast
from pathlib import Path

def check_syntax(file_path):
    """
    Checks if a Python file has valid syntax.
    Returns True if syntax is valid, False otherwise.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            ast.parse(f.read())
        return True
    except (SyntaxError, UnicodeDecodeError) as e:
        print(f"Syntax error in {file_path}: {e}")
        return False

pipelines_dir = Path('omission/codes/scripts/pipelines/')
for file_path in pipelines_dir.glob('*.py'):
    print(f"Checking {file_path}...")
    check_syntax(file_path)

print("Finished checking pipelines scripts.")
