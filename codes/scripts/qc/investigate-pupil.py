import scipy.io as sio
import numpy as np
import os
import glob

def find_pupil_data(file_paths):
    for fp in file_paths:
        print(f"Investigating: {os.path.basename(fp)}")
        try:
            mat = sio.loadmat(fp, struct_as_record=False, squeeze_me=True)
            bhvUni = mat['bhvUni']
            if not isinstance(bhvUni, (list, np.ndarray)):
                bhvUni = [bhvUni]
            
            for i, trial in enumerate(bhvUni):
                ad = trial.AnalogData
                fields = [f for f in dir(ad) if not f.startswith('_')]
                for f in fields:
                    val = getattr(ad, f)
                    if val is not None and hasattr(val, '__len__') and len(val) > 0:
                        if f not in ['Eye', 'PhotoDiode', 'SampleInterval', 'Button']:
                            print(f"  Trial {trial.Trial} Field {f} shape: {getattr(val, 'shape', len(val))}")
                            return
                if hasattr(trial, 'UserVars'):
                    uv = trial.UserVars
                    fields = [f for f in dir(uv) if not f.startswith('_')]
                    for f in fields:
                        val = getattr(uv, f)
                        if val is not None and hasattr(val, '__len__') and len(val) > 0:
                            if f not in ['SkippedFrameTimeInfo']:
                                print(f"  Trial {trial.Trial} UserVars {f} shape: {getattr(val, 'shape', len(val))}")
                                return
        except Exception as e:
            print(f"  Error: {e}")

if __name__ == "__main__":
    bhv_dir = r'D:/Analysis/Omission/local-workspace/data/behavioral'
    files = glob.glob(os.path.join(bhv_dir, "*.bhv2.mat"))
    find_pupil_data(files)
