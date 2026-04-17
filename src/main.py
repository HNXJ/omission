# core
import argparse
from pathlib import Path
from src.core.logger import log
from src.core.data_loader import DataLoader
from src.analysis.signal import extract_signal_features

def main():
    """
    Central CLI entry point for the Omission project.
    Consolidates pipeline execution and figure generation.
    """
    parser = argparse.ArgumentParser(description="Omission Project Central Pipeline CLI")
    parser.add_argument("--verbosity", type=float, default=1.0, help="Set the verbosity level (0.0 to 1.0)")
    parser.add_argument("--data-dir", type=str, default="D:/drive/data/nwb", help="Path to NWB data directory")
    parser.add_argument("--run-pipeline", type=str, choices=["lfp", "spk"], help="Run the core signal extraction pipeline")
    parser.add_argument("--session", type=str, help="Specific session ID to process")
    
    args = parser.parse_args()
    log.set_verbosity(args.verbosity)
    log.progress(f"""Starting Omission Pipeline...""")
    log.action(f"""Arguments received: {args}""")

    if args.run_pipeline:
        if not args.session:
            log.error(f"""A --session must be specified when using --run-pipeline.""")
            return
            
        try:
            loader = DataLoader(data_dir=args.data_dir)
            
            # Example lazy-loading pipeline execution
            log.progress(f"""Executing pipeline mode: {args.run_pipeline} for session: {args.session}""")
            
            # This would lazily return the signal object
            signal_proxy = loader.get_signal(session_id=args.session, mode=args.run_pipeline)
            
            # Process features via canonical paths
            features = extract_signal_features(data=signal_proxy, mode=args.run_pipeline)
            
            log.progress(f"""Pipeline '{args.run_pipeline}' completed successfully for session {args.session}.""")
            
        except Exception as e:
            log.error(f"""Pipeline execution failed: {e}""")
        finally:
            if 'loader' in locals():
                loader.close_all()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
