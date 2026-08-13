import time
from stormbreaker import get_battery_percentage

def main():
    pass

def refresh_battery() -> str:
    try:
        return f"{get_battery_percentage()}%"
    except RuntimeError as error:
        return f"Error: {error}"


if __name__ == "__main__":
    try:
        while True:
            print(refresh_battery())
            time.sleep(30)
    except KeyboardInterrupt:
        print("\nStopped.")