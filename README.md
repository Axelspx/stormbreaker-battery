# Pwnage StormBreaker Battery

A lightweight Windows utility for reading and visualizing the battery level of a Pwnage StormBreaker mouse without running the official Pwnage software.

## Plan

The project has two main pieces:

```text
stormbreaker.py  ->  HID/device communication
app.py           ->  tray/UI visualization
```

### `stormbreaker.py`

Responsible for:

- Discovering the StormBreaker receiver.
- Opening the vendor-defined HID interface.
- Sending the confirmed battery/status request.
- Reading and validating the response.
- Returning the battery percentage.

Confirmed device:

```text
VID:        0x3662
PID:        0x0002
Interface:  MI_00 / Col05
Usage page: 0xFF1C
Usage:      0x0092
```

Confirmed 64-byte battery/status request:

```text
04 20 00 1A 06 00 00 00 00 ...
```

The request checksum is stored little-endian in bytes `1-2` and is the sum of bytes `3..63`.

Confirmed response fields:

```text
response[7] = status/error
response[8] = battery percentage
```

Example: `response[8] == 0x62` means `98%`.

### `app.py`

Responsible for:

- Displaying the current battery level.
- Polling `stormbreaker.py` roughly every 30-60 seconds.
- Showing disconnected, sleeping, unavailable, or error states cleanly.
- Remaining as lightweight as possible.

## Reliability

The app should tolerate:

- Receiver unplugged.
- Mouse asleep/off.
- HID timeouts.
- Busy HID interface.
- Short/malformed responses.
- Invalid battery values.

Temporary failures should not terminate the application.

## Setup

```powershell
py -m pip install hidapi
```

Development currently targets Windows.

## Run

During development:

```powershell
py .\app.py
```

The official Pwnage StormBreaker software should not be required.

## Roadmap

1. Extract the working HID reader into `stormbreaker.py`.
2. Add robust device/error handling.
3. Build the minimal battery visualization in `app.py`.
4. Add tray/background behavior.
5. Package as a lightweight Windows executable.
