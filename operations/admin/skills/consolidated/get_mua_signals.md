# Skill: MUA Extraction
**Purpose**: Efficiently load Multi-Unit Activity (MUA) signals for specific cortical areas.

## Core API
```python
def get_mua_by_area_condition(area: str, condition: str, nwb_dir: Path) -> np.ndarray:
    """
    Extracts high-frequency band-passed MUA signals.
    """
    pass
```

## Implementation Rules
1. **Signal Conditioning**: Apply canonical filtering (e.g., 300-3000Hz) if raw MUA is not pre-processed.
2. **Resource Efficiency**: Use the same optimized block-reading logic as the LFP extractor.
3. **Consistency**: Ensure spatial resolution matches the electrode map.
