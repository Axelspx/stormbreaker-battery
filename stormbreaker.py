import hid
import win32con
import win32gui
import time


VID = 0x3662
PID = 0x0002
USAGE_PAGE = 0xFF1C
USAGE = 0x0092
RESPONSE_LENGTH = 64
READ_TIMEOUT_MS = 1000


def find_receiver() -> dict:
    for device in hid.enumerate(VID, PID):
        if device.get("usage_page") == USAGE_PAGE and device.get("usage") == USAGE:
            return device
    raise RuntimeError("StormBreaker receiver not found.")


def battery_request() -> bytearray:
    request = bytearray(64)
    request[0] = 0x04
    request[3] = 0x1A
    request[4] = 0x06

    checksum = sum(request[3:]) & 0xFFFF
    request[1] = checksum & 0xFF
    request[2] = checksum >> 8
    return request


def parse_battery_response(response: list[int]) -> int:

    if len(response) < 9:
        raise RuntimeError("Short response from mouse.")

    if response[7] != 0:
        raise RuntimeError(f"Mouse returned status 0x{response[7]:02X}.")

    battery = response[8]

    if not 0 <= battery <= 100:
        raise RuntimeError(f"Invalid battery value: {battery}.")

    return battery


def get_battery_status() -> tuple[int, bool]:
    receiver = find_receiver()
    mouse = hid.device()

    try:
        mouse.open_path(receiver["path"])
        mouse.write(battery_request())
        response = mouse.read(RESPONSE_LENGTH, timeout_ms=READ_TIMEOUT_MS)
        if not response:
            raise RuntimeError("Mouse did not respond.")
        if len(response) < 10:
            raise RuntimeError("Short response from mouse.")
        return parse_battery_response(response), response[9] == 0x01

    except OSError as error:
        raise RuntimeError(f"Error communicating with mouse: {error}")

    finally:
        mouse.close()


def get_battery_percentage() -> int:
    return get_battery_status()[0]


def is_charging() -> bool:
    return get_battery_status()[1]

def listen_for_device_changes(refresh_event) -> None:
    def window_proc(hwnd, message, wparam, lparam):
        if message == win32con.WM_DEVICECHANGE:
            time.sleep(1)
            refresh_event.set()

        return win32gui.DefWindowProc(hwnd, message, wparam, lparam)

    window_class = win32gui.WNDCLASS()
    window_class.lpfnWndProc = window_proc
    window_class.lpszClassName = "StormBreakerDeviceChanges"

    class_atom = win32gui.RegisterClass(window_class)

    win32gui.CreateWindowEx(
        0,
        class_atom,
        "StormBreakerDeviceChanges",
        0,
        0, 0, 0, 0,
        0, 0, 0, None,
    )

    win32gui.PumpMessages()
