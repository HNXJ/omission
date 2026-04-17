# core
from ..core.logger import log

def extract_signal_features(data: any, mode: str, **kwargs):
    """
    Canonical signal-agnostic feature extraction.
    
    Args:
        data: The raw data slice from DataLoader.
        mode: 'lfp' (e.g., TFR, bandpower) or 'spk' (e.g., PSTH, Fano factor).
        kwargs: Extraction-specific parameters.
    """
    log.action(f"""Extracting features for mode: {mode} with args {kwargs}""")
    
    if mode == "lfp":
        log.progress(f"""Running LFP feature extraction...""")
        return _process_lfp(data, **kwargs)
    elif mode == "spk":
        log.progress(f"""Running Spike feature extraction...""")
        return _process_spikes(data, **kwargs)
    else:
        log.error(f"""Invalid signal mode: {mode}""")
        raise ValueError(f"Unsupported mode: {mode}")

def _process_lfp(data, **kwargs):
    """Internal LFP processing logic (e.g., TFR)."""
    log.action(f"""_process_lfp invoked""")
    # Example logic to be ported from legacy codebase
    pass

def _process_spikes(data, **kwargs):
    """Internal Spike processing logic (e.g., PSTH)."""
    log.action(f"""_process_spikes invoked""")
    # Example logic to be ported from legacy codebase
    pass
