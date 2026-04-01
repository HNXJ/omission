
import numpy as np
import nitime.analysis as na
import nitime.timeseries as ts

def inspect_nitime():
    # Fake data for 2 channels
    data = np.random.randn(2, 1000)
    tseries = ts.TimeSeries(data, sampling_rate=1000.0)
    g_analyzer = na.GrangerAnalyzer(tseries, order=10)
    
    print(f"Frequencies shape: {g_analyzer.frequencies.shape}")
    print(f"Causality XY shape: {g_analyzer.causality_xy.shape}")
    print(f"Causality YX shape: {g_analyzer.causality_yx.shape}")

if __name__ == '__main__':
    inspect_nitime()
