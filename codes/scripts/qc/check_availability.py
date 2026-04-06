import os
import pandas as pd
from pynwb import NWBHDF5IO
import numpy as np

NWB_DIR = r'D:\Analysis\Omission\local-workspace'

def check_data_availability():
    nwb_files = [f for f in os.listdir(NWB_DIR) if f.endswith('.nwb')]
    availability_data = []

    for filename in nwb_files:
        session_id = filename.split('_')[1].split('-')[1]
        nwb_path = os.path.join(NWB_DIR, filename)
        print(f"Checking Session: {session_id}...")

        try:
            with NWBHDF5IO(nwb_path, 'r', load_namespaces=True) as io:
                nwb = io.read()
                
                # 1. Spikes (SPK)
                has_spk = nwb.units is not None and len(nwb.units) > 0
                n_units = len(nwb.units) if has_spk else 0
                
                # 2. LFP
                lfp_keys = [k for k in nwb.acquisition.keys() if 'lfp' in k.lower()]
                has_lfp = len(lfp_keys) > 0
                
                # 3. EYE (x, y, pupil)
                has_eye = 'eye_1_tracking' in nwb.acquisition
                has_pupil = 'pupil_1_tracking' in nwb.acquisition
                
                # 4. Reward
                has_reward = False
                n_trials = 0
                n_conditions = 0
                if 'omission_glo_passive' in nwb.intervals:
                    df_trials = nwb.intervals['omission_glo_passive'].to_dataframe()
                    n_trials = len(df_trials)
                    n_conditions = len(df_trials['task_condition_number'].unique())
                    # Check for reward in intervals or acquisition
                    if 'reward' in df_trials.columns:
                        has_reward = True
                    else:
                        reward_keys = [k for k in nwb.acquisition.keys() if 'reward' in k.lower()]
                        if len(reward_keys) > 0:
                            has_reward = True
                
                availability_data.append({
                    "Session": session_id,
                    "Trials": n_trials,
                    "Conditions": n_conditions,
                    "Units (SPK)": n_units,
                    "LFP": "Yes" if has_lfp else "No",
                    "Eye (x,y)": "Yes" if has_eye else "No",
                    "Pupil": "Yes" if has_pupil else "No",
                    "Reward": "Yes" if has_reward else "No"
                })
        except Exception as e:
            print(f"  Error reading {session_id}: {e}")

    df = pd.DataFrame(availability_data)
    md_table = df.to_markdown(index=False)
    
    output_path = os.path.join(NWB_DIR, 'DATA_AVAILABILITY_SUMMARY.md')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# 📊 13-Session Data Availability Summary\n\n")
        f.write(md_table)
    
    print(f"\nSummary table saved to {output_path}")
    print(md_table)

if __name__ == "__main__":
    check_data_availability()
