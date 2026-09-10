"""Combines raw iOS lockdown + AFC responses into a validated DeviceInfo.
Pure -- no hardware access, fully testable with sample dicts. This is
where imei-validator (a sibling published package) gets real
cross-project reuse: a device's reported IMEI is checked here before it
ever reaches a label or a database.
"""

from imei_validator import InvalidIMEIError, validate_imei

from .capacity import bytes_to_marketed_capacity_gb
from .ios_model_lookup import product_type_to_model_name
from .models import DeviceInfo, InvalidDeviceInfoError


def parse_ios_device_info(lockdown_values: dict, afc_device_info: dict) -> DeviceInfo:
    """Build a DeviceInfo from a lockdown client's `all_values` dict and
    an AFC service's `get_device_info()` dict."""
    product_type = lockdown_values.get("ProductType", "")
    model = product_type_to_model_name(product_type)

    imei = lockdown_values.get("InternationalMobileEquipmentIdentity", "")
    try:
        validate_imei(imei)
    except InvalidIMEIError as exc:
        raise InvalidDeviceInfoError(
            f"device reported an IMEI that fails validation: {exc}"
        ) from exc

    serial = lockdown_values.get("SerialNumber", "")

    total_bytes_raw = afc_device_info.get("FSTotalBytes")
    if total_bytes_raw is None:
        raise InvalidDeviceInfoError("device info is missing FSTotalBytes")
    capacity_gb = bytes_to_marketed_capacity_gb(int(total_bytes_raw))

    return DeviceInfo(model=model, capacity_gb=capacity_gb, imei=imei, serial=serial)
