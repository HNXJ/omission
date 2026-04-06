
from codes.config.paths import BEHAVIORAL_DIR

import scipy.io
import numpy as np
from collections import Counter

def check_conditions(file_path):
    data = scipy.io.loadmat(file_path, struct_as_record=False, squeeze_me=True)
    
    print("--- Top-level keys ---")
    print(data.keys())
    
    if 'bhvUni' in data:
        bhv_array = data['bhvUni']
        print(f"\n--- 'bhvUni' is an array of length: {len(bhv_array)} ---")
        
        if len(bhv_array) > 0:
            print("\n--- Structure of the first trial object ---")
            first_trial = bhv_array[0]
            print(dir(first_trial))
            
            conds = []
            for trial in bhv_array:
                conds.append(trial.Condition)
                
            counts = Counter(conds)
            print(f"\n--- Condition Summary ---")
            print(f"Unique Conditions in {file_path}: {sorted(counts.keys())}")
            print(f"Number of Unique Conditions: {len(counts)}")
            print(f"Counts: {counts}")

if __name__ == "__main__":
    check_conditions(str(BEHAVIORAL_DIR / '230629_Joule_glo_omission.bhv2.mat'))
