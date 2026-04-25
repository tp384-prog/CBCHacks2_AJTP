import pandas as pd

DAY_MAP = {
    "Monday": "Mon", "Tuesday": "Tue", "Wednesday": "Wed",
    "Thursday": "Thu", "Friday": "Fri", "Saturday": "Sat", "Sunday": "Sun"
}

def load_pantries(day_of_week="Saturday"):
    df = pd.read_csv("data/pantries.csv")
    short = DAY_MAP[day_of_week]

    # Filter to only pantries open on this day
    open_today = df[df["days"].str.contains(short, na=False)].copy()

    # Add id column (optimizer needs this for matrix indexing)
    open_today = open_today.reset_index(drop=True)
    open_today["id"] = open_today.index + 1

    # Add location as [lat, lng] list (optimizer expects this format)
    open_today["location"] = open_today.apply(
        lambda row: [row["lat"], row["lng"]], axis=1
    )

    return open_today.to_dict(orient="records")


def load_partners():
    df = pd.read_csv("data/fdn_partners.csv")
    df["location"] = df.apply(lambda row: [row["lat"], row["lng"]], axis=1)
    return df.to_dict(orient="records")


def load_donations():
    return [
        {"id": 1, "name": "Wegmans", "item": "produce", "quantity": 80,
         "urgency": "high", "expiry": "2026-04-25T15:00:00",
         "location": [42.4440, -76.5019]},
        {"id": 2, "name": "Purity Bakery", "item": "bread", "quantity": 40,
         "urgency": "medium", "expiry": "2026-04-25T17:00:00",
         "location": [42.4450, -76.5100]},
        {"id": 3, "name": "Cornell Dining", "item": "canned goods", "quantity": 30,
         "urgency": "low", "expiry": "2026-04-25T20:00:00",
         "location": [42.4480, -76.4840]},
    ]


def load_drivers():
    return [
        {"id": 1, "name": "Sarah", "capacity": 100, "current_load": 0,
         "avail_start": "10:00", "avail_end": "17:00",
         "location": [42.4440, -76.5019], "location_index": 0},
        {"id": 2, "name": "Marcus", "capacity": 80, "current_load": 0,
         "avail_start": "11:00", "avail_end": "16:00",
         "location": [42.4380, -76.4950], "location_index": 1},
    ]