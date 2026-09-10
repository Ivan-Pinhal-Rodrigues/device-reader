"""Thin adapter over the `adb` command-line tool (Android Debug Bridge,
part of Android SDK platform-tools) -- the only Android-hardware-touching
code in this package. Untestable end-to-end in an environment without a
physical, USB-debugging-enabled Android device connected (the four
tests here cover the pure command-building/parsing logic via a mocked
subprocess, not real hardware); verify the rest by hand against real
devices.

Security/privacy boundary: on Android 10+ (API level 29+), reading a
device's IMEI requires the READ_PHONE_STATE permission AND being a
system/privileged app -- neither a regular app nor plain (non-root) adb
shell access qualifies. Serial number access is similarly restricted
since Android 8. This tool does not attempt to work around either
restriction (e.g. by requiring root) -- it surfaces a clear error
instead, mirroring the same boundary already established on the iOS
side.

IMEI extraction caveat: on the one path where an IMEI read is actually
permitted (Android <=9, or a rooted device), `_read_imei` pulls digits
only from the quoted ASCII columns of the `service call iphonesubinfo 1`
Parcel dump (the "'........9.4.0.1.'" portions), not from the
hex-address labels (e.g. "0x00000000:") or raw hex words that surround
them and are not part of the actual payload. This is a best-effort
heuristic based on the standard binder Parcel dump format, and has NOT
been verified against a real device response where the read is actually
permitted -- no such hardware is available to test against in this
environment.
"""

import re
import subprocess

from .android_parsing import parse_android_device_info, parse_df_output
from .models import DeviceInfo, MultipleDevicesConnectedError, NoDeviceConnectedError


class AdbNotFoundError(RuntimeError):
    """Raised when the `adb` binary isn't found on PATH."""


class AndroidFieldRestrictedError(RuntimeError):
    """Raised when a specific field (IMEI or serial) can't be read due to
    Android's own privacy restrictions on that device/version."""


class AdbTimeoutError(RuntimeError):
    """Raised when an adb command doesn't complete within its timeout -- the
    device may be unresponsive or in a bad USB state."""


def _run_adb(*args: str) -> str:
    try:
        result = subprocess.run(
            ["adb", *args], capture_output=True, text=True, timeout=15, check=False
        )
    except FileNotFoundError as exc:
        raise AdbNotFoundError(
            "the 'adb' command was not found on PATH -- install Android SDK platform-tools"
        ) from exc
    except subprocess.TimeoutExpired as exc:
        raise AdbTimeoutError(
            f"'adb {' '.join(args)}' did not complete within 15 seconds -- the device may "
            "be unresponsive or disconnected"
        ) from exc
    return result.stdout


def list_android_device_serials() -> list[str]:
    """Return the serials of all Android devices currently connected and
    authorized for USB debugging (`adb devices`)."""
    output = _run_adb("devices")
    serials = []
    for line in output.strip().splitlines()[1:]:
        parts = line.split()
        if len(parts) == 2 and parts[1] == "device":
            serials.append(parts[0])
    return serials


def _getprop(serial: str, prop: str) -> str:
    return _run_adb("-s", serial, "shell", "getprop", prop).strip()


def _extract_quoted_ascii(output: str) -> str:
    """Extract and concatenate the quoted ASCII columns from an `adb
    shell service call` Parcel dump (the "'........9.4.0.1.'" style
    portions) -- this is where the actual string payload lives, unlike
    the hex-address labels and raw hex words elsewhere in the dump."""
    return "".join(re.findall(r"'([^']*)'", output))


def _read_imei(serial: str) -> str:
    output = _run_adb("-s", serial, "shell", "service", "call", "iphonesubinfo", "1")
    ascii_portion = _extract_quoted_ascii(output)
    digits = "".join(ch for ch in ascii_portion if ch.isdigit())
    if len(digits) < 15:
        raise AndroidFieldRestrictedError(
            f"could not read IMEI from device {serial!r} -- on Android 10+, this requires "
            "READ_PHONE_STATE plus system/privileged app access, which plain adb shell "
            "access does not have; this is a deliberate platform restriction, not a bug"
        )
    return digits[:15]


def _read_serial(serial: str) -> str:
    value = _getprop(serial, "ro.serialno")
    if not value or value.lower() == "unknown":
        raise AndroidFieldRestrictedError(
            f"could not read serial number from device {serial!r} -- Android 8+ restricts "
            "this without READ_PHONE_STATE and carrier/device-owner privileges that plain "
            "adb shell access does not have; this is a deliberate platform restriction, not a bug"
        )
    return value


def read_connected_android_device(serial: str | None = None) -> DeviceInfo:
    """Read model, capacity, IMEI, and serial from a connected Android
    device authorized for USB debugging. `serial` selects a specific
    device when more than one is connected.

    Raises AdbNotFoundError if the adb binary is missing,
    NoDeviceConnectedError/MultipleDevicesConnectedError for connectivity
    issues, AndroidFieldRestrictedError if IMEI/serial can't be read due
    to the device's Android version restricting that access, or
    AdbTimeoutError if an adb command doesn't complete within its timeout
    (e.g. an unresponsive or flaky USB device). Never requires or assumes
    root.
    """
    serials = list_android_device_serials()
    if not serials:
        raise NoDeviceConnectedError("no authorized Android device detected over USB")
    if serial is None:
        if len(serials) > 1:
            raise MultipleDevicesConnectedError(
                f"multiple Android devices connected ({', '.join(serials)}) -- "
                "pass serial to choose one"
            )
        serial = serials[0]
    elif serial not in serials:
        raise NoDeviceConnectedError(
            f"device {serial!r} is not currently connected and authorized for USB debugging "
            f"(connected and authorized: {', '.join(serials)})"
        )

    getprop_values = {
        "ro.product.manufacturer": _getprop(serial, "ro.product.manufacturer"),
        "ro.product.model": _getprop(serial, "ro.product.model"),
    }
    imei = _read_imei(serial)
    device_serial = _read_serial(serial)
    storage_output = _run_adb("-s", serial, "shell", "df", "-k", "/data")
    storage_bytes = parse_df_output(storage_output)

    return parse_android_device_info(getprop_values, storage_bytes, imei, device_serial)
