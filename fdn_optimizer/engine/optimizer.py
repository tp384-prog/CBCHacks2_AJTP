from .build_time_matrix import build_time_matrix
from .sort_edf import sort_by_edf, sort_pantries_by_close
from .feasibility import is_feasible
import copy
from datetime import datetime, timedelta

DATE = "2026-04-25"


def now_dt(sim_time=None):
    if sim_time is not None:
        return datetime.strptime(
            f"{DATE} {sim_time.strftime('%H:%M')}", "%Y-%m-%d %H:%M"
        )
    return datetime.now()


def parse_time_str(t):
    return datetime.fromisoformat(f"{DATE}T{t}")


def split_donations(donations, drivers):
    max_capacity = max(d["capacity"] for d in drivers)
    expanded = []
    for donation in donations:
        if donation["quantity"] <= max_capacity:
            expanded.append(donation)
        else:
            remaining = donation["quantity"]
            chunk_num = 1
            while remaining > 0:
                chunk_size = min(remaining, max_capacity)
                chunk = copy.deepcopy(donation)
                chunk["quantity"]    = chunk_size
                chunk["name"]        = f"{donation['name']} (trip {chunk_num})"
                chunk["original_id"] = donation["id"]
                expanded.append(chunk)
                remaining -= chunk_size
                chunk_num += 1
    return expanded


def greedy_insert(donations, pantries, drivers, time_matrix, sim_time=None):
    sorted_donations = sort_by_edf(donations)
    sorted_pantries  = sort_pantries_by_close(pantries)
    n_donations      = len(donations)
    expanded         = split_donations(sorted_donations, drivers)
    assignments      = []
    unroutable       = []

    driver_loads = {d["name"]: d["current_load"] for d in drivers}

    for donation in expanded:
        matrix_id = donation.get("original_id", donation["id"])
        d_idx     = matrix_id - 1

        remaining_qty = donation["quantity"]
        assigned_any  = False

        # Try to assign as much as possible across multiple drivers
        for driver in drivers:
            if remaining_qty <= 0:
                break

            current_load       = driver_loads[driver["name"]]
            remaining_capacity = driver["capacity"] - current_load

            if remaining_capacity <= 0:
                continue

            # How much can this driver take?
            chunk_qty = min(remaining_qty, remaining_capacity)

            # Find best pantry for this driver/chunk
            best_cost       = float("inf")
            best_assignment = None

            for pantry in sorted_pantries:
                p_idx = n_donations + pantry["id"] - 1

                if d_idx >= len(time_matrix) or p_idx >= len(time_matrix[d_idx]):
                    continue

                travel_secs = time_matrix[d_idx][p_idx]

                temp_driver = dict(driver)
                temp_driver["current_load"] = current_load

                # Check feasibility with the chunk size
                temp_donation = dict(donation)
                temp_donation["quantity"] = chunk_qty

                if is_feasible(temp_driver, pantry, temp_donation, travel_secs, sim_time=sim_time):
                    driver_start = parse_time_str(driver["avail_start"])
                    if sim_time is not None:
                        now = datetime.strptime(
                            f"{DATE} {sim_time.strftime('%H:%M')}", "%Y-%m-%d %H:%M"
                        )
                    else:
                        now = datetime.now()

                    depart    = max(now, driver_start)
                    arrival   = depart + timedelta(seconds=travel_secs)
                    open_time = parse_time_str(pantry["open"])
                    wait_secs = max(0, (open_time - arrival).total_seconds())
                    cost      = travel_secs + wait_secs

                    if cost < best_cost:
                        best_cost       = cost
                        best_assignment = {
                            "driver":          driver,
                            "pantry":          pantry,
                            "donation":        dict(donation),
                            "travel_time_min": round(travel_secs / 60, 1)
                        }
                        best_assignment["donation"]["quantity"] = chunk_qty
                        if chunk_qty < donation["quantity"]:
                            best_assignment["donation"]["name"] = (
                                f"{donation['name']} (partial {chunk_qty} lbs)"
                            )

            if best_assignment:
                assignments.append(best_assignment)
                driver_loads[best_assignment["driver"]["name"]] += chunk_qty
                remaining_qty -= chunk_qty
                assigned_any   = True

        if remaining_qty > 0:
            # Whatever couldn't be assigned goes to unroutable
            leftover = dict(donation)
            leftover["quantity"] = remaining_qty
            leftover["name"]     = f"{donation['name']} ({remaining_qty} lbs unassigned)"
            unroutable.append(leftover)

    return assignments, unroutable


def run_optimizer(donations, pantries, drivers, sim_time=None):
    drivers_copy = copy.deepcopy(drivers)
    matrix       = build_time_matrix(donations, pantries)

    assignments, unroutable = greedy_insert(
        donations, pantries, drivers_copy, matrix, sim_time=sim_time
    )

    total_travel = sum(a["travel_time_min"] * 60 for a in assignments)
    return {
        "assignments":          assignments,
        "unroutable":           unroutable,
        "total_travel_seconds": total_travel
    }


if __name__ == "__main__":
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from data.load_data import load_pantries, load_donations, load_drivers
    from datetime import time as dtime

    donations = load_donations()
    pantries  = load_pantries("Saturday")
    drivers   = load_drivers()
    sim_time  = dtime(10, 0)

    result = run_optimizer(donations, pantries, drivers, sim_time=sim_time)

    print("=== ASSIGNMENTS ===")
    for a in result["assignments"]:
        print(
            f"  {a['driver']['name']} → {a['donation']['name']} → "
            f"{a['pantry']['name']} ({a['donation']['quantity']} lbs, "
            f"{a['travel_time_min']} min)"
        )

    print("\n=== UNROUTABLE ===")
    for u in result["unroutable"]:
        print(f"  {u['name']} could not be assigned")

    print(f"\nTotal travel time: {round(result['total_travel_seconds'] / 60, 1)} minutes")