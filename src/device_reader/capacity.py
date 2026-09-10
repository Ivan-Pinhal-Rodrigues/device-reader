"""Converts a device's raw reported byte count into its marketed storage
capacity.

A device's actual formatted/usable byte count is always somewhat less
than its marketed capacity (filesystem overhead and reserved system
space eat into it) -- true on both iOS and Android -- e.g. a "128GB"
phone reports well under 128 * 10**9 bytes of total space. Rounding UP
to the nearest standard tier recovers the number that actually belongs
on a label.
"""

_STANDARD_CAPACITIES_GB = [16, 32, 64, 128, 256, 512, 1024, 2048]


class UnrecognizedCapacityError(ValueError):
    """Raised when a byte count doesn't fit under any known standard tier."""


def bytes_to_marketed_capacity_gb(total_bytes: int) -> int:
    """Round `total_bytes` up to the nearest standard marketed capacity
    (decimal GB: 1 GB = 10**9 bytes)."""
    for tier_gb in _STANDARD_CAPACITIES_GB:
        if total_bytes <= tier_gb * 10**9:
            return tier_gb
    raise UnrecognizedCapacityError(
        f"{total_bytes} bytes exceeds the largest known tier "
        f"({_STANDARD_CAPACITIES_GB[-1]}GB)"
    )
