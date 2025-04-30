import argparse
from datetime import datetime, timedelta

def get_common_args(description):
    """Get common arguments used across all scripts."""
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('--date', type=str, help='Date in YYYYMMDD format (default: yesterday)', 
                       default=(datetime.now() - timedelta(days=1)).strftime('%Y%m%d'))
    parser.add_argument('--raw-dir', type=str, default='output/raw_html',
                       help='Directory to save raw HTML files (default: output/raw_html)')
    parser.add_argument('--sanitized-dir', type=str, default='output/sanitized_html',
                       help='Directory to save sanitized HTML files (default: output/sanitized_html)')
    parser.add_argument('--output-dir', type=str, default='output/summaries',
                       help='Directory to save summary files (default: output/summaries)')
    parser.add_argument('--delay', type=int, default=2,
                       help='Delay in seconds between downloads (default: 2)')
    parser.add_argument('--filter', action='store_true',
                       help='Filter HTML content (remove script, style, and link tags)')
    return parser.parse_args()

def validate_date(date_str):
    """Validate date format."""
    try:
        datetime.strptime(date_str, '%Y%m%d')
        return True
    except ValueError:
        return False 