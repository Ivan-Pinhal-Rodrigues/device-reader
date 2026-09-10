"""Maps Apple's internal ProductType identifiers to marketing names.

Sourced from Wikipedia's "List of iPhone models" (a public, verifiable
reference) as of 2026-09-10, covering iPhone 11 onward. Apple doesn't
publish this mapping itself and releases new identifiers regularly, so
an unrecognized identifier is not an error -- it's returned unchanged,
still useful, honest information for an intake operator rather than a
guess or a crash.

Android's equivalent (ios_model_lookup has no direct android_model_lookup
counterpart) is deliberately NOT attempted the same way -- see
android_parsing.py's docstring for why a lookup table doesn't make sense
across Android's much larger manufacturer fragmentation.
"""

_PRODUCT_TYPE_TO_MODEL_NAME: dict[str, str] = {
    "iPhone12,1": "iPhone 11",
    "iPhone12,3": "iPhone 11 Pro",
    "iPhone12,5": "iPhone 11 Pro Max",
    "iPhone12,8": "iPhone SE (2nd generation)",
    "iPhone13,1": "iPhone 12 mini",
    "iPhone13,2": "iPhone 12",
    "iPhone13,3": "iPhone 12 Pro",
    "iPhone13,4": "iPhone 12 Pro Max",
    "iPhone14,2": "iPhone 13 Pro",
    "iPhone14,3": "iPhone 13 Pro Max",
    "iPhone14,4": "iPhone 13 mini",
    "iPhone14,5": "iPhone 13",
    "iPhone14,6": "iPhone SE (3rd generation)",
    "iPhone14,7": "iPhone 14",
    "iPhone14,8": "iPhone 14 Plus",
    "iPhone15,2": "iPhone 14 Pro",
    "iPhone15,3": "iPhone 14 Pro Max",
    "iPhone15,4": "iPhone 15",
    "iPhone15,5": "iPhone 15 Plus",
    "iPhone16,1": "iPhone 15 Pro",
    "iPhone16,2": "iPhone 15 Pro Max",
    "iPhone17,1": "iPhone 16 Pro",
    "iPhone17,2": "iPhone 16 Pro Max",
    "iPhone17,3": "iPhone 16",
    "iPhone17,4": "iPhone 16 Plus",
    "iPhone17,5": "iPhone 16e",
    "iPhone18,1": "iPhone 17 Pro",
    "iPhone18,2": "iPhone 17 Pro Max",
    "iPhone18,3": "iPhone 17",
    "iPhone18,4": "iPhone Air",
    "iPhone18,5": "iPhone 17e",
    "iPhone19,1": "iPhone 18 Pro",
    "iPhone19,2": "iPhone 18 Pro Max",
    "iPhone19,6": "iPhone Duo",
}


def product_type_to_model_name(product_type: str) -> str:
    """Return the marketing name for `product_type`, or `product_type`
    itself unchanged if it's not in the known table."""
    return _PRODUCT_TYPE_TO_MODEL_NAME.get(product_type, product_type)
