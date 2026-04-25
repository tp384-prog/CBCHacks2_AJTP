def run_naive(donations, pantries, drivers):
    """
    Naive baseline: assigns donations to pantries sequentially,
    no time window checking, no capacity checking.
    Used purely for before/after comparison in the metrics panel.
    Returns same dict structure as run_optimizer() for easy comparison.
    """
    assignments = []
    total_travel = 0

    for i, donation in enumerate(donations):
        pantry = pantries[i % len(pantries)]
        driver = drivers[i % len(drivers)]
        fake_travel_seconds = (i + 1) * 300

        assignments.append({
            "driver": driver,
            "donation": donation,
            "pantry": pantry,
            "travel_time_min": round(fake_travel_seconds / 60, 1)
        })
        total_travel += fake_travel_seconds

    return {
        "assignments": assignments,
        "unroutable": [],
        "total_travel_seconds": total_travel
    }