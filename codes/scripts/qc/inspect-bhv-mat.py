
import scipy.io
import numpy as np

def inspect_task_object(file_path):
    data = scipy.io.loadmat(file_path, struct_as_record=False, squeeze_me=True)
    trial_0 = data['bhvUni'][0]
    if hasattr(trial_0, 'TaskObject'):
        to = trial_0.TaskObject
        print(f"TaskObject type: {type(to)}")
        if hasattr(to, '_fieldnames'):
            print(f"TaskObject fields: {to._fieldnames}")
            for f in to._fieldnames:
                val = getattr(to, f)
                print(f"TaskObject {f}: {val}")
    
    # Check if there is a global ConditionNames mapping
    # Sometimes it's in bhvUni[0].UserVars or Trial 0 itself
    if hasattr(trial_0, 'UserVars'):
        print(f"Trial 0 UserVars: {trial_0.UserVars}")
        if hasattr(trial_0.UserVars, '_fieldnames'):
            print(f"UserVars fields: {trial_0.UserVars._fieldnames}")

if __name__ == "__main__":
    inspect_task_object(r'behavioral\omission_bhv\data\230629_Joule_glo_omission.bhv2.mat')
