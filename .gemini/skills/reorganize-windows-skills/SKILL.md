---
name: reorganize-windows-skills
description: Documents and guides the organization of Gemini CLI skills within a Windows environment, emphasizing a categorized directory structure and robust pathing practices for compatibility.
---
# SKILL: reorganize-windows-skills

## Description
This skill outlines the standardized organizational schema for Gemini CLI skills tailored for Windows environments. Its primary purpose is to prevent namespace collisions, enhance discoverability, and ensure cross-platform compatibility by enforcing a categorized directory structure and mandating the use of `os.path` or `pathlib` for all file system interactions. This schema facilitates dynamic skill loading and management, particularly important as the CLI's capabilities expand through auto-registered skills.

## Core Mandates for Skill Developers & Auto-Registration
1.  **Categorized Directory Structure**: All skills must reside within one of the following domain-specific subdirectories under `%USERPROFILE%\workspace\Computational\cli_tools` (or the current workspace's `.gemini/skills/` equivalent for project-specific skills).
    *   **`/vision_ops`**: Skills related to visual processing, image generation, asset optimization, and display.
    *   **`/infrastructure`**: Skills for managing the CLI's underlying infrastructure, local modes, model warehouses, and resolving model aliases.
    *   **`/memory_and_logic`**: Skills pertaining to memory management, meditation execution, and synchronization logic.
    *   **`/git_and_ops`**: Skills for Git operations, repository synchronization, and ledger updates.
    *   **`/interaction`**: Skills managing user interactions, decision routing, and advanced communication protocols.

2.  **Windows-Compatible Pathing (CRITICAL)**:
    *   **Absolute Paths**: Always construct file paths using `os.path.join()` or `pathlib.Path`.
    *   **Environment Variables**: Map `~/workspace/` references to `os.path.join(os.environ["USERPROFILE"], "workspace")` for consistency.
    *   **Directory Junctions**: When creating symbolic links, use Windows Directory Junctions via `subprocess.run(["cmd.exe", "/c", "mklink", "/J", target_alias_path, warehouse_source_path])` instead of `os.symlink` to avoid privilege issues.

3.  **Skill Auto-Registration**:
    *   The `auto_register_skills` function (e.g., as part of the `/meditate` command) must incorporate a classification mechanism (e.g., an LLM call) to semantically categorize newly generated skills into the appropriate subdirectory. This ensures new tools are placed correctly upon creation, adhering to the schema.

4.  **Execution Environment Guardrail**:
    *   When a skill relies on shell execution (e.g., starting a server), verify it invokes the correct Windows executable (`.exe`, `.cmd`, `.bat`) rather than assuming Unix-like shell scripts (`.sh`).

5.  **Scientific Code Safety**:
    *   Before performing any visual or mathematical analysis, strictly validate all file paths using `os.path.exists()` to ensure data integrity and prevent errors from outdated or missing files.

## When to Use This Skill
This skill serves as a reference for:
*   Creating new Python-based CLI tools and ensuring they conform to the Windows-compatible organizational and coding standards.
*   Debugging path-related issues in CLI tools running on Windows.
*   Understanding the expected structure for dynamically loaded skills.
*   Modifying the CLI's skill auto-registration logic.

## Example (Conceptual - No direct execution)

```python
# Conceptual example demonstrating Windows-compatible pathing in a skill.
import os
from pathlib import Path

def get_user_workspace_path():
    """Returns the user's workspace path using os.environ and os.path.join."""
    user_profile = os.environ.get("USERPROFILE")
    if user_profile:
        return os.path.join(user_profile, "workspace")
    else:
        raise EnvironmentError("USERPROFILE environment variable not set.")

def save_skill_file(skill_name, content, category_subdir):
    """
    Simulates saving a new skill file into the categorized structure.
    This example uses a conceptual `cli_tools` directory within the workspace.
    """
    try:
        cli_tools_base = Path(get_user_workspace_path()) / "Computational" / "cli_tools"
        target_dir = cli_tools_base / category_subdir
        
        # Ensure target directory exists, robustly handling Windows paths
        target_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = target_dir / f"{skill_name}.py"
        with open(file_path, "w") as f:
            f.write(content)
        print(f"Skill '{skill_name}.py' saved to: {file_path}")
        
        # Example of validating a file path before use
        if os.path.exists(file_path):
            print(f"Path '{file_path}' exists. Ready for loading.")
        else:
            print(f"Error: Path '{file_path}' does not exist after creation.")

    except Exception as e:
        print(f"Failed to save skill: {e}")

# Simulate saving a new 'my_vision_tool' skill
# save_skill_file(
#     "my_vision_tool",
#     "print('Hello from vision_ops!')",
#     "vision_ops"
# )

# Simulate creating a directory junction (conceptual, actual execution requires subprocess)
def create_mock_junction(junction_point, target_folder):
    """Conceptual demonstration of mklink /J usage."""
    # In a real scenario, this would involve:
    # import subprocess
    # subprocess.run(["cmd.exe", "/c", "mklink", "/J", str(junction_point), str(target_folder)])
    print(f"
Conceptual: Creating Directory Junction '{junction_point}' pointing to '{target_folder}'")

# Example: create_mock_junction(
#     Path(get_user_workspace_path()) / "ModelWarehouse" / "MyModelAlias",
#     Path("D:/LocalModels/MyModelV2")
# )
```