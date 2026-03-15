"""
File: utils/logger.py
Purpose: Setup logging for the pipeline
"""

import logging
import os

def setup_logger(name="pipeline", log_level=logging.INFO):
    """
    Setup a logger that prints to terminal and writes to file
    """
    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    os.makedirs("logs", exist_ok=True)

    if not logger.handlers:
        ch = logging.StreamHandler()
        ch.setLevel(log_level)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)

        fh = logging.FileHandler("logs/pipeline.log")
        fh.setLevel(log_level)
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    return logger