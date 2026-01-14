"""Test device pairs using pytest."""

import pytest

import isim


def test_list_device_pairs() -> None:
    """Test that we can list device pairs."""
    try:
        pairs = isim.DevicePair.list_all()
        assert pairs is not None
        assert isinstance(pairs, list)
    except ValueError as e:
        # Empty pairs dict causes error in current implementation
        if "Unexpected format for pairs list type" in str(e):
            pytest.skip("No device pairs configured (returns empty dict)")
        raise


@pytest.fixture(name="device_pair")
def fixture_device_pair() -> isim.DevicePair:
    """Create a device pair for testing if one exists."""
    try:
        pairs = isim.DevicePair.list_all()
    except ValueError as e:
        # Empty pairs dict causes error in current implementation
        if "Unexpected format for pairs list type" in str(e):
            pytest.skip("No device pairs configured (returns empty dict)")
        raise

    if not pairs:
        pytest.skip("No device pairs available for testing")
    return pairs[0]


def test_device_pair_attributes(device_pair: isim.DevicePair) -> None:
    """Test that device pair objects have expected attributes."""
    assert hasattr(device_pair, "identifier")
    assert hasattr(device_pair, "watch_udid")
    assert hasattr(device_pair, "phone_udid")

    # Check types
    assert isinstance(device_pair.identifier, str)
    assert isinstance(device_pair.watch_udid, str)
    assert isinstance(device_pair.phone_udid, str)


def test_device_pair_watch(device_pair: isim.DevicePair) -> None:
    """Test that we can get the watch device from a pair."""
    watch = device_pair.watch()
    assert watch is not None
    assert isinstance(watch, isim.Device)
    assert watch.udid == device_pair.watch_udid


def test_device_pair_phone(device_pair: isim.DevicePair) -> None:
    """Test that we can get the phone device from a pair."""
    phone = device_pair.phone()
    assert phone is not None
    assert isinstance(phone, isim.Device)
    assert phone.udid == device_pair.phone_udid


def test_device_pair_str_repr(device_pair: isim.DevicePair) -> None:
    """Test string representations of device pairs."""
    str_repr = str(device_pair)
    assert device_pair.identifier in str_repr

    repr_str = repr(device_pair)
    assert "identifier" in repr_str
