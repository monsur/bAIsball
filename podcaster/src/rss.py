import boto3
import datetime
import os
from mutagen.mp3 import MP3
from bs4 import BeautifulSoup, Comment
from podcaster.src import args_helper
from podcaster.src import logger_helper
from podcaster.src import os_helper

logger = logger_helper.get_logger(__name__)

def run(args):
    max_items = 7

    client = boto3.client('s3',
        aws_access_key_id=os_helper.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os_helper.getenv("AWS_SECRET_ACCESS_KEY"))

    rss_text = os_helper.read_file("docs/rss.xml")
    if rss_text is None:
        raise Exception("rss.xml not found!")

    rss_soup = BeautifulSoup(rss_text, 'xml')

    def get_item():
        item = rss_soup.new_tag("item")

        episodeType = rss_soup.new_tag("itunes:episodeType")
        episodeType.string = "full"
        item.append(episodeType)

        title = rss_soup.new_tag("title")
        dateObj = datetime.datetime.strptime(args.date, f"%Y%m%d").date()
        dateStr = dateObj.strftime(f"%A, %B %d, %Y")
        title.string = f"plAI ball! {dateStr}"
        item.append(title)

        description = rss_soup.new_tag("description")
        description.string = f"AI-curated MLB highlights for games on {dateStr}"
        item.append(description)

        guid = rss_soup.new_tag("guid")
        guid.string = args.date
        item.append(guid)

        pubDate = rss_soup.new_tag("pubDate")
        pubDate.string = datetime.datetime.now().strftime("%a, %d %b %Y %H:%M:%S %z")
        item.append(pubDate)

        duration = rss_soup.new_tag("itunes:duration")
        audio = MP3(f"{args.output_dir}/{args.date}-audio.mp3")
        duration.string = str(int(audio.info.length))
        item.append(duration)

        explicit = rss_soup.new_tag("itunes:explicit")
        explicit.string = "false"
        item.append(explicit)

        transcript = rss_soup.new_tag("podcast:transcript",
                                      url=f"https://{args.s3_bucket}.s3.amazonaws.com/audio/{args.date}-transcript.txt",
                                      type="text/plain")
        item.append(transcript)

        enclosure = rss_soup.new_tag("enclosure",
                                     length=os.path.getsize(f"{args.output_dir}/{args.date}-audio.mp3"),
                                     type="audio/mpeg",
                                     url=f"https://{args.s3_bucket}.s3.amazonaws.com/audio/{args.date}-audio.mp3")
        item.append(enclosure)

        return item

    # Retrieve all the item sections
    items = rss_soup.rss.channel.find_all("item")

    # If the date's entry already exists, update the entry.
    exists = False
    for item in items:
        guid = item.find("guid").string.strip()
        if guid == args.date:
            item.replace_with(get_item())
            exists = True

    # If this is a new podcast, upload the MP3 and insert a new entry.
    if not exists:
        rss_soup.rss.channel.find("itunes:explicit").insert_after(get_item())
        source_path = os_helper.join(args.output_dir, f"{args.date}-audio.mp3")
        s3_path = f"audio/{args.date}-audio.mp3"
        logger.info("Uploading from %s to %s..." % (source_path, s3_path))
        client.upload_file(source_path, args.s3_bucket, s3_path, ExtraArgs={"ACL": "public-read"})
        source_path = os_helper.join(args.output_dir, f"{args.date}-transcript.txt")
        s3_path = f"audio/{args.date}-transcript.txt"
        logger.info("Uploading from %s to %s..." % (source_path, s3_path))
        client.upload_file(source_path, args.s3_bucket, s3_path, ExtraArgs={"ACL": "public-read", "ContentType": "text/plain; charset=UTF-8"})

    # Purge old entries
    items = rss_soup.rss.channel.find_all("item")
    if (len(items) > max_items):
        item = items[-1].extract()
        filename = f"audio/{item.guid.string.strip()}-audio.mp3"
        logger.info(f"Deleting file {filename}")
        client.delete_object(Bucket=args.s3_bucket, Key=filename)
        filename = f"audio/{item.guid.string.strip()}-transcript.txt"
        logger.info(f"Deleting file {filename}")
        client.delete_object(Bucket=args.s3_bucket, Key=filename)

    os_helper.write_file(rss_soup.prettify(), "docs/rss.xml")

if __name__ == "__main__":
    run(args_helper.get_args())