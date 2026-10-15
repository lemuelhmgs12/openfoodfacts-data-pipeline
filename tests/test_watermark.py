import pytest
import logging
from pipeline.config import Settings
from pipeline.watermark import read_watermark,write_watermark
from botocore.exceptions import ClientError

def test_read_watermark_returns_none_when_missing(fake_s3, settings):
    
    
    result = read_watermark(settings, s3_client=fake_s3)
    assert result is None

def test_write_then_read_roundtrip(fake_s3,settings):
   
    
    write_watermark(settings, 12345, s3_client=fake_s3)
    result = read_watermark(settings, s3_client=fake_s3)
    assert result == 12345

def test_write_overwrites_previous_value(fake_s3,settings):
    
    
    write_watermark(settings, 100, s3_client=fake_s3)
    write_watermark(settings, 200, s3_client=fake_s3)
    result = read_watermark(settings, s3_client=fake_s3)
    assert result == 200

def test_read_watermark_failure(fake_s3, settings, mocker, caplog):

    mocker.patch.object(fake_s3, "get_object", side_effect=ClientError(
    {"Error": {"Code": "AccessDenied", "Message": "nope"}},
    "GetObject",))


    with caplog.at_level(logging.ERROR), pytest.raises(ClientError):
        read_watermark(settings,s3_client=fake_s3)




    result = [r.getMessage() for r in caplog.records if r.levelname == "ERROR"]
    assert len(result) == 1
    assert "Unexpected error reading watermark" in result[0]



def test_write_watermark_failue(fake_s3, settings, mocker, caplog):

    mocker.patch.object(fake_s3, "put_object", side_effect=ClientError(
        {"Error": {"Code": "AccessDenied", "Message": "nope"}},
            "PutObject",
    ))

    with caplog.at_level(logging.ERROR), pytest.raises(ClientError):
        write_watermark(settings, 100, s3_client=fake_s3)

    result  = [r.getMessage() for r in caplog.records if r.levelname == "ERROR"]

    assert len(result) == 1
    assert "Failed to write watermark:" in result[0]
