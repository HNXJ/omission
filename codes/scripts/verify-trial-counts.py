
import scipy.io
import numpy as np
import os

def verify_trial_counts():
    session_id = '230629'
    cond = 'AAAB'
    
    # 1. Check .mat
    mat_path = r'behavioral\omission_bhv\data\230629_Joule_glo_omission.bhv2.mat'
    data = scipy.io.loadmat(mat_path, struct_as_record=False, squeeze_me=True)
    bhv_array = data['bhvUni']
    
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

    mat_aaab_all = [t for t in bhv_array if get_stim_seq(t) == cond]
    mat_aaab_correct = [t for t in mat_aaab_all if t.TrialError == 0]
    
    print(f"Session {session_id}, Condition {cond}:")
    print(f"  .mat Total Trials: {len(mat_aaab_all)}")
    print(f"  .mat Correct Trials (TrialError=0): {len(mat_aaab_correct)}")
    
    # 2. Check .npy
    npy_path = f'data/ses{session_id}-behavioral-{cond}.npy'
    if os.path.exists(npy_path):
        npy_data = np.load(npy_path)
        print(f"  .npy Shape: {npy_data.shape}")
        print(f"  .npy Number of Trials: {npy_data.shape[0]}")
    else:
        print(f"  .npy file not found: {npy_path}")

if __name__ == "__main__":
    verify_trial_counts()
