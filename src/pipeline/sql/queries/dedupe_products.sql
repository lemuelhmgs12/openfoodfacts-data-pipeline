WITH ranked AS (
    SELECT code, last_modified_t, product_name, ecoscore_tags, ingest_date,
           row_number() OVER (PARTITION BY code ORDER BY last_modified_t DESC) AS rnk
    FROM read_json_auto('{s3_path}')
)
SELECT code, last_modified_t, product_name, ecoscore_tags, ingest_date
FROM ranked
WHERE rnk = 1