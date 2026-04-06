from codes.config.paths import PROJECT_ROOT

import h5py
import numpy as np
import matplotlib.pyplot as plt

def get_data_from_ref(f, ref):
    """Recursively dereference HDF5 objects."""
    obj = f[ref]
    if isinstance(obj, h5py.Dataset):
        return obj[()]
    elif isinstance(obj, h5py.Group):
        # If it's a cell array (Group with refs), dereference each element
        data = []
        for row in obj:
            row_data = []
            for item in row:
                row_data.append(get_data_from_ref(f, item))
            data.append(row_data)
        return data
    return None

def main():
    path = 'D:/Electrophysiology/Matdelane/lfpData/10_LFPs_OGLO_PFC.mat'
    print(f"Loading {path}...")
    
    with h5py.File(path, 'r') as f:
        z = f['z'] # Cell array [1, 10] or similar
        
        # Area 10 (PFC) is the file itself.
        # In MATLAB: xL{10} = load(path).z
        # Based on mainLFP.m: xL{k}{1, cond}{ses}
        
        # Let's try to find Mode 5 (AAAx - Omission)
        # indexing in HDF5 is 0-based, so Mode 5 is index 4
        cond_idx = 4 
        
        try:
            # z is likely [12, 1] or [1, 12] cell array (for 12 modes)
            # Based on Z Shape: (12, 2) from previous inspection
            # Column 0: mode data?
            mode_ref = z[cond_idx, 0]
            mode_group = f[mode_ref]
            
            # mode_group is a cell array of sessions [1, n_sessions]
            session_ref = mode_group[0, 0]
            session_data = f[session_ref][()] # [trials, channels, time]
            
            print(f"PFC Mode 5 Session 0 Shape: {session_data.shape}")
            
            # Plot mean LFP across trials and channels
            # session_data shape is likely [trials, channels, time]
            # MATLAB usually stores as [time, channels, trials] or similar in v7.3
            # But mainLFP.m says: x1 = xL{k}{1, cond1}{ses}(:, :, 1:5000);
            # Which suggests [trials, channels, time] or [channels, trials, time]
            
            # Let's assume the last dimension is time (5000 samples)
            time_axis = np.linspace(-1000, 4000, session_data.shape[-1])
            mean_lfp = np.mean(session_data, axis=(0, 1))
            
            plt.figure(figsize=(12, 6))
            plt.plot(time_axis, mean_lfp, color='gold', linewidth=1.5)
            plt.axvline(0, color='red', linestyle='--', label='Omission Onset')
            plt.title("PFC Mean LFP - Omission Mode (AAAx)")
            plt.xlabel("Time (ms)")
            plt.ylabel("Amplitude")
            plt.grid(True, alpha=0.3)
            plt.legend()
            plt.savefig(str(PROJECT_ROOT / 'pfc_omission_lfp.png'))
            print("Plot saved to D:/hnxj-gemini/pfc_omission_lfp.png")
            
        except Exception as e:
            print(f"Error extracting data: {e}")

if __name__ == "__main__":
    main()
