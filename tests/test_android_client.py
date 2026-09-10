import subprocess

import pytest


def test_run_adb_raises_clear_error_when_adb_binary_missing(monkeypatch):
    from device_reader.android_client import AdbNotFoundError, _run_adb

    def fake_run(*args, **kwargs):
        raise FileNotFoundError("adb not found")

    monkeypatch.setattr(subprocess, "run", fake_run)

    with pytest.raises(AdbNotFoundError, match="platform-tools"):
        _run_adb("devices")


def test_list_android_device_serials_parses_authorized_devices(monkeypatch):
    from device_reader import android_client

    class FakeResult:
        stdout = "List of devices attached\nABC123\tdevice\nDEF456\tunauthorized\n"

    monkeypatch.setattr(subprocess, "run", lambda *a, **k: FakeResult())

    assert android_client.list_android_device_serials() == ["ABC123"]


def test_read_imei_raises_field_restricted_error_on_short_output(monkeypatch):
    from device_reader.android_client import AndroidFieldRestrictedError, _read_imei

    class FakeResult:
        stdout = "Result: Parcel(00000000    'no.perm..' )"

    monkeypatch.setattr(subprocess, "run", lambda *a, **k: FakeResult())

    with pytest.raises(AndroidFieldRestrictedError, match="READ_PHONE_STATE"):
        _read_imei("ABC123")


def test_read_imei_ignores_hex_address_labels_outside_quotes(monkeypatch):
    from device_reader.android_client import _read_imei

    class FakeResult:
        stdout = (
            "Result: Parcel(\n"
            "  0x00000000: 00000000 00000010 '1.2.3.4.5.6.7.8.'\n"
            "  0x00000010: 00000000            '9.0.1.2.3.4.5.'    )\n"
        )

    monkeypatch.setattr(subprocess, "run", lambda *a, **k: FakeResult())

    # Digits inside the quotes only: 1,2,3,4,5,6,7,8,9,0,1,2,3,4,5 -> 15 digits
    # (a full IMEI length, matching validate_imei's requirement). The
    # 0x00000000/0x00000010 address labels are OUTSIDE the quotes and must
    # be excluded -- if they leaked in, this would fail differently (either
    # raising, since old code's broader scrape would behave differently on
    # this input, or returning a value polluted with those digits).
    assert _read_imei("ABC123") == "123456789012345"


def test_read_connected_android_device_rejects_a_serial_not_in_the_authorized_list(monkeypatch):
    from device_reader.android_client import read_connected_android_device
    from device_reader.models import NoDeviceConnectedError

    class FakeResult:
        stdout = "List of devices attached\nABC123\tdevice\n"

    monkeypatch.setattr(subprocess, "run", lambda *a, **k: FakeResult())

    with pytest.raises(NoDeviceConnectedError, match="TYPO-SERIAL"):
        read_connected_android_device(serial="TYPO-SERIAL")
