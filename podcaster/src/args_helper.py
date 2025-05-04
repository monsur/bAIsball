import argparse
import os
from datetime import datetime, timedelta
from podcaster.src import os_helper

def get_args():
    """Get common arguments used across all scripts."""
    parser = argparse.ArgumentParser("plAI ball!")
    parser.add_argument('--date', type=str, help='Date in YYYYMMDD format (default: yesterday)', 
                       default=(datetime.now() - timedelta(days=1)).strftime('%Y%m%d'))
    parser.add_argument('--delay', type=int, default=2,
                       help='Delay in seconds between downloads (default: 2)')
    parser.add_argument('--prettyprint', action='store_true',
                       help='whether to prettyprint the prompt file')
    
    args = parser.parse_args()
    
    # Validate date format
    try:
        datetime.strptime(args.date, '%Y%m%d')
    except ValueError:
        parser.error("Date must be in YYYYMMDD format")
    
    args.output_root = os_helper.join(os.getcwd(), "podcaster/output")
    args.output_dir = os_helper.join(args.output_root, args.date)
    args.output_data_dir = os_helper.join(args.output_dir, "data")
    args.output_log_dir = os_helper.join(args.output_dir, "logs")
    os_helper.make_dir(args.output_data_dir)
    os_helper.make_dir(args.output_log_dir)

    return args