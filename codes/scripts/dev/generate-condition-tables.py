import os
import pandas as pd
import scipy.io as sio
from pathlib import Path
import glob

def generate_condition_tables():
    """
    Generates condition_table.csv for each session from the .bhv2.mat files.
    """
    mat_data_dir = Path("D:/drive/data/behavioral")
    if not mat_data_dir.exists():
        print(f"Behavioral data directory not found at: {mat_data_dir}")
        return
    nwb_data_dir = Path("D:/analysis/nwb")
    if not nwb_data_dir.exists():
        print(f"NWB data directory not found at: {nwb_data_dir}")
        return
    
    mat_files = sorted([f for f in os.listdir(mat_data_dir) if f.endswith('.mat')])
    
    for mat_file in mat_files:
        try:
            # Extract date from mat file name, e.g., '230629'
            date_str = mat_file.split('_')[0]
            
            # Find the corresponding NWB file
            nwb_files = [f for f in glob.glob(f"{nwb_data_dir}/**/*.nwb", recursive=True) if date_str in f]
            if not nwb_files:
                print(f"Could not find NWB file for MAT file: {mat_file}")
                continue
            
            nwb_file_path = Path(nwb_files[0])
            output_dir = nwb_file_path.parent
            output_dir.mkdir(parents=True, exist_ok=True) # Ensure output directory exists

            # Load the .mat file
            mat_path = mat_data_dir / mat_file
            bhv_data = sio.loadmat(mat_path, squeeze_me=True, struct_as_record=False)
            
            if 'bhvUni' not in bhv_data:
                print(f"'bhvUni' not found in {mat_file}")
                continue
                
            trials = bhv_data['bhvUni']
            
            trial_conditions = []
            for i, trial in enumerate(trials):
                trial_id = i + 1 # Assuming 1-based trial_id
                condition_num = trial.Condition
                # Map condition number to name
                conditions_map = {
                    1: 'AAAB', 2: 'AAAX', 3: 'AAXB', 4: 'AXAB',
                    5: 'BBBA', 6: 'BBBX', 7: 'BBXA', 8: 'BXBA',
                    9: 'RRRR', 10: 'RRRX', 11: 'RRXR', 12: 'RXRR'
                }
                condition_name = conditions_map.get(condition_num, f"unknown_{condition_num}")
                trial_conditions.append({'trial_id': trial_id, 'condition': condition_name})

            condition_df = pd.DataFrame(trial_conditions)
            
            # Save to condition_table.csv
            output_path = output_dir / "condition_table.csv"
            condition_df.to_csv(output_path, index=False)
            print(f"Saved condition table to {output_path}")

        except Exception as e:
            print(f"Error processing {mat_file}: {e}")

if __name__ == "__main__":
    generate_condition_tables()
