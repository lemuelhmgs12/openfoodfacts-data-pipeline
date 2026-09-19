from pipeline.config import Settings
from pipeline.watermark import read_watermark,write_watermark


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

