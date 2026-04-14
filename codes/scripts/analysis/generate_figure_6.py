import numpy as np
from pathlib import Path
from scipy.signal import butter, filtfilt, hilbert
import plotly.graph_objects as go
from codes.functions.lfp.lfp_pipeline import get_signal_conditional
from codes.scripts.analysis.count_conditions import get_condition_map, get_condition_name

OUTPUT_DIR = Path(r'D:\drive\omission\outputs\oglo-figures\figure-6')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
NWB_DIR = Path(r'D:\analysis\nwb')

CANONICAL_AREAS = ['V1', 'V2', 'V3d', 'V3a', 'V4', 'MT', 'MST', 'TEO', 'FST', 'FEF', 'PFC']
BANDS = {'Theta': (4, 8), 'Alpha': (8, 12), 'Beta': (15, 30), 'Gamma': (30, 80)}
BAND_COLORS = {'Theta': '#00FFFF', 'Alpha': '#00FF00', 'Beta': '#D2B48C', 'Gamma': '#8A2BE2'}
WINDOW = (-1.0, 4.0)
FS = 1000

def get_slot(cond_name):
    # Mapping sequences to omission slots
    if cond_name in ['AXAB', 'BXBA', 'RXRR']: return 'P2'
    if cond_name in ['AAXB', 'BBXA', 'RRXR']: return 'P3'
    if cond_name in ['AAAX', 'BBBX', 'RRRX']: return 'P4'
    return 'None'

def butter_bandpass_filter(data, lowcut, highcut, fs, order=3):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return filtfilt(b, a, data, axis=-1)

def compute_band_power(epochs, fs=FS):
    if epochs.size == 0 or np.all(np.isnan(epochs)):
        return None
    powers = {}
    for band, (low, high) in BANDS.items():
        filtered = butter_bandpass_filter(epochs, low, high, fs)
        analytic = hilbert(filtered, axis=-1)
        power = np.abs(analytic)**2
        powers[band] = np.nanmean(np.nanmean(power, axis=0), axis=0)
    return powers

def generate_figure_6(session_file=None):
    if session_file is None:
        session_file = NWB_DIR / 'sub-V198o_ses-230629_rec.nwb'
    
    print(f"Generating Figure 6 for session: {session_file.name}")
    time_vec = np.linspace(WINDOW[0]*1000, WINDOW[1]*1000, int((WINDOW[1]-WINDOW[0])*FS))
    
    cond_map = get_condition_map()
    
    from pynwb import NWBHDF5IO
    with NWBHDF5IO(str(session_file), 'r') as io:
        nwb = io.read()
        df = nwb.intervals['omission_glo_passive'].to_dataframe()
        slots = df['task_condition_number'].apply(lambda x: get_slot(get_condition_name(x, cond_map))).values

    for area in CANONICAL_AREAS:
        try:
            all_epochs = get_signal_conditional(session_file, area, signal_type='LFP', epoch_window=WINDOW)
            if all_epochs.size == 0: continue
            
            # Contrast: Omission (slot) vs Control (RRRR)
            # This logic will need to be refined to select RRRR trials.
            # For now, let's just group by slot to demonstrate.
            for slot in ['P2', 'P3', 'P4']:
                mask = (slots == slot)
                if np.sum(mask) == 0: continue
                # Proceed with plotting logic...
            
            print(f"[infile] generate_figure_6.py [doing] Saved contrast plots for {area}")
        except Exception as e:
            print(f"Error processing {area}: {e}")
