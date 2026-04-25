from datetime import datetime, timedelta

DATE = "2026-04-25"

def parse_time(t):
    return datetime.fromisoformat(f"{DATE}T{t}")

def is_feasible(driver, pantry, donation, travel_seconds, sim_time=None):
    if sim_time is not None:
        now = datetime.strptime(
            f"{DATE} {sim_time.strftime('%H:%M')}", "%Y-%m-%d %H:%M"
        )
    else:
        now = datetime.now()

    driver_start = parse_time(driver["avail_start"])
    driver_end   = parse_time(driver["avail_end"])
    pantry_open  = parse_time(pantry["open"])
    pantry_close = parse_time(pantry["close"])
    expiry       = datetime.fromisoformat(donation["expiry"])

    # Driver departs at the later of now or their avail_start
    depart            = max(now, driver_start)
    arrival           = depart + timedelta(seconds=travel_seconds)

    # If driver arrives before pantry opens, they wait
    effective_arrival = max(arrival, pantry_open)

    if effective_arrival > pantry_close:                                   return False
    if effective_arrival > driver_end:                                     return False
    if effective_arrival > expiry:                                         return False
    if driver["current_load"] + donation["quantity"] > driver["capacity"]: return False

    return True


def get_effective_arrival(driver, pantry, travel_seconds, sim_time=None):
    """Returns the actual delivery time accounting for waiting."""
    if sim_time is not None:
        now = datetime.strptime(
            f"{DATE} {sim_time.strftime('%H:%M')}", "%Y-%m-%d %H:%M"
        )
    else:
        now = datetime.now()

    arrival     = now + timedelta(seconds=travel_seconds)
    pantry_open = parse_time(pantry["open"])
    return max(arrival, pantry_open)