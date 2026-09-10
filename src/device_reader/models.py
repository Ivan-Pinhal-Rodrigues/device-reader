"""The data read from a device -- deliberately mirrors label-printer's
LabelData shape (model, capacity_gb, imei, serial), minus a print date,
since reading a device doesn't involve one. device-intake-station (a
separate project) composes this output with a print date into a full
LabelData.

Also holds the two connectivity exceptions shared by both platform
clients and the unified reader -- kept here, not duplicated per module,
so the public API never has two different classes fighting over one name.
"""

from dataclasses import dataclass


class InvalidDeviceInfoError(ValueError):
    """Raised when a DeviceInfo field fails validation."""


class NoDeviceConnectedError(RuntimeError):
    """Raised when no supported device is connected on the platform(s) checked."""


class MultipleDevicesConnectedError(RuntimeError):
    """Raised when more than one device is connected and no identifier was given to choose one."""


@dataclass(frozen=True)
class DeviceInfo:
    model: str
    capacity_gb: int
    imei: str
    serial: str

    def __post_init__(self) -> None:
        if not self.model:
            raise InvalidDeviceInfoError("model must not be empty")
        if self.capacity_gb <= 0:
            raise InvalidDeviceInfoError(f"capacity_gb must be positive, got {self.capacity_gb}")
        if not self.imei:
            raise InvalidDeviceInfoError("imei must not be empty")
        if not self.serial:
            raise InvalidDeviceInfoError("serial must not be empty")
