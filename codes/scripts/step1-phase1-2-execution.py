
import sys
import os
import glob
import re
import json
import numpy as np
import plotly.graph_objects as go
from functions.omission_hierarchy_utils import extract_unit_traces, baseline_correct, compute_area_mmff, AREA_ORDER

def main():
    # 1. Identify sessions
    nwb_files = glob.glob('data/sub-*_ses-*_rec.nwb')
    session_ids = [re.search(r'ses-(\d+)', f).group(1) for f in nwb_files]
    print(f"Found {len(session_ids)} sessions: {session_ids}")

    all_unit_data = {}

    # 2. Extract traces session by session
    for ses in session_ids:
        print(f"Processing session {ses}...")
        try:
            ses_traces = extract_unit_traces(ses)
            ses_traces = baseline_correct(ses_traces)
            all_unit_data.update(ses_traces)
        except Exception as e:
            print(f"  Error processing session {ses}: {e}")

    print(f"Total units extracted: {len(all_unit_data)}")

    # 3. Compute Area Averaged PSTHs (Figure 1)
    print("Computing Area Averaged PSTHs...")
    area_psths = {area: {cond: [] for cond in ['RRRR', 'RXRR', 'RRXR', 'RRRX']} for area in AREA_ORDER}
    for unit_key, data in all_unit_data.items():
        area = data['area']
        for cond in data['traces']:
            if 'fr_baselined' in data['traces'][cond]:
                area_psths[area][cond].append(data['traces'][cond]['fr_baselined'])

    avg_psths = {area: {} for area in AREA_ORDER}
    for area in AREA_ORDER:
        for cond in area_psths[area]:
            if area_psths[area][cond]:
                avg_psths[area][cond] = np.mean(area_psths[area][cond], axis=0).tolist()
            else:
                avg_psths[area][cond] = []

    # 4. Compute MMFF (Figure 3)
    print("Computing MMFF (Phase 2)...")
    mmff_results, mmff_time = compute_area_mmff(all_unit_data)
    
    # Convert mmff_results to serializable (handle NaNs)
    mmff_serializable = {}
    for area in mmff_results:
        mmff_serializable[area] = {}
        for cond in mmff_results[area]:
            trace = mmff_results[area][cond]
            # Replace NaNs with None for JSON
            mmff_serializable[area][cond] = [x if not np.isnan(x) else None for x in trace]

    # 5. Save results
    os.makedirs('checkpoints', exist_ok=True)
    with open('checkpoints/step1_psth_traces.json', 'w') as f:
        json.dump(avg_psths, f)
    
    with open('checkpoints/step1_mmff_traces.json', 'w') as f:
        json.dump({
            'time': mmff_time.tolist(),
            'results': mmff_serializable
        }, f)
    
    print("Results saved to checkpoints/step1_psth_traces.json and checkpoints/step1_mmff_traces.json")

    # 6. Generate Summary Plots (Optional but good for validation)
    print("Generating validation plots...")
    os.makedirs('figures/step1', exist_ok=True)
    time_axis = np.linspace(-1000, 5000, 6000)
    
    for area in AREA_ORDER:
        if not avg_psths[area]['RRRR']: continue
        
        fig = go.Figure()
        for cond in ['RRRR', 'RXRR']:
            if avg_psths[area][cond]:
                fig.add_trace(go.Scatter(x=time_axis, y=avg_psths[area][cond], mode='lines', name=cond))
        
        fig.update_layout(title=f"Grand Average PSTH: {area}", xaxis_title="Time (ms)", yaxis_title="Baseline-Subtracted FR (Hz)")
        fig.write_html(f"figures/step1/{area}_psth_validation.html")

if __name__ == '__main__':
    main()
