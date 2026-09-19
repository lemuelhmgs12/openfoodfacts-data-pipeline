import pytest
from botocore.exceptions import ClientError
from pipeline.config import Settings


@pytest.fixture
def settings():
    return Settings(
        max_retry_attempts=3,
        backoff_multiplier=1,
        backoff_min_seconds=1,
        backoff_max_seconds=2,
        s3_bucket="test-bucket",
    )

@pytest.fixture
def fake_s3():
    return FakeS3Client()

@pytest.fixture
def fake_products():
    return [
        {"code": "111", "product_name": "Fake Chips", "last_modified_t": 500},
        {"code": "222", "product_name": "Fake Cookies", "last_modified_t": 400},
    ]

class FakeBody:
    def __init__(self, data: bytes):
        self._data = data

    def read(self):
        return self._data
    
class FakeS3Client:
    def __init__(self):
        self.storage = {}  

    def get_object(self, Bucket, Key):
        if Key in self.storage:
            return {"Body":FakeBody(self.storage[Key])}
        else:
            raise ClientError(
                {"Error": {"Code": "NoSuchKey", "Message": "not found"}},
                "GetObject",
            )
        

    def put_object(self, Bucket, Key, Body):
        self.storage[Key] = Body