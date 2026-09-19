import boto3
import json
from botocore.exceptions import ClientError
import logging

logger = logging.getLogger(__name__)

def write_batch(settings, products, ingest_date, count, s3_client=None):

    s3 = s3_client if s3_client is not None else boto3.client("s3")

    s3_key = f"{settings.raw_prefix}/ingest_date={ingest_date.isoformat()}/batch_{count:03d}.json"

    prod_data = json.dumps(products).encode("utf-8")

    try:
        s3.put_object(Bucket = settings.s3_bucket, Key = s3_key, Body = prod_data)
    except ClientError as exc:
        logger.error(f"Failed to write data into s3 bucket: {exc}")
        raise
    return s3_key