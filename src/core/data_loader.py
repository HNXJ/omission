# core
import os
import re
import numpy as np
from pathlib import Path
from collections import defaultdict
from src.core.logger import log

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

    def get_signal(self, mode: str, condition: str, area: str, **kwargs):
        """
        Loads concatenated, lazy memory-mapped arrays for a specific area across all valid sessions.
        Shape returns: (total_trials_across_sessions, channels_or_units_in_area, time)
        
        Args:
            mode: 'lfp' or 'spk'.
            condition: e.g., 'AAAB', 'AXAB'.
            area: One of the 11 CANONICAL_AREAS.
        """
        log.action(f"""Extracting {mode} signal for area {area} in condition {condition}""")
        
        if area not in self.area_map:
            log.warning(f"""No mapping found for area: {area}""")
            return None
            
        area_entries = self.area_map[area]
        
        # We need a list of arrays from different sessions/probes to concatenate.
        # Since concatenating mmaps drops laziness if not careful, we will yield a list 
        # or load them into RAM. Usually, returning a list of arrays is safer for large datasets.
        # However, to keep it simple, we'll return a list of valid arrays.
        data_list = []
        for entry in area_entries:
            ses = entry["session"]
            p = entry["probe"]
            start_ch = entry["start_ch"]
            end_ch = entry["end_ch"]
            
            if mode == "lfp":
                filename = f"ses{ses}-probe{p}-lfp-{condition}.npy"
            elif mode == "spk":
                filename = f"ses{ses}-units-probe{p}-spk-{condition}.npy"
            else:
                raise ValueError("mode must be 'lfp' or 'spk'")
                
            file_path = self.data_dir / filename
            if file_path.exists():
                try:
                    arr = np.load(file_path, mmap_mode='r')
                    # Shape is (trials, units/channels, time)
                    # Slice the appropriate channels/units
                    
                    if mode == "lfp":
                        # LFP strictly maps to 128 channels, so index applies perfectly
                        arr_slice = arr[:, start_ch:end_ch, :]
                    else:
                        # For SPK, the units are not strictly 1-to-1 with channels, but in the previous pipeline
                        # we either took all units for that probe or mapped them via a metadata file.
                        # For now, we take all units on the probe since previous unit mapping might require `all_units_metadata.csv`.
                        # Since `start_ch` and `end_ch` map strictly to LFP depths, SPK needs a proxy.
                        # We will take all units from this probe as a proxy if unit metadata isn't available,
                        # or evenly split them if multiple areas share a probe.
                        total_units = arr.shape[1]
                        # fractional slice based on channels
                        ratio_start = start_ch / 128.0
                        ratio_end = end_ch / 128.0
                        u_start = int(total_units * ratio_start)
                        u_end = int(total_units * ratio_end)
                        arr_slice = arr[:, u_start:u_end, :]
                        
                    data_list.append(arr_slice)
                except Exception as e:
                    log.warning(f"""Failed to load {file_path}: {e}""")
                    
        return data_list
        
    def close_all(self):
        pass
