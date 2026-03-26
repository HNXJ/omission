
import scipy.io
import numpy as np

def check_codes(file_path):
    data = scipy.io.loadmat(file_path, struct_as_record=False, squeeze_me=True)
    bhv_array = data['bhvUni']
    trial_0 = bhv_array[0]
    if hasattr(trial_0, 'BehavioralCodes'):
        bc = trial_0.BehavioralCodes
        print(f"Trial 0 CodeNumbers: {bc.CodeNumbers}")
        print(f"Trial 0 CodeTimes: {bc.CodeTimes}")

if __name__ == "__main__":
    check_codes(r'behavioral\omission_bhv\data\230629_Joule_glo_omission.bhv2.mat')
