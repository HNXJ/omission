
import scipy.io
import numpy as np
import os

def check_ranges():
    session_id = '230629'
    cond = 'AAAB'
    
    # 1. Load .mat
    mat_path = r'behavioral\omission_bhv\data\230629_Joule_glo_omission.bhv2.mat'
    data = scipy.io.loadmat(mat_path, struct_as_record=False, squeeze_me=True)
    bhv_array = data['bhvUni']
    
    # 2. Load .npy
    npy_path = f'data/ses{session_id}-behavioral-{cond}.npy'
    npy_data = np.load(npy_path)
    
    # BHV Sample
    eye_x_mat = bhv_array[0].AnalogData.Eye[:, 0]
    print(f"BHV Eye X Range: [{np.min(eye_x_mat):.3f}, {np.max(eye_x_mat):.3f}]")
    
    # NWB Sample
    eye_x_npy = npy_data[0, 1, :]
    print(f"NWB Eye X Range: [{np.min(eye_x_npy):.3f}, {np.max(eye_x_npy):.3f}]")

if __name__ == "__main__":
    check_ranges()
