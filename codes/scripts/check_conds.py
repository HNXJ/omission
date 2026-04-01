
import scipy.io
import numpy as np
from collections import Counter

def check_conditions(file_path):
    data = scipy.io.loadmat(file_path, struct_as_record=False, squeeze_me=True)
    bhv_array = data['bhvUni']
    
    conds = []
    for trial in bhv_array:
        conds.append(trial.Condition)
        
    counts = Counter(conds)
    print(f"Unique Conditions in {file_path}: {sorted(counts.keys())}")
    print(f"Number of Unique Conditions: {len(counts)}")
    print(f"Counts: {counts}")

if __name__ == "__main__":
    check_conditions(r'behavioral\omission_bhv\data\230629_Joule_glo_omission.bhv2.mat')
