from pipeline.sql.connection import get_connection
from pipeline.sql.runner import run_query
from pipeline.config import Settings
from pathlib import Path



settings = Settings()
conn = get_connection()

s3_path = f"s3://{settings.s3_bucket}/{settings.raw_prefix}/ingest_date=*/*.json"

df = run_query(conn, f"dedupe_products.sql", s3_path)

print(df.shape)
print(df.head())

ingest_date_rollup = run_query(conn, f"products_by_ingest_date.sql", s3_path)

print (ingest_date_rollup.head())
