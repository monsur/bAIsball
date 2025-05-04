import boto3
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

if __name__ == "__main__":
    run(args_helper.get_args())