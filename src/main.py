import argparse
from datetime import datetime, timedelta
from src.downloader.downloader import ContentDownloader
from src.sanitizer.sanitizer import ContentSanitizer
from src.ai.summarizer import GameSummarizer
import time

def main():
    parser = argparse.ArgumentParser(description='Generate baseball game summaries')
    parser.add_argument('--date', type=str, help='Date in YYYYMMDD format (default: yesterday)', 
                       default=(datetime.now() - timedelta(days=1)).strftime('%Y%m%d'))
    parser.add_argument('--raw-dir', type=str, default='raw_html',
                       help='Directory for raw HTML files (default: raw_html)')
    parser.add_argument('--sanitized-dir', type=str, default='sanitized_html',
                       help='Directory for sanitized HTML files (default: sanitized_html)')
    parser.add_argument('--output-dir', type=str, default='summaries',
                       help='Directory for summary files (default: summaries)')
    parser.add_argument('--filter', action='store_true',
                       help='Remove script tags from HTML files')
    parser.add_argument('--delay', type=int, default=60,
                       help='Delay in seconds between downloads (default: 60)')
    args = parser.parse_args()

    # Step 1: Download content
    print("\n=== Downloading Content ===")
    downloader = ContentDownloader(args.raw_dir)
    scoreboard_url = f"https://www.espn.com/mlb/scoreboard/_/date/{args.date}"
    box_score_urls = downloader.get_box_score_urls(scoreboard_url)
    
    if not box_score_urls:
        print("No box score URLs found. Exiting.")
        return
    
    for url in box_score_urls:
        print(f"Downloading: {url}")
        downloader.download_content(url)
        if url != box_score_urls[-1]:
            time.sleep(args.delay)

    # Step 2: Process content
    print("\n=== Processing Content ===")
    sanitizer = ContentSanitizer(args.raw_dir, args.sanitized_dir)
    sanitizer.process_files(args.filter)

    # Step 3: Generate summary
    print("\n=== Generating Summary ===")
    summarizer = GameSummarizer(args.sanitized_dir, args.output_dir)
    summarizer.process_files()

if __name__ == "__main__":
    main() 