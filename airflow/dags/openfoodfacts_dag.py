from airflow.decorators import dag, task
from datetime import datetime, timedelta




@dag(
    dag_id="openfoodfacts_pipeline",
    start_date=datetime(2026, 10, 1),
    schedule='@daily',        
    catchup=False,         
    default_args={
        "retries": 2,
        "retry_delay": timedelta(minutes=1),
    },
)
def openfoodfacts_pipeline():
    

    @task
    def ingest():
        from pipeline.config import Settings
        from pipeline.orchestrator import run    
        settings = Settings()
        run(settings)
       
        

    @task
    def dedupe():
        from pipeline.config import Settings
        from pipeline.sql import runner
        from pipeline.sql.connection import get_connection

        conn = get_connection()
        
        settings = Settings()
        s3_path = f"s3://{settings.s3_bucket}/{settings.raw_prefix}/ingest_date=*/*.json"
        staged_path = f"s3://{settings.s3_bucket}/{settings.staged_prefix}/products_deduped.parquet"

        runner.run_query(conn, "stage_deduped_products.sql", s3_path=s3_path, staged_path=staged_path)
        conn.close()

        return staged_path

    @task
    def rollup(staged_path):
        from pipeline.sql import runner
        from pipeline.sql.connection import get_connection

        conn = get_connection()
        result = runner.run_query(conn, "rollup_products.sql", staged_path=staged_path)
        print(result)           
        conn.close()
        

    ingested = ingest()
    staged = dedupe()
    rolled = rollup(staged)

    ingested >> staged


openfoodfacts_pipeline()