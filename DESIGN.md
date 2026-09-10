# Design decisions

## Why this only reads unlocked/authorized devices, on both platforms

**iOS**: the protocol this package talks over (Apple's lockdown/AFC services via `pymobiledevice3`) requires a device to already be unlocked and already paired ("Trust This Computer") before it will answer -- this isn't a policy choice layered on top, it's what the hardware does. `read_connected_ios_device` translates the library's low-level exceptions into one clear `DeviceNotAccessibleError`.

**Android**: reading IMEI or serial requires `READ_PHONE_STATE` plus system/privileged-app access since Android 10 (API 29) and Android 8 respectively -- plain, non-root `adb shell` access does not qualify for either. `read_connected_android_device` attempts both reads and raises `AndroidFieldRestrictedError` with the specific reason when they fail, rather than requiring or assuming root.

Both boundaries exist for the same underlying reason -- protecting a device's identifying information from casual extraction -- and this package respects both rather than working around either, even in principle. That symmetry across two very differently-built platforms is itself a real design point: the same *intent* (don't let unauthorized software read who a device belongs to) shows up as two structurally different mechanisms, and understanding both was necessary to build this honestly.

## Why there's no Android equivalent of the iOS model-name lookup table

Apple's ProductType identifiers are a small, single-vendor scheme (`ios_model_lookup.py` has ~35 entries covering iPhone 11 onward). Android has no equivalent central scheme -- hundreds of manufacturers, no shared identifier format. A lookup table attempting the same thing for Android would have hollow, misleadingly-narrow coverage. `manufacturer + model` (e.g. "Google Pixel 7", "samsung SM-G991B") is used directly instead -- less pretty than a marketing name, but honest about what's actually knowable generically.

## Why Android's storage/model reads use raw shell-text parsing (`parse_df_output`) instead of a structured response

iOS's AFC/lockdown services return structured key-value data over a defined protocol. Android's `getprop`/`df` return human-oriented shell text with no such structure -- `parse_df_output` exists specifically because there's no shortcut around parsing it. This is a real, honest platform difference: iOS access here is protocol-level, Android access here is shell-command-level, and the code reflects that rather than pretending otherwise.

## Why `pymobiledevice3` is an optional extra but `adb` isn't a Python dependency at all

`pymobiledevice3` is a large, installable Python library -- an optional `hardware` extra keeps it out of the core install for callers who only want the pure parsing/validation layer. `adb` isn't a Python package at all; it's an external binary (Android SDK platform-tools) that `pip` can't install. `android_client.py` detects its absence at runtime (`AdbNotFoundError`) rather than pretending pip can manage it.

## Why `imei-validator` is a git-URL dependency for now

`imei-validator` (a sibling project in this portfolio) isn't published to PyPI yet. `pyproject.toml` depends on it via a direct git URL, which works for local installs but PyPI rejects direct-URL dependencies at upload time -- this needs to become a plain version pin before `device-reader` can be published to PyPI. Tracked as a known, temporary state.

## What I'd change at real scale

- Android Enterprise (Device Owner / a Device Policy Controller app) can legitimately unlock broader telephony access on company-managed Android devices, similar in spirit to how Apple Business Manager can for supervised iOS devices -- worth adding as an alternate, opt-in access path for genuinely enterprise-managed fleets, rather than the plain-ADB best-effort path this version uses.
- A more robust Android storage read (parsing `dumpsys diskstats` or similar) instead of relying on `df`'s exact toybox output shape, which can vary slightly by OEM/Android version.
- A `--json-lines`/`--watch` CLI mode for streaming multiple devices as they connect.
