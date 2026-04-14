# Skill: Single Unit Extraction
**Purpose**: Efficiently load spike times/data for single units in specific cortical areas and condition groups.

## Core API
```python
def get_spikes_by_area_condition(area: str, condition: str, nwb_dir: Path) -> pd.DataFrame:
    """
    Extracts spike information (times, unit_id) for a specified area and condition.
    
    Args:
        area: e.g., 'PFC', 'V1'
        condition: e.g., 'omission'
    """
    pass
```

## Implementation Rules
1. **Metadata-First**: Load unit tables lazily. Filter by area using session metadata.
2. **Context Safety**: Ensure IO handles are closed promptly after extraction.
3. **Data Format**: Return spike times as a standardized DataFrame for downstream analysis.
