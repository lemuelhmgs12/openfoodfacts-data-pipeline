from pipeline.sql.connection import get_connection

conn = get_connection()
print ("DuckDB connection + s3 succeeded")
result = conn.execute("SELECT * FROM read_json_auto('s3://lemuel-de-portfolio-openfoodfacts/raw/openfoodfacts/ingest_date=2026-09-24/*.json') limit 5").df()
df = conn.execute(""" 
            SELECT COUNT(*) AS total_rows, COUNT(DISTINCT code) AS distinct_products
            FROM read_json_auto('s3://lemuel-de-portfolio-openfoodfacts/raw/openfoodfacts/ingest_date=*/*.json')
                  """).df()
print(df)

schema = conn.execute("""
DESCRIBE SELECT * FROM  read_json_auto('s3://lemuel-de-portfolio-openfoodfacts/raw/openfoodfacts/ingest_date=*/*.json')
                      """).df()

print(schema)




unique_data = conn.execute("""
with ranked as (select code, last_modified_t, product_name, ecoscore_tags, ingest_date, row_number() over(partition by code order by last_modified_t desc) as rnk
                from read_json_auto('s3://lemuel-de-portfolio-openfoodfacts/raw/openfoodfacts/ingest_date=*/*.json'))
    select count(*) from ranked
    where rnk = 1
    
   
                  """).df()

print(unique_data)

ecoscore_result = conn.execute("""
                               select count(*) as total, count(ecoscore_tags) as non_null_ecoscore
                               from read_json_auto('s3://lemuel-de-portfolio-openfoodfacts/raw/openfoodfacts/ingest_date=*/*.json')
                               """).df()

print(ecoscore_result)


