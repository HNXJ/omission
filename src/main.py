# core
import argparse
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
    parser.add_argument("--run-all", action="store_true", help="Run the full analytical batch pipeline (Fig 1-30)")
    
    args = parser.parse_args()
    log.set_verbosity(args.verbosity)
    log.progress(f"Starting Omission Pipeline CLI...")

    if args.run_all:
        from src.scripts.run_pipeline import run_all
        run_all()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
