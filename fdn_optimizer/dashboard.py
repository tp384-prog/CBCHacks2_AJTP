import streamlit as st
from datetime import datetime


def get_load_color(pct):
    if pct >= 0.85:
        return "red"
    elif pct >= 0.5:
        return "orange"
    return "green"


def pantry_status(pantry, sim_time=None):
    if sim_time is not None:
        now = datetime.strptime(f"2026-04-25 {sim_time.strftime('%H:%M')}", "%Y-%m-%d %H:%M")
    else:
        now = datetime.now()
    close_str = pantry["close"]
    close_dt = datetime.strptime(f"2026-04-25 {close_str}", "%Y-%m-%d %H:%M")
    mins_until_close = (close_dt - now).total_seconds() / 60
    if mins_until_close < 0:
        return "Closed", "red"
    elif mins_until_close < 30:
        return "Closing soon", "red"
    elif mins_until_close < 60:
        return "Closing soon", "orange"
    return "Open", "green"


def render_dashboard(drivers, active_pantries, opt_result, donations, sim_time=None):
    st.subheader("Resource dashboard")

    # ── Driver cards ───────────────────────────────────────────
    st.markdown("**Driver availability**")
    cols = st.columns(len(drivers))

    for i, driver in enumerate(drivers):
        assigned_lbs = sum(
            a["donation"]["quantity"]
            for a in opt_result["assignments"]
            if a["driver"]["name"] == driver["name"]
        )
        capacity = driver["capacity"]
        load_pct = assigned_lbs / capacity if capacity > 0 else 0
        color = get_load_color(load_pct)

        with cols[i]:
            st.markdown(
                f"""
                <div style="background:var(--background-color);
                            border:0.5px solid rgba(128,128,128,0.2);
                            border-radius:10px;padding:12px;">
                    <div style="font-weight:600;font-size:14px;
                                margin-bottom:6px">{driver['name']}</div>
                    <div style="font-size:12px;color:gray;
                                margin-bottom:2px">
                        {driver['avail_start']} – {driver['avail_end']}
                    </div>
                    <div style="font-size:12px;margin-bottom:6px">
                        Load: <b>{assigned_lbs} / {capacity} lbs</b>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
            st.progress(min(1.0, load_pct))

    st.divider()

    # ── Pantry status ──────────────────────────────────────────
    st.markdown("**Active pantries today**")

    for pantry in active_pantries:
        status_label, status_color = pantry_status(pantry, sim_time=sim_time)
        assigned_here = [
            a for a in opt_result["assignments"]
            if a["pantry"]["name"] == pantry["name"]
        ]
        total_lbs = sum(a["donation"]["quantity"] for a in assigned_here)

        col_name, col_time, col_lbs, col_status = st.columns([3, 2, 1, 1])
        col_name.write(pantry["name"])
        col_time.write(f"{pantry['open']} – {pantry['close']}")
        col_lbs.write(f"{total_lbs} lbs" if total_lbs > 0 else "—")

        if status_color == "green":
            col_status.success(status_label)
        elif status_color == "orange":
            col_status.warning(status_label)
        else:
            col_status.error(status_label)

    st.divider()

    # ── Unroutable explanations ────────────────────────────────
    if opt_result["unroutable"]:
        st.markdown("**Unroutable donations — why they failed**")
        for u in opt_result["unroutable"]:
            reasons = []
            total_assigned = sum(
                a["donation"]["quantity"]
                for a in opt_result["assignments"]
            )
            all_full = all(
                (d["current_load"] + u["quantity"]) > d["capacity"]
                for d in drivers
            )
            if all_full:
                reasons.append("all drivers at capacity")

            all_closed = all(
                pantry_status(p)[0] in ["Closed", "Closing soon"]
                for p in active_pantries
            )
            if all_closed:
                reasons.append("all pantries closing")

            if not reasons:
                reasons.append("time window conflict — no feasible driver/pantry pair")

            reason_str = " + ".join(reasons)
            st.warning(
                f"**{u['name']}** ({u['quantity']} lbs) — {reason_str}"
            )

        st.divider()

    # ── System totals ──────────────────────────────────────────
    st.markdown("**System totals**")
    total_capacity = sum(d["capacity"] for d in drivers)
    total_assigned = sum(
        a["donation"]["quantity"] for a in opt_result["assignments"]
    )
    total_donations = len(donations)
    routed = len(opt_result["assignments"])
    unrouted = len(opt_result["unroutable"])
    route_pct = min(1.0, routed / total_donations) if total_donations > 0 else 0

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("Capacity utilization")
        st.progress(min(1.0, total_assigned / total_capacity) if total_capacity > 0 else 0)
        st.caption(
            f"{total_assigned} lbs assigned of {total_capacity} lbs total "
            f"({min(100, round((total_assigned/total_capacity)*100))}%)"
        )
    with c2:
        st.markdown("Donation routing rate")
        st.progress(min(1.0, route_pct))
        st.caption(
            f"{routed} of {total_donations} donations routed "
            f"({round(route_pct*100)}%)"
        )