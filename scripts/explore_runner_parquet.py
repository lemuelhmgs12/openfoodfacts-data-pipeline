from pipeline.sql.connection import get_connection
from pipeline.sql.runner import run_query
from pipeline.config import Settings



settings = Settings()
conn = get_connection()

s3_path = f"s3://{settings.s3_bucket}/{settings.raw_prefix}/ingest_date=*/*.json"
staged_path = f"s3://{settings.s3_bucket}/{settings.staged_prefix}/products_deduped.parquet"

run_query(conn, f"stage_deduped_products.sql", s3_path=s3_path, staged_path=staged_path)

val = conn.execute(f"select count(*) from read_parquet('{staged_path}')").fetchone()
res = conn.execute(f"select count(distinct code) from read_json_auto('{s3_path}')").df()

rollup =run_query(conn,f"rollup_products.sql", staged_path=staged_path)
print(rollup)

