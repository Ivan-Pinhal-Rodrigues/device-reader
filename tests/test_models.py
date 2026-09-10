import pytest

from device_reader.models import (
    DeviceInfo,
    InvalidDeviceInfoError,
    MultipleDevicesConnectedError,
    NoDeviceConnectedError,
)


def test_device_info_holds_all_fields():
    info = DeviceInfo(model="iPhone 13 Pro", capacity_gb=256, imei="490154203237518", serial="C02D12345678")
    assert info.model == "iPhone 13 Pro"
    assert info.capacity_gb == 256
    assert info.imei == "490154203237518"
    assert info.serial == "C02D12345678"


def test_device_info_rejects_empty_model():
    with pytest.raises(InvalidDeviceInfoError, match="model"):
        DeviceInfo(model="", capacity_gb=256, imei="490154203237518", serial="C02D12345678")


def test_device_info_rejects_non_positive_capacity():
    with pytest.raises(InvalidDeviceInfoError, match="capacity_gb"):
        DeviceInfo(model="iPhone 13 Pro", capacity_gb=0, imei="490154203237518", serial="C02D12345678")


def test_device_info_rejects_empty_imei():
    with pytest.raises(InvalidDeviceInfoError, match="imei"):
        DeviceInfo(model="iPhone 13 Pro", capacity_gb=256, imei="", serial="C02D12345678")


def test_device_info_rejects_empty_serial():
    with pytest.raises(InvalidDeviceInfoError, match="serial"):
        DeviceInfo(model="iPhone 13 Pro", capacity_gb=256, imei="490154203237518", serial="")


def test_connectivity_exceptions_are_runtime_errors():
    assert issubclass(NoDeviceConnectedError, RuntimeError)
    assert issubclass(MultipleDevicesConnectedError, RuntimeError)
