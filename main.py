import pystray
import time
from pystray import MenuItem as Item
from PIL import Image, ImageDraw
from threading import Event
from stormbreaker import get_battery_percentage
from settings import is_startup, enable_startup, disable_startup


def refresh_battery() -> str:
    try:
        return f"{get_battery_percentage()}%"
    except RuntimeError as error:
        return f"Error: {error}"


def battery_color(level: int) -> tuple[int, int, int]:
    stops = ((100, (34, 197, 94)), (60, (250, 204, 21)), (30, (249, 115, 22)), (15, (239, 68, 68)))

    for (upper, upper_color), (lower, lower_color) in zip(stops, stops[1:]):
        if level >= lower:
            amount = (level - lower) / (upper - lower)
            return tuple(round(lower_color[i] + (upper_color[i] - lower_color[i]) * amount) for i in range(3))

    return stops[-1][1]


def battery_icon(level: int | None) -> Image.Image:
    battery = Image.open("assets/Battery_dark.png").convert("RGBA")
    mouse = Image.open("assets/Mouse_dark.png").convert("RGBA")
    icon = Image.new("RGBA", battery.size)

    if level is not None:
        height = round(253 * level / 100)
        if height:
            ImageDraw.Draw(icon).rectangle((315, 401 - height, 443, 400), fill=battery_color(level))

    icon.alpha_composite(battery)
    icon.alpha_composite(mouse)
    return icon


def update_tray(icon) -> None:
    global battery, last_alert
    icon.visible = True
    last_alert = 0.0
    while not stop_event.is_set():
        battery = refresh_battery()
        level = int(battery[:-1]) if battery.endswith("%") else None
        low_battery_alert(icon, level)
        icon.icon = battery_icon(level)
        icon.title = f"StormBreaker: {battery}"
        icon.update_menu()
        stop_event.wait(60)


def toggle_startup(icon, item) -> None:
    if is_startup():
        disable_startup()
    else:
        enable_startup()
    icon.update_menu()

def low_battery_alert(icon, level: int|None) -> None:
    global last_alert
    if level is not None and level <= 20 and time.monotonic() - last_alert >= 600:
        icon.notify(f"Battery is {battery}", title="StormBreaker")
        last_alert = time.monotonic()

def main() -> None:
    global battery
    battery = "loading..."
    icon = pystray.Icon(
        None,
        battery_icon(None),
        f"StormBreaker: {battery}",
        menu=pystray.Menu(
            Item(lambda item: f"StormBreaker: {battery}", None),
            pystray.Menu.SEPARATOR,
            Item('Launch on startup', toggle_startup, checked=lambda item: is_startup()),
            Item("Exit", exit_app)
        ),
    )
    icon.run(setup=update_tray)

def exit_app(icon, item) -> None:
    stop_event.set()
    icon.visible = False
    icon.stop()



if __name__ == "__main__":
    stop_event = Event()
    main()
