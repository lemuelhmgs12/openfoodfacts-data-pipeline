from airflow.decorators import dag, task
from datetime import datetime, timedelta


@dag(
    dag_id="openfoodfacts_pipeline",
    start_date=datetime(2026, 10, 1),
    schedule='@daily',        
    catchup=False,         
    default_args={
        "retries": 1,
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
        print("dedupe ran")

    @task
    def rollup():
        print("rollup ran")

    ingest() >> dedupe() >> rollup()


openfoodfacts_pipeline()