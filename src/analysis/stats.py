# core
from ..core.logger import log

def compute_statistics(data: any, stat_type: str, **kwargs):
    """
    Canonical signal-agnostic statistics computation.
    
    Args:
        data: The extracted features or raw data.
        stat_type: The type of statistic to compute (e.g., 'fano', 'zscore', 'granger').
        kwargs: Additional parameters for the statistical method.
    """
    log.action(f"""Computing statistics for type: {stat_type} with args {kwargs}""")
    
    if stat_type == "fano":
        log.progress(f"""Computing Fano Factor...""")
        return _compute_fano(data, **kwargs)
    elif stat_type == "zscore":
        log.progress(f"""Computing Z-Score...""")
        return _compute_zscore(data, **kwargs)
    else:
        log.error(f"""Invalid stat_type: {stat_type}""")
        raise ValueError(f"Unsupported stat_type: {stat_type}")

def _compute_fano(data, **kwargs):
    """Internal Fano Factor logic."""
    log.action(f"""_compute_fano invoked""")
    pass

def _compute_zscore(data, **kwargs):
    """Internal Z-Score logic."""
    log.action(f"""_compute_zscore invoked""")
    pass
