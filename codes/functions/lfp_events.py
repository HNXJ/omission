"""
lfp_events.py
Event timeline reconstruction for OGLO tasks.
"""
from __future__ import annotations
from typing import Dict, Any
import pandas as pd
from codes.functions.lfp_constants import EVENT_LINES_MS, ALL_CONDITIONS, OMISSION_CONDITIONS


def build_event_table(session: Dict[str, Any]) -> pd.DataFrame:
    """Construct a canonical event table aligned to code 101.0 / p1 onset."""
    trials = session.get("trials", pd.DataFrame()).copy()
    if trials.empty:
        return pd.DataFrame(columns=["trial_id", "condition", "event", "time_ms", "aligned_ms"])

    rows = []
    for _, tr in trials.iterrows():
        trial_id = int(tr.get("trial_id", len(rows)))
        cond = str(tr.get("condition", ""))
        for event, t_ms in EVENT_LINES_MS.items():
            # Use trial-specific time if available, otherwise fallback to canonical
            rows.append({
                "trial_id": trial_id,
                "condition": cond,
                "event": event,
                "time_ms": float(tr.get(f"{event}_time_ms", t_ms)),
                "aligned_ms": float(tr.get(f"{event}_time_ms", t_ms)) - EVENT_LINES_MS["p1"],
            })
    return pd.DataFrame(rows)


def infer_omission_position(condition: str) -> int | None:
    """Returns 1-based position of 'X' in condition string."""
    if "X" not in condition:
        return None
    return condition.index("X") + 1
