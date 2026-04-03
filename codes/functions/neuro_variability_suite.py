
import numpy as np
import scipy.ndimage as ndimage
try:
    import cupy as cp
    HAS_CUDA = True
except ImportError:
    HAS_CUDA = False

class NeuroVariabilitySuite:
    """
    Expert implementation of Neural Variability Quenching Algorithms.
    Adheres to Churchland et al. (2010) standards for Discrete (MMFF) 
    and Continuous (Across-trial variance) signal modalities.
    """

    @staticmethod
    def get_sliding_window_counts(spikes, win_size=50, step=10):
        """
        Efficiently compute spike counts using a sliding window.
        Input: spikes (Trials, Neurons, Time) - binary 3D array
        Output: counts (Neurons, TimeBins, Trials) - spike counts
        """
        n_trials, n_neurons, n_time = spikes.shape
        time_bins = np.arange(0, n_time - win_size + 1, step)
        n_bins = len(time_bins)
        
        # Reshape to (Neurons, Trials, Time) for better memory alignment
        spikes_trans = np.transpose(spikes, (1, 0, 2))
        counts = np.zeros((n_neurons, n_bins, n_trials), dtype=np.float32)
        
        for i, t in enumerate(time_bins):
            # Sum over the window for all neurons and trials simultaneously
            counts[:, i, :] = np.sum(spikes_trans[:, :, t:t+win_size], axis=2)
            
        return counts, time_bins

    @staticmethod
    def compute_mmff(counts, hist_bins=None, min_neurons=5, repeats=20):
        """
        Implementation of the Mean-Matching Algorithm (Churchland 2010).
        Input: counts (Neurons, TimeBins, Trials)
        Output: fano_traces (TimeBins,) - Mean-matched Fano Factor
        """
        n_neurons, n_bins, n_trials = counts.shape
        
        # Calculate mean and variance across trials for each neuron and time bin
        mu = np.mean(counts, axis=2)
        var = np.var(counts, axis=2, ddof=1)
        
        valid_mask = mu > 0
        
        if hist_bins is None:
            all_means = mu[valid_mask]
            if len(all_means) == 0:
                return np.full(n_bins, np.nan)
            hist_bins = np.linspace(0, np.percentile(all_means, 98), 30)
            
        # 1. Compute the Greatest Common Distribution (GCD) across all time points
        bin_counts = []
        for t in range(n_bins):
            m_t = mu[:, t][valid_mask[:, t]]
            counts_t, _ = np.histogram(m_t, bins=hist_bins)
            bin_counts.append(counts_t)
        
        bin_counts = np.array(bin_counts)
        gcd = np.min(bin_counts, axis=0)
        
        fano_trace_accum = np.zeros((repeats, n_bins))
        
        for r in range(repeats):
            for t in range(n_bins):
                m_t = mu[:, t]
                v_t = var[:, t]
                valid_t = valid_mask[:, t]
                
                if np.sum(valid_t) < min_neurons:
                    fano_trace_accum[r, t] = np.nan
                    continue
                    
                matched_ms = []
                matched_vs = []
                
                for b in range(len(hist_bins) - 1):
                    idx = np.where(valid_t & (m_t >= hist_bins[b]) & (m_t < hist_bins[b+1]))[0]
                    n_to_keep = int(gcd[b])
                    
                    if n_to_keep > 0 and len(idx) >= n_to_keep:
                        chosen = np.random.choice(idx, n_to_keep, replace=False)
                        matched_ms.extend(m_t[chosen])
                        matched_vs.extend(v_t[chosen])
                
                if len(matched_ms) >= min_neurons:
                    slope, _ = np.polyfit(matched_ms, matched_vs, 1)
                    fano_trace_accum[r, t] = slope
                else:
                    fano_trace_accum[r, t] = np.nan
        
        # Mean across repeats
        fano_trace = np.nanmean(fano_trace_accum, axis=0)
        return fano_trace

    @staticmethod
    def compute_continuous_mmv(data, win_size=50, step=10, repeats=20):
        """
        Computes Mean-Matched Variation (MMV) for continuous signals.
        Matches the distribution of Mean Absolute Value (MAV) across time points.
        Input: data (Channels, Trials, Time)
        Output: mmv_trace (TimeBins,)
        """
        n_ch, n_trials, n_time = data.shape
        time_bins = np.arange(0, n_time - win_size + 1, step)
        n_bins = len(time_bins)
        
        # Calculate MAV and Variance for each channel and window
        # Shape: (Channels, TimeBins, Trials)
        mav = np.zeros((n_ch, n_bins, n_trials))
        var = np.zeros((n_ch, n_bins, n_trials))
        
        for i, t in enumerate(time_bins):
            win_data = data[:, :, t:t+win_size]
            mav[:, i, :] = np.mean(np.abs(win_data), axis=2)
            var[:, i, :] = np.var(win_data, axis=2, ddof=1)
            
        # Flatten Channels into the 'Neuron' equivalent for matching
        # Shape: (Channels * TimeBins, Trials) -> No, (Channels, TimeBins) means/vars
        # We match distributions across (Channel, Condition) pairs at each time point
        mu = np.mean(mav, axis=2) # (Channels, TimeBins)
        v = np.mean(var, axis=2)  # (Channels, TimeBins)
        
        # Use standard MMFF matching logic on MAV vs Variance
        # ... (rest of matching logic similar to MMFF)
        valid_mask = mu > 0
        all_means = mu[valid_mask]
        if len(all_means) == 0: return np.full(n_bins, np.nan)
        hist_bins = np.linspace(0, np.percentile(all_means, 98), 30)
        
        bin_counts = []
        for t in range(n_bins):
            counts_t, _ = np.histogram(mu[:, t][valid_mask[:, t]], bins=hist_bins)
            bin_counts.append(counts_t)
        gcd = np.min(np.array(bin_counts), axis=0)
        
        mmv_accum = np.zeros((repeats, n_bins))
        for r in range(repeats):
            for t in range(n_bins):
                m_t = mu[:, t]
                v_t = v[:, t]
                valid_t = valid_mask[:, t]
                
                matched_ms = []
                matched_vs = []
                for b in range(len(hist_bins)-1):
                    idx = np.where(valid_t & (m_t >= hist_bins[b]) & (m_t < hist_bins[b+1]))[0]
                    n_to_keep = int(gcd[b])
                    if n_to_keep > 0 and len(idx) >= n_to_keep:
                        chosen = np.random.choice(idx, n_to_keep, replace=False)
                        matched_ms.extend(m_t[chosen])
                        matched_vs.extend(v_t[chosen])
                
                if len(matched_ms) > 3:
                    slope, _ = np.polyfit(matched_ms, matched_vs, 1)
                    mmv_accum[r, t] = slope
                else:
                    mmv_accum[r, t] = np.nan
                    
        return np.nanmean(mmv_accum, axis=0)

    @staticmethod
<<<<<<< Updated upstream
    def detect_bursts(data, fs=1000, band=(35, 80), threshold_factor=3.0):
        """
        Detects oscillatory bursts in a specific band.
        Input: data (Trials, Time)
        Output: burst_mask (Trials, Time) - binary
        """
=======
    def detect_bursts(data, fs=1000, band=(35, 70), threshold_factor=3.0):
        """
        Detects oscillatory bursts in a specific band (Default: Gamma 35-70Hz).
        Input: data (Trials, Time)
        Output: burst_mask (Trials, Time) - binary
        """
        data = np.nan_to_num(data)
>>>>>>> Stashed changes
        from scipy.signal import butter, filtfilt, hilbert
        nyq = 0.5 * fs
        b, a = butter(4, [band[0]/nyq, band[1]/nyq], btype='band')
        filtered = filtfilt(b, a, data, axis=-1)
        envelope = np.abs(hilbert(filtered, axis=-1))
        
        # Threshold relative to median (robust to outliers)
        threshold = threshold_factor * np.median(envelope)
        return (envelope > threshold).astype(np.int8)

    @staticmethod
    def get_total_variation_score(var_trace, window=None):
        """
        Aggregates time-resolved cross-trial variance into a scalar score.
        Identifies excessively noisy channels.
        """
        if window is not None:
            score = np.mean(var_trace[:, window[0]:window[1]], axis=1)
        else:
            score = np.mean(var_trace, axis=1)
        return score

def apply_post_hoc_smoothing(trace, sigma=2.0):
    """
    Applies 1D Gaussian smoothing to a trace, handling NaNs correctly.
    """
    trace = np.array(trace)
    nan_mask = np.isnan(trace)
    if np.all(nan_mask):
        return trace
    
    # Interpolate NaNs for smoothing
    valid_idx = np.where(~nan_mask)[0]
    if len(valid_idx) > 1:
        trace_interp = np.interp(np.arange(len(trace)), valid_idx, trace[valid_idx])
        smoothed = ndimage.gaussian_filter1d(trace_interp, sigma=sigma)
        smoothed[nan_mask] = np.nan # Restore NaNs
        return smoothed
    else:
        return trace
