# Skill: TFR Computation
**Purpose**: Perform time-frequency response (TFR) analysis on LFP signals.

## Core API
```python
def compute_tfr_power(lfp_data: np.ndarray, fs: float = 1000.0) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Computes dB-normalized TFR for an array of LFP epochs.
    
    Returns:
        (frequencies, time_points, power_spectrogram)
    """
    pass
```

## Implementation Rules
1. **Normalization**: Baseline subtract using the pre-stimulus interval (-1000ms to 0ms).
2. **Performance**: Utilize fast Fourier transform (FFT) or wavelet-based spectral estimation.
3. **Storage**: Save normalized arrays with metadata sidecars for reproducibility.
