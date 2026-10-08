from pipeline.sql.connection import get_connection
from pipeline.sql.runner import run_query
from pipeline.config import Settings



settings = Settings()
conn = get_connection()

s3_path = f"s3://{settings.s3_bucket}/{settings.raw_prefix}/ingest_date=*/*.json"
staged_path = f"s3://{settings.s3_bucket}/{settings.staged_prefix}/products_deduped.parquet"
mart_path = f"s3://{settings.s3_bucket}/{settings.mart_prefix}/products_modified_daily.parquet"

run_query(conn, f"stage_deduped_products.sql", s3_path=s3_path, staged_path=staged_path)

val = conn.execute(f"select count(*) from read_parquet('{staged_path}')").fetchone()
res = conn.execute(f"select count(distinct code) from read_json_auto('{s3_path}')").df()

rollup =run_query(conn,"rollup_products.sql", staged_path=staged_path, mart_path=mart_path)
print(rollup)

mart_rows = conn.execute(f"select * from read_parquet('{mart_path}') order by modified_date limit 5").df()

print(mart_rows)

mart_total = conn.execute(f"select sum(products) from read_parquet('{mart_path}')").fetchone()
staged_total = conn.execute(f"select count(*) from read_parquet('{staged_path}')").fetchone()

print(mart_total, staged_total)