
from pipeline.config import Settings
from botocore.exceptions import ClientError
from pipeline.watermark import read_watermark,write_watermark


def test_read_watermark_returns_none_when_missing():
    fake_s3 = FakeS3Client()
    settings = Settings(s3_bucket="test-bucket")
    result = read_watermark(settings, s3_client=fake_s3)
    assert result is None

def test_write_then_read_roundtrip():
    fake_s3 = FakeS3Client()
    settings = Settings(s3_bucket="test-bucket")
    write_watermark(settings, 12345, s3_client=fake_s3)
    result = read_watermark(settings, s3_client=fake_s3)
    assert result == 12345

def test_write_overwrites_previous_value():
    fake_s3 = FakeS3Client()
    settings = Settings(s3_bucket="test-bucket")
    write_watermark(settings, 100, s3_client=fake_s3)
    write_watermark(settings, 200, s3_client=fake_s3)
    result = read_watermark(settings, s3_client=fake_s3)
    assert result == 200

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
        

