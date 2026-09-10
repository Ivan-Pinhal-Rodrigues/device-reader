"""Command-line entry point. Reads one connected device (iOS or Android,
auto-detected) and prints its info as JSON -- model, capacity_gb, imei,
serial (no print_date; see models.py's docstring for why).
"""

import argparse
import json
import sys
from dataclasses import asdict


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="device-read")
    parser.add_argument(
        "--id",
        dest="identifier",
        type=str,
        default=None,
        help="Select a specific device by UDID (iOS) or serial (Android), "
        "required if more than one is connected",
    )
    args = parser.parse_args(argv)

    from .models import MultipleDevicesConnectedError, NoDeviceConnectedError
    from .reader import read_connected_device

    try:
        info = read_connected_device(identifier=args.identifier)
    except (NoDeviceConnectedError, MultipleDevicesConnectedError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # noqa: BLE001 -- platform-specific hardware/permission
        # errors (DeviceNotAccessibleError, MissingHardwareExtraError, AdbNotFoundError,
        # AndroidFieldRestrictedError) all need to surface here as a clean message, not a
        # raw crash -- same reasoning as label-printer's detect_loaded_media boundary.
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(asdict(info)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
