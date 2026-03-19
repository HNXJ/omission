
import numpy as np
import glob
import nitime.analysis as na
import nitime.timeseries as ts

def debug_granger():
    session_id = '230816'
    f_v1 = glob.glob(f'data/ses{session_id}-probe2-lfp-AAAX.npy')[0]
    f_pfc = glob.glob(f'data/ses{session_id}-probe0-lfp-AAAX.npy')[0]
    
    # Average over trials and channels
    lfp_v1 = np.mean(np.load(f_v1, mmap_mode='r')[:, :, 4093:4624], axis=(0, 1))
    lfp_pfc = np.mean(np.load(f_pfc, mmap_mode='r')[:, :, 4093:4624], axis=(0, 1))
    
    # Normalize signals
    lfp_v1 = (lfp_v1 - np.mean(lfp_v1)) / np.std(lfp_v1)
    lfp_pfc = (lfp_pfc - np.mean(lfp_pfc)) / np.std(lfp_pfc)
    
    combined = np.stack([lfp_v1, lfp_pfc])
    tseries = ts.TimeSeries(combined, sampling_rate=1000.0)
    
    for order in [5, 10, 15, 20]:
        print(f"\nOrder {order}:")
        g_analyzer = na.GrangerAnalyzer(tseries, order=order)
        g_12 = g_analyzer.causality_xy[1, 0, :]
        g_21 = g_analyzer.causality_yx[0, 1, :]
        
        print(f"  - V1->PFC (first 5): {g_12[:5]}")
        print(f"  - PFC->V1 (first 5): {g_21[:5]}")
        print(f"  - NaNs in V1->PFC: {np.isnan(g_12).sum()}")
        print(f"  - NaNs in PFC->V1: {np.isnan(g_21).sum()}")

if __name__ == '__main__':
    debug_granger()
