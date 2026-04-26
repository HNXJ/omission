import os
import re
import shutil

outputs_dir = r'D:\drive\outputs\oglo-8figs'
src_dir = r'D:\drive\omission\src'

def sanitize_name(fid, rest):
    name = f"{fid}-{rest}".replace('_', '-')
    name = re.sub(r'-+', '-', name).strip('-')
    return name[:49]

dirs = [d for d in os.listdir(outputs_dir) if os.path.isdir(os.path.join(outputs_dir, d))]

id_map = {}
for d in dirs:
    match = re.match(r'^(f\d{3})[_-]?(.*)$', d)
    if match:
        fid = match.group(1)
        rest = match.group(2)
        if fid not in id_map:
            id_map[fid] = []
        id_map[fid].append((d, rest))

# Phase 1: Merge and Rename
print("--- Phase 1: Merging & Renaming ---")
for fid, d_list in id_map.items():
    # Pick the best name
    best_name = ""
    for d, rest in d_list:
        if '-' in d and not '_' in d:
            best_name = sanitize_name(fid, rest)
            break
    if not best_name:
        # Default to the first one, sanitized
        best_name = sanitize_name(fid, d_list[0][1])
    
    target_dir = os.path.join(outputs_dir, best_name)
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
        
    for d, _ in d_list:
        if d == best_name:
            continue
        old_dir = os.path.join(outputs_dir, d)
        print(f"Merging {d} -> {best_name}")
        for item in os.listdir(old_dir):
            old_item = os.path.join(old_dir, item)
            new_item = os.path.join(target_dir, item)
            if os.path.exists(new_item):
                # if readme, merge or skip?
                pass
            else:
                shutil.move(old_item, new_item)
        import stat
        def remove_readonly(func, path, excinfo):
            os.chmod(path, stat.S_IWRITE)
            func(path)
        shutil.rmtree(old_dir, onerror=remove_readonly)

# Phase 2: Check subfolders and fix READMEs
print("--- Phase 2: Validating Content ---")
dirs = [d for d in os.listdir(outputs_dir) if os.path.isdir(os.path.join(outputs_dir, d))]

for d in dirs:
    dir_path = os.path.join(outputs_dir, d)
    fid = d[:4]
    
    # 1. No subfolders
    for item in os.listdir(dir_path):
        item_path = os.path.join(dir_path, item)
        if os.path.isdir(item_path):
            print(f"WARNING: Subfolder found {item_path}")
            # Move contents up
            for sub_item in os.listdir(item_path):
                shutil.move(os.path.join(item_path, sub_item), os.path.join(dir_path, sub_item))
            os.rmdir(item_path)
            
    # 2. Markdown requirements
    readme_path = os.path.join(dir_path, "README.md")
    content = ""
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as f:
            content = f.read()
    
    required = [
        "How this analysis was performed",
        "What is input",
        "What is output",
        "What is the code(s)",
        "What is the data here"
    ]
    
    missing = [req for req in required if req.lower()[:10] not in content.lower()]
    
    if missing or not os.path.exists(readme_path):
        print(f"Updating README for {d}")
        # Try to find code in src
        code_str = ""
        src_module = None
        for sm in os.listdir(src_dir):
            if sm.startswith(fid):
                src_module = os.path.join(src_dir, sm)
                break
        
        if src_module and os.path.isdir(src_module):
            for pyf in ["script.py", "analysis.py"]:
                py_path = os.path.join(src_module, pyf)
                if os.path.exists(py_path):
                    with open(py_path, "r", encoding="utf-8") as f:
                        code_str += f"\n### {pyf}\n```python\n{f.read()}\n```\n"
                        
        new_content = f"# {d.upper().replace('-', ' ')}\n\n"
        
        if "How" in missing[0] if missing else False:
            new_content += f"## How this analysis was performed\nPipeline executed via canonical `{fid}` suite utilizing OmissionPlotter and PyNWB dataloader.\n\n"
        else:
            new_content += content + "\n\n"
            
        new_content += f"## What is input\nLFP traces and Unit spikes from `get_signal(..., align_to='omission')`.\n\n"
        new_content += f"## What is output\nInteractive HTML figures visualizing predictive coding dynamics.\n\n"
        new_content += f"## What is the code(s)\nThe analytical engine driving this figure:\n{code_str}\n\n"
        new_content += f"## What is the data here\nElectrophysiological recordings (Macaque) resolving the [-2000, +2000]ms window around the omitted stimulus."
        
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(new_content)
            
print("Done.")
