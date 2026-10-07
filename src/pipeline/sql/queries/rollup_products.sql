SELECT CAST(to_timestamp(last_modified_t)AT TIME ZONE 'UTC' AS DATE) AS modified_date,
       COUNT(*) AS products
FROM read_parquet('{staged_path}')
GROUP BY modified_date
ORDER BY modified_date