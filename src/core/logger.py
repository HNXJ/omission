# core
import builtins
from typing import Any, Optional

class OmissionLogger:
    """
    Core logger for the Omission project adhering to the GAMMA verbosity rules.
    Verbosity levels scale from 0.0 (silent) to 1.0 (maximum line-by-line verbosity).
    """
    
    def __init__(self, verbosity: float = 1.0):
        """
        Initialize the logger.
        
        Args:
            verbosity: Float between 0.0 and 1.0. 
                       0.0 = Silent
                       0.25 = Errors/Critical only
                       0.50 = Warnings & High-level progress
                       0.75 = Standard operations
                       1.0 = Extreme line-by-line verbosity (default per GAMMA)
        """
        self.verbosity = max(0.0, min(1.0, verbosity))
        
    def set_verbosity(self, verbosity: float):
        self.verbosity = max(0.0, min(1.0, verbosity))

    def _log(self, level_threshold: float, prefix: str, message: Any, **kwargs):
        """Internal logging router based on verbosity threshold."""
        if self.verbosity >= level_threshold:
            builtins.print(f"[{prefix}] {message}", **kwargs)

    def action(self, message: Any, **kwargs):
        """Extreme verbosity (1.0). For line-by-line action printing."""
        self._log(1.0, "action", message, **kwargs)

    def info(self, message: Any, **kwargs):
        """Standard operations (0.75)."""
        self._log(0.75, "info", message, **kwargs)

    def progress(self, message: Any, **kwargs):
        """High-level progress (0.50)."""
        self._log(0.50, "progress", message, **kwargs)

    def warning(self, message: Any, **kwargs):
        """Warnings (0.50)."""
        self._log(0.50, "warning", message, **kwargs)

    def error(self, message: Any, **kwargs):
        """Errors/Critical (0.25)."""
        self._log(0.25, "error", message, **kwargs)

# Global singleton instance default to maximum verbosity per project mandates
log = OmissionLogger(verbosity=1.0)
