# AGENTS.md

## Goal

Maintain a small Windows tray utility that reads and visualizes the battery level and charging state of a Pwnage StormBreaker mouse without the official Pwnage software.

## Architecture

- `stormbreaker.py` — all StormBreaker HID communication and the Windows device-change listener.
- `main.py` — tray icon, polling, battery notifications, and menu actions.
- `settings.py` — Windows current-user startup Registry helpers.

Do not put HID/protocol logic in `main.py`. Do not send device commands from the UI other than the confirmed status request exposed by `stormbreaker.py`.

## Confirmed device/protocol

```text
VID:        0x3662
PID:        0x0002
Interface:  MI_00 / Col05
Usage page: 0xFF1C
Usage:      0x0092

64-byte request begins:
04 20 00 1A 06 00 00 00 ...

response[7] = status/error
response[8] = battery percentage (0-100)
response[9] = charging flag (0x01 = charging)
```

Request bytes `1-2` are the little-endian sum of bytes `3..63`.

## Current behavior

- `get_battery_status()` returns `(percentage, is_charging)` from one status request.
- `main.py` polls every 60 seconds and can wake early after any Windows `WM_DEVICECHANGE` notification.
- Temporary read failures must not terminate the tray app.
- The low-battery notification applies only at `1-20%` while not charging, then no more often than every 10 minutes.
- `settings.py` supports enabling, disabling, and reading per-user launch-at-startup state.

## HID safety

- Target only VID `0x3662`, PID `0x0002`, usage page `0xFF1C`, usage `0x0092`.
- Send only the confirmed battery/status request.
- Do not modify DPI, polling rate, firmware, pairing, profiles, or device settings.
- Keep polling infrequent unless a user explicitly changes the interval.

## Development rules

- Prefer the smallest readable Python change; avoid speculative abstractions and dependencies.
- Keep protocol constants centralized in `stormbreaker.py`.
- Preserve the module boundaries above.
- Verify non-trivial behavior with the smallest relevant local check.
- The reused `Battery_dark.png` and `Mouse_dark.png` assets originate from GPL-3.0 LGSTrayBattery; keep distribution licensing compatible when distributing them.

## Agent replies

After code changes, report briefly:

1. What changed.
2. What it means for the developer/user.
3. Before vs. after behavior.
4. How the change was verified.
