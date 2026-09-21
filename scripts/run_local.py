
import logging

from pipeline.config import Settings
from pipeline.orchestrator import run

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

settings = Settings()
print(f"Running against bucket: {settings.s3_bucket}")

run(settings)

print("Run complete.")