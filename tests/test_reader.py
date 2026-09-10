import pytest

from device_reader.models import DeviceInfo, MultipleDevicesConnectedError, NoDeviceConnectedError
from device_reader.reader import read_connected_device

SAMPLE = DeviceInfo(model="iPhone 13 Pro", capacity_gb=256, imei="490154203237518", serial="C02D12345678")


def test_dispatches_to_ios_when_only_an_ios_device_is_connected(monkeypatch):
    from device_reader import android_client, ios_client

    monkeypatch.setattr(ios_client, "list_ios_device_udids", lambda: ["ios-udid-1"])
    monkeypatch.setattr(android_client, "list_android_device_serials", list)
    monkeypatch.setattr(ios_client, "read_connected_ios_device", lambda udid=None: SAMPLE)

    assert read_connected_device() is SAMPLE


def test_dispatches_to_android_when_only_an_android_device_is_connected(monkeypatch):
    from device_reader import android_client, ios_client

    monkeypatch.setattr(ios_client, "list_ios_device_udids", list)
    monkeypatch.setattr(android_client, "list_android_device_serials", lambda: ["android-serial-1"])
    monkeypatch.setattr(android_client, "read_connected_android_device", lambda serial=None: SAMPLE)

    assert read_connected_device() is SAMPLE


def test_raises_no_device_when_nothing_connected_on_either_platform(monkeypatch):
    from device_reader import android_client, ios_client

    monkeypatch.setattr(ios_client, "list_ios_device_udids", list)
    monkeypatch.setattr(android_client, "list_android_device_serials", list)

    with pytest.raises(NoDeviceConnectedError):
        read_connected_device()


def test_raises_multiple_when_devices_connected_on_both_platforms(monkeypatch):
    from device_reader import android_client, ios_client

    monkeypatch.setattr(ios_client, "list_ios_device_udids", lambda: ["ios-udid-1"])
    monkeypatch.setattr(android_client, "list_android_device_serials", lambda: ["android-serial-1"])

    with pytest.raises(MultipleDevicesConnectedError):
        read_connected_device()


def test_a_listing_failure_on_one_platform_does_not_block_the_other(monkeypatch):
    from device_reader import android_client, ios_client

    def broken_ios_list():
        raise RuntimeError("pymobiledevice3 not installed or similar")

    monkeypatch.setattr(ios_client, "list_ios_device_udids", broken_ios_list)
    monkeypatch.setattr(android_client, "list_android_device_serials", lambda: ["android-serial-1"])
    monkeypatch.setattr(android_client, "read_connected_android_device", lambda serial=None: SAMPLE)

    assert read_connected_device() is SAMPLE


def test_explicit_identifier_surfaces_the_real_ios_error_instead_of_a_misleading_android_one(
    monkeypatch,
):
    from device_reader import android_client, ios_client
    from device_reader.ios_client import MissingHardwareExtraError

    def broken_ios_list():
        raise MissingHardwareExtraError("pip install 'device-reader[hardware]'")

    monkeypatch.setattr(ios_client, "list_ios_device_udids", broken_ios_list)
    monkeypatch.setattr(android_client, "list_android_device_serials", list)

    with pytest.raises(MissingHardwareExtraError, match="hardware"):
        read_connected_device(identifier="some-ios-udid")
