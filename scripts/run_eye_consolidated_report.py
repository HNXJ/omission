import numpy as np
import os
import matplotlib.pyplot as plt

# Global Aesthetics
plt.style.use('dark_background')
plt.rcParams['axes.facecolor'] = '#000000'
plt.rcParams['figure.facecolor'] = '#000000'
plt.rcParams['axes.edgecolor'] = SLATE = '#708090'
plt.rcParams['text.color'] = '#FFFFFF'
GOLD = '#CFB87C'
VIOLET = '#8F00FF'

def get_polar_direction(eye_x, eye_y, thresh=0.005):
    """Calculates polar direction for significant movements."""
    dx = np.diff(eye_x)
    dy = np.diff(eye_y)
    mag = np.sqrt(dx**2 + dy**2)
    valid = mag > thresh
    angles = np.arctan2(dy[valid], dx[valid])
    return np.degrees(angles) % 360

def plot_temporal_eye_trajectories(session_results, session_id):
    """Plots temporal X and Y eye trajectories for A vs B contexts."""
    fig, axes = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
    
    time_ms = np.arange(6000) - 1000
    
    contexts = ['AAAB', 'BBBA']
    colors = [GOLD, VIOLET]
    
    all_x = []
    all_y = []
    
    for ctx, color in zip(contexts, colors):
        if ctx not in session_results:
            continue
            
        eye_x = session_results[ctx]['eye_x']
        eye_y = session_results[ctx]['eye_y']
        
        # Mean across trials
        mx = np.mean(eye_x, axis=0)
        sx = np.std(eye_x, axis=0) / np.sqrt(eye_x.shape[0])
        my = np.mean(eye_y, axis=0)
        sy = np.std(eye_y, axis=0) / np.sqrt(eye_y.shape[0])
        
        axes[0].plot(time_ms, mx, color=color, label=f'Context: {ctx}')
        axes[0].fill_between(time_ms, mx-sx, mx+sx, color=color, alpha=0.2)
        
        axes[1].plot(time_ms, my, color=color)
        axes[1].fill_between(time_ms, my-sy, my+sy, color=color, alpha=0.2)
        
        all_x.extend([np.min(mx-sx), np.max(mx+sx)])
        all_y.extend([np.min(my-sy), np.max(my+sy)])
        
    # Apply extreme scaling
    if all_x:
        axes[0].set_ylim(min(all_x)*1.1, max(all_x)*1.1)
    if all_y:
        axes[1].set_ylim(min(all_y)*1.1, max(all_y)*1.1)
        
    axes[0].set_ylabel('Eye-X (Z-score)', color=SLATE)
    axes[1].set_ylabel('Eye-Y (Z-score)', color=SLATE)
    axes[1].set_xlabel('Time (ms)', color=SLATE)
    axes[0].set_title(f'Temporal Eye Trajectories: Session {session_id}', color=GOLD)
    axes[0].legend()
    
    for ax in axes:
        ax.axvline(0, color='#FFFFFF', alpha=0.5, linestyle='--')
        for i in range(1, 5): # P2, P3, P4
            ax.axvline(i*531, color='#FFFFFF', alpha=0.2, linestyle=':')
            
    plt.tight_layout()
    fig_path = os.path.join(r"D:\Analysis\Omission\local-workspace\figures", f"FIG_Eye_Temporal_Trajectories_{session_id}.png")
    plt.savefig(fig_path, dpi=300)
    print(f"Saved temporal trajectories to {fig_path}")

def run_eye_consolidated(data_dir, session_id):
    """Consolidated oculomotor analysis suite."""
    from run_behavioral_decoding_suite import analyze_session_eye
    
    results = analyze_session_eye(data_dir, session_id)
    
    # 1. Rose Plots
    contexts = ['AAAB', 'BBBA', 'AXAB', 'BXBA']
    directions_dict = {}
    for ctx in contexts:
        if ctx in results:
            dirs = get_polar_direction(results[ctx]['eye_x'].flatten(), results[ctx]['eye_y'].flatten())
            directions_dict[ctx] = dirs
            
    if directions_dict:
        # Import plotting function from the other script or redefine here
        import run_eye_direction_analysis as reda
        reda.plot_rose_directions(directions_dict, session_id)
        
    # 2. Temporal Trajectories
    plot_temporal_eye_trajectories(results, session_id)

if __name__ == "__main__":
    data_dir = r"D:\Analysis\Omission\local-workspace\data"
    session_id = "230629"
    run_eye_consolidated(data_dir, session_id)
