from codes.config.paths import PROJECT_ROOT

import os
import numpy as np
import pandas as pd

NWB_DIR = PROJECT_ROOT
DATA_DIR = os.path.join(NWB_DIR, 'data')

def get_npy_shape(path):
    try:
        arr = np.load(path, mmap_mode='r')
        return arr.shape
    except:
        return None

def enrich_summary():
    if not os.path.exists(DATA_DIR):
        print("Data directory not found.")
        return

    nwb_files = sorted([f for f in os.listdir(NWB_DIR) if f.endswith('.nwb')])
    sessions = [f.split('_')[1].split('-')[1] for f in nwb_files]
    
    shape_data = []
    
    for sid in sessions:
        # We'll check for AAAB as a representative condition for shapes
        cond = "AAAB"
        
        # Behavioral Shape
        behav_path = os.path.join(DATA_DIR, f'ses{sid}-behavioral-{cond}.npy')
        behav_shape = get_npy_shape(behav_path)
        
        # LFP Shapes (check P0, P1, P2)
        lfp_shapes = []
        for p in [0, 1, 2]:
            path = os.path.join(DATA_DIR, f'ses{sid}-probe{p}-lfp-{cond}.npy')
            shape = get_npy_shape(path)
            if shape: lfp_shapes.append(f"P{p}: {shape}")
        
        # Unit Shapes (check P0, P1, P2)
        unit_shapes = []
        for p in [0, 1, 2]:
            path = os.path.join(DATA_DIR, f'ses{sid}-units-probe{p}-spk-{cond}.npy')
            shape = get_npy_shape(path)
            if shape: unit_shapes.append(f"P{p}: {shape}")
            
        shape_data.append({
            "Session": sid,
            "Behavioral [T, 4, S]": str(behav_shape) if behav_shape else "⏳",
            "LFP Probes [T, 128, S]": ", ".join(lfp_shapes) if lfp_shapes else "⏳",
            "Unit Probes [T, N, S]": ", ".join(unit_shapes) if unit_shapes else "⏳"
        })

    df_shapes = pd.DataFrame(shape_data)
    
    # Read current content
    summary_path = os.path.join(NWB_DIR, 'DATA_AVAILABILITY_SUMMARY.md')
    with open(summary_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    # Find insertion point or replace if exists
    new_lines = []
    skip = False
    for line in lines:
        if "### 📐 Detailed Array Shapes" in line:
            skip = True
        if skip and line.startswith("###") and "### 📐 Detailed Array Shapes" not in line:
            skip = False
        if not skip:
            new_lines.append(line)
            
    # Append the new table
    content = "".join(new_lines).strip()
    content += "\n\n### 📐 Detailed Array Shapes\n"
    content += "Detailed dimensional mapping for each session and probe. Format: `(Trials, Channels/Units, Samples)`.\n\n"
    content += df_shapes.to_markdown(index=False)
    content += "\n\n---\n*Last updated by Gemini CLI Auto-Summary Suite.*"
    
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Summary enriched with shapes at {summary_path}")

if __name__ == "__main__":
    enrich_summary()
