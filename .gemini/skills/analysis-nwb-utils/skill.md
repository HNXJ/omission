---
name: analysis-nwb-utils
---
# analysis-nwb-utils

## Purpose
Infrastructure utilities: token estimation for LLM prompts, NWBInspector validation, trial-aligned LFP window extraction, and remote model bridge management.

## Input
| Name | Type | Description |
|------|------|-------------|
| text | str | Metadata snippet for token estimation |
| nwb_obj | NWBFile | Live PyNWB instance |
| ref_time | float | Event anchor time (s) |
| pre_ms / post_ms | int | Window bounds around ref_time |

## Output
| Name | Type | Description |
|------|------|-------------|
| token_count | int | ~4 chars/token estimate |
| validation_report | str | Markdown log of NWB errors |
| data_window | ndarray | Clipped array centered on event |

## Example
```python
from src.utils.nwb_utils import estimate_tokens, get_data_from_ref
tokens = estimate_tokens("Session metadata for ses_001...")
lfp_win = get_data_from_ref(nwb_obj, ref_time=120.5, pre_ms=100, post_ms=400)
print(f"""[result] {tokens} tokens, window shape: {lfp_win.shape}""")
```

## Files
- [nwb_utils.py](file:///D:/drive/omission/src/utils/nwb_utils.py) — Implementation
