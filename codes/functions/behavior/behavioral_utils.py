import numpy as np
import scipy.io as sio

def load_behavioral_data(file_path):
    """Loads MonkeyLogic behavioral .mat data."""
    data = sio.loadmat(file_path)
    return data['bhvUni']

def extract_trial_data(trial_struct, fs=1000):
    """Extracts eye, pupil, and event timing for a single trial with safety checks."""
    try:
        analog = trial_struct['AnalogData'][0, 0]
        
        # Eye data (X, Y)
        if 'Eye' in analog.dtype.names and analog['Eye'].size > 0:
            eye = analog['Eye'][0, 0]
        else:
            eye = None
            
        # Pupil data (Gen1 in MonkeyLogic for this setup)
        if 'General' in analog.dtype.names and analog['General'].size > 0:
            gen = analog['General'][0, 0]
            if 'Gen1' in gen.dtype.names and gen['Gen1'].size > 0:
                pupil = gen['Gen1'][0, 0]
            else:
                pupil = None
        else:
            pupil = None
            
        # BehavioralCodes.CodeNumbers and CodeTimes
        if 'BehavioralCodes' in trial_struct.dtype.names and trial_struct['BehavioralCodes'].size > 0:
            codes_struct = trial_struct['BehavioralCodes'][0, 0]
            codes = codes_struct['CodeNumbers'][0, 0].flatten()
            times = codes_struct['CodeTimes'][0, 0].flatten()
        else:
            codes, times = None, None
            
        return eye, pupil, codes, times
    except Exception as e:
        print(f"Error extracting trial: {e}")
        return None, None, None, None

def detect_saccades(eye_x, eye_y, fs=1000, vel_thresh=30, amp_thresh=1.5):
    """Detects saccades and microsaccades."""
    if eye_x is None or eye_y is None:
        return None, None
        
    vx = np.gradient(eye_x) * fs
    vy = np.gradient(eye_y) * fs
    vel = np.sqrt(vx**2 + vy**2)
    
    # Saccade candidates based on velocity
    saccade_indices = np.where(vel > vel_thresh)[0]
    
    return saccade_indices, vel

def get_angular_direction(eye_x, eye_y):
    """Calculates the direction (0-360) for eye movements."""
    if eye_x is None or eye_y is None or len(eye_x) < 2:
        return None
        
    dx = np.diff(eye_x)
    dy = np.diff(eye_y)
    angles = np.arctan2(dy, dx)
    return np.degrees(angles) % 360
