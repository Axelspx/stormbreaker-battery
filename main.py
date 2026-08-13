import pystray
import time
from pathlib import Path
from pystray import MenuItem as Item
from PIL import Image, ImageDraw
from threading import Event, Thread
from stormbreaker import get_battery_percentage, get_battery_status, is_charging, listen_for_device_changes
from settings import is_startup, enable_startup, disable_startup


def check_mouse_battery() -> str|tuple:
    global battery_percent, charging
    try:
        battery_percent, charging = get_battery_status()
        return f"{battery_percent}%", charging
    except RuntimeError as error:
        return f"Error: {error}", False


def battery_color(level: int) -> tuple[int, int, int]:
    stops = ((100, (34, 197, 94)), (60, (250, 204, 21)), (30, (249, 115, 22)), (15, (239, 68, 68)))

    for (upper, upper_color), (lower, lower_color) in zip(stops, stops[1:]):
        if level >= lower:
            amount = (level - lower) / (upper - lower)
            return tuple(round(lower_color[i] + (upper_color[i] - lower_color[i]) * amount) for i in range(3))

    return stops[-1][1]


def battery_icon(level: int | None) -> Image.Image:
    battery = Image.open(ASSETS / "Battery_dark.png").convert("RGBA")
    mouse = Image.open(ASSETS / "Mouse_dark.png").convert("RGBA")
    icon = Image.new("RGBA", battery.size)

    if level is not None:
        height = round(253 * level / 100)
        if height:
            ImageDraw.Draw(icon).rectangle((315, 401 - height, 443, 400), fill=battery_color(level))

    icon.alpha_composite(battery)
    icon.alpha_composite(mouse)
    return icon


def update_tray(icon) -> None:
    global charging, battery_percent, last_level
    icon.visible = True
    while not stop_event.is_set():
        refresh_event.clear()
        battery_percent, charging = check_mouse_battery()
        level = int(battery_percent[:-1]) if battery_percent.endswith("%") else None
        if not charging:
            low_battery_alert(icon, level)
        icon.icon = battery_icon(level)
        icon.title = f"{'Charging' if charging else 'Battery'}: {battery_percent}" if level is not None else "Loading..."
        icon.update_menu()

        refresh_event.wait(60)



def toggle_startup(icon, item) -> None:
    if is_startup():
        disable_startup()
    else:
        enable_startup()
    icon.update_menu()

def low_battery_alert(icon, level: int|None) -> None:
    global last_alert
    if level is not None and 0 < level <= 20 and time.monotonic() - last_alert >= 600:
        icon.notify(f"Battery is {battery_percent}", title="StormBreaker")
        last_alert = time.monotonic()

def main() -> None:
    icon = pystray.Icon(
        None,
        battery_icon(None),
        "Loading...",
        menu=pystray.Menu(
            Item(lambda item: f"{'Charging' if charging else 'Battery'}: {battery_percent}", None),
            pystray.Menu.SEPARATOR,
            Item('Launch on startup', toggle_startup, checked=lambda item: is_startup()),
            Item("Exit", exit_app)
        ),
    )
    icon.run(setup=update_tray)

def exit_app(icon, item) -> None:
    stop_event.set()
    refresh_event.set()
    icon.visible = False
    icon.stop()

battery_percent = "loading..."
charging = False
last_alert = 0.0
stop_event = Event()
refresh_event = Event()
ASSETS = Path(__file__).with_name("assets")


if __name__ == "__main__":
    Thread(target=listen_for_device_changes, args=(refresh_event,), daemon=True).start()
    main()
