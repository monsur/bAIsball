import os
from src.downloader.downloader import ContentDownloader
from src.sanitizer.sanitizer import ContentSanitizer
from src.ai.summarizer import GameSummarizer
from src.args import get_common_args

def main():
    args = get_common_args('Process baseball game summaries')

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
    sanitizer = ContentSanitizer(args.raw_dir, args.sanitized_dir)
    sanitizer.process_files(filter_html=args.filter)

    # Generate summaries
    print("\nGenerating summaries...")
    summarizer = GameSummarizer(args.sanitized_dir, args.output_dir)
    summarizer.process_files()

if __name__ == "__main__":
    main() 