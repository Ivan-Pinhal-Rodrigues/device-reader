import pytest

from device_reader.capacity import UnrecognizedCapacityError, bytes_to_marketed_capacity_gb


def test_rounds_up_to_smallest_tier():
    assert bytes_to_marketed_capacity_gb(4_000_000_000) == 16


def test_rounds_up_from_under_capacity_due_to_formatting_overhead():
    assert bytes_to_marketed_capacity_gb(119_000_000_000) == 128


def test_exact_tier_boundary_is_inclusive():
    assert bytes_to_marketed_capacity_gb(64_000_000_000) == 64


def test_rounds_up_to_largest_tier():
    assert bytes_to_marketed_capacity_gb(2_000_000_000_000) == 2048


def test_raises_above_largest_known_tier():
    with pytest.raises(UnrecognizedCapacityError, match="2048"):
        bytes_to_marketed_capacity_gb(3_000_000_000_000)
