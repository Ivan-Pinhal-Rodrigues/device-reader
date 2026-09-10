import json

from device_reader.cli import main

SAMPLE_DICT = {
    "model": "iPhone 13 Pro",
    "capacity_gb": 256,
    "imei": "490154203237518",
    "serial": "C02D12345678",
}


def test_reads_and_prints_json(monkeypatch, capsys):
    import device_reader.reader as reader_module

    def fake_read(identifier=None):
        from device_reader.models import DeviceInfo

        return DeviceInfo(**SAMPLE_DICT)

    monkeypatch.setattr(reader_module, "read_connected_device", fake_read)

    exit_code = main([])

    assert exit_code == 0
    captured = capsys.readouterr()
    assert json.loads(captured.out) == SAMPLE_DICT


def test_surfaces_device_errors_clearly(monkeypatch, capsys):
    import device_reader.reader as reader_module
    from device_reader.models import NoDeviceConnectedError

    def fake_read_failure(identifier=None):
        raise NoDeviceConnectedError("no supported device (iOS or Android) detected over USB")

    monkeypatch.setattr(reader_module, "read_connected_device", fake_read_failure)

    exit_code = main([])

    assert exit_code != 0
    captured = capsys.readouterr()
    assert "no supported device" in captured.err


def test_passes_through_explicit_identifier(monkeypatch):
    import device_reader.reader as reader_module

    captured = {}

    def fake_read(identifier=None):
        from device_reader.models import DeviceInfo

        captured["identifier"] = identifier
        return DeviceInfo(**SAMPLE_DICT)

    monkeypatch.setattr(reader_module, "read_connected_device", fake_read)

    main(["--id", "abc123"])

    assert captured["identifier"] == "abc123"
