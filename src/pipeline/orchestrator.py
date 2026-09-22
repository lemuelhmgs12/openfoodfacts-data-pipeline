import logging
from datetime import date,datetime
from pipeline.api_client import OpenFoodFactsClient
from pipeline.watermark import read_watermark, write_watermark
from pipeline.storage import write_batch
from pipeline.api_client import OpenFoodFactsError
from botocore.exceptions import ClientError


logger = logging.getLogger(__name__)




def run(settings, s3_client=None):
    since_epoch = read_watermark(settings, s3_client=s3_client)
    client = OpenFoodFactsClient(settings)

    batch = []
    batch_count = 0
    max_seen = since_epoch or 0

    run_time = datetime.now().strftime("%H-%M-%S")

    try:
        for product in client.iter_products(since_epoch = since_epoch):
            batch.append(product)
            max_seen = max(max_seen, product["last_modified_t"])

            if len(batch) >= settings.batch_size:
                write_batch(settings, batch, date.today(),batch_count, run_time, s3_client=s3_client)
                batch_count += 1
                batch = []

        if batch:
            write_batch(settings, batch, date.today(), batch_count, run_time, s3_client=s3_client)
            batch_count += 1

        write_watermark(settings, max_seen, s3_client=s3_client)
        logger.info(f"Run complete:  {batch_count} batches written, watermark now {max_seen}")

    except OpenFoodFactsError as exc:
        logger.error(f"Api error during pipeline run: {exc}")
        raise
    except ClientError as exc:
        logger.error(f"S3 read/write error during pipeline run: {exc}")
        raise

    except Exception as exc:
        logger.error(f"Pipeline run failed: {exc}")
        raise