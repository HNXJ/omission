import numpy as np
import os
import matplotlib.pyplot as plt

# Global Aesthetics
plt.style.use('dark_background')
plt.rcParams['axes.facecolor'] = '#000000'
plt.rcParams['figure.facecolor'] = '#000000'
plt.rcParams['axes.edgecolor'] = '#708090'
plt.rcParams['text.color'] = '#FFFFFF'
GOLD = '#CFB87C'
VIOLET = '#8F00FF'
SLATE = '#708090'

def get_polar_direction(eye_x, eye_y):
    """Calculates the polar direction of eye-movements (dx, dy)."""
    dx = np.diff(eye_x)
    dy = np.diff(eye_y)
    angles = np.arctan2(dy, dx)
    return np.degrees(angles) % 360

def plot_rose_directions(directions_dict, session_id):
    """Plots Rose Plots (Polar Histograms) for eye-movement directions."""
    fig, axes = plt.subplots(1, len(directions_dict), subplot_kw={'projection': 'polar'}, figsize=(12, 5))
    
    if len(directions_dict) == 1:
        axes = [axes]
        
    for i, (label, dirs) in enumerate(directions_dict.items()):
        # Filter for significant movements (where dx or dy > 0.01) to reduce noise
        # (Assuming directions were calculated from diffs)
        
        counts, bins = np.histogram(np.radians(dirs), bins=36, range=(0, 2*np.pi))
        
        axes[i].bar(bins[:-1], counts, width=2*np.pi/36, color=GOLD if 'A' in label else VIOLET, alpha=0.8, edgecolor='#FFFFFF')
        axes[i].set_title(f"Context: {label}", color=GOLD if 'A' in label else VIOLET, pad=20)
        axes[i].set_yticklabels([]) # Hide radial ticks
        
    plt.suptitle(f"Eye Movement Directionality: Session {session_id}", color='#FFFFFF', fontsize=16)
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    
    fig_path = os.path.join(r"D:\Analysis\Omission\local-workspace\figures", f"FIG_Eye_Rose_Directions_{session_id}.png")
    plt.savefig(fig_path, dpi=300)
    print(f"Saved rose plot to {fig_path}")

def run_analysis(data_dir, session_id):
    """Main execution function for directionality analysis."""
    # Target contexts: AAAB (45 deg) vs BBBA (135 deg)
    contexts = ['AAAB', 'BBBA', 'RRRR']
    directions_dict = {}
    
    for ctx in contexts:
        file_path = os.path.join(data_dir, f'ses{session_id}-behavioral-{ctx}.npy')
        if not os.path.exists(file_path):
            continue
            
        data = np.load(file_path)
        eye_x = data[:, 0, :]
        eye_y = data[:, 1, :]
        
        # Calculate directions across all trials and time
        all_dirs = []
        for t in range(eye_x.shape[0]):
            dirs = get_polar_direction(eye_x[t], eye_y[t])
            all_dirs.extend(dirs)
            
        directions_dict[ctx] = np.array(all_dirs)
        
    if directions_dict:
        plot_rose_directions(directions_dict, session_id)

if __name__ == "__main__":
    data_dir = r"D:\Analysis\Omission\local-workspace\data"
    session_id = "230629"
    run_analysis(data_dir, session_id)
