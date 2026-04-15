import numpy as np
import pandas as pd
from pathlib import Path
import re
from scipy.signal import butter, filtfilt, hilbert
import plotly.graph_objects as go
from plotly.subplots import make_subplots

ARRAY_DIR = Path(r'D:\drive\data\arrays')
PROFILE_PATH = Path(r'D:\drive\omission\outputs\waveforms\unit_nwb_profile.csv')
print(f"""[action] Updated PROFILE_PATH to {PROFILE_PATH}""")
OPLUS_PATH = Path(r'D:\drive\omission\outputs\waveforms\unit_refined_categories_v3.csv')
print(f"""[action] Updated OPLUS_PATH to {OPLUS_PATH}""")
OUTPUT_DIR = Path(r'D:\drive\omission\outputs\oglo-figures\figure-8')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

BANDS = {
    'Theta (4-8 Hz)': (4, 8),
    'Alpha (8-13 Hz)': (8, 13),
    'Beta (13-30 Hz)': (13, 30),
    'Low Gamma (30-60 Hz)': (30, 60),
    'High Gamma (60-100 Hz)': (60, 100)
}

def butter_bandpass(lowcut, highcut, fs=1000, order=4):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a

def extract_phase(data, lowcut, highcut, fs=1000):
    b, a = butter_bandpass(lowcut, highcut, fs)
    filtered = filtfilt(b, a, data, axis=-1)
    analytic_signal = hilbert(filtered, axis=-1)
    return np.angle(analytic_signal)

def compute_ppc(phases):
    N = len(phases)
    if N < 2:
        return 0.0
    # PPC = ( |sum(exp(i*theta))|^2 - N ) / (N * (N - 1))
    R_sum = np.sum(np.exp(1j * phases))
    ppc = (np.abs(R_sum)**2 - N) / (N * (N - 1))
    return ppc

def generate_figure_8():
    print("Generating Figure 8: Spike-Field Coupling (PPC) for the Ultimate 9 O+ Neurons")
    
    df_prof = pd.read_csv(PROFILE_PATH, low_memory=False)
    df_oplus = pd.read_csv(OPLUS_PATH)
    
    def extract_ses(s):
        match = re.search(r'ses-(\d+)', str(s))
        return match.group(1) if match else None
        
    df_prof['session_id'] = df_prof['session_nwb'].apply(extract_ses)
    df_prof['probe_id'] = df_prof['probe'].str.extract(r'probe([A-C])')[0].map({'A':0, 'B':1, 'C':2})
    df_prof['local_idx'] = df_prof.groupby(['session_nwb', 'probe_id']).cumcount()
    df_prof['refined_key'] = df_prof['session_id'].astype(str) + "_" + df_prof['unit_id_in_session'].astype(str)
    
    df_oplus['refined_key'] = df_oplus['session_id'].astype(str) + "_" + df_oplus['unit_id'].astype(str)
    
    # Merge to get probe and local_idx and channel
    oplus_full = pd.merge(df_oplus, df_prof[['refined_key', 'probe_id', 'local_idx', 'peak_channel_id']], on='refined_key', how='left')
    
    # Target window: p2 omission
    win_start = 2031
    win_end = 2562
    
    for idx, row in oplus_full.iterrows():
        session = row['session_id']
        probe = row['probe_id']
        l_idx = row['local_idx']
        ch_global = row['peak_channel_id']
        ch_local = ch_global % 128
        area = row['area']
        unit = row['unit_id']
        
        print(f"Processing Unit {unit} (Session {session}, Area {area})...")
        
        spk_path = ARRAY_DIR / f"ses{session}-units-probe{probe}-spk-RXRR.npy"
        lfp_path = ARRAY_DIR / f"ses{session}-probe{probe}-lfp-RXRR.npy"
        
        if not spk_path.exists() or not lfp_path.exists():
            print(f"  Missing arrays for session {session} probe {probe}")
            continue
            
        spk_data = np.load(spk_path) # (trials, units, time)
        lfp_data = np.load(lfp_path) # (trials, channels, time)
        
        if l_idx >= spk_data.shape[1] or ch_local >= lfp_data.shape[1]:
            print(f"  Index out of bounds")
            continue
            
        unit_spikes = spk_data[:, l_idx, win_start:win_end]
        unit_lfp = lfp_data[:, ch_local, win_start:win_end]
        
        # Find spike times (trial_idx, time_idx)
        spike_trials, spike_times = np.where(unit_spikes > 0)
        n_spikes = len(spike_times)
        if n_spikes < 10:
            print(f"  Too few spikes ({n_spikes}) for robust PPC.")
            continue
            
        ppc_results = {}
        band_phases = {}
        
        for band_name, (low, high) in BANDS.items():
            lfp_phase = extract_phase(unit_lfp, low, high)
            # Get phase exactly at spike times
            spk_phases = lfp_phase[spike_trials, spike_times]
            ppc = compute_ppc(spk_phases)
            ppc_results[band_name] = ppc
            band_phases[band_name] = spk_phases
            
        # Find preferred band
        best_band = max(ppc_results, key=ppc_results.get)
        best_ppc = ppc_results[best_band]
        best_phases = band_phases[best_band]
        
        # Create 2-panel figure
        fig = make_subplots(rows=1, cols=2, specs=[[{"type": "xy"}, {"type": "polar"}]],
                            subplot_titles=("Pairwise Phase Consistency (PPC)", f"Phase Distribution<br>{best_band}"))
                            
        # Bar chart
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
        fig.add_trace(go.Bar(
            x=list(ppc_results.keys()),
            y=list(ppc_results.values()),
            marker_color=colors,
            name="PPC"
        ), row=1, col=1)
        
        # Polar Histogram
        # Bin phases into 18 bins (20 degrees each)
        hist, bin_edges = np.histogram(best_phases, bins=18, range=(-np.pi, np.pi))
        bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
        
        fig.add_trace(go.Barpolar(
            r=hist,
            theta=np.degrees(bin_centers),
            marker_color='crimson',
            marker_line_color='black',
            marker_line_width=1,
            opacity=0.8,
            name="Spike Count"
        ), row=1, col=2)
        
        fig.update_layout(
            title=f"Figure 8: Spike-Field Coupling (Omission Window)<br><i>Unit {unit} | {area} | Session {session} | Spikes: {n_spikes}</i>",
            template="plotly_white",
            polar=dict(
                radialaxis=dict(visible=True, showticklabels=True),
                angularaxis=dict(direction="counterclockwise")
            ),
            showlegend=False,
            height=500, width=1000
        )
        
        fig.update_yaxes(title_text="PPC (Spike-Count Corrected)", row=1, col=1)
        
        out_path = OUTPUT_DIR / f'figure_8_sfc_{area}_ses{session}_unit{unit}.html'
        fig.write_html(out_path)
        print(f"  Saved {out_path} (Best Band: {best_band}, PPC: {best_ppc:.3f})")

if __name__ == "__main__":
    generate_figure_8()
