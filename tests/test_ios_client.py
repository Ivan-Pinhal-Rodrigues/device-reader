import pytest


def test_read_connected_ios_device_raises_clear_error_without_hardware_extra(monkeypatch):
    import builtins

    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "pymobiledevice3" or name.startswith("pymobiledevice3."):
            raise ImportError("No module named 'pymobiledevice3'")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)

    from device_reader.ios_client import MissingHardwareExtraError, read_connected_ios_device

    with pytest.raises(MissingHardwareExtraError, match="pip install"):
        read_connected_ios_device()


def test_a_device_that_fails_at_connect_time_still_raises_device_not_accessible(monkeypatch):
    # Needs the real pymobiledevice3 types/modules to monkeypatch against;
    # CI deliberately doesn't install the `hardware` extra (see ci.yml), so
    # skip rather than fail there -- this still runs wherever it's installed.
    pytest.importorskip("pymobiledevice3")
    import pymobiledevice3.lockdown
    import pymobiledevice3.usbmux
    from pymobiledevice3.exceptions import NotPairedError

    from device_reader.ios_client import DeviceNotAccessibleError, read_connected_ios_device

    class FakeDevice:
        serial = "udid-1"

    async def fake_list_devices():
        return [FakeDevice()]

    async def fake_create_using_usbmux(*args, **kwargs):
        raise NotPairedError("device is not paired")

    monkeypatch.setattr(pymobiledevice3.usbmux, "list_devices", fake_list_devices)
    monkeypatch.setattr(pymobiledevice3.lockdown, "create_using_usbmux", fake_create_using_usbmux)

    with pytest.raises(DeviceNotAccessibleError, match="locked or not yet trusted"):
        read_connected_ios_device(udid="udid-1")
