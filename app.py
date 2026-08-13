from stormbreaker import get_battery_percentage




def refresh_battery():
    try:
        battery = get_battery_percentage()
    except RuntimeError as error:
        print(error)