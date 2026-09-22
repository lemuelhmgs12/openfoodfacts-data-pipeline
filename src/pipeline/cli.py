import logging,sys
from pipeline.config import Settings
from pipeline.orchestrator import run



def main():
    logging.basicConfig(level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",)
    settings = Settings()

    try:
        run(settings)
        return 0
    except Exception as exc:
        logging.exception(f"Pipeline run failed: {exc}")
        return 1
    
if __name__ == "__main__":
    sys.exit(main())

