#!/usr/bin/env python3
import argparse
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="Canonical LFP Omission Pipeline")
    parser.add_argument("--nwb", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    logger.info(f"Pipeline started for {args.nwb}")

if __name__ == '__main__':
    main()
