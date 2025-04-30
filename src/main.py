import argparse
from datetime import datetime, timedelta
from src.downloader.downloader import ContentDownloader
from src.sanitizer.sanitizer import HTMLSanitizer
from src.ai.summarizer import GameSummarizer
import time
import os

def main():
    parser = argparse.ArgumentParser(description='Process baseball game summaries')
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
    args = parser.parse_args()

    # Validate date format
    try:
        datetime.strptime(args.date, '%Y%m%d')
    except ValueError:
        print("Error: Date must be in YYYYMMDD format")
        return

    # Create output directories
    os.makedirs(args.raw_dir, exist_ok=True)
    os.makedirs(args.sanitized_dir, exist_ok=True)
    os.makedirs(args.output_dir, exist_ok=True)

    # Download box scores
    print("Downloading box scores...")
    downloader = ContentDownloader(args.raw_dir)
    scoreboard_url = f"https://www.espn.com/mlb/scoreboard/_/date/{args.date}"
    downloaded_files = downloader.retrieve_scores(scoreboard_url, args.delay)
    
    if not downloaded_files:
        print("No files downloaded. Exiting.")
        return

    # Sanitize HTML files
    print("\nSanitizing HTML files...")
    sanitizer = HTMLSanitizer(args.raw_dir, args.sanitized_dir)
    sanitizer.process_files(filter_html=args.filter)

    # Generate summaries
    print("\nGenerating summaries...")
    summarizer = GameSummarizer(args.sanitized_dir, args.output_dir)
    summarizer.process_files()

if __name__ == "__main__":
    main() 