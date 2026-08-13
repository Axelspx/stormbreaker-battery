import sys
import winreg
from pathlib import Path


STARTUP_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
STARTUP_VALUE = "StormBreaker_Battery"


def enable_startup() -> None:
    exe_path = (
        f'"{Path(sys.executable).resolve()}"'
        if getattr(sys, "frozen", False)
        else f'"{Path(sys.executable).resolve()}" "{Path(__file__).with_name("main.py")}"'
    )

    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, STARTUP_KEY) as key:
        winreg.SetValueEx(key, STARTUP_VALUE, 0, winreg.REG_SZ, exe_path)


def disable_startup() -> None:
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, STARTUP_KEY, 0, winreg.KEY_SET_VALUE) as key:
            winreg.DeleteValue(key, STARTUP_VALUE)
    except FileNotFoundError:
        pass


def is_startup() -> bool:
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, STARTUP_KEY) as key:
            winreg.QueryValueEx(key, STARTUP_VALUE)
        return True
    except FileNotFoundError:
        return False
