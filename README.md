# device-reader

Reads model, storage capacity, IMEI, and serial number from a USB-connected, unlocked mobile device -- **iOS and Android, one product** -- built from a real device-intake tool, productized and generalized.

## Why this exists

Device-intake workflows need to pull identifying info off a phone before it can be labeled, logged, or entered into inventory, regardless of which platform that phone runs. This reads that info correctly on both, validates the IMEI it finds via the sibling [imei-validator](https://github.com/Ivan-Pinhal-Rodrigues/imei-validator) package, and stays strictly within what each platform's own security model allows -- see [DESIGN.md](DESIGN.md) for why that boundary is deliberate on both sides, not a limitation.

## Install

Not yet published to PyPI (see [DESIGN.md](DESIGN.md) for why) -- install from a clone for now:

```bash
git clone https://github.com/Ivan-Pinhal-Rodrigues/device-reader.git
cd device-reader
pip install -e .                          # core (parsing/validation only)
pip install -e ".[hardware]"              # + iOS access via pymobiledevice3
```

Android access needs the `adb` command-line tool on PATH (Android SDK platform-tools) -- a separate, external install, not a Python package.

## Usage

```python
from device_reader import read_connected_device

info = read_connected_device()  # auto-detects iOS or Android
print(info.model, info.capacity_gb, info.imei, info.serial)
```

```python
from device_reader import read_connected_ios_device, read_connected_android_device

ios_info = read_connected_ios_device()
android_info = read_connected_android_device()
```

## CLI

```bash
device-read
device-read --id 00008030-001A2B3C4D5E6F7A
```

Prints the device's info as JSON: `{"model": "...", "capacity_gb": ..., "imei": "...", "serial": "..."}`. No print date in this output -- reading a device doesn't involve one. `device-intake-station` (a separate, planned project) composes this output with a print timestamp into a full label for `label-printer`.

## What this does and doesn't do

- Reads from a device that is already unlocked (iOS) or USB-debugging-authorized (Android) -- never attempts to bypass either. See [DESIGN.md](DESIGN.md).
- On Android 10+, IMEI and serial number require permissions that plain `adb shell` access doesn't have -- this is surfaced as a clear error, not silently guessed or faked.
- Recognizes iPhone model identifiers from iPhone 11 onward; an unrecognized one is returned as-is. Android model names use manufacturer + model directly (e.g. "Google Pixel 7") rather than a lookup table -- Android's manufacturer fragmentation makes a meaningful table impractical, unlike Apple's cleaner identifier scheme.

## Testing

```bash
pip install -e ".[dev]"
pytest
```

The pure parsing/lookup/rounding logic (shared and per-platform) is fully unit-tested with sample data, and so is the error-handling/parsing logic inside `ios_client.py` and `android_client.py` via a mocked subprocess/import layer. Only the functions inside those two modules that actually talk to a connected device aren't covered by automated tests -- there's no physical device in CI -- and those are verified by hand.

## Design decisions

See [DESIGN.md](DESIGN.md).
