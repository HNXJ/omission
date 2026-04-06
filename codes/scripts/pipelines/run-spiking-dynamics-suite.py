
import os
import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.svm import SVC
from sklearn.model_selection import StratifiedKFold
from concurrent.futures import ProcessPoolExecutor
import json

# Parameters
WIN_SIZE = 50 
STEP = 10 
FS = 1000 
TIME_RANGE = (2500, 4500) # Window covering P3, Delay, and P4/Omission

DATA_DIR = "D:/Analysis/Omission/local-workspace/data"
CHECKPOINT_DIR = "D:/Analysis/Omission/local-workspace/data/checkpoints"
NEURON_CAT_FILE = os.path.join(CHECKPOINT_DIR, "enhanced_neuron_categories.csv")

def get_pop_vectors(spikes, win_size=50, step=10):
    """
    spikes: (Trials, Neurons, Time)
    Returns: (Trials, TimeBins, Neurons) population vectors
    """
    n_trials, n_neurons, n_time = spikes.shape
    time_bins = np.arange(0, n_time - win_size + 1, step)
    n_bins = len(time_bins)
    
    pop_vecs = np.zeros((n_trials, n_bins, n_neurons))
    for i, t in enumerate(time_bins):
        pop_vecs[:, i, :] = np.sum(spikes[:, :, t:t+win_size], axis=2)
    return pop_vecs, time_bins

def process_area_dynamics(session_id, area, session_neurons, area_neurons):
    session_id = str(session_id)
    results = {'area': area, 'session': session_id}
    
    # Load spiking data for conditions: RRRR (Standard), RXRR (Omission)
    # Mapping probes to areas
    probe_to_area = session_neurons.groupby('probe')['area'].first().to_dict()
    
    # We focus on the comparison: RXRR (Omit P2) vs RRRR (Standard)
    # Or AXAB (Omit P2) vs AAAB (Standard)
    
    # Let's use RXRR and RRRR for a general "Omission Detection" and identity comparison
    conds = ["RRRR", "RXRR", "AAAB", "AXAB", "BBBA", "BXBA"]
    
    data_store = {}
    for cond in conds:
        # Combine probes for this area
        area_spk = []
        probes_for_area = area_neurons['probe'].unique()
        for probe in probes_for_area:
            spk_file = os.path.join(DATA_DIR, f"ses{session_id}-units-probe{probe}-spk-{cond}.npy")
            if os.path.exists(spk_file):
                unit_indices = area_neurons[area_neurons['probe'] == probe]['unit_idx'].values
                # spikes shape: (Trials, Neurons, Time)
                spk = np.nan_to_num(np.load(spk_file))[:, unit_indices, :]
                area_spk.append(spk)
        
        if len(area_spk) > 0:
            data_store[cond] = np.concatenate(area_spk, axis=1) # (Trials, TotalAreaNeurons, Time)
            
    if not data_store: return None
    
    # 1. Population Manifolds (PCA)
    # Focus on Omission window (P4 or P2)
    # Let's take P4 window (3093ms - 3624ms)
    # Sample index for 3093ms (assuming 1000ms buffer) is 3093 + 1000 = 4093
    # Wait, the NWB export code says 6000ms window with 1000ms buffer. 
    # Sample 1000 = P1 onset.
    # P2 = 1031 + 1000 = 2031
    # P3 = 2062 + 1000 = 3062
    # P4/Omission = 3093 + 1000 = 4093
    
    omit_idx = slice(4093, 4624)
    delay_idx = slice(3562, 4093) # Delay before P4
    baseline_idx = slice(500, 1000) # Fixation
    
    # PCA on RRRR (Standard)
    if "RRRR" in data_store:
        spk_r = data_store["RRRR"]
        # Concatenate Trials and Time for PCA fitting
        # We'll take the Omission-equivalent window
        X = spk_r[:, :, omit_idx].reshape(-1, spk_r.shape[1])
        pca = PCA(n_components=min(10, X.shape[1]))
        pca.fit(X)
        results['manifold_exp_var'] = pca.explained_variance_ratio_.tolist()
        
    # 2. Decoding Identity (A vs B)
    # Using P1 window (1000-1531) for Stim A (AAAB) vs Stim B (BBBA)
    if "AAAB" in data_store and "BBBA" in data_store:
        p1_idx = slice(1000, 1531)
        # Average over P1
        feat_a = np.mean(data_store["AAAB"][:, :, p1_idx], axis=2)
        feat_b = np.mean(data_store["BBBA"][:, :, p1_idx], axis=2)
        
        X = np.vstack([feat_a, feat_b])
        y = np.concatenate([np.zeros(len(feat_a)), np.ones(len(feat_b))])
        
        skf = StratifiedKFold(n_splits=5, shuffle=True)
        scores = []
        for train_idx, test_idx in skf.split(X, y):
            clf = SVC(kernel='linear')
            clf.fit(X[train_idx], y[train_idx])
            scores.append(clf.score(X[test_idx], y[test_idx]))
        results['decoding_identity_acc'] = np.mean(scores)
        
    # 3. Decoding Omission (Omit vs Delay)
    # Comparison: Omission window (AXAB) vs physically identical Delay window (AAAB)
    if "AXAB" in data_store and "AAAB" in data_store:
        # Window of P2 Omission (2031-2562)
        omit_w = slice(2031, 2562)
        # In AXAB, this is Omission. In AAAB, this is P2. 
        # Wait, Delay vs Omission is better: 
        # d1 window in AAAB vs Omission in AXAB?
        # d1 is 1531-2031.
        
        feat_omit = np.mean(data_store["AXAB"][:, :, omit_w], axis=2)
        # Baseline (Fixation) for comparison
        feat_base = np.mean(data_store["AXAB"][:, :, baseline_idx], axis=2)
        
        # Omit vs Base
        X_ob = np.vstack([feat_omit, feat_base])
        y_ob = np.concatenate([np.zeros(len(feat_omit)), np.ones(len(feat_base))])
        
        scores_ob = []
        for train_idx, test_idx in skf.split(X_ob, y_ob):
            clf = SVC(kernel='linear')
            clf.fit(X_ob[train_idx], y_ob[train_idx])
            scores_ob.append(clf.score(X_ob[test_idx], y_ob[test_idx]))
        results['decoding_omit_vs_base_acc'] = np.mean(scores_ob)

        # Omit vs Delay (from same condition)
        feat_delay = np.mean(data_store["AXAB"][:, :, slice(1531, 2031)], axis=2)
        X_od = np.vstack([feat_omit, feat_delay])
        y_od = np.concatenate([np.zeros(len(feat_omit)), np.ones(len(feat_delay))])
        
        scores_od = []
        for train_idx, test_idx in skf.split(X_od, y_od):
            clf = SVC(kernel='linear')
            clf.fit(X_od[train_idx], y_od[train_idx])
            scores_od.append(clf.score(X_od[test_idx], y_od[test_idx]))
        results['decoding_omit_vs_delay_acc'] = np.mean(scores_od)

    return results

def main():
    neurons_df = pd.read_csv(NEURON_CAT_FILE)
    sessions = neurons_df['session'].unique()
    
    print(f"Starting Unified Spiking Dynamics Analysis for {len(sessions)} sessions...")
    
    all_results = []
    task_args = []
    
    for ses in sessions:
        session_neurons = neurons_df[neurons_df['session'] == ses]
        areas = session_neurons['area'].unique()
        for area in areas:
            area_neurons = session_neurons[session_neurons['area'] == area]
            if len(area_neurons) >= 5: # Threshold for population analysis
                task_args.append((ses, area, session_neurons, area_neurons))
                
    with ProcessPoolExecutor(max_workers=os.cpu_count()) as executor:
        futures = [executor.submit(process_area_dynamics, *arg) for arg in task_args]
        for future in futures:
            res = future.result()
            if res:
                all_results.append(res)
                
    output_file = os.path.join(CHECKPOINT_DIR, "spiking_dynamics_full_v1.json")
    with open(output_file, 'w') as f:
        json.dump(all_results, f)
        
    print(f"Analysis complete. Results saved to {output_file}")
    
    # Save a summary CSV for easier reading
    summary_df = pd.DataFrame(all_results)
    summary_df.to_csv(os.path.join(CHECKPOINT_DIR, "spiking_dynamics_summary.csv"), index=False)

if __name__ == "__main__":
    main()
