# core
import os
import re
import numpy as np
from pathlib import Path
from collections import defaultdict
from src.analysis.io.logger import log
from src.analysis.io.eye_mapper import EyeDataMapper

class DataLoader:
    """
    Core data loader utilizing lazy-loading (mmap) for `.npy` array files.
    Automatically parses the canonical session-area mapping.
    """
    
    CANONICAL_AREAS = ["V1", "V2", "V3d", "V3a", "V4", "MT", "MST", "TEO", "FST", "FEF", "PFC"]
    
    def __init__(self, data_dir: str = None, mapping_file: str = None):
        # Resolve paths relative to repo root
        root = Path(__file__).parent.parent.parent.parent
        self.data_dir = Path(data_dir) if data_dir else root.parent / "data" / "arrays"
        self.mapping_file = Path(mapping_file) if mapping_file else root / "context" / "overview" / "session-area-mapping.md"
        self.area_map = self._parse_mapping()
        self.eye_mapper = EyeDataMapper()
        log.action(f"Initialized DataLoader (NPY) with mapping from {self.mapping_file}")

    def get_eye_data_path(self, session: str) -> Path:
        """Resolves the exact .bhv2.mat file specifically for oculomotor (EYE) analysis."""
        return self.eye_mapper.get_behavioral_file(session)

    def _parse_mapping(self):
        """Parses the markdown table to build a mapping dict: area -> list of (session, probe, channel_indices)."""
        if not self.mapping_file.exists():
            log.error(f"Mapping file missing: {self.mapping_file}")
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
                        # Filter for canonical areas
                        if any(a in area for a in self.CANONICAL_AREAS):
                            start_ch, end_ch = boundaries[i], boundaries[i+1]
                            area_map[area].append({
                                "session": session,
                                "probe": probe,
                                "start_ch": start_ch,
                                "end_ch": end_ch,
                                "total_ch": total_ch
                            })
        return dict(area_map)

    def get_omission_onset(self, condition: str):
        """Returns the onset of the omission relative to p1 start (ms)."""
        # Family-aware timing
        if any(f in condition for f in ["AXAB", "BXBA", "RXRR"]): return 1031.0 # p2
        if any(f in condition for f in ["AAXB", "BBXA", "RRXR"]): return 2062.0 # p3
        if any(f in condition for f in ["AAAX", "BBBX", "RRRX"]): return 3093.0 # p4
        return 1031.0 # Default to p2

    def get_signal(self, mode: str, condition: str, area: str, align_to: str = "p1", **kwargs):
        """
        Loads signals with flexible alignment.
        align_to: 'p1' (stimulus onset) or 'omission' (family-aware).
        """
        log.action(f"Extracting {mode} signal for area {area} in condition {condition} (Align: {align_to})")
        
        data_list = self._load_data(mode, condition, area)
        if not data_list: return None
        
        if align_to == "omission":
            onset_ms = self.get_omission_onset(condition)
            # Sample 1000 is 0ms (p1 onset). Omission onset sample = 1000 + onset_ms
            onset_sample = 1000 + int(onset_ms)
            
            aligned_list = []
            for arr in data_list:
                # Crop to [-1000, +1000] ms relative to omission
                start = onset_sample - 1000
                end = onset_sample + 1000
                if arr.shape[-1] >= end:
                    aligned_list.append(arr[:, :, start:end])
                else:
                    log.warning(f"Array too short for omission alignment (End: {end}, Shape: {arr.shape[-1]})")
            return aligned_list
            
        return data_list

    def _load_data(self, mode, condition, area):
        """Internal raw loader."""
        if area not in self.area_map: return None
        area_entries = self.area_map[area]
        data_list = []
        for entry in area_entries:
            ses = entry["session"]; p = entry["probe"]; start_ch = entry["start_ch"]; end_ch = entry["end_ch"]; total_ch = entry["total_ch"]
            filename = f"ses{ses}-{'units-probe'+str(p)+'-spk' if mode=='spk' else 'probe'+str(p)+'-lfp'}-{condition}.npy"
            file_path = self.data_dir / filename
            if file_path.exists():
                try:
                    arr = np.load(file_path, mmap_mode='r')
                    if mode == "lfp":
                        arr_slice = arr[:, start_ch:end_ch, :]
                    else:
                        # Improved SPK assignment: use total_ch from mapping
                        u_start = int(arr.shape[1] * (start_ch / total_ch))
                        u_end = int(arr.shape[1] * (end_ch / total_ch))
                        arr_slice = arr[:, u_start:u_end, :]
                    data_list.append(arr_slice)
                except Exception: pass
        return data_list
        
    def get_output_dir(self, fig_id: str):
        """Returns the canonical output directory for a specific figure."""
        root = Path(__file__).parent.parent.parent.parent
        out_dir = root.parent / "outputs" / "oglo-8figs" / fig_id
        out_dir.mkdir(parents=True, exist_ok=True)
        return out_dir

    def close_all(self):
        pass
