# AGENTS.md

## Goal
Build a small Windows utility that reads and visualizes the battery level of a Pwnage StormBreaker mouse without requiring the official Pwnage software.

## Architecture
Keep the project split into two main modules:

- `stormbreaker.py` — all HID/device communication.
- `app.py` — tray/UI visualization and polling.

Do not put HID/protocol logic in `app.py`.

## `stormbreaker.py`
Responsibilities:

- Find the StormBreaker receiver.
- Open only the confirmed vendor HID interface.
- Send the battery/status request.
- Validate the response.
- Return battery percentage as a simple value.
- Raise or return clear errors for unavailable/invalid states.

Confirmed device/protocol:

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
```

Request bytes `1-2` are the little-endian sum of bytes `3..63`.

## `app.py`
Responsibilities:

- Display battery percentage clearly.
- Poll `stormbreaker.py` every 30-60 seconds.
- Show sensible disconnected/unavailable/error states.
- Remain lightweight and unobtrusive.
- Never duplicate HID/protocol implementation.

## Reliability
Handle gracefully:

- Receiver unplugged.
- Mouse asleep/off.
- HID read timeout.
- Interface already in use.
- Malformed/short responses.
- Battery values outside `0-100`.

Do not crash the app for temporary device failures.

## HID Safety
- Target only VID `0x3662`, PID `0x0002`, usage page `0xFF1C`, usage `0x0092`.
- Do not send undocumented commands.
- Keep writes limited to the confirmed battery/status request.
- Do not modify DPI, polling rate, firmware, pairing, profiles, or device settings.
- Avoid unnecessarily frequent polling/writes.

## Development Rules
- Prefer simple, readable Python over abstractions that are not needed.
- Keep protocol constants named and centralized.
- Keep functions small and testable.
- Preserve the two-module boundary unless there is a strong reason to add a small supporting module.
- Do not add unrelated features before the core battery reader and visualizer are reliable.

## Agent Replies
After code changes, report briefly:

1. What changed.
2. What it means for the developer/user.
3. Before vs. after behavior.
4. How the change was verified.
