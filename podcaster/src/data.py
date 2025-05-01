
from podcaster.src import args

class DataDownloader:
    def __init__(self, args):
        pass

def main():
    a = args.get_args()
    downloader = DataDownloader(a)

if __name__ == "__main__":
    main() 