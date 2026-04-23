# core
import numpy as np
import scipy.signal
from src.analysis.io.loader import DataLoader
from src.analysis.io.logger import log

def compute_modulation_index(phase, amplitude, n_bins=18):
    """Tort et al. (2010) Modulation Index."""
    phase_bins = np.linspace(-np.pi, np.pi, n_bins+1)
    bin_idx = np.digitize(phase, phase_bins) - 1
    
    mean_amp = np.zeros(n_bins)
    for b in range(n_bins):
        if np.any(bin_idx == b):
            mean_amp[b] = np.mean(amplitude[bin_idx == b])
    
    if np.sum(mean_amp) == 0: return 0.0
    p = mean_amp / np.sum(mean_amp)
    
    log_n = np.log(n_bins)
    h_p = -np.sum(p[p>0] * np.log(p[p>0]))
    mi = (log_n - h_p) / log_n
    return mi

def analyze_laminar_pac(loader: DataLoader, session: str, probe: int, condition="AXAB"):
    """
    Computes PAC matrix across 8 laminar depths.
    Phase: 8-13Hz (Alpha)
    Amplitude: 30-80Hz (Gamma)
    """
    log.info(f"Analyzing Laminar PAC for Session {session}, Probe {probe}")
    
    # Load LFP (trials, channels, time)
    f_lfp = loader.data_dir / f"ses{session}-probe{probe}-lfp-{condition}.npy"
    if not f_lfp.exists():
        log.warning(f"LFP file missing: {f_lfp}")
        return None
        
    lfp = np.load(f_lfp, mmap_mode='r') # (trials, 128, time)
    n_trials, n_ch, n_times = lfp.shape
    
    # 1. Define layers (8 bins of 16 channels)
    n_layers = 8
    ch_per_layer = n_ch // n_layers
    
    layer_signals = []
    for i in range(n_layers):
        # Mean across channels in layer
        sig = np.mean(lfp[:, i*ch_per_layer : (i+1)*ch_per_layer, :], axis=1)
        layer_signals.append(sig)
        
    # 2. Extract Phase and Amplitude
    # Window: Omission (1031 to 1562)
    win = slice(1031, 1562)
    
    fs = 1000.0
    nyq = fs / 2
    
    # Phase band: Alpha (8-13Hz)
    b_p, a_p = scipy.signal.butter(4, [8/nyq, 13/nyq], btype='bandpass')
    # Amp band: Gamma (30-80Hz)
    b_a, a_a = scipy.signal.butter(4, [30/nyq, 80/nyq], btype='bandpass')
    
    phases = []
    amplitudes = []
    for i in range(n_layers):
        sig = layer_signals[i][:, win].flatten() # Flatten across trials for global MI
        
        # Phase
        f_p = scipy.signal.filtfilt(b_p, a_p, sig)
        phases.append(np.angle(scipy.signal.hilbert(f_p)))
        
        # Amplitude
        f_a = scipy.signal.filtfilt(b_a, a_a, sig)
        amplitudes.append(np.abs(scipy.signal.hilbert(f_a)))
        
    # 3. Compute MI Matrix
    mi_matrix = np.zeros((n_layers, n_layers))
    for p_layer in range(n_layers):
        for a_layer in range(n_layers):
            mi_matrix[p_layer, a_layer] = compute_modulation_index(phases[p_layer], amplitudes[a_layer])
            
    return {
        "mi_matrix": mi_matrix,
        "layers": [f"L{i+1}" for i in range(n_layers)]
    }
