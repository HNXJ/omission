# core
import argparse
import sys
from pathlib import Path
from src.analysis.io.logger import log
from src.analysis.io.loader import DataLoader

def main():
    """
    Central CLI entry point for the Omission project.
    Consolidates pipeline execution and figure generation.
    """
    parser = argparse.ArgumentParser(description="Omission Project Central Pipeline CLI")
    parser.add_argument("--verbosity", type=float, default=1.0, help="Set the verbosity level (0.0 to 1.0)")
    parser.add_argument("--run-all", action="store_true", help="Run the full analytical batch pipeline (f001-f046)")
    
    args = parser.parse_args()
    log.set_verbosity(args.verbosity)
    log.progress(f"Starting Omission Pipeline CLI...")

    if args.run_all:
        try:
            from src.scripts.run_pipeline import run_all
            run_all()
        except ImportError as e:
            log.error(f"Failed to import pipeline runner: {e}")
            sys.exit(1)
        except Exception as e:
            log.error(f"Pipeline execution failed: {e}")
            sys.exit(1)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
