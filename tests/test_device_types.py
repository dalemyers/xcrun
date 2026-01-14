"""Test device types using pytest."""

import uuid

import pytest

import isim


@pytest.fixture(scope="module", name="all_device_types")
def fixture_all_device_types() -> list[isim.DeviceType]:
    """Fixture to get all available device types once per module."""
    return isim.DeviceType.list_all()


def test_from_info() -> None:
    """Test that we create a device type correctly from simctl info."""
    fake_device_type = {
        "name": "Apple Fridge 1.0",
        "bundlePath": (
            "\\/Applications\\/Xcode_10.1.app\\/Contents\\/Developer\\/Platforms\\/"
            "WatchOS.platform\\/Developer\\/Library\\/CoreSimulator\\/Profiles\\/"
            "DeviceTypes\\/Apple Watch Series 4 - 40mm.simdevicetype"
        ),
        "identifier": "io.myers.isim.device-type.Apple-Fridge",
    }

    device_types = isim.DeviceType.from_simctl_info([fake_device_type])
    assert len(device_types) == 1

    device_type = device_types[0]
    assert device_type.name == fake_device_type["name"]
    assert device_type.bundle_path == fake_device_type["bundlePath"].replace("\\/", "/")
    assert device_type.identifier == fake_device_type["identifier"]


def test_list_installed_device_types(all_device_types: list[isim.DeviceType]) -> None:
    """Test that we can parse all installed device types without error."""
    assert all_device_types is not None
    assert len(all_device_types) > 0, "Should have at least one device type installed"


def test_from_identifier(all_device_types: list[isim.DeviceType]) -> None:
    """Test that we can create a device type reference from an existing identifier."""
    assert len(all_device_types) > 0, "Need at least one device type to test"

    # Get a device type identifier from the list
    device_type_identifier = all_device_types[0].identifier
    device_type = isim.DeviceType.from_id(device_type_identifier)

    assert device_type is not None
    assert device_type.identifier == device_type_identifier


def test_from_name(all_device_types: list[isim.DeviceType]) -> None:
    """Test that we can create a device type reference from an existing name."""
    assert len(all_device_types) > 0, "Need at least one device type to test"

    # Get a device type name from the list
    device_type_name = all_device_types[0].name
    device_type = isim.DeviceType.from_name(device_type_name)

    assert device_type is not None
    assert device_type.name == device_type_name


def test_invalid_identifier() -> None:
    """Test that we don't accidentally match on invalid identifiers."""
    with pytest.raises(isim.DeviceTypeNotFoundError):
        isim.DeviceType.from_id("Hodor")


def test_invalid_name() -> None:
    """Test that we don't accidentally match on invalid names."""
    # It's unlikely that anyone would get the exact same UUID as we generate
    with pytest.raises(isim.DeviceTypeNotFoundError):
        isim.DeviceType.from_name(str(uuid.uuid4()))


def test_equality(all_device_types: list[isim.DeviceType]) -> None:
    """Test that the equality check on device types is accurate."""
    # We need at least 2 device types to test
    assert len(all_device_types) >= 2, "Need at least 2 device types for equality testing"

    device_type_a = all_device_types[0]
    device_type_b = all_device_types[1]

    # They should be different from each other
    assert device_type_a != device_type_b

    # Checking one against something totally different should always be false
    assert device_type_a != ["Hello", "World"]

    # Checking one against itself should always be true
    # pylint: disable=comparison-with-itself
    assert device_type_a == device_type_a  # noqa: PLR0124
    # pylint: enable=comparison-with-itself

    # Checking a copy of one against itself should always be true
    identifier_copy_a = isim.DeviceType.from_id(device_type_a.identifier)
    assert device_type_a == identifier_copy_a


def test_string_representations(all_device_types: list[isim.DeviceType]) -> None:
    """Test that the string representations are unique."""
    strings = {str(device_type) for device_type in all_device_types}
    assert len(strings) == len(all_device_types), "String representations should be unique"


def test_device_type_attributes(all_device_types: list[isim.DeviceType]) -> None:
    """Test that device type objects have expected attributes."""
    assert len(all_device_types) > 0

    device_type = all_device_types[0]
    assert hasattr(device_type, "identifier")
    assert hasattr(device_type, "name")
    assert hasattr(device_type, "bundle_path")

    # Check types
    assert isinstance(device_type.identifier, str)
    assert isinstance(device_type.name, str)
    assert isinstance(device_type.bundle_path, str)


@pytest.mark.parametrize("product_family", ["iPhone", "iPad", "Apple-Watch", "Apple-TV"])
def test_device_types_by_family(
    all_device_types: list[isim.DeviceType], product_family: str
) -> None:
    """Test that we can find device types by product family."""
    family_devices = [dt for dt in all_device_types if product_family in dt.identifier]

    # We may not have all families, so we don't assert they exist
    # Just verify that if they exist, they have the right properties
    for device_type in family_devices:
        assert product_family in device_type.identifier
        assert device_type.name  # Has a name
        assert device_type.identifier  # Has an identifier
