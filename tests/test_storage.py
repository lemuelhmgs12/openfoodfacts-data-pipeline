
import json
import pytest
from datetime import date,datetime
from botocore.exceptions import ClientError
from pipeline.storage import write_batch

run_time = datetime.now().strftime("%H-%M-%S")

def test_write_batch_to_s3(fake_s3, fake_products, settings):

    
    ingest_date = date(2026, 9, 5)
    count = 0

    result = write_batch(settings, fake_products, ingest_date, count, run_time, s3_client=fake_s3)
    stored = json.loads(fake_s3.storage[result])


    assert result == f"raw/openfoodfacts/ingest_date=2026-09-05/batch_{run_time}_000.json"
    assert stored == fake_products



def test_write_batch_raises_on_s3_failure(fake_s3, fake_products, settings, mocker):
    mocker.patch.object(fake_s3, "put_object", side_effect=ClientError(
        {"Error": {"Code": "AccessDenied", "Message": "nope"}},
    "PutObject",))

    with pytest.raises(ClientError):
        write_batch(settings, fake_products, date(2026, 9, 5), 0, run_time, s3_client=fake_s3)