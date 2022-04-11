#!/usr/bin/env python3.9
#coding:utf-8
import argparse, logging
from pathlib import Path
from src.configure_logging import configure_logging
from src.config import config
from src.hyphe import run_task

logger = logging.getLogger('csv')

def main() -> None:
    parser = argparse.ArgumentParser(description="Corpus scripts")
    parser.add_argument("--log-file", default=config.paths.LOG_FILEPATH, type=Path, help="Path of the logs file to use")
    parser.add_argument("--log-file-level", default="DEBUG", help="Logging level to use")
    args = parser.parse_args()
    log_file_level = getattr(logging, args.log_file_level)
    configure_logging(args.log_file, log_file_level)
    run_task(args.corpus_name)

if __name__ == "__main__":
    main()
