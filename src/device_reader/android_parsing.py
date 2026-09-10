"""Combines Android device data (getprop values + a df-parsed storage
byte count) into a validated DeviceInfo. Pure -- no hardware/subprocess
access, fully testable with sample data.

Android's device-facing tooling (getprop, df) returns free-form shell
text rather than iOS's structured lockdown/AFC protocol responses, so
this module includes its own small text-parsing step (parse_df_output)
rather than working with an already-structured dict -- a real, honest
platform difference, not a shortcut.

No marketing-name lookup table exists for Android the way
ios_model_lookup.py has one for iPhone: Apple's ProductType scheme is a
small, clean, single-vendor identifier space; Android spans hundreds of
manufacturers with no equivalent central scheme, so a lookup table here
would have hollow, misleadingly-narrow coverage. manufacturer + model
(e.g. "Google Pixel 7") is used directly instead.
"""

from imei_validator import InvalidIMEIError, validate_imei

from .capacity import bytes_to_marketed_capacity_gb
from .models import DeviceInfo, InvalidDeviceInfoError


def parse_df_output(raw_text: str) -> int:
    """Parse the total byte count from `adb shell df -k /data` output.

    Expects the standard toybox/toolbox `df` shape: a header line
    followed by one data line whose second whitespace-separated field is
    the total size in 1K blocks, e.g.:
        Filesystem      1K-blocks    Used Available Use% Mounted on
        /dev/block/dm-7  51354112 32456788  18765432  64% /data
    """
    lines = [line for line in raw_text.strip().splitlines() if line.strip()]
    if len(lines) < 2:
        raise InvalidDeviceInfoError(f"unexpected df output, no data row found: {raw_text!r}")
    fields = lines[1].split()
    if len(fields) < 2:
        raise InvalidDeviceInfoError(f"unexpected df output, too few fields: {lines[1]!r}")
    total_kb = int(fields[1])
    return total_kb * 1024


def parse_android_device_info(
    getprop_values: dict, storage_bytes: int, imei: str, serial: str
) -> DeviceInfo:
    """Build a DeviceInfo from Android getprop values, a total storage
    byte count (from parse_df_output), and an already-resolved IMEI and
    serial (the caller -- android_client.py -- is responsible for reading
    those two separately, since on Android 10+ they require different,
    more restricted access than plain model/manufacturer properties)."""
    manufacturer = getprop_values.get("ro.product.manufacturer", "").strip()
    product_model = getprop_values.get("ro.product.model", "").strip()
    model = f"{manufacturer} {product_model}".strip()

    try:
        validate_imei(imei)
    except InvalidIMEIError as exc:
        raise InvalidDeviceInfoError(
            f"device reported an IMEI that fails validation: {exc}"
        ) from exc

    capacity_gb = bytes_to_marketed_capacity_gb(storage_bytes)

    return DeviceInfo(model=model, capacity_gb=capacity_gb, imei=imei, serial=serial)
