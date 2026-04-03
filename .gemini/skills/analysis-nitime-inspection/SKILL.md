---
name: analysis-nitime-inspection
description: Provides a quick utility to inspect the output structure and dimensions of core `nitime.analysis` components, specifically the `GrangerAnalyzer`. This skill is useful for familiarizing oneself with `nitime`'s data representations for Granger causality, aiding in debugging or integration with other analysis pipelines.
---
# SKILL: analysis-nitime-inspection

## Description
This skill offers a simplified, self-contained demonstration of how to use `nitime`'s `GrangerAnalyzer` and inspect its output attributes. It generates synthetic multi-channel time-series data, processes it through the Granger causality pipeline, and then prints the shapes of the resulting frequency array and causality matrices (`causality_xy`, `causality_yx`). This is particularly useful as a rapid sanity check or for new users to understand the expected data structures returned by `nitime` functions, facilitating quick integration and debugging in more complex causality analyses.

## Core Tasks
1.  **Generate Synthetic Data**: Creates a 2-channel array of random Gaussian noise to simulate time-series data.
2.  **Create `TimeSeries` Object**: Encapsulates the synthetic data into a `nitime.timeseries.TimeSeries` object with a specified sampling rate.
3.  **Initialize `GrangerAnalyzer`**: Instantiates a `nitime.analysis.GrangerAnalyzer` with the `TimeSeries` object and a predefined model order.
4.  **Print Output Shapes**: Accesses and prints the NumPy `shape` attribute for the `frequencies` array and the `causality_xy` and `causality_yx` matrices from the `GrangerAnalyzer`.

## Inputs
*   No external inputs. The script generates its own synthetic data.

## Outputs
*   **Console Output**: Displays the shapes of the `frequencies` array, `causality_xy` matrix, and `causality_yx` matrix, which are key components of the Granger causality analysis output in `nitime`.

## Example Use

```python
import numpy as np
import nitime.analysis as na
import nitime.timeseries as ts

# --- Mocking the inspect_nitime function ---
def mock_inspect_nitime():
    print("--- Demonstrating Nitime Inspection (Mock) ---")
    
    # Generate fake data for 2 channels, 1000 time points
    data = np.random.randn(2, 1000)
    
    # Create a nitime TimeSeries object
    tseries = ts.TimeSeries(data, sampling_rate=1000.0) # Assuming 1000 Hz
    
    # Initialize GrangerAnalyzer with a model order
    print("  Initializing GrangerAnalyzer...")
    g_analyzer = na.GrangerAnalyzer(tseries, order=10) # Using order 10
    
    # Print shapes of key outputs
    print(f"  Frequencies shape: {g_analyzer.frequencies.shape}")
    print(f"  Causality XY (from Y to X) shape: {g_analyzer.causality_xy.shape}")
    print(f"  Causality YX (from X to Y) shape: {g_analyzer.causality_yx.shape}")

# --- Run the demonstration ---
if __name__ == '__main__':
    mock_inspect_nitime()
```