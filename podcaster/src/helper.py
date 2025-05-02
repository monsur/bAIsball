import argparse
import logging
import os
import shutil
from datetime import datetime, timedelta

# TODO: Better logging config
logger = logging.getLogger()
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)

def get_logger():
    return logger

def get_args():
    """Get common arguments used across all scripts."""
    parser = argparse.ArgumentParser("plAI ball!")
    parser.add_argument('--date', type=str, help='Date in YYYYMMDD format (default: yesterday)', 
                       default=(datetime.now() - timedelta(days=1)).strftime('%Y%m%d'))
    parser.add_argument('--delay', type=int, default=2,
                       help='Delay in seconds between downloads (default: 2)')
    
    args = parser.parse_args()
    
    # Validate date format
    try:
        datetime.strptime(args.date, '%Y%m%d')
    except ValueError:
        parser.error("Date must be in YYYYMMDD format")
    
    args.output_dir = os.path.join(os.getcwd(), 'podcaster/output', args.date)
    make_dir(args.output_dir)

    logging.basicConfig(filename=os.path.join(args.output_dir, "log.log"),
                        format='%(asctime)s %(message)s',
                        level=logging.DEBUG)

    return args 

def make_dir(path, clean=False):
    os.makedirs(path, exist_ok=True)
    if (clean):
        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            try:
                if os.path.isfile(item_path) or os.path.islink(item_path):
                    os.unlink(item_path)
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)
            except Exception as e:
                print(f"Error deleting {item_path}: {e}")
