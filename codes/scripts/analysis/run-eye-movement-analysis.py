
import numpy as np
import pandas as pd
import scipy.io
import os
import plotly.express as px
import plotly.graph_objects as go
from sklearn.svm import SVC
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

# Path setup
BHV_DIR = r'D:\Analysis\Omission\local-workspace\behavioral\omission_bhv\data'
DATA_DIR = r'D:\Analysis\Omission\local-workspace\data'
OUTPUT_DIR = r'D:\Analysis\Omission\local-workspace\figures\behavioral'
os.makedirs(OUTPUT_DIR, exist_ok=True)

SESSION = '230830'
MAT_FILE = os.path.join(BHV_DIR, f'{SESSION}_Cajal_glo_omission.bhv2.mat')

def extract_eye_features(eye_data, fs=1000):
    """Extract x, y, dx, dy, d2x, d2y, speed, accel from raw eye trace."""
    x = eye_data[:, 0]
    y = eye_data[:, 1]
    
    # Velocity (dx, dy)
    dx = np.gradient(x) * fs
    dy = np.gradient(y) * fs
    speed = np.sqrt(dx**2 + dy**2)
    
    # Acceleration (d2x, d2y)
    d2x = np.gradient(dx) * fs
    d2y = np.gradient(dy) * fs
    accel = np.sqrt(d2x**2 + d2y**2)
    
    return {
        'x_mean': np.mean(x), 'x_std': np.std(x),
        'y_mean': np.mean(y), 'y_std': np.std(y),
        'speed_mean': np.mean(speed), 'speed_max': np.max(speed),
        'accel_mean': np.mean(accel), 'accel_max': np.max(accel),
        'displacement': np.sqrt((x[-1]-x[0])**2 + (y[-1]-y[0])**2)
    }

def run_eye_analysis():
    print(f"Loading MonkeyLogic data for session {SESSION}...")
    data = scipy.io.loadmat(MAT_FILE)
    bhv = data['bhvUni'][0]
    
    results = []
    all_features = []
    all_labels = []
    
    # We focus on the window after the 4th stimulus (Omission window)
    # Stimulus 4 onset is around code 2007 (based on typical ML sequences)
    # But let's use the actual stim attributes to find A vs B identity
    
    for i in range(len(bhv)):
        trial = bhv[i]
        try:
            # 1. Determine Identity (A vs B)
            # Find the path in TaskObject attributes
            attr = trial['TaskObject'][0,0]['Attribute']
            path_str = str(attr)
            if 'A.avi' in path_str:
                label = 'A'
            elif 'B.avi' in path_str:
                label = 'B'
            else:
                continue # Skip X or others for now
            
            # 2. Extract Eye Trace (Full trial for now, we'll refine later)
            eye = trial['AnalogData']['Eye'][0,0]
            if eye.size == 0: continue
            
            # Extract features
            feats = extract_eye_features(eye)
            feats['label'] = label
            feats['trial'] = i
            results.append(feats)
            
            # Raw features for PCA/SVM
            raw_vec = [feats['x_mean'], feats['x_std'], feats['y_mean'], feats['y_std'], 
                       feats['speed_mean'], feats['speed_max'], feats['accel_mean'], feats['accel_max']]
            all_features.append(raw_vec)
            all_labels.append(label)
            
        except Exception as e:
            continue

    df = pd.DataFrame(results)
    X = np.array(all_features)
    y = np.array(all_labels)
    
    print(f"Extracted {len(df)} trials with eye data. A={sum(y=='A')}, B={sum(y=='B')}")

    # --- 1. PCA Embedding ---
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X_scaled)
    
    df['pca1'] = X_pca[:, 0]
    df['pca2'] = X_pca[:, 1]
    
    fig_pca = px.scatter(df, x='pca1', y='pca2', color='label', 
                         title=f"PCA of Eye Movement Features (A vs B) - Session {SESSION}")
    fig_pca.write_html(os.path.join(OUTPUT_DIR, f"eye_features_pca_{SESSION}.html"))
    
    # --- 2. SVM Classification ---
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    accs = []
    for train_idx, test_idx in skf.split(X_scaled, y):
        clf = SVC(kernel='linear')
        clf.fit(X_scaled[train_idx], y[train_idx])
        accs.append(clf.score(X_scaled[test_idx], y[test_idx]))
    
    avg_acc = np.mean(accs)
    print(f"SVM Accuracy (Eye Features A vs B): {avg_acc:.3f}")

    # --- 3. Save Markdown Report ---
    report = f"""# Eye Movement Analysis: A vs B Identity
- **Session**: {SESSION}
- **Features**: x, y, speed, accel (mean/std/max)
- **Trials**: {len(df)}
- **SVM Accuracy**: {avg_acc:.3f}
- **PCA Insight**: Visualized in `eye_features_pca_{SESSION}.html`

## Interpretation
If accuracy > 0.55, eye movements carry identity-specific information, possibly due to micro-saccadic bias or predictive tracking.
"""
    with open(os.path.join(OUTPUT_DIR, "eye_movement_report.md"), 'w') as f:
        f.write(report)

if __name__ == '__main__':
    run_eye_analysis()
