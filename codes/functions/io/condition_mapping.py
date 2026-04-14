"""
Canonical Omission Task Condition Mapping.
Centralizes translation from NWB task_condition_number/task_block_number 
to canonical condition labels.
"""
import pandas as pd

def get_canonical_condition_map():
    return {
        'AAAB': [1, 2], 'AXAB': [3], 'AAXB': [4], 'AAAX': [5],
        'BBBA': [6, 7], 'BXBA': [8], 'BBXA': [9], 'BBBX': [10],
        'RRRR': list(range(11, 27)), 'RXRR': list(range(27, 35)),
        'RRXR': [35, 37, 39, 41], 'RRRX': [36, 38, 40, 42] + list(range(43, 51)),
    }

def resolve_condition_name(condition_number, condition_map):
    """Maps raw NWB condition ID to canonical string."""
    try:
        val = int(float(condition_number))
        for name, numbers in condition_map.items():
            if val in numbers:
                return name
    except (ValueError, TypeError):
        return 'Unknown'
    return 'Unknown'
