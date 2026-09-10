from device_reader.ios_model_lookup import product_type_to_model_name


def test_known_identifier_maps_to_marketing_name():
    assert product_type_to_model_name("iPhone14,2") == "iPhone 13 Pro"


def test_another_known_identifier():
    assert product_type_to_model_name("iPhone15,4") == "iPhone 15"


def test_unrecognized_identifier_falls_back_to_raw_string():
    assert product_type_to_model_name("iPhone99,9") == "iPhone99,9"
