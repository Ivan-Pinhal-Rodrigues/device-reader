"""Thin adapter over pymobiledevice3 -- the only iOS-hardware-touching
code in this package. Untestable in an environment without a physical,
unlocked, already-trusted iOS device connected over USB; verify by hand
against real hardware. pymobiledevice3's API is asyncio-native; this
wraps it in asyncio.run() so callers get a plain synchronous function,
consistent with the rest of this portfolio.

Security boundary: this only ever reads from a device that is already
unlocked and already trusted/paired with this computer -- exactly what
pymobiledevice3's underlying protocol requires. A locked or untrusted
device raises DeviceNotAccessibleError; this package never attempts to
work around that. Concretely, the connect call passes autopair=False,
which disables pymobiledevice3's default behavior of silently sending a
live "Trust This Computer?" pairing request to an untrusted device; with
autopair=False an untrusted device instead fails cleanly (surfaced here
as DeviceNotAccessibleError) rather than triggering an unattended
pairing prompt.
"""

import asyncio

from .ios_parsing import parse_ios_device_info
from .models import DeviceInfo, MultipleDevicesConnectedError, NoDeviceConnectedError


class MissingHardwareExtraError(ImportError):
    """Raised when device access is attempted without the optional `hardware` extra installed."""


class DeviceNotAccessibleError(RuntimeError):
    """Raised when a device is locked or not yet trusted on this computer."""


async def _list_ios_device_udids_async() -> list[str]:
    from pymobiledevice3 import usbmux

    devices = await usbmux.list_devices()
    return [d.serial for d in devices]


def list_ios_device_udids() -> list[str]:
    """Return the UDIDs of all iOS devices currently connected over USB."""
    try:
        import pymobiledevice3  # noqa: F401  -- import-only check for the extra
    except ImportError as exc:
        raise MissingHardwareExtraError(
            "reading a device requires the optional 'hardware' extra: "
            "pip install 'device-reader[hardware]'"
        ) from exc
    return asyncio.run(_list_ios_device_udids_async())


async def _read_connected_ios_device_async(udid: str | None) -> DeviceInfo:
    from pymobiledevice3.exceptions import (
        DeviceNotFoundError,
        GetProhibitedError,
        NotPairedError,
        PasswordRequiredError,
    )
    from pymobiledevice3.lockdown import create_using_usbmux
    from pymobiledevice3.services.afc import AfcService

    udids = await _list_ios_device_udids_async()
    if not udids:
        raise NoDeviceConnectedError("no iOS device detected over USB")
    if udid is None:
        if len(udids) > 1:
            raise MultipleDevicesConnectedError(
                f"multiple iOS devices connected ({', '.join(udids)}) -- pass udid to choose one"
            )
        udid = udids[0]

    # autopair=False is essential: with the default autopair=True, an
    # untrusted device gets a live "Trust This Computer?" pairing request
    # sent to it and this call can hang indefinitely waiting for someone to
    # tap it on the device -- exactly the kind of unattended pairing
    # attempt this tool must never make. With autopair=False, an unpaired
    # device typically connects immediately with paired=False and no
    # exception, and the real failure surfaces below at the first
    # privileged request (inside AfcService) as NotPairedError. But
    # pymobiledevice3's own connect-time initialization can also raise
    # NotPairedError/PasswordRequiredError/GetProhibitedError directly
    # (e.g. under certain MDM-supervised device policies) -- both call
    # sites translate to the same DeviceNotAccessibleError below, so which
    # one actually fires doesn't matter to callers.
    try:
        lockdown = await create_using_usbmux(serial=udid, autopair=False)
    except DeviceNotFoundError as exc:
        raise NoDeviceConnectedError(f"no device with udid {udid!r} is currently connected") from exc
    except (NotPairedError, PasswordRequiredError, GetProhibitedError) as exc:
        raise DeviceNotAccessibleError(
            f"device {udid!r} is locked or not yet trusted on this computer: {exc}"
        ) from exc

    try:
        async with AfcService(lockdown=lockdown) as afc:
            afc_info = await afc.get_device_info()
        lockdown_values = lockdown.all_values
    except (NotPairedError, PasswordRequiredError, GetProhibitedError) as exc:
        raise DeviceNotAccessibleError(
            f"device {udid!r} is locked or not yet trusted on this computer: {exc}"
        ) from exc
    finally:
        await lockdown.close()

    return parse_ios_device_info(lockdown_values, afc_info)


def read_connected_ios_device(udid: str | None = None) -> DeviceInfo:
    """Read model, capacity, IMEI, and serial from a connected, unlocked,
    user-trusted iOS device. `udid` selects a specific device when more
    than one is connected.

    Raises MissingHardwareExtraError if the `hardware` extra isn't
    installed, NoDeviceConnectedError/MultipleDevicesConnectedError for
    connectivity issues, or DeviceNotAccessibleError if the device is
    locked or untrusted. Never attempts to access a locked device.
    """
    try:
        import pymobiledevice3  # noqa: F401  -- import-only check for the extra
    except ImportError as exc:
        raise MissingHardwareExtraError(
            "reading a device requires the optional 'hardware' extra: "
            "pip install 'device-reader[hardware]'"
        ) from exc

    return asyncio.run(_read_connected_ios_device_async(udid))
