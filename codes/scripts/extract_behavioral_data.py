import numpy as np
import scipy.io as sio
import os
import sys

# Ensure functions folder is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'functions')))
from behavioral_utils import load_behavioral_data, extract_trial_data

def process_session(file_path, output_dir):
    """Processes a single session and saves extracted eye/pupil data."""
    session_name = os.path.basename(file_path).split('_')[0]
    bhv_data = load_behavioral_data(file_path)
    
    num_trials = bhv_data.shape[1]
    
    processed_trials = []
    
    for i in range(num_trials):
        trial = bhv_data[0, i]
        
        # Only process correct trials (TrialError == 0)
        if trial['TrialError'][0, 0] != 0:
            continue
            
        eye, pupil, codes, times = extract_trial_data(trial)
        
        # Check if any data extraction failed
        if eye is None or pupil is None or codes is None or times is None:
            continue
        
        # Align to Code 101 (P1 onset)
        p1_idx = np.where(codes == 101)[0]
        if len(p1_idx) == 0:
            continue
            
        p1_time = times[p1_idx[0]]
        
        # Convert times (ms) to sample indices (assuming 1kHz sampling)
        # 1000ms pre-P1 buffer
        start_idx = int(p1_time - 1000)
        end_idx = int(p1_time + 5000) # 6000ms window as per TASK_DETAILS
        
        # Basic bounds check
        if start_idx < 0 or end_idx > eye.shape[0]:
            continue
            
        eye_seg = eye[start_idx:end_idx, :] # (6000, 2)
        pupil_seg = pupil[start_idx:end_idx, :] # (6000, 1)
        
        # Condition info
        cond = int(trial['Condition'][0, 0])
        block = int(trial['Block'][0, 0])
        
        # Store as trial dictionary
        processed_trials.append({
            'eye': eye_seg,
            'pupil': pupil_seg,
            'condition': cond,
            'block': block,
            'trial_idx': i
        })
        
    # Save as .npy
    save_path = os.path.join(output_dir, f'ses-{session_name}_behavioral_extracted.npy')
    np.save(save_path, processed_trials)
    print(f"Saved {len(processed_trials)} correct trials to {save_path}")

if __name__ == "__main__":
    input_dir = r"D:\Analysis\Omission\local-workspace\behavioral\omission_bhv\data"
    output_dir = r"D:\Analysis\Omission\local-workspace\data"
    
    # Process the first session as a test
    mat_files = sorted([f for f in os.listdir(input_dir) if f.endswith('.mat')])
    if mat_files:
        process_session(os.path.join(input_dir, mat_files[0]), output_dir)
