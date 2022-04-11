#coding:utf-8
import logging
from pathlib import Path

def configure_logging(path:Path, log_file_level:int) -> None:
    logger = logging.getLogger("corpus_builder")
    handler1 = logging.StreamHandler()
    handler2 = logging.FileHandler(filename=path, mode="w", encoding="utf-8")
    handler1.setLevel(logging.INFO)
    handler2.setLevel(log_file_level)
    console_formatter = logging.Formatter("%(filename)s@%(lineno)d - %(levelname)s - %(message)s")
    logfile_formatter = logging.Formatter("%(asctime)s - %(filename)s@%(lineno)d - %(levelname)s - %(message)s", datefmt="%H:%M:%S")
    handler1.setFormatter(console_formatter)
    handler2.setFormatter(logfile_formatter)
    logger.addHandler(handler1)
    logger.addHandler(handler2)
    logger.setLevel(logging.DEBUG)

