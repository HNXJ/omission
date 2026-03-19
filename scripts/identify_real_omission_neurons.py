"""
identify_real_omission_neurons.py: Detects "Real" omission neurons based on strict criteria:
1. Significant increase from Fixation (Baseline) during Omission window.
2. NO significant increase (or inhibition) from Fixation during Stimulus/Delay windows.
"""
import os
import numpy as np
import pandas as pd
from scipy.stats import ttest_rel
import glob

DATA_DIR = r'D:\Analysis\Omission\local-workspace\data'
OUTPUT_DIR = r'D:\Analysis\Omission\local-workspace\checkpoints'

# Sequence Logic: 
# 0-500: Fixation (True Baseline)
# 1000-3900: Sequence (Stimuli + Delays)
# 4000-4800: Omission Response
FIXATION_WIN = (0, 500)
SEQUENCE_WIN = (1000, 3900)
OMISSION_WIN = (4000, 4800)

SESSION_AREAS = {
    '230831': {'0': 'FEF', '1': 'MT', '2': 'V4'},
    '230901': {'0': 'PFC', '1': 'MT', '2': 'V3/V4'},
    '230720': {'0': 'V1/V2', '1': 'V3/V4'}
}

def detect_real_omission_units(session_id, probe_id):
    area = SESSION_AREAS[session_id].get(probe_id, 'unknown')
    print(f"Detecting 'Real' Omission Units: {session_id} P{probe_id} ({area})")
    
    omit_files = glob.glob(os.path.join(DATA_DIR, f'ses{session_id}-units-probe{probe_id}-spk-*X*.npy'))
    if not omit_files: return []

    real_omission_units = []
    
    for f_path in omit_files:
        cond = os.path.basename(f_path).split('-')[-1].replace('.npy', '')
        spikes = np.load(f_path, mmap_mode='r')
        n_trials, n_units, _ = spikes.shape
        
        for u in range(n_units):
            # Sum spikes per trial in each window
            fix_fr = np.sum(spikes[:, u, FIXATION_WIN[0]:FIXATION_WIN[1]], axis=1)
            seq_fr = np.sum(spikes[:, u, SEQUENCE_WIN[0]:SEQUENCE_WIN[1]], axis=1) / (SEQUENCE_WIN[1]-SEQUENCE_WIN[0]) * 500 # Normalize to 500ms
            omit_fr = np.sum(spikes[:, u, OMISSION_WIN[0]:OMISSION_WIN[1]], axis=1) / (OMISSION_WIN[1]-OMISSION_WIN[0]) * 500
            
            mean_fix = np.mean(fix_fr)
            mean_seq = np.mean(seq_fr)
            mean_omit = np.mean(omit_fr)
            
            # --- Strict Criteria ---
            # 1. Omission must be significantly higher than Baseline (Fixation)
            # 2. Omission must be significantly higher than the Sequence window
            # 3. Sequence must NOT be higher than Baseline (to ensure it's not a generic responder)
            # 4. Sequence must NOT be significantly lower than Baseline (to avoid "Fake" disinhibition)
            
            if mean_omit > max(mean_fix, mean_seq) * 2.0 and mean_omit > 1.0:
                # Statistical check
                _, p_fix = ttest_rel(omit_fr, fix_fr)
                _, p_seq = ttest_rel(omit_fr, seq_fr)
                
                # Check that it's NOT a stimulus-driven unit (Sequence <= Baseline * 1.5)
                is_not_stim = mean_seq <= mean_fix * 1.5
                
                # Check that it's NOT a disinhibition/inhibited unit (Sequence >= Baseline * 0.5)
                # i.e., it doesn't drop to zero during sequence and then "come back"
                is_not_inhib = mean_seq >= mean_fix * 0.5
                
                if p_fix < 0.001 and p_seq < 0.001 and is_not_stim and is_not_inhib:
                    real_omission_units.append({
                        'session_id': session_id,
                        'probe_id': probe_id,
                        'area': area,
                        'unit_idx': u,
                        'condition': cond,
                        'mean_fix': mean_fix,
                        'mean_seq': mean_seq,
                        'mean_omit': mean_omit,
                        'ratio_fix': mean_omit / (mean_fix + 1e-6),
                        'ratio_seq': mean_omit / (mean_seq + 1e-6)
                    })
                    
    return real_omission_units

def main():
    all_units = []
    for sid, probes in SESSION_AREAS.items():
        for pid in probes:
            units = detect_real_omission_units(sid, pid)
            all_units.extend(units)
            
    df = pd.DataFrame(all_units)
    if not df.empty:
        df = df.sort_values('ratio_fix', ascending=False).drop_duplicates(subset=['session_id', 'probe_id', 'unit_idx'])
        output_path = os.path.join(OUTPUT_DIR, 'real_omission_units.csv')
        df.to_csv(output_path, index=False)
        print(f"\nFound {len(df)} 'Real' omission neurons.")
        print(df['area'].value_counts())
    else:
        print("\nNo 'Real' omission neurons detected with these strict criteria.")

if __name__ == "__main__":
    main()
