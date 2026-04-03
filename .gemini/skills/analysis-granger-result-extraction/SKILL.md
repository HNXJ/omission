---
name: analysis-granger-result-extraction
description: Extracts and analyzes spectral Granger causality results between V1 and PFC LFP signals within defined frequency bands (e.g., Beta, Gamma) and reports the dominant direction of causality. This skill is critical for understanding directed functional connectivity between these regions during specific time windows.
---
# SKILL: analysis-granger-result-extraction

## Description
This skill focuses on extracting and interpreting spectral Granger causality results, specifically applied to Local Field Potential (LFP) signals exchanged between the primary visual cortex (V1) and the prefrontal cortex (PFC). It quantifies the directional influence (causality) within predefined frequency bands (e.g., Beta and Gamma) during a specified time window, typically relevant to an event like visual omission. The output identifies the dominant direction of information flow (V1->PFC or PFC->V1) for each band and session, providing insights into directed functional connectivity.

## Core Tasks
1.  **Load LFP Data**: Loads pre-processed LFP data from specified NumPy (.npy) files for V1 and PFC for a hardcoded set of sessions and condition.
2.  **Average LFP**: Averages LFP signals across trials and channels within a defined `OMISSION_WINDOW`.
3.  **Granger Causality Computation**: Computes spectral Granger causality using `nitime.analysis.GrangerAnalyzer` with a predefined `ORDER` for the model.
4.  **Band-limited Causality Extraction**: Calculates the mean Granger causality within specified frequency `BANDS` (e.g., Beta, Gamma).
5.  **Directional Analysis & Reporting**: Compares V1->PFC and PFC->V1 causality within each band to determine the dominant direction and prints the mean causality values.

## Inputs
*   **LFP NumPy Files**: Specific `.npy` files containing LFP data for V1 and PFC (e.g., `data/arrays/ses<ID>-probe<ID>-lfp-<COND>.npy`). The script targets a hardcoded list of `session_id`s and the `AAAX` condition.
*   **Configuration**: Internal parameters within the script:
    *   `OMISSION_WINDOW`: Tuple defining the time window for analysis (e.g., `(4093, 4624)`).
    *   `SAMPLING_RATE`: Sampling rate of the LFP data (e.g., `1000.0` Hz).
    *   `ORDER`: Model order for Granger causality computation (e.g., `15`).
    *   `BANDS`: Dictionary defining frequency bands (e.g., `{'beta': (13, 30), 'gamma': (35, 70)}`).

## Outputs
*   **Console Output**: Displays, for each session and frequency band, the mean Granger causality values for V1->PFC and PFC->V1, along with an indication of which direction dominates.

## Example Use

```python
import numpy as np
import os
import nitime.analysis as na
import nitime.timeseries as ts
import re
import glob # For mocking glob.glob

# --- Mocking constants from extract_granger_results.py ---
OMISSION_WINDOW = (100, 631) # Simplified window for mock
SAMPLING_RATE = 1000.0
ORDER = 10 # Reduced order for faster mock
BANDS = {
    'beta': (13, 30),
    'gamma': (35, 70)
}

# --- Mocking the extract_band_granger function ---
def mock_extract_band_granger():
    print("--- Demonstrating Spectral Granger Causality Extraction (Mock) ---")
    
    # Create mock LFP data files if they don't exist
    os.makedirs('data/arrays', exist_ok=True)
    
    target_sessions = ['230630', '230816'] # Simplified sessions for mock
    
    for session_id in target_sessions:
        f_v1_mock = f'data/arrays/ses{session_id}-probe2-lfp-AAAX.npy'
        f_pfc_mock = f'data/arrays/ses{session_id}-probe0-lfp-AAAX.npy'
        
        # Simulate LFP data for V1 and PFC - shape: (trials, channels, timepoints)
        # Timepoints based on OMISSION_WINDOW length (631 - 100 = 531)
        mock_lfp_v1_data = np.random.randn(5, 5, 531) * 100 
        mock_lfp_pfc_data = np.random.randn(5, 5, 531) * 100
        
        np.save(f_v1_mock, mock_lfp_v1_data)
        np.save(f_pfc_mock, mock_lfp_pfc_data)
        
        print(f"  Mock LFP files created for session {session_id}.")

    print("
  Running spectral Granger causality extraction for mock data:")
    
    for session_id in target_sessions:
        try:
            # Simulate loading from mock files
            f_v1_path = f'data/arrays/ses{session_id}-probe2-lfp-AAAX.npy'
            f_pfc_path = f'data/arrays/ses{session_id}-probe0-lfp-AAAX.npy'
            
            lfp_v1_full = np.load(f_v1_path, mmap_mode='r')
            lfp_pfc_full = np.load(f_pfc_path, mmap_mode='r')

            # Mock actual data slicing
            lfp_v1 = np.mean(lfp_v1_full, axis=(0, 1))
            lfp_pfc = np.mean(lfp_pfc_full, axis=(0, 1))
            
            combined = np.stack([lfp_v1, lfp_pfc])
            tseries = ts.TimeSeries(combined, sampling_rate=SAMPLING_RATE)
            
            g_analyzer = na.GrangerAnalyzer(tseries, order=ORDER)
            
            freqs = g_analyzer.frequencies
            g_v1_to_pfc = g_analyzer.causality_xy[1, 0, :]
            g_pfc_to_v1 = g_analyzer.causality_yx[0, 1, :]
            
            print(f"
  Session {session_id}:")
            for band, (f_min, f_max) in BANDS.items():
                mask = (freqs >= f_min) & (freqs <= f_max)
                mean_v1_pfc = np.nanmean(g_v1_to_pfc[mask])
                mean_pfc_v1 = np.nanmean(g_pfc_to_v1[mask])
                
                direction = "V1 -> PFC" if mean_v1_pfc > mean_pfc_v1 else "PFC -> V1"
                print(f"    - {band.upper()} ({f_min}-{f_max} Hz): V1->PFC={mean_v1_pfc:.4f}, PFC->V1={mean_pfc_v1:.4f} [{direction} dominates]")
        except Exception as e:
            print(f"    - Error session {session_id}: {e}")

    # Clean up mock files (optional)
    for session_id in target_sessions:
        os.remove(f'data/arrays/ses{session_id}-probe2-lfp-AAAX.npy')
        os.remove(f'data/arrays/ses{session_id}-probe0-lfp-AAAX.npy')
    print("
  Mock LFP files cleaned up.")


# --- Run the demonstration ---
if __name__ == '__main__':
    mock_extract_band_granger()
```