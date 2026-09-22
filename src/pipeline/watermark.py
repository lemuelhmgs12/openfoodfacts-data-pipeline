import json
import boto3
from botocore.exceptions import ClientError
import logging

logger = logging.getLogger(__name__)

def read_watermark(settings, s3_client=None):
    s3 = s3_client if s3_client is not None else boto3.client("s3")

    try:
        obj = s3.get_object(Bucket=settings.s3_bucket, Key = settings.watermark_key)
        body =json.loads(obj["Body"].read())
        logger.info(f"Current watermark: {body["last_modified_t"]}")
        return body["last_modified_t"]

    except ClientError as exc:
        if exc.response["Error"]["Code"] == "NoSuchKey":
            logger.info("No prior watermark found.")
            return None
        else:
            logger.error(f"Unexpected error reading watermark: {exc}")
    
            raise 

def write_watermark(settings, value, s3_client=None):
    s3 = s3_client if s3_client is not None else boto3.client("s3")

    data = {"last_modified_t" : value}
    body = json.dumps(data).encode("utf-8")

    try:
        s3.put_object(Bucket = settings.s3_bucket, Key = settings.watermark_key, Body = body)
    except ClientError as exc:
        logger.error(f"Failed to write watermark: {exc}")
        raise