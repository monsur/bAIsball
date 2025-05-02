import logging
import os
from podcaster.src import helper

logger = helper.get_logger()

class DataDownloader:
    def __init__(self, args):
        self.source_url = f"https://www.espn.com/mlb/scoreboard/_/date/{args.date}"
        self.output_dir = os.path.join(args.output_dir, "data")
        self.delay = args.delay
        helper.make_dir(self.output_dir, True)

    def retrieve_data(self):
        logger.info("Started")
        pass
        
def main():
    a = helper.get_args()
    downloader = DataDownloader(a)
    downloader.retrieve_data()

if __name__ == "__main__":
    main() 