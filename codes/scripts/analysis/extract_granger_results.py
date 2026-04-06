
import numpy as np
import glob
import nitime.analysis as na
import nitime.timeseries as ts
import re

OMISSION_WINDOW = (4093, 4624)
SAMPLING_RATE = 1000.0
ORDER = 15

BANDS = {
    'beta': (13, 30),
    'gamma': (35, 70)
}

def extract_band_granger():
    target_sessions = ['230630', '230816', '230830']
    
    print("\n--- Spectral Granger Causality Band Results (Omission) ---")
    
    for session_id in target_sessions:
        try:
            f_v1 = glob.glob(f'data/ses{session_id}-probe2-lfp-AAAX.npy')[0]
            f_pfc = glob.glob(f'data/ses{session_id}-probe0-lfp-AAAX.npy')[0]
            
            # Average over trials and channels for a stable population signal
            lfp_v1 = np.mean(np.load(f_v1, mmap_mode='r')[:, :, OMISSION_WINDOW[0]:OMISSION_WINDOW[1]], axis=(0, 1))
            lfp_pfc = np.mean(np.load(f_pfc, mmap_mode='r')[:, :, OMISSION_WINDOW[0]:OMISSION_WINDOW[1]], axis=(0, 1))
            
            combined = np.stack([lfp_v1, lfp_pfc])
            tseries = ts.TimeSeries(combined, sampling_rate=SAMPLING_RATE)
            g_analyzer = na.GrangerAnalyzer(tseries, order=ORDER)
            
            freqs = g_analyzer.frequencies
            # channel 0 is V1, channel 1 is PFC
            # causality_xy[i, j] is causality from j to i
            g_v1_to_pfc = g_analyzer.causality_xy[1, 0, :]
            g_pfc_to_v1 = g_analyzer.causality_yx[0, 1, :]
            
            print(f"Session {session_id}:")
            for band, (f_min, f_max) in BANDS.items():
                mask = (freqs >= f_min) & (freqs <= f_max)
                mean_v1_pfc = np.nanmean(g_v1_to_pfc[mask])
                mean_pfc_v1 = np.nanmean(g_pfc_to_v1[mask])
                
                direction = "V1 -> PFC" if mean_v1_pfc > mean_pfc_v1 else "PFC -> V1"
                print(f"  - {band.upper()} ({f_min}-{f_max} Hz): V1->PFC={mean_v1_pfc:.4f}, PFC->V1={mean_pfc_v1:.4f} [{direction} dominates]")
        except Exception as e:
            print(f"  - Error session {session_id}: {e}")


def main(args=None):
    extract_band_granger()

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Run script')
    # Add arguments here
    args = parser.parse_args()
    if 'main' in globals():
        main(args)
