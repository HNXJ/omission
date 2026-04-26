import os, re

skills_dir = r'D:\drive\omission\.gemini\skills'
skill_dirs = [d for d in os.listdir(skills_dir) if os.path.isdir(os.path.join(skills_dir, d))]

for s in skill_dirs:
    path = os.path.join(skills_dir, s, 'SKILL.md')
    if not os.path.exists(path): continue
    
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    fm_match = re.match(r'---\nname: (.*?)\n---\n(.*)', content, re.DOTALL)
    if fm_match:
        name = fm_match.group(1)
        body = fm_match.group(2)
    else:
        name = s
        body = content
        
    if '## 1. Problem' in body:
        continue
        
    # Build the robust 5-step format
    new_body = f"""# {name}

## 1. Problem
This skill encompasses the legacy instructions for {name}.
Legacy Purpose/Info:
{body.strip()}

## 2. Solution Architecture
Executes the analytical pipeline using the standardized Omission hierarchy.
- **Input**: NWB data or Numpy arrays via DataLoader.
- **Output**: Interactive HTML/SVG figures saved to `D:/drive/outputs/oglo-8figs/`.

## 3. Skills/Tools
- Python 3.14
- canonical LFP/Spike loaders (`src/analysis/io/loader.py`)
- OmissionPlotter (`src/analysis/visualization/plotting.py`)
- **Code/DOI Reference**: Internal Codebase (src)

## 4. Version Control
- All changes must be committed.
- Comply with the GAMMA protocol (Commit-Pull-Push after every action).

## 5. Rules/Cautions
- Ensure strict adherence to the Madelane Golden Dark aesthetic.
- Folders must be named using dashes (e.g., `f0xx-keyword`), NO underscores.
- Only run on 'Stable-Plus' neuronal populations.
"""
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(f"---\nname: {name}\n---\n{new_body}")

print("All skills reformatted to the 5-step standard.")
