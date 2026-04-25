import streamlit as st
from dotenv import load_dotenv
from streamlit_folium import st_folium

from data.load_data import load_pantries, load_donations, load_drivers
from claude_utils import parse_input, narrate_routes
from engine.optimizer import run_optimizer
from naive_optimizer import run_naive
from map_utils import build_map
from dashboard import render_dashboard
from datetime import datetime, time


load_dotenv()

st.set_page_config(
    page_title="FDN Route Optimizer",
    page_icon="🥦",
    layout="wide"
)

# Sidebar header + sticky top bar
st.markdown("""
<style>
    /* Sticky top header */
    header[data-testid="stHeader"] {
        content: "FDN Route Optimizer";
        background: white;
        border-bottom: 0.5px solid rgba(128,128,128,0.2);
    }

    /* Sidebar title above the nav links */
    [data-testid="stSidebarNav"]::before {
        content: "FDN Route Optimizer";
        display: block;
        font-size: 16px;
        font-weight: 600;
        color: #2d7a3a;
        padding: 1.2rem 1rem 0.8rem;
        border-bottom: 0.5px solid rgba(128,128,128,0.2);
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

st.set_page_config(
    page_title="Optimizer — FDN",
    page_icon="🗺️",
    layout="wide"
)

st.title("Route optimizer")
st.caption("VRPTW-based route optimization with Claude-powered natural language interface")

if st.button("← Back to home"):
    st.switch_page("Home.py")

st.divider()

# ── Sidebar inputs ─────────────────────────────────────────────
with st.sidebar:
    st.header("Today's setup")

    day = st.selectbox(
        "Day of week",
        ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"],
        index=5
    )

    sim_time = st.time_input(
        "Current time (for planning)",
        value=datetime.strptime("12:00", "%H:%M").time()
    )

    raw_input = st.text_area(
        "Describe today's donations",
        height=160,
        placeholder=(
            "e.g. We have 80 lbs of produce from Wegmans expiring at 3pm, "
            "and 40 loaves from Purity Bakery good until 5pm."
        )
    )

    all_pantries = load_pantries(day)
    active_pantry_names = st.multiselect(
        "Active pantries today",
        options=[p["name"] for p in all_pantries],
        default=[p["name"] for p in all_pantries]
    )

    optimize_btn = st.button(
        "Optimize routes",
        type="primary",
        use_container_width=True
    )

    st.divider()
    st.caption("Built for the 2026 Cornell Claude Builders Club Hackathon")

active_pantries = [p for p in all_pantries if p["name"] in active_pantry_names]
drivers = load_drivers()

# ── Session state ──────────────────────────────────────────────
for key in ["opt_result", "naive_result", "briefing", "donations", "sim_time"]:
    if key not in st.session_state:
        st.session_state[key] = None

# ── Run on button click ────────────────────────────────────────
if optimize_btn and raw_input:
    st.session_state.sim_time = sim_time
    with st.spinner("Parsing donation input with Claude..."):
        try:
            parsed = parse_input(raw_input)
            donations = parsed["donations"]
            for i, d in enumerate(donations):
                d["id"] = i + 1
            st.session_state.donations = donations
        except Exception as e:
            st.error(f"Could not parse input. Try rephrasing. Error: {e}")
            st.stop()

    st.success(f"Parsed {len(donations)} donation(s). Running optimizer...")

    with st.spinner("Running EDF greedy heuristic..."):
        try:
            st.session_state.opt_result = run_optimizer(
                donations, active_pantries, drivers, sim_time=sim_time
            )
        except Exception as e:
            st.error(f"Optimizer error: {e}")
            st.stop()

    with st.spinner("Running naive baseline for comparison..."):
        st.session_state.naive_result = run_naive(
            donations, active_pantries, drivers
        )

    with st.spinner("Generating driver briefing with Claude..."):
        try:
            st.session_state.briefing = narrate_routes(
                st.session_state.opt_result["assignments"],
                st.session_state.opt_result["unroutable"]
            )
        except Exception as e:
            st.session_state.briefing = "Could not generate briefing."

elif optimize_btn and not raw_input:
    st.warning("Please describe today's donations in the sidebar first.")

# ── Display results ────────────────────────────────────────────
if st.session_state.opt_result is not None:
    opt_result  = st.session_state.opt_result
    naive_result = st.session_state.naive_result
    briefing    = st.session_state.briefing
    donations   = st.session_state.donations
    sim_time     = st.session_state.sim_time

    st.subheader("Optimization results")

    c1, c2, c3, c4 = st.columns(4)
    opt_mins   = round(opt_result["total_travel_seconds"] / 60, 1)
    naive_mins = round(naive_result["total_travel_seconds"] / 60, 1)
    savings    = round(naive_mins - opt_mins, 1)

    c1.metric("Optimized travel time", f"{opt_mins} min")
    c2.metric("Naive travel time", f"{naive_mins} min",
              delta=f"-{savings} min saved", delta_color="inverse")
    c3.metric("Pantries reached", len(opt_result["assignments"]))
    c4.metric("Unroutable donations", len(opt_result["unroutable"]))

    st.divider()

    map_col, brief_col = st.columns([3, 2])
    with map_col:
        st.subheader("Route map")
        route_map = build_map(opt_result["assignments"], donations, active_pantries)
        st_folium(route_map, width=700, height=450)
    with brief_col:
        st.subheader("Driver briefing")
        st.markdown(briefing)

    st.divider()
    render_dashboard(drivers, active_pantries, opt_result, donations, sim_time=sim_time)

    st.divider()
    st.subheader("Full assignment table")
    if opt_result["assignments"]:
        st.dataframe([{
            "Driver":         a["driver"]["name"],
            "Pickup from":    a["donation"]["name"],
            "Deliver to":     a["pantry"]["name"],
            "Quantity (lbs)": a["donation"]["quantity"],
            "Travel (min)":   a["travel_time_min"],
        } for a in opt_result["assignments"]], use_container_width=True)

    if opt_result["unroutable"]:
        st.warning(
            f"{len(opt_result['unroutable'])} donation(s) could not be routed: "
            + ", ".join(d["name"] for d in opt_result["unroutable"])
        )

    with st.expander("View ORIE formulation"):
        st.markdown("**Problem class:** Vehicle Routing Problem with Time Windows (VRPTW)")
        st.latex(r"x_{ijk} = 1 \text{ if driver } k \text{ travels from stop } i \text{ to stop } j")
        st.latex(r"\min \sum_k \sum_i \sum_j d_{ij} \cdot x_{ijk} + \lambda \sum_p u_p \cdot (1 - y_p)")
        st.markdown("""
**Constraints:** time windows · volunteer availability · vehicle capacity · perishability

**Solution method:** Greedy insertion heuristic with Earliest Deadline First (EDF) priority ordering
        """)