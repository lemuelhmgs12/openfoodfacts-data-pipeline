from pipeline.sql.connection import get_connection

con = get_connection()
print ("DuckDB connection + s3 succeeded")
result = con.execute("SELECT * FROM read_json_auto('s3://lemuel-de-portfolio-openfoodfacts/raw/openfoodfacts/ingest_date=2026-09-24/*.json') limit 5").df()
print(result)