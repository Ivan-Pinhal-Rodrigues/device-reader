import pytest

from device_reader.android_parsing import parse_android_device_info, parse_df_output
from device_reader.models import InvalidDeviceInfoError

DF_OUTPUT = """Filesystem      1K-blocks    Used Available Use% Mounted on
/dev/block/dm-7  251000000 100000000 151000000  40% /data
"""


def test_parse_df_output_extracts_total_bytes():
    assert parse_df_output(DF_OUTPUT) == 251_000_000 * 1024


def test_parse_df_output_raises_on_missing_data_row():
    with pytest.raises(InvalidDeviceInfoError, match="no data row"):
        parse_df_output("Filesystem      1K-blocks    Used Available Use% Mounted on\n")


def test_parses_a_complete_valid_response():
    getprop_values = {"ro.product.manufacturer": "Google", "ro.product.model": "Pixel 7"}
    # 254_000_000_000 bytes (~254GB raw, same realistic value Task 5's iOS
    # test uses) rounds up to the 256GB tier. This is deliberately a
    # different number from DF_OUTPUT above -- this test exercises
    # parse_android_device_info's capacity-tier integration, not
    # parse_df_output's byte conversion, so they don't need to match.
    info = parse_android_device_info(
        getprop_values,
        storage_bytes=254_000_000_000,
        imei="490154203237518",
        serial="ABC123XYZ",
    )
    assert info.model == "Google Pixel 7"
    assert info.imei == "490154203237518"
    assert info.serial == "ABC123XYZ"
    assert info.capacity_gb == 256


def test_combines_manufacturer_and_model_even_when_manufacturer_missing():
    getprop_values = {"ro.product.manufacturer": "", "ro.product.model": "Pixel 7"}
    info = parse_android_device_info(
        getprop_values, storage_bytes=64_000_000_000, imei="490154203237518", serial="ABC123XYZ"
    )
    assert info.model == "Pixel 7"


def test_raises_when_reported_imei_fails_validation():
    getprop_values = {"ro.product.manufacturer": "Google", "ro.product.model": "Pixel 7"}
    # "000000000000000" would NOT work here -- all-zero digits trivially sum
    # to 0, which IS Luhn-valid (confirmed the hard way in Task 5). This value
    # has its rightmost (undoubled) digit changed to 1, giving digit-sum 1,
    # which genuinely fails the Luhn check.
    with pytest.raises(InvalidDeviceInfoError, match="IMEI"):
        parse_android_device_info(
            getprop_values,
            storage_bytes=64_000_000_000,
            imei="000000000000001",
            serial="ABC123XYZ",
        )
