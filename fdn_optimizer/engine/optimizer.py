from .sort_edf import sort_by_edf, sort_pantries_by_close
from .feasibility import is_feasible

def greedy_insert(donations, pantries, drivers, time_matrix):
    sorted_donations = sort_by_edf(donations)
    sorted_pantries  = sort_pantries_by_close(pantries)
    assignments      = []
    unroutable       = []

    for donation in sorted_donations:
        best_cost       = float("inf")
        best_assignment = None

        for driver in drivers:
            for pantry in sorted_pantries:
                d_idx        = donation["id"] - 1
                p_idx        = len(donations) + pantry["id"] - 1
                travel_time  = time_matrix[d_idx][p_idx]

                if is_feasible(driver, pantry, donation, travel_time):
                    cost = travel_time  # marginal cost = extra travel time
                    if cost < best_cost:
                        best_cost       = cost
                        best_assignment = {
                            "driver":   driver,
                            "pantry":   pantry,
                            "donation": donation,
                            "travel_time_min": round(travel_time / 60, 1)
                        }

        if best_assignment:
            assignments.append(best_assignment)
            best_assignment["driver"]["current_load"] += donation["quantity"]
        else:
            unroutable.append(donation)

    return assignments, unroutable

from .build_time_matrix import build_time_matrix

def run_optimizer(donations, pantries, drivers):
    import copy
    drivers_copy = copy.deepcopy(drivers)
    matrix = build_time_matrix(donations, pantries)
    assignments, unroutable = greedy_insert(donations, pantries, drivers_copy, matrix)
    total_travel = sum(a["travel_time_min"] * 60 for a in assignments)
    return {
        "assignments": assignments,
        "unroutable": unroutable,
        "total_travel_seconds": total_travel
    }

if __name__ == "__main__":
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from data.load_data import load_pantries, load_donations, load_drivers

    donations = load_donations()
    pantries = load_pantries("Saturday")   # today is Saturday
    drivers = load_drivers()

    print(f"Loaded {len(pantries)} pantries open on Saturday")
    print(f"Loaded {len(donations)} donations")

    result = run_optimizer(donations, pantries, drivers)

    print("\n=== ASSIGNMENTS ===")
    for a in result["assignments"]:
        print(f"  {a['driver']['name']} → {a['donation']['name']} → {a['pantry']['name']} ({a['donation']['quantity']} lbs, {a['travel_time_min']} min)")

    print("\n=== UNROUTABLE ===")
    for u in result["unroutable"]:
        print(f"  {u['name']} could not be assigned")

    print(f"\nTotal travel time: {round(result['total_travel_seconds'] / 60, 1)} minutes")