
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

# Timing config (from P1 at Sample 1000)
OMISSION_CONFIGS = {
    'p2': {'start': 531, 'end': 2062},
    'p3': {'start': 1562, 'end': 3093},
    'p4': {'start': 2593, 'end': 4124}
}

def detect_microsaccades(eye_x, eye_y, fs=1000, thresh=30):
    """Simple velocity thresholding for microsaccades."""
    vx = np.gradient(eye_x) * fs
    vy = np.gradient(eye_y) * fs
    vel = np.sqrt(vx**2 + vy**2)
    return (vel > thresh).astype(int)

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
            # Shape is (trials, signals, time). Signal 0=X, 1=Y
            beh_data = np.load(f_path)
            n_trials = beh_data.shape[0]
            
            config = OMISSION_CONFIGS[target_p]
            t_start = 1000 + config['start']
            t_end = 1000 + config['end']
            
            # Extract window
            eye_win = beh_data[:, :2, t_start:t_end] # (trials, XY, 1531)
            
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
            time = np.arange(eye_win.shape[2]) - 531 # Align omission onset to 0
            
            fig = make_subplots(rows=2, cols=1, 
                                subplot_titles=("Average Eye Trajectory (X/Y)", "Trial Variance Distribution"))
            
            # X Trace
            fig.add_trace(go.Scatter(x=time, y=avg_x, name='Avg X', line=dict(color=GOLD)), row=1, col=1)
            fig.add_trace(go.Scatter(
                x=np.concatenate([time, time[::-1]]),
                y=np.concatenate([avg_x - sem_x, (avg_x + sem_x)[::-1]]),
                fill='toself',
                fillcolor=GOLD,
                opacity=0.2,
                line=dict(color='rgba(255,255,255,0)'),
                showlegend=False,
                name='Avg X SEM'
            ), row=1, col=1)

            # Y Trace
            fig.add_trace(go.Scatter(x=time, y=avg_y, name='Avg Y', line=dict(color=VIOLET)), row=1, col=1)
            fig.add_trace(go.Scatter(
                x=np.concatenate([time, time[::-1]]),
                y=np.concatenate([avg_y - sem_y, (avg_y + sem_y)[::-1]]),
                fill='toself',
                fillcolor=VIOLET,
                opacity=0.2,
                line=dict(color='rgba(255,255,255,0)'),
                showlegend=False,
                name='Avg Y SEM'
            ), row=1, col=1)
            
            fig.add_trace(go.Box(y=total_var, name='Total Var (DVA^2)', marker_color=GOLD), row=2, col=1)
            
            fig.update_layout(
                title=f"🏺 Oculomotor Precision | {sid} {cond} ({target_p})",
                template="plotly_dark",
                paper_bgcolor=BLACK, plot_bgcolor=BLACK,
                font=dict(color=GOLD, family="Consolas"),
                height=800
            )
            
            out_name = f"EYE_DYNAMICS_{sid}_{cond}.html"
            fig.write_html(os.path.join(output_dir, out_name))
            print(f"  - Saved: {out_name}")

if __name__ == '__main__':
    run_eye_dynamics()
