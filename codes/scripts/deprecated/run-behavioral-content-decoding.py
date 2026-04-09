
from codes.config.paths import DATA_DIR, FIGURES_DIR

import numpy as np
import pandas as pd
import os
import scipy.io
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import umap
from collections import Counter
import plotly.express as px

# Constants
OUTPUT_DIR = FIGURES_DIR / 'final_reports/behavioral_decoding'
SESSIONS = ['230629', '230630', '230714', '230719', '230720', '230721', '230816', '230818', '230823', '230825', '230830', '230831', '230901']
CONDITIONS = ['AAAB', 'AAAX', 'AAXB', 'AXAB', 'BBBA', 'BBBX', 'BBXA', 'BXBA', 'RRRR', 'RRRX', 'RRXR', 'RXRR']
INTERVALS = {
'Fix': (0, 1000),
'P1': (1000, 1531),
'D1': (1531, 2062),
'P2': (2062, 2593),
'D2': (2593, 3124),
'P3': (3124, 3655),
'D3': (3655, 4186),
'P4': (4186, 4717),
'D4': (4717, 5248)
}
STIM_MAP = {
'AAAB': ['A', 'A', 'A', 'B'],
'AAAX': ['A', 'A', 'A', 'O'],
'AAXB': ['A', 'A', 'O', 'B'],
'AXAB': ['A', 'O', 'A', 'B'],
'BBBA': ['B', 'B', 'B', 'A'],
'BBBX': ['B', 'B', 'B', 'O'],
'BBXA': ['B', 'B', 'O', 'A'],
'BXBA': ['B', 'O', 'B', 'A'],
'RRRR': ['R', 'R', 'R', 'R'],
'RRRX': ['R', 'R', 'R', 'O'],
'RRXR': ['R', 'R', 'O', 'R'],
'RXRR': ['R', 'O', 'R', 'R']
}

def extract_features(data_seg, fs=1000):
# Ch 0: Pupil, Ch 1: X, Ch 2: Y
    pupil = data_seg[0]
    x = data_seg[1]
    y = data_seg[2]
    # Kinetics
    dx = np.gradient(x) * fs
    dy = np.gradient(y) * fs
    speed = np.sqrt(dx**2 + dy**2)
    accel = np.gradient(speed) * fs
    feats = {
        'x_mean': np.mean(x), 'x_std': np.std(x),
        'y_mean': np.mean(y), 'y_std': np.std(y),
        'pupil_mean': np.mean(pupil), 'pupil_std': np.std(pupil),
        'v_mean': np.mean(speed), 'v_max': np.max(speed),
        'a_mean': np.mean(accel), 'a_max': np.max(accel)
    }
    return feats

def run_content_decoding():
    all_data = []
    for sid in SESSIONS:
        print(f"Loading Session {sid}...")
        for cond in CONDITIONS:
            fpath = os.path.join(DATA_DIR, f'ses{sid}-behavioral-{cond}.npy')
            if not os.path.exists(fpath): continue
            try:
                data = np.load(fpath, mmap_mode='r') # (trials, 4, 6000)
                for t in range(data.shape[0]):
                    trial_data = data[t]
                    # Iterate through intervals
                    for name, (start, end) in INTERVALS.items():
                        if name == 'Fix':
                            label = 'Fixation'
                        elif name.startswith('D'):
                            label = 'Grey-Delay'
                        elif name.startswith('P'):
                            p_idx = int(name[1]) - 1
                            st = STIM_MAP[cond][p_idx]
                            if st == 'O': label = 'Grey-Omit'
                            else: label = f'Stim-{st}'
                        seg = trial_data[:, start:end]
                        feats = extract_features(seg)
                        feats['label'] = label
                        feats['session'] = sid
                        all_data.append(feats)
            except Exception as e:
                print(f"Error processing {fpath}: {e}")
                continue
    df = pd.DataFrame(all_data)
    print(f"Extracted {len(df)} feature vectors.")
    feature_sets = {
        'Pos': ['x_mean', 'x_std', 'y_mean', 'y_std'],
        'Kinetics': ['v_mean', 'v_max', 'a_mean', 'a_max'],
        'Pupil': ['pupil_mean', 'pupil_std'],
        'All': ['x_mean', 'x_std', 'y_mean', 'y_std', 'pupil_mean', 'pupil_std', 'v_mean', 'v_max', 'a_mean', 'a_max']
    }
    # 1. 5-Class: Fixation, Stim-A, Stim-B, Grey-Delay, Grey-Omit
    df_5c = df[df['label'].isin(['Fixation', 'Stim-A', 'Stim-B', 'Grey-Delay', 'Grey-Omit'])].copy()
    # 2. 3-Class: Fixation, Stimulus, Grey
    df['label_global'] = df['label'].apply(lambda x: 'Stimulus' if 'Stim' in x else ('Grey' if 'Grey' in x else 'Fixation'))
    results = []
    def balanced_subsample(sdf, target_col, max_per_class=1500):
        counts = Counter(sdf[target_col])
        min_size = min(min(counts.values()), max_per_class)
        indices = []
        for label in counts.keys():
            idx_list = sdf[sdf[target_col] == label].index.tolist()
            indices.extend(np.random.choice(idx_list, min_size, replace=False))
        return sdf.loc[indices]
    for target_name, target_col, work_df in [('Specific_5C', 'label', df_5c), ('Global_3C', 'label_global', df)]:
        print(f"Running Decoding for {target_name}...")
        sub_df = balanced_subsample(work_df, target_col)
        y = sub_df[target_col].values
        for fs_name, fs_cols in feature_sets.items():
            X = sub_df[fs_cols].values
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
            accs_svm = []
            for train_idx, test_idx in skf.split(X_scaled, y):
                clf = SVC(kernel='linear')
                clf.fit(X_scaled[train_idx], y[train_idx])
                accs_svm.append(clf.score(X_scaled[test_idx], y[test_idx]))
            results.append({
                'Task': target_name,
                'FeatureSet': fs_name,
                'Accuracy': np.mean(accs_svm),
                'Chance': 1.0 / len(np.unique(y))
            })
            print(f"  {fs_name}: {np.mean(accs_svm):.3f}")
    res_df = pd.DataFrame(results)
    res_df.to_csv(os.path.join(OUTPUT_DIR, "behavioral_content_decoding_results.csv"), index=False)
    # Visualization
    vis_df = balanced_subsample(df, 'label_global', max_per_class=500)
    X_vis = StandardScaler().fit_transform(vis_df[feature_sets['All']].values)
    pca_res = PCA(n_components=2).fit_transform(X_vis)
    umap_res = umap.UMAP(n_neighbors=15, min_dist=0.1, random_state=42).fit_transform(X_vis)
    vis_df['PCA1'], vis_df['PCA2'] = pca_res[:, 0], pca_res[:, 1]
    vis_df['UMAP1'], vis_df['UMAP2'] = umap_res[:, 0], umap_res[:, 1]
    px.scatter(vis_df, x='PCA1', y='PCA2', color='label_global', title="PCA: Content Encoding").write_html(os.path.join(OUTPUT_DIR, "PCA_Content_Encoding.html"))
    px.scatter(vis_df, x='UMAP1', y='UMAP2', color='label', title="UMAP: Specific Content").write_html(os.path.join(OUTPUT_DIR, "UMAP_Content_Specific.html"))
    with open(os.path.join(OUTPUT_DIR, "behavioral_content_decoding_report.md"), 'w', encoding='utf-8') as f:
        f.write("# Systematic Behavioral Content Decoding

")
        f.write("## 🎯 Objective
Determine if eye movements and pupil diameter encode the current visual content across 13 sessions.

")
        f.write("## 📈 Performance Summary
")
        f.write(res_df.to_markdown(index=False))
        f.write("

## 🔍 Interpretation
")
        f.write("The results indicate whether oculomotor states (gaze position and kinetics) are passive or systematically biased by the visual content and internal expectations.")

def main(args=None):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    run_content_decoding()

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Run script')
    # Add arguments here
    args = parser.parse_args()
    if 'main' in globals():
        main(args)
