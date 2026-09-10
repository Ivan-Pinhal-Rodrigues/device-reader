def test_pure_layer_is_importable_from_package_root():
    from device_reader import (
        DeviceInfo,
        InvalidDeviceInfoError,
        MultipleDevicesConnectedError,
        NoDeviceConnectedError,
        UnrecognizedCapacityError,
        bytes_to_marketed_capacity_gb,
        parse_android_device_info,
        parse_df_output,
        parse_ios_device_info,
        product_type_to_model_name,
    )

    assert issubclass(InvalidDeviceInfoError, ValueError)
    assert issubclass(NoDeviceConnectedError, RuntimeError)
    assert issubclass(MultipleDevicesConnectedError, RuntimeError)
    assert issubclass(UnrecognizedCapacityError, ValueError)
    assert callable(bytes_to_marketed_capacity_gb)
    assert callable(product_type_to_model_name)
    assert callable(parse_ios_device_info)
    assert callable(parse_android_device_info)
    assert callable(parse_df_output)
    assert DeviceInfo.__dataclass_fields__.keys() == {"model", "capacity_gb", "imei", "serial"}


def test_full_surface_is_importable_from_package_root():
    from device_reader import (
        AdbNotFoundError,
        AdbTimeoutError,
        AndroidFieldRestrictedError,
        DeviceNotAccessibleError,
        MissingHardwareExtraError,
        list_android_device_serials,
        list_ios_device_udids,
        read_connected_android_device,
        read_connected_device,
        read_connected_ios_device,
    )

    assert issubclass(DeviceNotAccessibleError, RuntimeError)
    assert issubclass(MissingHardwareExtraError, ImportError)
    assert issubclass(AdbNotFoundError, RuntimeError)
    assert issubclass(AdbTimeoutError, RuntimeError)
    assert issubclass(AndroidFieldRestrictedError, RuntimeError)
    assert callable(read_connected_device)
    assert callable(read_connected_ios_device)
    assert callable(read_connected_android_device)
    assert callable(list_ios_device_udids)
    assert callable(list_android_device_serials)
