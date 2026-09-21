import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Settings:
    base_url: str = "https://world.openfoodfacts.org"
    category: str = "snacks"
    page_size: int= 1000
    page: int=1
    user_agent: str = "DataEngPortfolioProject/1.0 (contact: lemuelhmgs@yahoo.com)"
    max_page_per_run: int = 100
    max_retry_attempts: int = 3
    raw_prefix: str="raw/openfoodfacts"
    watermark_key: str="state/watermark.json"
    s3_bucket: str = os.environ.get("S3_BUCKET")
    batch_size: int = 500
    fields: tuple[str, ...]=("code","product_name", "last_modified_t")
    timeout: int = 10
    backoff_multiplier: int = 2
    backoff_min_seconds: int = 2
    backoff_max_seconds: int = 30