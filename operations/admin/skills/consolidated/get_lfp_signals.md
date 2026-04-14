# Skill: LFP Extraction
**Purpose**: Efficiently load LFP signals for specific cortical areas and condition groups from frozen NWB datasets.

## Core API
```python
def get_lfp_by_area_condition(area: str, condition: str, nwb_dir: Path) -> np.ndarray:
    """
    Extracts LFP traces for a specified area and condition across all available NWB sessions.
    
    Args:
        area: e.g., 'PFC', 'V1', 'MST'
        condition: e.g., 'omission', 'passive', 'active'
        nwb_dir: Path to directory containing NWB files.
    """
    pass
```

## Implementation Rules
1. **Lazy I/O**: Access NWB files via `get_nwb_io()` context.
2. **Channel Mapping**: Use the session-specific `electrodes` table to resolve area-specific channel IDs per probe.
3. **Chunked Reads**: Always perform block-reads to avoid trial-by-trial random access overhead.
4. **Caching**: Precompute session-stable area-to-probe maps once per session.
