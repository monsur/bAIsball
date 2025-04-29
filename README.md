# Baseball Game Summarizer

A Python tool that downloads baseball game content from URLs and generates AI-powered summaries using Google's Gemini AI.

## Features

- Downloads and saves HTML content from baseball game URLs
- Extracts relevant text content from HTML files
- Generates concise summaries using Gemini AI
- Saves summaries to text files

## Setup

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file in the project root and add your Gemini API key:
```
GEMINI_API_KEY=your_api_key_here
```

## Usage

1. Modify the `urls` list in `game_summarizer.py` with the baseball game URLs you want to process.

2. Run the script:
```bash
python game_summarizer.py
```

The script will:
- Download HTML files to the `html_files` directory
- Generate summaries and save them to the `summaries` directory

## Directory Structure

- `html_files/`: Contains downloaded HTML files
- `summaries/`: Contains generated summary text files
- `game_summarizer.py`: Main script
- `requirements.txt`: Project dependencies

## Notes

- The script includes a 2-second delay between requests to avoid overwhelming servers
- HTML content is limited to 8000 characters when generating summaries to comply with API constraints
- Make sure to respect the terms of service of the websites you're scraping 