from codes.config.paths import PROJECT_ROOT

import os
import pandas as pd

NWB_DIR = PROJECT_ROOT
DATA_DIR = os.path.join(NWB_DIR, 'data')

def update_summary_table():
    if not os.path.exists(DATA_DIR):
        print("Data directory not found. Skipping granular summary.")
        return

    nwb_files = [f for f in os.listdir(NWB_DIR) if f.endswith('.nwb')]
    granular_status = []

    for filename in nwb_files:
        session_id = filename.split('_')[1].split('-')[1]
        
        # Check behavioral
        behav_files = [f for f in os.listdir(DATA_DIR) if f.startswith(f'ses{session_id}-behavioral')]
        behav_status = f"{len(behav_files)}/12 ✅" if len(behav_files) > 0 else "⏳"
        
        # Check LFP per probe
        lfp_p0 = [f for f in os.listdir(DATA_DIR) if f.startswith(f'ses{session_id}-probe0-lfp')]
        lfp_p1 = [f for f in os.listdir(DATA_DIR) if f.startswith(f'ses{session_id}-probe1-lfp')]
        lfp_p2 = [f for f in os.listdir(DATA_DIR) if f.startswith(f'ses{session_id}-probe2-lfp')]
        
        lfp_status = []
        if len(lfp_p0) > 0: lfp_status.append(f"P0 ({len(lfp_p0)})")
        if len(lfp_p1) > 0: lfp_status.append(f"P1 ({len(lfp_p1)})")
        if len(lfp_p2) > 0: lfp_status.append(f"P2 ({len(lfp_p2)})")
        lfp_final = ", ".join(lfp_status) if lfp_status else "⏳"
        
        # Check Units per probe
        spk_p0 = [f for f in os.listdir(DATA_DIR) if f.startswith(f'ses{session_id}-units-probe0-spk')]
        spk_p1 = [f for f in os.listdir(DATA_DIR) if f.startswith(f'ses{session_id}-units-probe1-spk')]
        spk_p2 = [f for f in os.listdir(DATA_DIR) if f.startswith(f'ses{session_id}-units-probe2-spk')]
        
        spk_status = []
        if len(spk_p0) > 0: spk_status.append(f"P0 ({len(spk_p0)})")
        if len(spk_p1) > 0: spk_status.append(f"P1 ({len(spk_p1)})")
        if len(spk_p2) > 0: spk_status.append(f"P2 ({len(spk_p2)})")
        spk_final = ", ".join(spk_status) if spk_status else "⏳"

        granular_status.append({
            "Session": session_id,
            "Behav (12)": behav_status,
            "LFP (12/probe)": lfp_final,
            "Units (12/probe)": spk_final,
            "Format": "Trial_Chan_Sample",
            "Window": "6000ms"
        })

    df = pd.DataFrame(granular_status)
    md_table = df.to_markdown(index=False)
    
    summary_path = os.path.join(NWB_DIR, 'DATA_AVAILABILITY_SUMMARY.md')
    
    with open(summary_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    marker = "### 📦 Granular .npy Data Store"
    if marker in content:
        content = content.split(marker)[0].strip()
        
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write(content)
        f.write(f"\n\n{marker}\n")
        f.write("Files organized as `ses<ID>-<probe>-<modality>-<condition>.npy` in the `data/` folder.\n\n")
        f.write(md_table)
    
    print(f"\nSummary table updated at {summary_path}")

if __name__ == "__main__":
    update_summary_table()
