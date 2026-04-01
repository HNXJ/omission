
import scipy.io
import numpy as np
import os

def find_matching_trial():
    session_id = '230629'
    cond = 'AAAB'
    
    # 1. Load .mat
    mat_path = r'behavioral\omission_bhv\data\230629_Joule_glo_omission.bhv2.mat'
    data = scipy.io.loadmat(mat_path, struct_as_record=False, squeeze_me=True)
    bhv_array = data['bhvUni']
    
    # 2. Load .npy
    npy_path = f'data/ses{session_id}-behavioral-{cond}.npy'
    npy_data = np.load(npy_path)
    
    # Stim sequence function
    def get_stim_seq(trial):
        attrs = trial.TaskObject.Attribute
        stim_names = []
        for attr in attrs[1:]:
            if isinstance(attr, np.ndarray) and len(attr) > 1:
                nm = str(attr[1])
                if 'A.avi' in nm: stim_names.append('A')
                elif 'B.avi' in nm: stim_names.append('B')
                else: stim_names.append('O')
            else: stim_names.append('O')
        return "".join(stim_names)

    # Filter .mat for correct AAAB
    mat_aaab_correct = [t for t in bhv_array if get_stim_seq(t) == cond and t.TrialError == 0]
    
    # Sample NWB (Trial 0, X=Ch1)
    nwb_sample_x = npy_data[0, 1, :]

    print(f"Total Correct AAAB in .mat: {len(mat_aaab_correct)}")
    print(f"Total Trials in .npy: {len(npy_data)}")

    
    # Search for match
    for i, t in enumerate(mat_aaab_correct):
        eye_x = t.AnalogData.Eye[:, 0]
        # NWB is usually 6000ms. BHV is aligned to some code.
        # Let's try to find if any offset of eye_x matches nwb_sample_x
        # nwb_sample_x is 6000 long.
        if len(eye_x) >= 100:
            # Check correlation or simple distance for first 100ms
            for offset in range(len(eye_x) - 100):
                if np.allclose(eye_x[offset:offset+100], nwb_sample_x[:100], atol=1e-3):
                    print(f"Found Match! Trial {i} in mat_aaab_correct matches trial 0 in .npy. Offset: {offset}")
                    return

if __name__ == "__main__":
    find_matching_trial()
