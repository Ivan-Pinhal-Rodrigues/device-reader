"""Unified entry point: detects whichever supported device is actually
connected (iOS or Android) and reads it. Thin dispatch logic only -- the
real per-platform work lives in ios_client.py and android_client.py,
each independently usable on its own too.
"""

from . import android_client, ios_client
from .models import DeviceInfo, MultipleDevicesConnectedError, NoDeviceConnectedError


def _safe_list(list_fn) -> list[str]:
    """Listing devices for one platform shouldn't fail the whole
    dispatch just because that platform's tooling isn't installed
    (pymobiledevice3's `hardware` extra, or the `adb` binary) -- treat
    that as "zero devices on this platform" rather than a fatal error,
    since the other platform might still have something connected.

    This catch is deliberately broad. Narrowing it (e.g. to only
    ImportError or only RuntimeError) would let a real, unanticipated
    failure on one platform PROPAGATE and crash the whole dispatch
    instead of degrading to "zero devices there" -- reopening exactly
    the "one platform's problem blocks the other" bug this function
    exists to prevent. A sibling module in this project once had an
    identical broad catch narrowed by a "lint fix," which reopened a
    real crash-on-real-hardware-failure bug for exactly this reason --
    don't repeat that here.
    """
    try:
        return list_fn()
    except Exception:  # noqa: BLE001 -- documented above: broad catch is intentional
        return []


def read_connected_device(identifier: str | None = None) -> DeviceInfo:
    """Read model, capacity, IMEI, and serial from whichever single
    supported device (iOS or Android) is connected. `identifier` is a
    UDID (iOS) or serial (Android) to choose a specific device when more
    than one is connected across either or both platforms.

    Locked iOS devices and Android 10+ IMEI/serial restrictions are
    surfaced as clear, specific errors from the underlying platform
    client -- this function does not attempt to work around either.
    """
    if identifier is not None:
        # Don't use _safe_list here: an explicit identifier means the
        # caller expects a specific match, so a real failure while
        # checking one platform (e.g. the `hardware` extra missing) must
        # not be silently swallowed and misattributed to the other
        # platform -- capture it and only surface it if neither platform
        # ends up claiming this identifier.
        ios_error: Exception | None = None
        try:
            ios_udids = ios_client.list_ios_device_udids()
        except Exception as exc:  # noqa: BLE001 -- captured, not swallowed; see comment above
            ios_error = exc
            ios_udids = []

        if identifier in ios_udids:
            return ios_client.read_connected_ios_device(udid=identifier)

        try:
            android_serials = android_client.list_android_device_serials()
        except Exception:
            if ios_error is not None:
                raise ios_error from None
            raise

        if identifier in android_serials:
            return android_client.read_connected_android_device(serial=identifier)

        if ios_error is not None:
            raise ios_error
        raise NoDeviceConnectedError(f"no connected device matches identifier {identifier!r}")

    ios_udids = _safe_list(ios_client.list_ios_device_udids)
    android_serials = _safe_list(android_client.list_android_device_serials)
    candidates = [("ios", udid) for udid in ios_udids] + [
        ("android", serial) for serial in android_serials
    ]

    if not candidates:
        raise NoDeviceConnectedError("no supported device (iOS or Android) detected over USB")
    if len(candidates) > 1:
        found = ", ".join(f"{platform}:{value}" for platform, value in candidates)
        raise MultipleDevicesConnectedError(
            f"multiple devices connected ({found}) -- pass identifier to choose one"
        )

    platform, chosen = candidates[0]
    if platform == "ios":
        return ios_client.read_connected_ios_device(udid=chosen)
    return android_client.read_connected_android_device(serial=chosen)
