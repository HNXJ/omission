
import scipy.io
import numpy as np

def check_timing_and_conds(file_path):
    data = scipy.io.loadmat(file_path, struct_as_record=False, squeeze_me=True)
    bhv_array = data['bhvUni']
    
    seen_conds = {}
    for trial in bhv_array:
        c = trial.Condition
        if c not in seen_conds:
            to = trial.TaskObject
            # Extract stim names
            attrs = to.Attribute
            stim_seq = []
            for attr in attrs[1:]: # Skip 'fix'
                if isinstance(attr, np.ndarray) and len(attr) > 1:
                    name = str(attr[1])
                    if 'A.avi' in name: stim_seq.append('A')
                    elif 'B.avi' in name: stim_seq.append('B')
                    elif 'R.avi' in name: stim_seq.append('R')
                    else: stim_seq.append('O') # Likely omission if not a known stim?
                else:
                    stim_seq.append('O')
            seen_conds[c] = "".join(stim_seq)
            
    print(f"Condition Mapping for {file_path}:")
    for c in sorted(seen_conds.keys()):
        print(f"  {c}: {seen_conds[c]}")
        
    # Check sample interval
    print(f"SampleInterval: {bhv_array[0].AnalogData.SampleInterval}")

if __name__ == "__main__":
    check_timing_and_conds(r'behavioral\omission_bhv\data\230629_Joule_glo_omission.bhv2.mat')
