# TODO: pretty this up and use it properly

import logging
import os
import sys
import datetime
from podcaster.src import args_helper

LOG_LEVEL = logging.INFO
_logger = None
_log_identifier = None  # Store the log identifier

def initialize_logger(log_identifier=None):
    global _logger
    global _log_identifier
    if _logger:
        return _logger

    if log_identifier is None:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        _log_identifier = f"log_{timestamp}"
    else:
        _log_identifier = log_identifier

    args = args_helper.get_args()
    LOG_FILE = os.path.join(args.output_log_dir, f"{_log_identifier}.log")

    logging.basicConfig(
        level=LOG_LEVEL,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stderr),
            logging.FileHandler(LOG_FILE)
        ]
    )
    _logger = logging.getLogger()
    return _logger

def get_logger(name):
    if not _logger:
        initialize_logger()  # Initialize with a default if not already done
    return logging.getLogger(name)

def get_log_identifier():
    return _log_identifier
