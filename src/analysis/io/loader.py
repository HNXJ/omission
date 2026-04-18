# core
import os
import re
import numpy as np
from pathlib import Path
from collections import defaultdict
from src.analysis.io.logger import log

class DataLoader:
    """
    Core data loader utilizing lazy-loading (mmap) for `.npy` array files.
    Automatically parses the canonical session-area mapping.
    """
    
    CANONICAL_AREAS = ["V1", "V2", "V3d", "V3a", "V4", "MT", "MST", "TEO", "FST", "FEF", "PFC"]
    
    def __init__(self, data_dir: str = "D:/drive/data/arrays", mapping_file: str = "D:/drive/omission/context/overview/session-area-mapping.md"):
        self.data_dir = Path(data_dir)
        self.mapping_file = Path(mapping_file)
        self.area_map = self._parse_mapping()
        log.action(f"""Initialized DataLoader (NPY) with mapping from {mapping_file}""")

    def _parse_mapping(self):
        """Parses the markdown table to build a mapping dict: area -> list of (session, probe, channel_indices)."""
        if not self.mapping_file.exists():
            log.error(f"""Mapping file missing: {self.mapping_file}""")
            return {}
            
        area_map = defaultdict(list)
        with open(self.mapping_file, "r") as f:
            lines = f.readlines()
            
        table_started = False
        for line in lines:
            if "| Session |" in line:
                table_started = True
                continue
            if table_started and line.startswith("|") and not line.startswith("|:---"):
                parts = [p.strip() for p in line.split("|")[1:-1]]
                if len(parts) >= 4:
                    session = parts[0]
                    probe = int(parts[1])
                    areas = [a.strip() for a in parts[2].split(",")]
                    # Alias DP to V4
                    areas = ["V4" if "DP" in a else a for a in areas]
                    total_ch = int(parts[3])
                    
                    n_areas = len(areas)
                    boundaries = np.linspace(0, total_ch, n_areas + 1, dtype=int)
                    
                    for i, area in enumerate(areas):
                        if area in self.CANONICAL_AREAS:
                            start_ch, end_ch = boundaries[i], boundaries[i+1]
                            area_map[area].append({
                                "session": session,
                                "probe": probe,
                                "start_ch": start_ch,
                                "end_ch": end_ch
                            })
        return dict(area_map)

    def get_omission_onset(self, condition: str):
        """Returns the onset of the second stimulus (or omission) relative to p1 start (ms)."""
        # Based on canonical timing: p1=0, d1=531, p2=1031
        return 1031.0

    def get_signal(self, mode: str, condition: str, area: str, align_to: str = "p1", **kwargs):
        """
        Loads signals with flexible alignment.
        align_to: 'p1' (stimulus onset) or 'omission' (1031ms later).
        """
        log.action(f"Extracting {mode} signal for area {area} in condition {condition} (Align: {align_to})")
        
        data_list = self._load_data(mode, condition, area)
        if not data_list: return None
        
        if align_to == "omission":
            onset = self.get_omission_onset(condition)
            # Signal is sampled at 1000Hz, so 1031ms = 1031 samples relative to p1 start (sample 1000 in raw?)
            # Wait, our .npy arrays are already epoched. 
            # In current scripts, sample 1000 is 0ms (p1 onset).
            # So omission onset is at sample 2031.
            aligned_list = []
            for arr in data_list:
                # arr shape: (trials, units/ch, time)
                # Crop to [-1000, +1000] ms relative to omission (Sample 2031)
                # Omission window: 2031 - 1000 = 1031 to 2031 + 1000 = 3031
                if arr.shape[-1] >= 3031:
                    aligned_list.append(arr[:, :, 1031:3031])
                else:
                    log.warning(f"Array too short for omission-local alignment: {arr.shape[-1]}")
            return aligned_list
            
        return data_list

    def _load_data(self, mode, condition, area):
        """Internal raw loader."""
        if area not in self.area_map: return None
        area_entries = self.area_map[area]
        data_list = []
        for entry in area_entries:
            ses = entry["session"]; p = entry["probe"]; start_ch = entry["start_ch"]; end_ch = entry["end_ch"]
            filename = f"ses{ses}-{'units-probe'+str(p)+'-spk' if mode=='spk' else 'probe'+str(p)+'-lfp'}-{condition}.npy"
            file_path = self.data_dir / filename
            if file_path.exists():
                try:
                    arr = np.load(file_path, mmap_mode='r')
                    if mode == "lfp":
                        arr_slice = arr[:, start_ch:end_ch, :]
                    else:
                        u_start = int(arr.shape[1] * (start_ch/128.0))
                        u_end = int(arr.shape[1] * (end_ch/128.0))
                        arr_slice = arr[:, u_start:u_end, :]
                    data_list.append(arr_slice)
                except Exception: pass
        return data_list
        
    def close_all(self):
        pass
