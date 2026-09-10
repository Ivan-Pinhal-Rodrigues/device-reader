"""Read model, capacity, IMEI, and serial number from a connected, unlocked mobile device (iOS and Android)."""

from .android_client import (
    AdbNotFoundError,
    AdbTimeoutError,
    AndroidFieldRestrictedError,
    list_android_device_serials,
    read_connected_android_device,
)
from .android_parsing import parse_android_device_info, parse_df_output
from .capacity import UnrecognizedCapacityError, bytes_to_marketed_capacity_gb
from .ios_client import (
    DeviceNotAccessibleError,
    MissingHardwareExtraError,
    list_ios_device_udids,
    read_connected_ios_device,
)
from .ios_model_lookup import product_type_to_model_name
from .ios_parsing import parse_ios_device_info
from .models import (
    DeviceInfo,
    InvalidDeviceInfoError,
    MultipleDevicesConnectedError,
    NoDeviceConnectedError,
)
from .reader import read_connected_device

__all__ = [
    "AdbNotFoundError",
    "AdbTimeoutError",
    "AndroidFieldRestrictedError",
    "DeviceInfo",
    "DeviceNotAccessibleError",
    "InvalidDeviceInfoError",
    "MissingHardwareExtraError",
    "MultipleDevicesConnectedError",
    "NoDeviceConnectedError",
    "UnrecognizedCapacityError",
    "bytes_to_marketed_capacity_gb",
    "list_android_device_serials",
    "list_ios_device_udids",
    "parse_android_device_info",
    "parse_df_output",
    "parse_ios_device_info",
    "product_type_to_model_name",
    "read_connected_android_device",
    "read_connected_device",
    "read_connected_ios_device",
]
