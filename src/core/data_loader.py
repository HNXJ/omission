# core
import os
from pathlib import Path
from typing import Dict, Any, Optional
from pynwb import NWBHDF5IO
from .logger import log

class DataLoader:
    """
    Core data loader utilizing pynwb lazy-loading for memory efficiency.
    Handles canonical signal-agnostic access across the pipeline.
    """
    
    def __init__(self, data_dir: str):
        """
        Args:
            data_dir: The root path to the NWB files (typically D:/drive/data/nwb).
        """
        self.data_dir = Path(data_dir)
        self._open_files = {}  # type: Dict[str, NWBHDF5IO]
        log.action(f"""Initialized DataLoader with data_dir: {self.data_dir}""")

    def load_session(self, session_id: str) -> Any:
        """
        Lazily opens an NWB file and returns the nwbfile object.
        Keeps the IO open until explicitly closed to allow lazy array slicing.
        
        Args:
            session_id: String like 'sub-C31o_ses-230630_rec'
        """
        log.action(f"""Loading session: {session_id}""")
        file_path = self.data_dir / f"{session_id}.nwb"
        
        if not file_path.exists():
            log.error(f"""File not found: {file_path}""")
            raise FileNotFoundError(f"NWB file {file_path} does not exist.")
            
        if session_id not in self._open_files:
            log.progress(f"""Opening NWBHDF5IO for {session_id}""")
            # Using 'r' for read-only lazy-loading
            io = NWBHDF5IO(str(file_path), mode='r', load_namespaces=True)
            self._open_files[session_id] = io
            
        return self._open_files[session_id].read()

    def get_signal(self, session_id: str, mode: str, **kwargs):
        """
        Canonical signal-agnostic loader.
        
        Args:
            session_id: The session NWB ID.
            mode: 'lfp' or 'spk'.
            kwargs: Additional filters (e.g., area, trial_ids, interval_name)
        """
        log.action(f"""Extracting {mode} signal for {session_id} with args {kwargs}""")
        nwb = self.load_session(session_id)
        
        if mode == "lfp":
            return self._extract_lfp(nwb, **kwargs)
        elif mode == "spk":
            return self._extract_spikes(nwb, **kwargs)
        else:
            log.error(f"""Unsupported signal mode: {mode}""")
            raise ValueError(f"Unsupported mode: {mode}. Use 'lfp' or 'spk'.")

    def _extract_lfp(self, nwb: Any, **kwargs):
        """Internal LFP extraction leveraging lazy slicing."""
        log.action(f"""Executing LFP lazy extraction""")
        # Example logic: nwb.processing['ecephys'].data_interfaces['LFP'].electrical_series['LFP']
        # Return the proxy object, allowing downstream slicing to load into RAM
        # Implementation will be fleshed out as specific pipeline paths are added.
        pass

    def _extract_spikes(self, nwb: Any, **kwargs):
        """Internal Spike extraction leveraging lazy slicing."""
        log.action(f"""Executing Spike lazy extraction""")
        # Example logic: nwb.units['spike_times']
        pass
        
    def close_all(self):
        """Closes all active PyNWB IO streams to release file locks."""
        log.action(f"""Closing all active NWB IO streams.""")
        for session_id, io in self._open_files.items():
            log.info(f"""Closing stream for {session_id}""")
            io.close()
        self._open_files.clear()
        
    def __del__(self):
        self.close_all()
