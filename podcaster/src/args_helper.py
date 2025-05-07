import argparse
import os
from datetime import datetime, timedelta

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

    args.s3_bucket = "plai-ball"

    args.output_root = os.path.join(os.getcwd(), "podcaster/output")
    args.output_dir = os.path.join(args.output_root, args.date)
    args.output_data_dir = os.path.join(args.output_dir, "data")
    args.output_log_dir = os.path.join(args.output_dir, "logs")
    os.makedirs(args.output_data_dir, exist_ok=True)
    os.makedirs(args.output_log_dir, exist_ok=True)

    return args