
import numpy as np
import scipy.io as sio
import os
import glob
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 🏺 Madelane Golden Dark Palette
GOLD = "#CFB87C"
BLACK = "#000000"
VIOLET = "#8F00FF"

# Gamma-Standard timings: p1=1000, d1=1531, p2=2031, d2=2562, p3=3062, d3=3593, p4=4093, d4=4624
OMISSION_CONFIGS = {
    'p2': {'start': 1031, 'end': 1562}, # Relative to p1 onset at 1000
    'p3': {'start': 2062, 'end': 2593}, # Relative to p1 onset at 1000
    'p4': {'start': 3093, 'end': 3624}  # Relative to p1 onset at 1000
}

def detect_microsaccades(eye_x, eye_y, fs=1000, thresh=30):
    """Simple velocity thresholding for microsaccades."""
    vx = np.gradient(eye_x) * fs
    vy = np.gradient(eye_y) * fs
    vel = np.sqrt(vx**2 + vy**2)
    return np.nan_to_num(vel > thresh).astype(int)

def run_eye_dynamics():
    # We search for behavioral NWB .npy files as they are already aligned
    data_dir = r'D:\Analysis\Omission\local-workspace\data'
    output_dir = r'D:\Analysis\Omission\local-workspace\figures\part01'
    os.makedirs(output_dir, exist_ok=True)
    
    sessions = ['230630', '230816', '230830']
    
    for sid in sessions:
        # Behavioral files (already aligned to P1=1000)
        beh_files = glob.glob(os.path.join(data_dir, f'ses{sid}-behavioral-*.npy'))
        
        for f_path in beh_files:
            fname = os.path.basename(f_path)
            cond = fname.split('-')[-1].replace('.npy', '')
            
            target_p = None
            if cond in ['AXAB', 'BXBA', 'RXRR']: target_p = 'p2'
            elif cond in ['AAXB', 'BBXA', 'RRXR']: target_p = 'p3'
            elif cond in ['AAAX', 'BBBX', 'RRRX']: target_p = 'p4'
            
            if not target_p: continue
            
            print(f"🏺 Eye Dynamics: {fname} | Target: {target_p}")
            # Shape is (trials, signals, time). Signal 0=X, 1=Y, 2=Pupil
            try:
                beh_data = np.nan_to_num(np.load(f_path))
                n_trials = beh_data.shape[0]
            except Exception:
                continue
            
            config = OMISSION_CONFIGS[target_p]
            t_start = 1000 + config['start']
            t_end = 1000 + config['end']
            
            # Extract window
            eye_win = beh_data[:, :2, t_start:t_end] # (trials, XY, 531)
            
            # Calculate Variance (across time, mean per trial)
            var_x = np.var(eye_win[:, 0, :], axis=1)
            var_y = np.var(eye_win[:, 1, :], axis=1)
            total_var = var_x + var_y
            
            # Microsaccade Density
            ms_counts = []
            for t in range(n_trials):
                ms = detect_microsaccades(eye_win[t, 0, :], eye_win[t, 1, :])
                ms_counts.append(np.sum(ms))
            
            # Plot trial-averaged XY trajectory with SEM
            avg_x = np.mean(eye_win[:, 0, :], axis=0)
            avg_y = np.mean(eye_win[:, 1, :], axis=0)
            sem_x = np.std(eye_win[:, 0, :], axis=0) / np.sqrt(n_trials)
            sem_y = np.std(eye_win[:, 1, :], axis=0) / np.sqrt(n_trials)
            time = np.arange(eye_win.shape[2]) # Window relative to onset
            
            fig = make_subplots(rows=2, cols=1, 
                                subplot_titles=("Average Eye Trajectory (X/Y)", "Trial Variance Distribution"))
            
            # X Trace
            fig.add_trace(go.Scatter(x=time, y=avg_x, name='Avg X', line=dict(color='red')), row=1, col=1)
            fig.add_trace(go.Scatter(
                x=np.concatenate([time, time[::-1]]),
                y=np.concatenate([avg_x - sem_x, (avg_x + sem_x)[::-1]]),
                fill='toself',
                fillcolor='rgba(255,0,0,0.2)',
                line=dict(color='rgba(255,255,255,0)'),
                showlegend=False,
                name='Avg X SEM'
            ), row=1, col=1)

            # Y Trace
            fig.add_trace(go.Scatter(x=time, y=avg_y, name='Avg Y', line=dict(color='blue')), row=1, col=1)
            fig.add_trace(go.Scatter(
                x=np.concatenate([time, time[::-1]]),
                y=np.concatenate([avg_y - sem_y, (avg_y + sem_y)[::-1]]),
                fill='toself',
                fillcolor='rgba(0,0,255,0.2)',
                line=dict(color='rgba(255,255,255,0)'),
                showlegend=False,
                name='Avg Y SEM'
            ), row=1, col=1)
            
            fig.add_trace(go.Box(y=total_var, name='Total Var (DVA^2)', marker_color='black'), row=2, col=1)
            
            fig.update_layout(
                title=f"🏺 Oculomotor Precision | {sid} {cond} ({target_p})",
                template="plotly_white",
                height=800
            )
            
            out_name = f"EYE_DYNAMICS_{sid}_{cond}.html"
            fig.write_html(os.path.join(output_dir, out_name))
            print(f"  - Saved: {out_name}")

if __name__ == '__main__':
    run_eye_dynamics()
