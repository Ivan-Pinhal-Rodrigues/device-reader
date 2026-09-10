import pytest

from device_reader.ios_parsing import parse_ios_device_info
from device_reader.models import InvalidDeviceInfoError

VALID_LOCKDOWN = {
    "ProductType": "iPhone14,2",
    "SerialNumber": "C02D12345678",
    "InternationalMobileEquipmentIdentity": "490154203237518",
}
VALID_AFC = {"FSTotalBytes": "254000000000"}


def test_parses_a_complete_valid_response():
    info = parse_ios_device_info(VALID_LOCKDOWN, VALID_AFC)
    assert info.model == "iPhone 13 Pro"
    assert info.serial == "C02D12345678"
    assert info.imei == "490154203237518"
    assert info.capacity_gb == 256


def test_falls_back_to_raw_product_type_when_unrecognized():
    lockdown = dict(VALID_LOCKDOWN, ProductType="iPhone99,9")
    info = parse_ios_device_info(lockdown, VALID_AFC)
    assert info.model == "iPhone99,9"


def test_raises_when_reported_imei_fails_validation():
    lockdown = dict(VALID_LOCKDOWN, InternationalMobileEquipmentIdentity="000000000000001")
    with pytest.raises(InvalidDeviceInfoError, match="IMEI"):
        parse_ios_device_info(lockdown, VALID_AFC)


def test_raises_when_fstotalbytes_missing():
    with pytest.raises(InvalidDeviceInfoError, match="FSTotalBytes"):
        parse_ios_device_info(VALID_LOCKDOWN, {})
