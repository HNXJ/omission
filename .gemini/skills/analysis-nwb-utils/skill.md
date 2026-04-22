---
name: analysis-nwb-utils
description: Low-level utility library for NWB manipulation. Provides helper functions for token estimation, remote model inference, and read-side validation.
---
# skill: analysis-nwb-utils

## When to Use
Use this skill for infrastructural tasks supporting NWB analysis. It is designed for:
- Estimating token counts for LLM-based metadata parsing (e.g., Qwen-72B integration).
- Running read-only validation (NWBInspector) to check for best-practice compliance.
- Extracting specific trial-aligned LFP windows for rapid debugging.
- Managing remote model bridge connections for secondary analysis agents.

## What is Input
- **Raw Text**: Metadata snippets for token estimation.
- **NWB Objects**: Live `pynwb.NWBFile` instances.
- **Reference Times**: Event anchors (e.g., Code 101.0) for time-series extraction.

## What is Output
- **Token Count**: Integer estimate of prompt size.
- **Validation Report**: Markdown-formatted log of NWB schema/metadata errors.
- **Data Windows**: Clipped NumPy arrays centered on specific behavioral events.

## Algorithm / Methodology
1. **Token Estimation**: Uses a `~4 chars/token` heuristic to budget prompt sizes for sub-agent calls.
2. **Remote Bridge**: Forwards structured prompts to the Office M3-Max server via a specialized API.
3. **NWB Validation**: Wraps `pynwb-validate` and `NWBInspector` to audit files without modification.
4. **Time Extraction**: Implements `get_data_from_ref` to slice LFP based on relative offsets (pre/post ms).

## Placeholder Example
```python
from src.utils.nwb_utils import estimate_tokens, get_data_from_ref

# 1. Budget a prompt
tokens = estimate_tokens("Session metadata summary for ses_001...")
print(f"Estimated tokens: {tokens}")

# 2. Extract a 500ms window around a specific event
lfp_window = get_data_from_ref(nwb_obj, ref_time=120.5, pre_ms=100, post_ms=400)
```

## Relevant Context / Files
- [analysis-nwb-read-guardrails](file:///D:/drive/omission/.gemini/skills/analysis-nwb-read-guardrails/skill.md) — For safety rules during extraction.
- [src/utils/qwen_subagent.py](file:///D:/drive/omission/src/utils/qwen_subagent.py) — Implementation of the remote bridge.
