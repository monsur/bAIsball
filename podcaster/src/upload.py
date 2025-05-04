import boto3
import os
from podcaster.src import args_helper
from podcaster.src import logger_helper
from podcaster.src import os_helper

logger = logger_helper.get_logger(__name__)

def run(args):
    s3 = boto3.client('s3',
        aws_access_key_id=os_helper.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os_helper.getenv("AWS_SECRET_ACCESS_KEY"))

    for root, dirs, files in os.walk(args.output_dir):
        for filename in files:
            # construct the full local path
            source_path = os.path.join(root, filename)
            
            # construct the full upload paths
            relative_path = os.path.relpath(source_path, args.output_dir)
            s3_path = os.path.join(args.date, relative_path)
            
            extra_args = {}
            # If its an MP3, make it publicly accessible
            if (source_path.endswith(".mp3")):
                extra_args["ACL"] = "public-read"

            logger.info("Uploading %s..." % s3_path)
            s3.upload_file(source_path, args.s3_bucket, s3_path, ExtraArgs=extra_args)

if __name__ == "__main__":
    run(args_helper.get_args())