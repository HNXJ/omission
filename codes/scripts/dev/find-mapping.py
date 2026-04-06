
import numpy as np
import scipy.io
import os

def find_mapping_by_data_matching():
    # Load .npy
    npy_path = r'data\ses230629-behavioral-AAAB.npy'
    if not os.path.exists(npy_path):
        print(f"File not found: {npy_path}")
        return
    
    npy_data = np.load(npy_path)
    print(f"npy_data shape: {npy_data.shape}")
    # npy_data is (nTrials, 3, 5248) - 3 channels (Pupil, X, Y)
    
    # Load .mat
    mat_path = r'behavioral\omission_bhv\data\230629_Joule_glo_omission.bhv2.mat'
    mat_data = scipy.io.loadmat(mat_path, struct_as_record=False, squeeze_me=True)
    bhv_array = mat_data['bhvUni']
    
    # Try to find a trial in .mat that matches the first trial in .npy
    # Sample first trial's X data (Channel 1)
    sample_x = npy_data[0, 1, :100]
    
    for i, trial in enumerate(bhv_array):
        if hasattr(trial, 'AnalogData') and hasattr(trial.AnalogData, 'Eye'):
            eye_x = trial.AnalogData.Eye[:, 0]
            # Check if sample_x is in eye_x
            # We don't know the offset, so let's use a correlation or just a simple search
            # Actually, the .npy files were probably sliced starting at some event.
            # But let's see if we can find the exact values.
            if len(eye_x) >= len(sample_x):
                # Search for sample_x in eye_x
                for start in range(len(eye_x) - len(sample_x) + 1):
                    if np.allclose(eye_x[start:start+100], sample_x, atol=1e-5):
                        print(f"Found match! Trial {i} in .mat matches first trial of AAAB. Condition: {trial.Condition}")
                        return

if __name__ == "__main__":
    find_mapping_by_data_matching()
