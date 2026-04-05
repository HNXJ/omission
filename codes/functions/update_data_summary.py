import os
import pandas as pd
import re
import numpy as np
from pathlib import Path

DATA_DIR = Path(__file__).parents[2] / "data"
SUMMARY_PATH = Path(__file__).parents[2] / "DATA_AVAILABILITY_SUMMARY.md"

def get_session_id(filename):
    match = re.search(r'ses-(\d{6})', filename)
    if match: return match.group(1)
    match = re.search(r'ses(\d{6})', filename)
    if match: return match.group(1)
    return None

def update_summary():
    if not os.path.exists(DATA_DIR):
        print("Data directory not found.")
        return

    files = os.listdir(DATA_DIR)
    
    # Identify all session IDs from NWB files
    nwb_files = [f for f in files if f.endswith('.nwb')]
    sessions = sorted(list(set([get_session_id(f) for f in nwb_files if get_session_id(f)])))
    
    if not sessions:
        # If no NWBs, try to get from NPYs
        sessions = sorted(list(set([get_session_id(f) for f in files if get_session_id(f)])))

    print(f"Detected sessions: {sessions}")

    granular_status = []
    multimodal_status = []

    for sid in sessions:
        # --- Granular Status ---
        behav_files = [f for f in files if f.startswith(f'ses{sid}-behavioral')]
        behav_count = len(behav_files)
        behav_str = f"{behav_count}/12 ✅" if behav_count >= 12 else (f"{behav_count}/12 ⏳" if behav_count > 0 else "⏳")
        
        lfp_probes = {}
        spk_probes = {}
        for p in [0, 1, 2]:
            lfp_f = [f for f in files if f.startswith(f'ses{sid}-probe{p}-lfp')]
            if lfp_f: lfp_probes[p] = len(lfp_f)
            
            spk_f = [f for f in files if f.startswith(f'ses{sid}-units-probe{p}-spk')]
            if spk_f: spk_probes[p] = len(spk_f)
            
        lfp_str = ", ".join([f"P{p} ({n})" for p, n in lfp_probes.items()]) if lfp_probes else "⏳"
        spk_str = ", ".join([f"P{p} ({n})" for p, n in spk_probes.items()]) if spk_probes else "⏳"

        granular_status.append({
            "Session": sid,
            "Behav (12)": behav_str,
            "LFP (12/probe)": lfp_str,
            "Units (12/probe)": spk_str,
            "Format": "Trial_Chan_Sample",
            "Window": "6000ms"
        })

        # --- Multi-Modal Status ---
        # (Assuming Multi-Modal refers to presence of any data for that modality)
        has_spk = "✅" if spk_probes else "⏳"
        lfp_probe_count = len(lfp_probes)
        has_lfp = f"{lfp_probe_count} Probes ✅" if lfp_probe_count > 0 else "⏳"
        has_behav = "✅" if behav_count > 0 else "⏳"
        
        # Try to get SPK shape from first available unit file
        spk_shape = "N/A"
        if spk_probes:
            # Pick first available spk file
            spk_file = next(f for f in files if f.startswith(f'ses{sid}-units-probe'))
            try:
                arr = np.load(os.path.join(DATA_DIR, spk_file), mmap_mode='r')
                spk_shape = str(arr.shape)
            except:
                pass

        multimodal_status.append({
            "Session": sid,
            "SPK": has_spk,
            "LFP": has_lfp,
            "BEHAV": has_behav,
            "SPK Shape [T, U, S]": spk_shape,
            "Window (ms)": "6000"
        })

    # Read existing summary
    with open(SUMMARY_PATH, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # We will rebuild the two bottom tables
    header_lines = []
    for line in lines:
        if "### 📦 Multi-Modal .npy Array Status" in line:
            break
        header_lines.append(line)
    
    new_content = "".join(header_lines).strip()
    
    new_content += "\n\n### 📦 Multi-Modal .npy Array Status\n"
    new_content += "All arrays are formatted as `[Trial x Channel/Unit x Sample]`.\n\n"
    new_content += pd.DataFrame(multimodal_status).to_markdown(index=False)
    
    new_content += "\n\n### 📦 Granular .npy Data Store\n"
    new_content += "Files organized as `ses<ID>-<probe>-<modality>-<condition>.npy` in the `data/` folder.\n\n"
    new_content += pd.DataFrame(granular_status).to_markdown(index=False)
    
    with open(SUMMARY_PATH, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"Updated {SUMMARY_PATH}")

if __name__ == "__main__":
    update_summary()
