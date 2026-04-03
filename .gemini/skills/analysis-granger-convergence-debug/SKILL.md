---
name: analysis-granger-convergence-debug
description: Debugs and assesses the convergence of Granger causality analysis for LFP data between specific brain regions (V1 and PFC). This skill systematically tests various model orders to identify potential issues with model stability or parameter selection for Granger causality computations using the Nitime library.
---
# SKILL: analysis-granger-convergence-debug

## Description
This skill is designed for debugging and evaluating the convergence of Granger causality analysis, particularly when applied to Local Field Potential (LFP) data recorded from distinct brain regions such as the primary visual cortex (V1) and the prefrontal cortex (PFC). It systematically varies the model order parameter within the Granger causality computation (using the `nitime` library) to observe how the causality estimates change. This helps in identifying stable model orders and diagnosing potential issues like overfitting or underfitting, which can lead to non-convergent or unreliable causality results.

## Core Tasks
1.  **Load LFP Data**: Loads pre-processed LFP data from specified NumPy (.npy) files for V1 and PFC for a given session and condition.
2.  **Average & Normalize**: Averages LFP signals across trials and channels, then normalizes them (mean-subtraction and standard deviation division).
3.  **Granger Causality Computation**: Computes Granger causality using `nitime.analysis.GrangerAnalyzer` for a range of specified model orders.
4.  **Convergence Assessment**: Prints and inspects the resulting causality values and the number of `NaN` values for different model orders to assess stability and convergence.

## Inputs
*   **LFP NumPy Files**: Specific `.npy` files containing LFP data for V1 and PFC (e.g., `data/arrays/ses<ID>-probe<ID>-lfp-<COND>.npy`). The script expects files to be present for a hardcoded `session_id` and `AAAX` condition.

## Outputs
*   **Console Output**: Displays Granger causality values (first few elements) for V1->PFC and PFC->V1 directions, along with counts of `NaN` values, for each tested model order.

## Example Use

```python
import numpy as np
import os
import nitime.analysis as na
import nitime.timeseries as ts

# --- Mocking the debug_granger function from debug_granger_convergence.py ---
def mock_debug_granger():
    print("--- Demonstrating Granger Convergence Debug (Mock) ---")
    
    # Create mock LFP data files if they don't exist
    os.makedirs('data/arrays', exist_ok=True)
    
    session_id = '230816'
    
    # Simulate LFP data for V1 and PFC
    # Shape: (trials, channels, timepoints) - simplified for mock
    mock_lfp_v1_data = np.random.randn(10, 10, 531) * 100 # Approx 531 timepoints after slicing
    mock_lfp_pfc_data = np.random.randn(10, 10, 531) * 100
    
    f_v1_mock = f'data/arrays/ses{session_id}-probe2-lfp-AAAX.npy'
    f_pfc_mock = f'data/arrays/ses{session_id}-probe0-lfp-AAAX.npy'
    
    np.save(f_v1_mock, mock_lfp_v1_data)
    np.save(f_pfc_mock, mock_lfp_pfc_data)
    
    print(f"  Mock LFP files created: {f_v1_mock}, {f_pfc_mock}")

    # Load and process mock data as in the original script
    lfp_v1 = np.mean(np.load(f_v1_mock, mmap_mode='r'), axis=(0, 1))
    lfp_pfc = np.mean(np.load(f_pfc_mock, mmap_mode='r'), axis=(0, 1))
    
    # Normalize signals
    lfp_v1 = (lfp_v1 - np.mean(lfp_v1)) / np.std(lfp_v1)
    lfp_pfc = (lfp_pfc - np.mean(lfp_pfc)) / np.std(lfp_pfc)
    
    combined = np.stack([lfp_v1, lfp_pfc])
    tseries = ts.TimeSeries(combined, sampling_rate=1000.0) # Assuming 1000 Hz
    
    print("
  Running Granger Causality for different orders:")
    for order in [5, 10, 15]: # Reduced orders for quicker mock execution
        print(f"
  Order {order}:")
        try:
            g_analyzer = na.GrangerAnalyzer(tseries, order=order)
            g_12 = g_analyzer.causality_xy[1, 0, :] # V1->PFC (assuming V1 is index 0, PFC is 1 in combined)
            g_21 = g_analyzer.causality_yx[0, 1, :] # PFC->V1
            
            print(f"    - V1->PFC (first 3): {g_12[:3]}")
            print(f"    - PFC->V1 (first 3): {g_21[:3]}")
            print(f"    - NaNs in V1->PFC: {np.isnan(g_12).sum()}")
            print(f"    - NaNs in PFC->V1: {np.isnan(g_21).sum()}")
        except Exception as e:
            print(f"    Error computing Granger for order {order}: {e}")

    # Clean up mock files (optional)
    os.remove(f_v1_mock)
    os.remove(f_pfc_mock)
    print("
  Mock LFP files cleaned up.")


# --- Run the demonstration ---
if __name__ == '__main__':
    mock_debug_granger()
```