import pystray
from pystray import MenuItem as Item
from PIL import Image, ImageDraw
from threading import Event

from stormbreaker import get_battery_percentage


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


def update_tray(icon: pystray.Icon) -> None:
    icon.visible = True
    while not stop_event.is_set():
        battery = refresh_battery()
        level = int(battery[:-1]) if battery.endswith("%") else None
        icon.icon = battery_icon(level)
        icon.title = f"StormBreaker: {battery}"
        stop_event.wait(60)


def main() -> None:
    icon = pystray.Icon(
        None,
        battery_icon(None),
        "StormBreaker: loading...",
        menu=pystray.Menu(
            Item(f"StormBreaker: {refresh_battery()}", None),
            pystray.Menu.SEPARATOR,
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
