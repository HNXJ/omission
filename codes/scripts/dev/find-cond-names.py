
import scipy.io
import numpy as np

def find_condition_names(file_path):
    data = scipy.io.loadmat(file_path, struct_as_record=False, squeeze_me=True)
    if 'bhvUni' in data:
        bhv = data['bhvUni']
        # Check if bhv is a list of trials or a master struct
        print(f"bhvUni type: {type(bhv)}")
        
        # If it's a list of trials, maybe the condition names are in a UserVars or something?
        # Let's check the first trial's TaskObject or UserVars
        trial_0 = bhv[0]
        if hasattr(trial_0, 'TaskObject'):
            print(f"Trial 0 TaskObject: {trial_0.TaskObject}")
            
    # List all top-level keys again
    print(f"All keys: {data.keys()}")

if __name__ == "__main__":
    find_condition_names(r'behavioral\omission_bhv\data\230629_Joule_glo_omission.bhv2.mat')
