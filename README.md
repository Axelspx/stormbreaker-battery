# Pwnage StormBreaker Battery

A lightweight Windows tray utility that shows the battery level and charging state of a Pwnage StormBreaker mouse without running the official Pwnage software.

## What it does

- Displays a battery-and-mouse tray icon with a proportional, colour-changing battery fill.
- Shows the current percentage and charging state in the tray tooltip and menu.
- Polls the confirmed HID status request every 60 seconds and refreshes early after Windows device-change events.
- Shows a low-battery notification at 20% or below, then no more than once every 10 minutes while the mouse is not charging.
- Provides a tray toggle for Windows launch-at-startup.

## Project layout

```text
main.py          tray icon, polling, notifications, and startup menu
stormbreaker.py  HID status request and Windows device-change listener
settings.py      Windows Registry startup helpers
assets/          tray artwork and application icon
```

## Confirmed protocol

```text
VID:        0x3662
PID:        0x0002
Interface:  MI_00 / Col05
Usage page: 0xFF1C
Usage:      0x0092
```

The only command sent is the confirmed 64-byte battery/status request:

```text
04 20 00 1A 06 00 00 00 ...
```

Bytes `1-2` are the little-endian sum of bytes `3-63`.

```text
response[7] = status/error
response[8] = battery percentage (0-100)
response[9] = charging flag (0x01 = charging)
```

## Setup and run

```powershell
py -m pip install hidapi pystray pillow pywin32
py .\main.py
```

The receiver may be unplugged or the mouse may be unavailable; the tray app should remain running and show `Loading...` until a valid reading is available.

## Build

```powershell
py -m pip install pyinstaller
py -m PyInstaller --onefile --noconsole --name StormBreakerBattery --icon assets\pwnage-battery.ico --add-data "assets;assets" main.py
```

The executable is written to `dist\StormBreakerBattery.exe`.

## Asset licensing

`Battery_dark.png` and `Mouse_dark.png` are reused from [LGSTrayBattery](https://github.com/andyvorld/LGSTrayBattery), which is licensed under GPL-3.0. Keep the project's distribution licensing compatible with GPL-3.0 when distributing those assets.
