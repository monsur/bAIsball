import boto3
import datetime
from bs4 import BeautifulSoup, Comment
from podcaster.src import args_helper
from podcaster.src import os_helper

def run(args):
    client = boto3.client('s3',
        aws_access_key_id=os_helper.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os_helper.getenv("AWS_SECRET_ACCESS_KEY"))
    
    resource = boto3.resource('s3',
        aws_access_key_id=os_helper.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os_helper.getenv("AWS_SECRET_ACCESS_KEY"))
#    my_bucket = resource.Bucket(args.s3_bucket)
#    for my_bucket_object in my_bucket.objects.all():
#        print(my_bucket_object)

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
        
        explicit = rss_soup.new_tag("itunes:explicit")
        explicit.string = "false"
        item.append(explicit)
        
        enclosure = rss_soup.new_tag("enclosure", type="audio/mpeg", url=f"https://plai-ball.s3.amazonaws.com/audio/{args.date}-audio.mp3")
        item.append(enclosure)

        return item
    
    rss_soup.rss.channel.find("itunes:explicit").insert_after(get_item())
    #rss_soup.find("rss").find("channel").insert(1, get_item())
    
    os_helper.write_file(rss_soup.prettify(), "docs/rss.xml")

if __name__ == "__main__":
    run(args_helper.get_args())