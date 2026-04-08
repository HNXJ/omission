import numpy as np
import pandas as pd
import io

# Canonical Mapping Table as defined in context/overview/session-area-mapping.md
MAPPING_DATA = """Session,Probe,Areas,Channels
230629,0,"V1,V2",128
230629,1,"V3d,V3a",128
230630,0,PFC,128
230630,1,"V4,MT",128
230630,2,"V3,V1",128
230714,0,"V1,V2",128
230714,1,"V3d,V3a",128
230719,0,"V1,V2",128
230719,1,V4,128
230719,2,"V3d,V3a",128
230720,0,"V1,V2",128
230720,1,"V3d,V3a",128
230721,0,"V1,V2",128
230721,1,"V3d,V3a",128
230816,0,PFC,128
230816,1,"V4,MT",128
230816,2,"V3,V1",128
230818,0,PFC,128
230818,1,"TEO,FST",128
230818,2,"MT,MST",128
230823,0,FEF,128
230823,1,"MT,MST",128
230823,2,"V1,V2,V3",128
230825,0,PFC,128
230825,1,"MT,MST",128
230825,2,"V4,TEO",128
230830,0,PFC,128
230830,1,"V4,MT",128
230830,2,"V1,V3",128
230831,0,FEF,128
230831,1,"MT,MST",128
230831,2,"V4,TEO",128
230901,0,PFC,128
230901,1,"MT,MST",128
230901,2,"V3,V4",128"""

MAPPING_DF = pd.read_csv(io.StringIO(MAPPING_DATA))

def resolve_area_membership(session_id, probe_id, n_probe_channels=128):
    """
    Returns a dictionary mapping area labels to arrays of channel indices 
    within the probe, using deterministic linear boundary splitting.
    """
    row = MAPPING_DF[(MAPPING_DF['Session'] == int(session_id)) & (MAPPING_DF['Probe'] == probe_id)]
    if row.empty:
        return {}
    
    raw_areas = [a.strip() for a in row.iloc[0]['Areas'].split(',')]
    # Canonicalize
    areas = []
    for a in raw_areas:
        if a == 'DP': areas.append('V4')
        elif a == 'V3': areas.extend(['V3d', 'V3a'])
        else: areas.append(a)
        
    n_labels = len(areas)
    edges = np.linspace(0, n_probe_channels, n_labels + 1).astype(int)
    
    membership = {}
    for i, area in enumerate(areas):
        membership[area] = np.arange(edges[i], edges[i+1])
        
    return membership

def get_signal_conditional(
    signal_type="MUAe",
    condition="AAAB",
    area="V1",
    t_pre_ms=1000,
    t_post_ms=4000,
    align_event="p1",
    target_fs=1000,
    spike_bin_ms=1,
    spike_smooth_ms=None
):
    """
    Canonical accessor for signal data: MUAe, LFP, or SPK.
    """
    # Placeholder structure for integration with lfp_io.py / lfp_pipeline.py
    out = {
        "signal_type": signal_type,
        "condition": condition,
        "area": area,
        "align_event": align_event,
        "t_pre_ms": t_pre_ms,
        "t_post_ms": t_post_ms,
        "fs": target_fs,
        "times_ms": np.arange(-t_pre_ms, t_post_ms),
        "sessions": {}
    }
    
    # Integration logic to be populated by pipeline loops
    return out
